---
title: "Расследование 03. Фишинговое письмо или нет?"
description: "Читаем .eml-файлы, извлекаем факты, обрабатываем ошибки и сохраняем проверку писем в JSON."
concepts:
  - email
  - urllib.parse
  - ipaddress
  - try/except
  - словари
  - JSON
  - Rich
difficulty: "средний"
projectId: "case-03"
time: "100-130 минут"
---

<div class="case-meta">
  <p><strong>Миссия</strong> прочитать шесть `.eml`-файлов и объяснить, почему два письма требуют проверки.</p>
  <p><strong>Инструменты</strong> `email`, `get_body()`, `iter_attachments()`, `urlparse`, `ipaddress`, один regex и локальная обработка ошибок.</p>
  <p><strong>Вход</strong> письма и `data/artifacts/02-text-matches.json` из предыдущего расследования.</p>
  <p><strong>Результат</strong> таблица и `artifacts/03-mail-review.json`.</p>
</div>

<div class="materials-panel">
  <p><strong>Быстрые ссылки:</strong> <a href="../../downloads/case-03.zip">case-03.zip</a> · <a href="../phishing-email-solution/">разбор решения</a></p>
  <p><strong>Справочник:</strong> <a href="../../field-guide/email-url-ip/">email, URL и IP</a> · <a href="../../field-guide/exceptions/">исключения</a> · <a href="../../field-guide/json/">JSON</a></p>
</div>

## Что изменилось после расследования 02

Детектор текстовых совпадений сохранил общие фразы в `02-text-matches.json`. Теперь программа проверит, встречаются ли эти фразы в письмах. Совпадение показывает, что письмо повторяет фразу из материалов архива. Такая фраза может встретиться и в обычной рабочей переписке, поэтому баллы добавляют только технические правила: домены, протокол ссылки, IP-адрес и расширение вложения.

Два независимых вопроса остаются отдельными:

1. письмо связано с текущим расследованием;
2. письмо содержит технические признаки риска.

## Подготовка

Скачайте [case-03.zip](../../downloads/case-03.zip), создайте окружение Python 3.13 и установите зависимости:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

В Windows активируйте окружение командой `\.venv\Scripts\Activate.ps1`.

В папке проекта находятся:

- `phishing_email.py` — пустой стартовый файл;
- `data/*.eml` — шесть учебных писем;
- `data/artifacts/02-text-matches.json` — результат предыдущего расследования;
- `check_result.txt` — ориентиры готового отчёта.

Запустите стартовый файл:

```bash
python phishing_email.py
```

Пока программа ничего не выводит. Дальше мы последовательно добавим чтение писем, разбор ссылок, правила риска, пакетную обработку и сохранение JSON.

## Шаг 1. Добавить импорты и настройки

Откройте пустой `phishing_email.py`. Первый листинг только подключает инструменты: парсер писем, HTML-парсер, работу с IP и URL, JSON, пути и Rich.

```python
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr, parsedate_to_datetime
from html.parser import HTMLParser
import ipaddress
import json
from pathlib import Path
import re
from urllib.parse import urlparse

from rich.console import Console
from rich.table import Table
```

Импорты из `email` читают заголовки, тело и дату письма. `HTMLParser` извлекает адрес и видимую подпись HTML-ссылки. `ipaddress` отличает числовой IP от домена, а `urlparse` разбирает URL на схему, хост и порт. `json` и `Path` понадобятся при чтении контекста и сохранении результата. Два класса Rich отвечают только за финальную таблицу.

Теперь задайте корень проекта и пути. Одна и та же функция работает и в пустом студенческом файле, и в канонической версии внутри `solution/`:

```python
def default_project_dir():
    script_dir = Path(__file__).resolve().parent
    return script_dir if (script_dir / "data").exists() else script_dir.parent


PROJECT_DIR = default_project_dir()
DATA_DIR = PROJECT_DIR / "data"
CONTEXT_PATH = DATA_DIR / "artifacts" / "02-text-matches.json"
ARTIFACT_PATH = PROJECT_DIR / "artifacts" / "03-mail-review.json"
```

