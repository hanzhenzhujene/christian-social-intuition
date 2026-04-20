# Revision Plan v2

## Goal

Tighten the paper from a broad prompt-effect story into a reviewer-resistant mechanism paper about stage separation. The revised analysis asks three nested questions:

1. Does Christian framing add anything beyond a matched secular motive-focused control on first-pass `J1`?
2. If explanation language moves, how much survives after direct lexical echo is removed?
3. Does post-framing change explanation with `J1` fixed, or does it mainly create `J1 -> J2` revision pressure?

## What Changed

- Replaced the cross-architecture robustness setup with a same-family scale comparison:
  - main model: `qwen2.5:7b-instruct`
  - smaller comparison model: `qwen2.5:0.5b-instruct`
- Added run-level metadata and manifests:
  - `split`
  - `run_id`
  - `seed`
  - decoding settings
  - `frame_mode`
  - `frame_family`
  - `frame_variant_id`
  - `frame_position`
  - `frames_config_version`
- Added two frame modes:
  - `selected`
  - `family_audit`
- Added variant-aware frame configuration and lexicon blocks in [frames.yaml](../configs/frames.yaml)
- Added direct Christian-vs-secular paired contrasts with bootstrap confidence intervals, sign-flip permutation tests, effect sizes, and short interpretations.
- Added lexical-echo-controlled explanation metrics:
  - `frame_echo_score`
  - `semantic_score_raw`
  - `semantic_score_controlled`
  - `restructure_beyond_echo`
- Added stronger mechanism summaries:
  - `J1 -> J2` revision rates
  - direction counts
  - toward/away moral option
  - dissociated explanation-shift rates
- Added heterogeneity by `primary_tension_tag`.
- Added paraphrase-family audit support and family summary outputs.

## Immediate Substantive Consequence

The revised `7B` analysis is more conservative than the earlier draft. Direct matched-control comparisons still show a modest Christian-over-secular first-pass heart difference, but the explanation-layer Christian-over-secular effect becomes weak or null after the secular motive-focused control and lexical-control metrics are applied.

That means the old paper framing was too strong. The cleaner current interpretation is:

- first-pass Christian-over-secular movement exists, but it is modest
- explanation language is highly labile relative to baseline
- much of that explanation movement appears to reflect generic motive salience and rhetorical uptake rather than uniquely Christian framing

## Current Compute Status

- `qwen2.5:7b-instruct`: full locked eval re-analyzed under the new v2 pipeline at [qwen2.5_7b_instruct_eval_v2](../outputs/analysis/qwen2.5_7b_instruct_eval_v2)
- `qwen2.5:0.5b-instruct`: full selected-v2 rerun is complete at [qwen2.5_0.5b_instruct_eval_v2.jsonl](../outputs/runs/qwen2.5_0.5b_instruct_eval_v2.jsonl)
- `qwen2.5:0.5b-instruct`: family-audit smoke validation was completed locally during development, but those smoke artifacts are not part of the public release surface.

## Chinese Note

这版计划的关键不是“把故事讲得更强”，而是把 story 改成 reviewer 更难击穿的版本。现在最重要的新信息是：Christian-specific explanation effect 在 matched secular control 下明显变弱，所以论文必须诚实下调。 
