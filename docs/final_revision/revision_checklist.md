# Final Revision Checklist

## Core calibration

- Main claim tightened to stage dissociation rather than a robust uniquely Christian-specific advantage.
- Direct Christian-vs-secular first-pass heart effect described as modest in 7B and absent in 0.5B.
- Direct Christian-vs-secular explanation contrasts described as weak or unstable after matched-control comparison and lexical-echo control.
- Same-family comparison framed as attenuation across Qwen scale, not robustness success.
- `J1→J2` revision framed as a secondary mechanism check and reported as rare.

## Analysis exports

- Added combined direct-contrast table source at `outputs/analysis/final_combined_v2/main_text_direct_contrasts.csv`.
- Added full appendix direct-contrast source at `outputs/analysis/final_combined_v2/appendix_direct_contrasts_full.csv`.
- Added deterministic qualitative examples at `outputs/analysis/final_combined_v2/qualitative_examples.csv`.
- Added figure interpretation notes at `outputs/analysis/final_combined_v2/figure_notes.md`.

## Paper files

- Rewrote `paper/main.tex` as the canonical manuscript.
- Recompiled `paper/main.pdf`.
- Rebuilt the paper figures in `paper/figures/`.

## Markdown mirrors

- Updated:
  - `docs/abstract_draft.md`
  - `docs/introduction_draft.md`
  - `docs/methods_draft.md`
  - `docs/results_draft.md`
  - `docs/discussion_draft.md`
  - `docs/limitations_draft.md`
  - `docs/conclusion_draft.md`
  - `docs/paper_draft.md`

## Validation

- `pytest -q` passes: `21 passed`
- `pdflatex` compiles successfully
- Active paper/docs/README references remain Qwen-only
