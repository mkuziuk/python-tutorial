---
title: "Разбор решения: Детектор текстовых совпадений"
description: "Рейтинг n-грамм и 02-text-matches.json."
---

Эта страница показывает полную версию программы после выполнения упражнения. Сначала завершите самостоятельную версию и запустите тесты.

Решение сохраняет результат в JSON для следующего расследования. Поэтому важно проверять не только таблицу в терминале, но и структуру созданного файла.

```python
from itertools import combinations
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table


def default_data_dir():
    script_dir = Path(__file__).resolve().parent
    local_data = script_dir / "data"
    # После копирования рядом будет data; в solution/ она находится уровнем выше.
    if local_data.exists():
        return local_data
    return script_dir.parent / "data"


DATA_DIR = default_data_dir()
PROJECT_DIR = DATA_DIR.parent
AUTHORSHIP_PATH = DATA_DIR / "artifacts" / "01-authorship.json"
ARTIFACT_PATH = PROJECT_DIR / "artifacts" / "02-text-matches.json"
NGRAM_SIZE = 4
TOP_EXAMPLES = 3

console = Console()

DISPLAY_NAMES = {
    "anonymous": "Анонимное предупреждение",
    "report_north_table": "Опись Северного стола",
    "report_tour_draft": "Черновик экскурсии",
    "report_basement_route": "Служебный маршрут подвального коридора",
    "report_alarm_stand": "Отчёт учебного стенда",
    "report_guard_note": "Отчёт охраны",
}


def read_text(path):
    return path.read_text(encoding="utf-8")


def normalize_words(text):
    cleaned = []

    # Заменяем разделители пробелами, чтобы слова по обе стороны знака не склеились.
    for char in text.lower():
        if char.isalpha():
            cleaned.append(char)
        else:
            cleaned.append(" ")

    return "".join(cleaned).split()


def make_ngrams(words, size=NGRAM_SIZE):
    if size < 1:
        raise ValueError("N-gram size must be positive")

    # Последнее окно начинается в len(words) - size; +1 включает эту позицию.
    return [
        tuple(words[index : index + size])
        for index in range(len(words) - size + 1)
    ]


def display_name(path):
    return DISPLAY_NAMES.get(path.stem, path.stem.replace("_", " ").title())


def build_profile(path, ngram_size=NGRAM_SIZE):
    text = read_text(path)
    words = normalize_words(text)
    # set хранит каждую уникальную n-грамму один раз.
    ngrams = set(make_ngrams(words, ngram_size))

    return {
        "path": path,
        "title": display_name(path),
        "word_count": len(words),
        "ngram_count": len(ngrams),
        "ngrams": ngrams,
    }


def overlap_score(left, right):
    # При пустом множестве сходство равно 0.
    if not left or not right:
        return 0.0

    shared = left & right
    if not shared:
        return 0.0

    # containment измеряет долю n-грамм меньшего текста, найденных в другом тексте.
    # Jaccard снижает оценку, если в текстах много несовпадающих n-грамм.
    containment = len(shared) / min(len(left), len(right))
    jaccard = len(shared) / len(left | right)
    return round(containment * 0.7 + jaccard * 0.3, 3)


def compare_profiles(left, right):
    left_ngrams = left["ngrams"]
    right_ngrams = right["ngrams"]
    # Сортировка делает примеры воспроизводимыми при любом порядке элементов множества.
    shared_ngrams = sorted(left_ngrams & right_ngrams)

    return {
        "pair": (str(left["title"]), str(right["title"])),
        "score": overlap_score(left_ngrams, right_ngrams),
        "shared_count": len(shared_ngrams),
        # examples содержит первые TOP_EXAMPLES n-грамм после сортировки.
        "examples": shared_ngrams[:TOP_EXAMPLES],
    }


def load_profiles(data_dir=DATA_DIR, ngram_size=NGRAM_SIZE):
    paths = sorted(data_dir.glob("report_*.txt"))
    anonymous_path = data_dir / "anonymous.txt"
    if anonymous_path.exists():
        paths.append(anonymous_path)
    if not paths:
        raise FileNotFoundError(f"No report_*.txt files found in {data_dir}")

    return [build_profile(path, ngram_size) for path in paths]


def rank_overlaps(data_dir=DATA_DIR, ngram_size=NGRAM_SIZE):
    profiles = load_profiles(data_dir, ngram_size)
    results = []

    # combinations(profiles, 2) создаёт каждую неупорядоченную пару один раз.
    for left, right in combinations(profiles, 2):
        result = compare_profiles(left, right)
        # Пары без общих n-грамм не добавляем в отчёт.
        if int(result["shared_count"]) > 0:
            results.append(result)

    return sorted(
        results,
        # Кортеж задаёт два ключа: сначала балл, затем число совпадений.
        key=lambda item: (float(item["score"]), int(item["shared_count"])),
        reverse=True,
    )


def format_ngram(ngram):
    return " ".join(ngram)


def load_authorship_lead(path=AUTHORSHIP_PATH):
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("investigation_id") != "I-01":
        raise ValueError(f"Expected I-01 artifact: {path}")
    finding = data["findings"][0]
    return {
        "finding_id": finding["finding_id"],
        "candidate": finding["candidates"][0]["name"],
        "score": finding["candidates"][0]["score"],
        "limitation": finding["limitation"],
    }


def build_artifact(results, authorship_path=AUTHORSHIP_PATH):
    matches = []
    for position, result in enumerate(results, start=1):
        matches.append(
            {
                "rank": position,
                "pair": list(result["pair"]),
                "score": result["score"],
                "shared_count": result["shared_count"],
                "examples": [format_ngram(item) for item in result["examples"]],
            }
        )
    return {
        "schema_version": 1,
        "investigation_id": "I-02",
        "generated_at": "2026-03-15T06:50:00+03:00",
        "source_files": [
            "anonymous.txt",
            *[path.name for path in sorted(DATA_DIR.glob("report_*.txt"))],
            "artifacts/01-authorship.json",
        ],
        "inputs": {"authorship_lead": load_authorship_lead(authorship_path)},
        "findings": [
            {
                "finding_id": "F-I02-TEXT-MATCHES",
                "kind": "text-overlap-ranking",
                "title": "Совпадения n-грамм в материалах архива",
                "summary": (
                    f"Самая сильная пара: {' / '.join(matches[0]['pair'])}."
                    if matches
                    else "Совпадений n-грамм не найдено."
                ),
                "matches": matches,
            }
        ],
    }


def save_artifact(artifact, path=ARTIFACT_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


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
    results = rank_overlaps()
    render_results(results)
    save_artifact(build_artifact(results))
    console.print(f"[green]Отчёт сохранён:[/green] {ARTIFACT_PATH.name}")


if __name__ == "__main__":
    main()
```

## Проверка

Из папки проекта выполните:

```bash
python -m unittest discover -s tests
```

Все переходы I-01 → I-06 дополнительно проверяет команда сопровождающего `pnpm test:part1-artifacts`.
