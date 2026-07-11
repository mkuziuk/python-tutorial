---
title: "Дело 06. Вердикт перед открытием"
description: "Собираем хронологию, ранжируем проверяемые гипотезы и принимаем осторожное решение перед открытием выставки."
concepts:
  - StrEnum
  - frozen dataclasses
  - match
  - JSON
  - sorting
  - scoring
difficulty: "продвинутый"
projectId: "case-06"
time: "120-150 минут"
---

<div class="case-meta">
  <p><strong>Миссия</strong> превратить материалы пяти дел в объяснимый финальный отчет до открытия выставки утром 15 марта.</p>
  <p><strong>Инструменты</strong> Python 3.13+, `StrEnum`, неизменяемые `dataclass`, `match`, JSON, сортировка и прозрачная система баллов.</p>
  <p><strong>Результат</strong> хронология, рейтинг гипотез с опорой и противоречиями, осторожный вывод и файл `verdict.json`.</p>
  <p><strong>Маршрут</strong> продвинутый · 120–150 минут · Python 3.13+</p>
</div>

<div class="materials-panel">
  <p><strong>Быстрые ссылки:</strong> <a href="../../downloads/case-06.zip">case-06.zip</a> · <a href="../../materials/">материалы всех дел</a> · <a href="../final-verdict-solution/">разбор решения</a></p>
  <p><strong>Справочник:</strong> <a href="../../field-guide/dataclasses/">dataclass</a> · <a href="../../field-guide/json/">JSON</a> · <a href="../../field-guide/pathlib/">pathlib</a> · <a href="../../field-guide/sorting/">сортировка</a> · <a href="../../field-guide/functions/">функции</a></p>
</div>

## Последние часы

Ночь 14 марта 2026 года закончилась, но до открытия выставки 15 марта в 10:00 осталось меньше двух часов. Отдельные инструменты уже нашли важные фрагменты:

- текст анонимного предупреждения похож на рабочие заметки Алины, но сходство текста не устанавливает автора;
- два фрагмента закрытой описи появились в черновике экскурсии;
- два письма похожи на фишинг, однако доставка письма еще не означает успешный взлом;
- резервная копия содержит строку 23:07 об отправке копии архивариусу, которой нет в рабочей хронологии.

Утром появились два новых материала. Алина Морозова дала подписанное подтверждение авторства предупреждения. Неизменяемый аудит `SEC-774` связал запись фрагментов закрытой описи в черновик до 18:00 и перезапись хронологии в 23:19 с аппаратно подтвержденными сеансами `nikita.k`.

Это сильная связь, но не магическое доказательство всего сразу. Аудит устанавливает происхождение действий учетной записи, а не мотив. Он не заменяет видео человека за клавиатурой и полное интервью.

Финальный вопрос поэтому состоит из двух частей:

1. Какая гипотеза лучше всего объясняет доступные материалы?
2. Достаточно ли целостны данные и доступы, чтобы открыть выставку сегодня?

Ответы могут различаться. Даже без судебной уверенности в личности и мотиве можно принять безопасное операционное решение.

Скачайте [case-06.zip](../../downloads/case-06.zip) или откройте `projects/case-06/` в репозитории. Стартовый набор содержит пустой `final_verdict.py`, пакет улик `data/evidence_bundle.json`, тесты, `requirements.txt`, README и файл ожидаемого результата. Папка `solution/` остается только в репозитории и не раскрывает готовый код в скачанном стартере.

## Как читать систему баллов

Каждая улика имеет надежность от 1 до 5. Ее связь с конкретной гипотезой имеет вес от 1 до 3 и направление:

- `support` — улика поддерживает гипотезу;
- `conflict` — улика ей противоречит.

Для каждой связи программа вычисляет `надежность × вес`. Затем отдельно суммирует баллы «за» и «против»:

```text
итог = баллы за - баллы против
```

Это не вероятность и не автоматический приговор. Веса — проверяемые решения аналитика. Связанные журналы могут зависеть друг от друга, а высокий балл не доказывает умысел. Система нужна, чтобы увидеть ход рассуждения, быстро найти спорную связь и не спрятать противоречащие материалы.

