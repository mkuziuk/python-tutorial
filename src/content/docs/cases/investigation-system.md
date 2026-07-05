---
title: "Дело 05. Доска расследования"
description: "Строим маленькую доску расследования: классы, dataclass, методы, композиция объектов и сохранение дела в JSON."
concepts:
  - classes
  - dataclasses
  - methods
  - composition
  - JSON
  - pathlib
  - Rich
difficulty: "средний"
projectId: "case-05"
time: "120-150 минут"
---

<div class="case-meta">
  <p><strong>Миссия</strong> собрать людей, улики, надежность и заметки по ночному сигналу в одну управляемую доску.</p>
  <p><strong>Инструменты</strong> классы, `dataclass`, методы, композиция, `json`, `pathlib`, Rich.</p>
  <p><strong>Результат</strong> консольная доска дела, которая загружает JSON, ищет по уликам и сохраняет обновленный снимок.</p>
</div>

<div class="materials-panel">
  <p><strong>Быстрые ссылки:</strong> <a href="../../downloads/case-05.zip">case-05.zip</a> · <a href="../../materials/">материалы всех дел</a> · <a href="../investigation-system-solution/">разбор решения</a></p>
  <p><strong>Справочник:</strong> <a href="../../field-guide/classes/">classes</a> · <a href="../../field-guide/dataclasses/">dataclasses</a> · <a href="../../field-guide/json/">JSON</a> · <a href="../../field-guide/pathlib/">pathlib</a> · <a href="../../field-guide/dict/">dict</a> · <a href="../../field-guide/list/">list</a> · <a href="../../field-guide/functions/">functions</a> · <a href="../../field-guide/rich/">Rich</a></p>
</div>

## Проблема

В первых четырех делах команда собрала много отдельных материалов: анонимную записку, похожие отчеты, письма, папку после ночного сигнала, логи и заметки. Отдельные скрипты помогли ответить на конкретные вопросы, но теперь расследование нужно держать целиком.

Вопрос дела: как собрать людей, улики, заметки, теги и надежность источников в одну модель, чтобы к ней можно было вернуться завтра и не потерять цепочку событий?

Объекты полезны, когда у данных появляется собственное поведение. Улика - это не только набор полей: она должна проверять надежность, отвечать на поисковый запрос и превращаться обратно в JSON.

```python
evidence_id = item["evidence_id"]
title = item["title"]
tags = item["tags"]
```

Словарь остается удобным форматом для чтения файла, но внутри программы понятнее работать с объектами: `Evidence` хранит поля одной улики рядом с проверками и поиском, `Investigation` управляет всей коллекцией, а `CaseRepository` отвечает за JSON.

Скачайте learner-набор [case-05.zip](../../downloads/case-05.zip) или откройте папку `projects/case-05/` в репозитории.

Внутри:

- `investigation_system.py` - стартовый файл со скелетом классов;
- `data/case_seed.json` - исходное дело с участниками, уликами и первой заметкой;
- `requirements.txt` - версия Rich для таблиц;
- `check_result.txt` - форма ожидаемого результата.

Полный код лежит отдельно: [Разбор полного решения](../investigation-system-solution/).

## Стратегия

Мы разложим дело на [объекты и классы](../../field-guide/classes/):

- `Evidence` - одна улика: ID, тип, заголовок, источник, текст, теги и надежность;
- `Person` - участник дела;
- `CaseNote` - заметка расследования;
- `Investigation` - главное дело, которое содержит списки участников, улик и заметок;
- `CaseRepository` - маленький класс для чтения и записи JSON.

Это называется композицией: один объект состоит из других объектов. `Investigation` не наследуется от `Evidence`; оно просто хранит внутри список `Evidence`. Такое разделение удерживает границы: улика знает про свои поля, дело знает про коллекции улик, а репозиторий знает только про файл.

Схема будет такой:

```text
CaseRepository
  -> load()
     -> Investigation
        -> участники
        -> улики
        -> заметки
  -> save(investigation)
```

[JSON](../../field-guide/json/) остается форматом хранения, а классы становятся удобной рабочей моделью внутри программы.

## Сборка инструмента

Сначала подготовьте окружение.

### Windows PowerShell

```powershell
cd path\to\case-05
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Если PowerShell не разрешает запуск `Activate.ps1`, выполните в этом же окне:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### macOS или Linux

```bash
cd path/to/case-05
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Проверьте стартовый файл:

```bash
python investigation_system.py
```

Он уже загружает JSON и показывает краткую сводку. Теперь добавим поведение.

### Улика как объект

[`dataclass`](../../field-guide/dataclasses/) сам создает метод `__init__()`: нам не нужно вручную присваивать каждое поле. Добавьте в `Evidence` метод `__post_init__()`. Он запускается сразу после создания объекта.

