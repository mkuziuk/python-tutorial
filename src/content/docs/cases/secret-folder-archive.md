---
title: "Дело 04. Ночной сигнал архива"
description: "Собираем индексатор папки после ночного сигнала: SHA-256, JSON-манифест, поиск изменений и difflib для двух хронологий."
concepts:
  - pathlib
  - обход файлов
  - hashlib
  - JSON
  - временные метки
  - поиск изменений
  - difflib
  - Rich
  - ветвления и циклы
  - работа с файлами
  - datetime
  - unittest
difficulty: "средний"
projectId: "case-04"
time: "100-130 минут"
---

<div class="case-meta">
  <p><strong>Миссия</strong> проверить рабочую папку после ночного сигнала: что внутри, какие файлы совпадают и почему расходятся две хронологии.</p>
  <p><strong>Инструменты</strong> `pathlib`, рекурсивный обход файлов, `hashlib`, `difflib`, JSON, UTC-время, сравнение снимков.</p>
  <p><strong>Результат</strong> консольный индексатор, который пишет `manifest.json`, показывает изменения и выводит строки расхождения хронологий.</p>
  <p><strong>Маршрут</strong> средний · 100–130 минут · Python 3.13+</p>
</div>

<div class="materials-panel">
  <p><strong>Быстрые ссылки:</strong> <a href="../../downloads/case-04.zip">case-04.zip</a> · <a href="../../materials/">материалы всех дел</a> · <a href="../secret-folder-archive-solution/">разбор решения</a></p>
  <p><strong>Справочник:</strong> <a href="../../field-guide/control-flow/">условия и циклы</a> · <a href="../../field-guide/file-io/">файлы</a> · <a href="../../field-guide/pathlib/">pathlib</a> · <a href="../../field-guide/hashlib/">hashlib</a> · <a href="../../field-guide/datetime/">дата и время</a> · <a href="../../field-guide/json/">JSON</a> · <a href="../../field-guide/exceptions/">exceptions</a> · <a href="../../field-guide/dict/">dict</a> · <a href="../../field-guide/list/">list</a> · <a href="../../field-guide/functions/">functions</a> · <a href="../../field-guide/rich/">Rich</a> · <a href="../../field-guide/testing/">unittest</a></p>
</div>

## Проблема

После текстов и писем расследование упирается в рабочую папку команды: `secret_folder`. Ночью система архива отметила короткое открытие комнаты хранения, а утром в папке лежат фотоиндекс витрины «Северный стол», его копия, заметки, журнал доступа и две версии хронологии. На глаз все выглядит почти спокойно, но похожие имена ничего не доказывают: файл могли скопировать, переименовать или сохранить заново.

Вопрос дела: как сделать опись рабочей папки так, чтобы завтра проверить дубли и изменения, не полагаясь на память и догадки?

Обычная дата изменения помогает, но ей нельзя полностью доверять. Файл можно скопировать, переименовать или сохранить заново. Поэтому мы будем считать криптографический хэш SHA-256 через [`hashlib`](../../field-guide/hashlib/) и сохранять манифест в формате [JSON](../../field-guide/json/).

Хэш здесь можно представить как цифровой отпечаток файла. Одинаковое содержимое даёт одинаковый отпечаток, а крошечная правка — даже один лишний пробел — делает отпечаток другим. Поэтому если два файла имеют одинаковый SHA-256, их содержимое практически наверняка совпадает байт в байт.

В сюжете `secret_folder` — это рабочая папка архивной команды. [case-04.zip](../../downloads/case-04.zip) — учебный набор для этой главы; вместо загрузки архива можно открыть папку `projects/case-04/` в репозитории.

Внутри учебного набора:

- `secret_folder_archive.py` — пустой стартовый файл;
- `requirements.txt` — зависимость для удобного вывода в терминале;
- `data/secret_folder/` — папка с заметками, журналом, копиями и хронологией;
- `check_result.txt` — форма результата для самопроверки.

Полное решение вынесено отдельно: [Разбор полного решения](../secret-folder-archive-solution/).

### Подготовка окружения

Нужен Python 3.13 или новее. Перед началом проверьте `py -3 --version` на Windows или `python3 --version` на macOS и Linux.

