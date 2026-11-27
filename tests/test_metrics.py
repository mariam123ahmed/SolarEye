"""Unit and edge-case tests for `src/metrics.py` (Owner: Member 1, M2)."""

from __future__ import annotations

import math
import unittest

import numpy as np

from src.metrics import (
    compute_area_error,
    compute_count_error,
    compute_dice,
    compute_iou,
    compute_mse,
    compute_precision_recall,
    compute_psnr,
)


class TestMetrics(unittest.TestCase):
    """Hand-worked and edge-case tests for quantitative evaluation metrics."""

    def test_mse_and_psnr_hand_worked_4x4(self) -> None:
        """Verify 4x4 MSE=2.0 and PSNR~45.12 dB without uint8 wraparound."""
        ref = np.full((4, 4), 100, dtype=np.uint8)
        target = ref.copy()
        target[0, 0] = 104
        target[1, 1] = 96
        self.assertAlmostEqual(compute_mse(ref, target), 2.0, places=8)
        expected_psnr = 10.0 * math.log10((255.0 ** 2) / 2.0)
        self.assertAlmostEqual(compute_psnr(ref, target), expected_psnr, 5)

    def test_mse_avoids_uint8_wraparound(self) -> None:
        """Ensure |0 - 255| equals 255^2 in MSE, not 1^2 from uint8 wrap."""
        a = np.zeros((2, 2), dtype=np.uint8)
        b = np.full((2, 2), 255, dtype=np.uint8)
        self.assertAlmostEqual(compute_mse(a, b), 255.0 ** 2, places=6)

    def test_psnr_identical_images_returns_inf(self) -> None:
        """Zero MSE must return +inf rather than raising ZeroDivisionError."""
        img = np.full((8, 8), 120, dtype=np.uint8)
        self.assertEqual(compute_mse(img, img), 0.0)
        self.assertTrue(math.isinf(compute_psnr(img, img)))

    def test_iou_dice_precision_recall_hand_worked(self) -> None:
        """Verify 4x4 mask metrics (TP=2, FP=1, FN=1 -> IoU=0.5, Dice=2/3)."""
        pred = np.zeros((4, 4), dtype=np.uint8)
        gt = np.zeros((4, 4), dtype=np.uint8)
        pred[0, 0] = pred[0, 1] = pred[1, 0] = 1
        gt[0, 0] = gt[1, 0] = gt[1, 1] = 1
        self.assertAlmostEqual(compute_iou(pred, gt), 0.5, places=6)
        self.assertAlmostEqual(compute_dice(pred, gt), 2.0 / 3.0, places=6)
        prec, rec = compute_precision_recall(pred, gt)
        self.assertAlmostEqual(prec, 2.0 / 3.0, places=6)
        self.assertAlmostEqual(rec, 2.0 / 3.0, places=6)
        self.assertAlmostEqual(compute_area_error(pred, gt), 0.0, places=6)
        self.assertEqual(compute_count_error(pred, gt), 0)

    def test_empty_mask_edge_cases_and_invalid_inputs(self) -> None:
        """Verify empty-mask handling, one-empty masks, and shape errors."""
        empty = np.zeros((4, 4), dtype=np.uint8)
        non_empty = np.zeros((4, 4), dtype=np.uint8)
        non_empty[1:3, 1:3] = 1

        self.assertEqual(compute_iou(empty, empty), 1.0)
        self.assertEqual(compute_dice(empty, empty), 1.0)
        self.assertEqual(compute_precision_recall(empty, empty), (1.0, 1.0))
        self.assertEqual(compute_area_error(empty, empty), 0.0)
        self.assertEqual(compute_count_error(empty, empty), 0)

        self.assertEqual(compute_iou(empty, non_empty), 0.0)
        self.assertEqual(compute_dice(empty, non_empty), 0.0)
        self.assertEqual(compute_precision_recall(empty, non_empty), (0.0, 0.0))
        self.assertAlmostEqual(
            compute_area_error(empty, non_empty), 25.0, places=6
        )
        self.assertEqual(compute_count_error(empty, non_empty), 1)

        bad_mask = np.zeros((4, 4), dtype=np.uint8)
        bad_mask[0, 0] = 255
        with self.assertRaises(ValueError):
            compute_iou(bad_mask, empty)
        with self.assertRaises(ValueError):
            compute_iou(empty, np.zeros((4, 5), dtype=np.uint8))
        with self.assertRaises(ValueError):
            compute_mse(empty, np.zeros((4, 5), dtype=np.uint8))


if __name__ == "__main__":
    unittest.main()
