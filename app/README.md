# SolarEye Interactive Classical DIP Inspection App (`app/`)

**Owner:** Member 1 (Integration) — Planned for Milestone 4 Deployment
**Status:** Milestone 1/2 UI Skeleton; only Baselines 0 and 1 are active.

Run from the integrated repository:
```bash
python -m streamlit run app/streamlit_app.py
```
Upload an EL image. Inspect the baseline mask, overlay, histogram, centered Fourier
spectrum and controlled degradations. Optional ground-truth comparison is for
development images only during M1/M2. A/B/C are future-stage interfaces.
The app does not certify PV safety or measure electrical power loss.
