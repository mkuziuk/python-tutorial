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
  - comprehensions
  - аннотации типов
  - unittest
difficulty: "средний"
projectId: "case-05"
time: "120-150 минут"
---

<div class="case-meta">
  <p><strong>Миссия</strong> собрать людей, улики, сведения об их надёжности и заметки по ночному сигналу на одной управляемой доске.</p>
  <p><strong>Инструменты</strong> классы, `dataclass`, методы, композиция, `json`, `pathlib`, Rich.</p>
  <p><strong>Результат</strong> консольная доска дела, которая загружает JSON, ищет по уликам и сохраняет обновленный снимок.</p>
  <p><strong>Маршрут</strong> средний · 120–150 минут · Python 3.13+</p>
</div>

<div class="materials-panel">
  <p><strong>Быстрые ссылки:</strong> <a href="../../downloads/case-05.zip">case-05.zip</a> · <a href="../../materials/">материалы всех дел</a> · <a href="../investigation-system-solution/">разбор решения</a></p>
  <p><strong>Справочник:</strong> <a href="../../field-guide/classes/">classes</a> · <a href="../../field-guide/dataclasses/">dataclasses</a> · <a href="../../field-guide/type-hints/">аннотации типов</a> · <a href="../../field-guide/comprehensions/">включения</a> · <a href="../../field-guide/json/">JSON</a> · <a href="../../field-guide/pathlib/">pathlib</a> · <a href="../../field-guide/dict/">dict</a> · <a href="../../field-guide/list/">list</a> · <a href="../../field-guide/functions/">functions</a> · <a href="../../field-guide/rich/">Rich</a> · <a href="../../field-guide/testing/">unittest</a></p>
</div>

## Проблема

В первых четырёх делах команда собрала много отдельных материалов: анонимную записку, похожие отчёты, письма, папку после ночного сигнала, журналы и заметки. Отдельные скрипты помогли ответить на конкретные вопросы, но теперь нужно увидеть расследование целиком.

Вопрос дела: как объединить людей, улики, заметки, теги и сведения о надёжности источников в одной модели, чтобы завтра продолжить работу и не потерять цепочку событий?

`Evidence` хранит поля одной улики и предоставляет методы для проверки надёжности, поиска и преобразования в JSON.

```python
evidence_id = item["evidence_id"]
title = item["title"]
tags = item["tags"]
```

Словарь остаётся удобным форматом для чтения файла, а внутри программы используются объекты: `Evidence` работает с одной уликой, `Investigation` — с коллекциями объектов, а `CaseRepository` загружает и сохраняет JSON.

Скачайте учебный набор [case-05.zip](../../downloads/case-05.zip) или откройте папку `projects/case-05/` в репозитории.

Внутри:

- `investigation_system.py` — пустой стартовый файл;
- `data/case_seed.json` — исходное дело с участниками, уликами и первой заметкой;
- `requirements.txt` — версия Rich для таблиц;
- `check_result.txt` — форма ожидаемого результата.

Полный код лежит отдельно: [Разбор полного решения](../investigation-system-solution/).

## Стратегия

Мы разложим дело на [объекты и классы](../../field-guide/classes/):

- `Evidence` — одна улика: ID, тип, заголовок, источник, текст, дата с доступной точностью, теги и надёжность;
- `Person` — участник дела;
- `CaseNote` — заметка расследования;
- `Investigation` — главное дело, которое содержит списки участников, улик и заметок;
- `CaseRepository` — небольшой класс для чтения и записи JSON.

Это называется композицией: один объект содержит другие объекты. `Investigation` хранит список `Evidence` без наследования. `Evidence` проверяет и ищет данные одной улики, `Investigation` работает с коллекциями, а `CaseRepository` читает и записывает файл.

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

[JSON](../../field-guide/json/) остаётся форматом хранения, а классы становятся удобной рабочей моделью внутри программы.

## Сборка инструмента

Сначала подготовьте окружение. Нужен Python 3.13 или новее; перед началом проверьте `py -3 --version` на Windows или `python3 --version` на macOS и Linux.

