"""Unit-test template for frequency modules (Owners: Members 1 & 2, M3).

Remove `@unittest.skip` decorators once `frequency_masks.py` and `frequency.py`
are implemented in Milestone 3.
"""

from __future__ import annotations

import unittest

import numpy as np

from src.frequency import apply_frequency_mask, compute_fft_spectrum
from src.frequency_masks import (
    butterworth_frequency_mask,
    ideal_frequency_mask,
)


@unittest.skip("TODO(Members 1 & 2, M3): Implement frequency modules.")
class TestFrequencyDomain(unittest.TestCase):
    """Verify radial symmetry, DC value, and FFT round-trip energy."""

    def test_ideal_and_butterworth_masks_bounds_and_dc(self) -> None:
        """LPF masks must equal 1.0 at center DC and lie in [0.0, 1.0]."""
        ideal_lp = ideal_frequency_mask((15, 15), cutoff=4.0, highpass=False)
        bw_lp = butterworth_frequency_mask(
            (15, 15), cutoff=4.0, order=2, highpass=False
        )
        self.assertEqual(ideal_lp[7, 7], 1.0)
        self.assertAlmostEqual(float(bw_lp[7, 7]), 1.0, places=8)
        self.assertTrue(np.all((bw_lp >= 0.0) & (bw_lp <= 1.0)))

    def test_all_pass_mask_preserves_spatial_image(self) -> None:
        """Applying an all-ones mask must reconstruct the original image."""
        img = np.arange(64, dtype=np.uint8).reshape(8, 8)
        fshift, spec = compute_fft_spectrum(img)
        self.assertEqual(fshift.shape, (8, 8))
        self.assertEqual(spec.dtype, np.uint8)
        recon = apply_frequency_mask(img, np.ones((8, 8), dtype=np.float64))
        self.assertTrue(np.array_equal(recon, img))


if __name__ == "__main__":
    unittest.main()