`script_dir` — папка текущего файла. Если рядом есть `data`, это корень распакованного проекта; иначе функция поднимается на уровень выше из `solution/`. Поэтому `PROJECT_DIR` всегда указывает на `case-03`, `DATA_DIR` — на письма, `CONTEXT_PATH` — на результат I-02, а `ARTIFACT_PATH` — на будущий JSON.

Проверьте найденные папки до чтения писем:

```python
print(DATA_DIR.name, CONTEXT_PATH.name)
```

```text
data 02-text-matches.json
```

Последний листинг шага задаёт правила анализа и создаёт исключение для ошибок одного письма:

```python

# После URL удаляются только знаки, которыми ссылка заканчивает предложение.
TRAILING_URL_CHARS = ".,;:!?)]}"
# Этот шаблон находит http/https-ссылки в обычной текстовой части письма.
URL_RE = re.compile(r"https?://[^\s<>'\"\\]+", re.IGNORECASE)

# Любая найденная фраза добавляет один общий признак срочности.
URGENT_PHRASES = (
    "срочно",
    "немедленно",
    "сегодня",
    "до конца дня",
    "последнее уведомление",
    "urgent",
    "immediately",
)
# Path.suffix вернёт одно из этих расширений вместе с точкой.
RISKY_SUFFIXES = {".exe", ".js", ".scr", ".cmd", ".bat", ".vbs", ".ps1"}

console = Console()


class EmailAnalysisError(Exception):
    """Ошибка чтения одного учебного .eml-файла."""
```

`TRAILING_URL_CHARS` содержит только знаки в конце предложения. `URL_RE` находит адреса с `http` или `https` в обычном тексте. `URGENT_PHRASES` — кортеж слов, которые создают один сигнал срочности, а `RISKY_SUFFIXES` — множество опасных расширений для быстрой проверки через `in`. `EmailAnalysisError` позволит пометить один повреждённый файл, не потеряв остальные пять.

## Шаг 2. Прочитать письмо и обработать ошибку

`BytesParser` получает исходные байты `.eml`. Этот `try/except` переводит ошибку файловой системы в понятную ошибку программы:

```python
def load_message(path):
    try:
        with path.open("rb") as file:
            message = BytesParser(policy=policy.default).parse(file)
    except OSError as exc:
        raise EmailAnalysisError(f"Cannot read {path}") from exc

    for header in ("From", "Subject"):
        if not message.get(header):
            raise EmailAnalysisError(f"{path.name}: missing {header} header")
    return message
```

Здесь `try` содержит только операцию, которая может не прочитать файл. Проверка обязательных заголовков идёт после него, поэтому причины ошибок не смешиваются.

Прочитайте одно письмо и посмотрите на объект через два знакомых заголовка:

```python
message = load_message(DATA_DIR / "02-lockout-warning.eml")
print(message["Subject"])
print(message["From"])
```

Первая строка будет `Срочно: доступ к архиву будет закрыт`, а вторая покажет отправителя. Пока `message` остаётся объектом `EmailMessage`; следующий шаг превратит его части в обычные строки и списки.

## Шаг 3. Получить текст, вложения и дату

Добавьте функции, которые переводят части `EmailMessage` в обычные строки и списки:

```python
def _body_text(message, subtype):
    # get_body() выбирает одну текстовую часть по указанному подтипу.
    part = message.get_body(preferencelist=(subtype,))
    if part is None:
        return ""
    try:
        content = part.get_content()
    except (LookupError, UnicodeDecodeError) as exc:
        # Ошибка декодирования относится к текущему письму и попадёт в его отчёт.
        raise EmailAnalysisError("Cannot decode message body") from exc
    return content if isinstance(content, str) else ""


def text_from_message(message):
    # Обе версии нужны: URL может находиться только в HTML-части письма.
    chunks = [_body_text(message, "plain"), _body_text(message, "html")]
    return "\n".join(chunk for chunk in chunks if chunk)
```

`_body_text()` просит `get_body()` выбрать один подтип. Отсутствующая часть даёт пустую строку. Для найденной части `get_content()` декодирует байты; ошибка превращается в `EmailAnalysisError`. `text_from_message()` вызывает помощник для `plain` и `html`, отбрасывает пустые строки и соединяет оставшийся текст переводом строки.

Вложения и дата — отдельные преобразования, поэтому добавьте их следующим листингом:

