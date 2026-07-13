---
title: "II-04. Карта дорогих ошибок"
description: "Проверяем регрессию на California Housing: базовая модель, остатки, географические срезы и holdout новых регионов."
arc: part-2
caseNumber: II-04
projectId: part-2-case-04
time: "4–5 часов"
format: Jupyter Notebook
difficulty: средний ML
datasetIds: [sklearn-california-housing-1990-frozen-v1]
notebook: projects/part-2/case-04/case-04.ipynb
solutionNotebook: projects/part-2/case-04/solution/case-04-solution.ipynb
archive: public/downloads/part-2-case-04.zip
prerequisite: Дела II-01–II-03
concepts: [DummyRegressor, linear regression, random forest, MAE, RMSE, R², residuals, grouped holdout]
---

<div class="bureau-brief">
  <p class="bureau-kicker">Аудит переноса · дело II-04</p>
  <p><strong>Миссия</strong> проверить заявление о работе в новых регионах и перевести агрегатные показатели в карту реальных ошибок.</p>
  <p><strong>Данные</strong> замороженный snapshot California Housing с локальной карточкой происхождения.</p>
  <p><strong>Результат</strong> три регрессионных baseline/model варианта, остатки, случайный и географический holdout.</p>
  <p><strong>Перед началом</strong> требуется Часть I и понимание split, pipeline, baseline и метрик из II-01–II-03.</p>
  <p><strong>Маршрут</strong> средний ML · 4–5 часов · notebook-first · Python 3.12/3.13.</p>
</div>

<div class="materials-panel bureau-actions">
  <p><strong>Начать:</strong> <a href="../../downloads/part-2-case-04.zip">скачать ZIP</a> · <a href="https://colab.research.google.com/github/mkuziuk/python-tutorial/blob/main/projects/part-2/case-04/case-04.ipynb">Open in Colab</a></p>
  <p><strong>После работы:</strong> <a href="../map-of-costly-errors-solution/">дебриф и готовый notebook</a> · <a href="../../materials/#ii-04--карта-дорогих-ошибок">состав архива</a></p>
  <p><strong>Справочник:</strong> <a href="../../field-guide/regression/">регрессия и остатки</a> · <a href="../../field-guide/ml-models/#дерево-и-случайный-лес">лес</a> · <a href="../../field-guide/grouped-validation/">групповая проверка</a> · <a href="../../field-guide/plotting/">графики</a></p>
</div>

## Сюжет

«Компас» предлагает Бюро модуль массовой оценки жилья. На слайде указан хороший R², а подпись обещает работу «в том числе в новых регионах». Тимур замечает, что строки случайно перемешаны: соседние кварталы легко оказываются и в обучении, и в тесте.

В этом деле нужно различить две задачи. Случайный holdout проверяет интерполяцию среди похожих наблюдений. Географический holdout ближе к обещанию переноса в области, которых модель не видела. Один и тот же алгоритм может давать правдивые, но относящиеся к разным вопросам оценки.

## Что расследуем

1. Прочитайте единицы целевой переменной и отметьте ее верхнее ограничение в наборе.
2. Сравните `DummyRegressor`, линейную регрессию и детерминированный random forest.
3. Рассчитайте MAE, RMSE и R²; переведите ошибки в понятные денежные единицы.
4. Постройте графики `y_true`/`y_pred` и остатков, проверьте ошибки у верхней границы цены.
5. Нанесите абсолютную ошибку на координаты широты и долготы.
6. Повторите оценку на предопределенном географическом разбиении.
7. Сопоставьте результаты: какой claim поддерживает каждый holdout?

## Код расследования

Ключевые learner-ячейки показывают, что новое утверждение требует нового разбиения. В первой заглушке нужно заменить технические группы реальными географическими ячейками; проверка пересечения уже подготовлена:

```python
# TODO: замените временные группы на географические ячейки 0,5° × 0,5°.
region_groups = pd.Series(np.arange(len(X)) // 100, index=X.index, name="region_id")

region_splitter = GroupShuffleSplit(
    n_splits=1, test_size=0.20, random_state=RANDOM_STATE
)
grouped_train, grouped_test = next(
    region_splitter.split(X, y, groups=region_groups)
)
group_overlap = set(region_groups.iloc[grouped_train]) & set(region_groups.iloc[grouped_test])
print(f"Временная группировка; пересечение={len(group_overlap)}. Выполните TODO.")
```

Общая функция оценки должна прогнать один набор моделей на обоих split. В исходной learner-ячейке реализован только baseline — линейную регрессию и лес добавляете вы:

```python
model_suite = {"dummy_mean": DummyRegressor(strategy="mean")}

# TODO: добавьте linear и random_forest, затем заполните общую функцию оценки.
def evaluate_suite(train_positions, test_positions):
    fitted = DummyRegressor(strategy="mean").fit(
        X.iloc[train_positions], y.iloc[train_positions]
    )
    predicted = fitted.predict(X.iloc[test_positions])
    result = pd.DataFrame([{
        "model": "dummy_mean",
        "mae": mean_absolute_error(y.iloc[test_positions], predicted),
        "rmse": root_mean_squared_error(y.iloc[test_positions], predicted),
        "r2": r2_score(y.iloc[test_positions], predicted),
    }]).set_index("model")
    return result, {"dummy_mean": predicted}, {"dummy_mean": fitted}

random_results, random_predictions, random_fitted = evaluate_suite(
    random_train, random_test
)
display(random_results.round(3))
```

После реализации леса та же тетрадь связывает величину ошибки с местом. Цвет показывает доллары, а не абстрактные единицы target:

```python
if "random_forest" in grouped_predictions:
    map_frame = X.iloc[grouped_test][["Longitude", "Latitude"]].copy()
    map_frame["absolute_error_usd"] = np.abs(grouped_residuals) * 100_000
    fig, ax = plt.subplots(figsize=(7, 6))
    points = ax.scatter(
        map_frame["Longitude"], map_frame["Latitude"],
        c=map_frame["absolute_error_usd"], s=10, alpha=0.65, cmap="magma"
    )
    fig.colorbar(points, ax=ax, label="Абсолютная ошибка, USD")
    ax.set(title="Карта ошибок на невиданных региональных ячейках", xlabel="Longitude", ylabel="Latitude")
    plt.show()
else:
    map_frame = pd.DataFrame()
    print("Карта появится после реализации random_forest.")
```

## Что сдать

- выполненный `case-04.ipynb`;
- таблицу трех моделей на случайном split с baseline;
- график остатков и карту абсолютных ошибок;
- сравнение случайного и географического holdout;
- анализ дорогого сегмента и capped target;
- аудиторское мемо о границах утверждения «работает в новых регионах».

## Рубрика

| Критерий | Зачет |
| --- | --- |
| Единицы | MAE/RMSE интерпретированы в исходных и денежных единицах; capped target назван. |
| Baseline | Модели сравниваются с `DummyRegressor`, а не только друг с другом. |
| Остатки | Показана структура ошибок по цене или географии, не только средняя метрика. |
| Разбиение | Случайный и региональный holdout отвечают на разные явно сформулированные вопросы. |
| Вывод | Хороший случайный R² не используется как доказательство переноса в новый регион. |

## Ключевой вопрос мемо

Как изменились метрики и характер ошибок, когда похожие географические области перестали пересекаться между train и test? Запишите, какую более узкую формулировку все еще поддерживает случайная проверка.

После самостоятельного анализа откройте [дебриф](../map-of-costly-errors-solution/). Далее Бюро перейдет от таблиц к изображениям и многоклассовой классификации.
