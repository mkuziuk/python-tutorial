---
title: "II-02. Пассажиры после факта"
description: "Аудируем Titanic, находим post-outcome leakage и собираем честный preprocessing pipeline."
arc: part-2
caseNumber: II-02
projectId: part-2-case-02
time: "4–5 часов"
format: Jupyter Notebook
difficulty: базовый ML
datasetIds: [openml-titanic-40945-frozen]
notebook: projects/part-2/case-02/case-02.ipynb
solutionNotebook: projects/part-2/case-02/solution/case-02-solution.ipynb
archive: public/downloads/part-2-case-02.zip
prerequisite: Дело II-01
concepts: [пропуски, категории, leakage, SimpleImputer, OneHotEncoder, ColumnTransformer, logistic regression]
---

<div class="bureau-brief">
  <p class="bureau-kicker">Аудит доступности признаков · дело II-02</p>
  <p><strong>Миссия</strong> определить, какие сведения реально существовали в момент прогноза, и пересчитать демонстрацию без информации из будущего.</p>
  <p><strong>Данные</strong> замороженный локальный snapshot Titanic с описанием источника и контрольной суммой.</p>
  <p><strong>Результат</strong> таблица доступности признаков, честный pipeline и сравнение honest/leaky моделей.</p>
  <p><strong>Перед началом</strong> требуется Часть I и навыки честного split/baseline из II-01.</p>
  <p><strong>Маршрут</strong> базовый ML · 4–5 часов · notebook-first · Python 3.12/3.13.</p>
</div>

<div class="materials-panel bureau-actions">
  <p><strong>Начать:</strong> <a href="../../downloads/part-2-case-02.zip">скачать ZIP</a> · <a href="../../datasets/titanic.csv" download>скачать данные CSV</a> · <a href="https://colab.research.google.com/github/mkuziuk/python-tutorial/blob/main/projects/part-2/case-02/case-02.ipynb">Open in Colab</a></p>
  <p><strong>После работы:</strong> <a href="../passengers-after-the-fact-solution/">дебриф и готовый notebook</a> · <a href="../../materials/#ii-02--пассажиры-после-факта">состав архива</a></p>
  <p><strong>Справочник:</strong> <a href="../../field-guide/pandas/">pandas и пропуски</a> · <a href="../../field-guide/ml-framing/">постановка задачи</a> · <a href="../../field-guide/leakage-pipelines/">утечка и pipeline</a> · <a href="../../field-guide/ml-models/#логистическая-регрессия">логистическая регрессия</a></p>
</div>

## Сюжет

После вступительного экзамена Тимур приносит первый реальный пакет «Компаса». В отчете о выживаемости пассажиров заявлена почти безошибочная классификация. Среди столбцов есть `boat` и `body`. Антон объясняет, что платформа «использует все доступные сигналы».

Но доступность — не свойство CSV-файла. Она зависит от времени решения. Номер спасательной шлюпки и номер найденного тела стали известны **после** исхода, который модель якобы предсказывает. Ваша задача — формально зафиксировать этот разрыв и показать его влияние на оценку.

## Что расследуем

1. Прочитайте карточку происхождения snapshot и проверьте контрольную сумму.
2. Исследуйте типы, пропуски, уникальные значения и связь столбцов с целевой переменной.
3. Для каждого кандидата в признаки отметьте: доступен до события, появляется после события или неоднозначен.
4. Уберите `boat` и `body` из честного набора признаков и заморозьте внешний стратифицированный holdout.
5. Для чисел соедините `SimpleImputer` и масштабирование; для категорий — `SimpleImputer` и `OneHotEncoder`.
6. Объедините ветки в `ColumnTransformer`, затем добавьте логистическую регрессию в `Pipeline`.
7. На одинаковом holdout сравните честный pipeline и учебную leaky-версию.

Главный результат — не максимальная accuracy. Нужна воспроизводимая демонстрация того, насколько оценка меняется после удаления недоступной информации.

## Код расследования

Эти фрагменты взяты из learner notebook и оставляют ключевое решение вам. Сначала проверьте локальный файл и создайте `DataFrame`; `DATA_DIR` и `sha256_file()` приходят из bootstrap-ячейки:

