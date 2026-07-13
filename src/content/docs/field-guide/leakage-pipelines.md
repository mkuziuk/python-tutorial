---
title: "Утечка данных и pipeline"
description: "Как информация из будущего или test проникает в модель и как Pipeline/ColumnTransformer защищают границу обучения."
concept: leakage-pipelines
usedIn: [part-2-case-01, part-2-case-02, part-2-case-03, part-2-case-04, part-2-case-05, part-2-case-06]
order: 35
---

## Что такое утечка

Утечка возникает, когда обучение получает информацию, которой не будет при реальном прогнозе или которая принадлежит validation/test. Оценка становится слишком оптимистичной.

Три частых вида:

1. **post-outcome leakage** — признак появился после предсказываемого события (`boat`, `body` в Titanic);
2. **preprocessing leakage** — медиана, масштаб или отбор признаков рассчитаны по всей таблице до split;
3. **group leakage** — связанные записи одного человека/источника оказались и в train, и в test.

Мини-пример preprocessing leakage: в train известны возраста `[20, 40]`, а в test — `[100]`. Медиана только train равна 30. Если сначала объединить всё, медиана станет 40: значение из test уже изменило правило заполнения train, хотя модель ещё «не открывала» test. На большой таблице такая утечка менее заметна, но принцип тот же.

## Почему pipeline помогает

`Pipeline.fit(X_train, y_train)` обучает каждый preprocessing-шаг только на train. При `predict(X_test)` он применяет сохраненные параметры без переобучения.

```python
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier

model = make_pipeline(
    StandardScaler(),
    KNeighborsClassifier(n_neighbors=5),
)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
```

## Разные типы столбцов

```python
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

numeric = make_pipeline(
    SimpleImputer(strategy="median"),
    StandardScaler(),
)
categorical = make_pipeline(
    SimpleImputer(strategy="most_frequent"),
    OneHotEncoder(handle_unknown="ignore"),
)

preprocess = ColumnTransformer([
    ("num", numeric, numeric_columns),
    ("cat", categorical, categorical_columns),
])
```

`SimpleImputer` учит значение для заполнения пропусков. `OneHotEncoder` превращает категорию, например `embarked="C"`, в отдельные 0/1-столбцы. `StandardScaler` сохраняет среднее и масштаб числовых признаков. Все эти величины являются обученными параметрами preprocessing, а не нейтральной «уборкой» данных.

Добавьте модель последним шагом. Тогда тот же объект можно безопасно использовать внутри CV: для каждого fold imputer, encoder, scaler и модель обучатся заново только на тренировочной части fold.

## Что pipeline не решает

Pipeline не знает смысла признака. Он не удалит `boat`, не выберет правильные группы, не запечатает batch C и не сформулирует deployment-сценарий. Семантическую границу задает исследователь.

## Проверочный список

- Сначала split, потом `.fit()` любых преобразований.
- Цель не входит в `X`, даже под другим именем.
- Каждый признак существовал в момент прогноза.
- Связанные объекты не пересекают границу оценки.
- Test не влияет на признаки, модель, гиперпараметры или порог.
- В CV передается целый pipeline, а не заранее преобразованная матрица.

## Типичные ловушки

- `scaler.fit_transform(X)` до split.
- Заполнение пропусков медианой всей таблицы.
- Выбор «лучших» столбцов по корреляции с `y_test`.
- Сохранение идентификатора, который кодирует цель или источник.
- Вызов `fit_transform()` на test вместо `transform()`.

## Где встречается

[II-02](../../bureau/passengers-after-the-fact/) показывает post-outcome leakage и смешанный pipeline. В [II-06](../../bureau/compass-exam/) процедурная проблема лежит не в преобразовании, а в связанных источниках.
