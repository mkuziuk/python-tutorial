---
title: "Дело 03. Фишинговое письмо или нет?"
description: "Пошагово строим анализатор .eml-писем: email, regex, urllib.parse, ipaddress, исключения и правила риска."
concepts:
  - повторение регулярных выражений
  - email
  - urllib.parse
  - ipaddress
  - exceptions
  - rules
  - Rich
  - работа с файлами
  - unittest
difficulty: "средний"
projectId: "case-03"
time: "120-150 минут"
---

<div class="case-meta">
  <p><strong>Миссия</strong> проверить шесть писем и отделить две ловушки от обычной переписки.</p>
  <p><strong>Инструменты</strong> `email`, регулярные выражения, `urllib.parse`, `ipaddress`, собственные исключения, правила и Rich.</p>
  <p><strong>Результат</strong> отчёт в терминале: файл, вердикт, баллы риска и понятные сигналы.</p>
  <p><strong>Маршрут</strong> средний · 120–150 минут · Python 3.13+</p>
</div>

<div class="materials-panel">
  <p><strong>Быстрые ссылки:</strong> <a href="../../downloads/case-03.zip">case-03.zip</a> · <a href="../../materials/">материалы всех дел</a> · <a href="../phishing-email-solution/">разбор решения</a></p>
  <p><strong>Справочник:</strong> <a href="../../field-guide/email-url-ip/">email, URL и IP</a> · <a href="../../field-guide/regex/">regex</a> · <a href="../../field-guide/exceptions/">exceptions</a> · <a href="../../field-guide/file-io/">файлы</a> · <a href="../../field-guide/str/">str</a> · <a href="../../field-guide/list/">list</a> · <a href="../../field-guide/functions/">functions</a> · <a href="../../field-guide/dataclasses/">dataclasses</a> · <a href="../../field-guide/rich/">Rich</a> · <a href="../../field-guide/testing/">unittest</a></p>
</div>

## Проблема

Пока команда разбирает текстовые следы, в почтовый ящик приходят новые письма: одно пугает блокировкой архива, другое обещает «отчёт с камеры» после ночного сигнала. Всего в наборе шесть файлов `.eml`: два выглядят как ловушки, четыре похожи на обычную рабочую переписку.

Вопрос дела: какие признаки риска видны, если не переходить по ссылкам, не запускать вложения и не доверять письму на слово?

Задача аналитика — сделать первый защитный фильтр. Инструмент откроет письмо как файл, разберёт заголовки и тело, найдёт ссылки, проверит несколько прозрачных правил и объяснит, почему письмо выглядит безопасным или подозрительным.

Скачайте архив [case-03.zip](../../downloads/case-03.zip) или откройте папку `projects/case-03/` в репозитории.

В учебном наборе:

- `phishing_email.py` — пустой стартовый файл;
- `requirements.txt` — единственная внешняя зависимость для удобного вывода;
- `data/*.eml` — письма из дела;
- `check_result.txt` — ориентиры ожидаемого результата.

Полное решение вынесено отдельно: [Разбор полного решения](../phishing-email-solution/).

## Стратегия

Мы построим не загадочную модель, а небольшой набор явных правил. Для этого дела особенно важно объяснить каждое решение.

План такой:

1. Прочитать `.eml` через модуль [`email`](../../field-guide/email-url-ip/).
2. Достать `From`, `Reply-To`, `Subject` и текстовые части письма.
3. Найти ссылки [регулярными выражениями](../../field-guide/regex/).
4. Разобрать каждую ссылку через [`urllib.parse.urlparse`](../../field-guide/email-url-ip/).
5. Проверить, является ли хост IP-адресом через [`ipaddress.ip_address`](../../field-guide/email-url-ip/).
6. Начислить баллы за понятные сигналы риска и сохранить их в списке.
7. Показать таблицу с вердиктом и объяснениями.

Сигналы будут такими:

- `Reply-To` ведёт в другой домен;
- в теме или теле есть слова срочности;
- ссылка использует IP-адрес вместо домена;
- ссылка начинается с `http://`, а не `https://`;
- видимый домен ссылки не совпадает с реальным адресом;
- ссылка уводит в домен, не похожий на домен отправителя;
- в письме необычно много ссылок;
- вложение имеет рискованное расширение.

Это не промышленный антифишинговый сканер. Но это хороший первый прибор: он не ставит один общий ярлык, а показывает, какие именно факты стоит проверить.

