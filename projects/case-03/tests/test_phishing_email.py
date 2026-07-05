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
        message_path = PROJECT_DIR / "data" / "01-archive-update.eml"
        self.assertIsInstance(load_message(message_path), EmailMessage)

    def test_lockout_warning_gets_expected_signals(self) -> None:
        report = analyze_file(PROJECT_DIR / "data" / "02-lockout-warning.eml")
        titles = {signal.title for signal in report.signals}
        self.assertEqual(report.verdict, "высокий риск")
        self.assertIn("Reply-To ведет в другой домен", titles)
        self.assertIn("Ссылка ведет на IP-адрес вместо домена", titles)
        self.assertIn("Видимый домен ссылки не совпадает с реальным", titles)

    def test_camera_report_uses_different_risk_pattern(self) -> None:
        report = analyze_file(PROJECT_DIR / "data" / "05-camera-report.eml")
        titles = {signal.title for signal in report.signals}
        self.assertEqual(report.verdict, "высокий риск")
        self.assertIn("Есть вложение с рискованным расширением", titles)
        self.assertIn("Видимый домен ссылки не совпадает с реальным", titles)
        self.assertNotIn("Ссылка ведет на IP-адрес вместо домена", titles)

    def test_safe_messages_stay_low_risk(self) -> None:
        reports = {
            report.filename: report for report in analyze_directory(PROJECT_DIR / "data")
        }
        self.assertEqual(len(reports), 6)
        for filename in [
            "01-archive-update.eml",
            "03-receipt-note.eml",
            "04-schedule-note.eml",
            "06-staff-note.eml",
        ]:
            self.assertEqual(reports[filename].verdict, "низкий риск")

        high_risk = {
            filename
            for filename, report in reports.items()
            if report.verdict == "высокий риск"
        }
        self.assertEqual(high_risk, {"02-lockout-warning.eml", "05-camera-report.eml"})
        self.assertGreater(
            reports["02-lockout-warning.eml"].score,
            reports["05-camera-report.eml"].score,
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
