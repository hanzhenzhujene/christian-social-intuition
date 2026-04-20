# Paper Build

This directory contains the canonical manuscript source and release-facing figure assets.

- Main LaTeX source: `main.tex`
- Compiled PDF: `main.pdf`
- Local figure assets: `figures/`

## Recommended build path

From the repository root:

```bash
make ci-smoke
```

That is the same lightweight gate used in GitHub Actions. If you want the full paper-facing refresh path, run:

```bash
make release-check
```

The full release check:

- runs the test suite
- rebuilds the analysis bundles from the committed selected-v2 raw runs
- regenerates the README and paper figures
- recompiles `paper/main.pdf`

If you only want to recompile the manuscript without refreshing the analysis artifacts:

```bash
make paper
```

## Manual LaTeX build

```bash
cd paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

## Scope notes

- The figures under `paper/figures/` are copied release artifacts generated from `outputs/analysis/`.
- The manuscript treats human-coded judgment-explanation consistency as pending and does not claim completed annotation-based results.
- The current public release is calibrated to the completed selected-v2 Qwen runs documented in `outputs/runs/`.
- Figure-by-figure asset notes live in [`figures/README.md`](figures/README.md).