Перед кодом откройте `data/evidence_bundle.json` и найдите:

- `EV-SIGNED-AUDIT` — новую сильную, но ограниченную привязку действий;
- `EV-ALINA-ADMISSION` — утреннее подписанное подтверждение;
- `EV-MAIL-AUDIT` — отсутствие наблюдаемых признаков успешного взлома;
- `EV-NIKITA-STATEMENT` — материал, который противоречит основной гипотезе и поэтому не должен исчезнуть из отчета.

## Подготовка

Проект использует возможности Python 3.13. Сторонних библиотек нет.

### Windows PowerShell

```powershell
py -3 --version
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Первая команда должна показать Python 3.13 или новее.

### macOS или Linux

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Первая команда должна показать Python 3.13 или новее.

Проверьте стартовый файл:

```bash
python final_verdict.py
```

Он пуст и пока ничего не выводит.

## Шаг 1. Модель, которую нельзя случайно переписать

Добавьте в `final_verdict.py` первый блок. `StrEnum` ограничивает словарь допустимых типов, а `frozen=True, slots=True` делает загруженные факты неизменяемыми. Если анализу понадобится другая версия улики, безопаснее создать новый объект, чем незаметно исправить старый.

```python
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
            # .value сохраняет в отчете строку, а не объект перечисления.
            "status": self.status.value,
            "score": self.score,
            "support_points": self.support_points,
            "conflict_points": self.conflict_points,
            "support": list(self.support),
            "conflicts": list(self.conflicts),
        }
```

Обратите внимание на путь. Один и тот же код работает и после вставки в корневой стартовый файл, и из папки `solution/`. Это важно: решение не должно искать `data/` уровнем выше проекта.

## Шаг 2. Загрузка и честная хронология

Добавьте функции ниже классов:

```python
def load_bundle(path: Path = DATA_PATH) -> CaseBundle:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return CaseBundle.from_dict(raw)


def build_timeline(evidence: tuple[Evidence, ...]) -> list[dict[str, str]]:
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
```

Первый промежуточный чек не требует законченного `main()`: импортируйте модуль и вызовите готовые функции.

```bash
python -c "import final_verdict as f; b=f.load_bundle(); t=f.build_timeline(b.evidence); print(len(t), t[0]['evidence_id'], t[-1]['evidence_id'])"
```

Ожидается:

```text
19 EV-TOUR-DRAFT EV-ALINA-ADMISSION
```

Сортировка использует настоящий `datetime` со смещением часового пояса, а не красивую, но хрупкую строку вида `14.03 9:05`.

## Шаг 3. Баллы «за» и «против»

Добавьте следующий блок. В `score_hypothesis()` оператор `match` заставляет явно обработать каждое допустимое направление связи. Противоречие не получает отрицательный ID и не исчезает: оно хранится в отдельном списке.

```python
def classify_assessment(
    support_points: int, conflict_points: int
) -> AssessmentStatus:
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
            if effect.hypothesis_id != hypothesis.hypothesis_id:
                continue

            # Вклад зависит и от надежности источника, и от силы его связи.
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
```

Второй чек выводит ID, итоговый балл и статус всех гипотез:

```bash
python -c "import final_verdict as f; b=f.load_bundle(); print([(a.hypothesis.hypothesis_id, a.score, a.status.value) for a in f.rank_hypotheses(b)])"
```

Ожидаемый порядок:

```text
[('H-NIKITA', 73, 'strongly_supported'), ('H-MISTAKE', 2, 'unresolved'), ('H-PHISHING', -16, 'not_supported'), ('H-SYNC', -20, 'not_supported')]
```

Все четыре гипотезы отвечают на один и тот же вопрос о причине двух правок файлов и поэтому конкурируют друг с другом. Авторство предупреждения не входит в этот рейтинг: оно является отдельным установленным выводом.

Остановитесь и проверьте смысл. `H-PHISHING` спрашивает не о том, были ли опасные письма — они были. Гипотеза утверждает, что **успешный взлом вызвал изменения файлов**. Для этого нет наблюдаемых следов. Сам вектор остается открытым и требует защитных действий, но его нельзя использовать как установленную причину этой ночи.

## Шаг 4. Вердикт как данные

Рейтинг еще не является решением. Добавьте сборку JSON-отчета и сохранение. Формулировка основной гипотезы намеренно содержит слова «самая сильная рабочая гипотеза», а рядом сохраняется ограничение вывода.

```python
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
                "Аппаратный ключ и локальный сеанс надежно связывают учетные "
                "действия, но не заменяют полное интервью и видео."
            ),
            (
                "Отсутствие следов успешного фишинга не доказывает, что попыток "
                "больше не будет."
            ),
        ],
    }


