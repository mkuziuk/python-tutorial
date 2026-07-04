---
title: "pathlib: пути как объекты"
description: "Path для файлов, папок, обхода дерева и переносимого кода."
concept: "pathlib"
usedIn:
  - "case-04"
  - "case-05"
order: 11
---

## Что это

`pathlib.Path` представляет путь к файлу или папке как объект с понятными методами.

## Когда использовать

Используйте `Path`, когда программа читает файлы, создает папки, ищет данные или должна работать на Windows, macOS и Linux.

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

## Типичные ловушки

- `Path("data")` зависит от текущей рабочей папки. Для файлов рядом со скриптом используйте `Path(__file__).parent`.
- `rglob("*")` находит и файлы, и папки. Проверяйте `path.is_file()`.
- Не склеивайте пути вручную через строки, используйте оператор `/`.

## Где встречается в делах

- [Дело 04. Архивариус секретной папки](../../cases/secret-folder-archive/) - обходим папку и пишем manifest.
- [Дело 05. Система расследований](../../cases/investigation-system/) - сохраняем базу дел в JSON.
