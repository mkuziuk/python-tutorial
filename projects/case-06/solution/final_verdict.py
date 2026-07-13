from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
import json
from pathlib import Path
import sys
from typing import Any, Self


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent if SCRIPT_DIR.name == "solution" else SCRIPT_DIR
DATA_PATH = PROJECT_DIR / "data" / "evidence_bundle.json"
OUTPUT_PATH = PROJECT_DIR / "verdict.json"


# StrEnum ограничивает значения, но в JSON они остаются обычными строками.
class EvidenceKind(StrEnum):
    ANALYSIS = "analysis"
    EMAIL = "email"
    DOCUMENT = "document"
    ACCESS_LOG = "access_log"
    SYSTEM_LOG = "system_log"
    FILE_AUDIT = "file_audit"
    BACKUP = "backup"
    POLICY = "policy"
    INTERVIEW = "interview"
    OBSERVATION = "observation"
    EMAIL_AUDIT = "email_audit"


class Stance(StrEnum):
    SUPPORT = "support"
    CONFLICT = "conflict"


class AssessmentStatus(StrEnum):
    STRONGLY_SUPPORTED = "strongly_supported"
    SUPPORTED = "supported"
    UNRESOLVED = "unresolved"
    NOT_SUPPORTED = "not_supported"
    NO_EVIDENCE = "no_evidence"


# frozen запрещает менять объект после загрузки, slots фиксирует набор его полей.
@dataclass(frozen=True, slots=True)
class Effect:
    hypothesis_id: str
    stance: Stance
    weight: int

    def __post_init__(self) -> None:
        if not 1 <= self.weight <= 3:
            raise ValueError("Effect weight must be between 1 and 3")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            hypothesis_id=str(data["hypothesis_id"]).strip(),
            stance=Stance(str(data["stance"])),
            weight=int(data["weight"]),
        )


@dataclass(frozen=True, slots=True)
class Evidence:
    evidence_id: str
    occurred_at: datetime
    kind: EvidenceKind
    title: str
    summary: str
    source: str
    reliability: int
    effects: tuple[Effect, ...]

    def __post_init__(self) -> None:
        if not self.evidence_id:
            raise ValueError("Evidence ID must not be empty")
        if not 1 <= self.reliability <= 5:
            raise ValueError("Evidence reliability must be between 1 and 5")
        # Без смещения UTC события из разных источников нельзя надёжно упорядочить.
        if self.occurred_at.tzinfo is None:
            raise ValueError("Evidence timestamp must include a UTC offset")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            evidence_id=str(data["evidence_id"]).strip(),
            # ISO-строку превращаем в datetime; часовой пояс проверяется выше.
            occurred_at=datetime.fromisoformat(str(data["occurred_at"])),
            kind=EvidenceKind(str(data["kind"])),
            title=str(data["title"]).strip(),
            summary=str(data["summary"]).strip(),
            source=str(data["source"]).strip(),
            reliability=int(data["reliability"]),
            effects=tuple(Effect.from_dict(item) for item in data.get("effects", [])),
        )


@dataclass(frozen=True, slots=True)
class Hypothesis:
    hypothesis_id: str
    claim: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            hypothesis_id=str(data["hypothesis_id"]).strip(),
            claim=str(data["claim"]).strip(),
        )


@dataclass(frozen=True, slots=True)
class CaseBundle:
    case_id: str
    title: str
    incident_date: str
    scheduled_opening: datetime
    analysis_time: datetime
    hypotheses: tuple[Hypothesis, ...]
    evidence: tuple[Evidence, ...]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            case_id=str(data["case_id"]),
            title=str(data["title"]),
            incident_date=str(data["incident_date"]),
            scheduled_opening=datetime.fromisoformat(str(data["scheduled_opening"])),
            analysis_time=datetime.fromisoformat(str(data["analysis_time"])),
            hypotheses=tuple(
                Hypothesis.from_dict(item) for item in data.get("hypotheses", [])
            ),
            evidence=tuple(Evidence.from_dict(item) for item in data.get("evidence", [])),
        )


