# VDCR Evaluation Granularity

VDCR evaluates dynamic video concept recognition at three complementary
granularities. These metrics should be reported together because they answer
different questions about model behavior.

## 1. Open Exact Naming

**Question measured:** Can the model generate the canonical dynamic concept name
from the video without seeing candidate answers?

**Input format:** The model receives the video and the open prompt:

```text
Which named dynamic concept is instantiated by the temporally evolving process in this video?
Return only the short canonical concept name in English or Chinese. Do not explain.
```

**Credit rule:** A response is correct only if normalized text exactly matches
the gold answer or an accepted alias/translation. Normalization handles case,
Unicode form, spacing, and light punctuation, but it does not give credit for a
broad parent category or a visual caption.

**What this metric captures:** Open-vocabulary expert concept recall and exact
terminology production.

**What this metric does not capture:** Partial video understanding when the
model describes the visible mechanism but fails to produce the benchmark's
canonical name.

## 2. Open Description Judge

**Question measured:** Can the model describe the dynamic mechanism specifically
enough to distinguish the gold concept, even if it does not know the canonical
name?

**Input format:** The model receives the video and a description prompt:

```text
Describe the visible dynamic process or mechanism in this video in one concise phrase or sentence.
It is fine if you do not know the exact scientific name, but be specific about the key temporal mechanism.
Do not list multiple guesses.
```

**Judge input:** The judge sees the gold answer, accepted aliases, domain,
concept type, dynamic evidence summary, and the model response. The judge does
not rescore by exact string match.

**Credit rule:** A response is correct only when it either:

- names the gold concept or a standard alias/translation; or
- describes the key dynamic mechanism specifically enough to distinguish it from
  nearby mechanisms.

The model does not need to use the canonical term. It must, however, identify
the mechanism-bearing temporal pattern rather than only the object, broad event,
or generic domain.

The judge uses five labels:

- `understands_mechanism`: correct. The response names the concept or gives a
  sufficiently specific mechanism description.
- `partial_generic`: incorrect. The response identifies only a broad event,
  object, material, domain, or high-level phenomenon.
- `related_but_wrong`: incorrect. The response names or describes a specific
  nearby mechanism, but it is not the gold mechanism.
- `wrong`: incorrect. The response is unrelated to, or contradicts, the gold
  dynamic concept.
- `unclear`: incorrect. The response is empty, malformed, or too ambiguous to
  judge.

**Positive examples:**

- Gold: `Double Pendulum Chaos`
  - Correct description: "a double pendulum swings in a chaotic, nonperiodic
    trajectory."
- Gold: `Rayleigh-Plateau Breakup`
  - Correct description: "a thin liquid thread becomes unstable and breaks into
    droplets due to surface tension."
- Gold: `Bubble-Net Feeding`
  - Correct description: "a whale creates a ring of bubbles to corral prey and
    then swims through it."
- Gold: `Capillary Rise / Wicking`
  - Correct description: "green dye rises upward through paper by capillary
    action."

**Negative examples:**

- Gold: `Belousov-Zhabotinsky Reaction`
  - Incorrect: "chemical reaction" (`partial_generic`)
- Gold: `Slab Avalanche Release`
  - Incorrect: "avalanche" (`partial_generic`)
- Gold: `Rayleigh-Plateau Breakup`
  - Incorrect: "fluid dynamics" (`partial_generic`)
- Gold: `Endocytosis`
  - Incorrect: "cell division" (`related_but_wrong` or `wrong`, depending on
    context)
- Gold: `Iodine Clock Reaction`
  - Incorrect: "liquid changes color" (`partial_generic`)

**Reviewer-facing interpretation:** This metric separates terminology recall
from mechanism-level video understanding. A model can fail exact naming but pass
description judging when it captures the distinguishing temporal mechanism. A
model should not pass merely for broad captions such as "chemical reaction",
"waves moving", "clouds moving", or "plant movement".

## 3. MCQ Recognition

**Question measured:** Can the model recognize the correct dynamic concept when
shown a small set of plausible candidate concepts?

**Input format:** The model receives the video, the task question, and four
candidate options. It must output one option letter: `A`, `B`, `C`, or `D`.

**Construction rule:** The MCQ options are constructed from the direct-answer
gold concept set. Distractors prefer the same domain, subdomain, and concept
type when available, and aliases of the gold concept are excluded from
distractors.

**Credit rule:** The selected option letter must match the gold option. Invalid
or non-letter responses are counted as wrong.

**What this metric captures:** Video-conditioned discrimination among plausible
candidate concepts.

**What this metric does not capture:** Open-vocabulary naming or the ability to
explain the mechanism without candidate answers. MCQ scores can be higher
because the option set reveals the expected specificity and answer space.

## Reporting Guidance

Report the three metrics as separate columns:

```text
open exact naming | open description judge | MCQ recognition
```

Do not collapse them into a single score. Their expected ordering is often:

```text
open exact naming <= open description judge <= MCQ recognition
```

Large gaps are meaningful:

- A low exact-naming score with a higher description-judge score means the model
  often sees the dynamic process but cannot produce the canonical expert term.
- A high MCQ score with low open scores means the model benefits substantially
  from candidate concepts and should be interpreted as recognition under a
  closed answer set, not as open world-knowledge generation.
- A low description-judge score means the model mostly produces broad captions
  or nearby-but-wrong mechanisms rather than distinguishing dynamic mechanisms.

This three-granularity view is the recommended reviewer-facing evaluation
protocol for VDCR.
