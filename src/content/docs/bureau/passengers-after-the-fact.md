---
title: "II-02. Пассажиры после факта"
description: "Аудируем Titanic, находим утечку сведений о результате и собираем корректный конвейер предобработки."
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
prerequisite: Расследование II-01
concepts: [пропуски, категории, leakage, SimpleImputer, OneHotEncoder, ColumnTransformer, логистическая регрессия]
---

<div class="bureau-brief">
  <p class="bureau-kicker">Аудит доступности признаков · расследование II-02</p>
  <p><strong>Миссия</strong> определить, какие сведения реально существовали в момент прогноза, и пересчитать демонстрацию без информации из будущего.</p>
  <p><strong>Данные</strong> зафиксированная локальная копия Titanic с описанием источника и контрольной суммой.</p>
  <p><strong>Результат</strong> таблица доступности признаков, корректный конвейер `Pipeline` и сравнение модели без утечки с заведомо некорректной.</p>
  <p><strong>Перед началом</strong> требуется Часть I и навыки разбиения и построения базовой модели из II-01.</p>
  <p><strong>Маршрут</strong> базовый ML · 4–5 часов · основная работа в тетради · Python 3.12/3.13.</p>
</div>

<div class="materials-panel bureau-actions">
  <p><strong>Начать:</strong> <a href="../../downloads/part-2-case-02.zip">скачать ZIP</a> · <a href="../../datasets/titanic.csv" download>скачать данные CSV</a> · <a href="https://colab.research.google.com/github/mkuziuk/python-tutorial/blob/main/projects/part-2/case-02/case-02.ipynb">Open in Colab</a></p>
  <p><strong>После работы:</strong> <a href="../passengers-after-the-fact-solution/">дебриф и готовая тетрадь</a> · <a href="../../materials/#ii-02--пассажиры-после-факта">состав архива</a></p>
  <p><strong>Справочник:</strong> <a href="../../field-guide/pandas/">pandas и пропуски</a> · <a href="../../field-guide/ml-framing/">постановка задачи</a> · <a href="../../field-guide/leakage-pipelines/">утечка и конвейер `Pipeline`</a> · <a href="../../field-guide/ml-models/#логистическая-регрессия">логистическая регрессия</a></p>
</div>

## Сюжет

После вступительного экзамена Тимур приносит первый реальный пакет «Компаса». В отчёте о выживаемости пассажиров заявлена почти безошибочная классификация. Среди столбцов есть `boat` и `body`. Антон объясняет, что платформа «использует все доступные сигналы».

Доступность признака определяется моментом, когда модель должна сделать прогноз. Номер спасательной шлюпки и номер найденного тела стали известны **после** исхода и поэтому создают утечку. Ваша задача — формально зафиксировать эту утечку и показать её влияние на оценку.

## Что расследуем

1. Прочитайте карточку происхождения snapshot и проверьте контрольную сумму.
2. Исследуйте типы, пропуски, уникальные значения и связь столбцов с целевой переменной.
3. Для каждого кандидата в признаки отметьте: доступен до события, появляется после события или неоднозначен.
4. Уберите `boat` и `body` из корректного набора признаков и зафиксируйте внешнюю стратифицированную тестовую выборку.
5. Для чисел соедините `SimpleImputer` и масштабирование; для категорий — `SimpleImputer` и `OneHotEncoder`.
6. Объедините ветки в `ColumnTransformer`, затем добавьте логистическую регрессию в `Pipeline`.
7. На одной и той же тестовой выборке сравните корректный конвейер и учебную версию с утечкой.

Главный результат — воспроизводимое измерение того, насколько оценка меняется после удаления недоступной информации.

## Код расследования

Эти фрагменты взяты из тетради для самостоятельной работы и оставляют ключевое решение вам. Сначала проверьте локальный файл и создайте `DataFrame`; `DATA_DIR` и `sha256_file()` создаются в начальной ячейке:

```python
DATASET_SHA256 = "c617db2c7470716250f6f001be51304c76bcc8815527ab8bae734bdca0735737"
data_path = DATA_DIR / "titanic.csv"
# Контрольная сумма связывает выводы с точной версией локального снимка.
actual_sha256 = sha256_file(data_path)
if actual_sha256 != DATASET_SHA256:
    raise RuntimeError("Контрольная сумма titanic.csv не совпала")

passengers = pd.read_csv(data_path, na_values=["?"])
passengers["survived"] = passengers["survived"].astype(int)
display(passengers.head(3))
print("Форма DataFrame:", passengers.shape)
```

После чтения таблицы определите временную доступность каждого поля:

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

После аудита тетрадь явно разделяет признаки, доступные до исхода, и признаки, появившиеся после него:

```python
honest_numeric = ["age", "sibsp", "parch", "fare"]
honest_categorical = ["pclass", "sex", "embarked"]
honest_features = honest_numeric + honest_categorical
post_outcome_features = ["boat", "body"]

X_train_honest = train_data[honest_features]
X_test_honest = test_data[honest_features]
print("Честные признаки:", honest_features)
```

Обучаемые преобразования собраны вместе с моделью. Поэтому вызов `.fit(...)` ниже передаёт импьютеру, масштабированию и кодировщику только обучающие данные:

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
    # Pipeline обучает преобразования на обучающей части каждого разбиения.
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

Корректный вариант оценивается на зафиксированной тестовой выборке. Числа появятся только после вашего **Run All**:

```python
honest_model = build_logistic_pipeline(honest_numeric, honest_categorical)
honest_model.fit(X_train_honest, y_train)
honest_predictions = honest_model.predict(X_test_honest)
honest_probabilities = honest_model.predict_proba(X_test_honest)[:, 1]

honest_accuracy = accuracy_score(y_test, honest_predictions)
honest_auc = roc_auc_score(y_test, honest_probabilities)
print(f"Корректная модель | доля правильных ответов={honest_accuracy:.3f} | ROC AUC={honest_auc:.3f}")
```

## Что сдать

- выполненный `case-02.ipynb`;
- таблицу аудита признаков с временной доступностью и решением include/exclude;
- неизменяемые индексы внешней обучающей и тестовой выборок;
- корректный конвейер `Pipeline`, который самостоятельно обрабатывает пропуски и категории;
- сравнение корректного варианта и варианта с утечкой на одной тестовой выборке;
- аудиторское мемо из пяти блоков.

## Рубрика

| Критерий | Зачёт |
| --- | --- |
| Данные | Источник и snapshot названы; пропуски не удаляются молча. |
| Доступность | `boat` и `body` помечены как доступные только после исхода и исключены из корректной модели. |
| Конвейер | Импьютер, кодировщик, масштабирование и модель обучаются только через `Pipeline` на обучающей выборке. |
| Сравнение | Корректный вариант и вариант с утечкой используют одну тестовую выборку; разница интерпретируется как эффект утечки. |
| Вывод | Доказана некорректность демонстрационной процедуры, но не умысел конкретного человека. |

## Ключевой вопрос мемо

Мог бы оператор получить значение каждого признака в тот момент, когда от модели требуется прогноз? Если нет, высокая метрика описывает распознавание уже известного исхода, а не полезную прогностическую систему.

После самостоятельного вывода откройте [дебриф](../passengers-after-the-fact-solution/). Корректный конвейер понадобится в следующем расследовании, но архив II-03 всё равно будет полностью самостоятельным.