```python


def attachment_names(message):
    # iter_attachments() возвращает вложения без обычных текстовых частей.
    return [
        part.get_filename()
        for part in message.iter_attachments()
        if part.get_filename()
    ]


def message_time(message):
    value = message.get("Date")
    if not value:
        return ""
    try:
        return parsedate_to_datetime(str(value)).isoformat()
    except (TypeError, ValueError):
        # Исходное значение сохраняется, если учебная дата не разобралась.
        return str(value)
```

`attachment_names()` проходит только вложения и сохраняет непустые имена. `message_time()` читает заголовок `Date`: корректная дата становится ISO-строкой, отсутствующая — пустой строкой, а нестандартная сохраняется как есть. Такой отчёт остаётся сериализуемым даже при плохой дате.

Проверьте три результата на уже загруженном письме:

```python
body = text_from_message(message)
print(len(body))
print(attachment_names(message))
print(message_time(message))
```

```text
691
[]
2026-03-14T20:17:00+03:00
```

Число `691` — длина объединённого текста в символах, пустой список означает отсутствие вложений, а дата уже готова для JSON.

## Шаг 4. Подготовить домены для сравнения

Сначала добавьте проверку IP-адреса и нормализацию имени хоста:

```python
def is_ip_address(host):
    if not host:
        return False
    try:
        # ip_address() принимает IPv4 и IPv6 и отклоняет обычные доменные имена.
        ipaddress.ip_address(host.strip("[]"))
    except ValueError:
        return False
    return True


def normalize_host(host):
    # Регистр и завершающая точка не должны менять результат сравнения.
    return host.strip().strip(".").lower()


def base_domain(host):
    host = normalize_host(host)
    if not host or is_ip_address(host):
        return host
    labels = host.split(".")
    return host if len(labels) < 2 else ".".join(labels[-2:])


def domain_from_address(value):
    # parseaddr() отделяет отображаемое имя человека от адреса в угловых скобках.
    _, address = parseaddr(value or "")
    if "@" not in address:
        return ""
    return normalize_host(address.rsplit("@", 1)[1])
```

В учебных данных `base_domain()` берёт две последние части имени. В реальных адресах публичный суффикс может состоять из нескольких частей, например `co.uk`, поэтому такое правило может выделить неверный базовый домен и не заменяет Public Suffix List.

Убедитесь, что функции приводят разные записи к сопоставимым значениям:

```python
print(domain_from_address("Служба <alerts@example.org>"))
print(base_domain("support.example.org"))
print(is_ip_address("198.51.100.44"))
```

```text
example.org
example.org
True
```

Теперь домен отправителя и хост ссылки можно сравнивать одинаковым правилом, а IP-адрес получает отдельный признак риска.

## Шаг 5. Извлечь и описать ссылки

HTML-ссылка содержит два разных значения: адрес в `href` и подпись, которую видит получатель. Добавьте небольшой наследник `HTMLParser`:

```python
class _AnchorParser(HTMLParser):
    """Собирает пары (href, видимая подпись) из HTML-ссылок в атрибуте links."""

    def __init__(self):
        super().__init__()
        # links хранит пары (href, видимая подпись) в порядке появления в HTML.
        self.links = []
        # _href и _label_parts описывают ссылку, которую парсер читает сейчас.
        self._href = None
        self._label_parts = []

    def handle_starttag(self, tag, attrs):
        # Остальные HTML-теги не содержат адрес и не начинают новую ссылку.
        if tag.casefold() != "a":
            return
        # attrs приходит списком пар; словарь позволяет получить href по имени.
        href = dict(attrs).get("href", "")
        # В отчёт входят только веб-ссылки, которые затем понимает urlparse.
        if href.casefold().startswith(("http://", "https://")):
            # Подпись собирается только для текущего открытого тега <a>.
            self._href = href
            self._label_parts = []

    def handle_data(self, data):
        # Текст вложенных HTML-тегов тоже относится к подписи текущей ссылки.
        if self._href is not None:
            self._label_parts.append(data)

    def handle_endtag(self, tag):
        if tag.casefold() == "a" and self._href is not None:
            # split() и join() сводят переносы и повторные пробелы к одному пробелу.
            label = " ".join("".join(self._label_parts).split())
            self.links.append((self._href, label))
            # Сброс состояния не позволяет тексту следующего тега попасть в эту ссылку.
            self._href = None
            self._label_parts = []
```

