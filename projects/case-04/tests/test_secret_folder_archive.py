from pathlib import Path
import hashlib
import json
import sys
import tempfile
import unittest

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR / "solution"))

from secret_folder_archive import (  # noqa: E402
    build_manifest,
    compare_manifests,
    detect_duplicates,
    file_sha256,
    load_manifest,
    scan_folder,
    utc_timestamp,
    write_manifest,
)


class SecretFolderArchiveTests(unittest.TestCase):
    def test_file_sha256_matches_hashlib(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "note.txt"
            path.write_text("secret archive\n", encoding="utf-8")

            expected = hashlib.sha256("secret archive\n".encode("utf-8")).hexdigest()
            self.assertEqual(file_sha256(path), expected)

    def test_utc_timestamp_uses_z_suffix(self) -> None:
        self.assertEqual(utc_timestamp(0), "1970-01-01T00:00:00Z")

    def test_scan_folder_returns_relative_records(self) -> None:
        records = scan_folder(PROJECT_DIR / "data" / "secret_folder")
        paths = [record["path"] for record in records]

        self.assertEqual(len(records), 6)
        self.assertEqual(paths, sorted(paths))
        self.assertIn("evidence/photo_index.txt", paths)
        self.assertTrue(all(len(str(record["sha256"])) == 64 for record in records))
        self.assertTrue(all(str(record["modified_at"]).endswith("Z") for record in records))

    def test_detect_duplicates_finds_photo_index_copy(self) -> None:
        records = scan_folder(PROJECT_DIR / "data" / "secret_folder")
        duplicates = detect_duplicates(records)

        self.assertEqual(len(duplicates), 1)
        self.assertEqual(
            duplicates[0]["paths"],
            ["evidence/photo_index.txt", "evidence/photo_index_copy.txt"],
        )

    def test_compare_manifests_reports_added_removed_changed(self) -> None:
        previous = {
            "files": [
                {"path": "same.txt", "sha256": "aaa"},
                {"path": "changed.txt", "sha256": "old"},
                {"path": "removed.txt", "sha256": "gone"},
            ]
        }
        current = {
            "files": [
                {"path": "same.txt", "sha256": "aaa"},
                {"path": "changed.txt", "sha256": "new"},
                {"path": "added.txt", "sha256": "fresh"},
            ]
        }

        self.assertEqual(
            compare_manifests(previous, current),
            {
                "added": ["added.txt"],
                "removed": ["removed.txt"],
                "changed": ["changed.txt"],
                "unchanged": ["same.txt"],
            },
        )

    def test_write_and_load_manifest_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.json"
            manifest = {"files": [{"path": "a.txt", "sha256": "123"}], "root": "tmp"}

            write_manifest(manifest, path)
            self.assertEqual(load_manifest(path), manifest)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), manifest)

    def test_build_manifest_contains_summary_and_duplicates(self) -> None:
        manifest = build_manifest(PROJECT_DIR / "data" / "secret_folder")

        self.assertEqual(manifest["file_count"], 6)
        self.assertGreater(manifest["total_bytes"], 0)
        self.assertEqual(len(manifest["files"]), 6)
        self.assertEqual(len(manifest["duplicates"]), 1)


if __name__ == "__main__":
    unittest.main()
