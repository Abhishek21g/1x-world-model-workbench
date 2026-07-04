# 1X World Model Workbench

Private workbench for studying the public
[`1x-technologies/1xgpt`](https://github.com/1x-technologies/1xgpt)
challenge repo and building small, reproducible tooling around robot
world-model evaluation.

This is not a replacement for 1X's models. The goal is narrower:

- make challenge/eval runs easier to document,
- inspect generated-vs-ground-truth rollouts,
- map the public action-conditioning gap,
- contribute small verified fixes upstream before building larger artifacts.

## Current Upstream PR

Draft PR opened against `1x-technologies/1xgpt`:

- [`#29 Fix teacher-forced generation mask token`](https://github.com/1x-technologies/1xgpt/pull/29)

## Tools

Audit the local upstream checkout for action-conditioning evidence:

```sh
python3 workbench/action_gap_audit.py \
  --repo upstream/1xgpt \
  --output reports/ACTION_CONDITIONING_AUDIT.md
```

Create a reproducible eval receipt from a saved eval log:

```sh
python3 workbench/eval_receipt.py \
  --eval-log examples/sample_eval.log \
  --command "python genie/evaluate.py --checkpoint_dir 1x-technologies/GENIE_138M --maskgit_steps 2" \
  --checkpoint 1x-technologies/GENIE_138M \
  --dataset data/val_v1.1 \
  --git-sha unknown \
  --output outputs/receipt.md
```

Build a static rollout-inspection page from image/GIF directories:

```sh
python3 workbench/rollout_inspector.py \
  --prompt-dir examples/rollout_demo/prompt \
  --generated-dir examples/rollout_demo/generated \
  --ground-truth-dir examples/rollout_demo/ground_truth \
  --tags examples/failure_tags.json \
  --title "1X rollout smoke inspection" \
  --output outputs/rollout_inspector.html
```

Build the combined demo page:

```sh
python3 workbench/demo_report.py \
  --audit reports/ACTION_CONDITIONING_AUDIT.md \
  --receipt reports/demo/receipt.md \
  --rollout-html reports/demo/rollout_inspector.html \
  --output reports/demo/index.html
```

## Reports

- [`docs/ACTION_CONDITIONING_GAP.md`](docs/ACTION_CONDITIONING_GAP.md)
- [`reports/ACTION_CONDITIONING_AUDIT.md`](reports/ACTION_CONDITIONING_AUDIT.md)
- [`reports/demo/index.html`](reports/demo/index.html)

## Local-Only Files

Agent scaffolding and private planning notes are intentionally ignored:

- `.claude/`
- `.codex/`
- `agent/`
- `AGENTS.md`
- `CLAUDE.md`

They can remain on the local machine without appearing in the GitHub repo.