`__init__()` создаёт итоговый список `links` и состояние одной открытой ссылки. `handle_starttag()` реагирует только на `<a>`, превращает пары атрибутов в словарь и запоминает веб-адрес. `handle_data()` собирает видимый текст, включая текст вложенных тегов. `handle_endtag()` нормализует пробелы, сохраняет пару `(href, label)` и очищает состояние перед следующей ссылкой.

Следующий листинг преобразует один URL в обычный словарь:

```python
def clean_url(raw_url):
    return raw_url.rstrip(TRAILING_URL_CHARS)


def display_host_from_label(label):
    # В учебных письмах видимый домен стоит первым словом подписи ссылки.
    token = label.strip().split(maxsplit=1)[0] if label.strip() else ""
    # Префикс // позволяет urlparse разобрать строку как домен без схемы.
    parsed = urlparse(f"//{token}")
    host = normalize_host(parsed.hostname or "")
    return host if "." in host else ""


def make_link_info(raw_url, label=""):
    # urlparse разделяет URL на схему, имя хоста, порт и остальные компоненты.
    parsed = urlparse(raw_url)
    host = normalize_host(parsed.hostname or "")
    return {
        "raw": raw_url,
        "label": label,
        "scheme": parsed.scheme.lower(),
        "host": host,
        "port": parsed.port,
        "display_host": display_host_from_label(label),
        "is_ip_host": is_ip_address(host),
    }
```

`clean_url()` убирает пунктуацию только справа. `display_host_from_label()` берёт первое слово видимой подписи и добавляет `//`, чтобы `urlparse` распознал домен без схемы. `make_link_info()` один раз разбирает настоящий адрес и сохраняет семь простых значений: исходный URL, подпись, схему, хост, порт, видимый хост и признак IP.

Теперь соберите HTML-ссылки и URL из обычного текста в один список:

```python


def extract_links(text):
    # HTMLParser сохраняет и href, и видимую подпись ссылки.
    parser = _AnchorParser()
    parser.feed(text)
    links = []
    # seen_urls не даёт добавить один URL дважды из HTML и обычного текста.
    seen_urls = set()

    for raw_url, label in parser.links:
        url = clean_url(raw_url)
        if url not in seen_urls:
            links.append(make_link_info(url, label))
            seen_urls.add(url)

    # URL_RE находит ссылки, напечатанные в обычной текстовой части письма.
    for match in URL_RE.finditer(text):
        url = clean_url(match.group(0))
        if url not in seen_urls:
            links.append(make_link_info(url))
            seen_urls.add(url)
    return links
```

`parser.feed(text)` заполняет `parser.links`. Первый цикл переносит HTML-ссылки. Второй проходит совпадения `URL_RE`, включая URL из plain-text части. Множество `seen_urls` хранит уже добавленные адреса, поэтому один и тот же `href`, который также встретился в HTML-тексте, не появится дважды.

Проверьте первую ссылку письма из шага 2:

```python
links = extract_links(body)
print(len(links))
print(links[0])
```

Обычный `print()` покажет словарь одной строкой. Ниже та же строка вручную перенесена, чтобы поля было легче читать:

```text
2
{'raw': 'http://198.51.100.44/archive-lock?ticket=DEMO-31',
 'label': 'support.example.org/archive',
 'scheme': 'http',
 'host': '198.51.100.44',
 'port': None,
 'display_host': 'support.example.org',
 'is_ip_host': True}
```

Словарь одновременно показывает настоящий IP-хост и подпись `support.example.org`. На следующем шаге это несовпадение станет объяснимым сигналом.

## Шаг 6. Оценить одну ссылку

`assess_link()` получает словарь одной ссылки и возвращает все найденные признаки. Независимые `if` нужны потому, что один URL может нарушить несколько правил одновременно.