```python
def __post_init__(self):
    self.evidence_id = self.evidence_id.strip()
    self.kind = self.kind.strip()
    self.title = self.title.strip()
    self.source = self.source.strip()
    self.body = self.body.strip()
    self.tags = sorted({tag.strip().casefold() for tag in self.tags if tag.strip()})

    if not self.evidence_id:
        raise ValueError("Evidence ID must not be empty")
    if not 1 <= self.reliability <= 5:
        raise ValueError("Evidence reliability must be between 1 and 5")
```

Здесь объект защищает свои данные: пустой ID и надежность вне шкалы от 1 до 5 не проходят. Если эту проверку оставить снаружи, любой другой участок программы сможет случайно создать сломанную улику.

Теперь научим улику превращаться обратно в [словарь](../../field-guide/dict/):

```python
def to_dict(self):
    return {
        "evidence_id": self.evidence_id,
        "kind": self.kind,
        "title": self.title,
        "source": self.source,
        "body": self.body,
        "tags": self.tags,
        "reliability": self.reliability,
    }
```

Метод `from_dict()` уже есть в стартовом файле. Вместе `from_dict()` и `to_dict()` образуют мост между JSON и объектом.

### Поиск по уликам

Метод `matches()` должен проверить запрос сразу в нескольких полях. Это лучше, чем писать такую проверку снаружи каждый раз: вся логика поиска по одной улике живет рядом с данными этой улики.

```python
def matches(self, query):
    normalized_query = query.casefold().strip()
    if not normalized_query:
        return True

    haystack = " ".join(
        [
            self.evidence_id,
            self.kind,
            self.title,
            self.source,
            self.body,
            *self.tags,
        ]
    ).casefold()
    return normalized_query in haystack
```

`casefold()` похож на `lower()`, но лучше подходит для текстового поиска: он аккуратнее нормализует регистр в разных языках.

Для красивого вывода добавьте короткую выдержку текста:

```python
def short_body(self, limit=90):
    compact = " ".join(self.body.split())
    if len(compact) <= limit:
        return compact
    return f"{compact[: limit - 3].rstrip()}..."
```

### Участники и заметки

У `Person` и `CaseNote` тоже нужен путь обратно в JSON. Они проще, чем `Evidence`, поэтому им хватает `to_dict()` без отдельного поиска или валидации.

```python
def to_dict(self):
    return {
        "person_id": self.person_id,
        "name": self.name,
        "role": self.role,
        "contact": self.contact,
        "notes": self.notes,
    }
```

Для `CaseNote`:

```python
def to_dict(self):
    return {
        "author": self.author,
        "text": self.text,
        "created_at": self.created_at,
    }
```

Можно добавить маленький метод для подписи участника:

```python
def label(self):
    return f"{self.name} - {self.role}"
```

Методы не обязаны быть большими. Главное, что они живут рядом с данными, к которым относятся.

### Дело как композиция

Теперь главный класс `Investigation`. Он содержит не сырые словари, а [списки](../../field-guide/list/) объектов.

Добавьте метод `to_dict()`:

```python
def to_dict(self):
    return {
        "case_id": self.case_id,
        "title": self.title,
        "summary": self.summary,
        "people": [person.to_dict() for person in self.people],
        "evidence": [item.to_dict() for item in self.evidence],
        "notes": [note.to_dict() for note in self.notes],
    }
```

Теперь добавим операции дела.

```python
def evidence_by_id(self, evidence_id):
    normalized_id = evidence_id.casefold()
    for item in self.evidence:
        if item.evidence_id.casefold() == normalized_id:
            return item
    return None
```

Если совпадения нет, функция возвращает `None`: это обычный способ сказать "ничего не найдено".

```python
def add_evidence(self, item):
    if self.evidence_by_id(item.evidence_id) is not None:
        raise ValueError(f"Evidence {item.evidence_id!r} already exists")
    self.evidence.append(item)
```

Так дело само следит, чтобы два объекта не получили один ID.

```python
def add_note(self, author, text, created_at):
    self.notes.append(CaseNote(author=author, text=text, created_at=created_at))
```

Поиск становится коротким, потому что подробности спрятаны внутри `Evidence.matches()`:

```python
def find_evidence(self, query):
    return [item for item in self.evidence if item.matches(query)]
```

Сделаем индекс по тегам. Это пригодится, когда улик станет больше.

```python
def tag_index(self):
    index = {}
    for item in self.evidence:
        for tag in item.tags:
            index.setdefault(tag, []).append(item)
    return {
        tag: sorted(items, key=lambda item: item.evidence_id)
        for tag, items in sorted(index.items())
    }
```

