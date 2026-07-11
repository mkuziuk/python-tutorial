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

## Изменяемые значения и `default_factory`

Список нельзя безопасно поставить обычным значением по умолчанию: один объект мог бы разделить его с другим. `default_factory` вызывает `list` отдельно для каждого нового объекта:

```python
from dataclasses import dataclass, field


@dataclass(slots=True)
class Evidence:
    title: str
    tags: list[str] = field(default_factory=list)
```

`slots=True` фиксирует объявленный набор полей и не позволяет случайно создать новое поле опечаткой.

## Валидация после создания

`__post_init__()` автоматически запускается после созданного dataclass-конструктора:

```python
@dataclass
class Evidence:
    title: str
    reliability: int

    def __post_init__(self):
        if not 1 <= self.reliability <= 5:
            raise ValueError("Надежность должна быть от 1 до 5")
```

Так неверный объект не успевает попасть в остальную программу.

## Фабрика из словаря

`@classmethod` получает сам класс в параметре `cls`. Метод `from_dict()` удобно держит преобразование JSON рядом с моделью:

```python
@classmethod
def from_dict(cls, data):
    return cls(
        title=str(data["title"]),
        reliability=int(data.get("reliability", 3)),
    )
```

Вызов `Evidence.from_dict(data)` создает `Evidence`; использование `cls(...)` сохраняет правильное поведение и для возможного подкласса.

## Неизменяемые факты и вычисляемые свойства

`frozen=True` запрещает присваивать полям новые значения после создания. Это полезно для загруженных фактов: вместо скрытой правки создайте новый объект.

```python
@dataclass(frozen=True, slots=True)
class Assessment:
    support_points: int
    conflict_points: int

    @property
    def score(self):
        return self.support_points - self.conflict_points
```

`@property` позволяет читать вычисляемое значение как `assessment.score`, хотя оно считается методом и не хранится отдельным полем.

## Типичные ловушки

- Для изменяемого значения по умолчанию используйте `field(default_factory=list)`.
- Dataclass не заменяет валидацию: он создает форму объекта, но не проверяет смысл каждого поля.
- `frozen=True` запрещает обычное присваивание полям, но не превращает вложенный изменяемый список в кортеж автоматически.
- `slots=True` не является проверкой типов: строка останется строкой, даже если поле аннотировано как `int`.
- Если у класса много поведения и мало данных, обычный класс может быть яснее.

## Где встречается в делах

- [Дело 03. Фишинговое письмо или нет?](../../cases/phishing-email/) - `LinkInfo`, `RiskSignal` и `EmailReport` как явные формы результата.
- [Дело 05. Доска расследования](../../cases/investigation-system/) - `Evidence`, `Person`, `CaseNote` и `Investigation` как объекты предметной области.
- [Дело 06. Вердикт перед открытием](../../cases/final-verdict/) - неизменяемые факты, фабрики `from_dict()` и вычисляемый балл гипотезы.