## Сборка инструмента

### Подготовка окружения

Создайте виртуальную среду в папке проекта. Нужен Python 3.13 или новее; перед началом проверьте `py -3 --version` на Windows или `python3 --version` на macOS и Linux.

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

Запустите стартовый файл:

```bash
python phishing_email.py
```

Пока программа ничего не выводит: это нормально. Теперь начнём собирать анализатор риска.

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

# Анализатор читает только локальные учебные письма и не обращается к найденным адресам.
DATA_DIR = Path(__file__).with_name("data")
console = Console()
```

### Данные отчёта

Добавим структуры для ссылки, сигнала и отчёта. [`dataclass`](../../field-guide/dataclasses/) удобен, когда нужно передавать по программе несколько связанных полей. Каждая структура явно описывает свою форму данных, поэтому ссылка, сигнал риска и итоговый отчёт не смешиваются в одном большом словаре.

```python
# frozen защищает уже созданный объект от случайного изменения на следующих этапах.
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
    # points — число баллов, которое сигнал добавляет к score.
    points: int
    level: str


@dataclass(frozen=True)
class EmailReport:
    filename: str
    subject: str
    sender: str
    sender_domain: str
    # links и signals сохраняют объяснение итогового score: отчёт можно проверить вручную.
    links: list[LinkInfo]
    signals: list[RiskSignal]
    score: int
    verdict: str
```

`raw` хранит исходную ссылку, `host` — фактический хост из URL, а `display_host` — домен, показанный в тексте ссылки. В HTML-письмах они могут различаться: текст выглядит как `support.example.org`, а `href` ведёт на другой адрес.

`EmailReport` — результат одной проверки. Функции анализа возвращают этот объект, а функция вывода получает готовые поля и не пересчитывает риск. `score` показывает сумму баллов правил, но не является вероятностью фишинга.

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
        # BytesParser преобразует содержимое .eml-файла в объект сообщения.
        with path.open("rb") as file:
            # Читаем исходные байты, чтобы policy.default корректно декодировала MIME.
            message = BytesParser(policy=policy.default).parse(file)
    except OSError as exc:
        raise EmailAnalysisError(f"Cannot read {path}") from exc

    # Для анализа нужны заголовки From и Subject, поэтому проверяем их сразу после чтения письма.
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
# Остальные MIME-типы не участвуют в поиске слов срочности и ссылок.


def text_from_message(message):
    try:
        if not message.is_multipart():
            content = message.get_content()
            return content if isinstance(content, str) else ""

        chunks = []
        # Обходим MIME-дерево, потому что текст может лежать глубже первого уровня письма.
        for part in message.walk():
            # walk() возвращает и multipart-контейнеры, поэтому пропускаем их и вложения.
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

#### Промежуточная проверка: письмо читается

Сохраните файл и проверьте первый законченный путь данных: путь → `.eml` → объект письма → тема. Команда импортирует функции, поэтому основной отчёт пока не нужен.

```bash
python -c "from phishing_email import DATA_DIR, load_message; message = load_message(DATA_DIR / '01-archive-update.eml'); print(message['Subject'])"
```

Вы должны увидеть `Обновление карточки архива`. Если вместо темы появилась ошибка пути, проверьте, что `phishing_email.py` и папка `data` лежат рядом.

### Повторяем regex: ссылки и HTML-ярлыки

Ссылки можно искать регулярным выражением. Первый шаблон находит обычные URL, второй — пару из `href` и видимого текста в HTML. Остальные шаблоны понадобятся для очистки подписи и поиска домена внутри неё.

```python
TRAILING_URL_CHARS = ".,;:!?)]}"

# URL_RE и HTML_LINK_RE находят ссылки http/https в учебных письмах.
URL_RE = re.compile(r"https?://[^\s<>'\"\\]+", re.IGNORECASE)
HTML_LINK_RE = re.compile(
    r"<a\s+[^>]*href=[\"'](?P<url>https?://[^\"']+)[\"'][^>]*>"
    r"(?P<label>.*?)</a>",
    re.IGNORECASE | re.DOTALL,
)
TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")
DOMAIN_RE = re.compile(
    r"\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}\b",
    re.IGNORECASE,
)
```

Эти шаблоны рассчитаны на формат учебных писем. Для разбора произвольного HTML нужен полноценный HTML-парсер.

Именованные группы `(?P<url>...)` и `(?P<label>...)` делают код чтения понятнее: мы не запоминаем, была ли ссылка первой или второй группой.

### Нормализация URL и доменов

Перед сравнением уберем пунктуацию после URL, HTML-теги внутри ярлыка и разницу в регистре хоста.

```python
def clean_url(raw_url):
    # Убираем только знаки, которыми URL обычно заканчивается в прозе; путь и параметры не меняем.
    return raw_url.rstrip(TRAILING_URL_CHARS)