Windows PowerShell:

```powershell
cd path\to\case-04
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

macOS или Linux:

```bash
cd path/to/case-04
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Запустите стартовый файл:

```bash
python secret_folder_archive.py
```

Пока программа ничего не выводит: это нормально. Дальше мы добавим обход папки, хэши, манифест и отчёт.

## Стратегия

Мы построим программу как маленький конвейер:

1. Найти все обычные файлы внутри `data/secret_folder/`.
2. Для каждого файла собрать запись: путь, размер, SHA-256, время изменения.
3. Сложить записи в манифест.
4. Найти группы дублей по одинаковому SHA-256.
5. Если старый `manifest.json` уже есть, сравнить его с новым снимком.
6. Сравнить рабочую и резервную хронологии построчно.
7. Показать отчёт и сохранить свежий манифест.

Запись одного файла будет выглядеть так:

```python
{
    # path — переносимое имя внутри архива, а не абсолютный путь на компьютере автора.
    "path": "evidence/photo_index.txt",
    # size хранится в байтах; sha256 описывает именно содержимое файла.
    "size": 172,
    "sha256": "8d4c...",
    "modified_at": "2026-03-14T19:20:10Z",
}
```

Мы храним путь относительно секретной папки. Так манифест можно перенести на другой компьютер: в нем не будет абсолютного пути вроде `/Users/...`.

## Сборка инструмента

Откройте `secret_folder_archive.py`. Вверху нам нужны стандартные модули и две сущности из Rich:

```python
from datetime import datetime, timezone
from difflib import ndiff
import hashlib
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

# Сканируем только secret_folder; manifest.json лежит рядом со скриптом и не индексирует сам себя.
DATA_DIR = Path(__file__).with_name("data") / "secret_folder"
MANIFEST_PATH = Path(__file__).with_name("manifest.json")
# Обе версии хронологии входят в снимок, но дополнительно сравниваются построчно ниже.
TIMELINE_PATH = DATA_DIR / "drafts" / "timeline.txt"
TIMELINE_BACKUP_PATH = DATA_DIR / "drafts" / "timeline_backup.txt"
console = Console()
```

`Path(__file__).with_name("data")` привязывает путь к папке проекта, а не к тому месту, откуда вы запустили команду. Это важная привычка для учебных и реальных скриптов.

### Обход папки

[`pathlib`](../../field-guide/pathlib/) умеет рекурсивно проходить по дереву:

```python
def iter_files(root):
    if not root.exists():
        raise FileNotFoundError(f"Folder not found: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Expected a folder: {root}")

    # rglob("*") рекурсивно проходит и вложенные каталоги.
    # Каталоги не индексируем, а сортировка делает порядок записей воспроизводимым.
    return sorted(path for path in root.rglob("*") if path.is_file())
```

`root.rglob("*")` находит все вложенные пути. Мы оставляем только файлы: у папок нет содержимого, которое можно хэшировать как обычный документ. Если папка отсутствует или вместо неё передан файл, функция явно выбрасывает исключение, чтобы ошибка была заметна сразу.

### Относительный путь

Манифест должен быть читаемым:

```python
def relative_name(root, path):
    # В манифест пишем переносимый относительный путь, а не адрес конкретного компьютера.
    return path.relative_to(root).as_posix()
```

`relative_to()` убирает начало пути, а `as_posix()` записывает разделители через `/`. Так JSON будет одинаково выглядеть на Windows, macOS и Linux.

### Хэш файла

Файл лучше читать кусками. Маленькие файлы можно прочитать целиком, но привычка с чанками спасает, когда архив разрастается. `file_sha256()` принимает путь и возвращает строку-хэш; именно эта строка потом решает, одинаковые ли файлы.

```python
# Читаем файл блоками по 65 536 байт.
def file_sha256(path, chunk_size=65_536):
    digest = hashlib.sha256()

    # Чтение частями ограничивает расход памяти независимо от размера файла.
    with path.open("rb") as file:
        # Оператор := сохраняет блок и сразу проверяет, не закончился ли файл.
        while chunk := file.read(chunk_size):
            digest.update(chunk)

    return digest.hexdigest()
```

Мы открываем файл в режиме `rb`, потому что хэш считается по байтам, а не по строкам.

