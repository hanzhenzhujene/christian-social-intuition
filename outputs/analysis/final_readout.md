# Christian Framing x SIM: v2 Readout

## Run Status

- Main-model v2 analysis is available at [qwen2.5_7b_instruct_eval_v2](/Users/hanzhenzhu/Desktop/Christian_Social_intuition/outputs/analysis/qwen2.5_7b_instruct_eval_v2).
- Same-family smaller-model analysis is now available at [qwen2.5_0.5b_instruct_eval_v2](/Users/hanzhenzhu/Desktop/Christian_Social_intuition/outputs/analysis/qwen2.5_0.5b_instruct_eval_v2).
- `family_audit` support is implemented and smoke-validated for `qwen2.5:0.5b-instruct` at [qwen2.5_0.5b_instruct_smoke_family_audit_v2](/Users/hanzhenzhu/Desktop/Christian_Social_intuition/outputs/analysis/qwen2.5_0.5b_instruct_smoke_family_audit_v2).

## Main Pattern in the Revised 7B Analysis

The revised v2 pipeline changes the interpretation.

- Christian-over-secular first-pass `J1` heart movement remains modest:
  - `christian_pre` heart shift vs baseline: `9.17%`
  - `secular_pre` heart shift vs baseline: `7.50%`
  - direct Christian-minus-secular estimate: `+1.67` percentage points
- Christian-over-secular first-pass act movement remains near zero:
  - direct estimate: `-0.83` percentage points
- Relative to baseline, explanation language is still more prompt-sensitive than first-pass exposed judgment.
- But under the matched secular control, the Christian-specific explanation advantage weakens sharply:
  - direct raw explanation-score contrast under post-framing: `-1.67` percentage points
  - direct lexical-controlled explanation-score contrast under post-framing: `-5.00` percentage points
  - direct dissociated explanation-shift contrast: `-0.83` percentage points

## Updated Interpretation

The cleaner current conclusion is not the old one.

The revised analysis suggests:

1. Christian wording adds only a modest increment over a secular motive-focused control on first-pass heart judgment.
2. Explanation language is highly labile relative to baseline.
3. Much of that explanation movement does not survive the matched secular control as a uniquely Christian effect.

So the stronger reviewer-resistant claim is now about stage separation and interpretive caution, not about a large Christian-specific explanation advantage.

## Same-Family Scale Comparison

The completed `qwen2.5:0.5b-instruct` run makes the scale story cleaner.

- The first-pass Christian-over-secular heart contrast does not persist at smaller scale:
  - `christian_pre` heart shift vs baseline: `0.83%`
  - `secular_pre` heart shift vs baseline: `1.67%`
  - direct Christian-minus-secular estimate: `-0.83` percentage points
- The raw post-framing explanation contrast is again not Christian-favoring:
  - direct raw explanation-score contrast: `-4.17` percentage points
- After lexical control, the smaller model shows only a small unstable residual:
  - direct controlled explanation-score contrast: `+2.50` percentage points
  - CI crosses zero and the paired test remains weak
- Sanity agreement is again perfect:
  - `1.0` act agreement
  - `1.0` heart agreement

The same-family comparison therefore points to attenuation, not reinforcement. The modest first-pass Christian increment visible in `7B` does not survive at `0.5B`, while the explanation layer remains prompt-sensitive but not stably Christian-specific.

## Remaining Work

- Run the full paraphrase-family audit if we want a completed robustness section beyond the selected-v2 comparison.
- Keep human explanation-consistency coding labeled as pending until the annotation sheet is filled.
- Use the completed appendix and direct-contrast tables in the final submission package rather than reverting to older baseline-only summaries.

## Chinese Note

这份 v2 readout 最重要的变化是：旧版“Christian framing 主要改 explanation layer”的强叙事，现在不能再直接沿用。更准确的说法是 explanation layer 本身很可变，但 Christian-specific 的那一部分在 matched secular control 下明显变弱了。 
