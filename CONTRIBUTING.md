# Contributing

Thanks for your interest in improving this repository.

This project is maintained as a **paper companion repository** for a stage-separated LLM moral-evaluation study. The main standard for contributions is not just "does it run?" but also "does it keep the paper, artifacts, and claims aligned?"

## Before you open a PR

Please make sure your change is clear about which layer it touches:

- **paper-facing text**: `paper/`, `docs/final_revision/`, `README.md`
- **analysis pipeline**: `src/christian_social_intuition/analysis.py`, figure scripts, tables
- **experiment pipeline**: prompts, schemas, runner logic, configs
- **release artifacts**: `outputs/analysis/`, `paper/figures/`, `paper/main.pdf`

## Local setup

```bash
make setup
```

This installs the pinned runtime and dev dependencies and then installs the package in editable mode.

## Minimum check before proposing a change

For most documentation or paper-text changes:

```bash
make ci-smoke
```

For changes that affect analysis, figures, or paper-facing numbers:

```bash
make release-check
```

For changes that affect experiment execution:

```bash
make rerun-selected-v2
make release-check
```

## Contribution rules for this repository

### 1. Keep claims aligned with artifacts

If a paragraph, caption, README summary, or figure makes a claim, there should be a corresponding artifact in:

- `outputs/analysis/`
- `paper/figures/`
- `paper/main.tex`

If the code or results weaken an existing narrative, please weaken the narrative instead of hiding the mismatch.

### 2. Prefer explicit reproducibility over convenience

When adding dependencies or commands:

- pin new dependencies in the lock files
- keep `Makefile` targets current
- avoid adding steps that only work in one local environment unless documented clearly

### 3. Treat paper-facing outputs as release artifacts

If your change affects the manuscript-facing outputs, regenerate the relevant assets rather than editing around them manually.

In practice this usually means refreshing:

- `outputs/analysis/...`
- `paper/figures/...`
- `paper/main.pdf`

### 4. Preserve the current claim boundary unless the evidence changes

The current public release supports a **stage dissociation** claim more strongly than a strong **Christian-specific advantage** claim. Please avoid reintroducing stronger language unless the artifacts genuinely support it.

## Good PRs for this repository

Strong contributions usually do one of the following:

- improve reproducibility without changing results
- make the paper and README better aligned with the code and artifacts
- fix figure clarity while preserving empirical meaning
- tighten metric definitions or reporting
- improve experiment logging or manifest quality

## Questions or uncertainty

If you are unsure whether a change should modify the code, the paper, or both, treat that as a paper-code alignment question and say so explicitly in the PR description.
