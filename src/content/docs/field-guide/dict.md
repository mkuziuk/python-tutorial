---
title: "dict: профиль и индекс"
description: "Словари в Python: связываем имена признаков со значениями."
concept: "dict"
usedIn:
  - "case-01"
  - "case-02"
  - "case-04"
  - "case-05"
  - "case-06"
order: 3
---

## Что это

`dict` хранит пары `ключ -> значение`. В деле словарь часто становится профилем: один ключ отвечает за имя автора, другой за число слов, третий за пунктуацию.

## Когда использовать

Используйте словарь, когда нужно быстро получить значение по имени.

```python
profile = {
    "name": "Алина Морозова",
    "word_count": 138,
}
print(profile["name"])
```

## Мини-пример

```python
counts = {}
for word in ["след", "пауза", "след"]:
    counts[word] = counts.get(word, 0) + 1
print(counts)
```

## Ещё примеры

`.get()` позволяет указать значение по умолчанию, если ключа нет:

```python
record = {"file": "note.txt", "status": "checked"}

owner = record.get("owner", "неизвестен")
print(owner)
```

Через `.items()` удобно одновременно читать ключи и значения. `setdefault()` помогает собрать несколько значений под одним ключом:

```python
files = [("txt", "note.txt"), ("json", "data.json"), ("txt", "log.txt")]
by_extension = {}

for extension, filename in files:
    by_extension.setdefault(extension, []).append(filename)

for extension, names in by_extension.items():
    print(extension, names)
```

## Типичные ловушки

- Обращение к отсутствующему ключу вызывает `KeyError`.
- `.get()` скрывает различие между отсутствующим ключом и ключом со значением `None`; иногда нужна явная проверка `if key in record`.
- Ключ должен быть хешируемым: строка подходит, список - нет.
- Словарь хранит связь, но не объясняет ее смысл сам по себе. Называйте ключи ясно.

## Где встречается в делах

- [Дело 01. Кто оставил предупреждение?](../../cases/anonymous-letter/) - профиль текста как словарь признаков.
- [Дело 02. Детектор текстовых совпадений](../../cases/copy-paste-detector/) - индекс отчётов и счетчики совпадений.
- [Дело 04. Ночной сигнал архива](../../cases/secret-folder-archive/) - записи файлов, manifest и отчёт об изменениях.
- [Дело 05. Доска расследования](../../cases/investigation-system/) - подготовка JSON-представления объектов.