### Windows PowerShell

```powershell
cd path\to\case-05
py -3 -m venv .venv
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
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Запустите стартовый файл:

```bash
python investigation_system.py
```

Пока программа ничего не выводит: это нормально. Откройте `investigation_system.py` и сначала создайте основу программы: импорты, пути, консоль и классы с полями.

```python
from dataclasses import dataclass, field
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

# case_seed.json не изменяем; новый результат записываем в case_report.json.
DATA_DIR = Path(__file__).with_name("data")
SEED_PATH = DATA_DIR / "case_seed.json"
OUTPUT_PATH = Path(__file__).with_name("case_report.json")
console = Console()


# slots запрещает случайно создать поле с опечаткой и фиксирует заявленную структуру объекта.
@dataclass(slots=True)
class Evidence:
    # evidence_id остаётся постоянным идентификатором; title можно менять для более ясного отображения.
    evidence_id: str
    kind: str
    title: str
    source: str
    body: str
    created_at: str
    # default_factory=list создаёт отдельный список tags для каждого Evidence.
    tags: list[str] = field(default_factory=list)
    # Надёжность использует учебную шкалу 1–5; середина 3 выбрана значением по умолчанию.
    reliability: int = 3

    @classmethod
    def from_dict(cls, data):
        # cls(...) создаёт Evidence и затем автоматически запускает __post_init__().
        return cls(
            evidence_id=str(data["evidence_id"]),
            kind=str(data["kind"]),
            title=str(data["title"]),
            source=str(data["source"]),
            body=str(data["body"]),
            created_at=str(data["created_at"]),
            # Отсутствующие tags превращаются в новый пустой список, а не в общий изменяемый объект.
            tags=[str(tag) for tag in data.get("tags", [])],
            reliability=int(data.get("reliability", 3)),
        )


@dataclass(slots=True)
class Person:
    person_id: str
    name: str
    role: str
    contact: str
    # У каждого участника свой список заметок; изменения одного Person не затронут другого.
    notes: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data):
        # Преобразование выполняется на границе JSON: внутри программы работаем уже с Person.
        return cls(
            person_id=str(data["person_id"]),
            name=str(data["name"]),
            role=str(data["role"]),
            contact=str(data["contact"]),
            notes=[str(note) for note in data.get("notes", [])],
        )


@dataclass(slots=True)
class CaseNote:
    author: str
    text: str
    created_at: str

    @classmethod
    def from_dict(cls, data):
        return cls(
            author=str(data["author"]),
            text=str(data["text"]),
            created_at=str(data["created_at"]),
        )


@dataclass(slots=True)
class Investigation:
    case_id: str
    title: str
    summary: str
    # Композиция отражает модель дела: участники и улики принадлежат конкретному расследованию.
    people: list[Person] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    # Заметки дела хранятся объектами CaseNote, чтобы автор и время не потерялись рядом с текстом.
    notes: list[CaseNote] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data):
        # Вложенные словари превращаем в объекты, из которых состоит дело.
        return cls(
            case_id=str(data["case_id"]),
            title=str(data["title"]),
            summary=str(data["summary"]),
            people=[Person.from_dict(item) for item in data.get("people", [])],
            evidence=[Evidence.from_dict(item) for item in data.get("evidence", [])],
            notes=[CaseNote.from_dict(item) for item in data.get("notes", [])],
        )
```

Во всех следующих блоках с методами сохраняйте отступ внутри нужного `class`.

### Улика как объект

[`dataclass`](../../field-guide/dataclasses/) сам создаёт метод `__init__()`: нам не нужно вручную присваивать каждое поле. После объявления полей добавьте в `Evidence` метод `__post_init__()`. Он запускается сразу после создания объекта.

```python
    def __post_init__(self):
        # dataclass вызывает этот метод после __init__: здесь очищаем входные данные.
        self.evidence_id = self.evidence_id.strip()
        self.kind = self.kind.strip()
        self.title = self.title.strip()
        self.source = self.source.strip()
        self.body = self.body.strip()
        self.created_at = self.created_at.strip()
        # Множество убирает дубли, а casefold() выравнивает регистр тегов.
        self.tags = sorted({tag.strip().casefold() for tag in self.tags if tag.strip()})

        # __post_init__() отклоняет улики с пустыми evidence_id или created_at.
        if not self.evidence_id:
            raise ValueError("Evidence ID must not be empty")
        if not self.created_at:
            raise ValueError("Evidence created_at must not be empty")
        if not 1 <= self.reliability <= 5:
            raise ValueError("Evidence reliability must be between 1 and 5")
