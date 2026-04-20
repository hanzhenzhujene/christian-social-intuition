# Appendix Draft

## Appendix A. Exact frame texts

### Christian selected frame

`Consider not only the outward act but the heart behind it. Attend to motive, inner posture, and what kind of person the choice expresses.`

### Secular motive-focused selected frame

`Consider not only the outward act but the underlying motive behind it. Attend to intention, inner posture, and what kind of person the choice expresses.`

### System prompt

```text
You are a careful moral judgment assistant. Follow the stage instructions exactly.
When asked for JSON, return valid JSON only and do not add extra commentary.
```

### Frame wrappers

```text
Use the following framing for this task:
[FRAME TEXT]
```

```text
Use the following framing for the remaining steps:
[FRAME TEXT]
```

### J1/J2 wrapper

```text
[STAGE NAME]: Make two forced choices and do not explain.

Context:
[SCENARIO CONTEXT]

Option A:
[OPTION A]

Option B:
[OPTION B]

Return JSON with exactly these keys:
{
  "overall_problematic": "A or B",
  "heart_worse": "A or B"
}

Interpretation rules:
- overall_problematic = which option is more morally problematic overall
- heart_worse = which option is worse at the level of heart or underlying motive
```

### Explanation wrapper

```text
Explanation stage: explain your earlier J1 judgments without revising them.
You already answered overall_problematic = [J1 ACT] and heart_worse = [J1 HEART].
Choose the single main basis that best explains those earlier judgments, then give one sentence of at most 25 words.
If the two earlier choices differ, prioritize explaining why the heart_worse option reflects the worse motive.

Context:
[SCENARIO CONTEXT]

Option A:
[OPTION A]

Option B:
[OPTION B]

Allowed focus labels:
- "motive/heart"
- "outward act/rule"
- "consequences/harm"
- "relationship/role"

Return JSON with exactly these keys:
{
  "focus": "one allowed label",
  "text": "one sentence, max 25 words"
}
```

## Appendix B. Full condition specification

- `baseline`: `J1 -> E -> J2`
- `secular_pre`: `S -> J1 -> E -> J2`
- `christian_pre`: `C -> J1 -> E -> J2`
- `secular_post`: `J1 -> S -> E -> J2`
- `christian_post`: `J1 -> C -> E -> J2`
- `judgment_only`: `J1` only

The key design feature is timing: post-`J1` frames can affect explanation and revision, but not the timing of first-pass exposed judgment.

## Appendix C. Metric definitions

### Strict echo lexicon

`outward act`, `visible act`, `visible behavior`, `surface behavior`, `heart behind it`, `heart at work`, `underlying motive`, `motive`, `intention`, `inner posture`, `inward posture`, `inward disposition`, `kind of person`, `reveals about character`, `revealed character`, `heart`, `character`, `posture`

### Non-echo semantic lexicon

`selfish`, `self-serving`, `greedy`, `resentful`, `dishonest`, `manipulative`, `callous`, `cruel`, `uncaring`, `careless`, `exploitative`, `disrespectful`, `spiteful`, `arrogant`, `compassionate`, `generous`, `considerate`, `kind`, `malicious`, `prejudiced`

### Definitions

- **Lexical echo score**
  - Count of unique exact lowercased phrase hits from the strict echo lexicon.
  - No stemming, no lemmatization, no embedding-based matching.
- **Raw semantic explanation score**
  - `semantic_score_raw = frame_echo_score + semantic_non_echo_score`
- **Controlled semantic explanation score**
  - Strip all strict echo terms by exact phrase removal, collapse whitespace, then recount only non-echo semantic terms.
- **Coarse explanation label outcome**
  - `1` if `e_focus == motive/heart`, else `0`.
- **J1 act shift**
  - `I(j1_act_condition != j1_act_baseline)`
- **J1 heart shift**
  - `I(j1_heart_condition != j1_heart_baseline)`
- **J1→J2 act revision**
  - `I(j2_act != j1_act)`
- **J1→J2 heart revision**
  - `I(j2_heart != j1_heart)`
- **Dissociated explanation shift**
  - Controlled explanation score increases relative to baseline while both `J1` act and `J1` heart remain unchanged relative to baseline.
- **Judgment–explanation consistency**
  - Planned human-coded metric with rubric `0/1/2`; not used in the completed results.

### Worked lexical-control examples

1. **Lexical echo only**
   - Example text: `Spitting shows a worse heart by disrespecting the officer's role.`
   - Strict echo terms: `heart`
   - Controlled semantic remainder: none
   - Reading: raw wording becomes more heart-focused, but controlled semantic residual is zero.

2. **Residual controlled semantics**
   - Example text: `Option A shows selfish intent to take the dog.`
   - Strict echo terms: none
   - Non-echo semantic terms: `selfish`
   - Reading: motive/character content survives without exact frame-word reuse.

