# Reviewer Risk Memo

## Top Risks and Responses

### 1. "You only compared prompt conditions to baseline, not to the matched secular control."

Response:
- The revised pipeline now reports direct Christian-vs-secular paired contrasts in [direct_control_contrasts.csv](/Users/hanzhenzhu/Desktop/Christian_Social_intuition/outputs/analysis/qwen2.5_7b_instruct_eval_v2/direct_control_contrasts.csv).
- Every direct contrast includes:
  - paired item-level estimate
  - bootstrap confidence interval
  - sign-flip permutation test
  - paired effect size (`Cohen's dz`)
  - short interpretation

### 2. "The explanation effect may just be lexical priming from the Christian prompt."

Response:
- The explanation layer is now decomposed into:
  - `frame_echo_score`
  - `semantic_score_raw`
  - `semantic_score_controlled`
  - `restructure_beyond_echo`
- The central result is no longer allowed to rest on raw lexical uptake alone.
- In the current `7B` v2 analysis, the Christian-over-secular explanation advantage weakens substantially after lexical control. This weakens the original stronger narrative, and the paper should say so explicitly.

### 3. "You claim a mechanism, but the staged design is underused."

Response:
- The revised analysis now separates:
  - `J1` first-pass shift
  - explanation-layer movement
  - `J1 -> J2` revision
  - dissociated explanation shifts with `J1` fixed
- This directly addresses whether post-framing changes explanation without rewriting first-pass judgment.

### 4. "Your robustness comparison across architectures is hard to interpret."

Response:
- The paper no longer uses the earlier cross-architecture robustness comparison.
- The new comparison is same-family scale:
  - `qwen2.5:7b-instruct`
  - `qwen2.5:0.5b-instruct`
- This isolates scale within Qwen rather than conflating scale and architecture.

### 5. "The result may depend on one exact Christian string."

Response:
- The runner now supports `family_audit` mode with stable frame variant IDs.
- Family-audit manifests and summary outputs are implemented.
- Full family reruns are optional for this revision cycle, but the code path, config structure, and smoke validation are already in place.

### 6. "Heterogeneity could be cherry-picked."

Response:
- Effects are now reported by the locked `primary_tension_tag` categories across the full evaluation set.
- The paper should label these heterogeneity slices as exploratory unless per-tag counts are large enough.

### 7. "Nulls are being hidden."

Response:
- The revised `7B` analysis actually weakens the older story:
  - Christian-over-secular first-pass heart shift is modest
  - Christian-over-secular explanation contrasts become weak or negative after matched-control and lexical-control analysis
- The revision should keep those null or attenuated findings visible, not bury them.

## What the Paper Should Claim Now

The safest high-level claim is:

- first-pass Christian-over-secular movement exists but is modest
- explanation language is more labile than first-pass judgment relative to baseline
- however, much of the explanation-layer movement does not survive the matched secular control as a uniquely Christian effect

That claim is less flashy, but much harder for a reviewer to knock down.

## Chinese Note

最关键的 reviewer 风险不是“效果太弱”，而是“论文还在沿用一个被新分析削弱了的旧故事”。现在最需要的是让 paper 正面承认：Christian-specific explanation advantage 并没有在 matched-control 下稳稳站住。 
