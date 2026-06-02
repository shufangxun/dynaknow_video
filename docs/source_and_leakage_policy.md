# Source And Leakage Policy

## Local Storage

All videos used for review and release must be stored inside this project. Evaluation files should reference local media paths only, using paths relative to `/root/public/jasonshu/dynaknow_video`.

Storage contract:

- `media/raw/`: original downloaded videos, named by `video_id`.
- `media/raw_transcoded/`: review-compatible transcodes when the original encoding is hard to decode.
- `media/segments/`: short local clips cut from longer sources; these should be no-audio by default and used when trimming removes leakage-prone openings, endings, title cards, subtitles, or narration.

Frame-review artifacts are stored under:

- `media/frames/<video_id>/first.jpg`
- `media/frames/<video_id>/middle.jpg`
- `media/frames/<video_id>/last.jpg`
- `media/frames/<video_id>/sparse/frame_*.jpg`
- `media/contact_sheets/`
- `media/contact_sheets/sparse/`

The authoritative mapping from `video_id` to source page and direct media URL is in the relevant media manifest:

- `data/draft_media_manifest*.csv`
- `data/pilot_manifest*.csv`
- release manifests under `release/<version>/`

The public evaluation JSONL must not include `source_url`, `direct_url`, title, author, license text, or other provenance fields. Those fields stay in the manifest so the benchmark remains auditable without giving models source-name or title shortcuts.

## Source Policy

Default source pool, in priority order:

1. Real-world public or license-verifiable video pages with stable file URLs.
2. Wikimedia Commons files, currently the primary source because each file has a stable page URL, media URL, and license metadata.
3. Public-domain government or public-institution media pages, such as NASA, NOAA, USGS, NIST, or similar sources, only when the visual content itself demonstrates the dynamic knowledge point.
4. University/OER demonstration libraries with explicit reuse terms and direct downloadable media.
5. Open-license stock or archive platforms, such as Internet Archive, Pixabay, or Pexels, only when the license is clear, the clip is real-world rather than illustrative stock filler, and the target mechanism is visually observable.

YouTube or social-video pages are not first-choice sources. They can enter only if the uploader/license is explicitly compatible, the media can be downloaded under the license/terms used by the project, and the source title/transcript does not leak the target knowledge point.

Do not use synthetic, simulation, animation, paper-supplement, slide, lecture, or explainer videos for the main split. If useful, they should be held for a separate diagnostic split rather than mixed into the main real-video benchmark.

Each candidate row must preserve:

- original source page URL
- direct media URL when available
- source platform
- license or usage note
- raw duration and suggested segment
- candidate knowledge point
- dynamic evidence rationale

Recommended source mix for v1 after expansion:

- 60-70% Wikimedia Commons or similarly license-verifiable public media.
- 20-30% government/public-institution/university/OER demonstration media.
- up to 10% open stock/archive clips, used only for very clean real-world dynamics.

## Leakage Policy

The default target is no subtitles and minimal OCR. Source candidates should be selected for visible dynamics, not for explanatory text.

Avoid source videos with visible text, source metadata, or audio that names the target knowledge point.

Reject or trim videos when any of the following reveal the answer:

- title text inside the video
- subtitles or burned-in captions
- formula text or labels such as `CO2`, `gravity`, `siphon`, `surface tension`, `density`, `phototropism`
- source-page title, file name, or thumbnail text that names the exact mechanism, unless that metadata is excluded from evaluation and the video frames themselves are clean
- slide decks, classroom title cards, or explanatory overlays
- narration that directly states the answer
- end cards, credits, watermarks, or lower thirds that name the demonstration or concept

Prefer videos with:

- no subtitles
- no explanatory overlays
- no screen-recorded slides
- minimal object labels
- no audible explanation needed to answer
- visible process evidence from motion alone

If a video is otherwise valuable but only the beginning or ending contains leakage, create a local segment under `media/segments/` and review the segment as a separate draft sample. The segment must remove audio by default.

If text is unavoidable but generic, apply this rule:

- Acceptable: incidental brand marks, timestamps, unit labels, or object labels that do not distinguish the correct knowledge point from the distractors.
- Reject: any text that names the phenomenon, law, mechanism, material transition, or likely answer option.
- Review-required: text that does not name the answer but narrows the answer space, such as `experiment`, `reaction`, `pressure`, or `magnet`.

OCR/subtitle gate:

- Run first/middle/last and sparse-frame visual review for visible text.
- Mark `ocr_leakage_status=pass` only if visible text is absent or irrelevant to the target knowledge point.
- Mark `ocr_leakage_status=fail` or `target_text_present` if OCR/subtitles/overlays name the target knowledge point or a near-synonym.
- Accepted release samples must have `ocr_leakage_status=pass`.

## Current Leakage Lessons

- `dynaknow_000085` has strong gas-production evidence but burned-in `CO2` and formula text, so it should not be accepted without mitigation.
- `dynaknow_000086` has visible siphon evidence but an opening title, so it was converted into `dynaknow_000088` by trimming the title frames and dropping audio.
- Plant time-lapse videos often fail because a final frame alone can reveal germination. They need especially strict single-frame review.

## Required Review Gates

Before acceptance, each sample must pass:

- answer-only leakage review
- title/source-name leakage review
- subtitle/OCR/overlay review from first/middle/last and sparse frames
- single-frame insufficiency review
- sparse-frame shortcut review
- full dynamic-knowledge support review

In practice, accepted samples should have:

- `answer_only_leakage=low`
- `single_frame_sufficient=no`
- `dynamic_knowledge_supported=yes`
- no visible subtitle/OCR text that directly names the correct knowledge point