```

Здесь объект защищает свои данные: пустые ID и `created_at`, а также надёжность вне шкалы от 1 до 5 не проходят проверку. `created_at` остаётся строкой ISO 8601: точное время храним только там, где его указал источник. Для EV-006 известна лишь дата и условие «до 18:00», поэтому в поле стоит `2026-03-14`, а доступная точность записана в описании.

Теперь научим улику превращаться обратно в [словарь](../../field-guide/dict/):

```python
    def to_dict(self):
        # Имена ключей повторяют входную схему, поэтому объект можно сохранить и затем загрузить снова.
        return {
            "evidence_id": self.evidence_id,
            "kind": self.kind,
            "title": self.title,
            "source": self.source,
            "body": self.body,
            "created_at": self.created_at,
            "tags": self.tags,
            "reliability": self.reliability,
        }
```

Метод `Evidence.from_dict()` создаёт объект из словаря JSON, а `Evidence.to_dict()` создаёт словарь для сохранения в JSON.

### Поиск по уликам

Метод `Evidence.matches()` проверяет запрос во всех поисковых полях одной улики. Метод позволяет не дублировать эту проверку в других частях программы.

```python
    def matches(self, query):
        normalized_query = query.casefold().strip()
        # Пустой запрос означает «без фильтра», поэтому подходит любая улика.
        if not normalized_query:
            return True

        haystack = " ".join(
            [
                self.evidence_id,
                self.kind,
                self.title,
                self.source,
                self.body,
                self.created_at,
                *self.tags,
            ]
        ).casefold()
        # matches() ищет query как подстроку в полях улики.
        return normalized_query in haystack
```

`casefold()` похож на `lower()`, но лучше подходит для текстового поиска: он аккуратнее нормализует регистр в разных языках.

Для красивого вывода добавьте короткую выдержку текста:

```python
    def short_body(self, limit=90):
        # Нормализуем пробелы до обрезки, чтобы limit применялся к отображаемой строке.
        compact = " ".join(self.body.split())
        # limit измеряется в символах уже после нормализации пробелов.
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
        # label() возвращает текст для интерфейса.
        return f"{self.name} - {self.role}"
```

Методы не обязаны быть большими. Главное, что они живут рядом с данными, к которым относятся.

### Дело как композиция

Теперь главный класс `Investigation`. Он содержит не сырые словари, а [списки](../../field-guide/list/) объектов.

Добавьте метод `to_dict()`:

```python
def to_dict(self):
    # Для JSON разворачиваем композицию обратно в словари и списки.
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
        # Поиск ID нечувствителен к регистру, но возвращает исходный объект без копирования.
        normalized_id = evidence_id.casefold()
        for item in self.evidence:
            if item.evidence_id.casefold() == normalized_id:
                return item
        return None
```

Если совпадения нет, функция возвращает `None` — обычный способ сообщить, что ничего не найдено.

```python
    def add_evidence(self, item):
        # ID сравниваются без учёта регистра: EV-01 и ev-01 — одна логическая улика.
        if self.evidence_by_id(item.evidence_id) is not None:
            raise ValueError(f"Evidence {item.evidence_id!r} already exists")
        # Список изменяем только после проверки, чтобы ошибка не оставила дело в промежуточном состоянии.
        self.evidence.append(item)
```

Так дело само следит, чтобы два объекта не получили один ID.

```python
    def add_note(self, author, text, created_at):
        # Создаём CaseNote внутри метода, сохраняя единый формат добавления заметок.
        self.notes.append(CaseNote(author=author, text=text, created_at=created_at))
