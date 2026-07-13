---
title: "II-05. Знакомый почерк"
description: "Сравниваем k-NN и RBF SVM на Digits, подбираем конфигурацию и исследуем повторяющиеся ошибки классов."
arc: part-2
caseNumber: II-05
projectId: part-2-case-05
time: "4–5 часов"
format: Jupyter Notebook
difficulty: средний ML
datasetIds: [sklearn-digits-8x8-v1]
notebook: projects/part-2/case-05/case-05.ipynb
solutionNotebook: projects/part-2/case-05/solution/case-05-solution.ipynb
archive: public/downloads/part-2-case-05.zip
prerequisite: Дела II-01–II-04
concepts: [images, k-NN, RBF SVM, GridSearchCV, macro-F1, per-class recall, error gallery]
---

<div class="bureau-brief">
  <p class="bureau-kicker">Многоклассовый аудит · дело II-05</p>
  <p><strong>Миссия</strong> проверить, какие цифры модель путает систематически, и зафиксировать конфигурацию до финального экзамена.</p>
  <p><strong>Данные</strong> встроенный Digits: изображения 8×8 и десять классов.</p>
  <p><strong>Результат</strong> сравнение k-NN/RBF SVM, небольшой GridSearchCV, confusion matrix и галерея ошибок.</p>
  <p><strong>Перед началом</strong> требуется Часть I и дела II-01–II-04; особенно пригодятся CV и анализ ошибок.</p>
  <p><strong>Маршрут</strong> средний ML · 4–5 часов · notebook-first · Python 3.12/3.13.</p>
</div>

<div class="materials-panel bureau-actions">
  <p><strong>Начать:</strong> <a href="../../downloads/part-2-case-05.zip">скачать ZIP</a> · <a href="https://colab.research.google.com/github/mkuziuk/python-tutorial/blob/main/projects/part-2/case-05/case-05.ipynb">Open in Colab</a></p>
  <p><strong>После работы:</strong> <a href="../familiar-handwriting-solution/">дебриф и готовый notebook</a> · <a href="../../materials/#ii-05--знакомый-почерк">состав архива</a></p>
  <p><strong>Справочник:</strong> <a href="../../field-guide/numpy/">NumPy и формы</a> · <a href="../../field-guide/ml-models/">k-NN и SVM</a> · <a href="../../field-guide/cross-validation/">GridSearchCV</a> · <a href="../../field-guide/classification-metrics/">macro-F1 и recall</a></p>
</div>

## Сюжет

На новом показе «Компас» мгновенно распознает рукописные цифры. На экране — галерея удачных примеров и одна общая accuracy. Вера просит убрать монтаж и показать полный журнал: десять классов, все ошибки и процедуру выбора модели.

Digits — подготовка к финалу. Сейчас каждый исходный объект встречается один раз, поэтому обычная стратифицированная проверка уместна. Вы зафиксируете выбранную конфигурацию, чтобы в следующем деле не подгонять ее под новый стресс-тест.

## Что расследуем

1. Исследуйте `images` формы `(n, 8, 8)` и плоскую матрицу признаков `(n, 64)`.
2. Визуализируйте сбалансированность классов и несколько честно выбранных образцов.
3. На одном split сравните k-NN и RBF SVM.
4. Запустите небольшой заранее заданный `GridSearchCV` только на train.
5. Оцените выбранную модель по accuracy, macro-F1 и recall каждого класса.
6. Постройте многоклассовую confusion matrix.
7. Создайте галерею ошибок с истинной и предсказанной цифрой; опишите повторяющиеся пары.
8. Запишите и заблокируйте итоговую конфигурацию для II-06.

## Код расследования

Learner notebook сначала просит исправить разбиение. Заглушка запускается, но только добавленный вами `stratify=y` сохранит доли десяти классов осознанно:

