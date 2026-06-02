# Answer-Only Leakage Filter Prompt

You are checking whether a multiple-choice video benchmark item leaks the answer without requiring the video.

You will receive only the question and choices. Do not assume any visual content. Choose the answer only if it is strongly inferable from wording, option specificity, common priors, or clue leakage.

Return JSON:

```json
{
  "predicted_answer": "A|B|C|D|uncertain",
  "confidence": 0.0,
  "leakage_risk": "low|medium|high",
  "reason": "short explanation"
}
```

Question:

```text
Which knowledge point is best demonstrated by the dynamic process in the video?
```

Choices:

```text
A. {choice_a}
B. {choice_b}
C. {choice_c}
D. {choice_d}
```

