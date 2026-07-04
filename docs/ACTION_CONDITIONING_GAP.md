# Action-Conditioning Gap

## Summary

1X's public writing emphasizes action-conditioned world models: generated futures
should change when the robot proposes different actions from the same starting
observation.

The public `1xgpt` baseline is useful, but it does not currently expose that
full action-conditioned path. Its README says the GENIE implementation trains on
video sequences, not actions, and the public code comments out the action memmap
in `data.py`.

That gap is also visible in upstream issue
[`1xgpt#26`](https://github.com/1x-technologies/1xgpt/issues/26), where a user
asks how the model can generate videos from given actions when no action input is
visible in the open-source code.

## Public Evidence

- The challenge repo says the dataset includes vector-quantized image tokens and
  raw actions.
- The README's GENIE section says the implementation trains on video sequences,
  not actions.
- `data.py` builds an `actions.bin` path but leaves the action memmap commented.
- `train.py`, `genie/generate.py`, and `genie/evaluate.py` operate on image token
  sequences.
- The challenge rules say compression submissions may use prior actions to the
  current prompt frame.

## Why This Matters

Action conditioning is the bridge from video prediction to robot-policy
evaluation. Without a clear public action interface, contributors can improve
loss or sampling quality, but it is harder to study the eventual evaluation
challenge:

- counterfactual futures from the same prompt,
- policy ranking inside a learned simulator,
- failure analysis when actions and visual outcomes disagree,
- best-of-N rollout selection with physical plausibility checks.

## Minimal Public Interface To Explore

A small, non-invasive upstream proposal could define how actions would flow
through the baseline without implementing a large new model:

1. `RawTokenDataset(..., include_actions=False)` optionally returns
   `action_ids`.
2. Collators preserve `action_ids` when present.
3. `STMaskGIT` accepts an optional action embedding tensor.
4. The action embedding is added at the frame/time level before the
   spatio-temporal transformer.
5. Generation/evaluation CLIs document whether they are video-only or
   action-conditioned.

## Workbench Opportunity

This workbench can make the gap concrete without overclaiming:

- document where public actions enter the dataset,
- trace where the current baseline drops them,
- build rollout views that can compare multiple generated futures from the same
  prompt,
- add failure tags for action mismatch, object/contact errors, and impossible
  geometry,
- produce run receipts that make challenge submissions easier to inspect.

The goal is not to claim private 1X knowledge. The goal is to make the public
research surface easier to understand and extend.
