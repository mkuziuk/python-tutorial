# Расследование 04. Ночной сигнал архива

Четвёртый проект фиксирует результаты I-01–I-03 и ночную папку как единый набор материалов. Он проверяет SHA-256 входных отчётов, ищет байтовые дубли и сравнивает сохранённые версии хронологии.

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
python secret_folder_archive.py
```

Стартовый файл намеренно пуст. По главе вы добавите обход `data/secret_folder/` и `data/artifacts/`, вычисление SHA-256, проверку трёх входных отчётов и построчное сравнение двух хронологий. Программа создаст `artifacts/04-evidence-index.json`; вручную менять файлы и повторять запуск не требуется.

Хэш SHA-256 работает как цифровой отпечаток файла: одинаковые байты дают одинаковую строку, а небольшая правка меняет её.

## Самопроверка

После сборки запустите тесты из папки расследования:

```bash
python -m unittest discover -s tests
```

## Что изучаем

- `pathlib.Path`;
- рекурсивный обход файлов;
- `hashlib.sha256`;
- JSON;
- временные метки в UTC;
- поиск дублей;
- проверку происхождения отчётов по SHA-256;
- `difflib.ndiff` для расхождения `22:53` / `23:07` в хронологиях;
- `rich.console.Console` и `rich.table.Table`.
