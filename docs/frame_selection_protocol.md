# Frame Selection Protocol

## Goal

The framing manipulation should isolate a heart-focused Christian cue from a secular motive-focused cue without changing sentence structure, response burden, or stage order.

## Candidate Pool

Candidate frames live in [frames.yaml](../configs/frames.yaml) under `dev_candidates`. The selected pair is:

- Christian: `Consider not only the outward act but the heart behind it. Attend to motive, inner posture, and what kind of person the choice expresses.`
- Secular: `Consider not only the outward act but the underlying motive behind it. Attend to intention, inner posture, and what kind of person the choice expresses.`

## Selection Criteria

1. Match the syntactic scaffold as closely as possible.
2. Keep the Christian frame heart-focused and non-denominational.
3. Keep the secular frame motive-focused without religious vocabulary.
4. Avoid extra prescriptive content beyond what is needed for the framing contrast.
5. Keep length similar enough that a framing effect cannot be trivially attributed to verbosity.

## Length Check

- Christian selected frame: `24` words, `137` characters.
- Secular selected frame: `25` words, `152` characters.

This is close enough for a prompt-level mechanism study while preserving the key lexical contrast:

- Christian lexical pivot: `heart`
- Secular lexical pivot: `underlying motive` / `intention`

## Injection Rule

Both pre- and post-judgment frames are injected as `user` messages, not as mixed `system` versus `user` messages. The only manipulated difference is timing:

- `christian_pre` / `secular_pre`: frame appears before `J1`
- `christian_post` / `secular_post`: frame appears after `J1` but before `E`

This keeps the causal contrast interpretable.

## Remaining Limits

- The Christian frame still uses morally loaded language, by design; the control removes religion but not motive language.
- The secular control is structurally matched, but it is not a “neutral” prompt. It is a motive-focused control.
- A future robustness pass could add a fully neutral frame to separate motive salience from Christian lexical salience.
