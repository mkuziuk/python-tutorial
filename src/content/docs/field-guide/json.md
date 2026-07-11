---
title: "JSON: переносимые данные"
description: "json для manifest-файлов, настроек и сохранения состояния."
concept: "json"
usedIn:
  - "case-04"
  - "case-05"
  - "case-06"
order: 13
---

## Что это

JSON - текстовый формат данных. В Python с ним работает модуль `json`: словари становятся объектами, списки - массивами, строки и числа сохраняются напрямую.

## Когда использовать

Используйте JSON для manifest-файлов, маленьких баз данных проекта, настроек и обмена данными между программами.

```python
import json

payload = {"case_id": "case-05", "open": True}
text = json.dumps(payload, ensure_ascii=False, indent=2)
```

## Мини-пример

```python
import json
from pathlib import Path

path = Path("case.json")
path.write_text(json.dumps({"title": "Архив"}, ensure_ascii=False), encoding="utf-8")
data = json.loads(path.read_text(encoding="utf-8"))
```

## Типичные ловушки

- JSON не хранит Python-объекты сам по себе. Классы нужно превращать в словари.
- Ключи JSON всегда строки.
- Для русских текстов обычно ставят `ensure_ascii=False`, чтобы файл оставался читаемым.

## Где встречается в делах

- [Дело 04. Ночной сигнал архива](../../cases/secret-folder-archive/) - manifest архива.
- [Дело 05. Доска расследования](../../cases/investigation-system/) - сохранение дел и улик.