### Время в UTC

Для манифеста нужна предсказуемая запись времени. Не используем локальный часовой пояс: сегодня скрипт запускают в Москве, завтра на сервере в другой стране.

```python
# seconds, если передан, — Unix-время в секундах; результат всегда возвращается в UTC.
def utc_timestamp(seconds=None):
    # Явно используем UTC, чтобы время не зависело от часового пояса компьютера.
    # None означает время самого сканирования; для файла передаём его st_mtime.
    if seconds is None:
        moment = datetime.now(timezone.utc)
    else:
        moment = datetime.fromtimestamp(seconds, tz=timezone.utc)

    return moment.isoformat(timespec="seconds").replace("+00:00", "Z")
```

Так мы получаем строку вида `2026-03-14T19:20:10Z`. Буква `Z` означает UTC.

### Запись о файле

Теперь соберём сведения об одном файле в [словарь](../../field-guide/dict/):

```python
def build_record(root, path):
    # stat() читаем один раз, чтобы размер и время относились к одному наблюдению файла.
    stat = path.stat()

    # Хэш описывает содержимое, размер — байты, а modified_at — метаданные файловой системы.
    return {
        "path": relative_name(root, path),
        "size": stat.st_size,
        "sha256": file_sha256(path),
        # mtime помогает аудиту, но изменение содержимого ниже определяется по SHA-256.
        "modified_at": utc_timestamp(stat.st_mtime),
    }
```

`stat.st_size` — размер в байтах, а `stat.st_mtime` — время последнего изменения в секундах.

### Сканирование и дубли

Сначала получим [список](../../field-guide/list/) записей:

```python
def scan_folder(root):
    # Абсолютный root нужен только во время обхода; наружу всё равно выйдут относительные пути.
    root = root.resolve()
    return [build_record(root, path) for path in iter_files(root)]
```

Для поиска дублей сгруппируем пути по хэшу. `detect_duplicates()` не читает файлы повторно: она работает только с готовыми записями, поэтому её легко проверить отдельно.

```python
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
```

Одинаковое имя файла не гарантирует одинакового содержимого. Совпадающий SHA-256 в архиве дела — сильный признак того, что перед нами настоящая копия.

### Манифест

Манифест — обычный словарь, который затем легко записать в JSON:

```python
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
```

`JSON` хорош для такого проекта: его можно открыть глазами, отправить другому человеку, сравнить в системе контроля версий или загрузить другой программой.

### Чтение и запись JSON

Добавим две функции. `load_manifest()` возвращает либо старый снимок, либо `None`, поэтому первый запуск не считается ошибкой; `write_manifest()` отвечает только за сохранение текущего снимка.

```python
def load_manifest(path):
    # При первом запуске load_manifest() возвращает None.
    if not path.exists():
        return None

    # Синтаксическая ошибка JSON не маскируется под первый запуск и должна остановить аудит.
    return json.loads(path.read_text(encoding="utf-8"))


def write_manifest(manifest, path):
    # Читаемый JSON облегчает ручной аудит и сравнение версий в системе контроля версий.
    text = json.dumps(manifest, ensure_ascii=False, indent=2)
    path.write_text(text + "\n", encoding="utf-8")
```

`ensure_ascii=False` сохраняет русские символы нормальным текстом, а не `\u041f\u0440...`.

### Сравнение снимков

Чтобы найти изменения, превратим список файлов в словарь `путь -> запись`:

```python
def index_by_path(manifest):
    # index_by_path() строит словарь «путь → запись» из раздела files.
    return {
        str(record["path"]): record
        for record in manifest.get("files", [])
        if isinstance(record, dict)
    }
```

Теперь сравним старый и новый манифесты:

```python
def compare_manifests(
    previous,
    current,
):
    old_files = index_by_path(previous)
    new_files = index_by_path(current)
    # Файлы сопоставляем по относительному пути, поэтому переименование считается удалением и добавлением.
    old_paths = set(old_files)
    new_paths = set(new_files)

    # Пересечение — общие пути; разности множеств — добавленные и удалённые.
    changed = []
    for path in sorted(old_paths & new_paths):
        # В changed попадают пути, у которых изменился SHA-256.
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
```

