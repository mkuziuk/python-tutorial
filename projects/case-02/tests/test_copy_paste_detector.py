from pathlib import Path
import sys
import unittest

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR / "solution"))

from copy_paste_detector import (  # noqa: E402
    build_profile,
    make_ngrams,
    normalize_words,
    overlap_score,
    rank_overlaps,
    render_results,
)


class CopyPasteDetectorTests(unittest.TestCase):
    def test_normalize_words_removes_punctuation_and_case(self) -> None:
        text = "Журнал, ЖУРНАЛ! Датчик-01 готов?"
        self.assertEqual(normalize_words(text), ["журнал", "журнал", "датчик", "готов"])

    def test_make_ngrams_returns_word_tuples(self) -> None:
        words = ["каждое", "утро", "группа", "открывает", "журнал"]
        self.assertEqual(
            make_ngrams(words, size=4),
            [
                ("каждое", "утро", "группа", "открывает"),
                ("утро", "группа", "открывает", "журнал"),
            ],
        )

    def test_make_ngrams_rejects_invalid_size(self) -> None:
        with self.assertRaises(ValueError):
            make_ngrams(["текст"], size=0)

    def test_overlap_score_combines_containment_and_jaccard(self) -> None:
        left = {("а", "б"), ("б", "в"), ("в", "г")}
        right = {("б", "в"), ("в", "г"), ("г", "д")}
        self.assertEqual(overlap_score(left, right), 0.617)

    def test_build_profile_contains_ngram_set(self) -> None:
        profile = build_profile(PROJECT_DIR / "data" / "report_tour_draft.txt")
        self.assertEqual(profile["title"], "Черновик экскурсии")
        self.assertGreater(profile["word_count"], 60)
        self.assertIsInstance(profile["ngrams"], set)

    def test_rank_overlaps_finds_strongest_pair(self) -> None:
        ranking = rank_overlaps(PROJECT_DIR / "data")
        self.assertEqual(
            set(ranking[0]["pair"]),
            {"Опись Северного стола", "Черновик экскурсии"},
        )
        self.assertGreater(float(ranking[0]["score"]), 0.45)
        self.assertEqual(
            set(ranking[1]["pair"]),
            {"Отчет охраны", "Дневник ночного сигнала"},
        )
        self.assertEqual(len(ranking), 2)

    def test_render_results_accepts_ranking(self) -> None:
        render_results(
            [
                {
                    "pair": ("Опись Северного стола", "Черновик экскурсии"),
                    "score": 0.61,
                    "shared_count": 31,
                    "examples": [("каждое", "утро", "дежурная", "группа")],
                }
            ]
        )


if __name__ == "__main__":
    unittest.main()
