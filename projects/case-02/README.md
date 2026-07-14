# Расследование 02. Детектор текстовых совпадений

Второй проект читает `data/artifacts/01-authorship.json`, добавляет анонимное предупреждение к архивным текстам и сравнивает их по n-граммам. Результат сохраняется в `artifacts/02-text-matches.json`.

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

`copy_paste_detector.py` — пустой стартовый файл. Переносите в него листинги главы по порядку: чтение текста, нормализацию слов, n-граммы, сравнение множеств, загрузку результата I-01 и сохранение нового отчёта.

## Что изучаем

- кортежи `tuple`;
- n-граммы;
- множества `set`;
- словари `dict`;
- сортировку;
- функции;
- `rich.console.Console` и `rich.table.Table`.
- передачу данных между программами через JSON.
