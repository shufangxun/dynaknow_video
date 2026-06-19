# Annotation Guidelines

## Main Rule

Annotate the knowledge point demonstrated by the **dynamic process**, not the visible object or the event description.

## Card-First Rule

Every candidate must first produce a Dynamic Knowledge Card:

```text
visible_dynamic_process
temporal_evidence
single_frame_failure
candidate_mechanisms
selected_mechanism
knowledge_point
verifier_flags
critic_notes
```

The order is strict:

```text
watch the video dynamics
-> describe the visible process
-> list plausible mechanisms
-> reject source-only or static-frame explanations
-> select the visually anchored mechanism
-> write the mechanism-level knowledge point
-> build QA
```

Do not start from a wiki/source description, title, search query, or old
candidate knowledge point and then look for support in the video. Source context
can only refine a mechanism that is already visually anchored.

If the source page does not contain usable mechanism knowledge, do not use it as
evidence. Mark it internally as source text not used and rely only on the video
anchor. Broad descriptions such as "a plant grows," "a liquid changes color,"
"an animation was rendered," or workflow/date/license notes are not source
grounding.

## Two-Step Annotation

Every candidate must be annotated in two separate steps.

### Step 1: Dynamic-Knowledge Eligibility

First decide whether the video contains a dynamic phenomenon that can support knowledge evaluation.

Record:

```text
visible_dynamic_phenomenon
temporal_evidence
single_frame_failure_reason
candidate_mechanisms
```

Accept this step only if:

- The phenomenon is visible across time.
- A single frame cannot identify the phenomenon and mechanism.
- The video shows more than an object, scene, final state, or generic growth/change.
- The phenomenon can be linked to at least one named or well-defined mechanism.

Reject or keep in review if the best label is only:

- "seeds sprout over time"
- "a plant grows"
- "a liquid changes color"
- "a machine operates"
- "objects move"
- "a candle burns"

### Step 2: Knowledge-Point Expression

Then express the selected mechanism as a reusable knowledge point.

The knowledge point must answer:

```text
What phenomenon is this, and what mechanism explains the visible time change?
```

If the answer is only "what happened in the clip," it is not a benchmark
knowledge point. Rewrite or reject it before QA construction.

Examples:

- Falling apple:
  - phenomenon: unsupported object falls downward
  - knowledge point: "Gravity causes unsupported objects near Earth to accelerate downward."
  - not: "The apple falls."
  - not: "Newton's first law" unless the video specifically demonstrates inertial motion without net force.
- Seed time lapse:
  - phenomenon: seed germination or growth, if the video visibly shows emergence stages
  - knowledge point should name the biological process and mechanism, such as hydration breaking dormancy and radicle/shoot emergence, or reject if the clip only shows "sprouts got taller."
  - not: "Seed germination is when seedlings grow during early growth."
- Chemistry color change:
  - phenomenon: delayed endpoint, reduction test, precipitation, gas evolution, combustion, crystallization, phase change
  - knowledge point must name the reaction/test/process and material transformation.
  - not: "The liquid changes color."

## Acceptable Sample

A sample is acceptable if:

- The video contains visible temporal change.
- The knowledge point is a concrete mechanism, law, phenomenon, or principle that can be distinguished from nearby mechanisms.
- A single frame is insufficient.
- Subtitles, OCR text, overlays, source title, and narration do not directly reveal the answer.
- The MCQ options are balanced and plausible.

## Reject Sample

Reject if any condition holds:

- The answer can be inferred from the question and choices alone.
- The answer is directly stated in the video title, subtitle, overlay, or narration.
- Burned-in text, formulas, labels, or slide titles reveal the mechanism needed to answer.
- A single frame reveals the knowledge point.
- The video only shows an object or final state.
- The knowledge point is too broad, too narrow, or not visually supported.
- The knowledge point is only a generic category statement such as "some reactions change color" or "some processes cause movement."
- The video shows an effect, but the underlying specific mechanism cannot be named from the visual evidence plus allowed non-leaky context.
- The wrong choices are obviously unrelated.
- The correct answer is uniquely longer, more technical, or more specific than all distractors.

## Knowledge Point Wording

Knowledge points must pass the essential-mechanism test:

- It names the relevant concept, phenomenon, or mechanism.
- It states the causal, variable, or process relation that produces the visible dynamic change.
- It identifies the material/system, reagent, condition, or constraint when needed to distinguish the mechanism.
- It can support hard negatives at the same specificity level.
- It would still be meaningful outside this one video.
- It does not merely describe what happened in the clip.

Preferred wording pattern:

```text
Named concept/mechanism + cause/condition/process relation + visible dynamic consequence.
```

Use mechanism-level answers:

