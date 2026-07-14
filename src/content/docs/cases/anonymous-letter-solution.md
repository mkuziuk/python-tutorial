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

Обращайтесь к этой странице после самостоятельной сборки `anonymous_letter.py`. Если открыть её раньше, значительная часть учебной задачи потеряет смысл.

## Полный код

```python
from collections import Counter
from pathlib import Path
import re

from rich.console import Console
from rich.table import Table

DATA_DIR = Path(__file__).with_name("data")
# Шаблон выделяет только цепочки русских букв, включая «ё».
WORD_RE = re.compile(r"[а-яё]+", re.IGNORECASE)
PUNCTUATION = ".,;:!?"
console = Console()

AUTHOR_NAMES = {
    "author_morozova": "Алина Морозова",
    "author_sokolov": "Илья Соколов",
    "author_korolev": "Никита Королев",
}


def normalize_words(text):
    # Список сохраняет повторы: они нужны и для частот, и для средней длины слов.
    return WORD_RE.findall(text.lower())


def punctuation_profile(text):
    # Counter получает только нужные знаки и сам подсчитывает их частоты.
    # Считаем абсолютные количества здесь; к долям перейдём только при сравнении профилей.
    return Counter(char for char in text if char in PUNCTUATION)


def build_profile(name, text):
    words = normalize_words(text)
    # Останавливаемся до деления: у пустого текста нельзя определить среднюю длину слова.
    if not words:
        raise ValueError(f"Text for {name!r} does not contain Russian words")

    # Длину измеряем в буквах, поэтому пробелы и знаки препинания в среднее не попадают.
    total_letters = sum(len(word) for word in words)
    # Берём 12 самых частых слов, чтобы единичная редкая лексика не влияла сильнее устойчивых привычек.
    return {
        "name": name,
        "word_count": len(words),
        "unique_words": len(set(words)),
        "average_word_length": total_letters / len(words),
        "common_words": Counter(words).most_common(12),
        "punctuation": punctuation_profile(text),
    }


def jaccard(left, right):
    # Если признака нет в обоих текстах, считаем отсутствие полным совпадением, а не ошибкой.
    if not left and not right:
        return 1.0
    # «&» даёт общие слова, а «|» — все слова из обоих множеств.
    return len(left & right) / len(left | right)


def punctuation_similarity(left, right):
    # Единица защищает от деления на ноль, а / 2 приводит результат к диапазону 0–1.
    # Нормируем на объём каждого текста, чтобы длинный текст не получал преимущество автоматически.
    left_total = sum(left.values()) or 1
    right_total = sum(right.values()) or 1
    distance = 0.0

    # Перебираем фиксированный алфавит знаков, поэтому отсутствующий знак Counter вернёт как ноль.
    for mark in PUNCTUATION:
        distance += abs((left[mark] / left_total) - (right[mark] / right_total))

    return max(0.0, 1.0 - distance / 2)


def compare_profiles(anonymous, candidate):
    # В формулу входит состав частых слов; количества использовались только при отборе двенадцати.
    anonymous_words = {word for word, _ in anonymous["common_words"]}
    candidate_words = {word for word, _ in candidate["common_words"]}
    word_overlap = jaccard(anonymous_words, candidate_words)

    # average_delta измеряется в буквах на слово и сравнивает одинаково определённые признаки.
    average_delta = abs(
        float(anonymous["average_word_length"]) - float(candidate["average_word_length"])
    )
    # Если средняя длина слова отличается на три буквы или больше, length_score равен 0.
    length_score = max(0.0, 1.0 - average_delta / 3)

    punctuation_score = punctuation_similarity(
        anonymous["punctuation"],
        candidate["punctuation"],
    )

    # Итоговая оценка — взвешенная сумма word_overlap, length_score и punctuation_score.
    return round(word_overlap * 0.45 + length_score * 0.25 + punctuation_score * 0.30, 3)


def display_name(path):
    # Словарь даёт читабельные имена, а запасной вариант позволяет добавить новый файл без правки кода.
    return AUTHOR_NAMES.get(path.stem, path.stem.replace("_", " ").title())


def read_text(path):
    # Явная UTF-8 кодировка делает чтение одинаковым на Windows, macOS и Linux.
    return path.read_text(encoding="utf-8")


def rank_candidates(data_dir=DATA_DIR):
    # Профиль анонимного текста строим один раз и используем при сравнении со всеми авторами.
    anonymous = build_profile("Анонимное письмо", read_text(data_dir / "anonymous.txt"))
    results = []

    # glob("author_*.txt") выбирает образцы авторов, а sorted() фиксирует их порядок.
    for path in sorted(data_dir.glob("author_*.txt")):
        profile = build_profile(display_name(path), read_text(path))
        # После сравнения полные профили больше не нужны, поэтому сохраняем только имя и итоговый балл.
        results.append((str(profile["name"]), compare_profiles(anonymous, profile)))

    # sorted() стабилен: при равных баллах сохранится зафиксированный выше порядок файлов.
    return sorted(results, key=lambda item: item[1], reverse=True)


def render_results(results):
    # Отрисовка отделена от расчёта: тесты проверяют результаты без захвата терминала.
    table = Table(title="Вероятные авторы")
    table.add_column("Место", justify="right", style="cyan")
    table.add_column("Кандидат")
    table.add_column("Сходство", justify="right")

    # Нумерация начинается с единицы, потому что это место в пользовательском рейтинге.
    for position, (name, score) in enumerate(results, start=1):
        table.add_row(str(position), name, f"{score:.2f}")

    console.print(table)
    # results[0] требует непустой рейтинг кандидатов.
    winner, score = results[0]
    console.print(
        f"\n[bold]Главная версия:[/bold] {winner} "
        f"([cyan]{score:.2f}[/cyan]). Это повод проверить текст вручную, а не окончательный приговор."
    )


def main():
    # main связывает расчёт и вывод, не пряча дополнительную обработку между ними.
    render_results(rank_candidates())


if __name__ == "__main__":
    main()
```

## Как читать решение

Данные проходят несколько этапов: файлы превращаются в строки, `normalize_words()` составляет список слов, `build_profile()` собирает словарь признаков, `compare_profiles()` вычисляет оценку, а `render_results()` только печатает таблицу.

Главное решение — отделить анализ от вывода. Если результат неверен, сначала проверяйте профиль и формулу, а не таблицу Rich.

Частые ошибки: забыть `ё` в regex, сравнивать все слова вместо частых слов, делить пунктуацию на ноль или считать итоговую оценку без округления.

Справочник: [str](../../field-guide/str/), [regex](../../field-guide/regex/), [list](../../field-guide/list/), [dict](../../field-guide/dict/), [set](../../field-guide/set/), [Counter](../../field-guide/counter/), [functions](../../field-guide/functions/), [Rich](../../field-guide/rich/).

## Что важно заметить

`Rich` подключён только в двух местах: `Console` печатает, а `Table` строит таблицу. Анализ текста остаётся на стандартной библиотеке Python.

`WORD_RE.findall(text.lower())` возвращает список слов, а не итератор совпадений. Для первого проекта это проще читать, чем `finditer()`.

`compare_profiles()` не пытается быть научной моделью. Это прозрачная эвристика: пересечение популярных слов, близость средней длины слова и похожесть пунктуации. Итоговая оценка показывает сходство этих признаков, но не является вероятностью авторства.
