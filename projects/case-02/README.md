# Дело 02. Детектор текстовых совпадений

Второй проект: консольный инструмент, который сравнивает архивные отчеты по n-граммам и поднимает наверх подозрительные совпадения, похожие на утечку или подмену.

## Подготовка

Нужен Python 3.13 или новее.

### Windows PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### macOS или Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Запуск

```bash
python copy_paste_detector.py
```

Стартовый файл пустой. В главе вы вручную добавите чтение текста, нормализацию слов, n-граммы, сравнение множеств, сортировку рейтинга и таблицу результатов.

## Самопроверка

После сборки запустите тесты из папки дела:

```bash
python -m unittest discover -s tests
```

## Что изучаем

- кортежи `tuple`;
- n-граммы;
- множества `set`;
- словари `dict`;
- сортировку;
- функции;
- `rich.console.Console` и `rich.table.Table`.
