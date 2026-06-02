# DynaKnow-Video v1 Execution Playbook

## 1. Goal

Build a 200-300 sample pilot benchmark for **dynamic video knowledge recognition**.

Each final item must answer:

```text
Which knowledge point is best demonstrated by the dynamic process in the video?
```

The benchmark should not test static object recognition, lecture transcript QA, or ordinary event description.

## 2. Collection Strategy

Use public videos only.

Target an initial candidate pool of 800-1000 videos because most public videos will fail at least one quality filter.

All accepted media is stored locally. The release sample should contain only `local_media`, for example `media/raw/dynaknow_000001.webm` or `media/segments/dynaknow_000088.mp4`. Source page URLs, direct media URLs, titles, author/license fields, and download notes belong in manifests, not in the evaluation JSONL.

Source priority:

- Wikimedia Commons real-world videos with stable file pages and license metadata.
- Government/public-institution public-domain media, when the clip itself demonstrates the dynamic knowledge point.
- University/OER demonstration media with explicit reuse terms and downloadable media.
- Open-license archive/stock platforms only when the clip is real-world, license-clear, and has no explanatory text leakage.

Preferred videos:

- 5-60 seconds after trimming.
- Clear start state, dynamic process, and end state.
- No subtitles/OCR overlays whenever possible.
- Visible process evidence, not only a final result.
- Basic science or everyday mechanism recognizable by educated non-experts.

Avoid:

- Pure lecture, slide, whiteboard, or talking-head clips.
- Videos whose title/subtitles directly state the answer.
- Videos with title cards, lower thirds, end cards, formulas, board text, or visible labels that make OCR useful for answering.
- Videos where one frame is enough.
- Magic tricks, ambiguous demonstrations, or edited montages where the mechanism is not visually supported.
- Videos requiring specialist external facts not visible in the clip.
- Synthetic, animation, simulation, paper-supplement, or lecture/explainer videos for the main split.

## 3. Candidate Sheet

For every candidate, record:

- `candidate_id`
- `source_url`
- `source_platform`
- `license_or_usage_note`
- `raw_duration_sec`
- `suggested_start_sec`
- `suggested_end_sec`
- `initial_category`
- `candidate_knowledge_point`
- `why_dynamic`
- `collector_notes`

Use `templates/candidate_videos.csv`.

## 4. Knowledge Point Selection

For each candidate video, write one primary knowledge point.

Good knowledge point:

- A reusable phenomenon, mechanism, law, or principle.
- Supported by visible temporal change.
- More abstract than the event itself.
- Specific enough to distinguish from nearby alternatives.
- Concrete enough that hard negatives can be written at the same level of detail.
- Names the mechanism, constrained process, material system, or condition when the visual effect alone is too broad.

Bad knowledge point:

- Event: "the apple falls."
- Object label: "an apple is visible."
- Broad topic: "physics."
- Generic effect: "some chemical reactions produce color change."
- Generic effect: "some reactions form a precipitate."
- Hidden cause not visible in the video.
- Caption restatement: "the video shows a melting ice cube."

### Specificity Gate

Before writing MCQ choices, apply this gate:

```text
Can a reviewer name the concrete knowledge point from the video evidence without using a broad catch-all phrase?
```

If no, do not generate an evaluation sample. Keep the candidate in `revise` only when the source can be trimmed, re-labeled, or paired with non-leaky context that supports a concrete point. Otherwise reject it.

### Source-grounded annotation

Source summaries, Commons file descriptions, categories, and provenance notes may be used by annotators to choose the concrete knowledge point. This is often necessary for chemistry, where the video can show a visible endpoint but not the reagent identity.

This context is allowed only if:

- The video visibly anchors the claimed process.
- The source summary names a concrete mechanism, reaction class, material system, or condition.
- The final QA does not require exposing the source title or summary to the model.
- The evaluation JSONL still omits `source_url`, source title, description, author, license text, and other metadata.

