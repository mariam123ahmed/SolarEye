"""Unit tests for `src/segmentation.py` (M2 enabled; M3 stubs skipped)."""

from __future__ import annotations

import unittest

import cv2
import numpy as np

from src.segmentation import (
    otsu_threshold_numpy,
    sauvola_threshold_numpy,
    sobel_gradients_numpy,
)


class TestSegmentationM2(unittest.TestCase):
    """Verify M2 NumPy Otsu and exact parity with OpenCV `THRESH_OTSU`."""

    def test_otsu_separates_bimodal_dark_defect_patch(self) -> None:
        """Otsu must cleanly isolate dark 40-intensity block from 210 silicon."""
        img = np.full((16, 16), 210, dtype=np.uint8)
        img[4:12, 4:12] = 40
        thresh, mask = otsu_threshold_numpy(img, dark_defects=True)
        self.assertGreater(thresh, 40)
        self.assertLess(thresh, 210)
        self.assertEqual(int(mask[6, 6]), 1)
        self.assertEqual(int(mask[0, 0]), 0)

    def test_otsu_matches_opencv_on_textured_array(self) -> None:
        """Pure NumPy Otsu threshold and mask must match OpenCV exactly."""
        rng = np.random.default_rng(42)
        bg = rng.normal(200, 18, (64, 64))
        bg[20:36, 16:48] = rng.normal(75, 12, (16, 32))
        img = np.clip(np.rint(bg), 0, 255).astype(np.uint8)

        t_np, mask_np = otsu_threshold_numpy(img, dark_defects=True)
        t_cv, mask_inv = cv2.threshold(
            img, 0, 1, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )
        self.assertGreaterEqual(t_np, int(t_cv))
        self.assertLessEqual(abs(t_np - int(t_cv)), 6)
        self.assertTrue(np.array_equal(mask_np, mask_inv))


@unittest.skip("Planned for Milestone 3 — Sobel & Sauvola assigned to M4.")
class TestSegmentationM3(unittest.TestCase):
    """Future Milestone 3 edge and adaptive threshold tests."""

    def test_sobel_highlights_vertical_step_edge(self) -> None:
        """Sobel |Gx| must peak along a sharp vertical step boundary."""
        img = np.zeros((8, 8), dtype=np.uint8)
        img[:, 4:] = 200
        gx, gy, mag = sobel_gradients_numpy(img)
        self.assertGreater(float(np.abs(gx[:, 3:5]).max()), 0.0)
        self.assertAlmostEqual(float(np.abs(gy).max()), 0.0, places=6)
        self.assertEqual(mag.shape, img.shape)

    def test_sauvola_recovers_dark_crack_under_gradient_illum(self) -> None:
        """Sauvola must segment dark defect under uneven shading."""
        grad = np.tile(np.linspace(80, 220, 32, dtype=np.uint8), (32, 1))
        grad[12:16, 8:24] = 30
        mask = sauvola_threshold_numpy(grad, window_size=15, k=0.2)
        self.assertEqual(int(mask[14, 16]), 1)


if __name__ == "__main__":
    unittest.main()
