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
prerequisite: Дела II-01–II-05
concepts: [related samples, StratifiedGroupKFold, distribution shift, macro-F1, bootstrap interval, model card]
---

<div class="bureau-brief">
  <p class="bureau-kicker">Закупочный аудит · дело II-06</p>
  <p><strong>Миссия</strong> воспроизвести оценку «Компаса», устранить пересечение источников и проверить зафиксированную модель на невиданной партии C.</p>
  <p><strong>Данные</strong> документированный синтетический стресс-тест на базе Digits; измененные изображения не являются реальными сканами.</p>
  <p><strong>Результат</strong> три уровня оценки, bootstrap-интервал, model card и закупочное мемо.</p>
  <p><strong>Перед началом</strong> требуется Часть I и дела II-01–II-05; конфигурация II-05 вложена для самостоятельного запуска.</p>
  <p><strong>Маршрут</strong> продвинутый ML-аудит · 6–8 часов · notebook-first · Python 3.12/3.13.</p>
</div>

<div class="materials-panel bureau-actions">
  <p><strong>Начать:</strong> <a href="../../downloads/part-2-case-06.zip">скачать ZIP</a> · <a href="../../datasets/compass_digits_synthetic_captures.csv.gz" download>скачать данные CSV.GZ</a> · <a href="https://colab.research.google.com/github/mkuziuk/python-tutorial/blob/main/projects/part-2/case-06/case-06.ipynb">Open in Colab</a></p>
  <p><strong>После работы:</strong> <a href="../compass-exam-solution/">финальный дебриф и готовый notebook</a> · <a href="../../materials/#ii-06--экзамен-для-компаса">состав архива</a></p>
  <p><strong>Справочник:</strong> <a href="../../field-guide/grouped-validation/">группы, сдвиг и model card</a> · <a href="../../field-guide/cross-validation/">CV</a> · <a href="../../field-guide/classification-metrics/">macro-F1 и срезы</a></p>
</div>

## Сюжет

До решения о закупке остается один рабочий день. Антон передает финальный benchmark с колонками `sample_id`, `source_id`, `variant_id`, `scanner_batch` и `vendor_split`. Результат снова выглядит убедительно. Тимур замечает, что у одной исходной цифры есть несколько почти одинаковых вариантов.

Если варианты одного `source_id` попали по разные стороны разбиения, тест перестает быть полностью новым: модель уже видела близкого родственника изображения. Кроме того, запечатанная партия C была синтетически изменена иначе, чем партии A и B. Она открывается только после выбора процедуры и модели.

> Все измененные изображения в этом деле — **учебный синтетический стресс-тест**, созданный из встроенного Digits. Он демонстрирует механизм связанных наблюдений и сдвига, но не имитирует конкретный реальный сканер и не доказывает качество какой-либо внешней системы.

## Что расследуем

1. Проверьте метаданные, уникальность `sample_id` и связи `source_id`/`variant_id`.
2. Воспроизведите `vendor_split` и его macro-F1 без изменения процедуры.
3. Измерьте, сколько источников пересекают vendor train/test, и покажите несколько родственных пар.
4. Замените построчный split на `StratifiedGroupKFold(groups=source_id)` для партий A/B.
5. Используйте зафиксированную в II-05 конфигурацию или ее вложенную копию; не подбирайте параметры по batch C.
6. После фиксации grouped-оценки откройте batch C и измерьте второй разрыв.
7. Рассчитайте per-class показатели и bootstrap-интервал macro-F1, ресемплируя **источники**, а не строки.
8. Заполните model card и закупочное мемо.

Генератор данных детерминирован и спроектирован так, чтобы разница macro-F1 между vendor и grouped evaluation, а также между grouped evaluation и batch C составляла не менее 0.05. Ваша работа — подтвердить разрывы корректной процедурой, а не подгонять код к пороговому числу.

## Код расследования

Финальное дело тоже начинается с файла. Notebook проверяет документированный синтетический CSV.GZ и создаёт `DataFrame` со связанными снимками и служебными полями:

