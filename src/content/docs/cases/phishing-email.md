---
title: "Дело 03. Фишинговое письмо или нет?"
description: "Пошагово строим анализатор .eml-писем: email, regex, urllib.parse, ipaddress, исключения и правила риска."
concepts:
  - regex review
  - email
  - urllib.parse
  - ipaddress
  - exceptions
  - rules
  - Rich
difficulty: "начальный+"
projectId: "case-03"
time: "90-120 минут"
---

<div class="case-meta">
  <p><strong>Миссия</strong> проверить шесть писем и отделить две ловушки от обычной переписки.</p>
  <p><strong>Инструменты</strong> `email`, регулярные выражения, `urllib.parse`, `ipaddress`, собственные исключения, правила и Rich.</p>
  <p><strong>Результат</strong> консольный отчет: файл, вердикт, баллы риска и понятные сигналы.</p>
</div>

<div class="materials-panel">
  <p><strong>Быстрые ссылки:</strong> <a href="../../downloads/case-03.zip">case-03.zip</a> · <a href="../../materials/">материалы всех дел</a> · <a href="../phishing-email-solution/">разбор решения</a></p>
  <p><strong>Справочник:</strong> <a href="../../field-guide/email-url-ip/">email, URL и IP</a> · <a href="../../field-guide/regex/">regex</a> · <a href="../../field-guide/exceptions/">exceptions</a> · <a href="../../field-guide/str/">str</a> · <a href="../../field-guide/list/">list</a> · <a href="../../field-guide/functions/">functions</a> · <a href="../../field-guide/dataclasses/">dataclasses</a> · <a href="../../field-guide/rich/">Rich</a></p>
</div>

## Проблема

Пока команда разбирает текстовые следы, в почтовый ящик приходят новые письма: одно пугает блокировкой архива, другое обещает "отчет с камеры" после ночного сигнала. Всего в наборе шесть `.eml`: два выглядят как ловушки, четыре похожи на обычную рабочую переписку.

Вопрос дела: какие признаки риска видны, если не переходить по ссылкам, не запускать вложения и не доверять письму на слово?

Задача аналитика - сделать первый защитный фильтр. Инструмент откроет письмо как файл, разберет заголовки и тело, найдет ссылки, проверит несколько прозрачных правил и объяснит, почему письмо выглядит спокойным или рискованным.

Скачайте архив [case-03.zip](../../downloads/case-03.zip) или откройте папку `projects/case-03/` в репозитории.

Внутри learner-набора:

- `phishing_email.py` - пустой стартовый файл, который мы будем заполнять;
- `requirements.txt` - единственная внешняя зависимость для красивого вывода;
- `data/*.eml` - письма из дела;
- `check_result.txt` - ориентиры ожидаемого результата.

Полное решение вынесено отдельно: [Разбор полного решения](../phishing-email-solution/).

## Стратегия

Мы построим не магическую модель, а маленький набор правил. Для этого дела важнее всего объяснить каждое решение.

План такой:

1. Прочитать `.eml` через модуль [`email`](../../field-guide/email-url-ip/).
2. Достать `From`, `Reply-To`, `Subject` и текстовые части письма.
3. Найти ссылки [регулярными выражениями](../../field-guide/regex/).
4. Разобрать каждую ссылку через [`urllib.parse.urlparse`](../../field-guide/email-url-ip/).
5. Проверить, является ли хост IP-адресом через [`ipaddress.ip_address`](../../field-guide/email-url-ip/).
6. Начислить баллы за понятные сигналы риска и сохранить их в списке.
7. Показать таблицу с вердиктом и объяснениями.

Сигналы будут такими:

- `Reply-To` ведет в другой домен;
- в теме или теле есть слова срочности;
- ссылка использует IP-адрес вместо домена;
- ссылка начинается с `http://`, а не `https://`;
- видимый домен ссылки не совпадает с реальным адресом;
- ссылка уводит в домен, не похожий на домен отправителя;
- вложение имеет рискованное расширение.

Это не промышленный антифишинговый сканер. Но это хороший первый прибор: он не ставит один общий ярлык, а показывает, какие именно факты стоит проверить.

## Сборка инструмента

### Подготовка окружения

Создайте виртуальную среду в папке проекта.

Windows PowerShell:

```powershell
cd path\to\case-03
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

macOS или Linux:

```bash
cd path/to/case-03
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Проверьте пустой стартовый файл:

```bash
python phishing_email.py
```

Он пока ничего не выводит: это нормально. Теперь начнем собирать анализатор риска.

Откройте `phishing_email.py` и добавьте импорты, путь к письмам и консоль:

```python
from dataclasses import dataclass
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr
from pathlib import Path
import ipaddress
import re
from urllib.parse import urlparse

from rich.console import Console
from rich.table import Table

DATA_DIR = Path(__file__).with_name("data")
console = Console()
```

### Данные отчета

