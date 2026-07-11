from pathlib import Path
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
    Investigation,
    build_report,
    console,
    render_overview,
    render_search_results,
)


class InvestigationSystemTests(unittest.TestCase):
    def load_seed(self):
        return CaseRepository(PROJECT_DIR / "data" / "case_seed.json").load()

    def test_repository_loads_composed_objects(self):
        investigation = self.load_seed()
        self.assertEqual(investigation.case_id, "case-05-archive-alarm")
        self.assertEqual(len(investigation.people), 4)
        self.assertEqual(len(investigation.evidence), 7)
        self.assertIsInstance(investigation.evidence[0], Evidence)
        self.assertEqual(
            investigation.evidence[1].created_at,
            "2026-03-14T23:07:00+03:00",
        )
        self.assertTrue(
            all(item.source.startswith("case-") for item in investigation.evidence)
        )

    def test_evidence_search_checks_tags_and_body(self):
        investigation = self.load_seed()
        self.assertEqual(
            [item.evidence_id for item in investigation.find_evidence("доступ")],
            ["EV-003", "EV-005"],
        )
        self.assertEqual(
            [item.evidence_id for item in investigation.find_evidence("02-lockout")],
            ["EV-003"],
        )
        self.assertEqual(
            [
                item.evidence_id
                for item in investigation.find_evidence("2026-03-14T23:07")
            ],
            ["EV-002"],
        )

    def test_priority_evidence_sorts_by_reliability_then_id(self):
        investigation = self.load_seed()
        self.assertEqual(
            [item.evidence_id for item in investigation.priority_evidence()],
            ["EV-004", "EV-005", "EV-006"],
        )

    def test_tag_index_groups_evidence(self):
        investigation = self.load_seed()
        index = investigation.tag_index()
        self.assertEqual([item.evidence_id for item in index["доступ"]], ["EV-003", "EV-005"])
        self.assertEqual([item.evidence_id for item in index["почта"]], ["EV-003", "EV-007"])

    def test_add_evidence_rejects_duplicate_id(self):
        investigation = self.load_seed()
        duplicate = Evidence(
            evidence_id="EV-001",
            kind="memo",
            title="Дубликат",
            source="проверка",
            body="Повторный ID не должен попасть в дело.",
            created_at="2026-03-15T08:20:00+03:00",
            tags=["проверка"],
        )
        with self.assertRaises(ValueError):
            investigation.add_evidence(duplicate)

    def test_repository_round_trips_json(self):
        investigation = self.load_seed()
        investigation.add_note(
            "Тест", "Проверяем сохранение.", "2026-03-15T08:35:00+03:00"
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "saved_case.json"
            CaseRepository(output_path).save(investigation)
            restored = CaseRepository(output_path).load()

        self.assertEqual(restored.notes[-1].author, "Тест")
        self.assertEqual(restored.evidence[0].tags, ["авторство", "правка", "текст"])
        self.assertEqual(
            [item.created_at for item in restored.evidence],
            [item.created_at for item in investigation.evidence],
        )
        self.assertEqual(restored.evidence[5].created_at, "2026-03-14")

    def test_build_report_adds_note_and_saves_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "case_report.json"
            investigation = build_report(PROJECT_DIR / "data" / "case_seed.json", output_path)
            self.assertTrue(output_path.exists())

        self.assertEqual(investigation.notes[-1].author, "Доска расследования")
        self.assertEqual(len(investigation.notes), 2)
        self.assertIn("2", investigation.notes[-1].text)
        self.assertEqual(
            investigation.notes[-1].created_at,
            "2026-03-15T08:30:00+03:00",
        )

    def test_render_functions_accept_loaded_data(self):
        investigation = self.load_seed()
        investigation.add_note(
            "Тест", "Вторая заметка.", "2026-03-15T08:30:00+03:00"
        )

        with console.capture() as capture:
            render_overview(investigation)
            render_search_results("доступ", investigation.find_evidence("доступ"))
        output = capture.get()

        self.assertIn("Дело: Ночной сигнал архива", output)
        self.assertIn("Участников: 4", output)
        self.assertIn("Улик: 7", output)
        self.assertIn("Заметок: 2", output)
        self.assertIn("EV-003", output)
        self.assertIn("EV-005", output)


if __name__ == "__main__":
    unittest.main()
