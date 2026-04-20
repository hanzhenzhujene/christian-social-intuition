# Christian Framing × the Social Intuitionist Model for LLMs

> A stage-separated benchmark for testing whether prompting changes an LLM's **first-pass exposed judgment** or mainly its **post-hoc explanation**.

[Paper (PDF)](paper/main.pdf) · [Canonical LaTeX](paper/main.tex) · [Qwen 7B analysis](outputs/analysis/qwen2.5_7b_instruct_eval_v2/analysis_report.md) · [Qwen 0.5B analysis](outputs/analysis/qwen2.5_0.5b_instruct_eval_v2/analysis_report.md)

![Study overview](paper/figures/study_overview_main.png)

## Why This Repository Exists

Most prompt-effect papers on LLM morality, values, or personas score a single bundled answer: judgment plus rationale. That setup is useful for benchmarking, but it leaves one central identification problem unresolved:

**when the output changes, did the model actually change its first-pass judgment, or did it mainly change how it explained itself?**

This repository is designed to answer that question directly. It adds four pieces that are usually missing in prompt studies:

- **stage separation**: `J1` first-pass judgment, `E` explanation, `J2` re-judgment
- a **matched secular motive-focused control**, not only a baseline
- **lexical-echo control** before claiming semantic explanation change
- a **secondary revision check** to test whether explanation movement propagates into later judgment

The Christian-framing case study is the application. The broader contribution is a reusable evaluation design for identifying **where prompting acts**.

## Quickstart

If you want to reproduce the released paper-facing artifacts from the committed raw runs:

```bash
make setup
make release-check
```

This will:

- install pinned dependencies
- run the test suite
- rebuild model-specific and combined analysis bundles
- regenerate paper/README figures
- recompile [paper/main.pdf](paper/main.pdf)

Expected refreshed outputs:

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

## What This Lets You Test That Bundled Evaluations Cannot

| Question | Standard bundled answer | This repository |
|---|---|---|
| Did prompting change the model's decision? | Ambiguous | Measured directly at `J1` |
| Did prompting only change the justification style? | Hard to isolate | Measured directly at `E`, with lexical-echo control |
| Does the effect survive a matched non-religious control? | Often not tested | Christian vs secular motive-focused contrast |
| Does explanation movement change later judgment? | Usually invisible | Checked with `J1 -> J2` revision |

This is the core research value of the project: it turns a vague prompt-effect question into a more identifiable mechanism question.

## Main Empirical Takeaway

The strongest evidence in this repository is a **mechanism distinction**, not a robust Christian-specific advantage claim.

1. **Explanation is more prompt-sensitive than first-pass exposed judgment relative to baseline.** In the main 7B run, Christian pre-framing changes `J1 heart` on `9.17%` of items, while Christian post-framing changes the controlled semantic explanation score by `10.0%` relative to baseline.
2. **The direct Christian-over-secular first-pass effect is modest.** On `qwen2.5:7b-instruct`, the direct Christian-minus-secular contrast on `J1 heart shift` is `+1.67 pp` with `95% CI [+0.00, +4.17]`. Act-level first-pass movement stays near zero.
3. **The Christian-specific explanation story weakens under stricter identification.** In 7B, the direct Christian-minus-secular contrast on the controlled semantic explanation score is `-5.00 pp` with `95% CI [-13.33, +1.67]`. In `qwen2.5:0.5b-instruct`, the corresponding residual is only `+2.50 pp` with `95% CI [-0.83, +6.67]`.
4. **Re-judgment barely moves.** `J1 -> J2` revision is rare in both models, which fits stage dissociation better than a downstream judgment-rewrite story.

![README results summary](paper/figures/readme_results_summary.png)

**How to read the figure**

- Left panel: relative to baseline, explanation movement is clearly larger than act-level first-pass movement, and in the 7B model is similar in scale to heart-level first-pass movement.
- Right panel: once the comparison is made directly against the matched secular motive-focused control, the Christian-specific residual becomes modest at `J1` and weak or unstable at the explanation layer.
- Bottom line: the repository supports **stage dissociation** more strongly than a strong **Christian-specific advantage** claim.

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

For the broader documentation layout, see [docs/README.md](docs/README.md).

## Reproducibility Details

### Pinned environment

- Python `>=3.11`
- locked runtime dependencies in [requirements.lock.txt](requirements.lock.txt)
- locked dev dependencies in [requirements-dev.lock.txt](requirements-dev.lock.txt)

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
python -m pip install -r requirements.lock.txt -r requirements-dev.lock.txt
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
