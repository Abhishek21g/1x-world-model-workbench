import unittest
from pathlib import Path


class SiteFilesTests(unittest.TestCase):
    def test_launch_site_has_required_copy_and_links(self):
        html = Path("site/index.html").read_text()

        self.assertIn("1X World Model Workbench", html)
        self.assertIn("A simple way to inspect 1X world-model runs", html)
        self.assertIn("https://github.com/Abhishek21g/1x-world-model-workbench", html)
        self.assertIn("../reports/demo/index.html", html)

    def test_styles_avoid_absolute_local_paths(self):
        for path in [Path("index.html"), Path("site/index.html"), Path("site/styles.css")]:
            self.assertNotIn("/Users/", path.read_text())

    def test_root_redirects_to_site(self):
        html = Path("index.html").read_text()

        self.assertIn("url=site/", html)


if __name__ == "__main__":
    unittest.main()
