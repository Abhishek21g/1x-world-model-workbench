# Public Surface Scan

## Scope

Checked public repositories under `1x-technologies` for visible world-model,
evaluation, benchmark, workbench, or challenge tooling.

## Relevant Public Repositories

| Repository | Public Description | Relevance |
| --- | --- | --- |
| `1x-technologies/1xgpt` | world modeling challenge for humanoid robots | Main public research surface for this project. |
| `1x-technologies/eve-ros2-examples` | ROS2 examples for EVE APIs | Robotics API examples, not world-model eval tooling. |
| `1x-technologies/halodi-robot-models` | Robot models in URDF format | Robot description assets, not challenge eval tooling. |
| `1x-technologies/material-tracking` | QR-based shipment tracking | Operational app, not research tooling. |

## Open Public Issue Signals

The meaningful public research questions currently cluster in `1xgpt`:

- `#26`: asks how videos can be generated from given actions when the public code
  does not expose action inputs.
- `#24`: asks about reproducing published baseline performance after training.
- `#17`: asks whether MagVIT2 fine-tuning is allowed.

## Interpretation

No public 1X repository surfaced a contributor-facing workbench for:

- eval receipts,
- rollout inspection,
- generated-vs-ground-truth review,
- public action-conditioning gap analysis.

This does not prove 1X lacks internal tooling. It only means this exact
contributor-facing layer is not visible in their public GitHub surface.

## Project Implication

The workbench should stay focused on public-challenge reproducibility, not claims
about replacing internal 1X infrastructure.

