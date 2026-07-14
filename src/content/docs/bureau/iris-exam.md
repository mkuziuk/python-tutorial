---
title: "II-01. Ирисовый экзамен"
description: "Первое расследование Бюро: строим базовую модель и k-NN на Iris, отделяя качество на обучении от качества на новых данных."
arc: part-2
caseNumber: II-01
projectId: part-2-case-01
time: "3–4 часа"
format: Jupyter Notebook
difficulty: вводный ML
datasetIds: [sklearn-iris]
notebook: projects/part-2/case-01/case-01.ipynb
solutionNotebook: projects/part-2/case-01/solution/case-01-solution.ipynb
archive: public/downloads/part-2-case-01.zip
prerequisite: Часть I или уверенное владение базовым Python
concepts: [DataFrame, разбиение на обучение и тест, DummyClassifier, StandardScaler, k-NN, accuracy, матрица ошибок]
---

<div class="bureau-brief">
  <p class="bureau-kicker">Вводный допуск · расследование II-01</p>
  <p><strong>Миссия</strong> воспроизвести «идеальный» показ поставщика и заменить его корректной оценкой на новых объектах.</p>
  <p><strong>Данные</strong> локальный CSV-снимок Iris: 150 цветков, четыре измерения, три вида.</p>
  <p><strong>Результат</strong> базовая модель, k-NN с масштабированием, матрица ошибок и первое аудиторское мемо.</p>
  <p><strong>Перед началом</strong> пройдите Часть I или повторите функции, коллекции, виртуальное окружение и чтение файлов.</p>
  <p><strong>Маршрут</strong> вводный ML · 3–4 часа · основная работа в тетради · Python 3.12/3.13.</p>
</div>

<div class="materials-panel bureau-actions">
  <p><strong>Начать:</strong> <a href="../../downloads/part-2-case-01.zip">скачать ZIP</a> · <a href="../../datasets/iris.csv" download>скачать данные CSV</a> · <a href="https://colab.research.google.com/github/mkuziuk/python-tutorial/blob/main/projects/part-2/case-01/case-01.ipynb">Open in Colab</a></p>
  <p><strong>После работы:</strong> <a href="../iris-exam-solution/">дебриф и готовая тетрадь</a> · <a href="../../materials/#ii-01--ирисовый-экзамен">состав архива</a></p>
  <p><strong>Справочник:</strong> <a href="../../field-guide/ml-notebooks/">Jupyter</a> · <a href="../../field-guide/pandas/">pandas и пропуски</a> · <a href="../../field-guide/plotting/">графики</a> · <a href="../../field-guide/ml-framing/">разбиение и базовая модель</a> · <a href="../../field-guide/ml-models/#k-ближайших-соседей-k-nn">k-NN</a> · <a href="../../field-guide/classification-metrics/">метрики</a></p>
</div>

## Сюжет

В первый день Вера Орлова не даёт вам секретные данные. Вместо этого на экране появляется знакомая таблица Iris и слайд поставщика: «100% правильных ответов». Антон Карев называет это доказательством точности ядра «Компаса». Тимур Сафин передаёт тетрадь с демонстрацией без описания разбиения.

Ваша задача — воспроизвести заявленные 100% и показать, почему оценка на обучающих данных не измеряет качество на новых цветках. Для этого отделите тестовую выборку до выбора и обучения модели.

## Что расследуем

Вы пройдете полный минимальный цикл классификации:

1. прочитаете `iris.csv` через `pd.read_csv()`, изучите форму, столбцы, классы и диаграммы признаков;
2. отделите матрицу признаков `X` от целевой переменной `y`;
3. зафиксируете стратифицированное разбиение на обучающую и тестовую выборки до выбора модели;
4. измерите `DummyClassifier`, который задаёт нижнюю планку;
5. соберёте `StandardScaler` и k-NN в единый конвейер;
6. сравните accuracy на обучающей и тестовой выборках и прочитаете матрицу ошибок;
7. объясните расстояние Евклида и accuracy простыми долями, без вывода формул.

Notebook ведёт расследование по шагам. Не переносите финальный код в отдельный скрипт: важны промежуточные таблицы, графики и письменные ответы рядом с ними.

