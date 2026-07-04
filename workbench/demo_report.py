#!/usr/bin/env python3
"""Build a static project demo page from the workbench artifacts."""

from __future__ import annotations

import argparse
import html
from pathlib import Path


def markdown_excerpt(path: Path, max_lines: int | None = None) -> str:
    if not path.exists():
        return f"_Missing artifact: `{path}`_"
    lines = path.read_text().splitlines()
    if max_lines is not None:
        lines = lines[:max_lines]
    return "\n".join(lines).strip()


def code_block(text: str) -> str:
    return f"<pre><code>{html.escape(text)}</code></pre>"


def render_page(args: argparse.Namespace) -> str:
    audit = markdown_excerpt(Path(args.audit), max_lines=90)
    receipt = markdown_excerpt(Path(args.receipt), max_lines=80)
    rollout_path = Path(args.rollout_html)
    rollout_link = html.escape(rollout_path.name)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>1X World Model Workbench Demo</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f5f6f2; color: #141414; }}
    header {{ padding: 42px 36px 30px; background: #111; color: white; }}
    header h1 {{ margin: 0 0 10px; font-size: clamp(30px, 6vw, 58px); line-height: 1; letter-spacing: 0; }}
    header p {{ margin: 0; max-width: 900px; font-size: 18px; line-height: 1.5; color: #e8e8e8; }}
    main {{ padding: 28px 36px 52px; max-width: 1180px; margin: 0 auto; }}
    .grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; margin: 22px 0 30px; }}
    .panel {{ background: white; border: 1px solid #d9ddd2; border-radius: 6px; padding: 18px; min-width: 0; }}
    h2 {{ margin: 0 0 12px; font-size: 22px; }}
    h3 {{ margin: 0 0 8px; font-size: 15px; color: #555; text-transform: uppercase; letter-spacing: 0; }}
    p, li {{ line-height: 1.55; }}
    pre {{ white-space: pre-wrap; overflow-wrap: anywhere; background: #161712; color: #f3f5ec; padding: 14px; border-radius: 6px; font-size: 13px; line-height: 1.45; max-height: 520px; overflow: auto; }}
    a {{ color: #0b5cad; }}
    .status {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }}
    .badge {{ display: inline-block; padding: 4px 8px; border-radius: 999px; background: #e7f0e0; color: #245323; font-size: 12px; font-weight: 700; }}
    @media (max-width: 900px) {{ .grid, .status {{ grid-template-columns: 1fr; }} header, main {{ padding-left: 18px; padding-right: 18px; }} }}
  </style>
</head>
<body>
  <header>
    <h1>1X World Model Workbench</h1>
    <p>A reproducibility layer for the public 1X world-model challenge: eval receipts, rollout inspection, and an evidence-backed audit of the public action-conditioning gap.</p>
  </header>
  <main>
    <section class="grid">
      <div class="panel">
        <h3>Upstream</h3>
        <p><span class="badge">Open PR</span></p>
        <p><a href="https://github.com/1x-technologies/1xgpt/pull/29">1xgpt#29</a> fixes the teacher-forced generation mask token path.</p>
      </div>
      <div class="panel">
        <h3>Audit</h3>
        <p>The scanner traces where public action data is described, where `actions.bin` is recognized, and where the baseline drops action tensors.</p>
      </div>
      <div class="panel">
        <h3>Demo</h3>
        <p>The rollout inspector creates a static review page for prompt/generated/ground-truth media and failure tags.</p>
        <p><a href="{rollout_link}">Open rollout inspector artifact</a></p>
      </div>
    </section>

    <section class="status">
      <div class="panel">
        <h2>Action-Conditioning Audit</h2>
        {code_block(audit)}
      </div>
      <div class="panel">
        <h2>Eval Receipt Example</h2>
        {code_block(receipt)}
      </div>
    </section>
  </main>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", required=True)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--rollout-html", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_page(args))


if __name__ == "__main__":
    main()
