from datetime import datetime, timezone
from difflib import ndiff
import hashlib
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table


def default_project_dir():
    script_dir = Path(__file__).resolve().parent
    if (script_dir / "data" / "secret_folder").exists():
        return script_dir
    return script_dir.parent


PROJECT_DIR = default_project_dir()
DATA_DIR = PROJECT_DIR / "data" / "secret_folder"
MANIFEST_PATH = PROJECT_DIR / "manifest.json"
TIMELINE_PATH = DATA_DIR / "drafts" / "timeline.txt"
TIMELINE_BACKUP_PATH = DATA_DIR / "drafts" / "timeline_backup.txt"
console = Console()


def utc_timestamp(seconds=None):
    # Явно используем UTC, чтобы время не зависело от часового пояса компьютера.
    if seconds is None:
        moment = datetime.now(timezone.utc)
    else:
        moment = datetime.fromtimestamp(seconds, tz=timezone.utc)

    return moment.isoformat(timespec="seconds").replace("+00:00", "Z")


def iter_files(root):
    if not root.exists():
        raise FileNotFoundError(f"Folder not found: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Expected a folder: {root}")

    # rglob("*") рекурсивно проходит и вложенные каталоги.
    return sorted(path for path in root.rglob("*") if path.is_file())


def relative_name(root, path):
    # В манифест пишем переносимый относительный путь, а не адрес конкретного компьютера.
    return path.relative_to(root).as_posix()


def file_sha256(path, chunk_size=65_536):
    digest = hashlib.sha256()

    # Чтение частями ограничивает расход памяти независимо от размера файла.
    with path.open("rb") as file:
        # Оператор := сохраняет блок и сразу проверяет, не закончился ли файл.
        while chunk := file.read(chunk_size):
            digest.update(chunk)

    return digest.hexdigest()


def build_record(root, path):
    stat = path.stat()

    # Хэш описывает содержимое, размер — байты, а modified_at — метаданные файловой системы.
    return {
        "path": relative_name(root, path),
        "size": stat.st_size,
        "sha256": file_sha256(path),
        "modified_at": utc_timestamp(stat.st_mtime),
    }


def scan_folder(root):
    root = root.resolve()
    return [build_record(root, path) for path in iter_files(root)]


def detect_duplicates(records):
    by_hash = {}

    for record in records:
        digest = str(record["sha256"])
        # При первом хэше setdefault создаёт список, затем возвращает его же.
        by_hash.setdefault(digest, []).append(str(record["path"]))

    groups = []
    for digest, paths in sorted(by_hash.items()):
        # Равный SHA-256 группирует байтовые дубли независимо от имени и каталога.
        if len(paths) > 1:
            groups.append({"sha256": digest, "paths": sorted(paths)})

    return groups


def build_manifest(root):
    records = scan_folder(root)

    return {
        "scanned_at": utc_timestamp(),
        "root": root.name,
        "file_count": len(records),
        "total_bytes": sum(int(record["size"]) for record in records),
        "files": records,
        "duplicates": detect_duplicates(records),
    }


def load_manifest(path):
    if not path.exists():
        return None

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Manifest must contain a JSON object: {path}")
    return data


def write_manifest(manifest, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(manifest, ensure_ascii=False, indent=2)
    path.write_text(text + "\n", encoding="utf-8")


def index_by_path(manifest):
    # index_by_path() строит словарь «путь → запись» из раздела files.
    # get("files", []) считает отсутствующий раздел пустым,
    # а isinstance() пропускает повреждённые записи другого типа.
    return {
        str(record["path"]): record
        for record in manifest.get("files", [])
        if isinstance(record, dict)
    }


def compare_manifests(previous, current):
    old_files = index_by_path(previous)
    new_files = index_by_path(current)
    old_paths = set(old_files)
    new_paths = set(new_files)

    # Пересечение — общие пути; разности множеств — добавленные и удалённые.
    changed = []
    for path in sorted(old_paths & new_paths):
        # В changed попадают пути, у которых изменился SHA-256.
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


def compare_timeline_versions(current_path, backup_path):
    current_lines = current_path.read_text(encoding="utf-8").splitlines()
    backup_lines = backup_path.read_text(encoding="utf-8").splitlines()
    differences = {"current": [], "backup": []}

    # В ndiff "- " относится к первой версии, "+ " — ко второй.
    for line in ndiff(current_lines, backup_lines):
        if line.startswith("- "):
            differences["current"].append(line[2:])
        elif line.startswith("+ "):
            differences["backup"].append(line[2:])

    return differences


def render_report(manifest, changes, had_previous_manifest):
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


def render_duplicates(manifest):
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


def render_timeline_difference(differences):
    table = Table(title="Расхождение хронологий")
    table.add_column("Версия")
    table.add_column("Строка только в этой версии")

    for line in differences["current"]:
        table.add_row("Рабочая", line)
    for line in differences["backup"]:
        table.add_row("Резервная", line)

    console.print(table)


def main():
    previous = load_manifest(MANIFEST_PATH)
    current = build_manifest(DATA_DIR)
    # На первом запуске сравниваем новый снимок с пустым списком файлов.
    changes = compare_manifests(previous or {"files": []}, current)

    render_report(current, changes, previous is not None)
    render_duplicates(current)
    timeline_differences = compare_timeline_versions(TIMELINE_PATH, TIMELINE_BACKUP_PATH)
    render_timeline_difference(timeline_differences)
    write_manifest(current, MANIFEST_PATH)
    console.print(f"[bold green]Манифест сохранён:[/bold green] {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