```python
generation_report = json.loads(
    (DATA_DIR / "generation_report.json").read_text(encoding="utf-8")
)
capture_path = DATA_DIR / "digits_compass.csv.gz"
assert sha256_file(capture_path) == generation_report["sha256"], "Derivative изменён"

captures = pd.read_csv(capture_path)
pixel_columns = [
    f"pixel_{row}_{column}" for row in range(8) for column in range(8)
]
display(captures.head())
print("Форма DataFrame:", captures.shape)
```

После этого learner-ячейки намеренно воспроизводят процедуру поставщика до того, как предлагают ее исправить. Сначала пересчитайте vendor test без изменения модели или split; формула macro-F1 остается упражнением:

```python
vendor_model = locked_model()
vendor_model.fit(X_development[vendor_train_mask], y_development[vendor_train_mask])
vendor_predictions = vendor_model.predict(X_development[vendor_test_mask])
# TODO: посчитайте macro-F1 vendor test.
vendor_macro_f1 = float("nan")
print("Модель воспроизведена; формула macro-F1 ждёт TODO.")
```

Затем проверьте единицу независимости. Если один `source_id` встречается с обеих сторон, разные строки не означают новые исходные изображения:

```python
# TODO: постройте множества source_id train/test и их пересечение.
vendor_train_sources: set[str] = set()
vendor_test_sources: set[str] = set()
leaked_sources: set[str] = set()
print("Временный результат: пересечение не рассчитано. Выполните TODO.")
```

Следующая заглушка должна быть заменена на out-of-fold прогнозы зафиксированной модели с `groups=source_groups`. Batch C на этом этапе все еще закрыт:

```python
# TODO: замените временный baseline на cross_val_predict с groups=source_groups.
fallback = DummyClassifier(strategy="most_frequent").fit(X_development, y_development)
grouped_predictions = fallback.predict(X_development)
grouped_macro_f1 = f1_score(y_development, grouped_predictions, average="macro")
print(f"Временный baseline macro-F1: {grouped_macro_f1:.3f}")
```

И интервал неопределенности обязан ресемплировать `source_id`, а не связанные строки. Сигнатура и вызов уже заданы, реализация — часть экзамена:

```python
# TODO: реализуйте ресемплинг source_id и пересчёт macro-F1.
def source_bootstrap_interval(
    y_true, y_pred, groups, *, repeats=1_000, confidence=0.95, random_state=42
):
    return (float("nan"), float("nan"))

batch_c_interval = source_bootstrap_interval(
    y_batch_c, batch_c_predictions, batch_c["source_id"].to_numpy()
)
print("Bootstrap CI ждёт TODO.")
```

## Что сдать

- выполненный `case-06.ipynb` с проверкой идентификаторов и трех оценок;
- доказательство пересечения `source_id` в vendor split;
- grouped CV без пересечения источников;
- запечатанный до финала и затем отдельно оцененный batch C;
- source-level bootstrap-интервал и per-class анализ;
- заполненный model card;
- закупочное мемо с решением и условиями возможного пересмотра.

## Рубрика

| Критерий | Зачет |
| --- | --- |
| Воспроизведение | Vendor split пересчитан как есть; найдено и измерено пересечение источников. |
| Группы | Ни один `source_id` не пересекает train/validation в `StratifiedGroupKFold`. |
| Запечатанная проверка | Batch C не используется для выбора модели или порога. |
| Неопределенность | Bootstrap ресемплирует независимые источники; интервал не выдается за гарантию. |
| Документы | Model card называет назначение, данные, метрики, ограничения и недопустимые применения. |
| Вердикт | Закупка приостановлена до независимой task-specific проверки; личное мошенничество не объявлено доказанным. |

## Финальный вопрос мемо

Какая именно часть демонстрационного качества объясняется родственными образцами, а какая исчезает при сдвиге партии? Укажите доказанные процедурные дефекты, ограничения синтетического теста и условия, при которых Бюро могло бы вернуться к оценке продукта.

Завершив документы, откройте [финальный дебриф](../compass-exam-solution/). Он фиксирует каноническое решение арки, но не заменяет ваш собственный ход доказательства.
