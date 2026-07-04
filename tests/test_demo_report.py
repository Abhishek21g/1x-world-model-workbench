import tempfile
import unittest
from pathlib import Path

from workbench.demo_report import markdown_excerpt, render_page


class DemoReportTests(unittest.TestCase):
    def test_markdown_excerpt_reads_limited_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.md"
            path.write_text("a\nb\nc\n")

            self.assertEqual(markdown_excerpt(path, max_lines=2), "a\nb")

    def test_render_page_contains_artifact_link(self):
        class Args:
            audit = "missing-audit.md"
            receipt = "missing-receipt.md"
            rollout_html = "reports/demo/rollout_inspector.html"
            output = "reports/demo/index.html"

        rendered = render_page(Args())
        self.assertIn("rollout_inspector.html", rendered)
        self.assertIn("1X World Model Workbench", rendered)


if __name__ == "__main__":
    unittest.main()