```python
DATASET_SHA256 = "c617db2c7470716250f6f001be51304c76bcc8815527ab8bae734bdca0735737"
data_path = DATA_DIR / "titanic.csv"
actual_sha256 = sha256_file(data_path)
if actual_sha256 != DATASET_SHA256:
    raise RuntimeError("Контрольная сумма titanic.csv не совпала")

passengers = pd.read_csv(data_path, na_values=["?"])
passengers["survived"] = passengers["survived"].astype(int)
display(passengers.head(3))
print("Форма DataFrame:", passengers.shape)
```

Только после чтения таблицы начинайте не с модели, а с временной доступности каждого поля:

```python
# TODO: замените статус и объяснение для каждого поля.
field_audit = pd.DataFrame(
    {
        "feature": passengers.columns,
        "decision_status": "TODO",
        "reason": "TODO: когда поле становится известно?",
    }
)
display(field_audit)
```

После аудита notebook фиксирует честные и post-outcome признаки отдельно. Это делает границу проверки видимой в коде:

```python
honest_numeric = ["age", "sibsp", "parch", "fare"]
honest_categorical = ["pclass", "sex", "embarked"]
honest_features = honest_numeric + honest_categorical
post_outcome_features = ["boat", "body"]

X_train_honest = train_data[honest_features]
X_test_honest = test_data[honest_features]
print("Честные признаки:", honest_features)
```

Обучаемые преобразования собраны вместе с моделью. Поэтому вызов `.fit(...)` ниже передает imputer, scaler и encoder только train-данные:

```python
def build_logistic_pipeline(
    numeric_features: list[str], categorical_features: list[str]
) -> Pipeline:
    numeric_steps = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_steps = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="constant", fill_value="__MISSING__")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    preprocessing = ColumnTransformer(
        [
            ("numeric", numeric_steps, numeric_features),
            ("categorical", categorical_steps, categorical_features),
        ]
    )
    return Pipeline(
        [
            ("preprocess", preprocessing),
            (
                "model",
                LogisticRegression(
                    solver="liblinear", max_iter=1000, random_state=RANDOM_STATE
                ),
            ),
        ]
    )
```

Оценка honest-варианта происходит на замороженном holdout. Числа появятся только после вашего Run All:

```python
honest_model = build_logistic_pipeline(honest_numeric, honest_categorical)
honest_model.fit(X_train_honest, y_train)
honest_predictions = honest_model.predict(X_test_honest)
honest_probabilities = honest_model.predict_proba(X_test_honest)[:, 1]

honest_accuracy = accuracy_score(y_test, honest_predictions)
honest_auc = roc_auc_score(y_test, honest_probabilities)
print(f"Честная модель | accuracy={honest_accuracy:.3f} | ROC AUC={honest_auc:.3f}")
```

## Что сдать

- выполненный `case-02.ipynb`;
- таблицу аудита признаков с временной доступностью и решением include/exclude;
- неизменяемые индексы outer train/test;
- honest pipeline, который самостоятельно обрабатывает пропуски и категории;
- сравнение honest/leaky на одном holdout;
- аудиторское мемо из пяти блоков.

## Рубрика

| Критерий | Зачет |
| --- | --- |
| Данные | Источник и snapshot названы; пропуски не удаляются молча. |
| Доступность | `boat` и `body` помечены как post-outcome и исключены из честной модели. |
| Pipeline | Imputer, encoder/scaler и модель обучаются только через pipeline на train. |
| Сравнение | Honest и leaky варианты используют один holdout; разница интерпретируется как эффект утечки. |
| Вывод | Доказана некорректность демонстрационной процедуры, но не умысел конкретного человека. |

## Ключевой вопрос мемо

Мог бы оператор получить значение каждого признака в тот момент, когда от модели требуется прогноз? Если нет, высокая метрика описывает распознавание уже известного исхода, а не полезную прогностическую систему.

После самостоятельного вывода откройте [дебриф](../passengers-after-the-fact-solution/). Честный pipeline понадобится в следующем деле, но архив II-03 все равно будет полностью самостоятельным.
