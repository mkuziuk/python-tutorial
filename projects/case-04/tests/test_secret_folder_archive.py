from pathlib import Path
import hashlib
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

from secret_folder_archive import (  # noqa: E402
    build_evidence_index,
    compare_timeline_versions,
    console,
    detect_duplicates,
    file_sha256,
    render_timeline_difference,
    scan_folder,
)


class SecretFolderArchiveTests(unittest.TestCase):
    def test_file_sha256_matches_hashlib(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "note.txt"
            path.write_text("secret archive\n", encoding="utf-8")

            expected = hashlib.sha256("secret archive\n".encode("utf-8")).hexdigest()
            self.assertEqual(file_sha256(path), expected)

    def test_scan_folder_returns_relative_records(self):
        records = scan_folder(PROJECT_DIR / "data" / "secret_folder")
        paths = [record["path"] for record in records]

        self.assertEqual(len(records), 6)
        self.assertEqual(paths, sorted(paths))
        self.assertIn("evidence/photo_index.txt", paths)
        self.assertTrue(all(len(str(record["sha256"])) == 64 for record in records))

    def test_detect_duplicates_finds_photo_index_copy(self):
        records = scan_folder(PROJECT_DIR / "data" / "secret_folder")
        duplicates = detect_duplicates(records)

        self.assertEqual(len(duplicates), 1)
        self.assertEqual(
            duplicates[0]["paths"],
            ["evidence/photo_index.txt", "evidence/photo_index_copy.txt"],
        )

    def test_timeline_diff_surfaces_conflicting_times(self):
        drafts = PROJECT_DIR / "data" / "secret_folder" / "drafts"
        differences = compare_timeline_versions(
            drafts / "timeline.txt",
            drafts / "timeline_backup.txt",
        )

        self.assertTrue(any("22:53" in line for line in differences["current"]))
        self.assertTrue(any("23:07" in line for line in differences["backup"]))

        with console.capture() as capture:
            render_timeline_difference(differences)
        output = capture.get()
        self.assertIn("22:53", output)
        self.assertIn("23:07", output)

    def test_evidence_index_hashes_upstream_reports_and_folder(self):
        index = build_evidence_index(
            PROJECT_DIR / "data" / "secret_folder",
            PROJECT_DIR / "data" / "artifacts",
        )
        self.assertEqual(index["investigation_id"], "I-04")
        self.assertEqual(
            [item["investigation_id"] for item in index["verified_artifacts"]],
            ["I-01", "I-02", "I-03"],
        )
        self.assertEqual(len(index["source_files"]), 9)
        self.assertEqual(
            {item["finding_id"] for item in index["findings"]},
            {"F-I04-DUPLICATES", "F-I04-TIMELINE", "F-I04-ACCESS-LOG"},
        )
        access = next(item for item in index["findings"] if item["finding_id"] == "F-I04-ACCESS-LOG")
        self.assertEqual(len(access["events"]), 4)


if __name__ == "__main__":
    unittest.main()
