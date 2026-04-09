# Reviewer Risk Memo

## Concerns now addressed

- **“You only compare each condition to baseline.”**
  - Fixed by elevating direct Christian-vs-secular paired contrasts into the main text and appendix, with confidence intervals, paired tests, and effect sizes.

- **“The explanation effect may just be lexical priming.”**
  - Fixed by defining and reporting lexical echo, raw semantic score, and controlled semantic explanation score separately.

- **“The staged design is underused.”**
  - Fixed by explicitly integrating `J1`, `E`, and `J2`, reporting revision rates by condition and model, and framing revision as a secondary mechanism check.

- **“The robustness comparison is hard to interpret.”**
  - Improved by replacing the old cross-architecture comparison with a same-family Qwen 7B vs 0.5B comparison.

- **“The appendix is incomplete.”**
  - Fixed by expanding Appendix A–I in the canonical LaTeX manuscript and mirroring the key pieces in `docs/final_revision/`.

## Concerns that remain open

- **Human-coded judgment–explanation consistency is still pending.**
  - The paper now says this clearly and limits claims accordingly.

- **Lexical control is still lexicon-based.**
  - This is reproducible and conservative, but still a hand-built rule system rather than a full semantic model.

- **Item construction retains researcher degrees of freedom.**
  - The paper now documents them, but documentation does not remove them.

- **The same-family robustness comparison is narrower than architectural diversity.**
  - This is now treated as a limit rather than spun as a strength.

- **Paraphrase-family audit is implemented in code but not completed as a result set.**
  - The paper now documents this only in reproducibility and limitations, not in the main findings.

## Bottom line

The revision substantially reduces the main reviewer risks around identification, overclaiming, and reproducibility. The biggest remaining open risk is the lack of completed human annotation, which is now visible and explicitly scoped.
