# Paper Outline

## Title Options

- Working title: `Judgment Before Justification: Christian Framing and the Social Intuitionist Model in LLM Moral Evaluation`
- Alternate title: `Does Christian Framing Change Moral Judgment or Moral Rationalization in LLMs?`

## One-Sentence Thesis

A staged LLM evaluation design shows that Christian heart-focused framing yields at most a modest first-pass heart-level increment over a matched secular motive-focused control, while explanation language is more labile overall but not robustly Christian-specific once matched-control and lexical-control tests are applied.

## Abstract Summary Note

- Goal: Frame the paper as a mechanism study, not a generic prompt-effect paper.
- Must include: the judgment-versus-explanation distinction, SIM motivation, staged `J1 -> E -> J2` design, main `qwen` result, same-family `0.5B` comparison setup, and perfect sanity agreement.
- Evidence/artifacts to cite: [final_readout.md](../outputs/analysis/final_readout.md), [qwen v2 analysis report](../outputs/analysis/qwen2.5_7b_instruct_eval_v2/analysis_report.md), and the released `qwen2.5:0.5b-instruct` selected-v2 outputs.
- Guardrails: Do not mention unsupported consistency findings or oversell model generality.

## Introduction

- Goal: Motivate the measurement problem, introduce SIM as an operational framework, justify Christian framing plus matched secular control, and preview the layered result.
- Must include:
  - current LLM moral prompting often conflates judgment and explanation
  - why this matters for interpreting prompt effects
  - SIM as the theory lens
  - Christian framing as a useful motive/heart probe rather than a normative standard
  - `christian_post` as the cleanest post-hoc rationalization test
  - preview of the `qwen` findings and the same-family scale-comparison logic
- Evidence/artifacts to cite: [methods_draft.md](methods_draft.md), [results_draft.md](results_draft.md), [final_readout.md](../outputs/analysis/final_readout.md).
- Guardrails:
  - avoid theology-first framing
  - explicitly say “intuition” is operationalized, not literal
  - mention annotation pending only briefly

## Related Work

- Goal: Position the paper across empirical NLP and moral psychology without letting either side swallow the contribution.
- Must include:
  - LLM moral reasoning benchmarks: benchmarked moral QA, scenario evaluation, and ethics prompting
  - prompt-framing / persona effects: system prompts, role prompts, value-conditioned prompting, and persona framing
  - moral psychology / SIM: intuitionist models, post-hoc reasoning, and motive-versus-outcome distinctions
  - a gap statement that no prior line cleanly stage-separates first-pass judgment from explanation in a Christian-framing setup
- Evidence/artifacts to cite:
  - current paper's design contrast versus single-response benchmark practice
  - empirical prompt-effect and moral-psychology references selected during literature review
- Guardrails:
  - do not claim “first” unless literature review really supports it
  - separate empirical prompt-effect papers from theory-linked mechanism papers

## Theoretical Framing / SIM

- Goal: Explain why SIM is the right interpretive framework for the staged design.
- Must include:
  - SIM's core distinction between initial judgment and later reasoning
  - how `J1`, `E`, and `J2` map onto an operationalized LLM analogue
  - why `christian_post` is theoretically informative
  - why this is an analogy for observed behavior, not a claim about internal cognition
- Evidence/artifacts to cite: [discussion_draft.md](discussion_draft.md), [methods_draft.md](methods_draft.md).
- Guardrails:
  - do not anthropomorphize the models
  - avoid saying LLMs “have” intuitions in the human sense

## Dataset and Item Construction

- Goal: Show that the benchmark is grounded, everyday, and carefully audited.
- Must include:
  - Moral Stories as the source benchmark
  - conversion into A/B contrastive vignettes
  - locked item fields
  - exclusion of explicit religious scenarios
  - option-order balancing
  - manual review and retagging
  - final split sizes
- Evidence/artifacts to cite: [item_audit.md](item_audit.md), [methods_draft.md](methods_draft.md), [item_review_v1.csv](../data/processed/item_review_v1.csv).
- Guardrails:
  - do not imply the tags are perfect or fully theory-pure
  - note that final tag balance is intentionally uneven after manual correction

## Experimental Design

- Goal: Make the staged causal design fully interpretable.
- Must include:
  - the five main conditions plus sanity condition
  - `J1`, `E`, `J2` definitions
  - matched Christian and secular frames
  - why pre/post timing is the key manipulated difference
  - why everyday scenarios are preferable to trolley-style paradigms here
- Evidence/artifacts to cite: [frame_selection_protocol.md](frame_selection_protocol.md), [methods_draft.md](methods_draft.md).
- Guardrails:
  - do not introduce new conditions not actually run
  - do not imply explanation-stage labels were human-coded

## Models and Analysis Plan

- Goal: Describe the modeling setup and the completed outcome measures.
- Must include:
  - `qwen2.5:7b-instruct` as main model on `120` items
  - `qwen2.5:0.5b-instruct` as smaller same-family comparison model
  - deterministic decoding
  - primary metrics: `J1` act shift, `J1` heart shift, direct Christian-versus-secular explanation contrasts, lexical-echo-controlled explanation metrics, and `J1 -> J2` revision
  - sanity agreement
  - mixed-effects analyses as confirmatory rather than headline evidence
  - annotation sheet generation and the pending status of manual coding