## Код расследования

Ниже — опорные ячейки из тетради для самостоятельной работы, а не готовое решение. Начните с файла: проверьте SHA-256, создайте `DataFrame`, выделите `X` и `y` — и только затем зафиксируйте разбиение. Переменные `DATA_DIR` и функция `sha256_file()` создаются начальной ячейкой тетради.

```python
manifest = json.loads(
    (DATA_DIR / "dataset_manifest.json").read_text(encoding="utf-8")
)
data_path = DATA_DIR / manifest["filename"]
# Проверяем точную версию данных до чтения: иначе результаты нельзя воспроизвести.
actual_sha256 = sha256_file(data_path)
assert actual_sha256 == manifest["sha256"], "SHA-256 iris.csv не совпадает"

frame = pd.read_csv(data_path)
feature_names = list(manifest["feature_names"])
species_by_code = dict(enumerate(manifest["classes"]))

display(frame.head())
print("Форма DataFrame:", frame.shape)

X = frame[feature_names]
y = frame["species_code"]
```

Теперь можно зафиксировать стратифицированное разбиение. Оно получает уже созданные из CSV `X` и `y`:

```python
# Модель выбираем по обучающей выборке; тестовую используем для итоговой оценки.
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=RANDOM_STATE,
    stratify=y,
)

split_summary = pd.concat(
    [
        y_train.value_counts(normalize=True).sort_index().rename("train_share"),
        y_test.value_counts(normalize=True).sort_index().rename("test_share"),
    ],
    axis=1,
).rename(index=species_by_code)
display(split_summary.round(3))
print("train:", len(X_train), "| test:", len(X_test))
```

`DummyClassifier(strategy="most_frequent")` всегда предсказывает самый частый класс и задаёт базовую accuracy. Сравните k-NN с этой моделью на той же внешней тестовой выборке:

```python
baseline = DummyClassifier(strategy="most_frequent", random_state=RANDOM_STATE)
baseline.fit(X_train, y_train)
baseline_predictions = baseline.predict(X_test)
baseline_accuracy = accuracy_score(y_test, baseline_predictions)
print(f"Dummy test accuracy: {baseline_accuracy:.3f}")
```

Финальная сравнительная ячейка не подбирает `k`: к этому моменту `selected_k` уже должен быть выбран только по кросс-валидации обучающей выборки.

```python
final_model = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=selected_k))
final_model.fit(X_train, y_train)
test_predictions = final_model.predict(X_test)
test_accuracy = accuracy_score(y_test, test_predictions)

comparison = pd.DataFrame(
    {
        "scenario": ["dummy / внешний test", "k-NN / внешний test", "vendor / train"],
        "accuracy": [baseline_accuracy, test_accuracy, vendor_training_accuracy],
        "valid_generalization_check": [True, True, False],
    }
)
display(comparison.round(3))
```

## Что сдать

- заполненный `case-01.ipynb`, запущенный сверху вниз без ошибок;
- зафиксированные размеры обучающей и тестовой выборок и доли трёх классов;
- сравнение базовой модели `DummyClassifier` и k-NN на одной тестовой выборке;
- подписанная матрица ошибок;
- аудиторское мемо из пяти обязательных блоков.

## Рубрика

| Критерий | Зачёт |
| --- | --- |
| Процедура | Разбиение сделано до обучения и использует `stratify=y`; тестовая выборка не участвует в подборе. |
| Код | Масштабирование и k-NN объединены в конвейер; все случайные операции воспроизводимы. |
| Оценка | Есть базовая модель, accuracy на тестовой выборке и интерпретация хотя бы одной ячейки матрицы ошибок. |
| Вывод | Установлен факт оценки на обучении; не утверждается, что поставщик совершил личный обман. |

## Ключевой вопрос мемо

Почему результат на тех же объектах, по которым алгоритм подстраивал решение, не оценивает обобщение? Сформулируйте ответ через различие между «запомнить известные примеры» и «правильно обработать новый цветок».

Когда все ячейки выполнены и вывод записан, переходите к [дебрифу](../iris-exam-solution/). Следующее расследование добавит пропуски, категории и признаки, которых не могло существовать в момент прогноза.