```python
def add_signal(signals, title, points):
    # Один тип риска учитывается один раз, даже если он найден в нескольких ссылках.
    if all(signal["title"] != title for signal in signals):
        signals.append({"title": title, "points": points})


def assess_link(link, sender_domain):
    """Вернуть признаки риска для одной ссылки из результата make_link_info()."""
    # Каждый элемент signals имеет форму {"title": str, "points": int}.
    # analyze_message() объединит этот локальный список с результатами других ссылок.
    signals = []

    # URL с числовым IP вместо домена получает отдельный сигнал риска.
    if link["is_ip_host"]:
        add_signal(signals, "Ссылка ведёт на IP-адрес вместо домена", 3)

    # Схема http передаёт данные без шифрования транспортного уровня.
    if link["scheme"] == "http":
        add_signal(signals, "Ссылка использует http без шифрования", 2)

    # Подпись ссылки может показывать один домен, а href открывать другой.
    display_host = link["display_host"]
    # base_domain() сравнивает последние две части хоста; это учебное упрощение без PSL.
    if display_host and base_domain(display_host) != base_domain(link["host"]):
        add_signal(signals, "Видимый домен ссылки не совпадает с реальным", 3)

    # Для числового IP уже создан отдельный, более точный признак выше.
    if (
        sender_domain
        and link["host"]
        and not link["is_ip_host"]
        and base_domain(link["host"]) != base_domain(sender_domain)
    ):
        add_signal(signals, "Ссылка ведёт в домен, отличный от домена отправителя", 1)

    # Словарь связывает схему с её стандартным портом.
    default_port = {"http": 80, "https": 443}.get(link["scheme"])
    # Явный порт не 80 для http и не 443 для https добавляет один балл риска.
    # Отсутствующий порт даёт None и не добавляет баллы.
    if link["port"] is not None and link["port"] != default_port:
        add_signal(signals, "Ссылка использует нестандартный порт", 1)

    return signals
```

`add_signal()` проверяет заголовки уже найденных сигналов и не начисляет один тип риска дважды. `assess_link()` начинает с пустого списка и независимо проверяет IP-хост, схему, различие видимого и настоящего домена, домен отправителя и нестандартный порт. Словарь `default_port` связывает `http` с `80`, а `https` с `443`; отсутствующий порт имеет значение `None` и не создаёт сигнал.

Первая ссылка с предыдущего шага нарушает сразу три правила:

```python
sender_domain = domain_from_address(message["From"])
print(assess_link(links[0], sender_domain))
```

`print()` выводит список одной строкой; в примере элементы перенесены только для чтения:

```text
[{'title': 'Ссылка ведёт на IP-адрес вместо домена', 'points': 3},
 {'title': 'Ссылка использует http без шифрования', 'points': 2},
 {'title': 'Видимый домен ссылки не совпадает с реальным', 'points': 3}]
```

Функция вернула список словарей, а не только сумму. Благодаря этому итоговый отчёт сможет объяснить каждый начисленный балл.

## Шаг 7. Собрать отчёт одного письма

Добавьте преобразование суммы баллов в итоговую категорию:

```python
def risk_verdict(score):
    if score >= 7:
        return "высокий риск"
    if score >= 3:
        return "проверить вручную"
    return "низкий риск"
```

Пороговые проверки выполняются сверху вниз. Значение `7` или больше сразу даёт высокий риск; до второй проверки выполнение доходит только для меньшего балла. Значения от `3` до `6` требуют ручной проверки, остальные получают низкий риск.

Затем объедините заголовки, ссылки, вложения и правила в `analyze_message()`:

