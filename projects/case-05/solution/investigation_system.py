from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table


def default_project_dir():
    script_dir = Path(__file__).resolve().parent
    return script_dir if (script_dir / "data").exists() else script_dir.parent


PROJECT_DIR = default_project_dir()
DATA_DIR = PROJECT_DIR / "data"
ARTIFACTS_DIR = DATA_DIR / "artifacts"
RELATIONSHIPS_PATH = DATA_DIR / "relationships.json"
OUTPUT_PATH = PROJECT_DIR / "artifacts" / "05-case-board.json"
console = Console()


def file_sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


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

    def __post_init__(self):
        self.evidence_id = self.evidence_id.strip()
        self.title = self.title.strip()
        self.tags = sorted({tag.strip().casefold() for tag in self.tags if tag.strip()})
        if not self.evidence_id:
            raise ValueError("Evidence ID must not be empty")
        if not self.origin_finding_id:
            raise ValueError("Evidence must keep its origin finding ID")
        if not 1 <= self.reliability <= 5:
            raise ValueError("Evidence reliability must be between 1 and 5")

    @classmethod
    def from_dict(cls, data):
        return cls(
            evidence_id=str(data["evidence_id"]),
            kind=str(data["kind"]),
            title=str(data["title"]),
            summary=str(data["summary"]),
            source=str(data["source"]),
            occurred_at=str(data["occurred_at"]),
            origin_finding_id=str(data["origin_finding_id"]),
            tags=[str(tag) for tag in data.get("tags", [])],
            reliability=int(data.get("reliability", 3)),
            effects=[dict(effect) for effect in data.get("effects", [])],
        )

    def to_dict(self):
        return {
            "evidence_id": self.evidence_id,
            "occurred_at": self.occurred_at,
            "kind": self.kind,
            "title": self.title,
            "summary": self.summary,
            "source": self.source,
            "reliability": self.reliability,
            "effects": self.effects,
            "origin_finding_id": self.origin_finding_id,
            "tags": self.tags,
        }

    def matches(self, query):
        normalized = query.casefold().strip()
        if not normalized:
            return True
        values = [
            self.evidence_id,
            self.kind,
            self.title,
            self.summary,
            self.source,
            self.occurred_at,
            self.origin_finding_id,
            *self.tags,
        ]
        return normalized in " ".join(values).casefold()


@dataclass(slots=True)
class Person:
    person_id: str
    name: str
    role: str

    @classmethod
    def from_dict(cls, data):
        return cls(str(data["person_id"]), str(data["name"]), str(data["role"]))

    def to_dict(self):
        return {"person_id": self.person_id, "name": self.name, "role": self.role}


@dataclass(slots=True)
class Hypothesis:
    hypothesis_id: str
    claim: str

    @classmethod
    def from_dict(cls, data):
        return cls(str(data["hypothesis_id"]), str(data["claim"]))

    def to_dict(self):
        return {"hypothesis_id": self.hypothesis_id, "claim": self.claim}


@dataclass(slots=True)
class EvidenceLink:
    evidence_id: str
    hypothesis_id: str
    stance: str
    weight: int

    def __post_init__(self):
        if self.stance not in {"support", "conflict"}:
            raise ValueError(f"Unknown stance: {self.stance}")
        if not 1 <= self.weight <= 3:
            raise ValueError("Link weight must be between 1 and 3")

    @classmethod
    def from_dict(cls, data):
        return cls(
            str(data["evidence_id"]),
            str(data["hypothesis_id"]),
            str(data["stance"]),
            int(data["weight"]),
        )

    def to_effect(self):
        return {
            "hypothesis_id": self.hypothesis_id,
            "stance": self.stance,
            "weight": self.weight,
        }

    def to_dict(self):
        return {
            "evidence_id": self.evidence_id,
            **self.to_effect(),
        }


