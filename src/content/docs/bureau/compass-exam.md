---
title: "II-06. Экзамен для «Компаса»"
description: "Финальный аудит связанных изображений, групповой валидации и сдвига новой партии сканера."
arc: part-2
caseNumber: II-06
projectId: part-2-case-06
time: "6–8 часов"
format: Jupyter Notebook
difficulty: продвинутый ML-аудит
datasetIds: [compass-digits-synthetic-captures-v1]
notebook: projects/part-2/case-06/case-06.ipynb
solutionNotebook: projects/part-2/case-06/solution/case-06-solution.ipynb
archive: public/downloads/part-2-case-06.zip
prerequisite: Расследования II-01–II-05
concepts: [связанные примеры, StratifiedGroupKFold, сдвиг распределения, macro-F1, бутстреп-интервал, карточка модели]
---

<div class="bureau-brief">
  <p class="bureau-kicker">Закупочный аудит · расследование II-06</p>
  <p><strong>Миссия</strong> воспроизвести оценку «Компаса», устранить пересечение источников и проверить зафиксированную модель на невиданной партии C.</p>
  <p><strong>Данные</strong> документированный синтетический стресс-тест на базе Digits; изменённые изображения не являются реальными сканами.</p>
  <p><strong>Результат</strong> macro-F1 для <code>vendor_split</code>, OOF macro-F1 групповой проверки на партиях A/B, macro-F1 на партии C с бутстреп-интервалом по <code>source_id</code>, карточка модели и закупочное мемо.</p>
  <p><strong>Перед началом</strong> требуется Часть I и расследования II-01–II-05; конфигурация II-05 вложена для самостоятельного запуска.</p>
  <p><strong>Маршрут</strong> продвинутый ML-аудит · 6–8 часов · основная работа в тетради · Python 3.12/3.13.</p>
</div>

<div class="materials-panel bureau-actions">
  <p><strong>Начать:</strong> <a href="../../downloads/part-2-case-06.zip">скачать ZIP</a> · <a href="../../datasets/compass_digits_synthetic_captures.csv.gz" download>скачать данные CSV.GZ</a> · <a href="https://colab.research.google.com/github/mkuziuk/python-tutorial/blob/main/projects/part-2/case-06/case-06.ipynb">Open in Colab</a></p>
  <p><strong>После работы:</strong> <a href="../compass-exam-solution/">финальный дебриф и готовая тетрадь</a> · <a href="../../materials/#ii-06--экзамен-для-компаса">состав архива</a></p>
  <p><strong>Справочник:</strong> <a href="../../field-guide/grouped-validation/">группы, сдвиг и карточка модели</a> · <a href="../../field-guide/cross-validation/">CV</a> · <a href="../../field-guide/classification-metrics/">macro-F1 и срезы</a></p>
</div>

## Сюжет

До решения о закупке остаётся один рабочий день. Антон передаёт финальную контрольную оценку с колонками `sample_id`, `source_id`, `variant_id`, `scanner_batch` и `vendor_split`. Результат снова выглядит убедительно. Тимур замечает, что у одной исходной цифры есть несколько почти одинаковых вариантов.

Если варианты одного `source_id` попали по разные стороны разбиения, тест перестаёт быть полностью новым: модель уже видела близкого родственника изображения. Кроме того, изолированная до финала партия C была синтетически изменена иначе, чем партии A и B. Она используется только после выбора процедуры и модели.

> Все измененные изображения в этом расследовании — **учебный синтетический стресс-тест**, созданный из встроенного Digits. Он демонстрирует механизм связанных наблюдений и сдвига, но не имитирует конкретный реальный сканер и не доказывает качество какой-либо внешней системы.

## Что расследуем

1. Проведите source audit A/B: форма, типы, диапазоны, пропуски, дубликаты,
   распределение `digit` и размеры групп `source_id`; до фиксации решения не
   читайте метки, пиксели, статистики и примеры C.
