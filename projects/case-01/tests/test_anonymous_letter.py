from collections import Counter
from pathlib import Path
import sys
import unittest

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR / "solution"))

from anonymous_letter import (  # noqa: E402
    build_profile,
    jaccard,
    normalize_words,
    punctuation_profile,
    rank_candidates,
    render_results,
)


class AnonymousLetterTests(unittest.TestCase):
    def test_normalize_words_keeps_russian_letters(self) -> None:
        text = "Ёжик видел след, но След исчез!"
        self.assertEqual(normalize_words(text), ["ёжик", "видел", "след", "но", "след", "исчез"])

    def test_punctuation_profile_counts_selected_marks(self) -> None:
        self.assertEqual(punctuation_profile("Да, нет. Правда? Да!"), Counter({",": 1, ".": 1, "?": 1, "!": 1}))

    def test_jaccard_compares_sets(self) -> None:
        self.assertAlmostEqual(jaccard({"след", "пауза"}, {"пауза", "ночь"}), 1 / 3)

    def test_build_profile_contains_core_metrics(self) -> None:
        profile = build_profile("Тест", "След есть. След рядом.")
        self.assertEqual(profile["word_count"], 4)
        self.assertEqual(profile["unique_words"], 3)
        self.assertGreater(profile["average_word_length"], 3)

    def test_rank_candidates_finds_morozova_first(self) -> None:
        result = rank_candidates(PROJECT_DIR / "data")
        self.assertEqual(result[0][0], "Алина Морозова")
        self.assertGreater(result[0][1], result[1][1])

    def test_render_results_accepts_ranking(self) -> None:
        render_results([("Алина Морозова", 0.69), ("Никита Королев", 0.51)])


if __name__ == "__main__":
    unittest.main()
