---
title: "Разбор решения: Последнее доказательство"
description: "Цепочка улик, рейтинг подозреваемых и 04-investigation-summary.json."
---

Эта страница показывает полную версию программы после выполнения упражнения. Сначала завершите самостоятельную версию и сверьте её результат с главой.

Решение сохраняет результат в JSON для следующего шага арки. Поэтому важно проверять не только вывод в терминале, но и структуру созданного файла.

```python
"""Эталон I-04: собрать улики, рейтинг и досье в один проверяемый JSON."""

import json
from pathlib import Path


def default_project_dir():
    """Найти корень case-04 из учебного файла или подпапки solution."""
    script_dir = Path(__file__).resolve().parent
    return script_dir if (script_dir / "data").exists() else script_dir.parent


PROJECT_DIR = default_project_dir()
DATA_DIR = PROJECT_DIR / "data"
ARTIFACTS_DIR = DATA_DIR / "artifacts"
FINAL_EVIDENCE_PATH = DATA_DIR / "final_evidence.json"
DOSSIERS_PATH = DATA_DIR / "suspect_dossiers.json"
OUTPUT_PATH = PROJECT_DIR / "artifacts" / "04-investigation-summary.json"

# Ключ одновременно задаёт ожидаемый ID внутри файла и порядок источников.
UPSTREAM_FILES = {
    "I-01": "01-authorship.json",
    "I-02": "02-text-matches.json",
    "I-03": "03-mail-review.json",
}
# Здесь перечислены выводы прошлых дел, которые нужны финалу. Порядок записей
# внутри исходного JSON может измениться, поэтому номера элементов не подходят.
SELECTED_FINDINGS = {
    "I-01": ["F-I01-AUTHORSHIP"],
    "I-02": ["F-I02-TEXT-MATCHES"],
    "I-03": ["F-I03-LOCKOUT", "F-I03-CAMERA"],
}


def load_artifact(path, expected_id):
    """Загрузить JSON и проверить его investigation_id."""
    data = json.loads(path.read_text(encoding="utf-8"))
    actual_id = data.get("investigation_id")
    if actual_id != expected_id:
        raise ValueError(f"Expected {expected_id} in {path}, found {actual_id!r}")
    return data


def find_finding(artifact, finding_id):
    """Найти вывод по метке или сообщить, какой вывод отсутствует."""
    for finding in artifact.get("findings", []):
        if finding.get("finding_id") == finding_id:
            return finding
    raise KeyError(f"Finding not found: {finding_id}")


def normalize_finding(finding, source_id):
    """Привести вывод любого этапа к общей схеме из шести полей."""
    return {
        "finding_id": finding["finding_id"],
        "source_investigation_id": source_id,
        "title": finding["title"],
        "summary": finding["summary"],
        "limitation": finding.get("limitation", ""),
        # dict(effect) создаёт копию: рейтинг не меняет загруженный JSON.
        "effects": [dict(effect) for effect in finding.get("effects", [])],
    }


def collect_evidence(artifacts, final_evidence):
    """Соединить выбранные старые выводы и все новые, запретив дубликаты."""
    evidence = []
    seen_ids = set()

    # В корректных данных этот цикл добавит 1 + 1 + 2 = 4 старых вывода.
    for investigation_id in ("I-01", "I-02", "I-03"):
        artifact = artifacts[investigation_id]
        for finding_id in SELECTED_FINDINGS[investigation_id]:
            finding = find_finding(artifact, finding_id)
            item = normalize_finding(finding, investigation_id)
            if item["finding_id"] in seen_ids:
                raise ValueError(f"Duplicate finding ID: {item['finding_id']}")
            seen_ids.add(item["finding_id"])
            evidence.append(item)

    # Утренняя проверка добавляет ещё 7 выводов с источником I-04.
    for finding in final_evidence.get("findings", []):
        item = normalize_finding(finding, "I-04")
        if item["finding_id"] in seen_ids:
            raise ValueError(f"Duplicate finding ID: {item['finding_id']}")
        seen_ids.add(item["finding_id"])
        evidence.append(item)

    return evidence


def dossier_index(dossiers):
    """Построить проверенный словарь person_id → досье."""
    index = {}
    for dossier in dossiers:
        person_id = dossier.get("person_id", "").strip()
        if not person_id:
            raise ValueError("Dossier person_id must not be empty")
        if person_id in index:
            raise ValueError(f"Duplicate person ID: {person_id}")
        index[person_id] = dossier
    return index


def lookup_dossier(dossiers, person_id):
    """Найти досье или заменить неясный KeyError понятным сообщением."""
    try:
        return dossier_index(dossiers)[person_id]
    except KeyError as error:
        raise KeyError(f"Unknown person: {person_id}") from error


def resolve_effect_person(effect, people):
    """Связать техническое значение из улики с одним локальным досье."""
    match_field = effect.get("match_field", "")
    if match_field not in {"account", "badge_id", "hardware_key_id"}:
        raise ValueError(f"Unknown dossier field: {match_field!r}")

    match_value = str(effect.get("match_value", "")).casefold()
    matches = [
        person_id
        for person_id, dossier in people.items()
        if str(dossier.get(match_field, "")).casefold() == match_value
    ]
    if not matches:
        raise ValueError(f"No dossier matches {match_field}={match_value!r}")
    if len(matches) > 1:
        raise ValueError(f"Ambiguous dossier match: {match_field}={match_value!r}")
    return matches[0]


def rank_suspects(evidence, dossiers):
    """Сложить support, вычесть conflict и отсортировать людей."""
    people = dossier_index(dossiers)
    # У каждого человека есть нулевой балл и два аудируемых списка причин.
    scores = {
        person_id: {
            "person_id": person_id,
            "name": dossier["name"],
            "score": 0,
            "supporting_finding_ids": [],
            "conflicting_finding_ids": [],
        }
        for person_id, dossier in people.items()
    }

    # Один вывод может влиять на нескольких людей, поэтому нужны два цикла.
    for finding in evidence:
        for effect in finding.get("effects", []):
            # Техническая улика содержит account, badge_id или hardware_key_id.
            # resolve_effect_person() находит владельца значения в локальных досье.
            person_id = resolve_effect_person(effect, people)
            weight = int(effect["weight"])
            if weight < 1:
                raise ValueError("Evidence weight must be positive")
            stance = effect["stance"]
            # Балл нужен для сортировки, а ID сохраняется для объяснения балла.
            if stance == "support":
                scores[person_id]["score"] += weight
                scores[person_id]["supporting_finding_ids"].append(
                    finding["finding_id"]
                )
            elif stance == "conflict":
                scores[person_id]["score"] -= weight
                scores[person_id]["conflicting_finding_ids"].append(
                    finding["finding_id"]
                )
            else:
                raise ValueError(f"Unknown evidence stance: {stance}")

    # Минус перед score даёт убывание; имя стабилизирует порядок при ничьей.
    return sorted(
        scores.values(),
        key=lambda item: (-item["score"], item["name"].casefold()),
    )


def source_record(investigation_id, filename, artifact):
    """Зафиксировать имя входного файла и список выводов, найденных в нём."""
    return {
        "investigation_id": investigation_id,
        "path": f"artifacts/{filename}",
        "finding_ids": [
            item["finding_id"] for item in artifact.get("findings", [])
        ],
    }


def load_investigation_inputs(
    artifacts_dir=ARTIFACTS_DIR,
    final_evidence_path=FINAL_EVIDENCE_PATH,
    dossiers_path=DOSSIERS_PATH,
):
    """Загрузить и проверить три старых отчёта, новые улики и досье."""
    artifacts = {}
    source_artifacts = []
    # Загружаем и одновременно описываем каждый из трёх старых отчётов.
    for investigation_id, filename in UPSTREAM_FILES.items():
        artifact = load_artifact(artifacts_dir / filename, investigation_id)
        artifacts[investigation_id] = artifact
        source_artifacts.append(
            source_record(investigation_id, filename, artifact)
        )

    # У новых улик и досье разные служебные ID: это защищает от перепутанных файлов.
    final_evidence = load_artifact(final_evidence_path, "I-04-EVIDENCE")
    dossiers_bundle = load_artifact(dossiers_path, "I-04-DOSSIERS")
    dossiers = dossiers_bundle.get("people", [])
    return artifacts, source_artifacts, final_evidence, dossiers


def build_summary(
    artifacts_dir=ARTIFACTS_DIR,
    final_evidence_path=FINAL_EVIDENCE_PATH,
    dossiers_path=DOSSIERS_PATH,
):
    """Выполнить анализ и вернуть семь содержательных разделов отчёта."""
    artifacts, source_artifacts, final_evidence, dossiers = (
        load_investigation_inputs(
            artifacts_dir,
            final_evidence_path,
            dossiers_path,
        )
    )

    # Сначала получаем общий список, затем на его основе считаем рейтинг.
    evidence = collect_evidence(artifacts, final_evidence)
    ranking = rank_suspects(evidence, dossiers)
    if not ranking or ranking[0]["score"] <= 0:
        raise ValueError("Evidence does not identify a main suspect")

    # Только после проверки непустого положительного рейтинга безопасно брать [0].
    main_suspect = ranking[0]
    dossier = lookup_dossier(dossiers, main_suspect["person_id"])
    # Код называет направление проверки, но не выносит юридический приговор.
    return {
        "schema_version": 1,
        "investigation_id": "I-04",
        "generated_at": "2026-03-15T09:15:00+03:00",
        "source_artifacts": source_artifacts,
        "evidence": evidence,
        "suspect_ranking": ranking,
        "main_suspect": {
            "person_id": main_suspect["person_id"],
            "name": main_suspect["name"],
            "score": main_suspect["score"],
            "conclusion": "Главный подозреваемый для углублённой проверки",
        },
        "dossier": dict(dossier),
        "unresolved_threads": [
            dict(item) for item in final_evidence.get("unresolved_threads", [])
        ],
        "recommended_actions": [
            str(item) for item in final_evidence.get("recommended_actions", [])
        ],
    }


def save_summary(summary, path=OUTPUT_PATH):
    """Сохранить итоговый словарь как читаемый UTF-8 JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
    path.write_text(payload, encoding="utf-8")


def main():
    """Собрать файл и напечатать три короткие контрольные строки."""
    summary = build_summary()
    save_summary(summary)
    print(f"Собрано улик: {len(summary['evidence'])}")
    print(f"Основной подозреваемый: {summary['main_suspect']['name']}")
    print(f"Отчёт сохранён: {OUTPUT_PATH.name}")


# При импорте функции доступны без автоматической записи файла.
if __name__ == "__main__":
    main()
```