```python
def analyze_message(message, filename="<memory>", context_phrases=()):
    # Заголовки и тело сначала преобразуются в простые строки и словари.
    subject = str(message.get("Subject", "(без темы)"))
    sender = str(message.get("From", ""))
    sender_domain = domain_from_address(sender)
    reply_to_domain = domain_from_address(message.get("Reply-To"))
    body = text_from_message(message)
    links = extract_links(body)
    signals = []

    if reply_to_domain and base_domain(reply_to_domain) != base_domain(sender_domain):
        add_signal(signals, "Reply-To ведёт в другой домен", 2)

    searchable = f"{subject}\n{body}".casefold()
    if any(phrase in searchable for phrase in URGENT_PHRASES):
        add_signal(signals, "Есть слова срочности", 1)

    for link in links:
        # assess_link() проверяет одну ссылку; add_signal() объединяет результаты письма.
        for signal in assess_link(link, sender_domain):
            add_signal(signals, signal["title"], signal["points"])

    # Количество ссылок относится ко всему письму, а не к одному URL.
    if len(links) >= 4:
        add_signal(signals, "В письме слишком много ссылок", 1)
    # Path.suffix извлекает последнее расширение имени вложения вместе с точкой.
    names = attachment_names(message)
    if any(Path(name).suffix.casefold() in RISKY_SUFFIXES for name in names):
        add_signal(signals, "Есть вложение с рискованным расширением", 3)

    # Итоговый score равен сумме баллов уникальных признаков.
    score = sum(signal["points"] for signal in signals)
    return {
        "filename": filename,
        "occurred_at": message_time(message),
        "subject": subject,
        "sender": sender,
        "sender_domain": sender_domain,
        "links": links,
        "attachments": names,
        "signals": signals,
        "score": score,
        "verdict": risk_verdict(score),
        "related_phrases": [
            phrase for phrase in context_phrases if phrase.casefold() in searchable
        ],
        "error": "",
    }


def analyze_file(path, context_phrases=()):
    return analyze_message(load_message(path), filename=path.name, context_phrases=context_phrases)
```

`subject`, `sender` и два домена переводят заголовки в строки. `body`, `links` и `signals` создают рабочие данные анализа. Первая проверка сравнивает `Reply-To` с отправителем, вторая ищет хотя бы одну фразу срочности. Два вложенных цикла добавляют признаки каждой ссылки через `add_signal()`, поэтому одинаковое нарушение в двух URL учитывается один раз. Затем программа отдельно проверяет количество ссылок и расширения вложений.

`score` — сумма вручную назначенных баллов сработавших правил. Возвращаемый словарь сохраняет исходные факты, объясняющие сигналы, категорию и связанные фразы I-02. `analyze_file()` соединяет чтение файла с этим анализом, но не меняет правила. Веса не обучались и не калибровались на размеченных письмах, поэтому `score` объясняет категорию, но не является вероятностью фишинга.

Проверьте полный отчёт одного письма:

```python
report = analyze_message(message, filename="02-lockout-warning.eml")
print(report["score"], report["verdict"])
print(len(report["links"]), report["attachments"])
```

```text
12 высокий риск
2 []
```

Баллы `12` складываются из уникальных сигналов всего письма. Следующий шаг применит ту же функцию ко всем шести файлам.

## Шаг 8. Обработать каталог и отдельные ошибки

Сначала прочитайте общие фразы из результата расследования 02:

```python
def load_context(path=CONTEXT_PATH):
    # Контекст I-02 необязателен: без файла анализ продолжается без связанных фраз.
    if not path.exists():
        return []
    # read_text() и json.loads() превращают файл предыдущего расследования в словарь.
    data = json.loads(path.read_text(encoding="utf-8"))
    # investigation_id защищает от случайной передачи JSON с другой схемой.
    if data.get("investigation_id") != "I-02":
        raise ValueError(f"Expected I-02 artifact: {path}")
    # Стабильный finding_id не зависит от порядка выводов в JSON.
    finding = next(
        (
            item
            for item in data.get("findings", [])
            if item.get("finding_id") == "F-I02-TEXT-MATCHES"
        ),
        None,
    )
    if finding is None:
        raise ValueError(f"I-02 text-match finding is missing: {path}")
    matches = finding.get("matches", [])
    # examples разворачиваются в один список; dict.fromkeys() удаляет повторы,
    # сохраняя порядок первого появления фраз.
    return list(
        dict.fromkeys(
            phrase
            for match in matches
            for phrase in match.get("examples", [])
        )
    )
```

Если файла нет, функция возвращает пустой список: анализ писем всё равно полезен без контекста. Для существующего файла `json.loads()` создаёт словарь, проверка подтверждает I-02, а `next(..., None)` ищет конкретную запись независимо от её позиции. Последний comprehension разворачивает примеры всех совпадений, а `dict.fromkeys()` удаляет повторы с сохранением порядка.

На учебном артефакте получится шесть фраз:

```python
context_phrases = load_context()
print(len(context_phrases))
print(context_phrases[:2])
```

```text
6
['а сначала отмечает расхождение', 'а фотография без записи']
```

Эти строки нужны только для поля `related_phrases`; они не увеличивают балл риска.

