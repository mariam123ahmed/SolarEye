"""Unit and integration tests for Baselines 0 and 1 (Members 1 & 4, M2)."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

import numpy as np
import pandas as pd
from PIL import Image

from src.config import load_config
from src.evaluate import evaluate_manifest
from src.pipeline import run_baseline_0, run_baseline_1


class TestBaselines(unittest.TestCase):
    """Verify Baseline 0 purity, Baseline 1 polarity, and batch evaluation."""

    def test_baseline_0_detects_dark_defect_below_127(self) -> None:
        """Dark defect (<127) must map to mask=1; bright silicon (>127) -> 0."""
        img = np.full((16, 16), 200, dtype=np.uint8)
        img[4:8, 4:8] = 50
        res = run_baseline_0(img, threshold=127, dark_defects=True)
        mask = res["mask"]
        self.assertEqual(mask.shape, img.shape)
        self.assertEqual(mask.dtype, np.uint8)
        self.assertTrue(set(np.unique(mask).tolist()).issubset({0, 1}))
        self.assertEqual(int(mask[5, 5]), 1)
        self.assertEqual(int(mask[0, 0]), 0)

    def test_baseline_1_removes_isolated_1px_speckle(self) -> None:
        """3x3 opening in Baseline 1 must remove single-pixel dark noise."""
        img = np.full((24, 24), 210, dtype=np.uint8)
        img[2, 2] = 10
        img[10:16, 10:16] = 30
        res = run_baseline_1(img, opening_size=3, dark_defects=True)
        mask = res["mask"]
        self.assertEqual(mask.shape, img.shape)
        self.assertEqual(int(mask[2, 2]), 0)
        self.assertEqual(int(mask[12, 12]), 1)

    def test_evaluate_manifest_integration_on_synthetic_dev_split(self) -> None:
        """Batch evaluator must export per-image CSV, figures, and log row."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            img = np.full((32, 32), 205, dtype=np.uint8)
            img[8:18, 8:18] = 30
            gt = np.zeros((32, 32), dtype=np.uint8)
            gt[8:18, 8:18] = 255
            img_p = tmp / "sample_0.png"
            msk_p = tmp / "sample_0_mask.png"
            Image.fromarray(img).save(img_p)
            Image.fromarray(gt).save(msk_p)

            manifest = tmp / "dev_manifest.csv"
            pd.DataFrame(
                [
                    {
                        "image_id": "sample_0",
                        "image_path": str(img_p),
                        "mask_path": str(msk_p),
                    }
                ]
            ).to_csv(manifest, index=False)

            cfg = load_config("configs/baseline_1.yaml")
            log_csv = tmp / "experiment_log.csv"
            summary = evaluate_manifest(
                manifest_csv=manifest,
                cfg=cfg,
                out_dir=tmp / "out",
                log_csv=log_csv,
                save_figures=False,
            )
            self.assertEqual(summary["num_images"], 1)
            self.assertAlmostEqual(summary["mean_iou"], 1.0, places=6)
            self.assertTrue(Path(summary["per_image_csv"]).exists())
            self.assertTrue(log_csv.exists())


if __name__ == "__main__":
    unittest.main()
