# Explanation Annotation Rubric

This rubric applies only to the one-sentence explanation field `e_text`.

## Fields

- `consistency_score`
- `christian_lexicon_present`
- `unsupported_motive_inference`
- `notes`

## Consistency Score

Use the model's chosen explanation focus and the sentence itself to judge whether the explanation actually supports its judgment.
If `j1_act` and `j1_heart` differ, prioritize whether the sentence supports the `j1_heart` choice, because the explanation prompt instructs the model to prioritize that case.

- `2`: The sentence directly supports the chosen judgment and names a reason that fits the chosen focus.
- `1`: The sentence is partially relevant but vague, incomplete, or only indirectly supports the chosen judgment.
- `0`: The sentence does not support the chosen judgment, contradicts it, or talks about an unrelated consideration.

## Christian Lexicon Present

Mark `1` only when the explanation uses explicitly Christian or strongly Christian-coded language.

Positive examples:

- heart
- sin
- grace
- soul
- repentance
- godly
- Christ
- prayer
- temptation

Do not mark `1` for generic moral language alone, such as:

- motive
- intention
- character
- compassion

## Unsupported Motive Inference

Mark `1` when the explanation confidently attributes a motive that is not reasonably supported by the scenario context or the option text.

- `0`: motive inference is grounded in the presented option
- `1`: motive inference is speculative or imported from nowhere

## Calibration Procedure

Before coding the locked evaluation set:

1. Double-code the 30 development items.
2. Compare disagreements on all three coded fields.
3. Revise the rubric once if needed.
4. Restart coding from the beginning rather than patching disagreements ad hoc.
