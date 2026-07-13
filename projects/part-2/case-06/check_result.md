# Ожидаемая форма результата II-06

Данные
- SHA-256 совпадает с generation_report.json.
- 5 838 строк, 1 797 source_id, 64 pixel columns.
- sample_id уникальны; instructional_synthetic=True для каждой строки.
- Batches A, B и C и splits train, test, holdout присутствуют.

Vendor audit
- Все A/B source_id встречаются и в vendor train, и в vendor test.
- Vendor row-split macro-F1 = 1,00 для замороженной модели.

Честная проверка
- В каждом StratifiedGroupKFold пересечение source_id train/validation равно 0.
- Source-grouped OOF macro-F1 примерно 0,88–0,90.
- Sealed scanner-C macro-F1 примерно 0,63–0,67.
- Vendor -> grouped gap >= 0,05.
- Grouped -> scanner-C gap >= 0,05.
- Показаны per-class показатели, confusion matrix, error gallery и 95%
  source-level bootstrap interval для scanner C.

Артефакты
- artifacts/model_card.md прямо называет данные синтетическим стресс-тестом,
  содержит три оценки, ограничения и запрещённые применения.
- artifacts/procurement_memo.md содержит пять разделов, приостанавливает закупку
  и не утверждает личное мошенничество.