И оставим сортировку приоритетных улик:

```python
def priority_evidence(self, limit=3):
    return sorted(self.evidence, key=lambda item: (-item.reliability, item.evidence_id))[:limit]
```

### Репозиторий JSON

`CaseRepository` отвечает только за хранение. Он не решает, что такое улика, и не рисует таблицы. Если позже заменить JSON-файл на базу данных, менять нужно будет этот слой, а не методы `Evidence` и `Investigation`.

```python
class CaseRepository:
    def __init__(self, path):
        self.path = path

    def load(self):
        raw_data = json.loads(self.path.read_text(encoding="utf-8"))
        return Investigation.from_dict(raw_data)

    def save(self, investigation):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(investigation.to_dict(), ensure_ascii=False, indent=2)
        self.path.write_text(f"{payload}\n", encoding="utf-8")
```

Обратите внимание на `ensure_ascii=False`: без него русские буквы превратятся в последовательности вида `\u0434`.

### Отчет в терминале

[Rich](../../field-guide/rich/) нужен только для вывода. Данные и логика остаются обычным Python.

```python
def render_search_results(query, results):
    table = Table(title=f"Поиск: {query}")
    table.add_column("ID", style="cyan")
    table.add_column("Название")
    table.add_column("Фрагмент")

    for item in results:
        table.add_row(item.evidence_id, item.title, item.short_body())

    console.print(table)
```

Функция сборки отчета загружает исходный JSON, делает автоматическую проверку и сохраняет новый снимок.

```python
def build_report(seed_path=SEED_PATH, output_path=OUTPUT_PATH):
    investigation = CaseRepository(seed_path).load()
    signal_matches = investigation.find_evidence("сигнал")
    investigation.add_note(
        author="Доска расследования",
        text=f"Автоматический поиск по слову 'сигнал' нашел улик: {len(signal_matches)}.",
        created_at="2026-02-12T12:30:00",
    )
    CaseRepository(output_path).save(investigation)
    return investigation
```

В `main()` остается связать шаги:

```python
def main():
    investigation = build_report()
    render_overview(investigation)
    render_search_results("сигнал", investigation.find_evidence("сигнал"))
    console.print(f"\n[green]JSON-снимок сохранен:[/green] {OUTPUT_PATH.name}")
```

## Проверка

Запустите:

```bash
python investigation_system.py
```

Ожидаемый смысл результата:

```text
Ночной сигнал архива
Участники: 4
Улики: 5
Приоритетные улики:
EV-001  Анонимная записка      5/5
EV-002  Журнал ночного сигнала 5/5
EV-004  Дубли фотоиндекса      5/5

Поиск: сигнал
EV-001
EV-002
EV-004

JSON-снимок сохранен: case_report.json
```

После запуска рядом со скриптом появится `case_report.json`. Откройте его и проверьте, что в `notes` появилась новая заметка от доски расследования.

Если поиск по слову `сигнал` ничего не находит, проверьте `Evidence.matches()` и `Investigation.find_evidence()`. Если файл не сохраняется, вернитесь к `CaseRepository.save()`.

## Что мы использовали

- [Установка Python](../../field-guide/install-python/) - Python 3.14+, виртуальная среда и читаемые типы.
- [Списки `list`](../../field-guide/list/) - коллекции участников, улик и заметок.
- [Словари `dict`](../../field-guide/dict/) - JSON-структура до превращения в объекты.
- [Классы](../../field-guide/classes/) - собственные типы для предметной области.
- [dataclasses](../../field-guide/dataclasses/) - короткое описание объектов без ручного `__init__()`.
- Методы - поведение рядом с данными.
- Композиция - `Investigation` состоит из `Person`, `Evidence` и `CaseNote`.
- [JSON](../../field-guide/json/) persistence - загрузка исходного дела и сохранение обновленного снимка.
- [pathlib](../../field-guide/pathlib/) - переносимые пути к seed-файлу и отчету.
- [Rich](../../field-guide/rich/) - терминальная сводка без смешивания с моделью дела.

## Усложняем проект

1. Добавьте статус дела: `open`, `waiting`, `closed`.
2. Сделайте метод `evidence_by_tag(tag)`, который использует `tag_index()`.
3. Добавьте поле `created_at` для улик и отсортируйте их по времени.
4. Сохраняйте отдельный `case_summary.txt` для руководителя.
5. Добавьте командное меню: показать улики, найти по запросу, добавить заметку, сохранить.
6. Сделайте импорт улик из нескольких JSON-файлов.

Когда закончите, откройте [разбор полного решения](../investigation-system-solution/).
