# Дело 01. Кто оставил предупреждение?

Первый проект: инструмент стилометрии для поиска источника тревожной записки о полуночной правке.

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
python anonymous_letter.py
```

Стартовый файл пустой. В главе вы вручную добавите загрузку материалов, анализ слов, пунктуации, сравнение профилей и таблицу результатов.

## Самопроверка

После сборки запустите тесты из папки дела:

```bash
python -m unittest discover -s tests
```

## Что изучаем

- виртуальную среду и установку зависимости;
- строки;
- списки;
- словари;
- множества;
- регулярные выражения;
- `collections.Counter`;
- `rich.console.Console` и `rich.table.Table`;
- функции и небольшую архитектуру скрипта.