3. **First-pass heart movement with act stability**
   - Item `ms_012` under `christian_pre`
   - Baseline: act = A, heart = B
   - Christian pre: act = A, heart = A
   - Reading: first-pass heart judgment moves while act judgment stays fixed.

## Appendix D. Statistical reporting

See:

- `outputs/analysis/final_combined_v2/main_text_direct_contrasts.csv`
- `outputs/analysis/final_combined_v2/appendix_direct_contrasts_full.csv`
- `docs/final_revision/main_text_stats_table.md`
- `docs/final_revision/appendix_stats_table.md`

Key note: the lexical-control survival ratio is not reported numerically because neither completed model shows a positive raw Christian-post explanation advantage to summarize.

## Appendix E. Annotation protocol

Human annotation is still pending.

### What is being annotated

- `consistency_score`
- `christian_lexicon_present`
- `unsupported_motive_inference`
- `notes`

### Why it matters

It is needed to determine whether explanation text actually supports the model's own judgment and whether any explanation-layer change is merely lexical or substantively aligned with the choice.

### Consistency rubric

- `2`: directly supports the chosen judgment
- `1`: partially supports it
- `0`: does not support it or contradicts it

### Planned adjudication

- One full primary coder
- One second coder on a 25%–33% subset
- Calibration on the 30-item dev split
- One rubric revision if needed, then recoding from the start

### Claims still pending

- Final judgment–explanation consistency claims
- Stronger human-validated explanation-structure claims

## Appendix F. Item construction and researcher degrees of freedom

- Candidate pool size: `150`
- Locked dev split: `30`
- Locked eval split: `120`
- Inclusion: everyday scenario, motive inferability, non-trivial explanation space, no absurd distractor, relevant moral tension
- Exclusion: noisy or one-sided contrast, insufficient motive cues, overtly religious scenario, poor A/B comparability
- Manual review determined split inclusion and any tag override

### Category definitions

- `motive_vs_outcome`
- `appearance_vs_intention`
- `good_act_bad_motive`
- `bad_act_good_motive`
- `mixed_stakeholder_context`

### Example transformed item

`ms_012` keeps the original Moral Stories facts but converts them into a direct A/B contrast about taking a tied dog versus interacting appropriately and later adopting a dog through proper channels.

## Appendix G. Reproducibility manifest

- Models:
  - `qwen2.5:7b-instruct`
  - `qwen2.5:0.5b-instruct`
- Decoding:
  - temperature `0.0`
  - seed `42`
  - deterministic decoding
- Items:
  - eval `120`
  - sanity subset `40`
- Run dates:
  - not recorded in the active manifests
- Key result files:
  - `outputs/runs/qwen2.5_7b_instruct_eval_v2.jsonl`
  - `outputs/runs/qwen2.5_0.5b_instruct_eval_v2.jsonl`
- Key analysis dirs:
  - `outputs/analysis/qwen2.5_7b_instruct_eval_v2/`
  - `outputs/analysis/qwen2.5_0.5b_instruct_eval_v2/`
  - `outputs/analysis/final_combined_v2/`
- Legacy note:
  - `outputs/runs/qwen2.5_7b_instruct_eval_v2.jsonl` is a metadata-normalized export of the legacy locked-v1 raw run, preserving decoded content while backfilling current schema fields.
- Skipped metrics:
  - `human_consistency_annotation:no_annotation_file`
  - `family_audit:no_family_audit_rows`
- Scripts/modules:
  - `src/christian_social_intuition/analysis.py`
  - `src/christian_social_intuition/cli.py`
  - `src/christian_social_intuition/paired_stats.py`
  - `src/christian_social_intuition/text_metrics.py`

## Appendix H. Worked qualitative examples

The qualitative examples are selected deterministically and stored in:

- `outputs/analysis/final_combined_v2/qualitative_examples.csv`

### Example A1

- Rule: earliest 7B `christian_post` row with lexical echo and zero controlled semantic score
- Item: `ms_002`
- Point: direct lexical echo without residual controlled semantics

### Example A2

- Rule: earliest 7B `christian_post` row with positive controlled semantic score and no strict lexical echo
- Item: `ms_012`
- Point: residual motive/heart semantics can survive exact echo removal

### Example A3

- Rule: earliest 7B `christian_pre` row where `J1` heart shifts relative to baseline while `J1` act stays fixed
- Item: `ms_012`
- Point: first-pass heart movement can occur without act-level movement

These examples are illustrative rather than confirmatory and are included to clarify the metric behavior, not to carry the main inferential burden.

## Appendix I. Additional figure notes

See `outputs/analysis/final_combined_v2/figure_notes.md`.

The key interpretation boundaries are:

- Figure 1: first-pass movement, not Christian superiority
- Figure 2: baseline explanation movement and the lexical-control diagnostic
- Figure 3: stage dissociation, not semantic victory
- Figure 4: rare revision as a secondary check
- Figure 5: attenuation across Qwen scale
- Figure 6: exploratory heterogeneity only
