---
title: "Дело 04. Архивариус секретной папки"
description: "Собираем индексатор папки: pathlib, обход файлов, SHA-256, JSON-манифест, timestamps и поиск изменений."
concepts:
  - pathlib
  - file traversal
  - hashlib
  - JSON
  - timestamps
  - change detection
  - Rich
difficulty: "средний"
projectId: "case-04"
time: "100-130 минут"
---

<div class="case-meta">
  <p><strong>Миссия</strong> сделать спокойный инструмент для проверки секретной папки: что внутри, какие файлы совпадают и что изменилось с прошлого запуска.</p>
  <p><strong>Инструменты</strong> `pathlib`, рекурсивный обход файлов, `hashlib`, JSON, UTC-время, сравнение двух снимков.</p>
  <p><strong>Результат</strong> консольный архивариус, который пишет `manifest.json` и показывает изменения таблицами.</p>
</div>

<div class="materials-panel">
  <p><strong>Быстрые ссылки:</strong> <a href="../../downloads/case-04.zip">case-04.zip</a> · <a href="../../materials/">материалы всех дел</a> · <a href="../secret-folder-archive-solution/">разбор решения</a></p>
  <p><strong>Справочник:</strong> <a href="../../field-guide/pathlib/">pathlib</a> · <a href="../../field-guide/hashlib/">hashlib</a> · <a href="../../field-guide/json/">JSON</a> · <a href="../../field-guide/exceptions/">exceptions</a> · <a href="../../field-guide/dict/">dict</a> · <a href="../../field-guide/list/">list</a> · <a href="../../field-guide/rich/">Rich</a></p>
</div>

## Проблема

После текстов и писем расследование упирается в папку `secret_folder`. В ней лежат заметки, черновики, служебные списки, логи и копии. На глаз все выглядит спокойно, но по именам уже непонятно, какие файлы совпадают и что менялось между проверками.

Вопрос дела: как сделать опись папки так, чтобы завтра можно было проверить дубли и изменения без ручной памяти?

Обычная дата изменения помогает, но ей нельзя полностью доверять. Файл можно скопировать, переименовать или сохранить заново. Поэтому мы будем считать криптографический хэш SHA-256 через [`hashlib`](../../field-guide/hashlib/) и сохранять [JSON](../../field-guide/json/)-manifest: если два файла имеют одинаковый хэш, их содержимое совпадает байт в байт.

Скачайте архив [case-04.zip](../../downloads/case-04.zip) или откройте папку `projects/case-04/` в репозитории.

Внутри learner-набора:

- `secret_folder_archive.py` - стартовый файл, который уже умеет обходить папку и печатать черновую таблицу;
- `requirements.txt` - зависимость для красивого терминального вывода;
- `data/secret_folder/` - безопасная учебная папка с заметками и копиями;
- `check_result.txt` - форма результата для самопроверки.

Полное решение вынесено отдельно: [Разбор полного решения](../secret-folder-archive-solution/).

### Подготовка окружения

Нужен Python 3.14 или новее.

Windows PowerShell:

```powershell
cd path\to\case-04
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

macOS или Linux:

```bash
cd path/to/case-04
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Проверьте стартовый файл:

```bash
python secret_folder_archive.py
```

Он пока не пишет манифест и не считает хэши. Но он показывает, какие файлы нашел, и это хорошая точка старта.

## Стратегия

Мы построим программу как маленький конвейер:

1. Найти все обычные файлы внутри `data/secret_folder/`.
2. Для каждого файла собрать запись: путь, размер, SHA-256, время изменения.
3. Сложить записи в манифест.
4. Найти группы дублей по одинаковому SHA-256.
5. Если старый `manifest.json` уже есть, сравнить его с новым снимком.
6. Показать отчет и сохранить свежий манифест.

Запись одного файла будет выглядеть так:

```python
{
    "path": "evidence/photo_index.txt",
    "size": 172,
    "sha256": "8d4c...",
    "modified_at": "2026-07-04T18:20:10Z",
}
```

