---
title: "Разбор полного решения"
description: "Полный код первого дела и короткий разбор после самостоятельной сборки инструмента."
concepts:
  - str
  - list
  - dict
  - set
  - regex
  - Counter
  - Rich
difficulty: "начальный+"
projectId: "case-01"
time: "15-20 минут"
---

Эта страница нужна после того, как вы уже собрали `anonymous_letter.py` по главе. Если открыть ее раньше, дело потеряет половину смысла.

## Полный код

```python
from collections import Counter
from pathlib import Path
import re

from rich.console import Console
from rich.table import Table

DATA_DIR = Path(__file__).with_name("data")
WORD_RE = re.compile(r"[а-яё]+", re.IGNORECASE)
PUNCTUATION = ".,;:!?"
console = Console()

AUTHOR_NAMES = {
    "author_morozova": "Алина Морозова",
    "author_sokolov": "Илья Соколов",
    "author_korolev": "Никита Королев",
}


def normalize_words(text):
    return WORD_RE.findall(text.lower())


def punctuation_profile(text):
    return Counter(char for char in text if char in PUNCTUATION)


def build_profile(name, text):
    words = normalize_words(text)
    if not words:
        raise ValueError(f"Text for {name!r} does not contain Russian words")

    total_letters = sum(len(word) for word in words)
    return {
        "name": name,
        "word_count": len(words),
        "unique_words": len(set(words)),
        "average_word_length": total_letters / len(words),
        "common_words": Counter(words).most_common(12),
        "punctuation": punctuation_profile(text),
    }


def jaccard(left, right):
    if not left and not right:
        return 1.0
    return len(left & right) / len(left | right)


def punctuation_similarity(left, right):
    left_total = sum(left.values()) or 1
    right_total = sum(right.values()) or 1
    distance = 0.0

    for mark in PUNCTUATION:
        distance += abs((left[mark] / left_total) - (right[mark] / right_total))

    return max(0.0, 1.0 - distance / 2)


def compare_profiles(anonymous, candidate):
    anonymous_words = {word for word, _ in anonymous["common_words"]}
    candidate_words = {word for word, _ in candidate["common_words"]}
    word_overlap = jaccard(anonymous_words, candidate_words)

    average_delta = abs(
        float(anonymous["average_word_length"]) - float(candidate["average_word_length"])
    )
    length_score = max(0.0, 1.0 - average_delta / 3)

    punctuation_score = punctuation_similarity(
        anonymous["punctuation"],
        candidate["punctuation"],
    )

    return round(word_overlap * 0.45 + length_score * 0.25 + punctuation_score * 0.30, 3)


def display_name(path):
    return AUTHOR_NAMES.get(path.stem, path.stem.replace("_", " ").title())


def read_text(path):
    return path.read_text(encoding="utf-8")


def rank_candidates(data_dir=DATA_DIR):
    anonymous = build_profile("Анонимное письмо", read_text(data_dir / "anonymous.txt"))
    results = []

    for path in sorted(data_dir.glob("author_*.txt")):
        profile = build_profile(display_name(path), read_text(path))
        results.append((str(profile["name"]), compare_profiles(anonymous, profile)))

    return sorted(results, key=lambda item: item[1], reverse=True)


def render_results(results):
    table = Table(title="Вероятные авторы")
    table.add_column("Место", justify="right", style="cyan")
    table.add_column("Кандидат")
    table.add_column("Сходство", justify="right")

    for position, (name, score) in enumerate(results, start=1):
        table.add_row(str(position), name, f"{score:.2f}")

    console.print(table)
    winner, score = results[0]
    console.print(
        f"\n[bold]Главная версия:[/bold] {winner} "
        f"([cyan]{score:.2f}[/cyan]). Это повод проверить текст вручную, а не окончательный приговор."
    )


def main():
    render_results(rank_candidates())


if __name__ == "__main__":
    main()
```

## Как читать решение

Поток данных такой: файлы превращаются в строки, `normalize_words()` делает список слов, `build_profile()` собирает словарь признаков, `compare_profiles()` выдает оценку, а `render_results()` только печатает таблицу.

Главное решение - держать анализ и вывод отдельно. Если результат неверный, сначала проверяйте профиль и формулу, а не Rich-таблицу.

Частые ошибки: забыть `ё` в regex, сравнивать все слова вместо частых слов, делить пунктуацию на ноль или считать итоговую оценку без округления.

Справочник: [str](../../field-guide/str/), [regex](../../field-guide/regex/), [list](../../field-guide/list/), [dict](../../field-guide/dict/), [set](../../field-guide/set/), [Counter](../../field-guide/counter/), [functions](../../field-guide/functions/), [Rich](../../field-guide/rich/).

## Что важно заметить

`Rich` подключен только в двух местах: `Console` печатает, `Table` рисует таблицу. Анализ текста остается на стандартной библиотеке Python.

`WORD_RE.findall(text.lower())` возвращает список слов, а не итератор совпадений. Для первого проекта это проще читать, чем `finditer()`.

`compare_profiles()` не пытается быть научной моделью. Это прозрачная эвристика: пересечение популярных слов, близость средней длины слова и похожесть пунктуации.
