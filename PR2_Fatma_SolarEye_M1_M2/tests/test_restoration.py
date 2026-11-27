"""Unit-test template for `src/restoration.py` (Owner: Member 2, M3).

Remove `@unittest.skip` decorators once Member 2 completes Milestone 3.
"""

from __future__ import annotations

import unittest

import numpy as np

from src.restoration import (
    alpha_trimmed_mean_filter_numpy,
    median_filter_numpy,
)


@unittest.skip("TODO(Member 2, M3): Implement src/restoration.py then enable.")
class TestRestoration(unittest.TestCase):
    """Verify hand-worked 3x3 median and alpha-trimmed mean restoration."""

    def test_median_filter_removes_center_impulse_outlier(self) -> None:
        """3x3 median filter must suppress a single 255 salt spike."""
        patch = np.full((5, 5), 100, dtype=np.uint8)
        patch[2, 2] = 255
        denoised = median_filter_numpy(patch, ksize=3, border_mode="reflect")
        self.assertEqual(denoised.dtype, np.uint8)
        self.assertEqual(int(denoised[2, 2]), 100)

    def test_alpha_trimmed_mean_rejects_salt_and_pepper_pair(self) -> None:
        """With d=2 on 3x3 window, discarding min(0) & max(255) recovers 100."""
        patch = np.full((5, 5), 100, dtype=np.uint8)
        patch[1, 1] = 0
        patch[3, 3] = 255
        denoised = alpha_trimmed_mean_filter_numpy(patch, ksize=3, d=2)
        self.assertEqual(int(denoised[2, 2]), 100)


if __name__ == "__main__":
    unittest.main()