@dataclass(slots=True)
class Investigation:
    case_id: str
    title: str
    summary: str
    incident_date: str
    scheduled_opening: str
    analysis_time: str
    people: list[Person] = field(default_factory=list)
    hypotheses: list[Hypothesis] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    links: list[EvidenceLink] = field(default_factory=list)
    source_artifacts: list[dict] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data):
        return cls(
            case_id=str(data["case_id"]),
            title=str(data["title"]),
            summary=str(data["summary"]),
            incident_date=str(data["incident_date"]),
            scheduled_opening=str(data["scheduled_opening"]),
            analysis_time=str(data["analysis_time"]),
            people=[Person.from_dict(item) for item in data.get("people", [])],
            hypotheses=[Hypothesis.from_dict(item) for item in data.get("hypotheses", [])],
            evidence=[Evidence.from_dict(item) for item in data.get("evidence", [])],
            links=[EvidenceLink.from_dict(item) for item in data.get("links", [])],
            source_artifacts=[dict(item) for item in data.get("source_artifacts", [])],
        )

    def to_dict(self):
        return {
            "schema_version": 1,
            "investigation_id": "I-05",
            "generated_at": self.analysis_time,
            "case_id": self.case_id,
            "title": self.title,
            "summary": self.summary,
            "incident_date": self.incident_date,
            "scheduled_opening": self.scheduled_opening,
            "analysis_time": self.analysis_time,
            "source_artifacts": self.source_artifacts,
            "people": [person.to_dict() for person in self.people],
            "hypotheses": [item.to_dict() for item in self.hypotheses],
            "evidence": [item.to_dict() for item in self.evidence],
            "links": [item.to_dict() for item in self.links],
        }

    def evidence_by_id(self, evidence_id):
        target = evidence_id.casefold()
        return next(
            (item for item in self.evidence if item.evidence_id.casefold() == target),
            None,
        )

    def add_evidence(self, item):
        if self.evidence_by_id(item.evidence_id) is not None:
            raise ValueError(f"Evidence {item.evidence_id!r} already exists")
        self.evidence.append(item)

    def find_evidence(self, query):
        return [item for item in self.evidence if item.matches(query)]

    def evidence_for_hypothesis(self, hypothesis_id):
        ids = {
            link.evidence_id
            for link in self.links
            if link.hypothesis_id == hypothesis_id
        }
        return [item for item in self.evidence if item.evidence_id in ids]

    def verified_evidence(self):
        return [item for item in self.evidence if item.origin_finding_id]


class CaseRepository:
    def __init__(self, path):
        self.path = path

    def load(self):
        return Investigation.from_dict(json.loads(self.path.read_text(encoding="utf-8")))

    def save(self, investigation):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(investigation.to_dict(), ensure_ascii=False, indent=2)
        self.path.write_text(payload + "\n", encoding="utf-8")