@dataclass(frozen=True, slots=True)
class HypothesisAssessment:
    hypothesis: Hypothesis
    support_points: int
    conflict_points: int
    support: tuple[str, ...]
    conflicts: tuple[str, ...]
    status: AssessmentStatus

    @property
    def score(self) -> int:
        return self.support_points - self.conflict_points

    def to_dict(self, rank: int) -> dict[str, Any]:
        return {
            "rank": rank,
            "hypothesis_id": self.hypothesis.hypothesis_id,
            "claim": self.hypothesis.claim,
            # .value сохраняет в отчёте строку, а не объект перечисления.
            "status": self.status.value,
            "score": self.score,
            "support_points": self.support_points,
            "conflict_points": self.conflict_points,
            "support": list(self.support),
            "conflicts": list(self.conflicts),
        }


def load_bundle(path: Path = DATA_PATH) -> CaseBundle:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return CaseBundle.from_dict(raw)


def build_timeline(evidence: tuple[Evidence, ...]) -> list[dict[str, str]]:
    # ID — вторичный ключ: он даёт стабильный порядок событий с одинаковым временем.
    ordered = sorted(evidence, key=lambda item: (item.occurred_at, item.evidence_id))
    return [
        {
            "occurred_at": item.occurred_at.isoformat(),
            "evidence_id": item.evidence_id,
            "kind": item.kind.value,
            "title": item.title,
            "source": item.source,
        }
        for item in ordered
    ]


def classify_assessment(
    support_points: int, conflict_points: int
) -> AssessmentStatus:
    # Границы статусов — зафиксированное правило этого дела, а не универсальная шкала доказанности.
    # match возвращает первую подходящую ветку, поэтому порядок условий важен.
    match support_points, conflict_points:
        case 0, 0:
            return AssessmentStatus.NO_EVIDENCE
        case support, conflict if support >= 15 and support >= conflict * 2:
            return AssessmentStatus.STRONGLY_SUPPORTED
        case support, conflict if support >= 10 and support >= conflict + 5:
            return AssessmentStatus.SUPPORTED
        case support, conflict if conflict > support:
            return AssessmentStatus.NOT_SUPPORTED
        case _:
            return AssessmentStatus.UNRESOLVED


def score_hypothesis(
    hypothesis: Hypothesis, evidence: tuple[Evidence, ...]
) -> HypothesisAssessment:
    support_points = 0
    conflict_points = 0
    support: list[str] = []
    conflicts: list[str] = []

    for item in evidence:
        for effect in item.effects:
            # Одна улика может влиять на несколько версий; здесь берём только связи с текущей.
            if effect.hypothesis_id != hypothesis.hypothesis_id:
                continue

            # Баллы ранжируют проверки, но не превращаются в вероятность гипотезы.
            # Вклад зависит и от надёжности источника, и от силы его связи.
            points = item.reliability * effect.weight
            match effect.stance:
                case Stance.SUPPORT:
                    support_points += points
                    support.append(item.evidence_id)
                case Stance.CONFLICT:
                    conflict_points += points
                    conflicts.append(item.evidence_id)

    status = classify_assessment(support_points, conflict_points)
    return HypothesisAssessment(
        hypothesis=hypothesis,
        support_points=support_points,
        conflict_points=conflict_points,
        support=tuple(sorted(support)),
        conflicts=tuple(sorted(conflicts)),
        status=status,
    )


def rank_hypotheses(bundle: CaseBundle) -> list[HypothesisAssessment]:
    assessments = [
        score_hypothesis(hypothesis, bundle.evidence)
        for hypothesis in bundle.hypotheses
    ]
    return sorted(
        assessments,
        # Минусы дают убывание баллов; ID задаёт стабильный порядок при ничьей.
        key=lambda item: (
            -item.score,
            -item.support_points,
            item.hypothesis.hypothesis_id,
        ),
    )


