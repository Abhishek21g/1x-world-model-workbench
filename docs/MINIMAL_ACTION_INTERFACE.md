# Minimal Action Interface Proposal

## Goal

Define the smallest public-code interface that would let `1xgpt` contributors
experiment with action-conditioned world modeling without disrupting the current
video-only baseline.

This is a proposal for discussion, not a claim about 1X's internal architecture.

## Constraints

- Preserve the existing default behavior.
- Do not require actions for video-only training or evaluation.
- Keep action loading optional because some generated-token directories may not
  contain `actions.bin`.
- Make the CLI mode explicit: video-only vs. action-conditioned.
- Avoid a large model rewrite as the first step.

## Proposed Dataset Change

Add an optional flag:

```py
RawTokenDataset(
    data_dir,
    window_size,
    stride=1,
    filter_interrupts=True,
    filter_overlaps=False,
    include_actions=False,
)
```

When `include_actions=False`, return the current fields:

```py
{
    "input_ids": x,
    "labels": x,
    "attention_mask": attention_mask,
}
```

When `include_actions=True`, additionally return an action sequence aligned with
the sampled frames:

```py
{
    "input_ids": x,
    "labels": x,
    "attention_mask": attention_mask,
    "action_ids": actions,
}
```

## Proposed Model Interface

Keep `STMaskGIT.forward` backward-compatible:

```py
def forward(self, input_ids, labels, action_ids=None):
    ...
```

Keep generation backward-compatible:

```py
def maskgit_generate(
    self,
    prompt_THW,
    out_t,
    action_ids=None,
    maskgit_steps=1,
    temperature=0.0,
    unmask_mode="random",
):
    ...
```

## Minimal Embedding Strategy

Start with a frame-level action embedding:

1. encode each action token or action vector into `d_model`,
2. broadcast it over spatial tokens for the corresponding frame,
3. add it to `x_TSC` before the spatio-temporal decoder.

Conceptually:

```py
x_TS = rearrange(x_THW, "B T H W -> B T (H W)")
x_TSC = self.token_embed(x_TS)

if action_ids is not None:
    action_TC = self.action_embed(action_ids)
    x_TSC = x_TSC + action_TC[:, :, None, :]

x_TSC = self.decoder(x_TSC + self.pos_embed_TSC)
```

## Evaluation Modes

The public CLI should make modes explicit:

```sh
# Existing behavior
python genie/evaluate.py --checkpoint_dir <ckpt>

# Proposed future behavior
python genie/evaluate.py --checkpoint_dir <ckpt> --include_actions
```

The receipt should record:

- `conditioning_mode: video_only | action_conditioned`
- whether actions came from `actions.bin`,
- which action horizon was provided,
- whether future actions were predicted or withheld.

## Open Questions

- What is the exact action token shape and dtype across dataset versions?
- Are actions per raw 30Hz frame, per 2Hz sampled frame, or both?
- Should compression submissions receive only prior actions, as the README
  states, while future actions must be predicted?
- Should actions be encoded discretely, continuously, or through a learned
  tokenizer?
- How should action-conditioned rollouts be scored beyond CE/LPIPS?

## First Upstream-Appropriate Step

Before implementing the model change, the safest upstream contribution would be
documentation or a tiny dataset-loader option:

1. document that the public GENIE baseline is video-only,
2. document that `actions.bin` exists but is not currently returned,
3. add `include_actions=False` to `RawTokenDataset`,
4. add a focused test using a tiny fake memmap dataset.

That would answer the public confusion in `1xgpt#26` without overreaching.

