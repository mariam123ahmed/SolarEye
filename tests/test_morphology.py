"""Unit tests for `src/morphology.py` (M2 enabled; M3 stubs skipped)."""

from __future__ import annotations

import unittest

import cv2
import numpy as np

from src.morphology import (
    binary_dilation_numpy,
    binary_erosion_numpy,
    morph_opening,
    remove_small_components,
)


class TestMorphologyM2(unittest.TestCase):
    """Verify M2 NumPy erosion/dilation/opening and OpenCV parity."""

    def test_erosion_eliminates_isolated_pixel(self) -> None:
        """3x3 erosion on a single foreground pixel must return all zeros."""
        mask = np.zeros((5, 5), dtype=np.uint8)
        mask[2, 2] = 1
        eroded = binary_erosion_numpy(mask, ksize=3, shape="rect")
        self.assertEqual(int(eroded.sum()), 0)

    def test_dilation_bridges_1px_crack_gap(self) -> None:
        """3x3 dilation must bridge two 1-pixel separated crack segments."""
        mask = np.zeros((5, 5), dtype=np.uint8)
        mask[2, 1] = 1
        mask[2, 3] = 1
        dilated = binary_dilation_numpy(mask, ksize=3, shape="rect")
        self.assertEqual(int(dilated[2, 2]), 1)

    def test_numpy_erosion_dilation_opening_match_opencv(self) -> None:
        """Pure NumPy erosion, dilation, and opening match OpenCV exactly."""
        rng = np.random.default_rng(42)
        mask = (rng.random((24, 24)) > 0.72).astype(np.uint8)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

        er_np = binary_erosion_numpy(mask, ksize=3, shape="rect")
        er_cv = cv2.erode(mask, kernel)
        self.assertTrue(np.array_equal(er_np, er_cv))

        di_np = binary_dilation_numpy(mask, ksize=3, shape="rect")
        di_cv = cv2.dilate(mask, kernel)
        self.assertTrue(np.array_equal(di_np, di_cv))

        op_np = morph_opening(mask, ksize=3, shape="rect")
        op_cv = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        self.assertTrue(np.array_equal(op_np, op_cv))


@unittest.skip("Planned for Milestone 3 — component pruning assigned to M4.")
class TestMorphologyM3(unittest.TestCase):
    """Future Milestone 3 morphology tests."""

    def test_small_component_removal(self) -> None:
        """min_area_px filtering must remove isolated specks."""
        mask = np.zeros((16, 16), dtype=np.uint8)
        mask[1, 1] = 1
        mask[8:13, 8:13] = 1
        pruned = remove_small_components(mask, min_area_px=10)
        self.assertEqual(int(pruned[1, 1]), 0)
        self.assertEqual(int(pruned[10, 10]), 1)


if __name__ == "__main__":
    unittest.main()
