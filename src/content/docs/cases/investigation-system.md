---
title: "Расследование 05. Доска расследования"
description: "Строим объектную доску из настоящих результатов I-01–I-04 и сохраняем происхождение каждой улики."
concepts:
  - classes
  - dataclasses
  - composition
  - JSON
  - связи объектов
  - валидация
difficulty: "средний"
projectId: "case-05"
time: "110-140 минут"
---

<div class="case-meta">
  <p><strong>Миссия</strong> превратить четыре проверенных отчёта в объекты улик, людей, гипотез и связей.</p>
  <p><strong>Инструменты</strong> `dataclass`, методы, композиция, индексы, JSON и проверка SHA-256.</p>
  <p><strong>Вход</strong> `data/artifacts/01-*.json` — `04-*.json` и `data/relationships.json`.</p>
  <p><strong>Результат</strong> `artifacts/05-case-board.json`.</p>
</div>

<div class="materials-panel">
  <p><strong>Быстрые ссылки:</strong> <a href="../../downloads/case-05.zip">case-05.zip</a> · <a href="../investigation-system-solution/">разбор решения</a></p>
  <p><strong>Справочник:</strong> <a href="../../field-guide/classes/">классы</a> · <a href="../../field-guide/dataclasses/">dataclass</a> · <a href="../../field-guide/json/">JSON</a></p>
</div>

## Почему доска теперь нужна

I-01–I-04 уже создали конкретные результаты. Поэтому программа не загружает заранее написанный пересказ. Она читает сами отчёты и сохраняет для каждой улики два идентификатора:

- `evidence_id` — ID улики на доске;
- `origin_finding_id` — ID вывода из предыдущего отчёта.

`relationships.json` содержит только людей, гипотезы и назначенные аналитиком связи. Факты и формулировки выводов берутся из созданных ранее файлов.

## Шаг 1. Описать улику

```python
@dataclass(slots=True)
class Evidence:
    evidence_id: str
    kind: str
    title: str
    summary: str
    source: str
    occurred_at: str
    origin_finding_id: str
    tags: list[str] = field(default_factory=list)
    reliability: int = 3
    effects: list[dict] = field(default_factory=list)
```

`__post_init__()` проверяет поля сразу после создания объекта:

```python
def __post_init__(self):
    self.evidence_id = self.evidence_id.strip()
    self.tags = sorted({tag.strip().casefold() for tag in self.tags if tag.strip()})
    if not self.evidence_id:
        raise ValueError("Evidence ID must not be empty")
    if not self.origin_finding_id:
        raise ValueError("Evidence must keep its origin finding ID")
    if not 1 <= self.reliability <= 5:
        raise ValueError("Evidence reliability must be between 1 and 5")
```

## Шаг 2. Описать связь с гипотезой

```python
@dataclass(slots=True)
class EvidenceLink:
    evidence_id: str
    hypothesis_id: str
    stance: str
    weight: int
```

`stance="support"` означает поддержку гипотезы, `stance="conflict"` — противоречие. На этом этапе программа только хранит связи. Баллы рассчитает I-06.

## Шаг 3. Проверить входные отчёты

`load_artifacts()` загружает четыре JSON-файла. Для I-01–I-03 функция сравнивает фактический SHA-256 с хэшем из `04-evidence-index.json`:

```python
expected = verified[investigation_id]["sha256"]
actual = file_sha256(artifacts[investigation_id]["path"])
if actual != expected:
    raise ValueError(f"Hash mismatch for {investigation_id}")
```

Если отчёт изменили после I-04, доска не строится молча.

## Шаг 4. Создать улики из выводов

Функция `finding()` ищет вывод по стабильному ID:

```python
authorship = finding(artifacts, "I-01", "F-I01-AUTHORSHIP")
matches = finding(artifacts, "I-02", "F-I02-TEXT-MATCHES")
lockout = finding(artifacts, "I-03", "F-I03-LOCKOUT")
timeline = finding(artifacts, "I-04", "F-I04-TIMELINE")
```

Затем `make_evidence()` создаёт объекты. Формулировка `summary` приходит из найденного вывода, а `origin_finding_id` сохраняет ссылку на него.

## Шаг 5. Проверить отношения

Перед добавлением связи убедитесь, что оба ID существуют:

```python
if link.evidence_id not in evidence_by_id:
    raise ValueError(f"Unknown evidence in link: {link.evidence_id}")
if link.hypothesis_id not in hypothesis_ids:
    raise ValueError(f"Unknown hypothesis in link: {link.hypothesis_id}")
```

Так опечатка не создаёт связь с несуществующей уликой или гипотезой.

## Шаг 6. Выполнить полезные запросы

Доска должна отвечать на вопросы, связанные с финалом:

```python
investigation.find_evidence("хронология")
investigation.find_evidence("Никита")
investigation.evidence_for_hypothesis("H-PHISHING")
```

Это заменяет прежний демонстрационный поиск одного слова. Каждый запрос используется для проверки собранной модели.

## Шаг 7. Сохранить доску

```bash
python investigation_system.py
python -m json.tool artifacts/05-case-board.json
python -m unittest discover -s tests
```

Ожидаемый файл содержит четыре `source_artifacts`, двенадцать улик и одиннадцать связей. I-06 загрузит этот файл без ручного копирования выводов.

## Что мы использовали

- `dataclass` для четырёх типов объектов;
- композицию вместо одного большого словаря;
- `__post_init__()` для проверки объектов;
- методы поиска и проверки ID;
- SHA-256 для проверки входных отчётов;
- `origin_finding_id` для происхождения улики.

## Усложняем проект

1. Добавьте метод поиска всех улик без связей.
2. Постройте индекс `person_id → evidence_id`.
3. Запретите сохранять доску, если у двух улик одинаковый ID без учёта регистра.
