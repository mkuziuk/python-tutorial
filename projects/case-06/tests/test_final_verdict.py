from dataclasses import FrozenInstanceError
from pathlib import Path
import json
import os
import sys
import tempfile
import unittest


PROJECT_DIR = Path(__file__).resolve().parents[1]
TEST_TARGET = os.environ.get("PYTHON_TUTORIAL_TEST_TARGET", "learner")
if TEST_TARGET not in {"learner", "solution"}:
    raise RuntimeError(f"Unknown test target: {TEST_TARGET}")
IMPLEMENTATION_DIR = (
    PROJECT_DIR if TEST_TARGET == "learner" else PROJECT_DIR / "solution"
)
sys.path.insert(0, str(IMPLEMENTATION_DIR))

from final_verdict import (  # noqa: E402
    AssessmentStatus,
    EvidenceKind,
    Stance,
    build_timeline,
    build_verdict,
    classify_assessment,
    load_bundle,
    rank_hypotheses,
    save_verdict,
)


class FinalVerdictTests(unittest.TestCase):
    def setUp(self):
        self.bundle = load_bundle(
            PROJECT_DIR / "data" / "artifacts" / "05-case-board.json",
            PROJECT_DIR / "data" / "morning_updates.json",
        )

    def test_bundle_loads_modern_typed_models(self):
        self.assertEqual(self.bundle.case_id, "case-06-final-verdict")
        self.assertEqual(len(self.bundle.evidence), 18)
        self.assertIs(self.bundle.evidence[0].kind, EvidenceKind.DOCUMENT)
        tour_draft = next(item for item in self.bundle.evidence if item.evidence_id == "EV-TOUR-DRAFT")
        self.assertIs(tour_draft.effects[0].stance, Stance.SUPPORT)
        with self.assertRaises(FrozenInstanceError):
            self.bundle.evidence[0].title = "changed"

    def test_timeline_is_chronological_and_keeps_provenance(self):
        timeline = build_timeline(self.bundle.evidence)
        self.assertEqual(timeline[0]["evidence_id"], "EV-TOUR-DRAFT")
        self.assertEqual(timeline[-1]["evidence_id"], "EV-ALINA-ADMISSION")
        self.assertTrue(all(item["source"] for item in timeline))
        self.assertEqual(
            [item["occurred_at"] for item in timeline],
            sorted(item["occurred_at"] for item in timeline),
        )

    def test_match_based_classification_handles_boundaries(self):
        self.assertIs(
            classify_assessment(15, 0), AssessmentStatus.STRONGLY_SUPPORTED
        )
        self.assertIs(classify_assessment(12, 5), AssessmentStatus.SUPPORTED)
        self.assertIs(classify_assessment(4, 8), AssessmentStatus.NOT_SUPPORTED)
        self.assertIs(classify_assessment(0, 0), AssessmentStatus.NO_EVIDENCE)

    def test_hypotheses_are_ranked_with_support_and_conflicts(self):
        ranked = rank_hypotheses(self.bundle)
        self.assertNotIn(
            "H-ALINA",
            [item.hypothesis.hypothesis_id for item in ranked],
        )
        self.assertEqual(
            [item.hypothesis.hypothesis_id for item in ranked],
            ["H-NIKITA", "H-MISTAKE", "H-PHISHING", "H-SYNC"],
        )
        self.assertEqual(ranked[0].score, 73)
        self.assertIs(ranked[0].status, AssessmentStatus.STRONGLY_SUPPORTED)
        self.assertIs(ranked[1].status, AssessmentStatus.UNRESOLVED)
        self.assertIn("EV-BACKUP-2307", ranked[0].support)
        self.assertIn("EV-SIGNED-AUDIT", ranked[0].support)
        self.assertIn("EV-NIKITA-STATEMENT", ranked[0].conflicts)
        self.assertEqual(ranked[1].score, 2)
        self.assertEqual(ranked[2].score, -16)
        self.assertEqual(ranked[-1].score, -20)
        self.assertIn("EV-TIMELINE-WORKING", ranked[-1].conflicts)
        self.assertIn("EV-SYNC-HEALTH", ranked[-1].conflicts)

    def test_verdict_resolves_plot_without_overclaiming(self):
        verdict = build_verdict(self.bundle)
        findings = verdict["findings"]
        self.assertEqual(
            findings["warning_author"]["finding"],
            "Алина Морозова написала анонимное предупреждение.",
        )
        self.assertEqual(
            findings["primary_hypothesis"]["hypothesis_id"], "H-NIKITA"
        )
        self.assertTrue(
            findings["primary_hypothesis"]["finding"].endswith(
                rank_hypotheses(self.bundle)[0].hypothesis.claim
            )
        )
        self.assertIn("Самая сильная рабочая гипотеза", findings["primary_hypothesis"]["finding"])
        self.assertIn("не доказывает", findings["primary_hypothesis"]["caveat"])
        self.assertEqual(
            findings["phishing"]["status"],
            "unresolved_vector_no_success_evidence",
        )
        self.assertIn("признаков успешного взлома нет", findings["phishing"]["finding"])

        evidence_ids = {item.evidence_id for item in self.bundle.evidence}
        for finding in findings.values():
            self.assertTrue(set(finding.get("basis", ())) <= evidence_ids)

    def test_operational_decision_is_complete(self):
        decision = build_verdict(self.bundle)["operational_decision"]
        self.assertEqual(decision["opening"], "postpone")
        self.assertEqual(len(decision["actions"]), 3)
        self.assertIn("строку 23:07", decision["actions"][0])
        self.assertIn("сохранить исходные", decision["actions"][0])
        self.assertIn("Сменить доступы", decision["actions"][1])
        self.assertIn("Опросить Никиту", decision["actions"][2])

    def test_verdict_round_trips_as_utf8_json(self):
        verdict = build_verdict(self.bundle)
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "verdict.json"
            save_verdict(verdict, output_path)
            restored = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(restored["case_id"], "case-06-final-verdict")
        self.assertEqual(restored["investigation_id"], "I-06")
        self.assertEqual(restored["ranked_hypotheses"][0]["score"], 73)
        self.assertEqual(restored["operational_decision"]["opening"], "postpone")


if __name__ == "__main__":
    unittest.main()
