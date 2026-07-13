# Дело 06. Вердикт перед открытием

Финальный проект сводит улики ночи 14 марта 2026 года в проверяемый отчёт: хронологию, рейтинг гипотез, ограничения вывода и решение об открытии выставки 15 марта.

## Подготовка

Нужен Python 3.13 или новее. Сторонних библиотек нет.

### Windows PowerShell

```powershell
py -3 --version
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python --version
```

### macOS или Linux

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Команда проверки версии должна показать Python 3.13 или новее.

## Запуск

```bash
python final_verdict.py
```

Стартовый файл намеренно пуст. Соберите программу по главе «Дело 06. Вердикт перед открытием»: готовая версия читает `data/evidence_bundle.json`, печатает отчёт и создаёт `verdict.json` рядом со скриптом.

После сборки сравните форму вывода с `check_result.txt` и проверьте JSON:

```bash
python final_verdict.py
python -m json.tool verdict.json
python -m unittest discover -s tests -v
```

Обычная команда `python -m unittest discover -s tests -v` всегда проверяет собранный вами корневой `final_verdict.py` — и в репозитории, и в скачанном наборе. Эталон из `solution/` отдельно проверяет общая команда сопровождающего `pnpm test:python`, запущенная из корня сайта.

## Что изучаем

- `StrEnum` для ограниченного словаря значений;
- неизменяемые `@dataclass(frozen=True, slots=True)`;
- структурное сопоставление `match`;
- чтение и запись JSON;
- сортировку хронологии и объяснимый рейтинг гипотез;
- различие между уликой, гипотезой и операционным решением.