Добавим структуры для ссылки, сигнала и отчета. [`dataclass`](../../field-guide/dataclasses/) удобен, когда нужно передавать по программе несколько связанных полей. Здесь каждая структура делает форму данных явной: ссылка, сигнал риска и итоговый отчет не смешиваются в один большой словарь.

```python
@dataclass(frozen=True)
class LinkInfo:
    raw: str
    label: str
    scheme: str
    host: str
    display_host: str
    is_ip_host: bool


@dataclass(frozen=True)
class RiskSignal:
    title: str
    points: int
    level: str


@dataclass(frozen=True)
class EmailReport:
    filename: str
    subject: str
    sender: str
    score: int
    verdict: str
    signals: list[RiskSignal]
    links: list[LinkInfo]
```

`raw` хранит исходную ссылку, `host` - реальный хост из URL, а `display_host` - домен, который был виден в тексте ссылки. В HTML-письмах это часто разные вещи: текст может выглядеть как `support.example.org`, а `href` вести совсем в другое место.

`EmailReport` - итог одной проверки. Функции анализа могут спокойно возвращать этот объект, а функция вывода получает уже готовые поля и не пересчитывает риск заново.

### Исключение для дела

Ошибки чтения лучше не прятать. Но и обычный `OSError` из глубины файловой системы мало говорит ученику. Сделаем свое [исключение](../../field-guide/exceptions/):

```python
class EmailAnalysisError(Exception):
    """Raised when an .eml file cannot be parsed for this case."""
```

Теперь чтение письма может объяснить, чего именно не хватает:

```python
from email import policy
from email.parser import BytesParser


def load_message(path):
    try:
        with path.open("rb") as file:
            message = BytesParser(policy=policy.default).parse(file)
    except OSError as exc:
        raise EmailAnalysisError(f"Cannot read {path}") from exc

    if not message.get("From"):
        raise EmailAnalysisError(f"{path.name}: missing From header")
    if not message.get("Subject"):
        raise EmailAnalysisError(f"{path.name}: missing Subject header")

    return message
```

### Текст письма

Файл `.eml` может быть простым текстом или `multipart`: например, одна часть `text/plain`, другая `text/html`. Для нашего дела берем только текстовые части и пропускаем вложения.

```python
TEXT_CONTENT_TYPES = {"text/plain", "text/html"}


def text_from_message(message):
    try:
        if not message.is_multipart():
            content = message.get_content()
            return content if isinstance(content, str) else ""

        chunks = []
        for part in message.walk():
            if part.is_multipart() or part.get_content_disposition() == "attachment":
                continue
            if part.get_content_type() in TEXT_CONTENT_TYPES:
                content = part.get_content()
                if isinstance(content, str):
                    chunks.append(content)
        return "\n".join(chunks)
    except (LookupError, UnicodeDecodeError) as exc:
        raise EmailAnalysisError("Cannot decode message body") from exc
```

Код явно говорит, какие части письма он анализирует, а какие оставляет за пределами задачи. Функция возвращает одну строку: это упрощает поиск ссылок и срочных слов, но не делает вид, что анализировал вложения как файлы.

### Повторяем regex: ссылки и HTML-ярлыки

Ссылки можно искать регулярным выражением. Для обычных URL достаточно такого шаблона:

```python
URL_RE = re.compile(r"https?://[^\s<>'\"\\]+", re.IGNORECASE)
```

Но в HTML бывает полезно отдельно найти пару `href` + видимый текст:

```python
HTML_LINK_RE = re.compile(
    r"<a\s+[^>]*href=[\"'](?P<url>https?://[^\"']+)[\"'][^>]*>"
    r"(?P<label>.*?)</a>",
    re.IGNORECASE | re.DOTALL,
)
```

Именованные группы `(?P<url>...)` и `(?P<label>...)` делают код чтения понятнее: мы не запоминаем, была ли ссылка первой или второй группой.

### Разбор URL и IP-адресов

[`urllib.parse.urlparse`](../../field-guide/email-url-ip/) разбирает строку URL на схему, хост, путь и параметры. [`ipaddress.ip_address`](../../field-guide/email-url-ip/) проверяет, является ли хост IP-адресом.

```python
from urllib.parse import urlparse
import ipaddress


def is_ip_address(host):
    if not host:
        return False
    try:
        ipaddress.ip_address(host.strip("[]"))
    except ValueError:
        return False
    return True


def make_link_info(raw_url, label=""):
    parsed = urlparse(raw_url)
    host = normalize_host(parsed.hostname or "")
    return LinkInfo(
        raw=raw_url,
        label=label,
        scheme=parsed.scheme.lower(),
        host=host,
        display_host=display_host_from_label(label),
        is_ip_host=is_ip_address(host),
    )
```

Обратите внимание: `ip_address()` бросает `ValueError`, если строка не похожа на IP. Это нормальная ситуация, а не авария. Мы перехватываем исключение и возвращаем `False`.

### Правила риска

Сделаем маленькую функцию, которая добавляет сигнал только один раз:

```python
def add_signal(
    signals,
    title,
    points,
    level="warning",
):
    if all(signal.title != title for signal in signals):
        signals.append(RiskSignal(title=title, points=points, level=level))
```

