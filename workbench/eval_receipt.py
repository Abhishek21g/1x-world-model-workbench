#!/usr/bin/env python3
"""Create a reproducible Markdown or JSON receipt for a 1X eval run."""

from __future__ import annotations

import argparse
import ast
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def parse_metric_lines(path: Path) -> dict[str, Any]:
    """Parse dict-like metric lines printed by genie/evaluate.py."""
    latest: dict[str, Any] = {}
    if not path.exists():
        raise FileNotFoundError(path)

    for line in path.read_text().splitlines():
        line = line.strip()
        if not (line.startswith("{") and line.endswith("}")):
            continue
        try:
            parsed = ast.literal_eval(line)
        except (SyntaxError, ValueError):
            continue
        if isinstance(parsed, dict):
            latest.update(parsed)
    return latest


def load_metrics(args: argparse.Namespace) -> dict[str, Any]:
    metrics: dict[str, Any] = {}
    if args.eval_log:
        metrics.update(parse_metric_lines(Path(args.eval_log)))
    if args.metrics_json:
        metrics.update(json.loads(args.metrics_json))
    return metrics


def render_markdown(receipt: dict[str, Any]) -> str:
    metric_rows = "\n".join(
        f"| `{key}` | `{value}` |" for key, value in sorted(receipt["metrics"].items())
    )
    if not metric_rows:
        metric_rows = "| _none parsed_ | _n/a_ |"

    return f"""# 1X Eval Receipt

Generated: `{receipt["generated_at"]}`

## Run

| Field | Value |
| --- | --- |
| Command | `{receipt["command"]}` |
| Checkpoint | `{receipt["checkpoint"]}` |
| Dataset | `{receipt["dataset"]}` |
| Git SHA | `{receipt["git_sha"]}` |
| External Data | `{receipt["external_data"]}` |
| FLOPs Estimate | `{receipt["flops_estimate"]}` |

## Metrics

| Metric | Value |
| --- | --- |
{metric_rows}

## Notes

{receipt["notes"]}
"""


def build_receipt(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": args.command,
        "checkpoint": args.checkpoint,
        "dataset": args.dataset,
        "git_sha": args.git_sha,
        "external_data": args.external_data,
        "flops_estimate": args.flops_estimate,
        "metrics": load_metrics(args),
        "notes": args.notes,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-log", help="Path to captured genie/evaluate.py stdout.")
    parser.add_argument("--metrics-json", help="Inline JSON object of extra metrics.")
    parser.add_argument("--command", required=True, help="Exact command used for the run.")
    parser.add_argument("--checkpoint", default="unknown")
    parser.add_argument("--dataset", default="unknown")
    parser.add_argument("--git-sha", default="unknown")
    parser.add_argument("--external-data", default="none declared")
    parser.add_argument("--flops-estimate", default="unknown")
    parser.add_argument("--notes", default="No additional notes.")
    parser.add_argument("--output", required=True, help="Output .md or .json path.")
    args = parser.parse_args()

    receipt = build_receipt(args)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    if output.suffix == ".json":
        output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    else:
        output.write_text(render_markdown(receipt))


if __name__ == "__main__":
    main()
