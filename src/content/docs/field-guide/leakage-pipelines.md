---
title: "Утечка данных и конвейеры"
description: "Как информация из будущего или тестовой выборки проникает в модель и как Pipeline/ColumnTransformer защищают границу обучения."
concept: leakage-pipelines
usedIn: [part-2-case-01, part-2-case-02, part-2-case-03, part-2-case-04, part-2-case-05, part-2-case-06]
order: 35
---

## Что такое утечка

Утечка возникает, когда при обучении используется информация, которой не будет
во время реального прогноза или которая относится к проверочной выборке. Из-за
этого оценка становится слишком оптимистичной.

Три частых вида:

1. **Утечка из будущего** — признак появился после предсказываемого события.
2. **Утечка при подготовке** — медиана или масштаб рассчитаны по всей таблице
   до разбиения.
3. **Утечка между группами** — связанные записи одного источника оказались по
   обе стороны границы оценки.

Например, в обучающей выборке известны возраста `[20, 40]`, а в тестовой —
`[100]`. Медиана обучения равна 30. Если сначала объединить строки, медиана
станет 40: тестовое значение уже повлияло на правило заполнения.

## Почему помогает `Pipeline`

`Pipeline.fit(X_train, y_train)` обучает каждый шаг подготовки только на
обучающей выборке. Проверим это на шести обучающих и двух тестовых объектах:

```python
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X_train = np.array([
    [0.0, 0.0], [0.2, 0.1], [1.0, 1.0],
    [1.2, 0.9], [0.1, 0.3], [0.9, 1.1],
])
y_train = np.array([0, 0, 1, 1, 0, 1])
X_test = np.array([[0.15, 0.2], [1.1, 1.0]])

model = make_pipeline(
    StandardScaler(),
    KNeighborsClassifier(n_neighbors=3),
)
model.fit(X_train, y_train)
predictions = model.predict(X_test)

print(predictions)
print(predictions.shape)
```

```text
[0 1]
(2,)
```

`StandardScaler` вычислил среднее и масштаб по шести строкам `X_train`, а
`predict` применил сохранённые параметры к двум строкам `X_test`. Форма `(2,)`
подтверждает по одной метке на тестовый объект. Числа не показывают качество:
для метрики понадобятся `y_test` и заранее выбранное правило оценки. Мы
проверили единый конвейер; теперь расширим подготовку на столбцы разных типов.

## Разные типы столбцов

Вход следующего этапа — таблица с двумя числовыми столбцами, одним
категориальным и одним пропуском. `ColumnTransformer` должен вернуть три строки
и четыре столбца: два масштабированных числовых и два one-hot-столбца порта.

```python
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

frame = pd.DataFrame({
    "age": [20.0, None, 40.0],
    "fare": [10.0, 20.0, 30.0],
    "port": ["S", "C", "S"],
})
numeric_columns = ["age", "fare"]
categorical_columns = ["port"]

numeric = make_pipeline(
    SimpleImputer(strategy="median"),
    StandardScaler(),
)
categorical = make_pipeline(
    SimpleImputer(strategy="most_frequent"),
    OneHotEncoder(handle_unknown="ignore", sparse_output=False),
)
preprocess = ColumnTransformer([
    ("num", numeric, numeric_columns),
    ("cat", categorical, categorical_columns),
])

transformed = preprocess.fit_transform(frame)
print(transformed.shape)
print(preprocess.get_feature_names_out().tolist())
```

```text
(3, 4)
['num__age', 'num__fare', 'cat__port_C', 'cat__port_S']
```

`SimpleImputer` выучил медиану возраста только из переданной обучающей таблицы.
`OneHotEncoder` создал по столбцу для категорий `C` и `S`, а
`handle_unknown="ignore"` позволит позднее кодировать неизвестную категорию
нулями без переобучения. Форма `(3, 4)` и имена подтверждают заявленное
преобразование. Следующий шаг реального проекта — добавить модель последним
шагом и передать весь конвейер внутрь кросс-валидации.

## Чего `Pipeline` не решает

Исследователь выбирает допустимые признаки, единицу группировки, тестовую
партию и сценарий применения. `Pipeline` обеспечивает только корректную
границу обучения преобразований.

## Проверочный список

- Сначала разбиение, потом `.fit()` любых преобразований.
- Цель не входит в `X`, даже под другим именем.
- Каждый признак существовал в момент прогноза.
- Связанные объекты не пересекают границу оценки.
- Тестовая выборка не влияет на признаки, модель, параметры или порог.
- В кросс-валидацию передаётся целый конвейер.

## Типичные ловушки

- `scaler.fit_transform(X)` до разбиения.
- Заполнение пропусков медианой всей таблицы.
- Выбор столбцов по корреляции с `y_test`.
- Сохранение идентификатора, который кодирует цель или источник.
- Вызов `fit_transform()` на тестовой выборке вместо `transform()`.

## Где встречается

[II-02](../../bureau/passengers-after-the-fact/) показывает утечку из будущего
и смешанный конвейер обработки. В [II-06](../../bureau/compass-exam/) проблема
связана не с преобразованием, а с зависимыми источниками.
