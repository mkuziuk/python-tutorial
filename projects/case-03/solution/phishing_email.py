from email import policy
from email.parser import BytesParser
from email.utils import parseaddr, parsedate_to_datetime
from html.parser import HTMLParser
import ipaddress
import json
from pathlib import Path
import re
from urllib.parse import urlparse

def default_project_dir():
    """Вернуть корень case-03 для learner-файла или файла внутри solution/."""
    script_dir = Path(__file__).resolve().parent
    return script_dir if (script_dir / "data").exists() else script_dir.parent


PROJECT_DIR = default_project_dir()
DATA_DIR = PROJECT_DIR / "data"
CONTEXT_PATH = DATA_DIR / "artifacts" / "02-text-matches.json"
ARTIFACT_PATH = PROJECT_DIR / "artifacts" / "03-mail-review.json"
TRAILING_URL_CHARS = ".,;:!?)]}"
URL_RE = re.compile(r"https?://[^\s<>'\"\\]+", re.IGNORECASE)
URGENT_PHRASES = (
    "срочно",
    "немедленно",
    "сегодня",
    "до конца дня",
    "последнее уведомление",
    "urgent",
    "immediately",
)
RISKY_SUFFIXES = {".exe", ".js", ".scr", ".cmd", ".bat", ".vbs", ".ps1"}

class EmailAnalysisError(Exception):
    """Ошибка чтения одного учебного .eml-файла."""


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


def clean_url(raw_url):
    """Убрать только завершающую пунктуацию, не меняя компоненты URL."""
    return raw_url.rstrip(TRAILING_URL_CHARS)


def is_ip_address(host):
    if not host:
        return False
    try:
        # Здесь try/except отвечает на один вопрос: является ли строка корректным IP-адресом.
        ipaddress.ip_address(host.strip("[]"))
    except ValueError:
        return False
    return True


def normalize_host(host):
    """Привести имя хоста к форме для сравнения доменов."""
    # Регистр и завершающая точка не должны менять результат сравнения.
    return host.strip().strip(".").lower()


def base_domain(host):
    """Вернуть учебный базовый домен: две последние метки имени хоста."""
    host = normalize_host(host)
    # Пустая строка и числовой IP уже являются конечной формой для сравнения.
    if not host or is_ip_address(host):
        return host
    labels = host.split(".")
    # Правило двух меток подходит учебным данным, но не учитывает составные публичные суффиксы.
    return host if len(labels) < 2 else ".".join(labels[-2:])


def domain_from_address(value):
    """Извлечь нормализованный домен или вернуть пустую строку."""
    # parseaddr() отделяет отображаемое имя человека от адреса в угловых скобках.
    _, address = parseaddr(value or "")
    # parseaddr() может вернуть отображаемый текст без части user@domain.
    if "@" not in address:
        return ""
    return normalize_host(address.rsplit("@", 1)[1])


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
    # HTMLParser сохраняет и href, и видимую подпись ссылки: они могут не совпадать.
    parser = _AnchorParser()
    parser.feed(text)
    links = []
    # seen_urls не даёт добавить один URL дважды из HTML и обычного текста.
    seen_urls = set()

    for raw_url, label in parser.links:
        # clean_url удаляет только знаки препинания после адреса.
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


def load_message(path):
    try:
        with path.open("rb") as file:
            message = BytesParser(policy=policy.default).parse(file)
    except OSError as exc:
        # Одна понятная ошибка расследования скрывает различия между отсутствующим файлом и отказом чтения.
        raise EmailAnalysisError(f"Cannot read {path}") from exc

    for header in ("From", "Subject"):
        if not message.get(header):
            raise EmailAnalysisError(f"{path.name}: missing {header} header")
    return message


def _body_text(message, subtype):
    part = message.get_body(preferencelist=(subtype,))
    if part is None:
        return ""
    try:
        content = part.get_content()
    except (LookupError, UnicodeDecodeError) as exc:
        raise EmailAnalysisError("Cannot decode message body") from exc
    return content if isinstance(content, str) else ""


def text_from_message(message):
    # get_body() выбирает текстовую часть письма; ученику не нужно вручную обходить MIME-контейнеры.
    chunks = [_body_text(message, "plain"), _body_text(message, "html")]
    return "\n".join(chunk for chunk in chunks if chunk)


def attachment_names(message):
    # iter_attachments() сразу пропускает обычные текстовые части письма.
    return [
        part.get_filename()
        for part in message.iter_attachments()
        if part.get_filename()
    ]


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


def risk_verdict(score):
    """Преобразовать сумму ручных баллов в одну из трёх категорий риска."""
    # Пороги 7 и 3 — учебные правила, а не калиброванные вероятности.
    if score >= 7:
        return "высокий риск"
    if score >= 3:
        return "проверить вручную"
    return "низкий риск"


def message_time(message):
    """Вернуть дату как ISO-строку, сохранив нестандартное исходное значение."""
    value = message.get("Date")
    # Пустая строка представляет отсутствующую дату в JSON-совместимой форме.
    if not value:
        return ""
    try:
        return parsedate_to_datetime(str(value)).isoformat()
    except (TypeError, ValueError):
        # Исходное значение сохраняется, если учебная дата не разобралась.
        return str(value)


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
        "related_phrases": [phrase for phrase in context_phrases if phrase.casefold() in searchable],
        "error": "",
    }


def analyze_file(path, context_phrases=()):
    return analyze_message(load_message(path), filename=path.name, context_phrases=context_phrases)


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
            # Те же ключи, что у обычного отчёта, упрощают вывод и JSON-сериализацию.
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
                    "summary": f"{report['filename']}: {report['score']} баллов, {report['verdict']}.",
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
            # Ошибка чтения получает собственный finding, чтобы следующий этап её не потерял.
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
    """Создать каталог назначения и записать один UTF-8 JSON-артефакт."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def render_results(reports):
    """Показать по каждому письму итог и объясняющие его признаки."""
    print("Проверка писем")
    # Письма идут по убыванию score; при равенстве сохраняется исходный порядок.
    for report in sorted(reports, key=lambda item: item["score"], reverse=True):
        print(f"{report['filename']}: {report['verdict']} (балл {report['score']})")
        if report["error"]:
            print(f"  - ошибка: {report['error']}")
        elif report["signals"]:
            for signal in report["signals"]:
                print(f"  - {signal['title']} (+{signal['points']})")
        else:
            print("  - явных сигналов нет")


def main():
    """Построить один набор reports для текста и передаваемого JSON."""
    reports = analyze_directory()
    render_results(reports)
    save_artifact(build_artifact(reports))
    print(f"Отчёт сохранён: {ARTIFACT_PATH.name}")


if __name__ == "__main__":
    main()
