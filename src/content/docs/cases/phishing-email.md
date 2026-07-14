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
- `tests/` — проверки функций и итоговых баллов;
- `check_result.txt` — ориентиры готового отчёта.

Запустите стартовый файл:

```bash
python phishing_email.py
```

Пока программа ничего не выводит. Дальше мы последовательно добавим чтение писем, разбор ссылок, правила риска, пакетную обработку и сохранение JSON.

## Шаг 1. Добавить импорты и настройки

Откройте пустой `phishing_email.py` и начните с импортов, путей и наборов правил:

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


PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
CONTEXT_PATH = DATA_DIR / "artifacts" / "02-text-matches.json"
ARTIFACT_PATH = PROJECT_DIR / "artifacts" / "03-mail-review.json"

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

Пути строятся от расположения скрипта, поэтому программа работает независимо от текущей папки терминала.

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

`get_body()` выбирает текстовую часть, а `iter_attachments()` возвращает вложения. Эти методы скрывают внутреннюю структуру MIME-контейнеров.

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

Теперь добавьте преобразование одного URL в словарь и извлечение всех ссылок:

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

`score` — сумма вручную назначенных баллов сработавших правил. Эти веса не обучались и не калибровались на размеченных письмах, поэтому `score` объясняет место письма в рейтинге, но не является вероятностью фишинга.

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
    # По контракту I-02 первый finding содержит пары текстов и примеры общих фраз.
    matches = data["findings"][0].get("matches", [])
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


def save_artifact(artifact, path=ARTIFACT_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
```

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

Запустите тесты и затем сам инструмент:

```bash
python -m unittest discover -s tests -v
python phishing_email.py
```

Ожидаемые ключевые результаты:

- `02-lockout-warning.eml` — 12 баллов;
- `05-camera-report.eml` — 8 баллов;
- остальные четыре письма — низкий риск;
- отчёт сохранён в `artifacts/03-mail-review.json`.

Расследование 04 проверит SHA-256 этого файла вместе с предыдущими отчётами и исходными материалами.

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