def clean_label(raw_label):
    # Удаляем разметку только из видимой подписи; адрес href разбирается отдельно.
    without_tags = TAG_RE.sub(" ", raw_label)
    return SPACE_RE.sub(" ", without_tags).strip()


def normalize_host(host):
    # Завершающая точка и регистр не должны превращать один DNS-хост в два разных.
    return host.strip().strip(".").lower()
```

[`urllib.parse.urlparse`](../../field-guide/email-url-ip/) разбирает URL на схему, хост, путь и параметры. [`ipaddress.ip_address`](../../field-guide/email-url-ip/) проверяет, является ли хост IP-адресом.

```python
def is_ip_address(host):
    if not host:
        return False
    try:
        # Квадратные скобки допустимы вокруг IPv6 в URL, но не являются частью самого адреса.
        ipaddress.ip_address(host.strip("[]"))
    except ValueError:
        return False
    return True


def base_domain(host):
    host = normalize_host(host)
    if not host or is_ip_address(host):
        return host

    labels = host.split(".")
    if len(labels) < 2:
        return host
    # В учебных данных базовый домен — две последние части хоста.
    return ".".join(labels[-2:])


def domain_from_address(value):
    # parseaddr возвращает адрес без отображаемого имени отправителя.
    _, address = parseaddr(value or "")
    if "@" not in address:
        return ""
    return normalize_host(address.rsplit("@", 1)[1])


def display_host_from_label(label):
    # DOMAIN_RE извлекает первый домен из текста ссылки.
    match = DOMAIN_RE.search(label)
    if match is None:
        return ""
    return normalize_host(match.group(0))
```

`base_domain()` в этом учебном наборе берёт последние две части хоста. В промышленном коде понадобился бы список публичных суффиксов, но для доменов из дела этого правила достаточно.

Теперь соберём `LinkInfo` и исключим дубли: HTML-ссылка встречается и в `href`, и при общем поиске URL, но в отчёте должна остаться только один раз.

```python
def make_link_info(raw_url, label=""):
    # urlparse разделяет raw_url на схему, хост, путь и параметры.
    parsed = urlparse(raw_url)
    # hostname уже отделён от схемы, порта, пути и параметров URL.
    host = normalize_host(parsed.hostname or "")
    return LinkInfo(
        raw=raw_url,
        label=label,
        scheme=parsed.scheme.lower(),
        host=host,
        display_host=display_host_from_label(label),
        is_ip_host=is_ip_address(host),
    )


def extract_links(text):
    links = []
    # Множество хранит уже учтённые адреса между двумя проходами по HTML и обычному тексту.
    seen_urls = set()

    # Сначала читаем HTML-ссылки: только так можно сравнить видимую подпись с реальным href.
    for match in HTML_LINK_RE.finditer(text):
        url = clean_url(match.group("url"))
        label = clean_label(match.group("label"))
        if url not in seen_urls:
            links.append(make_link_info(url, label))
            seen_urls.add(url)

    # href уже найден выше; seen_urls не даёт учесть тот же URL второй раз.
    for match in URL_RE.finditer(text):
        url = clean_url(match.group(0))
        if url not in seen_urls:
            links.append(make_link_info(url))
            seen_urls.add(url)

    return links
```

Обратите внимание: `ip_address()` бросает `ValueError`, если строка не похожа на IP. Это нормальная ситуация, а не авария. Мы перехватываем исключение и возвращаем `False`.

#### Промежуточная проверка: ссылка и её ярлык различаются

```bash
python -c "from phishing_email import DATA_DIR, extract_links, load_message, text_from_message; message = load_message(DATA_DIR / '02-lockout-warning.eml'); print([(link.host, link.display_host) for link in extract_links(text_from_message(message))])"
```

Среди пар должна быть `('198.51.100.44', 'support.example.org')`. Это именно тот факт, который позже превратится в риск-сигнал.

### Правила риска

Слова срочности и опасные расширения тоже зададим явными шаблонами. Функция `attachment_names()` читает только имена вложений; она ничего не сохраняет и не запускает. Совпадение расширения добавляет сигнал для ручной проверки, но само по себе не доказывает вредоносность файла.

```python
URGENT_RE = re.compile(
    r"срочно|немедленно|сегодня|до конца дня|последнее уведомление|urgent|immediately",
    re.IGNORECASE,
)
RISKY_ATTACHMENT_RE = re.compile(r"\.(exe|js|scr|cmd|bat|vbs|ps1)$", re.IGNORECASE)


