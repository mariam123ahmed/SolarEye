# SolarEye

CSE281 Digital Image Processing — Alamein International University.

Classical photovoltaic electroluminescence defect segmentation and quantification. No ML/DL.

## Phase 1 — Milestones 1 and 2

This is the shared AI-assisted starter, not a completed milestone or a record of student-authored work. The team will implement/adapt, test and review its own contributions on feature branches. AI assistance must be disclosed.

Candidate dataset: MSPS, https://zenodo.org/records/21549573 (CC BY 4.0, attribution required).
Primary metric: IoU. Baselines: raw grayscale threshold 127 and Otsu plus one 3x3 opening.
Team size of four is pending instructor approval.

## Ownership
| Member | Role | Ownership | Milestone 1 branch |
| --- | --- | --- | --- |
| Mariam (Member 1) | Team Leader | Metrics, configuration, integration, pipeline.py, evaluation and Colab | `feature/m01-mariam-foundation` |
| Fatma (Member 2) | Data Engineer | Dataset validation, data loader, manifests and noise generation | `feature/m01-fatma-data` |
| Fatima (Member 3) | Image Analysis Engineer | Image analysis, EDA figures and tables | `feature/m01-fatima-analysis` |
| Habiba (Member 4) | Segmentation Engineer | Segmentation, morphology and baseline algorithm tests | `feature/m01-habiba-segmentation` |

Use the named branches for current Milestone 1 work. The earlier role-based branches are retained as unused starter references. Every member must contribute and review genuine work.

Use only development data for analysis and tuning. Keep test data held out. Do not commit raw data or ZIP files. Add CI after the first real tests are merged; the full suite runs at the Phase 1 integration gate.

See docs/INTEGRATION_CONTRACT.md and docs/GITHUB_WORKFLOW.md for shared conventions.
