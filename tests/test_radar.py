import datetime as dt
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("radar", ROOT / "scripts" / "radar.py")
radar = importlib.util.module_from_spec(spec)
sys.modules["radar"] = radar
spec.loader.exec_module(radar)

TODAY = dt.date(2026, 11, 8)


def entry(**kw):
    e = {"id": "a", "repo": "o/a", "name": "A", "category": "skills", "verdict": "use",
         "what": "w", "reason": "r", "pick_if": "you need it.", "license": "MIT",
         "last_push": "2026-11-01", "archived": False}
    e.update(kw)
    return e


def data(*entries):
    return {"reviewed": "2026-11-08", "categories": {"skills": "Skills"}, "entries": list(entries)}


class RealDataTests(unittest.TestCase):
    def test_shipped_data_is_valid(self):
        self.assertEqual(radar.validate(radar.load()), [])

    def test_generated_files_are_current(self):
        self.assertEqual(radar.main(["render", "--check"]), 0)

    def test_top5_has_five(self):
        self.assertEqual(len(radar.top5_entries(radar.load())), 5)

    def test_no_use_verdict_without_license(self):
        for e in radar.load()["entries"]:
            if e["verdict"] == "use":
                self.assertNotIn(e["license"], ("none", "NOASSERTION"), e["id"])


class ValidateTests(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(radar.validate(data(entry())), [])

    def test_bad_verdict_category_repo_date(self):
        probs = radar.validate(data(entry(verdict="great", category="x", repo="bad", last_push="yesterday")))
        self.assertEqual(len(probs), 4)

    def test_missing_field(self):
        e = entry()
        del e["reason"]
        self.assertTrue(any("reason" in p for p in radar.validate(data(e))))

    def test_duplicates_and_top5(self):
        a, b = entry(top5=1), entry(id="b", repo="o/b", top5=1)
        self.assertTrue(any("rank 1" in p for p in radar.validate(data(a, b))))
        self.assertTrue(any("duplicate" in p for p in radar.validate(data(entry(), entry()))))
        self.assertTrue(any("1..5" in p for p in radar.validate(data(entry(top5=9)))))


class CompareTests(unittest.TestCase):
    live = {"status": 200, "last_push": "2026-11-05", "archived": False, "license": "MIT"}

    def test_clean(self):
        self.assertEqual(radar.compare(entry(), self.live, TODAY), [])

    def test_archived(self):
        out = radar.compare(entry(), dict(self.live, archived=True), TODAY)
        self.assertTrue(any("ARCHIVED" in f for f in out))

    def test_license_drift(self):
        out = radar.compare(entry(), dict(self.live, license="GPL-3.0"), TODAY)
        self.assertTrue(any("license changed" in f for f in out))

    def test_stale_but_not_for_avoid(self):
        old = dict(self.live, last_push="2025-01-01")
        self.assertTrue(any("no push" in f for f in radar.compare(entry(), old, TODAY)))
        self.assertEqual(radar.compare(entry(verdict="avoid"), old, TODAY), [])

    def test_missing_repo_and_unreadable(self):
        self.assertTrue(radar.compare(entry(), {"status": 404}, TODAY)[0].startswith("repository not found"))
        self.assertTrue(radar.compare(entry(), {"status": 0}, TODAY)[0].startswith("could not read"))


class LiveRowTests(unittest.TestCase):
    def test_parses_api(self):
        body = {"pushed_at": "2026-11-08T01:02:03Z", "archived": True, "license": {"spdx_id": "MIT"}}
        row = radar.live_row("o/a", fetch=lambda url, tok: (200, body))
        self.assertEqual(row, {"status": 200, "last_push": "2026-11-08", "archived": True, "license": "MIT"})

    def test_no_license_and_error(self):
        row = radar.live_row("o/a", fetch=lambda u, t: (200, {"pushed_at": "2026-01-01T00:00:00Z", "license": None}))
        self.assertEqual(row["license"], "none")
        self.assertEqual(radar.live_row("o/a", fetch=lambda u, t: (404, None)), {"status": 404})


class LinkTests(unittest.TestCase):
    def test_extract(self):
        t = "see [x](https://a.example/p). and <https://b.example/q>, https://a.example/p"
        self.assertEqual(radar.extract_links(t), ["https://a.example/p", "https://b.example/q"])

    def test_check_links(self):
        codes = {"https://ok": 200, "https://gone": 404, "https://flaky": 0}
        bad = radar.check_links(list(codes), head=codes.get)
        self.assertEqual(sorted(bad), [("https://flaky", 0), ("https://gone", 404)])


class ReportTests(unittest.TestCase):
    def test_report_counts_and_never_edits(self):
        d = data(entry(), entry(id="b", repo="o/b", name="B"))
        lives = {"a": {"status": 200, "last_push": "2026-11-05", "archived": False, "license": "MIT"},
                 "b": {"status": 200, "last_push": "2026-11-05", "archived": True, "license": "MIT"}}
        before = json.dumps(d, sort_keys=True)
        text, n = radar.build_report(d, lives, [("https://gone", 404), ("https://flaky", 429)], TODAY)
        self.assertEqual(n, 2)  # archived + one hard broken link; soft link not counted
        self.assertIn("never edits verdicts", text)
        self.assertIn("not verified", text)
        self.assertEqual(before, json.dumps(d, sort_keys=True))

    def test_all_clear_and_offline(self):
        text, n = radar.build_report(data(entry()), {}, [], TODAY)
        self.assertEqual(n, 0)
        self.assertIn("not checked", text)


class RenderTests(unittest.TestCase):
    def test_entries_and_comparison(self):
        d = data(entry(category="mcp-roslyn", facts={"language": "C#", "tools": "3|4"}))
        d["categories"] = {"mcp-roslyn": "Roslyn"}
        out = radar.render_entries(d)
        self.assertIn("### [A](https://github.com/o/a) - USE", out)
        self.assertIn("Comparison: Roslyn MCP servers", out)
        self.assertIn("3\\|4", out)
        self.assertEqual(out, radar.render_entries(d))

    def test_replace_block(self):
        t = "x\n<!-- radar:top5:start -->\nold\n<!-- radar:top5:end -->\ny"
        out = radar.replace_block(t, radar.TOP5_START, radar.TOP5_END, "NEW")
        self.assertIn("NEW", out)
        self.assertNotIn("old", out)
        with self.assertRaises(ValueError):
            radar.replace_block("none", radar.TOP5_START, radar.TOP5_END, "n")

    def test_top5_write_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "R.md"
            p.write_text("a\n<!-- radar:top5:start -->\n<!-- radar:top5:end -->\n", encoding="utf-8")
            self.assertEqual(radar.main(["top5", "--write", str(p)]), 0)
            self.assertIn("github.com/", p.read_text(encoding="utf-8"))


class CliTests(unittest.TestCase):
    def test_offline_check_writes_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "r.md"
            self.assertEqual(radar.main(["check", "--offline", "--report", str(p)]), 0)
            self.assertIn("Freshness table", p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
