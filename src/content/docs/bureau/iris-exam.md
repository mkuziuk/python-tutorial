---
title: "II-01. Ирисовый экзамен"
description: "Первое дело Бюро: строим честный baseline и k-NN на Iris, отделяя качество на обучении от качества на новых данных."
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
concepts: [DataFrame, train/test split, DummyClassifier, StandardScaler, k-NN, accuracy, confusion matrix]
---

<div class="bureau-brief">
  <p class="bureau-kicker">Вводный допуск · дело II-01</p>
  <p><strong>Миссия</strong> воспроизвести «идеальный» показ поставщика и заменить его честной оценкой на новых объектах.</p>
  <p><strong>Данные</strong> локальный CSV-снимок Iris: 150 цветков, четыре измерения, три вида.</p>
  <p><strong>Результат</strong> baseline, масштабированный k-NN, матрица ошибок и первое аудиторское мемо.</p>
  <p><strong>Перед началом</strong> пройдите Часть I или повторите функции, коллекции, виртуальное окружение и чтение файлов.</p>
  <p><strong>Маршрут</strong> вводный ML · 3–4 часа · notebook-first · Python 3.12/3.13.</p>
</div>

<div class="materials-panel bureau-actions">
  <p><strong>Начать:</strong> <a href="../../downloads/part-2-case-01.zip">скачать ZIP</a> · <a href="../../datasets/iris.csv" download>скачать данные CSV</a> · <a href="https://colab.research.google.com/github/mkuziuk/python-tutorial/blob/main/projects/part-2/case-01/case-01.ipynb">Open in Colab</a></p>
  <p><strong>После работы:</strong> <a href="../iris-exam-solution/">дебриф и готовый notebook</a> · <a href="../../materials/#ii-01--ирисовый-экзамен">состав архива</a></p>
  <p><strong>Справочник:</strong> <a href="../../field-guide/ml-notebooks/">Jupyter</a> · <a href="../../field-guide/pandas/">pandas</a> · <a href="../../field-guide/plotting/">графики</a> · <a href="../../field-guide/ml-framing/">разбиение и baseline</a> · <a href="../../field-guide/ml-models/#k-ближайших-соседей-k-nn">k-NN</a> · <a href="../../field-guide/classification-metrics/">метрики</a></p>
</div>

## Сюжет

В первый день Вера Орлова не дает вам секретные данные. Вместо этого на экране появляется знакомая таблица Iris и слайд поставщика: «100% правильных ответов». Антон Карев называет это доказательством точности ядра «Компаса». Тимур Сафин передает notebook демонстрации без описания разбиения.

Это квалификационный экзамен Бюро. Нужно показать, где заканчивается наблюдение и начинается необоснованное обещание. Никакого подвоха в самих цветках нет: проблема в том, **на каких данных модель училась и на каких ее оценивали**.

## Что расследуем

Вы пройдете полный минимальный цикл классификации:

1. прочитаете `iris.csv` через `pd.read_csv()`, изучите форму, столбцы, классы и диаграммы признаков;
2. отделите матрицу признаков `X` от целевой переменной `y`;
3. зафиксируете стратифицированный train/test split до выбора модели;
4. измерите `DummyClassifier`, который задает нижнюю планку;
5. соберете `StandardScaler` и k-NN в единый pipeline;
6. сравните accuracy на train и test и прочитаете confusion matrix;
7. объясните расстояние Евклида и accuracy простыми долями, без вывода формул.

Notebook ведет расследование по шагам. Не переносите финальный код в отдельный скрипт: важны промежуточные таблицы, графики и письменные ответы рядом с ними.

## Код расследования

Ниже — реперные ячейки из learner notebook, а не готовое решение. Порядок начинается с файла: проверить SHA-256, создать `DataFrame`, выделить `X` и `y` — и только затем заморозить split. Переменные `DATA_DIR` и функция `sha256_file()` создаются bootstrap-ячейкой notebook.

```python
manifest = json.loads(
    (DATA_DIR / "dataset_manifest.json").read_text(encoding="utf-8")
)
data_path = DATA_DIR / manifest["filename"]
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

Теперь можно зафиксировать стратифицированный split. Он получает уже созданные из CSV `X` и `y`:

```python
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

Baseline отвечает на вопрос «лучше ли модель самого примитивного правила?», поэтому использует тот же внешний test:

```python
baseline = DummyClassifier(strategy="most_frequent", random_state=RANDOM_STATE)
baseline.fit(X_train, y_train)
baseline_predictions = baseline.predict(X_test)
baseline_accuracy = accuracy_score(y_test, baseline_predictions)
print(f"Dummy test accuracy: {baseline_accuracy:.3f}")
```

Финальная сравнительная ячейка не подбирает `k`: к этому моменту `selected_k` уже должен быть выбран только по train/CV.

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
- зафиксированные размеры train/test и доли трех классов;
- сравнение dummy baseline и k-NN на одном и том же test-наборе;
- подписанная матрица ошибок;
- аудиторское мемо из пяти обязательных блоков.

## Рубрика

| Критерий | Зачет |
| --- | --- |
| Процедура | Разбиение сделано до обучения и использует `stratify=y`; test не участвует в подборе. |
| Код | Масштабирование и k-NN объединены в pipeline; все случайные операции воспроизводимы. |
| Оценка | Есть baseline, test accuracy и интерпретация хотя бы одной ячейки матрицы ошибок. |
| Вывод | Установлен факт оценки на обучении; не утверждается, что поставщик совершил личный обман. |

## Ключевой вопрос мемо

Почему результат на тех же объектах, по которым алгоритм подстраивал решение, не оценивает обобщение? Сформулируйте ответ через различие между «запомнить известные примеры» и «правильно обработать новый цветок».

Когда все ячейки выполнены и вывод записан, переходите к [дебрифу](../iris-exam-solution/). Следующее дело добавит пропуски, категории и признаки, которых не могло существовать в момент прогноза.