2. Воспроизведите `vendor_split` и его macro-F1 без изменения процедуры.
3. Измерьте, сколько источников пересекают обучающую и тестовую выборки поставщика, и покажите несколько родственных пар.
4. Замените построчное разбиение на `StratifiedGroupKFold(groups=source_id)`
   для партий A/B и на одних фолдах сравните `DummyClassifier` с кандидатом.
5. Используйте зафиксированную в II-05 конфигурацию или её вложенную копию; не подбирайте параметры по партии C.
6. После фиксации групповой оценки откройте партию C и измерьте второй разрыв.
7. Рассчитайте показатели по классам и бутстреп-интервал macro-F1, пересэмплируя **источники**, а не строки.
8. Заполните карточку модели и закупочное мемо.

Генератор данных детерминирован и спроектирован так, чтобы разница macro-F1 между оценкой поставщика и групповой оценкой, а также между групповой оценкой и оценкой на партии C составляла не менее 0.05. Ваша работа — подтвердить разрывы корректной процедурой, а не подгонять код к пороговому числу.

## Код расследования

Финальное расследование начинается с файла. Тетрадь проверяет документированный
синтетический CSV.GZ и создаёт `DataFrame` со связанными снимками и служебными
полями. Сначала важно проверить не только первые строки, но и границы каждого
поля: пропуски и дубликаты способны изменить число независимых объектов, а
неожиданный диапазон пикселей — смысл признаков.

```python
checksum_fields = (
    DATA_DIR / "CHECKSUMS.sha256"
).read_text(encoding="utf-8").split()
expected_sha256, checked_filename = checksum_fields
capture_path = DATA_DIR / "digits_compass.csv.gz"
# Контрольную сумму проверяем до чтения: метрики относятся к точной версии производного файла.
assert checked_filename == capture_path.name
assert sha256_file(capture_path) == expected_sha256, "Derivative изменён"

batch_boundary = pd.read_csv(capture_path, usecols=["scanner_batch"])
c_file_rows = [
    position + 1
    for position, batch in enumerate(batch_boundary["scanner_batch"])
    if batch == "C"
]
development_file_rows = [
    position + 1
    for position, batch in enumerate(batch_boundary["scanner_batch"])
    if batch != "C"
]
development = pd.read_csv(capture_path, skiprows=c_file_rows)
pixel_columns = [
    f"pixel_{row}_{column}" for row in range(8) for column in range(8)
]
assert development["scanner_batch"].isin(["A", "B"]).all()
display(development.head())
print("Форма A/B:", development.shape)
print("Пропусков:", development.isna().sum().sum())
print("Полных дубликатов:", development.duplicated().sum())
display(development["digit"].value_counts().sort_index())
```

Манифест фиксирует 5 838 строк целиком, но ранняя проверка читает только 5 388
строк A/B, 64 числовых пиксельных столбца, цель 0–9 и 1 347 `source_id`.
Последнее число меньше числа строк: оно заранее предупреждает, что `sample_id`
не задаёт единицу независимости. Оставшиеся 450 строк C физически читаются
только после фиксации процедуры и модели.

После аудита воспроизведите процедуру поставщика без изменения модели или
разбиения. Macro-F1 усредняет F1 классов с одинаковым весом и потому подходит
для десяти цифр лучше одной общей accuracy:

```python
vendor_model = locked_model()
vendor_model.fit(X_development[vendor_train_mask], y_development[vendor_train_mask])
vendor_predictions = vendor_model.predict(X_development[vendor_test_mask])
vendor_macro_f1 = f1_score(
    y_development[vendor_test_mask], vendor_predictions,
    labels=np.arange(10), average="macro", zero_division=0,
)
```

Результат 1,000 ещё не означает работу на новых источниках. Если один
`source_id` встречается с обеих сторон, разные строки являются вариантами
одного исходного изображения:

```python
vendor_train_sources = set(development.loc[vendor_train_mask, "source_id"])
vendor_test_sources = set(development.loc[vendor_test_mask, "source_id"])
leaked_sources = vendor_train_sources & vendor_test_sources
```

