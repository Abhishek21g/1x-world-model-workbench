import json
import tempfile
import unittest
from pathlib import Path

from workbench.eval_receipt import parse_metric_lines, render_markdown


class EvalReceiptTests(unittest.TestCase):
    def test_parse_latest_metric_dict(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "eval.log"
            path.write_text("noise\n{'loss': '9.0'}\n{'loss': '8.8', 'acc': '0.03'}\n")

            self.assertEqual(parse_metric_lines(path), {"loss": "8.8", "acc": "0.03"})

    def test_render_markdown_contains_metrics(self):
        receipt = {
            "generated_at": "now",
            "command": "python eval.py",
            "checkpoint": "ckpt",
            "dataset": "val",
            "git_sha": "abc",
            "external_data": "none",
            "flops_estimate": "unknown",
            "metrics": {"loss": "8.8"},
            "notes": "ok",
        }

        rendered = render_markdown(json.loads(json.dumps(receipt)))
        self.assertIn("| `loss` | `8.8` |", rendered)


if __name__ == "__main__":
    unittest.main()
