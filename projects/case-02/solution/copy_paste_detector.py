from itertools import combinations
from pathlib import Path
from typing import Any, cast

from rich.console import Console
from rich.table import Table

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
NGRAM_SIZE = 4
TOP_EXAMPLES = 3

console = Console()

Ngram = tuple[str, ...]
TextProfile = dict[str, Any]
OverlapResult = dict[str, Any]

DISPLAY_NAMES = {
    "fragment_atrium_report": "Отчет атриума",
    "fragment_greenhouse_note": "Заметка о теплице",
    "fragment_river_walk": "Маршрут у реки",
    "fragment_sensor_lab": "Дневник сенсорной лаборатории",
    "fragment_school_blog": "Блог кружка",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalize_words(text: str) -> list[str]:
    cleaned: list[str] = []

    for char in text.lower():
        if char.isalpha():
            cleaned.append(char)
        else:
            cleaned.append(" ")

    return "".join(cleaned).split()


def make_ngrams(words: list[str], size: int = NGRAM_SIZE) -> list[Ngram]:
    if size < 1:
        raise ValueError("N-gram size must be positive")

    return [
        tuple(words[index : index + size])
        for index in range(len(words) - size + 1)
    ]


def display_name(path: Path) -> str:
    return DISPLAY_NAMES.get(path.stem, path.stem.replace("_", " ").title())


def build_profile(path: Path, ngram_size: int = NGRAM_SIZE) -> TextProfile:
    text = read_text(path)
    words = normalize_words(text)
    ngrams = set(make_ngrams(words, ngram_size))

    return {
        "path": path,
        "title": display_name(path),
        "word_count": len(words),
        "ngram_count": len(ngrams),
        "ngrams": ngrams,
    }


def overlap_score(left: set[Ngram], right: set[Ngram]) -> float:
    if not left or not right:
        return 0.0

    shared = left & right
    if not shared:
        return 0.0

    containment = len(shared) / min(len(left), len(right))
    jaccard = len(shared) / len(left | right)
    return round(containment * 0.7 + jaccard * 0.3, 3)


def compare_profiles(left: TextProfile, right: TextProfile) -> OverlapResult:
    left_ngrams = cast(set[Ngram], left["ngrams"])
    right_ngrams = cast(set[Ngram], right["ngrams"])
    shared_ngrams = sorted(left_ngrams & right_ngrams)

    return {
        "pair": (str(left["title"]), str(right["title"])),
        "score": overlap_score(left_ngrams, right_ngrams),
        "shared_count": len(shared_ngrams),
        "examples": shared_ngrams[:TOP_EXAMPLES],
    }


def load_profiles(data_dir: Path = DATA_DIR, ngram_size: int = NGRAM_SIZE) -> list[TextProfile]:
    paths = sorted(data_dir.glob("fragment_*.txt"))
    if not paths:
        raise FileNotFoundError(f"No fragment_*.txt files found in {data_dir}")

    return [build_profile(path, ngram_size) for path in paths]


def rank_overlaps(data_dir: Path = DATA_DIR, ngram_size: int = NGRAM_SIZE) -> list[OverlapResult]:
    profiles = load_profiles(data_dir, ngram_size)
    results: list[OverlapResult] = []

    for left, right in combinations(profiles, 2):
        result = compare_profiles(left, right)
        if int(result["shared_count"]) > 0:
            results.append(result)

    return sorted(
        results,
        key=lambda item: (float(item["score"]), int(item["shared_count"])),
        reverse=True,
    )


def format_ngram(ngram: Ngram) -> str:
    return " ".join(ngram)


def render_results(results: list[OverlapResult], limit: int = 5) -> None:
    table = Table(title="Подозрительные совпадения")
    table.add_column("Место", justify="right", style="cyan")
    table.add_column("Пара")
    table.add_column("Оценка", justify="right")
    table.add_column("Общих n-грамм", justify="right")
    table.add_column("Пример")

    for position, result in enumerate(results[:limit], start=1):
        left, right = cast(tuple[str, str], result["pair"])
        examples = cast(list[Ngram], result["examples"])
        example = format_ngram(examples[0]) if examples else "нет общих n-грамм"

        table.add_row(
            str(position),
            f"{left} / {right}",
            f"{float(result['score']):.3f}",
            str(result["shared_count"]),
            example,
        )

    console.print(table)

    if results:
        best = results[0]
        left, right = cast(tuple[str, str], best["pair"])
        console.print(
            f"\n[bold]Главная версия:[/bold] {left} и {right} "
            f"имеют самый сильный общий след: [cyan]{float(best['score']):.3f}[/cyan]."
        )


def main() -> None:
    render_results(rank_overlaps())


if __name__ == "__main__":
    main()
