---
title: "dataclasses: компактные классы данных"
description: "dataclass для объектов, которые в основном хранят понятные поля."
concept: "dataclasses"
usedIn:
  - "case-05"
  - "case-06"
order: 15
---

## Что это

`@dataclass` создаёт для класса служебный код: `__init__`, удобное представление и сравнение по полям.

## Когда использовать

Используйте dataclass для объектов данных: улики, люди, гипотезы, связи и результаты анализа.

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

```text
Письмо
```

Объект хранит две строки с именованными полями; вывод проверяет чтение поля
`title`. Если поле содержит изменяемый контейнер, его значение по умолчанию
нужно создавать отдельно для каждого объекта.

## Изменяемые значения и `default_factory`

Список нельзя безопасно поставить обычным значением по умолчанию: один объект мог бы разделить его с другим. `default_factory` вызывает `list` отдельно для каждого нового объекта:

```python
from dataclasses import dataclass, field


@dataclass(slots=True)
class Evidence:
    title: str
    tags: list[str] = field(default_factory=list)


first = Evidence("Письмо")
second = Evidence("Фото")
first.tags.append("текст")
print(first.tags, second.tags)
```

`slots=True` фиксирует объявленный набор полей и не позволяет случайно создать новое поле опечаткой.

```text
['текст'] []
```

Пустой список у `second` подтверждает инвариант: экземпляры не разделяют
`tags`. Теперь можно добавить проверку значений, которая действует на каждый
создаваемый объект.

## Валидация после создания

`__post_init__()` автоматически запускается после созданного dataclass-конструктора:

```python
@dataclass
class Evidence:
    title: str
    reliability: int

    def __post_init__(self):
        if not 1 <= self.reliability <= 5:
            raise ValueError("Надёжность должна быть от 1 до 5")


try:
    Evidence("Письмо", 7)
except ValueError as error:
    print(error)
```

```text
Надёжность должна быть от 1 до 5
```

Границы `1..5` — инвариант модели: неверный объект не попадает в остальную
программу. Следующая задача — применить этот же конструктор к внешнему словарю,
где типы и наличие ключей ещё не гарантированы.

## Фабрика из словаря

Ниже предполагается класс `Evidence` из предыдущего примера. Метод
`from_dict()` удобно держит преобразование JSON рядом с моделью:

```python
@classmethod
def from_dict(cls, data: dict[str, object]):
    return cls(
        title=str(data["title"]),
        reliability=int(data.get("reliability", 3)),
    )


Evidence.from_dict = from_dict
item = Evidence.from_dict({"title": "Письмо", "reliability": "4"})
print(item)
```

```text
Evidence(title='Письмо', reliability=4)
```

Ключ `title` обязателен: при его отсутствии возникает `KeyError`. Для
`reliability` выбран нейтральный учебный default `3`, а `int()` принимает
строковое число и отклоняет прочие значения через `ValueError`. `cls(...)`
создаёт правильный тип и для возможного подкласса. После проверки границы
внешних данных модель можно сделать неизменяемой.

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


assessment = Assessment(support_points=5, conflict_points=2)
print(assessment.score)
```

`@property` позволяет читать вычисляемое значение как `assessment.score`, хотя оно считается методом и не хранится отдельным полем.

```text
3
```

Результат подтверждает, что `score` вычисляется из двух сохранённых целых
чисел; отдельного поля, которое могло бы рассинхронизироваться, нет.

## Типичные ловушки

- Для изменяемого значения по умолчанию используйте `field(default_factory=list)`.
- Dataclass не заменяет валидацию: он создаёт форму объекта, но не проверяет смысл каждого поля.
- `frozen=True` запрещает обычное присваивание полям, но не превращает вложенный изменяемый список в кортеж автоматически.
- `slots=True` не является проверкой типов: строка останется строкой, даже если поле аннотировано как `int`.
- Если у класса много поведения и мало данных, обычный класс может быть яснее.

## Где встречается в расследованиях

- [Расследование 03. Фишинговое письмо или нет?](../../cases/phishing-email/) — компактная структура результата разбора письма.
