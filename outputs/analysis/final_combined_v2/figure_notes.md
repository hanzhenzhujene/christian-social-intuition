# Figure Notes

## Figure 1: first_pass_shift.png
- Data slice: `condition_summary.csv` rows for `secular_pre`, `christian_pre`, `secular_post`, `christian_post` across the two Qwen models.
- Transformation: item-level shift rates vs baseline with bootstrap confidence intervals.
- Infer: heart-level pre-framing movement is larger than act-level movement; 0.5B attenuates that pattern.
- Do not infer: a significant Christian-over-secular advantage from this figure alone.

## Figure 2: explanation_layer_effect.png
- Data slice: `condition_summary.csv` rows for the four framed conditions across both Qwen models.
- Transformation: baseline deltas for coarse explanation focus, raw semantic score, and controlled semantic score.
- Infer: explanation outputs are prompt-sensitive relative to baseline; the controlled row is the key diagnostic layer.
- Do not infer: Christian-post exceeds secular-post after lexical control unless the direct contrast table also supports it.

## Figure 3: judgment_explanation_dissociation.png
- Data slice: `condition_summary.csv` rows for the four framed conditions across both Qwen models.
- Transformation: x-axis is first-pass heart shift vs baseline; y-axis is controlled semantic explanation shift vs baseline.
- Infer: some conditions move explanation more than first-pass judgment.
- Do not infer: Christian superiority or hidden internal mechanisms.

## Figure 4: j1_j2_revision.png
- Data slice: `revision_summary.csv` for `baseline`, `secular_pre`, `christian_pre`, `secular_post`, and `christian_post` across both Qwen models.
- Transformation: condition-level act and heart revision rates from `J1` to `J2`.
- Infer: revision is rare and secondary to explanation movement.
- Do not infer: substantial downstream judgment rewriting.

## Figure 5: cross_model_summary.png
- Data slice: `direct_control_contrasts.csv` for the direct pre-framing heart contrast and direct post-framing controlled explanation contrast.
- Transformation: paired Christian-minus-secular estimates with bootstrap intervals.
- Infer: the smaller Qwen model attenuates the Christian-specific story.
- Do not infer: scale-stable robustness of a Christian-specific mechanism.

## Figure 6: heterogeneity_effects.png
- Data slice: `heterogeneity_summary.csv` by `primary_tension_tag` for the two exploratory contrasts.
- Transformation: within-tag Christian-minus-secular estimates with bootstrap intervals.
- Infer: where motive-sensitive effects might concentrate.
- Do not infer: confirmed category-level effects.