`add_signal()` защищает отчет от повторов. Например, если в письме пять `http`-ссылок, ученик должен увидеть один понятный сигнал "есть нешифрованные ссылки", а не пять одинаковых строк, которые раздувают отчет и балл.

Теперь центральная функция анализа становится последовательным списком правил:

```python
def analyze_message(message, filename="<memory>"):
    subject = str(message.get("Subject", "(без темы)"))
    sender = str(message.get("From", ""))
    sender_domain = domain_from_address(sender)
    reply_to_domain = domain_from_address(message.get("Reply-To"))
    body = text_from_message(message)
    links = extract_links(body)
    signals = []

    if reply_to_domain and base_domain(reply_to_domain) != base_domain(sender_domain):
        add_signal(signals, "Reply-To ведет в другой домен", 2)

    if URGENT_RE.search(f"{subject}\n{body}"):
        add_signal(signals, "Есть слова срочности", 1)

    for link in links:
        if link.is_ip_host:
            add_signal(signals, "Ссылка ведет на IP-адрес вместо домена", 3, "danger")

        if link.scheme == "http":
            add_signal(signals, "Ссылка использует http без шифрования", 2)

        if link.display_host and base_domain(link.display_host) != base_domain(link.host):
            add_signal(signals, "Видимый домен ссылки не совпадает с реальным", 3, "danger")
```

Дальше добавьте правило про домен ссылки, правило про количество ссылок, проверку расширений вложений и итоговый `EmailReport`. Эти правила используют ту же форму: нашли факт, добавили `RiskSignal`, затем сумма баллов превращается в вердикт. Полный код есть в разборе, но лучше сначала собрать этот каркас руками.

### Вердикт и таблица

Баллы превращаются в человеческий вердикт. Границы выбраны так, чтобы один слабый сигнал не поднимал письмо наверх, а несколько независимых признаков давали заметный результат:

```python
def risk_verdict(score):
    if score >= 7:
        return "высокий риск"
    if score >= 3:
        return "проверить вручную"
    return "низкий риск"
```

Для вывода используем только две части [Rich](../../field-guide/rich/): `Console` и `Table`. `render_results()` не решает, опасно ли письмо; он только показывает готовые `EmailReport`.

```python
def render_results(reports):
    table = Table(title="Проверка писем")
    table.add_column("Файл", style="cyan")
    table.add_column("Вердикт")
    table.add_column("Балл", justify="right")
    table.add_column("Сигналы")

    for report in sorted(reports, key=lambda item: item.score, reverse=True):
        signals = "\n".join(
            f"{signal.title} (+{signal.points})" for signal in report.signals
        )
        table.add_row(
            report.filename,
            report.verdict,
            str(report.score),
            signals or "явных сигналов нет",
        )

    console.print(table)
```

## Проверка

Запустите инструмент:

```bash
python phishing_email.py
```

Ожидаемая форма результата:

```text
02-lockout-warning.eml  высокий риск  12
05-camera-report.eml    высокий риск  8
01-archive-update.eml   низкий риск   0
03-receipt-note.eml     низкий риск   0
04-schedule-note.eml    низкий риск   0
06-staff-note.eml       низкий риск   0
```

Если `02-lockout-warning.eml` и `05-camera-report.eml` оказались наверху, а четыре рабочих письма остались спокойными, инструмент работает как задумано. Если числа отличаются, проверьте веса правил и то, не добавили ли вы один и тот же сигнал несколько раз.

## Что мы использовали

- [Установка Python](../../field-guide/install-python/) - виртуальная среда, зависимости и запуск проекта.
- [Regex](../../field-guide/regex/) - повторили поиск URL, HTML-ссылок и слов срочности.
- [Строки `str`](../../field-guide/str/) - нормализация хостов, доменов и текстовых ярлыков.
- [Списки `list`](../../field-guide/list/) - список ссылок, сигналов и отчетов.
- [dataclasses](../../field-guide/dataclasses/) - `LinkInfo`, `RiskSignal` и `EmailReport` как явные формы данных.
- [email, URL и IP](../../field-guide/email-url-ip/) - `.eml`, `urllib.parse.urlparse` и `ipaddress.ip_address`.
- [Исключения](../../field-guide/exceptions/) - отделили ошибки чтения письма от обычных проверок риска.
- [Rich](../../field-guide/rich/) - таблица отчета, а не логика анализа.
- Правила риска - небольшие функции и проверки, которые можно объяснить словами.

## Усложняем проект

1. Добавьте список доверенных доменов и отдельный сигнал для всех остальных.
2. Считайте количество разных доменов в письме.
3. Разберите `Authentication-Results` и добавьте осторожный сигнал для `spf=fail` или `dkim=fail`.
4. Сохраните отчет в JSON, чтобы его можно было сравнивать между запусками.
5. Добавьте режим `--file path/to/message.eml` для проверки одного письма.

Когда закончите, откройте [разбор полного решения](../phishing-email-solution/).