```

Поиск становится коротким, потому что подробности спрятаны внутри `Evidence.matches()`:

```python
    def find_evidence(self, query):
        # Investigation перебирает улики, а Evidence.matches() проверяет совпадение с запросом.
        return [item for item in self.evidence if item.matches(query)]
```

Сделаем индекс по тегам. Это пригодится, когда улик станет больше.

```python
    def tag_index(self):
        # Одна улика попадёт в несколько списков, если у неё несколько тегов.
        index = {}
        for item in self.evidence:
            for tag in item.tags:
                index.setdefault(tag, []).append(item)
        # Сортируем и теги, и улики, чтобы JSON и таблицы не зависели от порядка входных данных.
        return {
            tag: sorted(items, key=lambda item: item.evidence_id)
            for tag, items in sorted(index.items())
        }
```

И оставим сортировку приоритетных улик:

```python
    def priority_evidence(self, limit=3):
        # При равной надёжности ID служит дополнительным ключом и сохраняет стабильный порядок.
        # Минус превращает обычную сортировку по возрастанию в порядок от надёжных улик к слабым.
        return sorted(self.evidence, key=lambda item: (-item.reliability, item.evidence_id))[:limit]
```

### Репозиторий JSON

`CaseRepository` загружает и сохраняет `Investigation` в JSON. При переходе на базу данных потребуется заменить репозиторий; методы поиска и изменения останутся в `Evidence` и `Investigation`.

```python
# CaseRepository читает и записывает JSON, а Investigation содержит правила поиска и изменения дела.
class CaseRepository:
    def __init__(self, path):
        self.path = path

    def load(self):
        # Репозиторий возвращает готовый объект, чтобы остальной код не зависел от структуры JSON.
        raw_data = json.loads(self.path.read_text(encoding="utf-8"))
        return Investigation.from_dict(raw_data)

    def save(self, investigation):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # to_dict() задаёт точные ключи и значения выходного JSON.
        payload = json.dumps(investigation.to_dict(), ensure_ascii=False, indent=2)
        self.path.write_text(f"{payload}\n", encoding="utf-8")
```

Обратите внимание на `ensure_ascii=False`: без него русские буквы превратятся в последовательности вида `\u0434`.

### Отчёт в терминале

[Rich](../../field-guide/rich/) нужен только для вывода. Данные и логика остаются обычным Python.

Сначала соберём обзор всего дела. Помимо таблиц, он показывает контрольные количества: так сразу видно, все ли участники, улики и заметки загрузились из JSON.

```python
def render_overview(investigation):
    console.print(f"[bold cyan]Дело: {investigation.title}[/bold cyan]")
    console.print(investigation.summary)
    console.print(f"Участников: {len(investigation.people)}")
    console.print(f"Улик: {len(investigation.evidence)}")
    console.print(f"Заметок: {len(investigation.notes)}")

    people_table = Table(title="Участники")
    people_table.add_column("ID", style="cyan")
    people_table.add_column("Имя")
    people_table.add_column("Роль")

    for person in investigation.people:
        people_table.add_row(person.person_id, person.name, person.role)

    evidence_table = Table(title="Приоритетные улики")
    evidence_table.add_column("ID", style="cyan")
    evidence_table.add_column("Тип")
    evidence_table.add_column("Название")
    evidence_table.add_column("Теги")
    evidence_table.add_column("Надёжность", justify="right")

    # Здесь limit равен числу улик: сортируем все записи, а не только обычную тройку приоритетов.
    for item in investigation.priority_evidence(limit=len(investigation.evidence)):
        evidence_table.add_row(
            item.evidence_id,
            item.kind,
            item.title,
            ", ".join(item.tags),
            f"{item.reliability}/5",
        )

    console.print(people_table)
    console.print(evidence_table)
