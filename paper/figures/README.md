# Figure Assets

This directory contains the canonical release figures used in the paper and README.

## Main manuscript figures

- `study_overview_main.png`
- `first_pass_shift.png`
- `explanation_layer_effect.png`
- `judgment_explanation_dissociation.png`
- `j1_j2_revision.png`
- `cross_model_summary.png`
- `heterogeneity_effects.png`

## README-facing figure

- `readme_results_summary.png`

## Generation path

From the repository root:

```bash
make refresh-figures
```

That command rebuilds:

- the six analysis-derived paper figures used in the manuscript
- the README summary figure
- the study overview figure

## Source of truth

Figure inputs come from the committed analysis bundles under `outputs/analysis/`. If a figure is changed, the corresponding analysis outputs and manuscript claims should change with it.
