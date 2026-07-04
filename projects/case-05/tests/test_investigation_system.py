from pathlib import Path
import sys
import tempfile
import unittest

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR / "solution"))

from investigation_system import (  # noqa: E402
    CaseRepository,
    Evidence,
    Investigation,
    build_report,
    render_overview,
    render_search_results,
)


class InvestigationSystemTests(unittest.TestCase):
    def load_seed(self) -> Investigation:
        return CaseRepository(PROJECT_DIR / "data" / "case_seed.json").load()

    def test_repository_loads_composed_objects(self) -> None:
        investigation = self.load_seed()
        self.assertEqual(investigation.case_id, "case-05-draft-archive")
        self.assertEqual(len(investigation.people), 4)
        self.assertEqual(len(investigation.evidence), 5)
        self.assertIsInstance(investigation.evidence[0], Evidence)

    def test_evidence_search_checks_tags_and_body(self) -> None:
        investigation = self.load_seed()
        self.assertEqual(
            [item.evidence_id for item in investigation.find_evidence("цепочка")],
            ["EV-001", "EV-003"],
        )
        self.assertEqual(
            [item.evidence_id for item in investigation.find_evidence("zeta-14")],
            ["EV-005"],
        )

    def test_priority_evidence_sorts_by_reliability_then_id(self) -> None:
        investigation = self.load_seed()
        self.assertEqual(
            [item.evidence_id for item in investigation.priority_evidence()],
            ["EV-001", "EV-003", "EV-002"],
        )

    def test_tag_index_groups_evidence(self) -> None:
        investigation = self.load_seed()
        index = investigation.tag_index()
        self.assertEqual([item.evidence_id for item in index["архив"]], ["EV-002", "EV-005"])
        self.assertEqual([item.evidence_id for item in index["цепочка"]], ["EV-001", "EV-003"])

    def test_add_evidence_rejects_duplicate_id(self) -> None:
        investigation = self.load_seed()
        duplicate = Evidence(
            evidence_id="EV-001",
            kind="memo",
            title="Дубликат",
            source="проверка",
            body="Повторный ID не должен попасть в дело.",
            tags=["проверка"],
        )
        with self.assertRaises(ValueError):
            investigation.add_evidence(duplicate)

    def test_repository_round_trips_json(self) -> None:
        investigation = self.load_seed()
        investigation.add_note("Тест", "Проверяем сохранение.", "2026-02-12T13:00:00")

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "saved_case.json"
            CaseRepository(output_path).save(investigation)
            restored = CaseRepository(output_path).load()

        self.assertEqual(restored.notes[-1].author, "Тест")
        self.assertEqual(restored.evidence[0].tags, ["текст", "цепочка", "черновики"])

    def test_build_report_adds_note_and_saves_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "case_report.json"
            investigation = build_report(PROJECT_DIR / "data" / "case_seed.json", output_path)
            self.assertTrue(output_path.exists())

        self.assertEqual(investigation.notes[-1].author, "Система расследований")
        self.assertIn("2", investigation.notes[-1].text)

    def test_render_functions_accept_loaded_data(self) -> None:
        investigation = self.load_seed()
        render_overview(investigation)
        render_search_results("цепочка", investigation.find_evidence("цепочка"))


if __name__ == "__main__":
    unittest.main()
