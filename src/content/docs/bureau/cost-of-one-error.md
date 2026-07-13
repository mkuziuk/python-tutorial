---
title: "II-03. Цена одной ошибки"
description: "Сравниваем модели на Titanic, выбираем порог без подглядывания в holdout и исследуем цену ошибок по срезам."
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
prerequisite: Дела II-01 и II-02; честный Titanic pipeline вложен в архив
concepts: [cross-validation, precision, recall, F1, threshold, out-of-fold predictions, slices]
---

<div class="bureau-brief">
  <p class="bureau-kicker">Цена решения · дело II-03</p>
  <p><strong>Миссия</strong> выбрать модель и порог под заранее заданные ограничения, не превращая исторический прогноз в совет о спасении.</p>
  <p><strong>Данные</strong> тот же замороженный Titanic; честный pipeline из II-02 уже включен в самостоятельный архив.</p>
  <p><strong>Результат</strong> CV-сравнение, выбранный по out-of-fold прогнозам порог, одно финальное измерение и анализ срезов.</p>
  <p><strong>Перед началом</strong> требуется Часть I и дела II-01–II-02; все нужные файлы II-02 продублированы в ZIP.</p>
  <p><strong>Маршрут</strong> средний ML · 4–5 часов · notebook-first · Python 3.12/3.13.</p>
</div>

<div class="materials-panel bureau-actions">
  <p><strong>Начать:</strong> <a href="../../downloads/part-2-case-03.zip">скачать ZIP</a> · <a href="https://colab.research.google.com/github/mkuziuk/python-tutorial/blob/main/projects/part-2/case-03/case-03.ipynb">Open in Colab</a></p>
  <p><strong>После работы:</strong> <a href="../cost-of-one-error-solution/">дебриф и готовый notebook</a> · <a href="../../materials/#ii-03--цена-одной-ошибки">состав архива</a></p>
  <p><strong>Справочник:</strong> <a href="../../field-guide/classification-metrics/">метрики, пороги и срезы</a> · <a href="../../field-guide/cross-validation/">кросс-валидация</a> · <a href="../../field-guide/ml-models/">логистическая регрессия и дерево</a></p>
</div>

## Сюжет

После удаления утечки показатели стали скромнее. Антон предлагает вернуть модели статус «готово», потому что accuracy все еще выглядит высокой. Журнал демонстрации при этом показывает, что внешний test открывали после нескольких настроек, а в отчет попал лучший запуск. Вера останавливает обсуждение: разные ошибки имеют разный смысл, а многократно просмотренный holdout уже не дает независимой финальной оценки.

Бюро задает операционное правило до анализа holdout: **recall должен быть не ниже 0.85, доля отмеченных пассажиров — не выше 55%; среди допустимых порогов максимизируем precision**. Это учебное ограничение для аудита исторических данных, а не рецепт спасательной операции.

## Что расследуем

1. Проверьте, что внешний holdout совпадает с зафиксированным разбиением и остается закрытым.
2. Сравните логистическую регрессию и неглубокое дерево через стратифицированную кросс-валидацию только на outer-train.
3. Получите out-of-fold вероятности выбранной модели.
4. Постройте таблицу порогов: precision, recall, F1 и доля flagged.
5. Примените записанное правило и зафиксируйте порог до открытия holdout.
6. Ровно один раз оцените выбранную процедуру на outer-test.
7. Исследуйте ошибки по полу и классу билета; явно укажите маленькие срезы.

## Код расследования

В learner notebook внешний holdout остается закрытым, пока одинаковые folds сравнивают кандидатов на outer-train. Эта ячейка собирает несколько метрик, чтобы accuracy не стала единственным критерием:

```python
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
scoring = ["accuracy", "precision", "recall", "f1"]
cv_rows = []

for model_name, model in {"logistic": logistic_model, "shallow_tree": tree_model}.items():
    result = cross_validate(
        model,
        X_train,
        y_train,
        cv=cv,
        scoring=scoring,
        n_jobs=1,
        return_train_score=False,
    )
    for metric in scoring:
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

Между следующими фрагментами notebook добавляет третий, заранее зафиксированный кандидат `supplied_random_forest`. Одна служебная ячейка получает OOF-вероятности всех трёх кандидатов, проверяет операционное ограничение только на train и записывает вероятности выбранного по этому правилу кандидата в `oof_probabilities`. Внешний holdout в выборе не участвует.

Пороговая таблица тоже строится по этим out-of-fold прогнозам train. TODO оставляет вам применение операционного правила и выбор единственного порога:

```python
threshold_rows = []
for threshold in np.linspace(0.05, 0.95, 181):
    candidate_predictions = (oof_probabilities >= threshold).astype(int)
    threshold_rows.append(
        {
            "threshold": threshold,
            "precision": precision_score(y_train, candidate_predictions, zero_division=0),
            "recall": recall_score(y_train, candidate_predictions),
            "f1": f1_score(y_train, candidate_predictions),
            "flag_rate": candidate_predictions.mean(),
        }
    )
threshold_table = pd.DataFrame(threshold_rows)

# TODO: отфильтруйте допустимые строки и максимизируйте precision.
feasible = threshold_table.iloc[0:0].copy()
selected_threshold = 0.5
print(f"Временный порог до выполнения TODO: {selected_threshold:.3f}")
```

После единственного открытия holdout одна функция должна одинаково считать ошибки для всех срезов. Заглушки не позволяют получить готовый вывод со страницы:

```python
def slice_metrics(group: pd.DataFrame) -> pd.Series:
    # TODO: вычислите confusion matrix и верните n/precision/recall/fpr/errors.
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
- финальные holdout-метрики и confusion matrix;
- срезы ошибок по `sex` и `pclass` с размерами групп;
- аудиторское мемо, отделяющее прогноз, причинность и политику решения.

## Рубрика

| Критерий | Зачет |
| --- | --- |
| Изоляция holdout | Модель и порог выбраны без результатов outer-test. |
| CV | Сравнение использует одинаковые folds и честный preprocessing pipeline. |
| Порог | Соблюдены `recall ≥ 0.85` и `flagged ≤ 55%`; затем максимизирован precision. |
| Срезы | Для каждой группы показаны размер и ошибки; малые выборки не переинтерпретированы. |
| Вывод | Ассоциации Titanic не названы причинными эффектами или инструкцией по спасению. |

## Ключевой вопрос мемо

Как изменился вывод, когда вы заменили accuracy на требования к recall, нагрузке и precision? Укажите, что было решено заранее, что оценено кросс-валидацией и что узнали только из финального holdout.

Сверьте логику с [дебрифом](../cost-of-one-error-solution/). В следующем деле целевая переменная станет непрерывной, а случайное разбиение столкнется с географией.
