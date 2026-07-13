---
title: "Кросс-валидация и подбор параметров"
description: "Как оценивать процедуру на нескольких folds, получать out-of-fold прогнозы и использовать GridSearchCV без утечки."
concept: cross-validation
usedIn: [part-2-case-03, part-2-case-05, part-2-case-06]
order: 38
---

## Зачем нужна CV

Один validation split может оказаться случайно легким или трудным. K-fold cross-validation делит train на `k` частей: по очереди обучается на `k-1` частях и оценивается на оставшейся. Каждый объект участвует в validation ровно в одном fold.

**Fold** — одна из этих частей, а не отдельный датасет из другого источника. Если в train 12 объектов и `k=3`, получится три запуска: каждый раз 8 объектов для обучения и 4 для validation. Оценки, например `0.82`, `0.88`, `0.84`, можно свести к среднему `0.847` и разбросу; эти слова разобраны в [математическом словаре](../numpy/#math-vocabulary). Несколько folds честнее одного удачного числа, но всё ещё проверяют только выбранную схему разбиения.

```python
from sklearn.model_selection import StratifiedKFold, cross_validate

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_validate(
    pipeline,
    X_train,
    y_train,
    cv=cv,
    scoring=["accuracy", "precision", "recall", "f1"],
    n_jobs=1,
)
```

Для классификации `StratifiedKFold` сохраняет доли классов. Для связанных наблюдений он недостаточен — используйте группы.

## Out-of-fold прогнозы

`cross_val_predict()` возвращает для каждого train-объекта прогноз модели, которая не училась на этом объекте:

```python
from sklearn.model_selection import cross_val_predict

oof_probability = cross_val_predict(
    pipeline,
    X_train,
    y_train,
    cv=cv,
    method="predict_proba",
    n_jobs=1,
)[:, 1]
```

На этих вероятностях можно выбрать threshold, не открывая внешний holdout. Затем pipeline переобучается на всем outer-train и один раз проверяется на test.

## GridSearchCV

Гиперпараметры задают до обучения: например, `n_neighbors`, глубину дерева, `C` и `gamma`. В отличие от коэффициентов модели, они не вычисляются обычным `.fit()` — исследователь задаёт кандидатов, а процедура сравнивает их. `GridSearchCV` перебирает конечную объявленную сетку:

```python
from sklearn.model_selection import GridSearchCV

search = GridSearchCV(
    pipeline,
    param_grid={
        "svc__C": [1, 10],
        "svc__gamma": ["scale", 0.01],
    },
    scoring="f1_macro",
    cv=cv,
    n_jobs=1,
)
search.fit(X_train, y_train)
```

Имена параметров включают имя шага и двойное подчеркивание. Передавайте целый pipeline, иначе preprocessing будет обучен до folds и утечет в validation.

В примере два значения `C` умножаются на два значения `gamma`: всего четыре кандидата. При пяти folds это 20 обучений, после которых лучшая конфигурация ещё раз обучается на всём переданном train. Размер поиска стоит считать и сообщать: сотни неявных попыток повышают шанс случайной победы.

## Как читать результат

Показывайте не только `best_score_`, но и среднее, разброс, параметры кандидатов и размер поиска. Победа на тысячную может быть шумом CV. Чем больше комбинаций и ручных итераций, тем сильнее процедура подстраивается под folds.

## Типичные ловушки

- Включить внешний test в CV.
- Масштабировать всю матрицу до вызова `GridSearchCV`.
- Выбрать scoring после просмотра результатов.
- Расширять сетку до тех пор, пока score не понравится, и не документировать поиск.
- Считать folds независимыми доверительными интервалами.

## Где встречается

[II-03](../../bureau/cost-of-one-error/) использует CV и out-of-fold прогнозы для выбора модели и порога. [II-05](../../bureau/familiar-handwriting/) проводит небольшой GridSearchCV. [II-06](../../bureau/compass-exam/) добавляет группы.