Теперь добавьте пакетную обработку. `try/except` находится внутри цикла, поэтому ошибка одного файла не скрывает отчёты остальных писем:

```python
def analyze_directory(data_dir=DATA_DIR, context_path=CONTEXT_PATH):
    # Сортировка делает порядок отчётов одинаковым на разных файловых системах.
    paths = sorted(data_dir.glob("*.eml"))
    if not paths:
        raise EmailAnalysisError(f"No .eml files found in {data_dir}")
    # Фразы I-02 читаются один раз и передаются всем письмам.
    context_phrases = load_context(context_path)
    reports = []

    for path in paths:
        try:
            reports.append(analyze_file(path, context_phrases))
        except EmailAnalysisError as exc:
            # Ошибка одного файла становится отчётом и не прерывает обработку каталога.
            # Те же ключи, что у обычного отчёта, упрощают таблицу и JSON-сериализацию.
            reports.append(
                {
                    "filename": path.name,
                    "occurred_at": "",
                    "subject": "",
                    "sender": "",
                    "sender_domain": "",
                    "links": [],
                    "attachments": [],
                    "signals": [],
                    "score": 0,
                    "verdict": "ошибка чтения",
                    "related_phrases": [],
                    "error": str(exc),
                }
            )
    return reports
```

`glob("*.eml")` находит письма, а `sorted()` фиксирует их порядок. Контекст читается один раз до цикла. Внутри цикла успешный файл добавляет обычный отчёт, а `EmailAnalysisError` превращается в словарь с теми же ключами и вердиктом `ошибка чтения`. Благодаря одинаковой форме следующие функции не нуждаются в отдельной ветке для таблицы.

Проверьте короткую сводку каталога:

```python
reports = analyze_directory()
for report in reports:
    print(report["filename"], report["score"], report["verdict"])
```

```text
01-archive-update.eml 0 низкий риск
02-lockout-warning.eml 12 высокий риск
03-receipt-note.eml 0 низкий риск
04-schedule-note.eml 0 низкий риск
05-camera-report.eml 8 высокий риск
06-staff-note.eml 0 низкий риск
```

Список `reports` теперь содержит шесть однородных словарей. Из него можно отдельно выбрать важные выводы и одновременно сохранить полный журнал обработки.

## Шаг 9. Сохранить результат и вывести таблицу

`build_artifact()` отделяет два вывода с высоким риском от полных отчётов:

```python
def build_artifact(reports):
    # В findings входят только высокий риск и ошибки; reports сохраняет все письма.
    findings = []
    for report in reports:
        if report["verdict"] == "высокий риск":
            # Канонические письма получают стабильные ID; остальные нумеруются
            # в порядке reports, который уже зафиксирован сортировкой файлов.
            finding_id = {
                "02-lockout-warning.eml": "F-I03-LOCKOUT",
                "05-camera-report.eml": "F-I03-CAMERA",
            }.get(report["filename"], f"F-I03-{len(findings) + 1:02d}")
            findings.append(
                {
                    "finding_id": finding_id,
                    "kind": "high-risk-email",
                    "title": report["subject"],
                    "summary": (
                        f"{report['filename']}: {report['score']} баллов, "
                        f"{report['verdict']}."
                    ),
                    "source_file": report["filename"],
                    "occurred_at": report["occurred_at"],
                    "signals": report["signals"],
                    "limitation": (
                        "Признаки атаки описывают содержимое письма, но не доказывают "
                        "успешный вход или запуск вложения: программа не проверяет "
                        "журналы переходов, входов и запуска файлов."
                    ),
                }
            )
        elif report["error"]:
            # Ошибка чтения получает finding, чтобы следующий этап её не потерял.
            findings.append(
                {
                    "finding_id": f"F-I03-ERROR-{report['filename']}",
                    "kind": "parse-error",
                    "title": f"Не удалось прочитать {report['filename']}",
                    "summary": report["error"],
                    "source_file": report["filename"],
                }
            )
    # Фиксированный generated_at делает учебный артефакт воспроизводимым.
    # Верхний уровень также фиксирует происхождение и полный набор результатов.
    return {
        "schema_version": 1,
        "investigation_id": "I-03",
        "generated_at": "2026-03-15T06:55:00+03:00",
        "source_files": [report["filename"] for report in reports],
        "inputs": {"text_matches": "artifacts/02-text-matches.json"},
        "findings": findings,
        "reports": reports,
    }
```

