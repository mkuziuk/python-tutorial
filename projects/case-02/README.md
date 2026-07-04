# Дело 02. Детектор текстовых совпадений

Второй проект учебника: консольный инструмент, который сравнивает текстовые фрагменты по n-граммам и поднимает наверх подозрительные совпадения.

## Подготовка

Нужен Python 3.14 или новее.

### Windows PowerShell

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### macOS или Linux

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Запуск

```bash
python copy_paste_detector.py
```

В начале файл только загружает фрагменты и показывает короткую сводку. Дальше глава показывает, как постепенно добавить нормализацию слов, n-граммы, сравнение множеств, сортировку рейтинга и таблицу результатов.

## Что изучаем

- кортежи `tuple`;
- n-граммы;
- множества `set`;
- словари `dict`;
- сортировку;
- функции;
- `rich.console.Console` и `rich.table.Table`.
