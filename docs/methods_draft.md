# Methods Draft

The completed confirmatory evidence base is stored in two selected-v2 analysis files: `qwen2.5:7b-instruct` and `qwen2.5:0.5b-instruct` on the locked 120-item eval split, plus a 40-item `judgment-only baseline` sanity subset for each (internal key: `baseline_judgment_only`). The benchmark itself is built from a 150-item Moral Stories-derived candidate pool, then locked into a 30-item development split and a 120-item evaluation split after manual review.

Each item is a contrastive A/B vignette. The staged protocol is `J1 -> E -> J2`, where `J1` and `J2` ask for two forced choices with no explanation, and `E` asks for a short explanation explicitly tied to the model's earlier `J1`. The five main conditions are `baseline`, `secular_pre`, `christian_pre`, `secular_post`, and `christian_post`, with `judgment-only baseline` as a sanity condition.

Decoding is deterministic: `temperature = 0.0`, `seed = 42`, `max_judgment_tokens = 80`, and `max_explanation_tokens = 100`. The active 7B selected-v2 file is a metadata-normalized export of the locked raw 7B run, preserving decoded outputs while backfilling the current schema fields.

The key metric definitions are:

- `J1 act shift = I(j1_act_condition != j1_act_baseline)`
- `J1 heart shift = I(j1_heart_condition != j1_heart_baseline)`
- `J1→J2 act revision = I(j2_act != j1_act)`
- `J1→J2 heart revision = I(j2_heart != j1_heart)`
- `coarse explanation label = I(e_focus == motive/heart)`
- `lexical echo score = count of unique exact matches from the strict echo lexicon`
- `raw semantic explanation score = frame_echo_score + semantic_non_echo_score`
- `controlled semantic explanation score = count of non-echo semantic terms after exact stripping of all strict echo terms`

The lexical control is intentionally strict and reproducible. It uses exact lowercased phrase matching with word-boundary regex. There is no stemming, no lemmatization, and no embedding-based paraphrase expansion beyond the manual lexicon.

Primary direct contrasts are paired Christian-minus-secular comparisons:

- `christian_pre - secular_pre` on `J1 heart shift`
- `christian_pre - secular_pre` on `J1 act shift`
- `christian_post - secular_post` on raw explanation score
- `christian_post - secular_post` on controlled semantic explanation score
- `christian_post - secular_post` on act and heart revision

For each direct contrast, the analysis reports:

- paired item-level mean difference
- bootstrap confidence interval
- sign-flip permutation test
- Cohen's `dz`

Human-coded judgment–explanation consistency remains planned but incomplete. The intended rubric is `0/1/2`, but this metric is not used in the completed inferential claims.

中文提示：
- 方法部分现在把 metric definition 写成可复现形式。
- lexical echo / controlled semantic 的差别已经锁死。
- `J1→J2` 被降级成 secondary mechanism check。
