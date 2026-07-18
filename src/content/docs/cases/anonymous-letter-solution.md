---
title: "Разбор решения: Кто оставил предупреждение?"
description: "Рейтинг авторов и 01-authorship.json."
---

Эта страница показывает полную версию программы после выполнения упражнения. Сначала завершите самостоятельную версию и сверьте её результат с главой.

Решение сохраняет результат в JSON для следующего шага арки. Поэтому важно проверять не только вывод в терминале, но и структуру созданного файла.

```python
"""Эталон I-01: построить и сравнить простые стилометрические профили."""

from collections import Counter
import json
from pathlib import Path
import re

# Эталон лежит в solution/, поэтому parents[1] возвращает папку case-01.
PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
ARTIFACT_PATH = PROJECT_DIR / "artifacts" / "01-authorship.json"
# Шаблон выделяет только цепочки русских букв, включая «ё».
WORD_RE = re.compile(r"[а-яё]+", re.IGNORECASE)
# Закрытый набор задаёт границу признака: кавычки, тире и скобки в профиль не входят.
PUNCTUATION = ".,;:!?"

# Словарь связывает основу имени каждого входного файла с подписью в отчёте.
AUTHOR_NAMES = {
    "author_morozova": "Алина Морозова",
    "author_sokolov": "Илья Соколов",
    "author_korolev": "Никита Королев",
}


def normalize_words(text):
    """Вернуть русские слова в нижнем регистре, сохранив их повторы."""
    # Список сохраняет повторы: они нужны и для частот, и для средней длины слов.
    return WORD_RE.findall(text.lower())


def punctuation_profile(text):
    """Посчитать шесть выбранных знаков препинания."""
    # Counter получает только нужные знаки и сам подсчитывает их частоты.
    return Counter(char for char in text if char in PUNCTUATION)


def build_profile(name, text):
    """Собрать имя и пять измеримых признаков текста в одном словаре."""
    words = normalize_words(text)
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
    """Измерить отношение пересечения множеств к их объединению."""
    if not left and not right:
        return 1.0
    # «&» даёт общие слова, а «|» — все слова из обоих множеств.
    return len(left & right) / len(left | right)


def punctuation_similarity(left, right):
    """Сравнить доли знаков препинания и вернуть сходство от 0 до 1."""
    # Единица защищает от деления на ноль, а / 2 приводит результат к диапазону 0–1.
    left_total = sum(left.values()) or 1
    right_total = sum(right.values()) or 1
    # distance накапливает L1-расстояние: сумму модулей разностей долей каждого знака.
    distance = 0.0

    # Фиксированный набор знаков делает формы обоих профилей одинаковыми;
    # для отсутствующего знака Counter возвращает ноль.
    for mark in PUNCTUATION:
        distance += abs((left[mark] / left_total) - (right[mark] / right_total))

    return max(0.0, 1.0 - distance / 2)


def compare_profiles(anonymous, candidate):
    """Смешать три признака профилей в один воспроизводимый балл."""
    # Каждый элемент common_words — пара (слово, количество);
    # _ показывает, что количество здесь не используется.
    anonymous_words = {word for word, _ in anonymous["common_words"]}
    candidate_words = {word for word, _ in candidate["common_words"]}
    word_overlap = jaccard(anonymous_words, candidate_words)

    # average_delta измеряет абсолютную разницу средних длин в буквах на слово.
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
    """Преобразовать техническое имя файла в подпись для читателя."""
    return AUTHOR_NAMES.get(path.stem, path.stem.replace("_", " ").title())


def read_text(path):
    """Прочитать один UTF-8 файл целиком."""
    return path.read_text(encoding="utf-8")


def rank_candidates(data_dir=DATA_DIR):
    """Вернуть непустой рейтинг как список пар (имя, балл) для учебного набора."""
    anonymous = build_profile("Анонимное письмо", read_text(data_dir / "anonymous.txt"))
    # results хранит пары (имя, балл); учебный каталог гарантирует три author_*.txt.
    results = []

    # glob("author_*.txt") выбирает образцы авторов, а sorted() фиксирует их порядок.
    for path in sorted(data_dir.glob("author_*.txt")):
        profile = build_profile(display_name(path), read_text(path))
        results.append((str(profile["name"]), compare_profiles(anonymous, profile)))

    # sorted() стабилен: при равных баллах сохранится зафиксированный выше порядок файлов.
    return sorted(results, key=lambda item: item[1], reverse=True)


def build_artifact(results, data_dir=DATA_DIR):
    """Преобразовать непустой рейтинг в JSON-совместимый отчёт I-01."""
    # candidates меняет форму (имя, балл) на словари с name, score и rank.
    candidates = [
        {"name": name, "score": score, "rank": position}
        for position, (name, score) in enumerate(results, start=1)
    ]
    # Артефакт хранит не только лидера, но и происхождение и предел метода.
    return {
        "schema_version": 1,
        "investigation_id": "I-01",
        "generated_at": "2026-03-15T06:45:00+03:00",
        "source_files": [
            path.relative_to(data_dir).as_posix()
            for path in sorted(data_dir.glob("*.txt"))
        ],
        "findings": [
            {
                "finding_id": "F-I01-AUTHORSHIP",
                "kind": "authorship-ranking",
                "title": "Рейтинг сходства с анонимным предупреждением",
                "summary": (
                    f"Первое место занимает {candidates[0]['name']}; "
                    "оценка сравнивает только частые слова, длину слов и пунктуацию."
                ),
                "candidates": candidates,
                "limitation": (
                    "Выбранные признаки могут совпасть у разных людей, поэтому "
                    "рейтинг задаёт направление проверки, но не устанавливает автора."
                ),
            }
        ],
    }


def save_artifact(artifact, path=ARTIFACT_PATH):
    """Сохранить словарь как читаемый UTF-8 JSON для следующего проекта."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def render_results(results):
    """Показать непустой рейтинг и осторожную интерпретацию в терминале."""
    print("Вероятные авторы")
    print("Место | Кандидат | Сходство")
    for position, (name, score) in enumerate(results, start=1):
        print(f"{position:>5} | {name} | {score:.2f}")

    # Учебный набор содержит три кандидатских файла, поэтому у results есть первый элемент.
    winner, score = results[0]
    print(
        f"\nГлавная версия: {winner} ({score:.2f}). "
        "Это лидер по трём выбранным признакам. "
        "Разные авторы могут использовать похожие слова и пунктуацию, "
        "поэтому результат нужно сверить с другими материалами."
    )


def main():
    """Вычислить рейтинг один раз, затем показать и сохранить его."""
    results = rank_candidates()
    render_results(results)
    save_artifact(build_artifact(results))
    print(f"Отчёт сохранён: {ARTIFACT_PATH.name}")


# При импорте модуль определяет функции, но не запускает расследование.
if __name__ == "__main__":
    main()
```
