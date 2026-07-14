import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = ROOT / "src" / "content" / "docs" / "cases"

PAGES = [
    ("01", "anonymous_letter.py", "anonymous-letter-solution.md", "Кто оставил предупреждение?", "Рейтинг авторов и 01-authorship.json"),
    ("02", "copy_paste_detector.py", "copy-paste-detector-solution.md", "Детектор текстовых совпадений", "Рейтинг n-грамм и 02-text-matches.json"),
    ("03", "phishing_email.py", "phishing-email-solution.md", "Фишинговое письмо или нет?", "Разбор писем и 03-mail-review.json"),
    ("04", "secret_folder_archive.py", "secret-folder-archive-solution.md", "Ночной сигнал архива", "SHA-256, происхождение файлов и 04-evidence-index.json"),
    ("05", "investigation_system.py", "investigation-system-solution.md", "Доска расследования", "Объекты, связи и 05-case-board.json"),
    ("06", "final_verdict.py", "final-verdict-solution.md", "Вердикт перед открытием", "Утренние обновления, гипотезы и 06-verdict.json"),
]


def page_text(case_number, source_name, title, description):
    source_path = ROOT / "projects" / f"case-{case_number}" / "solution" / source_name
    code = source_path.read_text(encoding="utf-8").rstrip()
    return f'''---
title: "Разбор решения: {title}"
description: "{description}."
---

Эта страница показывает полную версию программы после выполнения упражнения. Сначала завершите самостоятельную версию и запустите тесты.

Решение сохраняет результат в JSON для следующего расследования. Поэтому важно проверять не только таблицу в терминале, но и структуру созданного файла.

```python
{code}
```

## Проверка

Из папки проекта выполните:

```bash
python -m unittest discover -s tests
```

Все переходы I-01 → I-06 дополнительно проверяет команда сопровождающего `pnpm test:part1-artifacts`.
'''


def main():
    parser = argparse.ArgumentParser(description="Build Part I solution pages from canonical Python files.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = []
    for case_number, source_name, page_name, title, description in PAGES:
        path = CASES_DIR / page_name
        expected = page_text(case_number, source_name, title, description)
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                stale.append(path.relative_to(ROOT).as_posix())
        else:
            path.write_text(expected, encoding="utf-8")
            print(f"built {path.relative_to(ROOT)}")
    if stale:
        print("Part I solution pages are stale:", file=sys.stderr)
        for item in stale:
            print(f"- {item}", file=sys.stderr)
        raise SystemExit(1)
    if args.check:
        print(f"checked {len(PAGES)} Part I solution pages")


if __name__ == "__main__":
    main()
