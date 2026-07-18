---
title: "Кросс-валидация и подбор параметров"
description: "Как оценивать процедуру на нескольких частях выборки, получать вневыборочные прогнозы и использовать GridSearchCV без утечки."
concept: cross-validation
usedIn: [part-2-case-03, part-2-case-05, part-2-case-06]
order: 38
---

## Зачем нужна CV

Одно разбиение на обучение и проверку может оказаться случайно лёгким или
трудным. K-fold кросс-валидация делит обучающую выборку на `k` частей: по
очереди обучается на `k-1` частях и оценивается на оставшейся. Каждый объект
участвует в проверке ровно один раз.

**Фолд (fold)** — одна из этих частей. Следующий пример создаёт 40 объектов с
четырьмя признаками и бинарной целью. Конвейер масштабирует признаки внутри
каждого фолда и обучает логистическую регрессию:

```python
import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X_train, y_train = make_classification(
    n_samples=40,
    n_features=4,
    n_informative=3,
    n_redundant=0,
    class_sep=1.2,
    random_state=7,
)
pipeline = make_pipeline(
    StandardScaler(),
    LogisticRegression(max_iter=1000, random_state=42),
)
cv = StratifiedKFold(n_splits=4, shuffle=True, random_state=42)
scores = cross_validate(
    pipeline,
    X_train,
    y_train,
    cv=cv,
    scoring=["accuracy", "precision", "recall", "f1"],
    n_jobs=1,
)

print("F1 по фолдам:", np.round(scores["test_f1"], 3))
print(
    "Среднее ± стандартное отклонение:",
    f"{scores['test_f1'].mean():.3f} ± {scores['test_f1'].std():.3f}",
)
```

```text
F1 по фолдам: [0.8   0.833 1.    1.   ]
Среднее ± стандартное отклонение: 0.908 ± 0.092
```

`scores` — словарь вида `название → массив из четырёх значений`. F1 лежит от
0 до 1, больше — лучше; стандартное отклонение `0.092` описывает разброс
четырёх оценок, но не является доверительным интервалом. `StratifiedKFold`
сохраняет доли классов. Для связанных наблюдений он недостаточен — нужны
группы.

## Вневыборочные прогнозы

`cross_val_predict()` возвращает для каждого объекта прогноз модели, которая
не училась на этом объекте. Повторим определения, чтобы листинг запускался
отдельно, и проверим форму вневыборочных (OOF) оценок:

```python
import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X_train, y_train = make_classification(
    n_samples=40,
    n_features=4,
    n_informative=3,
    n_redundant=0,
    class_sep=1.2,
    random_state=7,
)
pipeline = make_pipeline(
    StandardScaler(),
    LogisticRegression(max_iter=1000, random_state=42),
)
cv = StratifiedKFold(n_splits=4, shuffle=True, random_state=42)
oof_score = cross_val_predict(
    pipeline,
    X_train,
    y_train,
    cv=cv,
    method="predict_proba",
    n_jobs=1,
)[:, 1]

assert oof_score.shape == (len(X_train),)
print(np.round(oof_score[:3], 3))
print(oof_score.shape)
```

```text
[0.053 0.82  0.538]
(40,)
```

Форма `(40,)` подтверждает по одной оценке на строку. Первые три числа —
оценки класса `1`, а не метки и не автоматически откалиброванные вероятности.
Теперь можно сравнить несколько заранее заданных порогов на OOF-оценках, не
используя внешнюю тестовую выборку.

## GridSearchCV

Гиперпараметры задают до обучения. `GridSearchCV` перебирает конечную
объявленную сетку. Сравним три значения силы регуляризации `C` на тех же
четырёх фолдах и выведем всех кандидатов:

```python
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X_train, y_train = make_classification(
    n_samples=40,
    n_features=4,
    n_informative=3,
    n_redundant=0,
    class_sep=1.2,
    random_state=7,
)
pipeline = make_pipeline(
    StandardScaler(),
    LogisticRegression(max_iter=1000, random_state=42),
)
cv = StratifiedKFold(n_splits=4, shuffle=True, random_state=42)
search = GridSearchCV(
    pipeline,
    param_grid={"logisticregression__C": [0.1, 1.0, 10.0]},
    scoring="f1_macro",
    cv=cv,
    n_jobs=1,
)
search.fit(X_train, y_train)

results = pd.DataFrame(search.cv_results_)
table = results[[
    "param_logisticregression__C",
    "mean_test_score",
    "std_test_score",
]].sort_values("mean_test_score", ascending=False)
print(table.to_string(
    index=False,
    formatters={
        "mean_test_score": "{:.3f}".format,
        "std_test_score": "{:.3f}".format,
    },
))
```

```text
 param_logisticregression__C mean_test_score std_test_score
                         0.1           0.898          0.102
                         1.0           0.898          0.102
                        10.0           0.873          0.085
```

Имя параметра включает имя шага и двойное подчёркивание. Три значения `C` и
четыре фолда означают 12 обучений, после которых лучшая конфигурация ещё раз
обучается на всей переданной выборке. Кандидаты `0.1` и `1.0` имеют одинаковое
среднее `0.898`, поэтому таблица не обосновывает преимущество одного из них.
`std_test_score` показывает разброс по фолдам. Мы проверили кандидатов внутри
обучающей выборки; внешняя тестовая выборка всё ещё закрыта.

## Как читать результат

Показывайте не только `best_score_`, но и среднее, разброс, параметры кандидатов
и размер поиска. Победа на тысячную может быть шумом кросс-валидации. Чем
больше комбинаций и ручных итераций, тем сильнее процедура подстраивается под
фолды.

## Типичные ловушки

- Включить внешнюю тестовую выборку в кросс-валидацию.
- Масштабировать всю матрицу до вызова `GridSearchCV`.
- Выбрать scoring после просмотра результатов.
- Расширять сетку, пока значение метрики не понравится, и не документировать
  поиск.
- Считать фолды независимыми доверительными интервалами.

## Где встречается

[II-03](../../bureau/cost-of-one-error/) использует кросс-валидацию и
вневыборочные прогнозы для выбора модели и порога.
[II-05](../../bureau/familiar-handwriting/) проводит небольшой `GridSearchCV`.
[II-06](../../bureau/compass-exam/) добавляет группы.