Файл считается изменённым только при изменении хэша. Если дата поменялась, но байты остались прежними, содержимое не изменилось. Поэтому сравнение манифестов опирается на `sha256`, а `modified_at` остаётся вспомогательной подсказкой для человека.

### Сравнение двух хронологий

Манифест отвечает на вопрос «одинаковы ли файлы?», но не показывает, какие строки различаются. Для двух текстовых версий используем [`difflib.ndiff()`](https://docs.python.org/3/library/difflib.html#difflib.ndiff) из стандартной библиотеки. Строки с префиксом `- ` есть только в рабочей версии, с `+ ` - только в резервной; служебные подсказки `? ` нам не нужны.

```python
def compare_timeline_versions(current_path, backup_path):
    # splitlines() преобразует каждую версию в список строк для ndiff().
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
```

Мы сохраняем направление различий, чтобы в отчёте было видно, из какой версии взята каждая строка. В учебных файлах функция должна найти рабочую запись `22:53` и резервную запись `23:07`.

### Отчёт

[Rich](../../field-guide/rich/) нужен только для вывода:

```python
def render_report(
    manifest,
    changes,
    had_previous_manifest,
):
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
```

Для дублей можно сделать отдельную таблицу:

```python
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
```

Отдельная таблица делает расхождение хронологий частью основного результата дела:

```python
def render_timeline_difference(differences):
    table = Table(title="Расхождение хронологий")
    table.add_column("Версия")
    table.add_column("Строка только в этой версии")

    for line in differences["current"]:
        table.add_row("Рабочая", line)
    for line in differences["backup"]:
        table.add_row("Резервная", line)

    console.print(table)
```

### Финальный запуск

В `main()` свяжем все шаги:

```python
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

Теперь скрипт не просто смотрит на папку. Он оставляет снимок, с которым можно сравнить следующий запуск.

## Проверка

Запустите:

```bash
python secret_folder_archive.py
```

После отчёта запустите тесты из учебного набора:

```bash
python -m unittest discover -s tests
```

В первом запуске программа должна найти 6 файлов, заметить одну группу дублей, показать расхождение хронологий `22:53` / `23:07` и сохранить `manifest.json`.

Откройте любой файл в `data/secret_folder/notes/`, добавьте строку и запустите скрипт ещё раз. В таблице «Изменения» должен появиться один изменённый файл. Затем можно удалить созданный `manifest.json` и начать проверку заново.

Сравните форму вывода с `check_result.txt`. Хэши и временные метки могут отличаться, но структура отчёта должна совпадать.

## Что мы использовали

- [Установка Python](../../field-guide/install-python/) — Python 3.13+, виртуальная среда и точная версия зависимости.
- [pathlib.Path](../../field-guide/pathlib/) — пути, рекурсивный обход и относительные имена.
- [hashlib.sha256()](../../field-guide/hashlib/) — надёжный отпечаток содержимого файла.
- `difflib.ndiff()` — построчная разница рабочей и резервной хронологий.
- [JSON](../../field-guide/json/) — человекочитаемый манифест.
- [Исключения](../../field-guide/exceptions/) — явные ошибки для отсутствующей или неправильной папки.
- `datetime.now(timezone.utc)` и `datetime.fromtimestamp(..., tz=timezone.utc)` — временные метки без привязки к локальному часовому поясу.
- [Словари `dict`](../../field-guide/dict/) — записи файлов, манифест и отчёт об изменениях.
- [Списки `list`](../../field-guide/list/) — упорядоченные файлы и группы дублей.
- [Rich](../../field-guide/rich/) — сводка, изменения и дубли в отдельных таблицах.

## Усложняем проект

1. Добавьте список игнорируемых шаблонов: например, не индексировать `.DS_Store` и временные файлы редакторов.
2. Сделайте аргументы командной строки для папки и пути к манифесту.
3. Сохраняйте историю снимков в папку `manifests/`, а не перезаписывайте один файл.
4. Добавьте проверку переименований: если хэш уже был, но путь изменился, показывайте это отдельно.
5. Экспортируйте короткий отчёт в `report.txt`.

Когда закончите, откройте [разбор полного решения](../secret-folder-archive-solution/).
