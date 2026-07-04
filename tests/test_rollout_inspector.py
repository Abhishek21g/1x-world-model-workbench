import tempfile
import unittest
from pathlib import Path

from workbench.rollout_inspector import collect_media, load_tags


class RolloutInspectorTests(unittest.TestCase):
    def test_collect_media_filters_supported_extensions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.gif").write_text("")
            (root / "b.txt").write_text("")
            (root / "c.png").write_text("")

            self.assertEqual([p.name for p in collect_media(str(root))], ["a.gif", "c.png"])

    def test_load_tags_requires_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tags.json"
            path.write_text("[]")

            self.assertEqual(load_tags(str(path)), [])


if __name__ == "__main__":
    unittest.main()
