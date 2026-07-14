---
title: "II-03. Цена одной ошибки"
description: "Сравниваем модели на Titanic, выбираем порог без подглядывания в отложенную тестовую выборку и исследуем цену ошибок по срезам."
arc: part-2
caseNumber: II-03
projectId: part-2-case-03
time: "4–5 часов"
format: Jupyter Notebook
difficulty: средний ML
datasetIds: [openml-titanic-40945-frozen]
notebook: projects/part-2/case-03/case-03.ipynb
solutionNotebook: projects/part-2/case-03/solution/case-03-solution.ipynb
archive: public/downloads/part-2-case-03.zip
prerequisite: Дела II-01 и II-02; корректный конвейер Titanic вложен в архив
concepts: [кросс-валидация, precision, recall, F1, порог, вневыборочные прогнозы, срезы]
---

<div class="bureau-brief">
  <p class="bureau-kicker">Цена решения · дело II-03</p>
  <p><strong>Миссия</strong> сравнить модели кросс-валидацией, выбрать порог по OOF-прогнозам с ограничениями <code>recall ≥ 0.85</code> и <code>flagged ≤ 55%</code>, а затем один раз оценить выбранную процедуру на тестовой выборке.</p>
  <p><strong>Данные</strong> та же зафиксированная локальная копия Titanic; корректный конвейер из II-02 уже включён в самостоятельный архив.</p>
  <p><strong>Результат</strong> сравнение с помощью кросс-валидации, выбранный по вневыборочным (out-of-fold, OOF) прогнозам порог, одно финальное измерение и анализ срезов.</p>
  <p><strong>Перед началом</strong> требуется Часть I и дела II-01–II-02; все нужные файлы II-02 продублированы в ZIP.</p>
  <p><strong>Маршрут</strong> средний ML · 4–5 часов · основная работа в тетради · Python 3.12/3.13.</p>
</div>

<div class="materials-panel bureau-actions">
  <p><strong>Начать:</strong> <a href="../../downloads/part-2-case-03.zip">скачать ZIP</a> · <a href="../../datasets/titanic.csv" download>скачать данные CSV</a> · <a href="https://colab.research.google.com/github/mkuziuk/python-tutorial/blob/main/projects/part-2/case-03/case-03.ipynb">Open in Colab</a></p>
  <p><strong>После работы:</strong> <a href="../cost-of-one-error-solution/">дебриф и готовая тетрадь</a> · <a href="../../materials/#ii-03--цена-одной-ошибки">состав архива</a></p>
  <p><strong>Справочник:</strong> <a href="../../field-guide/classification-metrics/">метрики, пороги и срезы</a> · <a href="../../field-guide/cross-validation/">кросс-валидация</a> · <a href="../../field-guide/ml-models/">логистическая регрессия и дерево</a></p>
</div>

## Сюжет

После удаления утечки показатели стали скромнее. Антон предлагает вернуть модели статус «готово», потому что accuracy всё ещё выглядит высокой. Журнал демонстрации при этом показывает, что внешнюю тестовую выборку открывали после нескольких настроек, а в отчёт попал лучший запуск. Вера останавливает обсуждение: разные ошибки имеют разный смысл, а многократно просмотренная тестовая выборка уже не даёт независимой финальной оценки.

Бюро задаёт операционное правило до анализа тестовой выборки: **recall должен быть не ниже 0.85, доля отмеченных пассажиров — не выше 55%; среди допустимых порогов максимизируем precision**. Это учебное ограничение для аудита исторических данных, а не рецепт спасательной операции.

## Что расследуем

1. Проверьте, что внешняя тестовая выборка совпадает с зафиксированным разбиением и остаётся закрытой.
2. Сравните логистическую регрессию и неглубокое дерево с помощью стратифицированной кросс-валидации только на внешней обучающей выборке.
3. Получите OOF-вероятности выбранной модели.
4. Постройте таблицу порогов: precision, recall, F1 и доля flagged.
5. Примените записанное правило и зафиксируйте порог до оценки на тестовой выборке.
6. Ровно один раз оцените выбранную процедуру на внешней тестовой выборке.
7. Исследуйте ошибки по полу и классу билета; явно укажите маленькие срезы.

## Код расследования

Дело автономно: оно снова начинается с локального `titanic.csv` и не требует переменных из II-02. Начальная ячейка заранее создаёт `DATA_DIR` и `sha256_file()`:

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

