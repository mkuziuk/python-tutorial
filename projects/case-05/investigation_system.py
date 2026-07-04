from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

DATA_DIR = Path(__file__).with_name("data")
SEED_PATH = DATA_DIR / "case_seed.json"
OUTPUT_PATH = Path(__file__).with_name("case_report.json")
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

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Evidence":
        return cls(
            evidence_id=str(data["evidence_id"]),
            kind=str(data["kind"]),
            title=str(data["title"]),
            source=str(data["source"]),
            body=str(data["body"]),
            tags=[str(tag) for tag in data.get("tags", [])],
            reliability=int(data.get("reliability", 3)),
        )

    def matches(self, query: str) -> bool:
        # TODO: искать query в ID, типе, заголовке, источнике, тексте и тегах.
        # Подсказка: соберите эти поля в одну строку и сравнивайте через casefold().
        normalized_query = query.casefold().strip()
        if not normalized_query:
            return True
        return False


@dataclass(slots=True)
class Person:
    person_id: str
    name: str
    role: str
    contact: str
    notes: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Person":
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
    def from_dict(cls, data: dict[str, object]) -> "CaseNote":
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
    people: list[Person] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    notes: list[CaseNote] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Investigation":
        return cls(
            case_id=str(data["case_id"]),
            title=str(data["title"]),
            summary=str(data["summary"]),
            people=[Person.from_dict(item) for item in data.get("people", [])],
            evidence=[Evidence.from_dict(item) for item in data.get("evidence", [])],
            notes=[CaseNote.from_dict(item) for item in data.get("notes", [])],
        )

    def find_evidence(self, query: str) -> list[Evidence]:
        # TODO: вернуть только те улики, для которых Evidence.matches(query) дает True.
        return []

    def add_note(self, author: str, text: str, created_at: str) -> None:
        # TODO: создать CaseNote и добавить его в self.notes.
        raise NotImplementedError("Добавьте заметку в список self.notes")

    def priority_evidence(self, limit: int = 3) -> list[Evidence]:
        return sorted(self.evidence, key=lambda item: (-item.reliability, item.evidence_id))[:limit]


class CaseRepository:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> Investigation:
        raw_data = json.loads(self.path.read_text(encoding="utf-8"))
        return Investigation.from_dict(raw_data)

    def save(self, investigation: Investigation) -> None:
        # TODO: превратить investigation обратно в словарь и записать JSON.
        raise NotImplementedError("Сохранение появится в финальной версии")


def render_overview(investigation: Investigation) -> None:
    table = Table(title=f"Дело: {investigation.title}")
    table.add_column("Показатель", style="cyan")
    table.add_column("Значение", justify="right")
    table.add_row("Участников", str(len(investigation.people)))
    table.add_row("Улик", str(len(investigation.evidence)))
    table.add_row("Заметок", str(len(investigation.notes)))

    console.print(table)
    console.print("\n[bold]Приоритетные улики[/bold]")
    for item in investigation.priority_evidence():
        console.print(f"{item.evidence_id}: {item.title} ({item.reliability}/5)")


def main() -> None:
    investigation = CaseRepository(SEED_PATH).load()
    render_overview(investigation)
    console.print("\n[dim]Дальше в главе вы добавите поиск, заметки и сохранение JSON-снимка.[/dim]")


if __name__ == "__main__":
    main()
