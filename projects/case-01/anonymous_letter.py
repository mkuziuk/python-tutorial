from pathlib import Path

from rich.console import Console

DATA_DIR = Path(__file__).with_name("data")
console = Console()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> None:
    anonymous_text = read_text(DATA_DIR / "anonymous.txt")
    samples = sorted(DATA_DIR.glob("author_*.txt"))

    console.print("[bold cyan]Материалы дела загружены.[/bold cyan]")
    console.print(f"Анонимное письмо: {len(anonymous_text)} символов")
    console.print(f"Образцы кандидатов: {len(samples)} файла")
    console.print("\n[dim]Дальше в главе мы превратим эти тексты в профили авторов.[/dim]")


if __name__ == "__main__":
    main()
