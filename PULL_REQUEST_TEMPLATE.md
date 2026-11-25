## Pull Request Summary
- **Milestone:** `M1` / `M2` / `M3` / `M4`
- **Linked Issue:** `#<issue-number>`
- **Owner:** Member `<1 / 2 / 3 / 4>`
- **Assigned Peer Reviewer:** Member `<different-member>` (Tech Lead PRs must also be peer-reviewed)

## Changes Made
- Describe files modified and contracts preserved.

## Classical DIP & Integration Contract Checklist
- [ ] **Zero ML/DL Policy:** No `torch`, `tensorflow`, `keras`, `sklearn` classifiers, `timm`, or pretrained weights.
- [ ] **Data & Polarity Contract:** Grayscale `uint8 [0, 255]`; masks `uint8 {0, 1}` with `1 = dark defect foreground`; `BGR -> RGB` applied before display.
- [ ] **Border & Seed Parity:** `np.pad(..., mode="reflect")` matches `cv2.BORDER_REFLECT_101`; `seed=42` (`np.random.default_rng(42)`).
- [ ] **Code Style:** Every Python line `<= 95` characters; all modules, classes, and functions have docstrings; zero hardcoded machine paths.
- [ ] **Split Hygiene:** No tuning or exploratory analysis touched `data/splits/test_manifest.csv`.
- [ ] **Verification:** `python -m unittest discover -s tests -v` / `pytest` passes locally after final edit.
