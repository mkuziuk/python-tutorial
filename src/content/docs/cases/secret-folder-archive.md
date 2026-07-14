---
title: "Расследование 04. Ночной сигнал архива"
description: "Проверяем происхождение отчётов, считаем SHA-256 файлов и фиксируем расхождение двух хронологий."
concepts:
  - pathlib
  - hashlib
  - JSON
  - difflib
  - происхождение данных
difficulty: "средний"
projectId: "case-04"
time: "90-120 минут"
---

<div class="case-meta">
  <p><strong>Миссия</strong> зафиксировать отчёты I-01–I-03 и ночную папку так, чтобы следующий скрипт мог проверить каждый источник.</p>
  <p><strong>Инструменты</strong> `pathlib`, чтение блоками, `hashlib.sha256`, относительные пути, `difflib`, JSON.</p>
  <p><strong>Вход</strong> три предыдущих JSON-отчёта и `data/secret_folder/`.</p>
  <p><strong>Результат</strong> `artifacts/04-evidence-index.json`.</p>
</div>

<div class="materials-panel">
  <p><strong>Быстрые ссылки:</strong> <a href="../../downloads/case-04.zip">case-04.zip</a> · <a href="../secret-folder-archive-solution/">разбор решения</a></p>
  <p><strong>Справочник:</strong> <a href="../../field-guide/pathlib/">pathlib</a> · <a href="../../field-guide/hashlib/">hashlib</a> · <a href="../../field-guide/json/">JSON</a></p>
</div>

## Зачем нужен отдельный индекс

Предыдущие программы уже нашли кандидата, совпадающие тексты и рискованные письма. Теперь важно сохранить связь между выводом и исходным файлом. Если отчёт или источник изменится, его SHA-256 тоже изменится.

В отличие от прежней версии упражнения, вам не нужно вручную редактировать файл и запускать программу второй раз. Главная задача — собрать один проверяемый снимок всех материалов.

## Структура входных данных

```text
data/
  artifacts/
    01-authorship.json
    02-text-matches.json
    03-mail-review.json
  secret_folder/
    drafts/
    evidence/
    notes/
```

## Шаг 1. Найти файлы

```python
def iter_files(root):
    if not root.exists():
        raise FileNotFoundError(f"Folder not found: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Expected a folder: {root}")
    return sorted(path for path in root.rglob("*") if path.is_file())
```

В JSON сохраняйте путь относительно `data/`, а не абсолютный путь на вашем компьютере.

## Шаг 2. Посчитать SHA-256

```python
def file_sha256(path, chunk_size=65_536):
    digest = hashlib.sha256()
    with path.open("rb") as file:
        while chunk := file.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()
```

Файл читается блоками, поэтому объём памяти не зависит от размера файла. Одинаковый SHA-256 означает, что учебные файлы совпадают байт в байт.

## Шаг 3. Проверить отчёты I-01–I-03

Для каждого отчёта загрузите JSON, проверьте `investigation_id` и сохраните:

```python
{
    "investigation_id": artifact["investigation_id"],
    "path": f"artifacts/{path.name}",
    "sha256": file_sha256(path),
    "finding_ids": [item["finding_id"] for item in artifact["findings"]],
}
```

Так I-05 сможет проверить, что получил именно те отчёты, которые были зафиксированы здесь.

## Шаг 4. Найти дубли

Сгруппируйте записи по хэшу:

```python
by_hash.setdefault(record["sha256"], []).append(record["path"])
```

В учебной папке `photo_index.txt` и `photo_index_copy.txt` должны попасть в одну группу.

## Шаг 5. Сравнить хронологии

```python
for line in ndiff(current_lines, backup_lines):
    if line.startswith("- "):
        differences["current"].append(line[2:])
    elif line.startswith("+ "):
        differences["backup"].append(line[2:])
```

Результат должен явно сохранить направление различия:

- рабочая версия содержит строку `22:53`;
- резервная версия содержит строку `23:07`.

## Шаг 6. Сохранить индекс

`build_evidence_index()` объединяет:

- три проверенных входных отчёта;
- SHA-256 шести файлов ночной папки;
- группу дублей;
- различия хронологий;
- четыре события из журнала доступа.

Запустите:

```bash
python secret_folder_archive.py
python -m json.tool artifacts/04-evidence-index.json
python -m unittest discover -s tests
```

Следующее расследование загрузит этот индекс и проверит хэши отчётов перед созданием объектов.

## Что мы использовали

- `Path.rglob()` для рекурсивного обхода;
- относительные пути для переносимого отчёта;
- SHA-256 для проверки содержимого;
- `ndiff()` для двух сохранённых версий;
- JSON для передачи результата I-05.

## Усложняем проект

1. Добавьте размер и MIME-тип каждого файла.
2. Подпишите индекс отдельным ключом и проверьте подпись перед I-05.
3. Добавьте список файлов, которые разрешено включать в архив.