- "Unsupported objects accelerate downward under gravity."
- "Momentum transfer in collisions causes objects to change speed and direction after contact."
- "Plant shoots exhibit phototropism by growing toward a light source."
- "In iodine-clock reactions, thiosulfate reduces iodine back to iodide, delaying the dark starch-iodine complex until thiosulfate is depleted."
- "In Benedict's test, reducing sugars reduce copper(II) ions during heating, producing orange-red copper(I) oxide precipitate."
- "In the Brazil nut effect, vibration opens gaps that let smaller grains percolate downward, leaving larger particles on top."

Avoid:

- "The apple falls."
- "The ice becomes water in this video."
- "The siphon transfers liquid after priming."
- "The seedlings change orientation over time."
- "The elastic pendulum combines swinging and stretching."
- "Some chemical reactions produce color change."
- "Some reactions form a precipitate."
- "This is a plant."
- "Physics."

For chemistry and material-change samples, generic observable outcomes are not sufficient. If the candidate can only be labeled as "a reaction changes color," "a solid appears," or "bubbles form," reject or keep it in review until the specific reaction class or mechanism is supported by visible anchors plus allowed source-grounding context. Acceptable answers should name the reaction/test class and the mechanism behind the visible change, such as iodine-clock delay chemistry, Benedict copper reduction/Cu2O precipitate formation, acid-carbonate carbon dioxide generation, insoluble-salt precipitation after ion exchange, or crystallization during solvent evaporation.

## Knowledge Point Attachment

When a video could support several labels, attach the most specific reusable mechanism that is visibly anchored by the temporal process.

Decision order:

1. Identify the visible temporal change: motion transfer, delayed endpoint, growth direction, segregation, flow, deformation, or state change.
2. List candidate mechanisms from the video, taxonomy, and allowed source-grounding context.
3. Choose the mechanism that explains the visible change with the fewest hidden assumptions.
4. Reject labels that only name the object, device, demonstration, or final state.
5. Reject labels whose key mechanism exists only in source text and has no visible anchor in the video.
6. Prefer named mechanisms when the video and source context support them: `phototropism`, `iodine-clock reaction`, `Benedict's test`, `Brazil nut effect`, `capillary breakup`.
7. Build QA only after the Dynamic Knowledge Card has selected this mechanism.

Examples:

- For a siphon clip, do not attach "the siphon transfers liquid." Attach the fluid mechanism: "A height difference in a continuous liquid column creates a pressure imbalance that drives flow."
- For a seedling time lapse, do not attach "shoots change direction." Attach the biological mechanism: "Plant shoots exhibit phototropism by growing toward a light source."
- For a granular shaking clip, do not attach "vibration separates particles." Attach the named mechanism and causal route: "In the Brazil nut effect, vibration opens gaps that let smaller grains percolate downward, leaving larger particles on top."
- For a chemistry color-change clip, do not attach "the liquid changes color." Attach the reaction mechanism only if visible anchors plus source grounding support the reaction class.

## Source-Grounded Annotation

Annotators may use source-page summaries, file descriptions, captions, categories, and license/provenance metadata to determine the concrete knowledge point. This context is annotation-only.

Use source summaries when:

- The video visibly anchors the process, but the exact mechanism or reaction class cannot be inferred from pixels alone.
- The source description names the reagents, conditions, or mechanism needed to avoid a broad label.
- The final answer can be written as a reusable knowledge point rather than a source-title restatement.

Do not use source summaries when:

- The video does not visibly show the claimed dynamic process.
- The source text supplies a hidden mechanism with no visual anchor.
- The only possible QA would test memorization of the source page rather than recognition of the demonstrated process.
- The source text is only a broad scene description, rendering workflow, file
  history, date/license metadata, or generic phenomenon description.

For accepted source-grounded samples, record a short provenance note in internal data or the manifest. Keep source title, summary, author, URL-derived title, and other textual metadata out of the evaluation JSONL and model input.

## Evidence Span

Every accepted item needs at least one evidence span:

- `start_sec`
- `end_sec`
- one-sentence description

The evidence description should explain the visible change, not the final answer alone.

Good:

```text
The object moves from a high position to a lower position over time, with no visible support.
```

Bad:

```text
The video shows gravity.
```

## Hard Negative Rules

Distractors should be near misses:

- Same domain and preferably the same subdomain or visible phenomenon family.
- Same abstraction level and mechanism-wording style.
- Similar length and specificity.
- Plausible under a static-frame shortcut.
- Each distractor has a concrete confusion rationale.

Do not copy another sample's exact `knowledge_point` as a distractor. A
nearby mechanism can be used only after it is rewritten as a target-specific
near miss with its own confusion rationale. This prevents answer-only models
from exploiting repeated benchmark answers.

Bad distractors:

- Cross-domain fillers used only to complete four choices.
- Options that are visibly unrelated to the clip's objects or dynamic process.
- Options that are much shorter, longer, broader, or more technical than the
  correct answer.
- Exact text copied from another video's answer.

For a falling-object video, good distractors include drag, inertia, friction,
or elastic rebound when those mechanisms could plausibly be confused from a
static frame. Bad distractors include photosynthesis, plate tectonics, or DNA
replication.