def build_verdict(bundle: CaseBundle) -> dict[str, Any]:
    timeline = build_timeline(bundle.evidence)
    assessments = rank_hypotheses(bundle)
    # Основной вывод берём из рассчитанного рейтинга, а не задаём вручную.
    primary = assessments[0]

    return {
        "case_id": bundle.case_id,
        "title": bundle.title,
        "generated_at": bundle.analysis_time.isoformat(),
        "scheduled_opening": bundle.scheduled_opening.isoformat(),
        "timeline": timeline,
        "ranked_hypotheses": [
            item.to_dict(rank)
            for rank, item in enumerate(assessments, start=1)
        ],
        "findings": {
            "warning_author": {
                "status": "confirmed_by_signed_admission",
                "finding": "Алина Морозова написала анонимное предупреждение.",
                "basis": [
                    "EV-ALINA-ADMISSION",
                    "EV-TEXT-ANALYSIS",
                    "EV-WARNING",
                ],
            },
            "primary_hypothesis": {
                "status": primary.status.value,
                "hypothesis_id": primary.hypothesis.hypothesis_id,
                "finding": f"Самая сильная рабочая гипотеза: {primary.hypothesis.claim}",
                "caveat": (
                    "Подписанный аудит связывает обе правки с аппаратно "
                    "подтвержденными сеансами nikita.k, но сам по себе не "
                    "доказывает мотив или физическую личность пользователя."
                ),
            },
            "phishing": {
                "status": "unresolved_vector_no_success_evidence",
                "finding": (
                    "Фишинговые попытки остаются отдельным нерасследованным "
                    "вектором; признаков успешного взлома нет."
                ),
                "basis": [
                    "EV-PHISH-LOCKOUT",
                    "EV-PHISH-CAMERA",
                    "EV-MAIL-AUDIT",
                ],
            },
        },
        "operational_decision": {
            "opening": "postpone",
            "decision": "Отложить открытие 15 марта 2026 года.",
            "reason": (
                "Целостность реестра и рабочей хронологии нарушена, а доступы "
                "и цепочка передачи еще не проверены полностью."
            ),
            "actions": [
                (
                    "Вернуть в новую проверенную хронологию строку 23:07 из "
                    "резервной копии; сохранить исходные рабочую и резервную "
                    "версии с контрольными суммами."
                ),
                (
                    "Сменить доступы к архиву, почте и рабочей станции экскурсии; "
                    "отозвать активные токены."
                ),
                (
                    "Опросить Никиту Королева в присутствии второго расследователя "
                    "и проверить использование аппаратного ключа."
                ),
            ],
        },
        "limitations": [
            (
                "Баллы упорядочивают проверяемые гипотезы, но не превращают "
                "корреляцию в доказанный умысел."
            ),
            (
                "Аппаратный ключ и локальный сеанс надёжно связывают учётные "
                "действия, но не заменяют полное интервью и видео."
            ),
            (
                "Отсутствие следов успешного фишинга не доказывает, что попыток "
                "больше не будет."
            ),
        ],
    }


def save_verdict(verdict: dict[str, Any], path: Path = OUTPUT_PATH) -> None:
    # ensure_ascii=False оставляет русский текст читаемым, а финальный \n делает файл удобным для diff и POSIX-инструментов.
    payload = json.dumps(verdict, ensure_ascii=False, indent=2)
    path.write_text(f"{payload}\n", encoding="utf-8")


def render_report(verdict: dict[str, Any]) -> None:
    print("ФИНАЛЬНЫЙ ВЕРДИКТ")
    print(f"Дело: {verdict['title']}")
    print(f"Событий в хронологии: {len(verdict['timeline'])}")
    print("\nХронология:")
    for item in verdict["timeline"]:
        moment = datetime.fromisoformat(item["occurred_at"])
        print(f"- {moment:%d.%m %H:%M}  {item['evidence_id']}: {item['title']}")

    print("\nРейтинг гипотез:")
    for item in verdict["ranked_hypotheses"]:
        print(
            f"{item['rank']}. {item['hypothesis_id']} — {item['status']} — "
            f"{item['score']:+d} (за {item['support_points']}, "
            f"против {item['conflict_points']})"
        )
        print(f"   опора: {', '.join(item['support']) or 'нет'}")
        print(f"   противоречия: {', '.join(item['conflicts']) or 'нет'}")

    findings = verdict["findings"]
    print("\nВыводы:")
    print(f"- {findings['warning_author']['finding']}")
    print(f"- {findings['primary_hypothesis']['finding']}")
    print(f"  Ограничение: {findings['primary_hypothesis']['caveat']}")
    print(f"- {findings['phishing']['finding']}")

    decision = verdict["operational_decision"]
    print(f"\nРешение: {decision['decision']}")
    for action in decision["actions"]:
        print(f"- {action}")


def main() -> None:
    if sys.version_info < (3, 13):
        raise SystemExit("Для дела 06 нужен Python 3.13 или новее.")

    bundle = load_bundle()
    verdict = build_verdict(bundle)
    render_report(verdict)
    save_verdict(verdict)
    print(f"\nJSON-вердикт сохранён: {OUTPUT_PATH.name}")


if __name__ == "__main__":
    main()
