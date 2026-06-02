# Curated Sourcing Playbook

## Goal

Find public or license-verifiable videos where the answer is a reusable knowledge point demonstrated by temporal change.

Use curated sourcing when Commons category/search APIs are noisy or rate-limited.

## Source Priority

Use sources in this order:

1. Wikimedia Commons real-world videos with stable file pages and direct media URLs.
2. Government/public-institution media with public-domain or explicit reuse terms.
3. University/OER demonstration media with clear license terms.
4. Open archive or stock platforms only when the clip is real-world, non-explanatory, license-clear, and downloadable under the project's terms.

Do not use a source if the only available evidence is a transcript, lecture explanation, animation, simulation, or paper-supplement visualization.

Keep provenance in manifests, not in evaluation samples. The release JSONL should point to `local_media`; source page, direct URL, title, author, and license stay in the manifest.

## Prefer

- Titles that name the object or setup, not the target mechanism.
- 5-60 second clips, or clips with a clean 5-60 second segment.
- Visible start state, process, and end state.
- No subtitles/OCR overlays. A clip with visible text should be treated as review-risk even if the text looks harmless.
- Minimal narration, and no audio should be needed to answer.
- Everyday demonstrations of physics, chemistry, biology, or causal mechanisms.

Examples:

- `pool break` can be useful for collision momentum transfer.
- `water drop slow motion` can be useful for falling motion or impact dynamics.
- `bimetal coil reacts to heat` can be useful for uneven thermal expansion.
- `iodine clock` can be useful for reaction color change if the question asks the generic knowledge point.

## Reject During Sourcing

- Title directly names the target knowledge point: `phototropism`, `surface tension`, `magnetic field`, `filtration`, `pendulum`.
- A single frame would make the answer obvious.
- Specialist paper supplementary videos or microscopy requiring domain-specific interpretation.
- Animation/simulation unless building a separate synthetic split.
- Audio-only or performance videos where the mechanism is not visible.
- Broad plant time-lapses unless the mapped plant process is exact.
- Videos where the source URL, title, subtitle, or overlay states the correct option.
- Videos with burned-in formulas, labels, or explanatory captions that name the mechanism, unless a clean segment can remove them.
- Videos with title cards, end cards, lower thirds, captions, subtitles, or visible board/slide text that make OCR useful for answering.
- Source pages whose title or thumbnail leaks the answer and cannot be hidden from the evaluation setting.

## Intake Format

Fill:

- `templates/curated_source_intake.csv`

Then run:

```bash
python /root/public/jasonshu/dynaknow_video/scripts/import_curated_sources.py \
  --input /root/public/jasonshu/dynaknow_video/templates/curated_source_intake.csv \
  --output /root/public/jasonshu/dynaknow_video/data/candidate_videos_curated_next.csv \
  --start-index 1 \
  --skip-existing /root/public/jasonshu/dynaknow_video/data/candidate_videos_merged.csv

python /root/public/jasonshu/dynaknow_video/scripts/filter_candidate_quality.py \
  --input /root/public/jasonshu/dynaknow_video/data/candidate_videos_curated_next.csv \
  --priority-output /root/public/jasonshu/dynaknow_video/data/candidate_quality_priority_curated_next.csv \
  --review-output /root/public/jasonshu/dynaknow_video/data/candidate_quality_manual_curated_next.csv \
  --exclude-output /root/public/jasonshu/dynaknow_video/data/candidate_quality_exclude_curated_next.csv
```

Only priority/manual rows should advance to draft MCQ generation.
