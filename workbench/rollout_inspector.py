#!/usr/bin/env python3
"""Build a static generated-vs-ground-truth rollout inspection page."""

from __future__ import annotations

import argparse
import html
import json
import os
from pathlib import Path


IMAGE_EXTENSIONS = {".gif", ".jpg", ".jpeg", ".png", ".svg", ".webp"}


def collect_media(directory: str | None) -> list[Path]:
    if not directory:
        return []
    root = Path(directory)
    if not root.exists():
        raise FileNotFoundError(root)
    return sorted(path for path in root.iterdir() if path.suffix.lower() in IMAGE_EXTENSIONS)


def load_tags(path: str | None) -> list[dict[str, str]]:
    if not path:
        return []
    data = json.loads(Path(path).read_text())
    if not isinstance(data, list):
        raise ValueError("tags file must contain a list")
    return data


def rel(path: Path, output: Path) -> str:
    return os.path.relpath(path.resolve(), output.parent.resolve())


def render_column(title: str, media: list[Path], output: Path) -> str:
    cards = []
    for item in media:
        src = html.escape(rel(item, output))
        label = html.escape(item.name)
        cards.append(f'<figure><img src="{src}" alt="{label}"><figcaption>{label}</figcaption></figure>')
    if not cards:
        cards.append('<p class="empty">No media supplied.</p>')
    return f'<section><h2>{html.escape(title)}</h2>{"".join(cards)}</section>'


def render_tags(tags: list[dict[str, str]]) -> str:
    if not tags:
        return '<p class="empty">No failure tags supplied.</p>'
    rows = []
    for tag in tags:
        frame = html.escape(str(tag.get("frame", "")))
        label = html.escape(str(tag.get("label", "")))
        note = html.escape(str(tag.get("note", "")))
        rows.append(f"<tr><td>{frame}</td><td>{label}</td><td>{note}</td></tr>")
    return (
        "<table><thead><tr><th>Frame</th><th>Tag</th><th>Note</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def render_page(args: argparse.Namespace, output: Path) -> str:
    prompt = collect_media(args.prompt_dir)
    generated = collect_media(args.generated_dir)
    ground_truth = collect_media(args.ground_truth_dir)
    tags = load_tags(args.tags)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(args.title)}</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #151515; background: #f7f7f4; }}
    header {{ padding: 28px 32px 18px; border-bottom: 1px solid #ddd; background: #fff; }}
    h1 {{ margin: 0; font-size: 28px; }}
    main {{ padding: 24px 32px 40px; }}
    .grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; align-items: start; }}
    section {{ min-width: 0; }}
    h2 {{ font-size: 15px; text-transform: uppercase; letter-spacing: 0; color: #555; }}
    figure {{ margin: 0 0 14px; padding: 10px; background: #fff; border: 1px solid #ddd; border-radius: 6px; }}
    img {{ display: block; width: 100%; height: auto; border-radius: 4px; background: #eee; }}
    figcaption {{ margin-top: 8px; font-size: 12px; color: #666; overflow-wrap: anywhere; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #ddd; }}
    th, td {{ padding: 10px; border-bottom: 1px solid #e6e6e6; text-align: left; vertical-align: top; }}
    .failures {{ margin-top: 28px; }}
    .empty {{ color: #777; font-style: italic; }}
    @media (max-width: 850px) {{ .grid {{ grid-template-columns: 1fr; }} main, header {{ padding-left: 18px; padding-right: 18px; }} }}
  </style>
</head>
<body>
  <header>
    <h1>{html.escape(args.title)}</h1>
  </header>
  <main>
    <div class="grid">
      {render_column("Prompt", prompt, output)}
      {render_column("Generated", generated, output)}
      {render_column("Ground Truth", ground_truth, output)}
    </div>
    <section class="failures">
      <h2>Failure Tags</h2>
      {render_tags(tags)}
    </section>
  </main>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt-dir")
    parser.add_argument("--generated-dir")
    parser.add_argument("--ground-truth-dir")
    parser.add_argument("--tags")
    parser.add_argument("--title", default="1X Rollout Inspection")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_page(args, output))


if __name__ == "__main__":
    main()
