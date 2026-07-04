# 1X Action-Conditioning Audit

Source repo: `upstream/1xgpt`

## Finding

The public `1xgpt` challenge surface includes raw action data and frames the
eventual evaluation challenge as action-conditioned, but the public GENIE
baseline is still video-only. The dataset loader constructs an `actions.bin`
path, yet the action memmap is commented out and no training/generation/eval
path consumes action tensors.

## Summary

| Check | Result |
| --- | --- |
| Dataset constructs an actions path | `yes` |
| Baseline exposes actions to callers | `no` |
| Evidence hits | `7` |
| Code action mentions, excluding argparse boilerplate | `3` |

## Evidence

| Location | Signal | Snippet | Note |
| --- | --- | --- | --- |
| `README.md:5` | Dataset advertises raw actions | `To accelerate progress in learned simulators for robots, we're announcing the 1X World Model Challenge, where the task is to predict future first-person observations of the [EVE Android](https://www.1x.tech/androids/eve). We provide over 100 hours of vector-quantized image tokens and raw actions collected from operating EVE at 1X offices, baseline world model (GENIE-style), and a frame-level MAGVIT2 autoencoder that compresses images into 16x16 tokens and decodes them back into images.` | The public challenge surface includes action data. |
| `README.md:207` | Dataset advertises raw actions | `<td><code itemprop="description">A dataset of over 100 hours of compressed image tokens + raw actions across a fleet of EVE robots.</code></td>` | The public challenge surface includes action data. |
| `README.md:32` | Evaluation challenge is action-conditioned | `- **Evaluation Challenge (upcoming)**: given a set of N policies, $\pi_1, \pi_2, ... \pi_N$, where each policy $\pi_i(a_t|z_t)$ predicts action tokens from image tokens, can you evaluate all of the policies inside a "world model" $p(z_{t+1}|z_t, a_t)$ and tell us the ranked order of which policy is the best?` | The eventual evaluation challenge is framed around action-conditioned world models. |
| `README.md:49` | GENIE baseline is video-only | `This repo provides an implementation of the spatio-temporal transformer and MaskGIT sampler as described in [Genie: Generative Interactive Environments](https://arxiv.org/abs/2402.15391). Note that this implementation only trains on video sequences, not actions (though it is trivial to add this via an additive embedding).` | The baseline explicitly omits action conditioning. |
| `README.md:113` | Rules mention prior actions | `4. For the compression challenge, submissions may only use the *prior* actions to the current prompt frame. Submissions can predict subsequent actions autoregressively to improve performance, but these actions will not be provided with the prompt.` | Actions are allowed under challenge rules, but only in a constrained way. |
| `data.py:45` | Dataset knows actions.bin exists | `for name in ["video", "segment_ids", "actions"]]` | The dataset loader constructs an actions.bin path. |
| `data.py:48` | Action memmap is commented out | `# self.actions = np.memmap(action_tokens_path, dtype=np.uint16, mode="r", shape=(self.metadata["num_images"],))` | The public loader currently drops actions instead of returning them. |

## Action Mentions In Core Code

| Location | Snippet |
| --- | --- |
| `data.py:44` | `video_tokens_path, segment_ids_path, action_tokens_path = [data_dir / f"{name}.bin"` |
| `data.py:45` | `for name in ["video", "segment_ids", "actions"]]` |
| `data.py:48` | `# self.actions = np.memmap(action_tokens_path, dtype=np.uint16, mode="r", shape=(self.metadata["num_images"],))` |

## Workbench Implication

The next useful artifact is a minimal action-path design and rollout inspector:

1. document exactly where `actions.bin` exists and where it is dropped,
2. propose an optional `include_actions` dataset flag,
3. preserve action tensors through collators,
4. expose video-only vs. action-conditioned generation/eval modes clearly,
5. use rollout inspection to compare futures from the same prompt under
   different action assumptions.
