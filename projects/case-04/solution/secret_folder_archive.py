from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "secret_folder"
MANIFEST_PATH = Path(__file__).resolve().parents[1] / "manifest.json"
console = Console()


def utc_timestamp(seconds: float | None = None) -> str:
    if seconds is None:
        moment = datetime.now(timezone.utc)
    else:
        moment = datetime.fromtimestamp(seconds, tz=timezone.utc)

    return moment.isoformat(timespec="seconds").replace("+00:00", "Z")


def iter_files(root: Path) -> list[Path]:
    if not root.exists():
        raise FileNotFoundError(f"Folder not found: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Expected a folder: {root}")

    return sorted(path for path in root.rglob("*") if path.is_file())


def relative_name(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def file_sha256(path: Path, chunk_size: int = 65_536) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        while chunk := file.read(chunk_size):
            digest.update(chunk)

    return digest.hexdigest()


def build_record(root: Path, path: Path) -> dict[str, object]:
    stat = path.stat()

    return {
        "path": relative_name(root, path),
        "size": stat.st_size,
        "sha256": file_sha256(path),
        "modified_at": utc_timestamp(stat.st_mtime),
    }


def scan_folder(root: Path) -> list[dict[str, object]]:
    root = root.resolve()
    return [build_record(root, path) for path in iter_files(root)]


def detect_duplicates(records: list[dict[str, object]]) -> list[dict[str, object]]:
    by_hash: dict[str, list[str]] = {}

    for record in records:
        digest = str(record["sha256"])
        by_hash.setdefault(digest, []).append(str(record["path"]))

    groups = []
    for digest, paths in sorted(by_hash.items()):
        if len(paths) > 1:
            groups.append({"sha256": digest, "paths": sorted(paths)})

    return groups


def build_manifest(root: Path) -> dict[str, object]:
    records = scan_folder(root)

    return {
        "scanned_at": utc_timestamp(),
        "root": root.name,
        "file_count": len(records),
        "total_bytes": sum(int(record["size"]) for record in records),
        "files": records,
        "duplicates": detect_duplicates(records),
    }


def load_manifest(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Manifest must contain a JSON object: {path}")
    return data


def write_manifest(manifest: dict[str, object], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(manifest, ensure_ascii=False, indent=2)
    path.write_text(text + "\n", encoding="utf-8")


def index_by_path(manifest: dict[str, object]) -> dict[str, dict[str, object]]:
    return {
        str(record["path"]): record
        for record in manifest.get("files", [])
        if isinstance(record, dict)
    }


def compare_manifests(
    previous: dict[str, object],
    current: dict[str, object],
) -> dict[str, list[str]]:
    old_files = index_by_path(previous)
    new_files = index_by_path(current)
    old_paths = set(old_files)
    new_paths = set(new_files)

    changed = []
    for path in sorted(old_paths & new_paths):
        if old_files[path].get("sha256") != new_files[path].get("sha256"):
            changed.append(path)

    unchanged = sorted(
        path
        for path in old_paths & new_paths
        if old_files[path].get("sha256") == new_files[path].get("sha256")
    )

    return {
        "added": sorted(new_paths - old_paths),
        "removed": sorted(old_paths - new_paths),
        "changed": changed,
        "unchanged": unchanged,
    }


def render_report(
    manifest: dict[str, object],
    changes: dict[str, list[str]],
    had_previous_manifest: bool,
) -> None:
    summary = Table(title="Индекс секретной папки")
    summary.add_column("Показатель")
    summary.add_column("Значение", justify="right")
    summary.add_row("Файлов", str(manifest["file_count"]))
    summary.add_row("Байт", str(manifest["total_bytes"]))
    summary.add_row("Групп дублей", str(len(manifest["duplicates"])))
    console.print(summary)

    if not had_previous_manifest:
        console.print("[yellow]Предыдущий manifest.json не найден. Это первый снимок.[/yellow]")

    change_table = Table(title="Изменения")
    change_table.add_column("Тип")
    change_table.add_column("Количество", justify="right")
    change_table.add_column("Файлы")

    labels = {
        "added": "Добавлены",
        "removed": "Удалены",
        "changed": "Изменены",
        "unchanged": "Без изменений",
    }

    for key, label in labels.items():
        paths = changes[key]
        change_table.add_row(label, str(len(paths)), ", ".join(paths[:4]) or "-")

    console.print(change_table)


def render_duplicates(manifest: dict[str, object]) -> None:
    groups = manifest["duplicates"]
    if not groups:
        console.print("[green]Дубли не найдены.[/green]")
        return

    table = Table(title="Возможные дубли")
    table.add_column("SHA-256", overflow="fold")
    table.add_column("Файлы")

    for group in groups:
        table.add_row(str(group["sha256"])[:16] + "...", "\n".join(group["paths"]))

    console.print(table)


def main() -> None:
    previous = load_manifest(MANIFEST_PATH)
    current = build_manifest(DATA_DIR)
    changes = compare_manifests(previous or {"files": []}, current)

    render_report(current, changes, previous is not None)
    render_duplicates(current)
    write_manifest(current, MANIFEST_PATH)
    console.print(f"[bold green]Манифест сохранен:[/bold green] {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
