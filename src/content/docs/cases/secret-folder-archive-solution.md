---
title: "Разбор полного решения"
description: "Полный код четвёртого дела: SHA-256, JSON-манифест, дубли, изменения и сравнение двух хронологий."
concepts:
  - pathlib
  - обход файлов
  - hashlib
  - JSON
  - timestamps
  - поиск изменений
  - difflib
  - Rich
difficulty: "средний"
projectId: "case-04"
time: "20-30 минут"
---

Обращайтесь к этой странице после самостоятельной сборки `secret_folder_archive.py`. Если открыть её раньше, работа сведётся к переписыванию готового ответа.

## Полный код

```python
from datetime import datetime, timezone
from difflib import ndiff
import hashlib
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table


def default_project_dir():
    # Проверка расположения data позволяет запускать один текст решения из двух каталогов.
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


# seconds, если передан, — Unix-время в секундах; результат всегда возвращается в UTC.
def utc_timestamp(seconds=None):
    # Явно используем UTC, чтобы время не зависело от часового пояса компьютера.
    # None означает время самого сканирования; для файла передаём его st_mtime.
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
    # Каталоги не индексируем, а сортировка делает порядок записей воспроизводимым.
    return sorted(path for path in root.rglob("*") if path.is_file())


def relative_name(root, path):
    # В манифест пишем переносимый относительный путь, а не адрес конкретного компьютера.
    return path.relative_to(root).as_posix()


# 65 536 байт — размер блока чтения, а не ограничение на размер файла.
def file_sha256(path, chunk_size=65_536):
    digest = hashlib.sha256()

    # Чтение частями ограничивает расход памяти независимо от размера файла.
    with path.open("rb") as file:
        # Оператор := сохраняет блок и сразу проверяет, не закончился ли файл.
        while chunk := file.read(chunk_size):
            digest.update(chunk)

    return digest.hexdigest()


def build_record(root, path):
    # stat() читаем один раз, чтобы размер и время относились к одному наблюдению файла.
    stat = path.stat()

    # Хэш описывает содержимое, размер — байты, а modified_at — метаданные файловой системы.
    return {
        "path": relative_name(root, path),
        "size": stat.st_size,
        "sha256": file_sha256(path),
        "modified_at": utc_timestamp(stat.st_mtime),
    }


def scan_folder(root):
    # Абсолютный root нужен только во время обхода; наружу всё равно выйдут относительные пути.
    root = root.resolve()
    return [build_record(root, path) for path in iter_files(root)]


def detect_duplicates(records):
    # Сначала строим индекс «хэш → пути», а уже затем оставляем только группы из нескольких файлов.
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
    # Один список records служит источником и счётчиков, и полного раздела files.
    records = scan_folder(root)

    return {
        "scanned_at": utc_timestamp(),
        "root": root.name,
        "file_count": len(records),
        # total_bytes измеряется в байтах и складывается из тех же записей, что попадут в files.
        "total_bytes": sum(int(record["size"]) for record in records),
        "files": records,
        "duplicates": detect_duplicates(records),
    }


def load_manifest(path):
    # Отсутствие манифеста означает первый запуск, а не повреждение данных.
    if not path.exists():
        return None

    # JSON разбираем только после проверки существования: синтаксическая ошибка не считается первым запуском.
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Manifest must contain a JSON object: {path}")
    return data


def write_manifest(manifest, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Читаемый JSON облегчает ручной аудит и сравнение версий в системе контроля версий.
    text = json.dumps(manifest, ensure_ascii=False, indent=2)
    path.write_text(text + "\n", encoding="utf-8")


def index_by_path(manifest):
    # Для сравнения берём только файлы: scanned_at меняется при каждом запуске и не является изменением архива.
    return {
        str(record["path"]): record
        for record in manifest.get("files", [])
        if isinstance(record, dict)
    }


def compare_manifests(previous, current):
    old_files = index_by_path(previous)
    new_files = index_by_path(current)
    # Путь служит идентичностью файла: переименование будет парой «удалён + добавлен», даже при том же хэше.
    old_paths = set(old_files)
    new_paths = set(new_files)

    # Пересечение — общие пути; разности множеств — добавленные и удалённые.
    changed = []
    for path in sorted(old_paths & new_paths):
        # Изменением считаем новое содержимое; один лишь mtime не создаёт ложную тревогу.
        if old_files[path].get("sha256") != new_files[path].get("sha256"):
            changed.append(path)

    # Сохраняем и неизменившиеся пути: категории вместе описывают весь снимок.
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
    # splitlines() сравнивает содержимое строк и намеренно не считает финальный перевод строки отдельной уликой.
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
        # В таблице показываем до четырёх имён, но количество рассчитано по полному списку.
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

    # В таблице сокращаем только отображение хэша; в манифесте остаются все 64 символа.
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
    # Перезаписываем снимок только после сравнения и отчёта, чтобы previous ещё описывал прошлый запуск.
    write_manifest(current, MANIFEST_PATH)
    console.print(f"[bold green]Манифест сохранён:[/bold green] {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
```

## Как читать решение

Данные проходят несколько этапов: `iter_files()` находит файлы, `build_record()` собирает запись с SHA-256, `build_manifest()` создаёт снимок для записи в JSON, `compare_manifests()` ищет изменения между запусками, а `compare_timeline_versions()` отдельно показывает расхождение двух существующих текстовых версий.

Главное решение — сравнивать содержимое по хэшу, а не по имени или времени. Имя и временная метка помогают читать отчёт, но изменение файла определяет SHA-256. `difflib.ndiff()` показывает конкретное различие текста: в отчёте видны строки с `22:53` и `23:07`, а не только два разных хэша.

Частые ошибки: сохранять абсолютные пути в манифесте, читать большие файлы целиком, определять изменение только по новой дате или забыть обработать первый запуск без `manifest.json`.

Справочник: [pathlib](../../field-guide/pathlib/), [hashlib](../../field-guide/hashlib/), [JSON](../../field-guide/json/), [exceptions](../../field-guide/exceptions/), [dict](../../field-guide/dict/), [list](../../field-guide/list/), [functions](../../field-guide/functions/), [Rich](../../field-guide/rich/).

## Что важно заметить

`pathlib` держит работу с путями читаемой: `rglob()`, `relative_to()`, `as_posix()` и `with_name()` убирают большую часть ручной склейки строк.

`hashlib.sha256()` читает байты файла и выдаёт стабильный отпечаток содержимого. Размер и временная метка полезны для отчёта, но изменение файла определяет именно хэш.

JSON-манифест намеренно остаётся простым: это словарь со списком файлов, группами дублей и временем сканирования. Такой формат легко расширять без переписывания всей программы.
