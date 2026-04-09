# Item Audit

## Scope

This project uses Moral Stories as the source benchmark, but the experiment requires contrastive A/B vignettes that support staged judgment, explanation, and re-judgment. The locked item set was therefore audited for:

- everyday plausibility
- explanation-rich motive space
- lack of direct treatment leakage from explicitly religious scenario content
- stable A/B parsing
- acceptable surface text quality

## Audit Actions

1. Rebuilt the candidate pool after adding text cleanup for quoted actions and several dataset typos.
2. Excluded scenarios with explicit religious lexical content such as `Christian`, `church`, `Bible`, `pastor`, `prayer`, and `Satanism` to avoid treatment-content contamination in a Christian-framing experiment.
3. Rebalanced option order so the candidate pool is exactly `75/75` on the location of the moral option, and the locked splits are exactly `15/15` for dev and `60/60` for eval.
4. Completed the review sheet at [item_review_v1.csv](/Users/hanzhenzhu/Desktop/Christian_Social_intuition/data/processed/item_review_v1.csv) with `manual_accept` filled for all `150` rows.
5. Applied `16` manual tag overrides where the heuristic tagger clearly mismatched the item’s main diagnostic tension.

## Final Counts

- Candidate pool: `150` items, `75/75` moral-option balance, heuristic tags initially `30` per category.
- Locked dev split: `30` items with tag counts `7 motive_vs_outcome`, `7 appearance_vs_intention`, `7 mixed_stakeholder_context`, `5 bad_act_good_motive`, `4 good_act_bad_motive`.
- Locked eval split: `120` items with tag counts `29 motive_vs_outcome`, `28 appearance_vs_intention`, `27 mixed_stakeholder_context`, `18 good_act_bad_motive`, `18 bad_act_good_motive`.

The final locked tag distribution is intentionally not forced back to uniformity after manual review. Primary analyses do not depend on tag balance. Tags are retained for diagnostic slice analyses, so tag validity was prioritized over equal quotas.

## Manual Tag Overrides

- `ms_061` -> `mixed_stakeholder_context`: family versus global beneficiaries.
- `ms_062` -> `appearance_vs_intention`: same help-seeking goal, manipulative versus direct expression.
- `ms_063` -> `mixed_stakeholder_context`: spouse support versus household financial risk.
- `ms_064` -> `appearance_vs_intention`: same protective aim, different interpersonal method.
- `ms_065` -> `appearance_vs_intention`: same protective aim, different interpersonal method.
- `ms_076` -> `appearance_vs_intention`: same civic goal, harsh versus respectful delivery.
- `ms_082` -> `appearance_vs_intention`: same social goal, rude outburst versus quiet signal.
- `ms_086` -> `bad_act_good_motive`: bad act justified by a pro-social aim.
- `ms_091` -> `motive_vs_outcome`: honesty versus pocketing extra money.
- `ms_099` -> `motive_vs_outcome`: support versus neglect.
- `ms_101` -> `mixed_stakeholder_context`: speech affects friend and employer.
- `ms_108` -> `motive_vs_outcome`: child safety versus convenience.
- `ms_110` -> `motive_vs_outcome`: parental help effectiveness tradeoff.
- `ms_113` -> `motive_vs_outcome`: discipline versus inaction.
- `ms_116` -> `motive_vs_outcome`: downstream social outcomes, not a good-motive bad-act case.
- `ms_117` -> `mixed_stakeholder_context`: patient-family end-of-life conflict.

## Remaining Limits

- Some category boundaries remain conceptually fuzzy, especially between `appearance_vs_intention` and `bad_act_good_motive`.
- The locked splits are balanced on option order, but not on diagnostic tag counts after manual correction.
- The item audit removed explicit religion words, but not all culturally charged content. That is deliberate: the experiment targets everyday moral scenarios, not sanitized toy cases.
