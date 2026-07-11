---
title: "Разбор полного решения"
description: "Полный код второго дела: n-граммы, множества и рейтинг подозрительных текстовых совпадений."
concepts:
  - tuple
  - n-grams
  - set
  - dict
  - sorting
  - functions
difficulty: "начальный+"
projectId: "case-02"
time: "15-20 минут"
---

Эта страница нужна после того, как вы уже собрали `copy_paste_detector.py` по главе. Если открыть ее раньше, интрига дела исчезнет слишком быстро.

## Полный код

```python
from itertools import combinations
from pathlib import Path

from rich.console import Console
from rich.table import Table


def default_data_dir():
    script_dir = Path(__file__).resolve().parent
    local_data = script_dir / "data"
    if local_data.exists():
        return local_data
    return script_dir.parent / "data"


DATA_DIR = default_data_dir()
NGRAM_SIZE = 4
TOP_EXAMPLES = 3

console = Console()

DISPLAY_NAMES = {
    "report_north_table": "Опись Северного стола",
    "report_tour_draft": "Черновик экскурсии",
    "report_basement_route": "Служебный маршрут подвального коридора",
    "report_alarm_stand": "Отчет учебного стенда",
    "report_guard_note": "Отчет охраны",
}


def read_text(path):
    return path.read_text(encoding="utf-8")


def normalize_words(text):
    cleaned = []

    for char in text.lower():
        if char.isalpha():
            cleaned.append(char)
        else:
            cleaned.append(" ")

    return "".join(cleaned).split()


def make_ngrams(words, size=NGRAM_SIZE):
    if size < 1:
        raise ValueError("N-gram size must be positive")

    return [
        tuple(words[index : index + size])
        for index in range(len(words) - size + 1)
    ]


def display_name(path):
    return DISPLAY_NAMES.get(path.stem, path.stem.replace("_", " ").title())


def build_profile(path, ngram_size=NGRAM_SIZE):
    text = read_text(path)
    words = normalize_words(text)
    ngrams = set(make_ngrams(words, ngram_size))

    return {
        "path": path,
        "title": display_name(path),
        "word_count": len(words),
        "ngram_count": len(ngrams),
        "ngrams": ngrams,
    }


def overlap_score(left, right):
    if not left or not right:
        return 0.0

    shared = left & right
    if not shared:
        return 0.0

    containment = len(shared) / min(len(left), len(right))
    jaccard = len(shared) / len(left | right)
    return round(containment * 0.7 + jaccard * 0.3, 3)


def compare_profiles(left, right):
    left_ngrams = left["ngrams"]
    right_ngrams = right["ngrams"]
    shared_ngrams = sorted(left_ngrams & right_ngrams)

    return {
        "pair": (str(left["title"]), str(right["title"])),
        "score": overlap_score(left_ngrams, right_ngrams),
        "shared_count": len(shared_ngrams),
        "examples": shared_ngrams[:TOP_EXAMPLES],
    }


def load_profiles(data_dir=DATA_DIR, ngram_size=NGRAM_SIZE):
    paths = sorted(data_dir.glob("report_*.txt"))
    if not paths:
        raise FileNotFoundError(f"No report_*.txt files found in {data_dir}")

    return [build_profile(path, ngram_size) for path in paths]


def rank_overlaps(data_dir=DATA_DIR, ngram_size=NGRAM_SIZE):
    profiles = load_profiles(data_dir, ngram_size)
    results = []

    for left, right in combinations(profiles, 2):
        result = compare_profiles(left, right)
        if int(result["shared_count"]) > 0:
            results.append(result)

    return sorted(
        results,
        key=lambda item: (float(item["score"]), int(item["shared_count"])),
        reverse=True,
    )


def format_ngram(ngram):
    return " ".join(ngram)


def render_results(results, limit=5):
    table = Table(title="Подозрительные совпадения")
    table.add_column("Место", justify="right", style="cyan")
    table.add_column("Пара")
    table.add_column("Оценка", justify="right")
    table.add_column("Общих n-грамм", justify="right")
    table.add_column("Пример")

    for position, result in enumerate(results[:limit], start=1):
        left, right = result["pair"]
        examples = result["examples"]
        example = format_ngram(examples[0]) if examples else "нет общих n-грамм"

        table.add_row(
            str(position),
            f"{left} / {right}",
            f"{float(result['score']):.3f}",
            str(result["shared_count"]),
            example,
        )

    console.print(table)

    if results:
        best = results[0]
        left, right = best["pair"]
        console.print(
            f"\n[bold]Главная версия:[/bold] {left} и {right} "
            f"имеют самый сильный общий след: [cyan]{float(best['score']):.3f}[/cyan]."
        )


def main():
    render_results(rank_overlaps())


if __name__ == "__main__":
    main()
```

## Как читать решение

Поток данных такой: каждый файл становится списком слов, список превращается в n-граммы, n-граммы складываются во множество, затем каждая пара профилей получает оценку и сортируется для отчета.

Главное решение - сравнивать не одиночные слова, а соседние группы слов. Это снижает шум от общей темы и поднимает наверх реальные повторяющиеся фразы.

Частые ошибки: вернуть списки вместо кортежей, забыть проверку `size < 1`, сортировать пары только по числу общих n-грамм или печатать все совпадения вместо короткого примера.

Справочник: [list](../../field-guide/list/), [tuple](../../field-guide/tuple/), [set](../../field-guide/set/), [dict](../../field-guide/dict/), [sorting](../../field-guide/sorting/), [functions](../../field-guide/functions/), [Rich](../../field-guide/rich/).

## Что важно заметить

Формула `overlap_score()` совмещает два сигнала. `containment` помогает заметить короткий повторяющийся отчет внутри длинного текста, а `jaccard` снижает оценку, если у пары много разных n-грамм.

Rich используется только в `render_results()`. Чтение файлов, нормализация, n-граммы, множества и сортировка остаются на стандартной библиотеке.