```python
all_indices = np.arange(len(y))
# TODO: добавьте stratify=y и объясните, зачем он нужен.
train_indices, test_indices = train_test_split(
    all_indices, test_size=0.25, random_state=RANDOM_STATE
)
X_train, X_test = X[train_indices], X[test_indices]
y_train, y_test = y[train_indices], y[test_indices]
print(f"Временный split: train={len(train_indices)}, test={len(test_indices)}")
```

Два классических кандидата сравниваются на одинаковых folds и сразу по accuracy и macro-F1. Сбор таблицы остается упражнением:

```python
candidates = {
    "knn_5": make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=5)),
    "rbf_svm": make_pipeline(StandardScaler(), SVC(kernel="rbf")),
}
cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=RANDOM_STATE)
# TODO: вызовите cross_validate для каждой модели и соберите обе метрики.
cv_comparison = pd.DataFrame(
    columns=["accuracy_mean", "macro_f1_mean", "macro_f1_std"]
)
print("Таблица CV пока пуста — выполните TODO.")
```

Сетка намеренно мала и объявлена заранее. В learner-версии временная SVM позволяет продолжить Run All, но параметры блокировки останутся `TODO`, пока вы не реализуете `GridSearchCV` только на train:

```python
svm_pipeline = make_pipeline(StandardScaler(), SVC(kernel="rbf"))
parameter_grid = {"svc__C": [2, 10], "svc__gamma": ["scale", 0.001]}
# TODO: создайте GridSearchCV только на X_train/y_train.
grid = None
best_model = clone(svm_pipeline).fit(X_train, y_train)
locked_config = {
    "pipeline": "StandardScaler -> SVC",
    "kernel": "rbf",
    "C": "TODO",
    "gamma": "TODO",
    "selection_metric": "macro_f1",
    "cv": "TODO",
}
grid_table = pd.DataFrame(columns=[
    "param_svc__C", "param_svc__gamma", "mean_test_score", "std_test_score"
])
print("Временная SVM обучена; завершите grid и lock.")
```

Галерея берет первые воспроизводимые ошибки holdout, не выбранные вручную удачные или эффектные примеры:

```python
error_positions = np.flatnonzero(test_predictions != y_test)
shown = error_positions[: min(12, len(error_positions))]
if len(shown):
    fig, axes = plt.subplots(3, 4, figsize=(8, 6))
    for ax in axes.ravel():
        ax.axis("off")
    for ax, local_position in zip(axes.ravel(), shown, strict=False):
        source_index = test_indices[local_position]
        ax.imshow(images[source_index], cmap="gray_r", vmin=0, vmax=16)
        ax.set_title(f"истина {y_test[local_position]} → {test_predictions[local_position]}")
        ax.axis("off")
    fig.suptitle("Первые воспроизводимые ошибки holdout")
    plt.tight_layout()
    plt.show()
print(f"Ошибок в holdout: {len(error_positions)} из {len(y_test)}")
```

## Что сдать

- выполненный `case-05.ipynb`;
- сетку поиска и таблицу CV-результатов;
- test accuracy, macro-F1 и per-class recall;
- подписанную confusion matrix;
- галерею ошибочных примеров без ручного выбора только «красивых» случаев;
- аудиторское мемо и зафиксированную конфигурацию модели.

## Рубрика

| Критерий | Зачет |
| --- | --- |
| Форма данных | Ученик различает матрицу 8×8 для показа и 64 признака для классической модели. |
| Подбор | GridSearchCV работает только на train и перебирает небольшую объявленную сетку. |
| Метрики | Кроме accuracy есть macro-F1 и recall каждого класса. |
| Ошибки | Confusion matrix и галерея связывают метрику с конкретными путаницами. |
| Фиксация | Выбранная конфигурация записана до знакомства с batch C финального дела. |

## Ключевой вопрос мемо

Какие классы скрывались за хорошей общей accuracy и почему macro-F1 полезен, даже если классы почти сбалансированы? Отделите наблюдаемую путаницу цифр от догадки о причине почерка.

После своей версии откройте [дебриф](../familiar-handwriting-solution/). Финальное дело проверит, что случится, если связанные варианты одной цифры разнести между train и test.