Мы храним путь относительно секретной папки. Так манифест можно перенести на другой компьютер: в нем не будет абсолютного пути вроде `/Users/...`.

## Сборка инструмента

Откройте `secret_folder_archive.py`. Вверху нам нужны стандартные модули и две сущности из Rich:

```python
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

DATA_DIR = Path(__file__).with_name("data") / "secret_folder"
MANIFEST_PATH = Path(__file__).with_name("manifest.json")
console = Console()
```

`Path(__file__).with_name("data")` привязывает путь к папке проекта, а не к тому месту, откуда вы запустили команду. Это важная привычка для учебных и реальных скриптов.

### Обход папки

[`pathlib`](../../field-guide/pathlib/) умеет рекурсивно проходить по дереву:

```python
def iter_files(root: Path) -> list[Path]:
    if not root.exists():
        raise FileNotFoundError(f"Folder not found: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Expected a folder: {root}")

    return sorted(path for path in root.rglob("*") if path.is_file())
```

`root.rglob("*")` находит все вложенные пути. Мы оставляем только файлы, потому что папки не имеют содержимого, которое можно хэшировать как обычный документ. Если папка отсутствует или вместо нее файл, функция явно бросает исключение, чтобы ошибка была заметна сразу.

### Относительный путь

Манифест должен быть читаемым:

```python
def relative_name(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()
```

`relative_to()` убирает начало пути, а `as_posix()` записывает разделители через `/`. Так JSON будет одинаково выглядеть на Windows, macOS и Linux.

### Хэш файла

Файл лучше читать кусками. Маленькие учебные файлы можно прочитать целиком, но привычка с чанками спасает, когда архив разрастается. `file_sha256()` принимает путь и возвращает строку-хэш; именно эта строка потом решает, одинаковые ли файлы.

```python
def file_sha256(path: Path, chunk_size: int = 65_536) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        while chunk := file.read(chunk_size):
            digest.update(chunk)

    return digest.hexdigest()
```

Мы открываем файл в режиме `rb`, потому что хэш считается по байтам, а не по строкам.

### Время в UTC

Для манифеста нужна предсказуемая запись времени. Не используем локальный часовой пояс: сегодня скрипт запускают в Москве, завтра на сервере в другой стране.

```python
def utc_timestamp(seconds: float | None = None) -> str:
    if seconds is None:
        moment = datetime.now(timezone.utc)
    else:
        moment = datetime.fromtimestamp(seconds, tz=timezone.utc)

    return moment.isoformat(timespec="seconds").replace("+00:00", "Z")
```

Так мы получаем строку вида `2026-07-04T18:20:10Z`. Буква `Z` означает UTC.

### Запись о файле

Теперь соберем один файл в [словарь](../../field-guide/dict/):

```python
def build_record(root: Path, path: Path) -> dict[str, object]:
    stat = path.stat()

    return {
        "path": relative_name(root, path),
        "size": stat.st_size,
        "sha256": file_sha256(path),
        "modified_at": utc_timestamp(stat.st_mtime),
    }
```

`stat.st_size` - размер в байтах. `stat.st_mtime` - время последнего изменения в секундах.

### Сканирование и дубли

Сначала получим [список](../../field-guide/list/) записей:

```python
def scan_folder(root: Path) -> list[dict[str, object]]:
    root = root.resolve()
    return [build_record(root, path) for path in iter_files(root)]
```

Для дублей сгруппируем пути по хэшу. `detect_duplicates()` не читает файлы повторно: она работает только с готовыми записями, поэтому ее легко проверить отдельно.

```python
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
```

Одинаковое имя файла не обязательно означает одинаковое содержимое. Одинаковый SHA-256 в учебном архиве - сильный сигнал, что это настоящая копия.

### Манифест

Манифест - обычный словарь, который потом легко записать в JSON:

```python
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
```

`JSON` хорош для такого проекта: его можно открыть глазами, отправить другому человеку, сравнить в системе контроля версий или загрузить другой программой.

### Чтение и запись JSON

