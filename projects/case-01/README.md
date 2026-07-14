# Расследование 01. Кто оставил предупреждение?

Первый проект — инструмент стилометрии для поиска автора тревожной записки о полуночной правке.

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

Стартовый файл намеренно пуст. По главе вы добавите загрузку материалов, анализ слов и пунктуации, сравнение профилей и таблицу результатов. В конце программа сохранит рейтинг и его ограничение в `artifacts/01-authorship.json`; расследование 02 прочитает этот файл.

## Самопроверка

После сборки запустите тесты из папки расследования:

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
- сохранение результата для следующего расследования в JSON.
