import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

PROJECT_DIR = Path(__file__).resolve().parents[1]
TEST_TARGET = os.environ.get("PYTHON_TUTORIAL_TEST_TARGET", "learner")
if TEST_TARGET not in {"learner", "solution"}:
    raise RuntimeError(f"Unknown test target: {TEST_TARGET}")
SOURCE_DIR = PROJECT_DIR if TEST_TARGET == "learner" else PROJECT_DIR / "solution"
sys.path.insert(0, str(SOURCE_DIR))

from final_evidence import (  # noqa: E402
    build_summary,
    collect_evidence,
    find_finding,
    load_artifact,
    lookup_dossier,
    rank_suspects,
    resolve_effect_person,
    save_summary,
)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


class FinalEvidenceTests(unittest.TestCase):
    def setUp(self):
        artifacts_dir = PROJECT_DIR / "data" / "artifacts"
        self.artifacts = {
            investigation_id: read_json(artifacts_dir / filename)
            for investigation_id, filename in {
                "I-01": "01-authorship.json",
                "I-02": "02-text-matches.json",
                "I-03": "03-mail-review.json",
            }.items()
        }
        self.final_evidence = read_json(PROJECT_DIR / "data" / "final_evidence.json")
        self.dossiers = read_json(PROJECT_DIR / "data" / "suspect_dossiers.json")["people"]

    def test_missing_artifact_is_not_silently_ignored(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            with self.assertRaises(FileNotFoundError):
                build_summary(artifacts_dir=Path(tmp_dir))

    def test_load_artifact_rejects_wrong_investigation_id(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "artifact.json"
            path.write_text('{"investigation_id": "I-99"}', encoding="utf-8")
            with self.assertRaises(ValueError):
                load_artifact(path, "I-01")

    def test_find_finding_rejects_unknown_id(self):
        with self.assertRaises(KeyError):
            find_finding(self.artifacts["I-01"], "F-MISSING")

    def test_collect_evidence_preserves_upstream_limitations(self):
        evidence = collect_evidence(self.artifacts, self.final_evidence)
        by_id = {item["finding_id"]: item for item in evidence}
        self.assertIn("не устанавливает автора", by_id["F-I01-AUTHORSHIP"]["limitation"])
        self.assertIn("не доказывают", by_id["F-I03-LOCKOUT"]["limitation"])
        self.assertIn(
            "не устанавливают направление копирования",
            by_id["F-I02-TEXT-MATCHES"]["limitation"],
        )

    def test_collect_evidence_marks_missing_upstream_limitation(self):
        artifacts = copy.deepcopy(self.artifacts)
        artifacts["I-02"]["findings"][0].pop("limitation")
        evidence = collect_evidence(artifacts, self.final_evidence)
        by_id = {item["finding_id"]: item for item in evidence}
        self.assertIn(
            "не указано в исходном артефакте",
            by_id["F-I02-TEXT-MATCHES"]["limitation"],
        )

    def test_collect_evidence_rejects_duplicate_finding_id(self):
        duplicate = copy.deepcopy(self.final_evidence)
        duplicate["findings"].append(copy.deepcopy(duplicate["findings"][0]))
        with self.assertRaises(ValueError):
            collect_evidence(self.artifacts, duplicate)

    def test_lookup_dossier_handles_known_and_unknown_people(self):
        dossier = lookup_dossier(self.dossiers, "P-NIKITA")
        self.assertEqual(dossier["account"], "nikita.k")
        with self.assertRaises(KeyError):
            lookup_dossier(self.dossiers, "P-UNKNOWN")

    def test_effects_resolve_through_local_dossiers(self):
        people = {item["person_id"]: item for item in self.dossiers}
        self.assertEqual(
            resolve_effect_person(
                {"match_field": "account", "match_value": "nikita.k"},
                people,
            ),
            "P-NIKITA",
        )
        self.assertTrue(
            all(
                "person_id" not in effect
                for finding in self.final_evidence["findings"]
                for effect in finding.get("effects", [])
            )
        )

    def test_ranking_rejects_effect_without_matching_dossier(self):
        evidence = collect_evidence(self.artifacts, self.final_evidence)
        evidence[0]["effects"] = [
            {
                "match_field": "account",
                "match_value": "unknown.user",
                "stance": "support",
                "weight": 1,
            }
        ]
        with self.assertRaises(ValueError):
            rank_suspects(evidence, self.dossiers)

    def test_ranking_puts_nikita_first(self):
        evidence = collect_evidence(self.artifacts, self.final_evidence)
        ranking = rank_suspects(evidence, self.dossiers)
        self.assertEqual(ranking[0]["person_id"], "P-NIKITA")
        self.assertEqual(ranking[0]["score"], 10)
        self.assertEqual(
            [item["name"] for item in ranking[1:]],
            ["Алина Морозова", "Илья Соколов"],
        )

    def test_summary_selects_nikita_without_declaring_a_verdict(self):
        summary = build_summary()
        self.assertEqual(summary["investigation_id"], "I-04")
        self.assertEqual(summary["main_suspect"]["person_id"], "P-NIKITA")
        self.assertIn("подозреваемый", summary["main_suspect"]["conclusion"].casefold())
        self.assertNotIn("винов", json.dumps(summary["main_suspect"], ensure_ascii=False).casefold())
        self.assertEqual(summary["dossier"]["hardware_key_id"], "NK-17")

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "04-investigation-summary.json"
            save_summary(summary, path)
            self.assertEqual(read_json(path), summary)


if __name__ == "__main__":
    unittest.main()