# attachment_names() собирает имена MIME-частей с типом attachment.
def attachment_names(message):
    names = []
    for part in message.walk():
        if part.get_content_disposition() == "attachment":
            filename = part.get_filename()
            if filename:
                names.append(filename)
    return names
```

Сделаем маленькую функцию, которая добавляет сигнал только один раз, и отдельную функцию для перевода суммы в вердикт:

```python
def add_signal(
    signals,
    title,
    points,
    level="warning",
):
    # Каждый тип риска добавляем один раз, даже если ему соответствуют несколько ссылок.
    # Повторяющиеся ссылки не должны повторно добавлять сигнал и увеличивать score.
    if all(signal.title != title for signal in signals):
        signals.append(RiskSignal(title=title, points=points, level=level))


def risk_verdict(score):
    # score от 7 означает высокий риск, от 3 — ручную проверку.
    if score >= 7:
        return "высокий риск"
    if score >= 3:
        return "проверить вручную"
    return "низкий риск"
```

`add_signal()` защищает отчёт от повторов. Например, для пяти `http`-ссылок нужен один понятный сигнал «есть незашифрованные ссылки», а не пять одинаковых строк, искусственно увеличивающих отчёт и балл.

Теперь центральная функция анализа становится последовательным списком правил:

```python
def analyze_message(message, filename="<memory>"):
    # Сначала извлекаем поля письма и ссылки, затем проверяем правила риска.
    subject = str(message.get("Subject", "(без темы)"))
    sender = str(message.get("From", ""))
    sender_domain = domain_from_address(sender)
    reply_to_domain = domain_from_address(message.get("Reply-To"))
    body = text_from_message(message)
    links = extract_links(body)
    signals = []

    if reply_to_domain and base_domain(reply_to_domain) != base_domain(sender_domain):
        add_signal(signals, "Reply-To ведёт в другой домен", 2)

    # Срочность ищем и в теме, и в теле: отправитель может вынести давление в любое из полей.
    if URGENT_RE.search(f"{subject}\n{body}"):
        add_signal(signals, "Есть слова срочности", 1)

    for link in links:
        # Одна ссылка может нарушать несколько независимых правил, поэтому проверки не связаны через elif.
        if link.is_ip_host:
            add_signal(signals, "Ссылка ведёт на IP-адрес вместо домена", 3, "danger")

        if link.scheme == "http":
            add_signal(signals, "Ссылка использует http без шифрования", 2)

        # Текст ссылки может обещать один домен, а href вести на другой.
        if link.display_host and base_domain(link.display_host) != base_domain(link.host):
            add_signal(signals, "Видимый домен ссылки не совпадает с реальным", 3, "danger")

        if (
            sender_domain
            and link.host
            and not link.is_ip_host
            and base_domain(link.host) != base_domain(sender_domain)
        ):
            add_signal(signals, "Ссылка ведёт в домен, отличный от домена отправителя", 1)

    if len(links) >= 4:
        add_signal(signals, "В письме слишком много ссылок", 1)

    risky_attachments = [
        name for name in attachment_names(message) if RISKY_ATTACHMENT_RE.search(name)
    ]
    if risky_attachments:
        add_signal(signals, "Есть вложение с рискованным расширением", 3, "danger")

    # score равен сумме points всех сигналов, поэтому вклад каждого правила виден в отчёте.
    score = sum(signal.points for signal in signals)
    return EmailReport(
        filename=filename,
        subject=subject,
        sender=sender,
        sender_domain=sender_domain,
        links=links,
        signals=signals,
        score=score,
        verdict=risk_verdict(score),
    )
