"""scripts/errors_report.py: the daily "Errors (last 24 h)" and backend-size lines, without a network."""
import io
import sys
import unittest
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import errors_report as er  # noqa: E402


def fake(answers):
    def q(token, ref, sql):
        for key, val in answers.items():
            if key in sql:
                if isinstance(val, Exception):
                    raise val
                return val
        raise AssertionError(sql)
    return q


SIZE = {"db_bytes": 50 * 2**20, "storage_bytes": 256 * 2**20, "files": 900}


class ErrorsReport(unittest.TestCase):
    def test_lists_errors_and_sizes(self):
        md = er.build("t", "ref", fake({
            "limit 10": [{"message": "TypeError: x | `y`\n<b>z</b>", "source": "/app.js", "n": 7, "browsers": "Chrome 130 Android", "views": "explore"}],
            "kinds": [{"n": 9, "kinds": 2}],
            "pg_database_size": [SIZE]}))
        self.assertIn("## Errors (last 24 h)", md)
        self.assertIn("**9** error reports, 2 distinct", md)
        self.assertIn("| `TypeError: x / 'y' <b>z</b>` | `/app.js` | 7 |", md)   # inert: pipes and backticks neutralised
        self.assertIn("Database **50 MB** of 500 MB (10%)", md)
        self.assertIn("Moments storage **256 MB** of 1024 MB (25%, 900 files)", md)

    def test_quiet_day(self):
        md = er.build("t", "ref", fake({"limit 10": [], "kinds": [{"n": 0, "kinds": 0}], "pg_database_size": [SIZE]}))
        self.assertIn("No app errors reported in the last 24 hours.", md)

    def test_missing_view_does_not_fail(self):
        err = urllib.error.HTTPError("u", 400, "Bad Request", {}, io.BytesIO(b'{"message":"relation \\"analytics.client_errors_daily\\" does not exist"}'))
        md = er.build("t", "ref", fake({"limit 10": err, "pg_database_size": OSError("down")}))
        self.assertIn("Not available: the client_errors migration isn't applied yet.", md)
        self.assertIn("## Backend size\n\nNot available (OSError).", md)

    def test_long_text_is_cut(self):
        self.assertEqual(len(er.cell("x" * 500, 90)), 92)   # 90 characters plus the backticks
        self.assertEqual(er.cell(None), "")


if __name__ == "__main__":
    unittest.main()
