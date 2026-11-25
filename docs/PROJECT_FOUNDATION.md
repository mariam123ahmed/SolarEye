# Milestone 1 — Project foundation and metric selection

**Owner for review and implementation:** Mariam (Team Leader).
**Status:** AI-assisted working draft; pending team review and instructor approval of the four-member team. This commit is not evidence of independent student authorship or completed experiments.

## Problem formulation
SolarEye is an academic prototype for photovoltaic quality-inspection engineers who need to locate and quantify defects in supported electroluminescence (EL) images. It takes a cell image and returns a binary defect mask, an overlay and image-based defect measurements. False negatives miss potentially relevant defects, while false positives increase unnecessary inspection workload. This is not a certified industrial test, an electrical-efficiency measurement, or a detector of EL-only defects from ordinary phone photos.

## Input and output
- Candidate dataset: MSPS, https://zenodo.org/records/21549573, CC BY 4.0 (attribution required); source code reference https://github.com/wch313/MSPS-Dataset.
- Expected input: grayscale EL image represented as uint8, 0–255; archive properties and masks must be verified by the data engineer.
- Output: spatially aligned binary mask (0 background, 1 defect), defect area fraction and connected region measurements; optional overlay.
- Primary metric: IoU = intersection / union of predicted and reference defect masks. IoU penalizes both false positives and false negatives, unlike raw pixel accuracy which can hide poor detection of sparse defects. Define both-empty IoU as 1 and record this convention.
- Secondary metrics: precision, recall, Dice and measured runtime. MSE and PSNR are used for controlled restoration experiments, not as substitutes for task performance.

## Scope and research question
How effectively can classical image processing detect and quantify photovoltaic defects under real image degradation without learned models? Compare two required unmodified baselines on development data: raw grayscale threshold 127 (dark foreground) and Otsu followed by one rectangular 3x3 opening. Document poor results honestly. Advanced methods remain reserved for Milestone 3.

## Team responsibilities
Mariam: metrics, integration, configuration, evaluation and Colab.
Fatma: dataset qualification, loader, manifests, controlled noise.
Fatima: image analysis, histograms, spectra and resolution/gray-level study.
Habiba: baseline design, segmentation, morphology and baseline tests.

## Milestone 1 acceptance checklist
- [ ] Team reviews and approves problem and primary metric.
- [ ] Data engineer verifies dataset criteria and attribution.
- [ ] Confirm instructor approval for four members.
- [ ] Peer review each member's actual contribution.
- [ ] Keep test images out of method selection.
- [ ] Merge reviewed PRs and tag only after the checkpoint is genuinely complete.

## References
- CSE281 Digital Image Processing Course Project Specification, sections 1, 3.1–3.3, 4 and 5.
- MSPS publisher and repository links above.

Mariam should review, revise and explain this draft before requesting peer review. AI assistance must be disclosed in the report.
