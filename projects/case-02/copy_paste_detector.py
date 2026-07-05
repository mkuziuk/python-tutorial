from pathlib import Path

from rich.console import Console

DATA_DIR = Path(__file__).with_name("data")

console = Console()


def main():
    paths = sorted(DATA_DIR.glob("report_*.txt"))

    console.print("[bold cyan]Материалы дела загружены.[/bold cyan]")
    console.print(f"Отчеты: {len(paths)} файла")

    for path in paths:
        console.print(f"- {path.name}")

    console.print(
        "\n[dim]Дальше в главе мы добавим чтение, n-граммы и сравнение отчетов.[/dim]"
    )


if __name__ == "__main__":
    main()