- Evidence/artifacts to cite: [methods_draft.md](methods_draft.md), [qwen v2 analysis report](../outputs/analysis/qwen2.5_7b_instruct_eval_v2/analysis_report.md), the `qwen2.5:0.5b-instruct` selected-v2 outputs, and the annotation sheets.
- Guardrails:
  - treat consistency as pending
  - do not imply mixed-effects are the only evidence base

## Results

- Goal: Present a layered findings narrative that mirrors the paper's mechanism claim.
- Must include:
  - **Sanity and setup validation**
    - perfect `baseline` versus `baseline_judgment_only` agreement
    - clean parsing and zero malformed rows
  - **First-pass judgment effects**
    - `qwen` act judgments mostly fixed
    - `qwen christian_pre J1 heart shift = 9.17%`
    - `qwen secular_pre J1 heart shift = 7.50%`
    - Christian-over-secular first-pass heart contrast `+1.67` percentage points
  - **Explanation-layer effects**
    - baseline-centered explanation movement is larger than first-pass movement
    - direct Christian-versus-secular explanation contrasts weaken after matched-control and lexical-control analysis
    - item-level exemplars should illustrate explanation redescription and matched-control attenuation
  - **Same-family scale comparison**
    - compare `qwen2.5:7b-instruct` against `qwen2.5:0.5b-instruct`
    - treat this as a scale-sensitivity question, not an architecture-diversity claim
  - **Pending human annotation**
    - explanation-consistency subsection present but explicitly marked incomplete
- Evidence/artifacts to cite:
  - [qwen v2 analysis report](../outputs/analysis/qwen2.5_7b_instruct_eval_v2/analysis_report.md)
  - the released `qwen2.5:0.5b-instruct` selected-v2 outputs
  - [final_readout.md](../outputs/analysis/final_readout.md)
  - raw run files for selected examples
- Guardrails:
  - do not claim Christian framing broadly rewrites first-pass judgment
  - do not present pending consistency coding as if completed

## Discussion

- Goal: Interpret the empirical pattern against the paper's competing mechanism stories.
- Must include:
  - explicit comparison between a “judgment rewrite” story and a “post-hoc rationalization” story
  - why current evidence favors a stage-separation story with substantial rhetorical mediation, especially on `qwen`
  - why the effect is best described as layered rather than purely post-hoc or purely first-pass
  - why matched secular motive framing matters for this interpretation
  - implications for future prompt-based LLM morality work
- Evidence/artifacts to cite: [discussion_draft.md](discussion_draft.md), [results_draft.md](results_draft.md).
- Guardrails:
  - avoid sweeping theory claims across all LLMs
  - do not overstate the Christian-specific increment

## Limitations

- Goal: State the real boundaries of the current evidence before reviewers do it for us.
- Must include:
  - no final human-coded consistency result yet
  - open-model scope only
  - same-family scale comparison is narrower than architecture diversity
  - lexical priming risk even after control
  - baseline already high on motive-focus for `qwen`
  - operational rather than literal use of “intuition”
  - model- and prompt-family sensitivity
- Evidence/artifacts to cite: both analysis reports, annotation sheets, [discussion_draft.md](discussion_draft.md).
- Guardrails:
  - do not turn limitations into a second discussion section
  - keep them concrete and tied to this dataset and setup

## Conclusion

- Goal: End with the narrow but novel claim the paper can actually support.
- Must include:
  - the staged design contribution
  - the main empirical takeaway that first-pass Christian-over-secular movement is modest and explanation language is more labile but not cleanly Christian-specific under matched-control analysis
  - why this matters for future benchmark design
- Evidence/artifacts to cite: [final_readout.md](../outputs/analysis/final_readout.md).
- Guardrails:
  - do not claim the paper resolves LLM moral reasoning in general
  - do not imply theology-specific superiority

## Ethics / Broader Impacts

- Goal: Address the risks of framing-sensitive moral evaluation without turning this into a normative theology section.
- Must include:
  - Christian framing is treated as a probe, not a preferred value system
  - prompt-conditioned moral evaluation can be rhetorically malleable
  - explanation-layer shifts may be mistaken for deeper value alignment
  - potential misuse of religious or ideological prompting in alignment narratives
- Evidence/artifacts to cite: design rationale in [methods_draft.md](methods_draft.md) and empirical findings in both reports.
- Guardrails:
  - avoid culture-war framing
  - avoid endorsing any religious viewpoint

## Appendix Plan

- Goal: Put all implementation-detail material in one place so the main paper stays tight.
- Must include:
  - exact Christian and secular frame text
  - item review protocol
  - manual tag overrides
  - prompt templates for `J1`, `E`, `J2`
  - additional item examples, including Christian-only first-pass cases and post-hoc lexicon cases
  - annotation rubric
  - same-family comparison tables, heterogeneity tables, paraphrase-audit tables, and mixed-effects full outputs
- Evidence/artifacts to cite:
  - [frame_selection_protocol.md](frame_selection_protocol.md)
  - [item_audit.md](item_audit.md)
  - [annotation_rubric.md](annotation_rubric.md)
  - both analysis directories
- Guardrails:
  - appendix should support reproducibility, not carry new headline claims
  - keep pending annotation clearly labeled as pending
