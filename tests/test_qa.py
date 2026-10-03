import contextlib
import copy
import io
import json
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

import app
from ai_sankalp.captions import estimate_cues_from_package, export_captions
from ai_sankalp.generator import LessonGenerator
from ai_sankalp.history import HistoryLog
from ai_sankalp.package import package_to_lesson
from ai_sankalp.qa import EXIT_CODES, default_report_path, run_qa, write_report
from ai_sankalp.qa.report import FAIL, NEEDS_REVIEW, PASS

ROOT = Path(__file__).resolve().parents[1]
SLUG = "arrays_in_cpp"
NOW = lambda: datetime(2026, 10, 1, 10, 0, tzinfo=timezone.utc)  # noqa: E731
APPROVAL = {
    "sme_approved": True, "sme_reviewer": "Asha Rao", "sme_approved_on": "2026-09-30", "notes": "",
    "checklist": {"pedagogy": "pass", "pacing": "pass", "readability": "pass", "brand": "pass"},
}


class QAFixture:
    """A temp project with a generated, rendered, captioned, and approved flagship lesson."""

    def __init__(self, directory: str, approved: bool = True):
        self.root = Path(directory)
        (self.root / "templates").mkdir()
        shutil.copy(ROOT / "templates" / "generated_scene.py.tmpl", self.root / "templates")
        (self.root / "assets").mkdir()
        shutil.copy(ROOT / "assets" / "ai_sankalp_logo.svg", self.root / "assets")
        self.package = json.loads((ROOT / "examples" / SLUG / "lesson_package.json").read_text(encoding="utf-8"))
        if approved:
            self.package["review_status"] = copy.deepcopy(APPROVAL)
        self.package_path = self.root / "examples" / SLUG / "lesson_package.json"
        self.save_package()
        LessonGenerator(self.root).generate(package_to_lesson(self.package), package_path=self.package_path)
        self.videos = self.root / "generated" / "videos"
        self.videos.mkdir(parents=True)
        self.video = self.videos / f"{SLUG}.mp4"
        self.video.write_bytes(b"fake mp4")
        files = export_captions(estimate_cues_from_package(self.package), self.videos, SLUG, "render")
        HistoryLog(self.root / "generated" / "history.jsonl").add(
            "render_succeeded", topic="Arrays", video=str(self.video), quality="high", voiceover=True,
            captions={"srt": str(files.srt), "vtt": str(files.vtt), "source": "render", "cue_count": files.cue_count},
        )

    def save_package(self):
        self.package_path.parent.mkdir(parents=True, exist_ok=True)
        self.package_path.write_text(json.dumps(self.package), encoding="utf-8")

    def run(self, **kwargs):
        kwargs.setdefault("slug", SLUG)
        kwargs.setdefault("probe", lambda path: 320.0)
        return run_qa(self.root, now=NOW, **kwargs)


def statuses(report):
    return {check.id: check.status for check in report.checks}