Добавим две функции. `load_manifest()` возвращает либо старый снимок, либо `None`, поэтому первый запуск не считается ошибкой; `write_manifest()` отвечает только за сохранение текущего снимка.

```python
def load_manifest(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None

    return json.loads(path.read_text(encoding="utf-8"))


def write_manifest(manifest: dict[str, object], path: Path) -> None:
    text = json.dumps(manifest, ensure_ascii=False, indent=2)
    path.write_text(text + "\n", encoding="utf-8")
```

`ensure_ascii=False` сохраняет русские символы нормальным текстом, а не `\u041f\u0440...`.

### Сравнение снимков

Чтобы найти изменения, превратим список файлов в словарь `путь -> запись`:

```python
def index_by_path(manifest: dict[str, object]) -> dict[str, dict[str, object]]:
    return {
        str(record["path"]): record
        for record in manifest.get("files", [])
        if isinstance(record, dict)
    }
```

Теперь сравним старый и новый манифесты:

```python
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
```

Мы считаем файл измененным только по хэшу. Если дата поменялась, но байты те же, содержимое не изменилось. Поэтому сравнение manifest-файлов опирается на `sha256`, а `modified_at` остается вспомогательной подсказкой для человека.

### Отчет

[Rich](../../field-guide/rich/) нужен только для вывода:

```python
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
```

Для дублей можно сделать отдельную таблицу:

```python
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
```

### Финальный запуск

В `main()` свяжем все шаги:

```python
def main() -> None:
    previous = load_manifest(MANIFEST_PATH)
    current = build_manifest(DATA_DIR)
    changes = compare_manifests(previous or {"files": []}, current)

    render_report(current, changes, previous is not None)
    render_duplicates(current)
    write_manifest(current, MANIFEST_PATH)
    console.print(f"[bold green]Манифест сохранен:[/bold green] {MANIFEST_PATH}")
```

Теперь скрипт не просто смотрит на папку. Он оставляет снимок, с которым можно сравнить следующий запуск.

## Проверка

Запустите:

```bash
python secret_folder_archive.py
```

В первом запуске программа должна найти 6 файлов, заметить одну группу дублей и сохранить `manifest.json`.

Откройте любой файл в `data/secret_folder/notes/`, добавьте строку и запустите скрипт еще раз. В таблице `Изменения` у вас должен появиться один измененный файл. Потом можно удалить созданный `manifest.json` и начать проверку заново.

Сравните форму вывода с `check_result.txt`. Числа хэшей и timestamps у вас могут отличаться, а структура отчета должна совпадать.

## Что мы использовали

- [Современный Python](../../field-guide/modern-python/) - Python 3.14+, виртуальная среда и точная версия зависимости.
- [pathlib.Path](../../field-guide/pathlib/) - пути, рекурсивный обход и относительные имена.
- [hashlib.sha256()](../../field-guide/hashlib/) - надежный отпечаток содержимого файла.
- [JSON](../../field-guide/json/) - человекочитаемый манифест.
- [Исключения](../../field-guide/exceptions/) - явные ошибки для отсутствующей или неправильной папки.
- `datetime.now(timezone.utc)` и `datetime.fromtimestamp(..., tz=timezone.utc)` - timestamps без привязки к локальному часовому поясу.
- [Словари `dict`](../../field-guide/dict/) - записи файлов, манифест и отчет об изменениях.
- [Списки `list`](../../field-guide/list/) - упорядоченные файлы и группы дублей.
- [Rich](../../field-guide/rich/) - таблицы summary, изменений и дублей.

## Усложняем проект

1. Добавьте список игнорируемых шаблонов: например, не индексировать `.DS_Store` и временные файлы редакторов.
2. Сделайте аргументы командной строки для папки и пути к манифесту.
3. Сохраняйте историю снимков в папку `manifests/`, а не перезаписывайте один файл.
4. Добавьте проверку переименований: если хэш уже был, но путь изменился, показывайте это отдельно.
5. Экспортируйте короткий отчет в `report.txt`.

Когда закончите, откройте [разбор полного решения](../secret-folder-archive-solution/).
