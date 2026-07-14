# Расследование 03. Фишинговое письмо или нет?

Консольный инструмент читает письма в формате `.eml` и объясняет, какие признаки риска в них обнаружены.

В папке `data/` шесть писем: два похожи на ловушки перед открытием архива, четыре выглядят как обычная рабочая переписка.

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
python phishing_email.py
```

`phishing_email.py` — пустой стартовый файл. Добавляйте код по разделам урока: сначала чтение `.eml`, затем описание и оценку ссылок, правила уровня письма, пакетную обработку и `artifacts/03-mail-review.json`. Программа читает общие фразы из `data/artifacts/02-text-matches.json` и отмечает связь письма с предыдущими материалами отдельно от риска.

## Самопроверка

После сборки запустите тесты из папки расследования:

```bash
python -m unittest discover -s tests
```

## Что изучаем

- модуль `email` для чтения `.eml`;
- один регулярный шаблон для обычных URL;
- `EmailMessage.get_body()` и `iter_attachments()`;
- `urllib.parse.urlparse`;
- `ipaddress.ip_address`;
- отдельную функцию `assess_link()` для проверки схемы, домена, подписи и порта URL;
- собственные исключения;
- отдельный `try`/`except` для ошибки чтения файла;
- обработку `EmailAnalysisError` внутри цикла с продолжением остальных писем;
- `rich.console.Console` и `rich.table.Table` для отчёта в терминале.