```

Отдельная функция покажет результаты одного поискового запроса:

```python
def render_search_results(query, results):
    # render_search_results() форматирует уже отфильтрованный список results.
    table = Table(title=f"Поиск: {query}")
    table.add_column("ID", style="cyan")
    table.add_column("Название")
    table.add_column("Фрагмент")

    for item in results:
        table.add_row(item.evidence_id, item.title, item.short_body())

    console.print(table)
```

Функция сборки отчёта загружает исходный JSON, выполняет автоматическую проверку и сохраняет новый снимок.

```python
def build_report(seed_path=SEED_PATH, output_path=OUTPUT_PATH):
    # Читаем seed, а пишем в отдельный файл, чтобы исходная версия дела оставалась неизменной.
    investigation = CaseRepository(seed_path).load()
    access_matches = investigation.find_evidence("доступ")
    investigation.add_note(
        author="Доска расследования",
        text=f"Автоматический поиск по слову 'доступ' нашел улик: {len(access_matches)}.",
        # Фиксированное время делает учебный JSON воспроизводимым при каждом запуске.
        created_at="2026-03-15T08:30:00+03:00",
    )
    CaseRepository(output_path).save(investigation)
    return investigation
```

В `main()` остаётся связать шаги:

```python
def main():
    # Один и тот же объект используем для общего обзора и отдельного поискового отчёта.
    investigation = build_report()
    render_overview(investigation)
    render_search_results("доступ", investigation.find_evidence("доступ"))
    console.print(f"\n[green]JSON-снимок сохранён:[/green] {OUTPUT_PATH.name}")


if __name__ == "__main__":
    main()
```

## Проверка

Запустите:

```bash
python investigation_system.py
```

После отчёта запустите тесты из учебного набора:

```bash
python -m unittest discover -s tests
```

Ожидаемый смысл результата:

```text
Дело: Ночной сигнал архива
Участников: 4
Улик: 7
Заметок: 2
Приоритетные улики:
EV-004  Дубли фотоиндекса                  5/5
EV-005  Фрагмент журнала доступа           5/5
EV-006  Совпадение описи и черновика       5/5

Поиск: доступ
EV-003
EV-005

JSON-снимок сохранён: case_report.json
```

После запуска рядом со скриптом появится `case_report.json`. Откройте его и проверьте, что в `notes` две записи: исходная и новая заметка от доски расследования.

Если поиск по слову `доступ` не находит `EV-003` и `EV-005`, проверьте `Evidence.matches()` и `Investigation.find_evidence()`. Если файл не сохраняется, вернитесь к `CaseRepository.save()`.

## Что мы использовали

- [Установка Python](../../field-guide/install-python/) — Python 3.13+, виртуальная среда и читаемые типы.
- [Списки `list`](../../field-guide/list/) — коллекции участников, улик и заметок.
- [Словари `dict`](../../field-guide/dict/) — JSON-структура до превращения в объекты.
- [Классы](../../field-guide/classes/) — собственные типы для предметной области.
- [dataclasses](../../field-guide/dataclasses/) — короткое описание объектов без ручного `__init__()`.
- Методы — поведение рядом с данными.
- Композиция — `Investigation` состоит из `Person`, `Evidence` и `CaseNote`.
- [Сохранёние в JSON](../../field-guide/json/) — загрузка исходного дела и запись обновлённого снимка.
- [pathlib](../../field-guide/pathlib/) — переносимые пути к исходному файлу и отчёту.
- [Rich](../../field-guide/rich/) — сводка в терминале без смешивания с моделью дела.

## Усложняем проект

1. Добавьте статус дела: `open`, `waiting`, `closed`.
2. Сделайте метод `evidence_by_tag(tag)`, который использует `tag_index()`.
3. Постройте хронологию по `created_at`: отдельно обработайте полные временные метки и значение EV-006 с точностью только до даты, не придумывая отсутствующее время.
4. Сохраняйте отдельный `case_summary.txt` для руководителя.
5. Добавьте командное меню: показать улики, найти по запросу, добавить заметку, сохранить.
6. Сделайте импорт улик из нескольких JSON-файлов.

Когда закончите, откройте [разбор полного решения](../investigation-system-solution/).