Не используйте `X_test` и `y_test` при сравнении кандидатов. Запустите стратифицированную кросс-валидацию на `X_train` и `y_train`, используя одинаковые разбиения для каждой модели, и сравните accuracy, precision, recall и F1:

```python
# Все кандидаты получают одинаковые части выборки, поэтому их оценки сопоставимы.
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
подсчёт баллов = ["accuracy", "precision", "recall", "f1"]
cv_rows = []

for model_name, model in {"logistic": logistic_model, "shallow_tree": tree_model}.items():
    result = cross_validate(
        model,
        X_train,
        y_train,
        cv=cv,
        подсчёт баллов=подсчёт баллов,
        n_jobs=1,
        return_train_score=False,
    )
    for metric in подсчёт баллов:
        values = result[f"test_{metric}"]
        cv_rows.append(
            {
                "model": model_name,
                "metric": metric,
                "mean": values.mean(),
                "std": values.std(),
            }
        )

cv_summary = pd.DataFrame(cv_rows)
display(cv_summary.pivot(index="model", columns="metric", values="mean").round(3))
display(cv_summary.query("metric == 'f1'").round(3))
```

Между следующими фрагментами тетрадь добавляет третий, заранее зафиксированный кандидат `supplied_random_forest`. Одна служебная ячейка получает OOF-вероятности всех трёх кандидатов, проверяет операционное ограничение только на обучающей выборке и записывает вероятности выбранного по этому правилу кандидата в `oof_probabilities`. Внешняя тестовая выборка в выборе не участвует.

Пороговая таблица тоже строится по OOF-прогнозам обучающей выборки. TODO оставляет вам применение операционного правила и выбор единственного порога:

```python
порог_rows = []
for порог in np.linspace(0.05, 0.95, 181):
    candidate_predictions = (oof_probabilities >= порог).astype(int)
    порог_rows.append(
        {
            "порог": порог,
            "precision": precision_score(y_train, candidate_predictions, zero_division=0),
            "recall": recall_score(y_train, candidate_predictions),
            "f1": f1_score(y_train, candidate_predictions),
            "flag_rate": candidate_predictions.mean(),
        }
    )
порог_table = pd.DataFrame(порог_rows)

# TODO: отфильтруйте допустимые строки и максимизируйте precision.
# Порог выбирается по OOF-прогнозам обучающей выборки.
feasible = порог_table.iloc[0:0].copy()
selected_порог = 0.5
print(f"Временный порог до выполнения TODO: {selected_порог:.3f}")
```

После единственной оценки на тестовой выборке одна функция должна одинаково считать ошибки для всех срезов. Заглушки не позволяют получить готовый вывод со страницы:

```python
def slice_metrics(group: pd.DataFrame) -> pd.Series:
    # TODO: вычислите матрица ошибок и верните n/precision/recall/fpr/errors.
    return pd.Series({"n": len(group), "precision": np.nan, "recall": np.nan, "fpr": np.nan, "errors": np.nan})

slice_frame = test_data[["sex", "pclass"]].copy()
slice_frame["actual"] = y_test
slice_frame["predicted"] = final_predictions
slice_report = slice_frame.groupby(["sex", "pclass"], dropna=False).apply(slice_metrics, include_groups=False)
display(slice_report.round(3))
```

## Что сдать

- выполненный `case-03.ipynb`;
- таблицу CV для двух моделей;
- таблицу допустимых порогов и однозначное обоснование выбора;
- финальные метрики на тестовой выборке и матрицу ошибок;
- срезы ошибок по `sex` и `pclass` с размерами групп;
- аудиторское мемо, отделяющее прогноз, причинность и политику решения.

## Рубрика

| Критерий | Зачёт |
| --- | --- |
| Изоляция теста | Модель и порог выбраны без результатов внешней тестовой выборки. |
| Кросс-валидация | Сравнение использует одинаковые части выборки и корректный конвейер предобработки. |
| Порог | Соблюдены `recall ≥ 0.85` и `flagged ≤ 55%`; затем максимизирован precision. |
| Срезы | Для каждой группы показаны размер и ошибки; малые выборки не переинтерпретированы. |
| Вывод | Ассоциации Titanic не названы причинными эффектами или инструкцией по спасению. |

## Ключевой вопрос мемо

Как изменился вывод, когда вы заменили accuracy на требования к recall, нагрузке и precision? Укажите, что было решено заранее, что оценено кросс-валидацией и что узнали только из финальной тестовой выборки.

Сверьте логику с [дебрифом](../cost-of-one-error-solution/). В следующем деле целевая переменная станет непрерывной, а случайное разбиение столкнется с географией.
