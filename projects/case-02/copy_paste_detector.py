from pathlib import Path

from rich.console import Console

DATA_DIR = Path(__file__).with_name("data")
NGRAM_SIZE = 4

console = Console()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalize_words(text: str) -> list[str]:
    """Rough first version: the chapter will replace this with safer cleanup."""
    return text.lower().split()


def make_ngrams(words: list[str], size: int = NGRAM_SIZE) -> list[tuple[str, ...]]:
    """Build neighboring word groups as tuples."""
    # TODO: move a window of length size across words and return tuple n-grams.
    return []


def main() -> None:
    paths = sorted(DATA_DIR.glob("fragment_*.txt"))

    console.print("[bold cyan]Материалы дела загружены.[/bold cyan]")
    console.print(f"Фрагменты: {len(paths)} файла")

    for path in paths:
        words = normalize_words(read_text(path))
        ngrams = make_ngrams(words)
        console.print(
            f"- {path.name}: {len(words)} слов, "
            f"{len(ngrams)} стартовых n-грамм"
        )

    console.print(
        "\n[dim]Дальше в главе мы научим программу сравнивать фрагменты попарно.[/dim]"
    )


if __name__ == "__main__":
    main()