`findings` начинается пустым. Цикл добавляет туда только письма высокого риска и ошибки чтения, а полный список остаётся в `reports`. Для двух канонических писем словарь задаёт постоянные ID, которые прочитает финал; дополнительное письмо получило бы ID по своему положению. Каждый высокий риск переносит заголовок, время, сигналы и ограничение: анализ содержимого не подтверждает успешный вход.

Внешний словарь фиксирует версию, дело, время, имена всех шести файлов, вход I-02, важные выводы и полные отчёты. Проверьте его форму до записи:

```python
artifact = build_artifact(reports)
print(len(artifact["reports"]))
print([item["finding_id"] for item in artifact["findings"]])
```

```text
6
['F-I03-LOCKOUT', 'F-I03-CAMERA']
```

Теперь сохраните этот словарь отдельной функцией:

```python


def save_artifact(artifact, path=ARTIFACT_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
```

`mkdir()` создаёт папку `artifacts`, если её ещё нет. `json.dumps()` превращает словарь в текст; `ensure_ascii=False` сохраняет русские буквы, `indent=2` добавляет читаемые отступы, а `"\n"` завершает файл переводом строки. `write_text()` записывает результат в UTF-8.

Добавьте таблицу и точку входа программы:

```python
def render_results(reports):
    # Колонки отделяют итоговую категорию и балл от объясняющих её признаков.
    table = Table(title="Проверка писем")
    table.add_column("Файл", style="cyan")
    table.add_column("Вердикт")
    table.add_column("Балл", justify="right")
    table.add_column("Сигналы или ошибка")

    # Письма идут по убыванию score; при равенстве сохраняется исходный порядок.
    for report in sorted(reports, key=lambda item: item["score"], reverse=True):
        # Каждый признак занимает отдельную строку внутри последней ячейки.
        details = "\n".join(
            f"{signal['title']} (+{signal['points']})"
            for signal in report["signals"]
        )
        # Последняя ячейка показывает ошибку, иначе сигналы, иначе явный fallback.
        table.add_row(
            report["filename"],
            report["verdict"],
            str(report["score"]),
            report["error"] or details or "явных сигналов нет",
        )
    console.print(table)


def main():
    reports = analyze_directory()
    render_results(reports)
    save_artifact(build_artifact(reports))
    console.print(f"[green]Отчёт сохранён:[/green] {ARTIFACT_PATH.name}")


if __name__ == "__main__":
    main()
```

`render_results()` сортирует копию списка по баллам и строит по строке на письмо. Выражение для `details` соединяет объяснения переводами строк. В последней ячейке приоритет имеет ошибка, затем сигналы, затем явная подпись об их отсутствии. `main()` один раз получает `reports`, передаёт тот же список таблице и артефакту, а затем печатает путь. Проверка `__name__` не запускает обработку при обычном импорте функций.

Запустите инструмент:

```bash
python phishing_email.py
```

Ожидаемые ключевые результаты:

- `02-lockout-warning.eml` — 12 баллов;
- `05-camera-report.eml` — 8 баллов;
- остальные четыре письма — низкий риск;
- отчёт сохранён в `artifacts/03-mail-review.json`.

В узком терминале Rich может переносить длинные названия сигналов на несколько строк. Это только оформление таблицы: точные поля, баллы и порядок записей сохраняются в JSON без переносов.

Расследование 04 проверит `investigation_id`, выберет два вывода высокого риска по их ID и сохранит их ограничения вместе с остальными уликами.

## Что мы использовали

- объект письма из стандартного модуля `email`;
- `get_body()` и `iter_attachments()` вместо ручного обхода MIME;
- один regex для обычных URL;
- словари для ссылок, сигналов и отчётов;
- отдельные `try/except` для чтения, декодирования, даты и продолжения пакетной обработки;
- JSON как результат, который использует следующая программа.

## Усложняем проект

1. Добавьте проверку `Authentication-Results`.
2. Записывайте отдельный статус для письма с некорректной датой.
3. Замените учебное выделение базового домена библиотекой Public Suffix List.
