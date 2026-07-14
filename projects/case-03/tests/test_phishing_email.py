from pathlib import Path
import json
import os
import sys
import tempfile
import unittest

PROJECT_DIR = Path(__file__).resolve().parents[1]
TEST_TARGET = os.environ.get("PYTHON_TUTORIAL_TEST_TARGET", "learner")
if TEST_TARGET not in {"learner", "solution"}:
    raise RuntimeError(f"Unknown test target: {TEST_TARGET}")
SOURCE_DIR = PROJECT_DIR if TEST_TARGET == "learner" else PROJECT_DIR / "solution"
sys.path.insert(0, str(SOURCE_DIR))

from phishing_email import (  # noqa: E402
    EmailAnalysisError,
    analyze_directory,
    analyze_file,
    assess_link,
    attachment_names,
    base_domain,
    build_artifact,
    domain_from_address,
    extract_links,
    is_ip_address,
    load_context,
    load_message,
    make_link_info,
    render_results,
    risk_verdict,
    save_artifact,
    text_from_message,
)


class PhishingEmailTests(unittest.TestCase):
    def test_domain_from_address_uses_email_domain(self):
        self.assertEqual(domain_from_address("Support <help@desk.example.org>"), "desk.example.org")
        self.assertEqual(domain_from_address("broken-address"), "")

    def test_base_domain_keeps_ip_literals(self):
        self.assertEqual(base_domain("alerts.support.example.org"), "example.org")
        self.assertEqual(base_domain("198.51.100.44"), "198.51.100.44")
        self.assertTrue(is_ip_address("198.51.100.44"))

    def test_extract_links_keeps_visible_label_domain(self):
        links = extract_links(
            '<a href="http://198.51.100.44/review">support.example.org/review</a>'
        )
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]["host"], "198.51.100.44")
        self.assertEqual(links[0]["display_host"], "support.example.org")
        self.assertTrue(links[0]["is_ip_host"])

    def test_assess_link_checks_each_url_property(self):
        # Одна ссылка одновременно проверяет IP, HTTP, подпись и явный порт.
        link = make_link_info(
            "http://198.51.100.44:8080/review",
            "support.example.org/review",
        )
        signals = assess_link(link, "mail.example.org")
        points_by_title = {signal["title"]: signal["points"] for signal in signals}

        self.assertEqual(link["port"], 8080)
        self.assertEqual(points_by_title["Ссылка ведёт на IP-адрес вместо домена"], 3)
        self.assertEqual(points_by_title["Ссылка использует http без шифрования"], 2)
        self.assertEqual(points_by_title["Видимый домен ссылки не совпадает с реальным"], 3)
        self.assertEqual(points_by_title["Ссылка использует нестандартный порт"], 1)
        # Для IP не создаётся менее точный признак несовпадения с доменом отправителя.
        self.assertNotIn(
            "Ссылка ведёт в домен, отличный от домена отправителя",
            points_by_title,
        )

    def test_assess_link_compares_domain_with_sender(self):
        link = make_link_info("https://review.example.net/report")
        signals = assess_link(link, "mail.example.org")

        self.assertEqual(
            signals,
            [
                {
                    "title": "Ссылка ведёт в домен, отличный от домена отправителя",
                    "points": 1,
                }
            ],
        )

    def test_load_message_requires_core_headers(self):
        message_path = PROJECT_DIR / "data" / "01-archive-update.eml"
        self.assertEqual(load_message(message_path).get("Subject"), "Обновление карточки архива")

    def test_lockout_warning_gets_expected_signals(self):
        report = analyze_file(PROJECT_DIR / "data" / "02-lockout-warning.eml")
        titles = {signal["title"] for signal in report["signals"]}
        self.assertEqual(report["verdict"], "высокий риск")
        self.assertEqual(report["score"], 12)
        self.assertIn("Reply-To ведёт в другой домен", titles)
        self.assertIn("Ссылка ведёт на IP-адрес вместо домена", titles)
        self.assertIn("Видимый домен ссылки не совпадает с реальным", titles)

    def test_camera_report_uses_different_risk_pattern(self):
        report = analyze_file(PROJECT_DIR / "data" / "05-camera-report.eml")
        titles = {signal["title"] for signal in report["signals"]}
        self.assertEqual(report["verdict"], "высокий риск")
        self.assertEqual(report["score"], 8)
        self.assertIn("Есть вложение с рискованным расширением", titles)
        self.assertIn("Видимый домен ссылки не совпадает с реальным", titles)
        self.assertNotIn("Ссылка ведёт на IP-адрес вместо домена", titles)

    def test_safe_messages_stay_low_risk(self):
        reports = {
            report["filename"]: report for report in analyze_directory(PROJECT_DIR / "data")
        }
        self.assertEqual(len(reports), 6)
        for filename in [
            "01-archive-update.eml",
            "03-receipt-note.eml",
            "04-schedule-note.eml",
            "06-staff-note.eml",
        ]:
            self.assertEqual(reports[filename]["verdict"], "низкий риск")

        high_risk = {
            filename
            for filename, report in reports.items()
            if report["verdict"] == "высокий риск"
        }
        self.assertEqual(high_risk, {"02-lockout-warning.eml", "05-camera-report.eml"})
        self.assertGreater(
            reports["02-lockout-warning.eml"]["score"],
            reports["05-camera-report.eml"]["score"],
        )

    def test_risk_verdict_boundaries(self):
        self.assertEqual(risk_verdict(0), "низкий риск")
        self.assertEqual(risk_verdict(3), "проверить вручную")
        self.assertEqual(risk_verdict(7), "высокий риск")

    def test_render_results_accepts_reports(self):
        render_results(analyze_directory(PROJECT_DIR / "data"))

    def test_missing_message_file_raises_case_exception(self):
        with self.assertRaises(EmailAnalysisError):
            load_message(PROJECT_DIR / "data" / "missing.eml")

    def test_standard_email_helpers_extract_body_and_attachments(self):
        message = load_message(PROJECT_DIR / "data" / "05-camera-report.eml")
        self.assertIn("ночного сигнала", text_from_message(message).casefold())
        self.assertIn("camera_report.js", attachment_names(message))

    def test_batch_records_parse_error_and_continues(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            data_dir = Path(tmp_dir)
            (data_dir / "01-good.eml").write_bytes(
                (PROJECT_DIR / "data" / "01-archive-update.eml").read_bytes()
            )
            (data_dir / "02-broken.eml").write_text(
                "Subject: Есть тема\n\nНет отправителя", encoding="utf-8"
            )
            reports = analyze_directory(data_dir, data_dir / "missing-context.json")

        self.assertEqual(len(reports), 2)
        self.assertEqual(reports[0]["verdict"], "низкий риск")
        self.assertEqual(reports[1]["verdict"], "ошибка чтения")
        self.assertIn("missing From header", reports[1]["error"])

    def test_context_finds_text_matches_by_stable_id(self):
        context = {
            "investigation_id": "I-02",
            "findings": [
                {"finding_id": "F-OTHER", "matches": []},
                {
                    "finding_id": "F-I02-TEXT-MATCHES",
                    "matches": [{"examples": ["общая фраза"]}],
                },
            ],
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "02-text-matches.json"
            path.write_text(json.dumps(context, ensure_ascii=False), encoding="utf-8")
            self.assertEqual(load_context(path), ["общая фраза"])

            context["findings"] = [{"finding_id": "F-OTHER", "matches": []}]
            path.write_text(json.dumps(context, ensure_ascii=False), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_context(path)

    def test_artifact_preserves_attack_limit(self):
        artifact = build_artifact(analyze_directory(PROJECT_DIR / "data"))
        self.assertEqual(artifact["investigation_id"], "I-03")
        self.assertEqual(
            {finding["finding_id"] for finding in artifact["findings"]},
            {"F-I03-LOCKOUT", "F-I03-CAMERA"},
        )
        self.assertTrue(all("не доказывают" in finding["limitation"] for finding in artifact["findings"]))

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "03-mail-review.json"
            save_artifact(artifact, path)
            restored = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(restored, artifact)


if __name__ == "__main__":
    unittest.main()