class FinalReadyTests(unittest.TestCase):
    def test_final_ready_when_everything_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            report = QAFixture(directory).run()
            self.assertEqual({check: PASS for check in statuses(report)}, statuses(report))
            self.assertTrue(report.final_ready)
            self.assertEqual(PASS, report.status)
            self.assertEqual(11, len(report.checks))

    def test_not_final_ready_without_sme_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            report = QAFixture(directory, approved=False).run()
            self.assertEqual(FAIL, statuses(report)["sme_approval"])
            self.assertEqual(NEEDS_REVIEW, statuses(report)["manual_checklist"])
            self.assertFalse(report.final_ready)
            self.assertEqual(FAIL, report.status)

    def test_tracked_fixtures_are_not_approved(self):
        for slug in ("arrays_in_cpp", "python_for_loops"):
            package = json.loads((ROOT / "examples" / slug / "lesson_package.json").read_text(encoding="utf-8"))
            self.assertFalse(package["review_status"]["sme_approved"])

    def test_invalid_approval_fields_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = QAFixture(directory)
            fixture.package["review_status"]["sme_reviewer"] = ""
            fixture.package["review_status"]["sme_approved_on"] = "30/09/2026"
            fixture.save_package()
            report = fixture.run()
            self.assertEqual(FAIL, statuses(report)["sme_approval"])
            self.assertEqual(FAIL, statuses(report)["package_schema"])
            details = next(check for check in report.checks if check.id == "package_schema").details
            self.assertTrue(any("review_status.sme_approved_on" in detail for detail in details))

    def test_approval_with_bad_date_is_not_shown_as_approved(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = QAFixture(directory)
            fixture.package["review_status"]["sme_approved_on"] = "yesterday"
            fixture.save_package()
            check = next(check for check in fixture.run().checks if check.id == "sme_approval")
            self.assertEqual(FAIL, check.status)
            self.assertNotIn("Approved by", check.message)


class FailureTests(unittest.TestCase):
    def test_missing_package_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            report = run_qa(Path(directory), slug="nothing_here", now=NOW, probe=lambda path: None)
            self.assertEqual(FAIL, statuses(report)["package_present"])
            self.assertIn("nothing_here", report.checks[0].message)
            self.assertNotIn(directory, report.checks[0].message)

    def test_missing_captions_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = QAFixture(directory)
            (fixture.videos / f"{SLUG}.vtt").unlink()
            report = fixture.run()
            self.assertEqual(FAIL, statuses(report)["captions"])
            self.assertFalse(report.final_ready)

    def test_estimated_captions_need_review_even_after_a_render(self):
        # `app.py captions` overwriting render captions must not pass as render-timed.
        with tempfile.TemporaryDirectory() as directory:
            fixture = QAFixture(directory)
            export_captions(estimate_cues_from_package(fixture.package), fixture.videos, SLUG, "estimated")
            check = next(check for check in fixture.run().checks if check.id == "captions")
            self.assertEqual(NEEDS_REVIEW, check.status)
            self.assertIn("estimated from narration text", check.details[0])

    def test_invalid_captions_fail(self):
        cases = {
            "garbage srt": lambda f: (f.videos / f"{SLUG}.srt").write_text("not captions\n", encoding="utf-8"),
            "empty srt": lambda f: (f.videos / f"{SLUG}.srt").write_text("", encoding="utf-8"),
            "vtt disagrees": lambda f: (f.videos / f"{SLUG}.vtt").write_text(
                "WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nOnly one\n", encoding="utf-8"),
        }
        for name, damage in cases.items():
            with self.subTest(case=name), tempfile.TemporaryDirectory() as directory:
                fixture = QAFixture(directory)
                damage(fixture)
                self.assertEqual(FAIL, statuses(fixture.run())["captions"])

    def test_no_history_needs_review(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = QAFixture(directory)
            (fixture.root / "generated" / "history.jsonl").unlink()
            self.assertEqual(NEEDS_REVIEW, statuses(fixture.run())["history"])

    def test_malformed_packages_still_produce_a_report(self):
        cases = {
            "assets list of strings": lambda p: p.update(assets=["x"]),
            "review_status not an object": lambda p: p.update(review_status="yes"),
            "checklist not an object": lambda p: p.update(review_status={"sme_approved": False, "checklist": "pending"}),
            "duration not a number": lambda p: p.update(duration_minutes="five"),
            "generator_compatibility not an object": lambda p: p.update(generator_compatibility="x"),
        }
        for name, mutate in cases.items():
            with self.subTest(case=name), tempfile.TemporaryDirectory() as directory:
                fixture = QAFixture(directory)
                mutate(fixture.package)
                fixture.save_package()
                report = fixture.run()
                self.assertEqual(11, len(report.checks))
                self.assertEqual(FAIL, statuses(report)["package_schema"])
                self.assertFalse(report.final_ready)
                for check in report.checks:
                    self.assertNotIn("could not run", check.message, check.id)

    def test_crashing_check_becomes_a_fail_row(self):
        from ai_sankalp import qa

        def explode(ctx):
            raise RuntimeError("boom")

        with tempfile.TemporaryDirectory() as directory:
            fixture = QAFixture(directory)
            with mock.patch.object(qa, "CHECKS", (explode,)):
                report = fixture.run()
            self.assertEqual("explode", report.checks[0].id)
            self.assertEqual(FAIL, report.checks[0].status)
            self.assertIn("RuntimeError: boom", report.checks[0].message)

    def test_silent_preview_config_is_named_in_reduced_config(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = QAFixture(directory)
            config = fixture.root / "generated" / "configs" / f"{SLUG}.json"
            data = json.loads(config.read_text(encoding="utf-8"))
            data["voiceover"]["enabled"] = False
            config.write_text(json.dumps(data), encoding="utf-8")
            check = next(check for check in fixture.run().checks if check.id == "reduced_config")
            self.assertEqual(NEEDS_REVIEW, check.status)
            self.assertIn("--no-voiceover", check.message)

    def test_generated_copy_shadowing_examples_needs_review(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = QAFixture(directory)
            stale = dict(fixture.package)
            stale.pop("review_status")
            generated = fixture.root / "generated" / "packages" / SLUG / "lesson_package.json"
            generated.parent.mkdir(parents=True)
            generated.write_text(json.dumps(stale), encoding="utf-8")
            check = fixture.run().checks[0]
            self.assertEqual(NEEDS_REVIEW, check.status)
            self.assertIn("examples/arrays_in_cpp/lesson_package.json also exists", check.message)

    def test_missing_mp4_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = QAFixture(directory)
            fixture.video.unlink()
            self.assertEqual(FAIL, statuses(fixture.run())["final_video"])

    def test_duration_far_from_plan_needs_review(self):
        with tempfile.TemporaryDirectory() as directory:
            report = QAFixture(directory).run(probe=lambda path: 72.0)
            self.assertEqual(NEEDS_REVIEW, statuses(report)["final_video"])

    def test_invalid_schema_fails_with_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = QAFixture(directory)
            del fixture.package["scenes"][3]["voiceover"]
            fixture.save_package()
            check = next(check for check in fixture.run().checks if check.id == "package_schema")
            self.assertEqual(FAIL, check.status)
            self.assertIn("scenes[3].voiceover: is required", check.details)

    def test_missing_reuse_asset_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = QAFixture(directory)
            (fixture.root / "assets" / "ai_sankalp_logo.svg").unlink()
            check = next(check for check in fixture.run().checks if check.id == "required_assets")
            self.assertEqual(FAIL, check.status)
            self.assertIn("asset_branding: ai_sankalp_logo.svg", check.details)

    def test_silent_preview_render_fails_history(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = QAFixture(directory)
            HistoryLog(fixture.root / "generated" / "history.jsonl").add(
                "render_succeeded", video=str(fixture.video), voiceover=False, captions={"source": "render"},
            )
            self.assertEqual(FAIL, statuses(fixture.run())["history"])

    def test_stale_generated_config_needs_review(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = QAFixture(directory)
            fixture.package["generator_compatibility"]["summary"][0] = "Changed after generation."
            fixture.save_package()
            self.assertEqual(NEEDS_REVIEW, statuses(fixture.run())["reduced_config"])

    def test_qa_writes_nothing_outside_report(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = QAFixture(directory)
            before = sorted(str(path) for path in fixture.root.rglob("*"))
            fixture.run()
            self.assertEqual(before, sorted(str(path) for path in fixture.root.rglob("*")))


class ReportTests(unittest.TestCase):
    def test_report_json_shape_and_text_format(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = QAFixture(directory, approved=False)
            report = fixture.run()
            path = write_report(report, default_report_path(fixture.root, SLUG))
            self.assertEqual(fixture.root / "generated" / "qa" / SLUG / "qa_report.json", path)
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(
                ["report_version", "slug", "created_at", "status", "final_ready", "summary", "inputs", "checks"], list(data),
            )
            self.assertEqual("2026-10-01T10:00:00+00:00", data["created_at"])
            self.assertEqual("examples/arrays_in_cpp/lesson_package.json", data["inputs"]["package"])
            self.assertEqual("generated/videos/arrays_in_cpp.mp4", data["inputs"]["video"])
            for check in data["checks"]:
                self.assertEqual({"id", "title", "status", "message", "fix", "details"}, set(check))
                if check["status"] != PASS:
                    self.assertTrue(check["fix"], check["id"])
            text = report.format_text()
            self.assertIn("QA report for arrays_in_cpp: FAIL", text)
            self.assertIn("Fix: Ask the SME", text)
            self.assertIn("Not final-ready.", report.summary)

    def test_cli_exit_codes(self):
        self.assertEqual({PASS: 0, FAIL: 1, NEEDS_REVIEW: 2}, EXIT_CODES)
        with tempfile.TemporaryDirectory() as directory:
            fixture = QAFixture(directory)
            for approved, expected in ((True, 0), (False, 1)):
                fixture.package["review_status"]["sme_approved"] = approved
                fixture.save_package()
                with mock.patch.object(app, "PROJECT_ROOT", fixture.root), \
                        mock.patch("ai_sankalp.qa.probe_duration", return_value=320.0), \
                        contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(expected, app.main(["qa", "--slug", SLUG]))
            fixture.package["review_status"].update(sme_approved=True)
            fixture.package["review_status"]["checklist"]["pacing"] = "needs_review"
            fixture.save_package()
            with mock.patch.object(app, "PROJECT_ROOT", fixture.root), \
                    mock.patch("ai_sankalp.qa.probe_duration", return_value=320.0), \
                    contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(2, app.main(["qa", "--package", str(fixture.package_path)]))


if __name__ == "__main__":
    unittest.main()
