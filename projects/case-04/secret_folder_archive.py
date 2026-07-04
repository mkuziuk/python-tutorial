from pathlib import Path

from rich.console import Console
from rich.table import Table

DATA_DIR = Path(__file__).with_name("data") / "secret_folder"
MANIFEST_PATH = Path(__file__).with_name("manifest.json")
console = Console()


def iter_files(root: Path) -> list[Path]:
    if not root.exists():
        raise FileNotFoundError(f"Folder not found: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Expected a folder: {root}")

    return sorted(path for path in root.rglob("*") if path.is_file())


def relative_name(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def build_record(root: Path, path: Path) -> dict[str, object]:
    stat = path.stat()

    return {
        "path": relative_name(root, path),
        "size": stat.st_size,
        "sha256": "<добавьте hashlib.sha256>",
        "modified_at": "<добавьте timestamp UTC>",
    }


def scan_folder(root: Path) -> list[dict[str, object]]:
    root = root.resolve()
    return [build_record(root, path) for path in iter_files(root)]


def render_preview(records: list[dict[str, object]]) -> None:
    table = Table(title="Черновой индекс секретной папки")
    table.add_column("Файл")
    table.add_column("Байт", justify="right")
    table.add_column("SHA-256")
    table.add_column("Изменен")

    for record in records:
        table.add_row(
            str(record["path"]),
            str(record["size"]),
            str(record["sha256"]),
            str(record["modified_at"]),
        )

    console.print(table)


def main() -> None:
    records = scan_folder(DATA_DIR)
    render_preview(records)
    console.print(f"[dim]Найдено файлов: {len(records)}[/dim]")
    console.print("[dim]Дальше в главе мы добавим хэши, JSON-манифест и сравнение снимков.[/dim]")


if __name__ == "__main__":
    main()
