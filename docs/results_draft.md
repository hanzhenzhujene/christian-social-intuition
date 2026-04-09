# Results Draft

The sanity check passed cleanly. Both completed Qwen runs achieve `1.0 / 1.0` agreement between the staged baseline and the `judgment_only` baseline on the 40-item sanity subset. This supports treating `J1` as a stable first-pass exposed judgment measure.

For first-pass exposed judgment, the strongest Christian-over-secular effect is modest and limited to the main 7B model's heart judgment. In `qwen2.5:7b-instruct`, `christian_pre` shifts `J1` heart judgments on `9.17%` of items and `secular_pre` shifts them on `7.50%`, yielding a direct Christian-minus-secular contrast of `+1.67` percentage points with a bootstrap interval of `[0.00, 4.17]`, `p = 0.494`, and `dz = 0.13`. Act-level first-pass movement remains near zero. In `qwen2.5:0.5b-instruct`, the direct first-pass heart contrast disappears (`-0.83` points).

Relative to baseline, explanation language is more prompt-sensitive than first-pass exposed judgment. In the 7B model, the raw explanation score rises by `+15.83` points under `christian_post` and by `+17.50` points under `secular_post`. After lexical-echo control, the controlled semantic explanation score rises by `+10.00` points under `christian_post` and by `+15.00` points under `secular_post`. This shows explanation-layer movement, but not a uniquely Christian residual advantage.

The direct matched-control explanation contrasts are weak or unstable. In 7B, the direct Christian-minus-secular raw explanation contrast is `-1.67` points `[-15.83, 11.67]`, and the controlled semantic contrast is `-5.00` points `[-13.33, 1.67]`. In 0.5B, the raw contrast is `-4.17` points `[-20.83, 10.00]`, while the controlled semantic contrast is only `+2.50` points `[-0.83, 6.67]`. The same-family comparison therefore attenuates rather than strengthens a Christian-specific story.

`J1→J2` revision is rare. In 7B, post conditions show small heart revision (`8.33%` in `secular_post`, `6.67%` in `christian_post`) and very small act revision. In 0.5B, act revision is zero throughout and heart revision is only `0.83%` in baseline and both post conditions. The direct Christian-minus-secular revision contrasts are weak or null. This supports a mechanism reading in which explanation can move while both `J1` and `J2` remain largely stable.

The exploratory heterogeneity analysis suggests where motive-sensitive effects might concentrate, but it does not support strong category-level claims. Positive 7B pre-heart estimates appear in `motive_vs_outcome` and `good_act_bad_motive`, but intervals remain wide and the smaller model is unstable.

中文提示：
- results 的主顺序已经固定成：sanity -> first-pass -> explanation -> revision -> scale -> heterogeneity。
- Christian-specific story 在 explanation layer 里被明确写弱。
