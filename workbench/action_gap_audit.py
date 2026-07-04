#!/usr/bin/env python3
"""Audit the public 1xgpt repo for action-conditioning integration points."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EvidenceQuery:
    label: str
    path: str
    needle: str
    note: str


QUERIES = [
    EvidenceQuery(
        label="Dataset advertises raw actions",
        path="README.md",
        needle="raw actions",
        note="The public challenge surface includes action data.",
    ),
    EvidenceQuery(
        label="Evaluation challenge is action-conditioned",
        path="README.md",
        needle="p(z_{t+1}|z_t, a_t)",
        note="The eventual evaluation challenge is framed around action-conditioned world models.",
    ),
    EvidenceQuery(
        label="GENIE baseline is video-only",
        path="README.md",
        needle="only trains on video sequences, not actions",
        note="The baseline explicitly omits action conditioning.",
    ),
    EvidenceQuery(
        label="Rules mention prior actions",
        path="README.md",
        needle="submissions may only use the *prior* actions",
        note="Actions are allowed under challenge rules, but only in a constrained way.",
    ),
    EvidenceQuery(
        label="Dataset knows actions.bin exists",
        path="data.py",
        needle='for name in ["video", "segment_ids", "actions"]',
        note="The dataset loader constructs an actions.bin path.",
    ),
    EvidenceQuery(
        label="Action memmap is commented out",
        path="data.py",
        needle="# self.actions = np.memmap(action_tokens_path",
        note="The public loader currently drops actions instead of returning them.",
    ),
]

CODE_PATHS = [
    "data.py",
    "train.py",
    "genie/generate.py",
    "genie/evaluate.py",
    "genie/st_mask_git.py",
]


def line_hits(repo: Path, query: EvidenceQuery) -> list[dict[str, object]]:
    path = repo / query.path
    if not path.exists():
        return []

    hits = []
    for line_no, line in enumerate(path.read_text(errors="replace").splitlines(), start=1):
        if query.needle in line:
            hits.append(
                {
                    "label": query.label,
                    "path": query.path,
                    "line": line_no,
                    "snippet": line.strip(),
                    "note": query.note,
                }
            )
    return hits


def action_mentions(repo: Path) -> list[dict[str, object]]:
    mentions = []
    for rel_path in CODE_PATHS:
        path = repo / rel_path
        if not path.exists():
            continue
        for line_no, line in enumerate(path.read_text(errors="replace").splitlines(), start=1):
            lowered = line.lower()
            if "action" in lowered or "actions" in lowered:
                mentions.append(
                    {
                        "path": rel_path,
                        "line": line_no,
                        "snippet": line.strip(),
                    }
                )
    return mentions


def build_audit(repo: Path) -> dict[str, object]:
    evidence = []
    for query in QUERIES:
        evidence.extend(line_hits(repo, query))

    mentions = action_mentions(repo)
    action_code_mentions = [
        item
        for item in mentions
        if "action=\"store_true\"" not in str(item["snippet"])
    ]

    return {
        "repo": str(repo),
        "evidence": evidence,
        "action_mentions": action_code_mentions,
        "summary": {
            "evidence_count": len(evidence),
            "action_mention_count": len(action_code_mentions),
            "baseline_exposes_actions": any(
                "self.actions = np.memmap" in str(item["snippet"]) and not str(item["snippet"]).startswith("#")
                for item in action_code_mentions
            ),
            "dataset_constructs_actions_path": any(
                item["path"] == "data.py" and "actions" in str(item["snippet"])
                for item in action_code_mentions
            ),
        },
    }


def render_markdown(audit: dict[str, object]) -> str:
    summary = audit["summary"]
    evidence = audit["evidence"]
    mentions = audit["action_mentions"]

    evidence_rows = "\n".join(
        f"| `{item['path']}:{item['line']}` | {item['label']} | `{item['snippet']}` | {item['note']} |"
        for item in evidence
    )
    mention_rows = "\n".join(
        f"| `{item['path']}:{item['line']}` | `{item['snippet']}` |" for item in mentions
    )

    if not evidence_rows:
        evidence_rows = "| _none_ | _none_ | _none_ | _none_ |"
    if not mention_rows:
        mention_rows = "| _none_ | _none_ |"

    exposes_actions = "yes" if summary["baseline_exposes_actions"] else "no"
    constructs_path = "yes" if summary["dataset_constructs_actions_path"] else "no"

    return f"""# 1X Action-Conditioning Audit

Source repo: `{audit["repo"]}`

## Finding

The public `1xgpt` challenge surface includes raw action data and frames the
eventual evaluation challenge as action-conditioned, but the public GENIE
baseline is still video-only. The dataset loader constructs an `actions.bin`
path, yet the action memmap is commented out and no training/generation/eval
path consumes action tensors.

## Summary

| Check | Result |
| --- | --- |
| Dataset constructs an actions path | `{constructs_path}` |
| Baseline exposes actions to callers | `{exposes_actions}` |
| Evidence hits | `{summary["evidence_count"]}` |
| Code action mentions, excluding argparse boilerplate | `{summary["action_mention_count"]}` |

## Evidence

| Location | Signal | Snippet | Note |
| --- | --- | --- | --- |
{evidence_rows}

## Action Mentions In Core Code

| Location | Snippet |
| --- | --- |
{mention_rows}

## Workbench Implication

The next useful artifact is a minimal action-path design and rollout inspector:

1. document exactly where `actions.bin` exists and where it is dropped,
2. propose an optional `include_actions` dataset flag,
3. preserve action tensors through collators,
4. expose video-only vs. action-conditioned generation/eval modes clearly,
5. use rollout inspection to compare futures from the same prompt under
   different action assumptions.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="Path to a local 1xgpt checkout.")
    parser.add_argument("--output", required=True, help="Output .md or .json path.")
    args = parser.parse_args()

    repo = Path(args.repo)
    audit = build_audit(repo)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    if output.suffix == ".json":
        output.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    else:
        output.write_text(render_markdown(audit))


if __name__ == "__main__":
    main()