def save_verdict(verdict: dict[str, Any], path: Path = OUTPUT_PATH) -> None:
    payload = json.dumps(verdict, ensure_ascii=False, indent=2)
    path.write_text(f"{payload}\n", encoding="utf-8")
```

Третий чек проверяет именно решение, не формат терминала:

```bash
python -c "import final_verdict as f; v=f.build_verdict(f.load_bundle()); print(v['operational_decision']['opening'], v['findings']['phishing']['status'])"
```

Ожидается:

```text
postpone unresolved_vector_no_success_evidence
```

## Шаг 5. Отчет и точка входа

Добавьте последние функции. Здесь появляется обязательный `main()` и защита `if __name__ == "__main__"`. После этого обычный запуск действительно выполняет расследование.

```python
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
    print(f"\nJSON-вердикт сохранен: {OUTPUT_PATH.name}")


if __name__ == "__main__":
    main()
```

Запустите завершенную программу:

```bash
python final_verdict.py
```

Сверьте форму отчета с `check_result.txt`, затем проверьте созданный JSON:

```bash
python -m json.tool verdict.json
```

Последний промежуточный чек запускает тесты. Обычная команда ниже всегда импортирует ваш корневой `final_verdict.py` — и в скачанном наборе, и в репозитории. Эталон из `solution/` отдельно проверяет общая команда сопровождающего `pnpm test:python`, запущенная из корня сайта.

```bash
python -m unittest discover -s tests -v
```

## Развязка

Код отделяет три разных уровня уверенности:

- **Установленный факт:** Алина подтвердила авторство предупреждения подписанной утренней записью и воспроизвела содержание до показа оригинала; раннее сравнение текста согласуется с ее словами.
- **Самая сильная рабочая гипотеза:** Никита Королев скопировал фрагменты закрытой описи в черновик экскурсии и исключил из рабочей хронологии строку 23:07 об отправке резервной копии архивариусу. Подписанный аудит связывает обе записи с его аппаратно подтвержденными сеансами. Мотив и физическая личность пользователя еще требуют интервью.
- **Отдельный нерешенный риск:** фишинговые попытки были, но журнал не показывает успешного компромисса и не связывает письма с изменениями файлов.

Открытие нужно **отложить**. Это не наказание и не объявление виновного. Опись и рабочая хронология потеряли целостность, а доступы нельзя считать надежными до проверки. Команда должна вернуть строку 23:07 в новую проверенную хронологию, сохранить обе исходные версии и их хэши, сменить доступы и токены, затем провести полное интервью с Никитой в присутствии второго расследователя.

## Задания после финала

1. Уберите из временной копии JSON связь `EV-SIGNED-AUDIT` с `H-NIKITA`. Остается ли эта гипотеза первой? Запишите, какие независимые материалы удерживают ее наверху.
2. Поменяйте вес `EV-NIKITA-STATEMENT` с 1 на 3. Почему это разумный стресс-тест, но не основание автоматически считать заявление истинным?
3. Добавьте в `verdict.json` поле `evidence_dependencies`, которое помечает журналы одной рабочей станции как связанные. Баллы не обязаны быть вероятностью; отчет должен честно показать возможное двойное считывание источников.
4. Напишите тест, который гарантирует: ни одна гипотеза со статусом `not_supported` не превращается в формулировку установленного факта.

Полный файл без промежуточных остановок находится в [разборе решения](../final-verdict-solution/).
