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
SOURCE_DIR = PROJECT_DIR if TEST_TARGET == "learner" else PROJECT_DIR / "solution"
sys.path.insert(0, str(SOURCE_DIR))

from investigation_system import (  # noqa: E402
    CaseRepository,
    Evidence,
    EvidenceLink,
    build_board,
    build_report,
    console,
    load_artifacts,
    render_overview,
    render_search_results,
)


class InvestigationSystemTests(unittest.TestCase):
    def build_board(self):
        return build_board(
            PROJECT_DIR / "data" / "artifacts",
            PROJECT_DIR / "data" / "relationships.json",
        )

    def test_load_artifacts_verifies_chain(self):
        artifacts = load_artifacts(PROJECT_DIR / "data" / "artifacts")
        self.assertEqual(set(artifacts), {"I-01", "I-02", "I-03", "I-04"})
        self.assertEqual(
            artifacts["I-04"]["data"]["verified_artifacts"][0]["investigation_id"],
            "I-01",
        )

    def test_board_is_built_from_real_findings(self):
        investigation = self.build_board()
        self.assertEqual(len(investigation.source_artifacts), 4)
        self.assertEqual(len(investigation.evidence), 12)
        self.assertEqual(len(investigation.people), 4)
        self.assertEqual(len(investigation.hypotheses), 4)
        self.assertIsInstance(investigation.evidence[0], Evidence)
        self.assertTrue(all(item.origin_finding_id.startswith("F-I") for item in investigation.evidence))
        self.assertEqual(investigation.evidence_by_id("EV-TOUR-DRAFT").origin_finding_id, "F-I02-TEXT-MATCHES")

    def test_queries_answer_investigation_questions(self):
        investigation = self.build_board()
        self.assertEqual(
            {item.evidence_id for item in investigation.find_evidence("хронология")},
            {"EV-WORKING-2253", "EV-BACKUP-2307"},
        )
        nikita = {item.evidence_id for item in investigation.find_evidence("Никита")}
        self.assertTrue({"EV-KEY", "EV-NIKITA-STATEMENT"} <= nikita)
        linked = {
            item.evidence_id
            for item in investigation.evidence_for_hypothesis("H-PHISHING")
        }
        self.assertEqual(linked, {"EV-PHISH-LOCKOUT", "EV-PHISH-CAMERA"})

    def test_duplicate_evidence_and_invalid_link_are_rejected(self):
        investigation = self.build_board()
        with self.assertRaises(ValueError):
            investigation.add_evidence(investigation.evidence[0])
        with self.assertRaises(ValueError):
            EvidenceLink("EV-1", "H-1", "maybe", 1)

    def test_board_round_trips_and_keeps_origins(self):
        investigation = self.build_board()
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "05-case-board.json"
            CaseRepository(output_path).save(investigation)
            restored = CaseRepository(output_path).load()

        self.assertEqual(restored.evidence[0].origin_finding_id, investigation.evidence[0].origin_finding_id)
        self.assertEqual(restored.links[0].to_dict(), investigation.links[0].to_dict())
        self.assertEqual(len(restored.verified_evidence()), 12)

    def test_build_report_saves_i05_artifact(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "05-case-board.json"
            investigation = build_report(
                PROJECT_DIR / "data" / "artifacts",
                PROJECT_DIR / "data" / "relationships.json",
                output_path,
            )
            restored = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(restored["investigation_id"], "I-05")
        self.assertEqual(len(restored["source_artifacts"]), 4)
        self.assertEqual(len(investigation.links), 11)

    def test_render_functions_accept_built_board(self):
        investigation = self.build_board()
        with console.capture() as capture:
            render_overview(investigation)
            render_search_results("хронология", investigation.find_evidence("хронология"))
        output = capture.get()
        self.assertIn("Расследование: Ночь перед открытием", output)
        self.assertIn("Проверенных входных отчётов: 4", output)
        self.assertIn("EV-BACKUP-2307", output)


if __name__ == "__main__":
    unittest.main()