Record the source-grounding note in manifests or internal review files, not in the evaluation JSONL. Reject the candidate if the source text supplies a mechanism that is not visibly supported by the video.

For chemistry and material-change clips, the following are too broad for final samples:

- "Some chemical reactions produce color change."
- "Some reactions form a precipitate."
- "Some mixtures produce gas during chemical reactions."

Replace them with concrete points when supported, for example:

- "Iodine-clock reactions can show a delayed abrupt endpoint color change."
- "Persulfate iodine-clock reactions turn dark blue after thiosulfate is depleted and iodine binds starch."
- "Benedict's reagent changes color when heated with reducing sugars."
- "Acid-carbonate reactions release carbon dioxide gas bubbles."
- "Mixing ions that form an insoluble salt can produce a precipitate."

## 5. MCQ Construction

Use one generic question:

```text
Which knowledge point is best demonstrated by the dynamic process in the video?
```

Each item has 4 options:

- 1 correct knowledge point.
- 3 hard negatives.

Hard negatives should:

- Come from the same broad category when possible.
- Use the same abstraction level.
- Be plausible if one only sees static frames.
- Represent nearby concepts or common misconceptions.

Hard negatives should not:

- Be obviously unrelated.
- Differ strongly in length or specificity.
- Include only one option matching the visible object type.

## 6. Shortcut Filtering

Run these checks before accepting a sample.

### Specificity audit

Input: full sample JSONL.

Reject or revise if `knowledge_point` or the correct choice contains broad phrases such as `some reactions`, `some chemical`, `some mixtures`, `can cause a change`, or an unnamed effect that does not identify the mechanism. This audit runs before answer-only and frame-shortcut checks because a broad target can pass shortcut checks while still failing the benchmark objective.

Command:

```bash
python3 scripts/audit_knowledge_specificity.py release/<version>/dynaknow_video_pilot_<version>_balanced.jsonl
```

### Answer-only

Input: question and choices only.

Reject if a strong text-only model or human can reliably infer the answer from option wording.

### Single-frame

Input: first frame, middle frame, last frame, and manually selected best frame.

Reject if any single frame makes the correct knowledge point obvious.

### Sparse-frame

Input: 4-8 sampled frames, preferably without temporal order for one variant.

Flag if sparse frames match full-video performance. Keep only if the full motion is materially useful.

### Subtitle-only

Input: ASR/transcript only.

Reject if subtitles or narration directly state the knowledge point.

For the main split, prefer clips with no subtitles and no required audio. If useful content has only a short leaky opening or ending, cut a no-audio segment into `media/segments/` and rerun the frame/OCR review on that segment.

### Static-caption-only

Input: captions for one or more still frames.

Reject if a static image description is sufficient.

## 7. Human Review

Each final sample needs human review fields:

- `human_full_video_correct`: reviewer can answer from full video.
- `human_single_frame_status`: `wrong`, `uncertain`, or `correct`.
- `answer_leakage_status`: `pass` or `fail`.
- `subtitle_leakage_status`: `pass` or `fail`.
- `ocr_leakage_status`: `pass`, `fail`, or `target_text_present`.
- `review_decision`: `accept`, `revise`, or `reject`.

Accept only if:

```text
human_full_video_correct = true
AND human_single_frame_status != correct
AND answer_leakage_status = pass
AND subtitle_leakage_status = pass
AND ocr_leakage_status = pass
```

## 8. Pilot Milestones

Week 1:

- Lock taxonomy and 50-80 candidate knowledge points.
- Create initial hard negative pools.

Week 2-3:

- Collect 800-1000 public video candidates.
- Record metadata and rough timestamps.

Week 4:

- First-pass filter to 400-500 candidates.

Week 5-6:

- Write primary knowledge points, dynamic evidence spans, and MCQs.

Week 7:

- Run shortcut filters and human review.
- Keep 200-300 samples.

Week 8:

- Run pilot model evaluation.
- Report full-video accuracy, answer-only accuracy, best-static accuracy, Dynamic Necessity Gap, and Leakage Gap.
