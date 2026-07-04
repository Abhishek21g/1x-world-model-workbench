import tempfile
import unittest
from pathlib import Path

from workbench.action_gap_audit import build_audit, render_markdown


class ActionGapAuditTests(unittest.TestCase):
    def test_audit_finds_video_only_action_gap(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "genie").mkdir()
            (repo / "README.md").write_text(
                "raw actions\n"
                "p(z_{t+1}|z_t, a_t)\n"
                "only trains on video sequences, not actions\n"
                "submissions may only use the *prior* actions\n"
            )
            (repo / "data.py").write_text(
                'video_tokens_path, segment_ids_path, action_tokens_path = [data_dir / f"{name}.bin" '
                'for name in ["video", "segment_ids", "actions"]]\n'
                "# self.actions = np.memmap(action_tokens_path)\n"
            )
            for rel_path in ["train.py", "genie/generate.py", "genie/evaluate.py", "genie/st_mask_git.py"]:
                (repo / rel_path).write_text("")

            audit = build_audit(repo)

            self.assertEqual(audit["summary"]["evidence_count"], 6)
            self.assertTrue(audit["summary"]["dataset_constructs_actions_path"])
            self.assertFalse(audit["summary"]["baseline_exposes_actions"])
            self.assertIn("baseline is still video-only", render_markdown(audit))


if __name__ == "__main__":
    unittest.main()
