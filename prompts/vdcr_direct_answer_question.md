# VDCR Direct-Answer Prompt

Ask the model:

```text
Which named dynamic concept is instantiated by the temporally evolving process in this video?
```

Expected answer format:

- A short concept name, preferably the canonical English name.
- Chinese aliases and standard abbreviations are accepted when listed in `accepted_answers`.
- Do not ask for multiple-choice selection in v1 direct-answer evaluation.

Scoring policy:

- Normalize case, punctuation, whitespace, and common separators.
- Match against `answer` plus every string in `accepted_answers`.
- Do not give credit for generic event descriptions such as "the liquid changes color", "a wave breaks", or "a player turns".
