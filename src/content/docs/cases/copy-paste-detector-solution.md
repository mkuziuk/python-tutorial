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

Обращайтесь к этой странице после самостоятельной сборки `copy_paste_detector.py`. Если открыть её раньше, задача сведётся к переписыванию готового ответа.

## Полный код

```python
from itertools import combinations
from pathlib import Path

from rich.console import Console
from rich.table import Table


def default_data_dir():
    # resolve() убирает неоднозначность относительного пути при запуске из другой папки.
    script_dir = Path(__file__).resolve().parent
    local_data = script_dir / "data"
    # После копирования рядом будет data; в solution/ она находится уровнем выше.
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
    "report_alarm_stand": "Отчёт учебного стенда",
    "report_guard_note": "Отчёт охраны",
}


def read_text(path):
    # Явная UTF-8 кодировка сохраняет одинаковое чтение русского текста на разных системах.
    return path.read_text(encoding="utf-8")


def normalize_words(text):
    cleaned = []

    # Заменяем разделители пробелами, чтобы слова по обе стороны знака не склеились.
    for char in text.lower():
        # isalpha() принимает буквы разных алфавитов; для этого набора это осознанная граница нормализации.
        if char.isalpha():
            cleaned.append(char)
        else:
            cleaned.append(" ")

    return "".join(cleaned).split()


def make_ngrams(words, size=NGRAM_SIZE):
    # Проверяем параметр сразу, чтобы отрицательный диапазон не выглядел как корректный пустой результат.
    if size < 1:
        raise ValueError("N-gram size must be positive")

    # Последнее окно начинается в len(words) - size; +1 включает эту позицию.
    return [
        tuple(words[index : index + size])
        for index in range(len(words) - size + 1)
    ]


def display_name(path):
    # Неизвестный stem всё равно получает читаемую подпись, поэтому новый файл не требует правки словаря.
    return DISPLAY_NAMES.get(path.stem, path.stem.replace("_", " ").title())


def build_profile(path, ngram_size=NGRAM_SIZE):
    text = read_text(path)
    words = normalize_words(text)
    # Множество считает повторяющуюся n-грамму одним фрагментом, а не несколькими уликами.
    ngrams = set(make_ngrams(words, ngram_size))

    return {
        "path": path,
        "title": display_name(path),
        "word_count": len(words),
        # Это число уникальных фрагментов: повтор одной фразы внутри отчёта не увеличивает счётчик.
        "ngram_count": len(ngrams),
        "ngrams": ngrams,
    }


def overlap_score(left, right):
    # Пустая сторона не даёт свидетельства сходства и защищает формулу от деления на ноль.
    if not left or not right:
        return 0.0

    # Пересечение множеств оставляет только фрагменты, которые встретились в обоих отчётах.
    shared = left & right
    if not shared:
        return 0.0

    # Первая доля ищет вложение в меньший текст, вторая штрафует лишние n-граммы.
    # shared не может быть больше меньшего множества, поэтому containment всегда лежит в диапазоне 0–1.
    containment = len(shared) / min(len(left), len(right))
    # Jaccard симметрично штрафует лишние фрагменты в обоих текстах.
    jaccard = len(shared) / len(left | right)
    # Округляем опубликованную оценку; при равенстве рейтинг дополнительно смотрит на число совпадений.
    return round(containment * 0.7 + jaccard * 0.3, 3)


def compare_profiles(left, right):
    # Сравнение получает готовые профили и больше не читает файлы с диска.
    left_ngrams = left["ngrams"]
    right_ngrams = right["ngrams"]
    # Сортировка делает примеры воспроизводимыми при любом порядке элементов множества.
    shared_ngrams = sorted(left_ngrams & right_ngrams)

    # Результат пары хранит и числовую оценку, и данные для объяснения этой оценки в таблице.
    return {
        "pair": (str(left["title"]), str(right["title"])),
        "score": overlap_score(left_ngrams, right_ngrams),
        "shared_count": len(shared_ngrams),
        # Это первые примеры в стабильном порядке, а не «самые сильные» совпадения.
        "examples": shared_ngrams[:TOP_EXAMPLES],
    }


def load_profiles(data_dir=DATA_DIR, ngram_size=NGRAM_SIZE):
    # Маска задаёт границу входа: посторонние txt-файлы в каталоге в расследование не попадут.
    paths = sorted(data_dir.glob("report_*.txt"))
    if not paths:
        raise FileNotFoundError(f"No report_*.txt files found in {data_dir}")

    return [build_profile(path, ngram_size) for path in paths]


def rank_overlaps(data_dir=DATA_DIR, ngram_size=NGRAM_SIZE):
    # Каждый файл нормализуем один раз, а затем переиспользуем профиль во всех попарных сравнениях.
    profiles = load_profiles(data_dir, ngram_size)
    results = []

    # combinations(..., 2) выдаёт каждую пару один раз и не сравнивает файл с собой.
    for left, right in combinations(profiles, 2):
        result = compare_profiles(left, right)
        # Нулевые совпадения не засоряют отчёт; отсутствующая пара означает нулевой общий след.
        if int(result["shared_count"]) > 0:
            results.append(result)

    return sorted(
        results,
        # Кортеж задаёт два ключа: сначала балл, затем число совпадений.
        key=lambda item: (float(item["score"]), int(item["shared_count"])),
        reverse=True,
    )


def format_ngram(ngram):
    # Внутри алгоритма порядок хранит кортеж, а пользователю показываем обычную строку.
    return " ".join(ngram)


def render_results(results, limit=5):
    table = Table(title="Подозрительные совпадения")
    table.add_column("Место", justify="right", style="cyan")
    table.add_column("Пара")
    table.add_column("Оценка", justify="right")
    table.add_column("Общих n-грамм", justify="right")
    table.add_column("Пример")

    # limit ограничивает только таблицу; полный рейтинг в results остаётся доступен вызывающему коду.
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

    # Пустой рейтинг допустим: например, если ни одна пара не имеет общей n-граммы.
    if results:
        best = results[0]
        left, right = best["pair"]
        console.print(
            f"\n[bold]Главная версия:[/bold] {left} и {right} "
            f"имеют самый сильный общий след: [cyan]{float(best['score']):.3f}[/cyan]."
        )


def main():
    # Вывод получает уже отсортированный рейтинг и не меняет результаты анализа.
    render_results(rank_overlaps())


if __name__ == "__main__":
    main()
```

## Как читать решение

Данные проходят несколько этапов: каждый файл становится списком слов, список превращается в n-граммы, а n-граммы — во множество. Затем каждая пара профилей получает оценку, и результаты сортируются для отчёта.

Главное решение — сравнивать не отдельные слова, а соседние группы слов. Так общая тема создаёт меньше шума, а повторяющиеся фразы получают более высокую оценку.

Частые ошибки: вернуть списки вместо кортежей, забыть проверку `size < 1`, сортировать пары только по числу общих n-грамм или печатать все совпадения вместо короткого примера.

Справочник: [list](../../field-guide/list/), [tuple](../../field-guide/tuple/), [set](../../field-guide/set/), [dict](../../field-guide/dict/), [sorting](../../field-guide/sorting/), [functions](../../field-guide/functions/), [Rich](../../field-guide/rich/).

## Что важно заметить

Формула `overlap_score()` объединяет два сигнала. `containment` помогает заметить короткий повторяющийся отчёт внутри длинного текста, а `jaccard` снижает оценку, если у пары много различающихся n-грамм.

Rich используется только в `render_results()`. Чтение файлов, нормализация, n-граммы, множества и сортировка остаются на стандартной библиотеке.
