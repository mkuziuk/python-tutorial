# Дело 03. Фишинговое письмо или нет?

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

В стартовом файле есть только учебные ориентиры. По главе вы добавите чтение писем, поиск ссылок и правила риска: срочность, несовпадение `Reply-To`, ссылки на IP-адреса, `http` без шифрования, расхождение видимого домена с фактическим адресом и подозрительные имена вложений.

## Самопроверка

После сборки запустите тесты из папки дела:

```bash
python -m unittest discover -s tests
```

## Что изучаем

- модуль `email` для чтения `.eml`;
- регулярные выражения для аккуратного поиска ссылок и слов срочности;
- `urllib.parse.urlparse`;
- `ipaddress.ip_address`;
- собственные исключения;
- правила как небольшие проверяемые функции;
- `rich.console.Console` и `rich.table.Table` для отчёта в терминале.
