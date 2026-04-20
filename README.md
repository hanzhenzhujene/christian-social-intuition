# Christian Framing × the Social Intuitionist Model for LLMs

[![CI](https://github.com/hanzhenzhujene/christian-social-intuition/actions/workflows/ci.yml/badge.svg)](https://github.com/hanzhenzhujene/christian-social-intuition/actions/workflows/ci.yml)
[![Paper](https://img.shields.io/badge/paper-PDF-1f4d8f)](paper/main.pdf)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Citation metadata](https://img.shields.io/badge/citation-CITATION.cff-blue)](CITATION.cff)

> Paper companion repository for a stage-separated study of whether prompting changes an LLM's **first-pass exposed judgment** or mainly its **post-hoc explanation**.

[Paper (PDF)](paper/main.pdf) · [Canonical LaTeX](paper/main.tex) · [Qwen 7B analysis](outputs/analysis/qwen2.5_7b_instruct_eval_v2/analysis_report.md) · [Qwen 0.5B analysis](outputs/analysis/qwen2.5_0.5b_instruct_eval_v2/analysis_report.md)

<p align="center">
  <img src="paper/figures/study_overview_main.png" alt="Study overview: benchmark, staged protocol, identification logic, and evidence snapshot." width="960">
</p>
<p align="center">
  <em>Study overview: design logic plus a compact evidence snapshot from the released Qwen runs.</em>
</p>

## At a Glance

| Item | Release |
|---|---|
| Research question | When prompting changes moral output, does it change **first-pass exposed judgment** or mainly **post-hoc explanation**? |
| Benchmark design | Stage-separated `J1 -> E -> J2` with matched Christian and secular motive-focused framing |
| Data | `120` locked eval items + `40` judgment-only sanity items derived from Moral Stories |
| Models | `qwen2.5:7b-instruct` and `qwen2.5:0.5b-instruct` |
| Main take-home | Explanation is more prompt-sensitive than first-pass judgment relative to baseline; Christian-specific residuals weaken under matched control |
| Release status | Committed selected-v2 raw runs, regenerated analysis bundles, compiled paper PDF, and CI smoke checks |

## If You're Coming From The Paper

This repository is organized as a paper companion release, so the fastest path is:

- [`paper/main.pdf`](paper/main.pdf) for the canonical argument
- [`outputs/analysis/final_combined_v2/main_text_direct_contrasts.csv`](outputs/analysis/final_combined_v2/main_text_direct_contrasts.csv) for the exact matched-control estimates behind the main claims
- [`docs/final_revision/appendix_draft.md`](docs/final_revision/appendix_draft.md) for prompts, metric definitions, and reproducibility details
- [`outputs/analysis/final_combined_v2/analysis_report.md`](outputs/analysis/final_combined_v2/analysis_report.md) for the shortest artifact-grounded summary of the released runs

## Evidence Snapshot

These are the comparisons that most directly determine what the paper can and cannot claim:

| Diagnostic comparison | Qwen 7B | Qwen 0.5B | Practical reading |
|---|---|---|---|
| `christian_pre - secular_pre` on `J1 heart shift` | `+1.67 pp` `[+0.00, +4.17]` | `-0.83 pp` `[-2.50, +0.00]` | At most a modest Christian-specific first-pass heart increment in 7B; it does not persist at smaller scale. |
| `christian_post - secular_post` on controlled semantic explanation score | `-5.00 pp` `[-13.33, +1.67]` | `+2.50 pp` `[-0.83, +6.67]` | No stable Christian-specific explanation residual survives matched control plus lexical-echo control. |
| `christian_post` `J1 -> J2` heart revision rate | `6.67%` | `0.83%` | Revision is rare, so explanation can move without substantial downstream judgment rewriting. |
| `baseline` vs `judgment_only` sanity agreement | `1.0 / 1.0` | `1.0 / 1.0` | The staged interface does not appear to distort first-pass exposed judgment on the sanity subset. |

## Quickstart

### 1. Run the same lightweight checks as CI

```bash
make setup
make ci-smoke
```

This is the fastest trust check for the public release. It runs:

- `pytest -q`
- `make paper-smoke`

### 2. Rebuild the released paper-facing artifacts

```bash
make release-check
```

This is the canonical local reproduction path for the public release. It will:

- install pinned runtime and dev dependencies
- run `pytest`
- rebuild the committed analysis bundles from the released raw runs
- regenerate the paper and README figures
- recompile [`paper/main.pdf`](paper/main.pdf)

### 3. Re-run the selected-v2 experiments themselves

Only do this if you want to regenerate the raw model outputs. You need a local Ollama-compatible endpoint with both Qwen models available.

```bash
make rerun-selected-v2
make release-check
```

## Canonical Release Surface

If you only read five things in this repository, make them these:

| Artifact | Why it matters |
|---|---|
| [`paper/main.pdf`](paper/main.pdf) | Canonical writeup |
| [`paper/main.tex`](paper/main.tex) | Canonical manuscript source |
| [`outputs/analysis/final_combined_v2/analysis_report.md`](outputs/analysis/final_combined_v2/analysis_report.md) | Combined empirical readout |
| [`outputs/analysis/final_combined_v2/main_text_direct_contrasts.csv`](outputs/analysis/final_combined_v2/main_text_direct_contrasts.csv) | Main matched-control statistics |
| [`docs/final_revision/appendix_draft.md`](docs/final_revision/appendix_draft.md) | Exact prompts, metric definitions, and reproducibility details |

## Main Empirical Takeaway

The strongest evidence in this repository is a **mechanism distinction**, not a robust Christian-specific advantage claim.

1. **Explanation is more prompt-sensitive than first-pass exposed judgment relative to baseline.** In the main 7B run, Christian pre-framing changes `J1 heart` on `9.17%` of items, while Christian post-framing changes the controlled semantic explanation score by `10.0%` relative to baseline.
2. **The direct Christian-over-secular first-pass effect is modest.** On `qwen2.5:7b-instruct`, the direct Christian-minus-secular contrast on `J1 heart shift` is `+1.67 pp` with `95% CI [+0.00, +4.17]`. Act-level first-pass movement stays near zero.
3. **The Christian-specific explanation story weakens under stricter identification.** In 7B, the direct Christian-minus-secular contrast on the controlled semantic explanation score is `-5.00 pp` with `95% CI [-13.33, +1.67]`. In `qwen2.5:0.5b-instruct`, the corresponding residual is only `+2.50 pp` with `95% CI [-0.83, +6.67]`.
4. **Re-judgment barely moves.** `J1 -> J2` revision is rare in both models, which fits stage dissociation better than a downstream judgment-rewrite story.

<p align="center">
  <img src="paper/figures/readme_results_summary.png" alt="Three-panel results summary comparing baseline-relative movement, matched-control residuals, and same-family scale attenuation." width="960">
</p>
<p align="center">
  <em>Results summary: baseline movement is easiest to induce, matched-control residuals are much smaller, and the same-family scale comparison mainly shows attenuation.</em>
</p>

**How to read the figure**

- Panel A: relative to baseline, explanation movement is clearly larger than act-level first-pass movement, and in the 7B model is similar in scale to heart-level first-pass movement.
- Panel B: once the comparison is made directly against the matched secular motive-focused control, the Christian-specific residual becomes modest at `J1` and weak or unstable at the explanation layer.
- Panel C: across Qwen scales, the Christian-specific story attenuates rather than becoming more stable.
- Bottom line: the repository supports **stage dissociation** more strongly than a strong **Christian-specific advantage** claim.

## Why This Repository Is Worth Reading

Most prompt-effect papers on LLM morality, values, or personas score a single bundled answer: judgment plus rationale. That setup is useful for benchmarking, but it leaves one central identification problem unresolved:

**when the output changes, did the model actually change its first-pass judgment, or did it mainly change how it explained itself?**

This repository is designed to answer that question directly. It adds four pieces that are usually missing in prompt studies:

- **stage separation**: `J1` first-pass judgment, `E` explanation, `J2` re-judgment
- a **matched secular motive-focused control**, not only a baseline
- **lexical-echo control** before claiming semantic explanation change
- a **secondary revision check** to test whether explanation movement propagates into later judgment

The Christian-framing case study is the application. The broader contribution is a reusable evaluation design for identifying **where prompting acts**.

## What To Read First

- [paper/main.pdf](paper/main.pdf) for the canonical argument
- [outputs/analysis/final_combined_v2/analysis_report.md](outputs/analysis/final_combined_v2/analysis_report.md) for the empirical readout
- [docs/final_revision/appendix_draft.md](docs/final_revision/appendix_draft.md) for prompts, metrics, and appendix detail
- [outputs/README.md](outputs/README.md) for the released run and analysis layout
- [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md) for validation expectations

## Reproduce The Released Artifacts

The public repository is intentionally split into:

- committed raw selected-v2 runs in [`outputs/runs/`](outputs/runs/)
- committed paper-facing analysis bundles in [`outputs/analysis/`](outputs/analysis/)
- committed manuscript and figures in [`paper/`](paper/)

GitHub Actions runs the lightweight release checks on every push and pull request:

- `make ci-smoke`

The full local release check will:

- install pinned dependencies
- run the test suite
- rebuild model-specific and combined analysis bundles
- regenerate paper/README figures
- recompile [paper/main.pdf](paper/main.pdf)

If you only want to mirror the GitHub Actions gate locally, run:

```bash
make ci-smoke
```

Expected refreshed outputs after `make release-check`:

- `outputs/analysis/qwen2.5_7b_instruct_eval_v2/`
- `outputs/analysis/qwen2.5_0.5b_instruct_eval_v2/`
- `outputs/analysis/final_combined_v2/`
- `paper/figures/`
- `paper/main.pdf`

If you want to rerun the selected-v2 experiments themselves, you need a local Ollama-compatible endpoint with both Qwen models available:

```bash
make rerun-selected-v2
make release-check
```

## What This Benchmark Identifies That Bundled Evaluations Cannot

| Question | Standard bundled answer | This repository |
|---|---|---|
| Did prompting change the model's decision? | Ambiguous | Measured directly at `J1` |
| Did prompting only change the justification style? | Hard to isolate | Measured directly at `E`, with lexical-echo control |
| Does the effect survive a matched non-religious control? | Often not tested | Christian vs secular motive-focused contrast |
| Does explanation movement change later judgment? | Usually invisible | Checked with `J1 -> J2` revision |

This is the core research value of the project: it turns a vague prompt-effect question into a more identifiable mechanism question.

## Why This Matters Beyond Christian Framing

You can reuse this design anywhere a prompt may change how a model **sounds** without necessarily changing what it **decides**.

That matters for work on:

- persona prompting
- value prompting
- safety and alignment prompting
- legal and normative prompting
- politically or religiously loaded prompting
- any benchmark where explanation style could be mistaken for judgment change

If you are studying prompt effects, the most transferable lesson here is:

**do not infer judgment change from explanation change alone.**

## Repository Map

```text
src/christian_social_intuition/   core benchmark, experiment, parsing, analysis, and figure scripts
configs/                          experiment defaults and frame/lexicon definitions
data/processed/                   locked benchmark splits and review sheet
outputs/runs/                     committed selected-v2 raw runs for the two Qwen models
outputs/analysis/                 paper-facing analysis bundles
paper/                            canonical LaTeX paper, figures, and compiled PDF
docs/final_revision/              appendix, reviewer-risk memo, and release-facing notes
tests/                            unit tests for parsing, metrics, item construction, and analysis
```

Directory guides:

- [docs/README.md](docs/README.md)
- [data/README.md](data/README.md)
- [outputs/README.md](outputs/README.md)
- [paper/README.md](paper/README.md)
- [paper/figures/README.md](paper/figures/README.md)

## Reproducibility Details

### Pinned environment

- Python `>=3.11`
- locked runtime dependencies in [requirements/runtime.lock.txt](requirements/runtime.lock.txt)
- locked dev dependencies in [requirements/dev.lock.txt](requirements/dev.lock.txt)

### Command-line entrypoint

After installation, the package exposes:

```bash
csi-sim --help
```

### Manual command equivalents

If you prefer not to use the Makefile, the core commands are:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements/runtime.lock.txt -r requirements/dev.lock.txt
python -m pip install -e . --no-deps
pytest -q
PYTHONPATH=src python -m christian_social_intuition.cli analyze-results \
  --results outputs/runs/qwen2.5_7b_instruct_eval_v2.jsonl \
  --frames-path configs/frames.yaml \
  --output-dir outputs/analysis/qwen2.5_7b_instruct_eval_v2
PYTHONPATH=src python -m christian_social_intuition.cli analyze-results \
  --results outputs/runs/qwen2.5_0.5b_instruct_eval_v2.jsonl \
  --frames-path configs/frames.yaml \
  --output-dir outputs/analysis/qwen2.5_0.5b_instruct_eval_v2
PYTHONPATH=src python -m christian_social_intuition.cli analyze-results \
  --results outputs/runs/qwen2.5_7b_instruct_eval_v2.jsonl outputs/runs/qwen2.5_0.5b_instruct_eval_v2.jsonl \
  --frames-path configs/frames.yaml \
  --output-dir outputs/analysis/final_combined_v2
PYTHONPATH=src python -m christian_social_intuition.cli build-paper-figures \
  --analysis-dirs outputs/analysis/qwen2.5_7b_instruct_eval_v2 outputs/analysis/qwen2.5_0.5b_instruct_eval_v2 \
  --output-dir paper/figures
PYTHONPATH=src python -m christian_social_intuition.study_overview_figure
PYTHONPATH=src python -m christian_social_intuition.readme_summary_figure
cd paper && pdflatex -interaction=nonstopmode -halt-on-error main.tex && pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

## Key Artifacts

### Paper

- [Main PDF](paper/main.pdf)
- [LaTeX source](paper/main.tex)
- [Paper build notes](paper/README.md)

### Model-specific analysis

- [Qwen 7B report](outputs/analysis/qwen2.5_7b_instruct_eval_v2/analysis_report.md)
- [Qwen 7B direct contrasts](outputs/analysis/qwen2.5_7b_instruct_eval_v2/main_text_direct_contrasts.csv)
- [Qwen 0.5B report](outputs/analysis/qwen2.5_0.5b_instruct_eval_v2/analysis_report.md)
- [Qwen 0.5B direct contrasts](outputs/analysis/qwen2.5_0.5b_instruct_eval_v2/main_text_direct_contrasts.csv)
- [Combined final bundle](outputs/analysis/final_combined_v2/analysis_report.md)

### Final revision package

- [Appendix draft](docs/final_revision/appendix_draft.md)
- [Main-text stats table](docs/final_revision/main_text_stats_table.md)
- [Appendix stats table](docs/final_revision/appendix_stats_table.md)
- [Reviewer-risk memo](docs/final_revision/reviewer_risk_memo_final.md)
- [Safe claims](docs/final_revision/safe_claims.md)
- [Avoid claims](docs/final_revision/avoid_claims.md)

## Current Claim Boundary

This repository supports the following claims well:

- staged prompting reveals a real separation between **first-pass exposed judgment** and **post-hoc explanation**
- explanation outputs are more prompt-sensitive than first-pass judgment **relative to baseline**
- the direct Christian-over-secular first-pass heart effect in 7B is **modest**
- the Christian-specific explanation residual becomes **weak or unstable** once matched-control comparison and lexical-echo control are applied

This repository does **not** currently support strong claims that:

- Christian prompting robustly improves moral reasoning
- Christian prompting yields a stable uniquely Christian explanation advantage
- prompt-induced explanation changes reliably propagate into strong downstream judgment revision

Two pieces remain explicitly pending:

- human judgment-explanation consistency annotation
- full paraphrase-family audit results

## License and Data Note

- Code in this repository is released under the [MIT License](LICENSE).
- The benchmark items are derived from Moral Stories source material; please check upstream dataset terms when reusing the underlying data outside this repository.

## Citation

If this repository is useful in your work, please cite the paper and/or the repository metadata in [CITATION.cff](CITATION.cff).

BibTeX-style software citation:

```bibtex
@software{zhu2026christian_social_intuition,
  author = {Zhu, Hanzhen},
  title = {Christian Framing x the Social Intuitionist Model for LLMs},
  year = {2026},
  url = {https://github.com/hanzhenzhujene/christian-social-intuition},
  version = {0.1.0}
}
```
