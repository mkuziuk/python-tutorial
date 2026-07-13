from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table


def default_project_dir():
    script_dir = Path(__file__).resolve().parent
    if (script_dir / "data" / "case_seed.json").exists():
        return script_dir
    return script_dir.parent


PROJECT_DIR = default_project_dir()
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
    created_at: str
    # default_factory даёт каждой улике свой список, а не один общий.
    tags: list[str] = field(default_factory=list)
    reliability: int = 3

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

        if not self.evidence_id:
            raise ValueError("Evidence ID must not be empty")
        if not self.created_at:
            raise ValueError("Evidence created_at must not be empty")
        if not 1 <= self.reliability <= 5:
            raise ValueError("Evidence reliability must be between 1 and 5")

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
            "created_at": self.created_at,
            "tags": self.tags,
            "reliability": self.reliability,
        }

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
        return normalized_query in haystack

    def short_body(self, limit=90):
        # Сначала сжимаем пробелы, чтобы переносы строк не ломали таблицу и не расходовали лимит незаметно.
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
        # Вложенные словари превращаем в объекты, из которых состоит дело.
        return cls(
            case_id=str(data["case_id"]),
            title=str(data["title"]),
            summary=str(data["summary"]),
            people=[Person.from_dict(item) for item in data.get("people", [])],
            evidence=[Evidence.from_dict(item) for item in data.get("evidence", [])],
            notes=[CaseNote.from_dict(item) for item in data.get("notes", [])],
        )

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

    def add_evidence(self, item):
        # ID сравниваются без учёта регистра: EV-01 и ev-01 — одна логическая улика.
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
        # При равной надёжности ID служит дополнительным ключом и сохраняет стабильный порядок.
        return sorted(self.evidence, key=lambda item: (-item.reliability, item.evidence_id))[:limit]

    def tag_index(self):
        index = {}
        for item in self.evidence:
            for tag in item.tags:
                index.setdefault(tag, []).append(item)
        # Сортируем и теги, и улики, чтобы JSON и таблицы не зависели от порядка входных данных.
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
    # Читаем seed, а пишем в отдельный файл, чтобы исходная версия дела оставалась неизменной.
    investigation = CaseRepository(seed_path).load()
    access_matches = investigation.find_evidence("доступ")
    investigation.add_note(
        author="Доска расследования",
        text=f"Автоматический поиск по слову 'доступ' нашел улик: {len(access_matches)}.",
        created_at="2026-03-15T08:30:00+03:00",
    )
    CaseRepository(output_path).save(investigation)
    return investigation


def main():
    investigation = build_report()
    render_overview(investigation)
    render_search_results("доступ", investigation.find_evidence("доступ"))
    console.print(f"\n[green]JSON-снимок сохранён:[/green] {OUTPUT_PATH.name}")


if __name__ == "__main__":
    main()
