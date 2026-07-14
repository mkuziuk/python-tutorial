---
title: "pathlib: пути как объекты"
description: "Path для файлов, папок, обхода дерева и переносимого кода."
concept: "pathlib"
usedIn:
  - "case-04"
  - "case-05"
  - "case-06"
order: 11
---

## Что это

`pathlib.Path` представляет путь к файлу или папке как объект с понятными методами.

## Когда использовать

Используйте `Path`, когда программа читает файлы, создаёт папки, ищет данные или должна работать на Windows, macOS и Linux.

```python
from pathlib import Path

data_dir = Path("data")
for path in data_dir.rglob("*"):
    print(path)
```

## Мини-пример

```python
from pathlib import Path

report = Path("out") / "manifest.json"
report.parent.mkdir(exist_ok=True)
report.write_text("{}", encoding="utf-8")
```

## Ещё примеры

Ищите только файлы нужного типа и отделяйте имя, расширение и размер:

```python
from pathlib import Path

for path in Path("data").rglob("*.txt"):
    if path.is_file():
        print(path.name, path.suffix, path.stat().st_size)
```

Путь можно сделать относительным к корню расследования, чтобы отчёт не зависел от имени домашней папки:

```python
root = Path("data")
path = root / "archive" / "timeline.txt"

print(path.relative_to(root))  # archive/timeline.txt
```

## Типичные ловушки

- `Path("data")` зависит от текущей рабочей папки. Для файлов рядом со скриптом используйте `Path(__file__).parent`.
- `relative_to()` работает только когда путь действительно лежит внутри указанного корня.
- `rglob("*")` находит и файлы, и папки. Проверяйте `path.is_file()`.
- Не склеивайте пути вручную через строки, используйте оператор `/`.

## Где встречается в расследованиях

- [Расследование 04. Последнее доказательство](../../cases/final-evidence/) - строим пути к входным JSON и сохраняем итоговый отчёт.
