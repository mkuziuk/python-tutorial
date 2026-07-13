---
title: "Counter: быстрый счетчик"
description: "collections.Counter для частот слов, n-грамм и других повторяющихся признаков."
concept: "Counter"
usedIn:
  - "case-01"
order: 6
---

## Что это

`Counter` из модуля `collections` - словарь, который умеет считать элементы.

## Когда использовать

Используйте `Counter`, когда нужно быстро понять, что повторяется чаще: слова, символы, расширения файлов или n-граммы.

```python
from collections import Counter

words = ["след", "архив", "след"]
print(Counter(words))
```

## Мини-пример

```python
from collections import Counter

letters = Counter("расследование")
print(letters.most_common(3))
```

## Ещё примеры

Счётчик можно пополнять частями — удобно при чтении нескольких файлов:

```python
from collections import Counter

word_counts = Counter()
word_counts.update(["архив", "ночь", "архив"])
word_counts.update(["след", "ночь"])

for word, count in word_counts.most_common():
    print(word, count)
```

Частоту иногда полезнее выразить долей от общего числа наблюдений:

```python
total = word_counts.total()
night_share = word_counts["ночь"] / total if total else 0
print(f"доля слова 'ночь': {night_share:.1%}")
```

## Типичные ловушки

- `Counter` считает точные значения: `"След"` и `"след"` разные строки.
- Обращение к отсутствующему элементу возвращает `0`, а не вызывает `KeyError`.
- `most_common()` сортирует по частоте, но равные частоты могут идти в порядке первого появления.
- Для долей и процентов все равно нужно делить на общее количество элементов.

## Где встречается в делах

- [Дело 01. Кто оставил предупреждение?](../../cases/anonymous-letter/) - частоты слов и знаков.