```

Каждое правило использует одну форму: нашли проверяемый факт, один раз добавили `RiskSignal`, затем сумма баллов превратилась в вердикт. Границы подобраны так, чтобы один слабый сигнал не поднимал письмо наверх.

Обернем анализ одного сообщения в функции для файла и каталога:

```python
def analyze_file(path):
    # Читаем письмо из файла и передаём разобранное сообщение в analyze_message().
    return analyze_message(load_message(path), filename=path.name)


def analyze_directory(data_dir=DATA_DIR):
    # Фиксированный порядок файлов делает отчёт одинаковым на разных файловых системах.
    paths = sorted(data_dir.glob("*.eml"))
    if not paths:
        raise EmailAnalysisError(f"No .eml files found in {data_dir}")
    return [analyze_file(path) for path in paths]
```

#### Промежуточная проверка: правила дают ожидаемый балл

```bash
python -c "from phishing_email import DATA_DIR, analyze_file; print(analyze_file(DATA_DIR / '02-lockout-warning.eml').score)"
```

Результат должен быть `12`. Если он меньше, распечатайте названия `report.signals` и найдите правило, которое не сработало. Затем так же проверьте `05-camera-report.eml`: его балл должен быть `8`.

### Таблица и запуск

Для вывода используем только две части [Rich](../../field-guide/rich/): `Console` и `Table`. `render_results()` не решает, опасно ли письмо; он только показывает готовые `EmailReport`.

```python
def render_results(reports):
    table = Table(title="Проверка писем")
    table.add_column("Файл", style="cyan")
    table.add_column("Вердикт")
    table.add_column("Балл", justify="right")
    table.add_column("Сигналы")

    # sorted() создаёт новый список отчётов в порядке убывания score.
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

    # При равных баллах max сохраняет первый отчёт из стабильного файлового порядка.
    highest = max(reports, key=lambda item: item.score)
    console.print(
        f"\n[bold]Самая рискованная версия:[/bold] {highest.filename} "
        f"({highest.verdict}, {highest.score} баллов)."
    )
```

Последний шаг связывает чтение каталога и вывод. Ошибку дела показываем кратко и завершаем программу с ненулевым кодом:

```python
def main():
    try:
        reports = analyze_directory()
    except EmailAnalysisError as exc:
        # Пользователь получает короткую причину, а ненулевой код сообщает об ошибке оболочке и CI.
        console.print(f"[bold red]Ошибка:[/bold red] {exc}")
        raise SystemExit(1) from exc

    render_results(reports)


if __name__ == "__main__":
    main()
```

## Проверка

Запустите инструмент:

```bash
python phishing_email.py
```

После отчёта запустите тесты из учебного набора:

```bash
python -m unittest discover -s tests
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

- [Установка Python](../../field-guide/install-python/) — виртуальная среда, зависимости и запуск проекта.
- [Regex](../../field-guide/regex/) — поиск URL, HTML-ссылок и слов срочности.
- [Строки `str`](../../field-guide/str/) — нормализация хостов, доменов и текстовых подписей.
- [Списки `list`](../../field-guide/list/) — списки ссылок, сигналов и отчётов.
- [dataclasses](../../field-guide/dataclasses/) — `LinkInfo`, `RiskSignal` и `EmailReport` как явные формы данных.
- [email, URL и IP](../../field-guide/email-url-ip/) — `.eml`, `urllib.parse.urlparse` и `ipaddress.ip_address`.
- [Исключения](../../field-guide/exceptions/) — отделение ошибок чтения письма от обычных проверок риска.
- [Rich](../../field-guide/rich/) — таблица отчёта, отделённая от логики анализа.
- Правила риска — небольшие функции и проверки, которые можно объяснить словами.

## Усложняем проект

1. Добавьте список доверенных доменов и отдельный сигнал для всех остальных.
2. Считайте количество разных доменов в письме.
3. Разберите заголовок `Authentication-Results`: в `01-archive-update.eml` находятся `spf=pass` и `dkim=pass`, а в `02-lockout-warning.eml` - `spf=fail` и `dkim=fail`. Добавьте осторожный сигнал только для второго письма и явно выберите его вес.
4. Выведите имена вложений рядом с сигналами. Критерий готовности: только `05-camera-report.eml` показывает `camera_report.js`, остальные письма показывают пустой список.
5. Сохраните отчёт в JSON, чтобы сравнивать результаты между запусками.
6. Добавьте режим `--file path/to/message.eml` для проверки одного письма.

Когда закончите, откройте [разбор полного решения](../phishing-email-solution/).
