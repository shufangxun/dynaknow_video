# v0.5 Release Report

Date: 2026-06-01

## Release Package

Directory:

- `release/v0_5/`

Files:

- `dynaknow_video_pilot_v0_5.jsonl`
- `dynaknow_video_pilot_v0_5_balanced.jsonl`
- `dynaknow_video_pilot_v0_5_manifest.csv`
- `answer_only_tasks_v0_5.jsonl`
- `frame_shortcut_tasks_v0_5.jsonl`
- `shortcut_run_manifest_v0_5.csv`
- `answer_only_tasks_v0_5_balanced.jsonl`
- `frame_shortcut_tasks_v0_5_balanced.jsonl`
- `shortcut_run_manifest_v0_5_balanced.csv`
- `combined_gold_v0_5_balanced.jsonl`
- `stats_v0_5.md`
- `stats_v0_5_balanced.md`
- `README.md`

## Counts

- release samples: 8
- answer-only tasks: 8
- frame shortcut tasks: 32
- shortcut run manifest rows: 3
- balanced answer distribution: A/B/C/D = 2/2/2/2
- combined scoring rows: 48

## Interpretation

This release is a pilot dataset, not the final 200-300 item benchmark.

It is useful for:

- validating the data format,
- running a first model smoke test,
- checking answer-only and static-frame shortcut behavior,
- demonstrating the dynamic-knowledge recognition task.

It should not be used as a final leaderboard dataset.

## Current Accepted Knowledge Points

- Collisions transfer momentum between objects.
- Materials can expand unevenly when heated.
- Some chemical reactions produce color change.
- Surface tension can support or reshape small liquid structures.
- A pendulum exchanges gravitational potential energy and kinetic energy.
- Unsupported objects accelerate downward under gravity.
- Vibration can cause granular materials to segregate by particle size.

## Next Step

Run baseline inference on:

- full video input using `prompts/video_knowledge_question.md`,
- `release/v0_5/dynaknow_video_pilot_v0_5_balanced.jsonl`,
- `release/v0_5/answer_only_tasks_v0_5_balanced.jsonl`,
- `release/v0_5/frame_shortcut_tasks_v0_5_balanced.jsonl`.

Then report:

- full-video accuracy,
- answer-only accuracy,
- single-frame accuracy,
- sparse-frame accuracy,
- Dynamic Necessity Gap.

The local evaluator is documented in:

- `reports/v0_5_evaluation_harness_report.md`
