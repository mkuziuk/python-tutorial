from email.message import EmailMessage
from pathlib import Path
import sys
import unittest

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR / "solution"))

from phishing_email import (  # noqa: E402
    EmailAnalysisError,
    analyze_directory,
    analyze_file,
    base_domain,
    domain_from_address,
    extract_links,
    is_ip_address,
    load_message,
    render_results,
    risk_verdict,
)


class PhishingEmailTests(unittest.TestCase):
    def test_domain_from_address_uses_email_domain(self) -> None:
        self.assertEqual(domain_from_address("Support <help@desk.example.org>"), "desk.example.org")
        self.assertEqual(domain_from_address("broken-address"), "")

    def test_base_domain_keeps_ip_literals(self) -> None:
        self.assertEqual(base_domain("alerts.support.example.org"), "example.org")
        self.assertEqual(base_domain("198.51.100.44"), "198.51.100.44")
        self.assertTrue(is_ip_address("198.51.100.44"))

    def test_extract_links_keeps_visible_label_domain(self) -> None:
        links = extract_links(
            '<a href="http://198.51.100.44/review">support.example.org/review</a>'
        )
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0].host, "198.51.100.44")
        self.assertEqual(links[0].display_host, "support.example.org")
        self.assertTrue(links[0].is_ip_host)

    def test_load_message_requires_core_headers(self) -> None:
        message_path = PROJECT_DIR / "data" / "01-team-update.eml"
        self.assertIsInstance(load_message(message_path), EmailMessage)

    def test_high_risk_message_gets_expected_signals(self) -> None:
        report = analyze_file(PROJECT_DIR / "data" / "02-account-review.eml")
        titles = {signal.title for signal in report.signals}
        self.assertEqual(report.verdict, "высокий риск")
        self.assertIn("Reply-To ведет в другой домен", titles)
        self.assertIn("Ссылка ведет на IP-адрес вместо домена", titles)
        self.assertIn("Видимый домен ссылки не совпадает с реальным", titles)

    def test_safe_messages_stay_low_risk(self) -> None:
        reports = {
            report.filename: report for report in analyze_directory(PROJECT_DIR / "data")
        }
        self.assertEqual(reports["01-team-update.eml"].verdict, "низкий риск")
        self.assertEqual(reports["03-invoice-note.eml"].verdict, "низкий риск")
        self.assertEqual(reports["04-calendar-mix.eml"].verdict, "проверить вручную")
        self.assertGreater(
            reports["02-account-review.eml"].score,
            reports["04-calendar-mix.eml"].score,
        )

    def test_risk_verdict_boundaries(self) -> None:
        self.assertEqual(risk_verdict(0), "низкий риск")
        self.assertEqual(risk_verdict(3), "проверить вручную")
        self.assertEqual(risk_verdict(7), "высокий риск")

    def test_render_results_accepts_reports(self) -> None:
        render_results(analyze_directory(PROJECT_DIR / "data"))

    def test_missing_message_file_raises_case_exception(self) -> None:
        with self.assertRaises(EmailAnalysisError):
            load_message(PROJECT_DIR / "data" / "missing.eml")


if __name__ == "__main__":
    unittest.main()