def load_artifacts(artifacts_dir=ARTIFACTS_DIR):
    artifacts = {}
    for path in sorted(artifacts_dir.glob("0[1-4]-*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        artifacts[data["investigation_id"]] = {"path": path, "data": data}
    if set(artifacts) != {"I-01", "I-02", "I-03", "I-04"}:
        raise ValueError("The board requires artifacts from I-01 through I-04")

    verified = {
        item["investigation_id"]: item
        for item in artifacts["I-04"]["data"]["verified_artifacts"]
    }
    for investigation_id in ("I-01", "I-02", "I-03"):
        expected = verified[investigation_id]["sha256"]
        actual = file_sha256(artifacts[investigation_id]["path"])
        if actual != expected:
            raise ValueError(f"Hash mismatch for {investigation_id}")
    return artifacts


def finding(artifacts, investigation_id, finding_id):
    for item in artifacts[investigation_id]["data"].get("findings", []):
        if item["finding_id"] == finding_id:
            return item
    raise ValueError(f"Finding {finding_id} not found in {investigation_id}")


def make_evidence(artifacts):
    authorship = finding(artifacts, "I-01", "F-I01-AUTHORSHIP")
    matches = finding(artifacts, "I-02", "F-I02-TEXT-MATCHES")
    lockout = finding(artifacts, "I-03", "F-I03-LOCKOUT")
    camera = finding(artifacts, "I-03", "F-I03-CAMERA")
    duplicates = finding(artifacts, "I-04", "F-I04-DUPLICATES")
    timeline = finding(artifacts, "I-04", "F-I04-TIMELINE")
    access = finding(artifacts, "I-04", "F-I04-ACCESS-LOG")

    evidence = [
        Evidence("EV-WARNING", "document", "Анонимное предупреждение", authorship["summary"], "01-authorship.json", "2026-03-14T18:20:00+03:00", authorship["finding_id"], ["текст", "авторство"], 5),
        Evidence("EV-TEXT-ANALYSIS", "analysis", authorship["title"], authorship["summary"], "01-authorship.json", "2026-03-15T06:45:00+03:00", authorship["finding_id"], ["текст", "авторство"], 3),
        Evidence("EV-TOUR-DRAFT", "analysis", matches["title"], matches["summary"], "02-text-matches.json", "2026-03-14T17:48:00+03:00", matches["finding_id"], ["текст", "копирование"], 5),
        Evidence("EV-PHISH-LOCKOUT", "email", lockout["title"], lockout["summary"], lockout["source_file"], lockout["occurred_at"], lockout["finding_id"], ["почта", "доступ"], 5),
        Evidence("EV-PHISH-CAMERA", "email", camera["title"], camera["summary"], camera["source_file"], camera["occurred_at"], camera["finding_id"], ["почта", "камера"], 4),
        Evidence("EV-PHOTO-DUPLICATE", "backup", duplicates["title"], duplicates["summary"], "04-evidence-index.json", "2026-03-14T22:48:00+03:00", duplicates["finding_id"], ["файлы", "хеш"], 5),
        Evidence("EV-WORKING-2253", "document", "Рабочая хронология заканчивается в 22:53", timeline["summary"], "timeline.txt", "2026-03-14T22:53:00+03:00", timeline["finding_id"], ["хронология"], 5),
        Evidence("EV-BACKUP-2307", "backup", "Резервная хронология содержит строку 23:07", timeline["summary"], "timeline_backup.txt", "2026-03-14T23:07:00+03:00", timeline["finding_id"], ["хронология", "резервная копия"], 5),
    ]

    event_specs = {
        "22:35": ("EV-KEY", "access_log", "Никита Королев получил ключ", ["доступ", "королев"], 5),
        "22:41": ("EV-SENSOR", "access_log", "Датчик отметил открытие комнаты", ["доступ", "датчик"], 5),
        "22:43": ("EV-NIKITA-STATEMENT", "interview", "Никита сообщил, что работал только с копией", ["королев", "объяснение"], 2),
        "22:57": ("EV-FREEZE", "policy", "Дежурный запретил менять исходные файлы", ["целостность", "доступ"], 5),
    }
    for event in access["events"]:
        key = event["occurred_at"][11:16]
        evidence_id, kind, title, tags, reliability = event_specs[key]
        evidence.append(Evidence(evidence_id, kind, title, event["text"], access["source_file"], event["occurred_at"], access["finding_id"], tags, reliability))
    return evidence


def build_board(artifacts_dir=ARTIFACTS_DIR, relationships_path=RELATIONSHIPS_PATH):
    artifacts = load_artifacts(artifacts_dir)
    relationships = json.loads(relationships_path.read_text(encoding="utf-8"))
    links = [EvidenceLink.from_dict(item) for item in relationships["links"]]
    evidence = make_evidence(artifacts)
    evidence_by_id = {item.evidence_id: item for item in evidence}
    hypothesis_ids = {item["hypothesis_id"] for item in relationships["hypotheses"]}
    for link in links:
        if link.evidence_id not in evidence_by_id:
            raise ValueError(f"Unknown evidence in link: {link.evidence_id}")
        if link.hypothesis_id not in hypothesis_ids:
            raise ValueError(f"Unknown hypothesis in link: {link.hypothesis_id}")
        evidence_by_id[link.evidence_id].effects.append(link.to_effect())

    source_artifacts = [
        {
            "investigation_id": investigation_id,
            "path": item["path"].name,
            "sha256": file_sha256(item["path"]),
        }
        for investigation_id, item in sorted(artifacts.items())
    ]
    return Investigation(
        case_id=relationships["case_id"],
        title=relationships["title"],
        summary=relationships["summary"],
        incident_date=relationships["incident_date"],
        scheduled_opening=relationships["scheduled_opening"],
        analysis_time=relationships["analysis_time"],
        people=[Person.from_dict(item) for item in relationships["people"]],
        hypotheses=[Hypothesis.from_dict(item) for item in relationships["hypotheses"]],
        evidence=evidence,
        links=links,
        source_artifacts=source_artifacts,
    )


def build_report(artifacts_dir=ARTIFACTS_DIR, relationships_path=RELATIONSHIPS_PATH, output_path=OUTPUT_PATH):
    investigation = build_board(artifacts_dir, relationships_path)
    CaseRepository(output_path).save(investigation)
    return investigation


def render_overview(investigation):
    console.print(f"[bold cyan]Расследование: {investigation.title}[/bold cyan]")
    console.print(f"Проверенных входных отчётов: {len(investigation.source_artifacts)}")
    console.print(f"Улик на доске: {len(investigation.evidence)}")
    console.print(f"Связей с гипотезами: {len(investigation.links)}")

    table = Table(title="Материалы доски")
    table.add_column("ID", style="cyan")
    table.add_column("Источник")
    table.add_column("Название")
    for item in investigation.evidence:
        table.add_row(item.evidence_id, item.origin_finding_id, item.title)
    console.print(table)


def render_search_results(query, results):
    table = Table(title=f"Поиск: {query}")
    table.add_column("ID", style="cyan")
    table.add_column("Название")
    for item in results:
        table.add_row(item.evidence_id, item.title)
    console.print(table)


def main():
    investigation = build_report()
    render_overview(investigation)
    render_search_results("хронология", investigation.find_evidence("хронология"))
    console.print(f"[green]Доска сохранена:[/green] {OUTPUT_PATH.name}")


if __name__ == "__main__":
    main()
