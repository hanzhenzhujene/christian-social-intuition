# Outputs Map

This directory contains the released experiment artifacts that the paper and README summarize.

## Canonical subdirectories

- `runs/`
  - committed selected-v2 raw outputs for the two released Qwen models
  - these are the source-of-truth model responses used to rebuild the paper-facing analysis bundles
- `analysis/`
  - regenerated summaries, tables, figures, manifests, and reports derived from the committed raw runs
  - `final_combined_v2/` is the main paper-facing bundle
  - `final_readout.md` is the shortest repo-level empirical summary

## What to use for the paper

If you are trying to verify a claim in the manuscript, start here:

- `analysis/final_combined_v2/analysis_report.md`
- `analysis/final_combined_v2/main_text_direct_contrasts.csv`
- `analysis/final_combined_v2/appendix_direct_contrasts_full.csv`
- `analysis/final_combined_v2/figure_notes.md`

## Rebuild path

From the repository root:

```bash
make refresh-analysis
make refresh-figures
```

Or run the full paper-facing path:

```bash
make release-check
```

## Scope note

The public release is intentionally calibrated to the completed selected-v2 Qwen runs. Family-audit support exists in code, but full paraphrase-family audit results are not part of the current public claim set.
