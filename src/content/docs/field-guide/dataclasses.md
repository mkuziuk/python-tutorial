---
title: "dataclasses: компактные классы данных"
description: "dataclass для объектов, которые в основном хранят понятные поля."
concept: "dataclasses"
usedIn:
  - "case-03"
  - "case-05"
  - "case-06"
order: 15
---

## Что это

`@dataclass` создает для класса служебный код: `__init__`, удобное представление и сравнение по полям.

## Когда использовать

Используйте dataclass для объектов данных: ссылки, сигналы риска, улики, записи дела и результаты анализа.

```python
from dataclasses import dataclass

@dataclass
class Evidence:
    title: str
    source: str
```

## Мини-пример

```python
evidence = Evidence(title="Письмо", source="anonymous.txt")
print(evidence.title)
```

## Типичные ловушки

- Для изменяемого значения по умолчанию используйте `field(default_factory=list)`.
- Dataclass не заменяет валидацию: он создает форму объекта, но не проверяет смысл каждого поля.
- Если у класса много поведения и мало данных, обычный класс может быть яснее.

## Где встречается в делах

- [Дело 03. Фишинговое письмо или нет?](../../cases/phishing-email/) - `LinkInfo`, `RiskSignal` и `EmailReport` как явные формы результата.
- [Дело 05. Доска расследования](../../cases/investigation-system/) - `Evidence`, `Person`, `CaseNote` и `Investigation` как объекты предметной области.