Пересекаются все источники A/B, поэтому для ответа о новых исходниках
материализуйте групповые фолды один раз. И baseline без пиксельной информации,
и кандидат должны получить буквально одинаковые индексы:

```python
grouped_splits = list(
    grouped_cv.split(X_development, y_development, groups=source_groups)
)
baseline_predictions = cross_val_predict(
    DummyClassifier(strategy="most_frequent"),
    X_development, y_development, groups=source_groups, cv=grouped_splits,
)
grouped_predictions = cross_val_predict(
    locked_model(),
    X_development, y_development, groups=source_groups, cv=grouped_splits,
)
```

Baseline показывает нижний ориентир, а grouped-оценка кандидата около 0,888
отделяет полезность пикселей от завышения построчного теста. Только после этого
можно один раз прочитать оставшиеся строки C:

```python
batch_c = pd.read_csv(
    capture_path,
    skiprows=development_file_rows,
)
assert batch_c["scanner_batch"].eq("C").all()
```

После единственной финальной оценки допустимы описательные срезы уже полученных
прогнозов, но не изменение модели или решения. Интервал неопределенности обязан ресемплировать
`source_id`, а не связанные строки:

```python
def source_bootstrap_interval(
    y_true, y_pred, groups, *, repeats=1_000, confidence=0.95, random_state=42
):
    unique_groups = np.unique(groups)
    positions_by_group = {
        group: np.flatnonzero(groups == group) for group in unique_groups
    }
    rng = np.random.default_rng(random_state)
    scores = np.empty(repeats)
    for repeat in range(repeats):
        sampled_groups = rng.choice(
            unique_groups, size=len(unique_groups), replace=True
        )
        sampled_positions = np.concatenate(
            [positions_by_group[group] for group in sampled_groups]
        )
        scores[repeat] = f1_score(
            y_true[sampled_positions], y_pred[sampled_positions],
            labels=np.arange(10), average="macro", zero_division=0,
        )
    alpha = 1 - confidence
    return tuple(np.quantile(scores, [alpha / 2, 1 - alpha / 2]))

batch_c_interval = source_bootstrap_interval(
    y_batch_c, batch_c_predictions, batch_c["source_id"].to_numpy()
)
```

В тетради после каждой таблицы и галереи сформулировано, что именно она
подтверждает и чего не доказывает. Итоговая записка автоматически подставляет
фактические оценки, разрывы, интервал, слабые классы и частые направления
ошибок, поэтому вывод можно проверить по показанным результатам.

## Что сдать

- выполненный `case-06.ipynb` с проверкой идентификаторов и трёх оценок;
- доказательство пересечения `source_id` в разбиении поставщика;
- групповую кросс-валидацию без пересечения источников;
- изолированную до финала и затем отдельно оценённую партию C;
- бутстреп-интервал по источникам и анализ по классам;
- заполненную карточку модели;
- закупочное мемо с решением и условиями возможного пересмотра.

## Рубрика

| Критерий | Зачёт |
| --- | --- |
| Воспроизведение | Разбиение поставщика пересчитано как есть; найдено и измерено пересечение источников. |
| Группы | Ни один `source_id` не пересекает обучающую и проверочную части `StratifiedGroupKFold`. |
| Изолированная проверка | Партия C не используется для выбора модели или порога. |
| Неопределённость | Бутстреп пересэмплирует независимые источники; интервал не выдаётся за гарантию. |
| Документы | Карточка модели называет назначение, данные, метрики, ограничения и недопустимые применения. |
| Вердикт | Закупка приостановлена до независимой проверки на данных целевой задачи; личное мошенничество не объявлено доказанным. |

## Финальный вопрос мемо

Какая именно часть демонстрационного качества объясняется родственными образцами, а какая исчезает при сдвиге партии? Укажите доказанные процедурные дефекты, ограничения синтетического теста и условия, при которых Бюро могло бы вернуться к оценке продукта.

Завершив документы, откройте [финальный дебриф](../compass-exam-solution/). Он фиксирует каноническое решение арки, но не заменяет ваш собственный ход доказательства.
