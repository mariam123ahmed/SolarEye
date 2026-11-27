# Milestones 1 and 2 — integration readiness (AI-assisted review)

This is a checkpoint record, not a certification that the current GitHub branch or all individual contributions are complete.

## Local reference package evidence
The integrated M1/M2 review ZIP was independently extracted and tested: `python -m pytest -q` returned 26 passed, 10 skipped (1.05s). Skips are future-stage tests. This is evidence for the local ZIP, not for current main. Raw data was not downloaded again during this review.

The archived validation report in that ZIP records 1,507 matched pairs, 1,004 development and 503 held-out test images (split manifests), zero unmatched/corrupt/dimension mismatches and no exact duplicate image groups. The archived development baseline log records:

| Method | N (dev) | Mean IoU |
| --- | ---: | ---: |
| Raw grayscale threshold 127 | 1004 | 0.001159 |
| Otsu + one 3x3 opening | 1004 | 0.001860 |

These are previous AI-assisted reference results, not claimed new experiments or individual student work. Members must verify and interpret the evidence before acceptance. No test-set tuning.

## Required before closing M1/M2
- [ ] Mariam: review and upload metrics/tests, configuration, baseline orchestration and evaluation/Colab files.
- [ ] Fatma: reconcile PR #1 with the actual official split, validator output, manifests and common loader.
- [ ] Fatima: commit dev-only image analysis notebook, figures and findings-to-design decisions.
- [ ] Habiba: commit baseline implementations, morphology and tests, and verify baseline evidence.
- [ ] Each member documents actual contributions, including AI assistance, and runs relevant tests.
- [ ] Independent peer review of every PR; preserve existing commits and do not self-approve.
- [ ] Integrate reviewed work, rerun tests from the merged revision and record evidence.
- [ ] Instructor approval for the four-member team remains pending.
- [ ] Only tag completed checkpoints after these checks pass. Do not submit M3/M4 or bonus code in this checkpoint.

The course specification describes M1/M2 as suggested internal checkpoints; follow any separate instructor deadline for today.
