---
title: "Rich: читаемый терминальный отчет"
description: "Rich в этих проектах отвечает только за вывод, а не за логику расследования."
concept: "Rich"
usedIn:
  - "case-01"
  - "case-02"
  - "case-03"
  - "case-04"
  - "case-05"
order: 16
---

## Что это

Rich - библиотека для красивого вывода в терминал. В учебнике она закреплена как `rich==15.0.0`.

## Когда использовать

Используйте Rich, когда отчет должен быть читаемым: таблица результатов, список предупреждений, компактная сводка.

```python
from rich.console import Console
from rich.table import Table

console = Console()
table = Table(title="Отчет")
table.add_column("Признак")
table.add_column("Значение")
table.add_row("риск", "низкий")
console.print(table)
```

## Мини-пример

```python
from rich.console import Console

console = Console()
console.print("[bold cyan]Готово[/bold cyan]")
```

## Типичные ловушки

- Не смешивайте форматирование с логикой. Сначала посчитайте результат обычным Python, потом выведите таблицу.
- Версию библиотеки фиксируйте в `requirements.txt`.
- Для учебника не нужны сложные возможности Rich: достаточно `Console` и `Table`.

## Где встречается в делах

- Все дела первой арки используют Rich только для финального отчета.
