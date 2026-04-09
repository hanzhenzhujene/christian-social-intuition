# Christian Framing × the Social Intuitionist Model for LLMs

> A stage-separated benchmark for testing whether prompting changes an LLM's **first-pass exposed moral judgment** or mainly its **post-hoc explanation**.

[Paper (PDF)](paper/main.pdf) · [Canonical LaTeX](paper/main.tex) · [Qwen 7B analysis](outputs/analysis/qwen2.5_7b_instruct_eval_v2/analysis_report.md) · [Qwen 0.5B analysis](outputs/analysis/qwen2.5_0.5b_instruct_eval_v2/analysis_report.md)

![Study overview](paper/figures/study_overview_main.png)

## Overview

Most moral-prompting studies in LLMs evaluate a single bundled answer: judgment plus rationale. That setup is useful for benchmarking, but it makes one central identification problem hard to see:

**Did the prompt change the model's judgment, or did it mostly change how the model explained that judgment?**

This repository is built to answer that question directly. We convert everyday **Moral Stories** scenarios into a staged protocol:

- `J1`: first-pass forced-choice judgment
- `E`: explanation explicitly tied to `J1`
- `J2`: re-judgment after explanation

The framing manipulation is intentionally narrow:

- a **Christian heart-focused frame**
- a **matched secular motive-focused control**

The goal is not to ask whether Christian prompting is “better.” The goal is to separate:

- prompt effects on **first-pass exposed judgment**
- prompt effects on **post-hoc explanation**
- prompt effects that survive a **matched secular control**
- prompt effects that survive **lexical-echo control**

## Main Empirical Takeaway

The strongest evidence in this project is a **mechanism distinction**, not a robust Christian-specific advantage claim.

1. **Explanation is more prompt-sensitive than first-pass judgment relative to baseline.** In the main 7B run, Christian pre-framing changes `J1 heart` on `9.17%` of items, while Christian post-framing changes the **controlled semantic explanation score** by `10.0%` relative to baseline.
2. **The direct Christian-over-secular first-pass effect is modest.** On `qwen2.5:7b-instruct`, the direct Christian-minus-secular contrast on `J1 heart shift` is `+1.67 pp` with `95% CI [+0.00, +4.17]`. Act-level first-pass movement stays near zero.
3. **The Christian-specific explanation story weakens under stricter comparison.** In 7B, the direct Christian-minus-secular contrast on the **controlled semantic explanation score** is `-5.00 pp` with `95% CI [-13.33, +1.67]`. In `qwen2.5:0.5b-instruct`, the corresponding residual is only `+2.50 pp` with `95% CI [-0.83, +6.67]`.
4. **Re-judgment barely moves.** `J1 → J2` revision is rare in both models, which supports a stage-dissociation reading more than a downstream judgment-rewrite story.

![README results summary](paper/figures/readme_results_summary.png)

**How to read the figure**

- Left panel: relative to baseline, explanation movement is larger than first-pass act movement, and often comparable to or larger than first-pass heart movement.
- Right panel: once the comparison is made directly against the matched secular motive-focused control, the Christian-specific residual is modest at `J1` and weak or unstable at the explanation layer.
- Bottom line: this repository supports a **stage dissociation** claim more strongly than a strong **Christian-specific advantage** claim.

## Why This Matters

This project is useful even if you do not care about Christian framing per se.

It gives you a reusable experimental pattern for prompt-effect studies in which the usual “single answer” evaluation is too blunt. In particular, it helps you avoid a common mistake:

**do not infer judgment change from explanation change alone.**

That matters for work on:

- value framing
- persona prompting
- safety and alignment prompting
- politically or religiously loaded prompting
- legal and normative prompting

## What This Repository Contributes

- A stage-separated moral-evaluation benchmark built from **everyday Moral Stories scenarios**, not only trolley-style dilemmas.
- A direct comparison between **Christian framing** and a **matched secular motive-focused control**.
- Explanation analysis that distinguishes:
  - **lexical echo**
  - **raw semantic explanation score**
  - **controlled semantic explanation score**
- A same-family scale comparison:
  - `qwen2.5:7b-instruct`
  - `qwen2.5:0.5b-instruct`
- Paper-ready artifacts:
  - figures
  - direct-contrast tables
  - qualitative examples
  - appendix materials
  - reproducibility manifests

## Repository Structure

- `src/christian_social_intuition/`
  Core code for item construction, staged prompting, experiment execution, parsing, and analysis.
- `configs/frames.yaml`
  Frame text plus the lexicons used for lexical-echo and controlled-semantic scoring.
- `configs/experiment.yaml`
  Default run settings and presets.
- `data/processed/`
  Candidate pool, locked dev/eval splits, and item review sheet.
- `outputs/analysis/qwen2.5_7b_instruct_eval_v2/`
  Main-model analysis bundle.
- `outputs/analysis/qwen2.5_0.5b_instruct_eval_v2/`
  Smaller-model comparison bundle.
- `paper/`
  Canonical manuscript, figures, and compiled PDF.
- `docs/final_revision/`
  Final-calibration appendix, tables, reviewer-risk memo, and claim-boundary notes.

## Reproducing the Main Results

### Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Build the benchmark

```bash
PYTHONPATH=src python -m christian_social_intuition.cli fetch-moral-stories
PYTHONPATH=src python -m christian_social_intuition.cli build-items
PYTHONPATH=src python -m christian_social_intuition.cli apply-item-review
```

### Run the staged experiment

```bash
PYTHONPATH=src python -m christian_social_intuition.cli run-experiment \
  --model qwen2.5:7b-instruct \
  --split eval \
  --frame-mode selected \
  --run-id selected_v2
```

### Analyze the run

```bash
PYTHONPATH=src python -m christian_social_intuition.cli analyze-results \
  --results outputs/runs/qwen2.5_7b_instruct_eval_locked_v1.jsonl \
  --frames-path configs/frames.yaml \
  --output-dir outputs/analysis/qwen2.5_7b_instruct_eval_v2
```

For the smaller-model comparison, replace the model and result path with:

- `qwen2.5:0.5b-instruct`
- `outputs/runs/qwen2.5_0.5b_instruct_eval_v2.jsonl`

## Key Artifacts

### Paper

- [Main PDF](paper/main.pdf)
- [LaTeX source](paper/main.tex)

### Model-specific analysis

- [Qwen 7B report](outputs/analysis/qwen2.5_7b_instruct_eval_v2/analysis_report.md)
- [Qwen 7B direct contrasts](outputs/analysis/qwen2.5_7b_instruct_eval_v2/main_text_direct_contrasts.csv)
- [Qwen 0.5B report](outputs/analysis/qwen2.5_0.5b_instruct_eval_v2/analysis_report.md)
- [Qwen 0.5B direct contrasts](outputs/analysis/qwen2.5_0.5b_instruct_eval_v2/main_text_direct_contrasts.csv)

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

## If You Want To Build On This

The most reusable design lesson is simple:

1. separate judgment from explanation
2. include a matched control, not only a baseline
3. control for lexical echo before claiming semantic explanation change
4. test whether explanation movement actually propagates into later judgment

That logic should transfer to many other prompting domains where interpretability matters more than leaderboard-style single scores.

## Citation

If this repository is useful in your work, please cite the paper or link the repository.
