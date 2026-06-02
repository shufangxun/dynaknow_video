# Annotation Guidelines

## Main Rule

Annotate the knowledge point demonstrated by the **dynamic process**, not the visible object or the event description.

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

Knowledge points must pass the specificity test:

- It names the relevant mechanism or constrained process, not only an outcome.
- It identifies the material/system or condition when that is needed to distinguish the knowledge.
- It can support hard negatives at the same specificity level.
- It would still be meaningful outside this one video.

Use:

- "Unsupported objects accelerate downward under gravity."
- "A solid can absorb heat and melt into a liquid."
- "Benedict's reagent changes color when heated with reducing sugars."
- "Plant shoots can grow toward a light source."

Avoid:

- "The apple falls."
- "The ice becomes water in this video."
- "Some chemical reactions produce color change."
- "Some reactions form a precipitate."
- "This is a plant."
- "Physics."

For chemistry and material-change samples, generic observable outcomes are not sufficient. If the candidate can only be labeled as "a reaction changes color," "a solid appears," or "bubbles form," reject or keep it in review until the specific reaction class or mechanism is supported. Acceptable examples include iodine-clock delayed endpoint color change, Benedict's reducing-sugar color test, acid-carbonate carbon dioxide generation, insoluble-salt precipitation after ion exchange, or crystallization during solvent evaporation.

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

- Same category when possible.
- Same abstraction level.
- Similar length and specificity.
- Plausible under a static-frame shortcut.

For a falling-object video, good distractors include friction, elasticity, or inertia. Bad distractors include photosynthesis, plate tectonics, or DNA replication.
