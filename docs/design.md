# Benchmark Design

DynaKnow-Video evaluates dynamic video concept recognition: a model must
identify the named concept demonstrated by a temporally evolving process in a
video.

The benchmark is intentionally narrower than general video QA. It should test
whether a model can connect visible dynamics to a reusable mechanism or concept,
not whether it can recognize an object, read a title card, exploit source
metadata, or produce a broad caption.

## Core Task

```text
Which named dynamic concept is instantiated by the temporally evolving process in this video?
```

Current VDCR v1 is a direct-answer benchmark. The model gives the short
canonical concept name in English or Chinese. A four-choice MCQ file is derived
from the direct-answer gold set for closed-set recognition analysis, but MCQ is
not the primary release format.

## What Counts

An accepted sample must show a temporal process whose mechanism cannot be
identified from a single frame alone. Examples include propagation, instability,
growth direction, phase or reaction dynamics, transport, deformation, collective
motion, and other changes where the sequence matters.

The answer should be a named or well-defined mechanism-level concept, such as
`Rayleigh-Plateau Breakup`, `Phototropism`, `Belousov-Zhabotinsky Reaction`, or
`Bubble-Net Feeding`.

## What Does Not Count

Reject or keep in review clips whose best answer is only a broad event or object
description, such as:

- a plant grows;
- liquid changes color;
- objects move;
- a machine operates;
- a candle burns;
- an avalanche happens.

The benchmark should not reward source-page memorization, OCR, subtitles,
narration, or title matching.

## Current Release

The current runnable release is `release/v1/`. It contains 114 source-hidden
direct-answer samples across biology, chemistry/materials, earth/environment,
and physics. See `release/v1/README.md` for release contents and validation.

The original proposal remains in
`dynamic_video_knowledge_benchmark_proposal.md`; this file is the shorter
current-design entry point for contributors.
