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

from copy_paste_detector import (  # noqa: E402
    build_profile,
    build_artifact,
    load_authorship_lead,
    make_ngrams,
    normalize_words,
    overlap_score,
    rank_overlaps,
    render_results,
    save_artifact,
)


class CopyPasteDetectorTests(unittest.TestCase):
    def test_normalize_words_removes_punctuation_and_case(self):
        text = "Журнал, ЖУРНАЛ! Датчик-01 готов?"
        self.assertEqual(normalize_words(text), ["журнал", "журнал", "датчик", "готов"])

    def test_make_ngrams_returns_word_tuples(self):
        words = ["каждое", "утро", "группа", "открывает", "журнал"]
        self.assertEqual(
            make_ngrams(words, size=4),
            [
                ("каждое", "утро", "группа", "открывает"),
                ("утро", "группа", "открывает", "журнал"),
            ],
        )

    def test_make_ngrams_rejects_invalid_size(self):
        with self.assertRaises(ValueError):
            make_ngrams(["текст"], size=0)

    def test_overlap_score_combines_containment_and_jaccard(self):
        left = {("а", "б"), ("б", "в"), ("в", "г")}
        right = {("б", "в"), ("в", "г"), ("г", "д")}
        self.assertEqual(overlap_score(left, right), 0.617)

    def test_build_profile_contains_ngram_set(self):
        profile = build_profile(PROJECT_DIR / "data" / "report_tour_draft.txt")
        self.assertEqual(profile["title"], "Черновик экскурсии")
        self.assertGreater(profile["word_count"], 60)
        self.assertIsInstance(profile["ngrams"], set)

    def test_rank_overlaps_finds_strongest_pair(self):
        ranking = rank_overlaps(PROJECT_DIR / "data")
        self.assertEqual(
            set(ranking[0]["pair"]),
            {"Опись Северного стола", "Черновик экскурсии"},
        )
        self.assertGreater(float(ranking[0]["score"]), 0.25)
        self.assertEqual(
            set(ranking[1]["pair"]),
            {"Отчёт охраны", "Отчёт учебного стенда"},
        )
        self.assertEqual(len(ranking), 2)

    def test_artifact_consumes_authorship_result(self):
        authorship_path = PROJECT_DIR / "data" / "artifacts" / "01-authorship.json"
        lead = load_authorship_lead(authorship_path)
        artifact = build_artifact(rank_overlaps(PROJECT_DIR / "data"), authorship_path)

        self.assertEqual(lead["candidate"], "Алина Морозова")
        self.assertEqual(artifact["investigation_id"], "I-02")
        self.assertEqual(artifact["inputs"]["authorship_lead"]["finding_id"], "F-I01-AUTHORSHIP")
        self.assertEqual(artifact["findings"][0]["matches"][0]["pair"], ["Опись Северного стола", "Черновик экскурсии"])

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "02-text-matches.json"
            save_artifact(artifact, path)
            restored = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(restored, artifact)

    def test_render_results_accepts_ranking(self):
        render_results(
            [
                {
                    "pair": ("Опись Северного стола", "Черновик экскурсии"),
                    "score": 0.27,
                    "shared_count": 49,
                    "examples": [("а", "сначала", "отмечает", "расхождение")],
                }
            ]
        )


if __name__ == "__main__":
    unittest.main()
