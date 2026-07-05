---
title: "Дело 05. Разбор полного решения"
description: "Полный код доски расследования с dataclass-моделями, методами, композицией и JSON-сохранением."
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
time: "20-30 минут"
---

Эта страница нужна после самостоятельной сборки `investigation_system.py`. Если открыть ее раньше, можно случайно пропустить самую полезную часть дела: решение, где должны жить данные, а где поведение.

## Полный код

```python
from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
SEED_PATH = DATA_DIR / "case_seed.json"
OUTPUT_PATH = PROJECT_DIR / "case_report.json"
console = Console()


@dataclass(slots=True)
class Evidence:
    evidence_id: str
    kind: str
    title: str
    source: str
    body: str
    tags: list[str] = field(default_factory=list)
    reliability: int = 3

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

    @classmethod
    def from_dict(cls, data):
        return cls(
            evidence_id=str(data["evidence_id"]),
            kind=str(data["kind"]),
            title=str(data["title"]),
            source=str(data["source"]),
            body=str(data["body"]),
            tags=[str(tag) for tag in data.get("tags", [])],
            reliability=int(data.get("reliability", 3)),
        )

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

    def short_body(self, limit=90):
        compact = " ".join(self.body.split())
        if len(compact) <= limit:
            return compact
        return f"{compact[: limit - 3].rstrip()}..."


@dataclass(slots=True)
class Person:
    person_id: str
    name: str
    role: str
    contact: str
    notes: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data):
        return cls(
            person_id=str(data["person_id"]),
            name=str(data["name"]),
            role=str(data["role"]),
            contact=str(data["contact"]),
            notes=[str(note) for note in data.get("notes", [])],
        )

    def to_dict(self):
        return {
            "person_id": self.person_id,
            "name": self.name,
            "role": self.role,
            "contact": self.contact,
            "notes": self.notes,
        }

    def label(self):
        return f"{self.name} - {self.role}"


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

    def to_dict(self):
        return {
            "author": self.author,
            "text": self.text,
            "created_at": self.created_at,
        }


@dataclass(slots=True)
class Investigation:
    case_id: str
    title: str
    summary: str
    people: list[Person] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    notes: list[CaseNote] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data):
        return cls(
            case_id=str(data["case_id"]),
            title=str(data["title"]),
            summary=str(data["summary"]),
            people=[Person.from_dict(item) for item in data.get("people", [])],
            evidence=[Evidence.from_dict(item) for item in data.get("evidence", [])],
            notes=[CaseNote.from_dict(item) for item in data.get("notes", [])],
        )

    def to_dict(self):
        return {
            "case_id": self.case_id,
            "title": self.title,
            "summary": self.summary,
            "people": [person.to_dict() for person in self.people],
            "evidence": [item.to_dict() for item in self.evidence],
            "notes": [note.to_dict() for note in self.notes],
        }

    def add_evidence(self, item):
        if self.evidence_by_id(item.evidence_id) is not None:
            raise ValueError(f"Evidence {item.evidence_id!r} already exists")
        self.evidence.append(item)

    def add_note(self, author, text, created_at):
        self.notes.append(CaseNote(author=author, text=text, created_at=created_at))

    def evidence_by_id(self, evidence_id):
        normalized_id = evidence_id.casefold()
        for item in self.evidence:
            if item.evidence_id.casefold() == normalized_id:
                return item
        return None

    def find_evidence(self, query):
        return [item for item in self.evidence if item.matches(query)]

    def priority_evidence(self, limit=3):
        return sorted(self.evidence, key=lambda item: (-item.reliability, item.evidence_id))[:limit]

    def tag_index(self):
        index = {}
        for item in self.evidence:
            for tag in item.tags:
                index.setdefault(tag, []).append(item)
        return {
            tag: sorted(items, key=lambda item: item.evidence_id)
            for tag, items in sorted(index.items())
        }


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


def render_overview(investigation):
    console.print(f"[bold cyan]{investigation.title}[/bold cyan]")
    console.print(investigation.summary)

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
    evidence_table.add_column("Надежность", justify="right")

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


def render_search_results(query, results):
    table = Table(title=f"Поиск: {query}")
    table.add_column("ID", style="cyan")
    table.add_column("Название")
    table.add_column("Фрагмент")

    for item in results:
        table.add_row(item.evidence_id, item.title, item.short_body())

    console.print(table)


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


def main():
    investigation = build_report()
    render_overview(investigation)
    render_search_results("сигнал", investigation.find_evidence("сигнал"))
    console.print(f"\n[green]JSON-снимок сохранен:[/green] {OUTPUT_PATH.name}")


if __name__ == "__main__":
    main()
```

## Как читать решение

Поток данных такой: `CaseRepository.load()` превращает JSON в `Investigation`, объект дела хранит списки `Person`, `Evidence` и `CaseNote`, методы выполняют поиск и добавляют заметку, а `CaseRepository.save()` снова пишет JSON.

Главное решение - разделить предметную модель и хранение. `Evidence` не знает про файл, `Investigation` не рисует таблицы, а `CaseRepository` не решает, как искать по уликам.

Частые ошибки: оставить сырые словари внутри `Investigation`, забыть `field(default_factory=list)`, разрешить дубликаты `evidence_id` или смешать сохранение JSON с логикой поиска.

Справочник: [classes](../../field-guide/classes/), [dataclasses](../../field-guide/dataclasses/), [JSON](../../field-guide/json/), [pathlib](../../field-guide/pathlib/), [dict](../../field-guide/dict/), [list](../../field-guide/list/), [functions](../../field-guide/functions/), [Rich](../../field-guide/rich/).

## Что важно заметить

`Evidence`, `Person` и `CaseNote` не знают, где лежит JSON-файл. Они отвечают только за свои данные и маленькие операции вокруг них.

`Investigation` собирает объекты вместе. Это центр предметной логики: поиск, добавление заметки, защита от дубликатов и индекс по тегам.

`CaseRepository` занимается хранением. Благодаря этому сохранение можно заменить позже: например, писать не в файл, а в базу данных, не переписывая методы `Evidence.matches()` или `Investigation.find_evidence()`.
