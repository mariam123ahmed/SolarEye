"""Batch evaluation, experiment logging, and failure analysis (M2/M4).

Owners: Member 1 (Evaluation & Logger) and Member 4 (Failure Analysis).
Implements Milestone 2 experiment logging, split evaluation, per-image
metrics CSV export, and side-by-side comparison figure rendering.
Milestone 4 failure taxonomy (`>=20` worst test cases) remains planned.
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "mpl"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src import EXPERIMENT_LOG_COLUMNS
from src.config import get_project_root
from src.data import load_image_mask_pair
from src.metrics import (
    compute_area_error,
    compute_count_error,
    compute_dice,
    compute_iou,
    compute_precision_recall,
)
from src.pipeline import run_single_image


def _resolve_git_commit() -> str:
    """Return short HEAD commit hash or 'untracked' when outside a Git repo."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(get_project_root()),
            capture_output=True,
            text=True,
            check=True,
        )
        return res.stdout.strip() or "untracked"
    except Exception:
        return "untracked"


def _resolve_repo_path(path: str | Path) -> Path:
    """Resolve `path` relative to project root when not already absolute."""
    p = Path(path)
    if p.is_absolute() or p.exists():
        return p
    return get_project_root() / p


def log_experiment(
    row_data: dict[str, Any],
    log_csv: str | Path = "experiments/experiment_log.csv",
) -> Path:
    """Append one validated 16-column row to `experiments/experiment_log.csv`."""
    csv_path = Path(log_csv)
    if not csv_path.is_absolute():
        csv_path = get_project_root() / csv_path
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    defaults: dict[str, Any] = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "git_commit": _resolve_git_commit(),
        "notes": "",
    }
    merged = {**defaults, **row_data}
    missing = [col for col in EXPERIMENT_LOG_COLUMNS if col not in merged]
    if missing:
        raise ValueError(
            f"Experiment log row missing required columns: {missing}"
        )

    write_header = not csv_path.exists() or csv_path.stat().st_size == 0
    with open(csv_path, "a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=EXPERIMENT_LOG_COLUMNS)
        if write_header:
            writer.writeheader()
        writer.writerow({col: merged[col] for col in EXPERIMENT_LOG_COLUMNS})
    return csv_path


def save_comparison_figure(
    image: np.ndarray,
    gt_mask: np.ndarray,
    pred_mask: np.ndarray,
    out_path: Path,
    title: str,
) -> Path:
    """Save 4-panel `[Raw | Ground Truth | Prediction | Error Map]` figure."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    err_rgb = np.zeros((*gt_mask.shape, 3), dtype=np.uint8)
    tp = (pred_mask == 1) & (gt_mask == 1)
    fp = (pred_mask == 1) & (gt_mask == 0)
    fn = (pred_mask == 0) & (gt_mask == 1)
    err_rgb[tp] = [46, 204, 113]   # Green = TP
    err_rgb[fp] = [231, 76, 60]    # Red = FP
    err_rgb[fn] = [241, 196, 15]   # Yellow = FN

    fig, axes = plt.subplots(1, 4, figsize=(15, 3.8))
    axes[0].imshow(image, cmap="gray", vmin=0, vmax=255)
    axes[0].set_title("Input EL Image")
    axes[1].imshow(gt_mask * 255, cmap="gray", vmin=0, vmax=255)
    axes[1].set_title("Ground Truth")
    axes[2].imshow(pred_mask * 255, cmap="gray", vmin=0, vmax=255)
    axes[2].set_title("Prediction")
    axes[3].imshow(err_rgb)
    axes[3].set_title("Error (G=TP, R=FP, Y=FN)")
    for ax in axes:
        ax.axis("off")
    fig.suptitle(title, fontsize=10)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_path


def evaluate_manifest(
    manifest_csv: str | Path,
    cfg: dict[str, Any],
    out_dir: str | Path,
    log_csv: str | Path = "experiments/experiment_log.csv",
    author: str = "AI-assisted reference; runner attribution pending",
    config_file: str = "",
    max_samples: int | None = None,
    save_figures: bool = True,
    append_to_log: bool = True,
) -> dict[str, Any]:
    """Evaluate a configured pipeline across all image/mask pairs in a split."""
    manifest_path = _resolve_repo_path(manifest_csv)
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest CSV not found: {manifest_path}")

    df = pd.read_csv(manifest_path)
    if df.empty:
        raise ValueError(f"Manifest CSV is empty: {manifest_path}")
    if max_samples is not None and max_samples > 0:
        df = df.iloc[:max_samples].reset_index(drop=True)

    out_path = _resolve_repo_path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    pipeline_name = str(cfg["pipeline"])
    split_name = manifest_path.stem.replace("_manifest", "")

    records: list[dict[str, Any]] = []
    cached_samples: list[tuple[float, str, np.ndarray, np.ndarray, np.ndarray]] = []
    for row in df.to_dict(orient="records"):
        img_p = _resolve_repo_path(row["image_path"])
        msk_p = _resolve_repo_path(row["mask_path"])
        img, gt = load_image_mask_pair(img_p, msk_p, grayscale=True)
        res = run_single_image(img, cfg)
        pred = res["mask"]

        iou = compute_iou(pred, gt)
        dice = compute_dice(pred, gt)
        prec, rec = compute_precision_recall(pred, gt)
        area_err = compute_area_error(pred, gt)
        cnt_err = compute_count_error(pred, gt)

        records.append(
            {
                "image_id": row["image_id"],
                "pipeline": pipeline_name,
                "iou": iou,
                "dice": dice,
                "precision": prec,
                "recall": rec,
                "area_error_pct": area_err,
                "count_error": cnt_err,
                "pred_area_pct": res["stats"]["area_pct"],
                "pred_count": res["stats"]["defect_count"],
                "runtime_s": res["runtime_s"],
            }
        )
        if save_figures:
            cached_samples.append((iou, str(row["image_id"]), img, gt, pred))

    res_df = pd.DataFrame(records)
    per_img_csv = out_path / f"{pipeline_name}_{split_name}_per_image.csv"
    res_df.to_csv(per_img_csv, index=False)

    summary: dict[str, Any] = {
        "pipeline": pipeline_name,
        "split": split_name,
        "num_images": int(len(res_df)),
        "mean_iou": float(res_df["iou"].mean()),
        "std_iou": float(res_df["iou"].std(ddof=0)),
        "min_iou": float(res_df["iou"].min()),
        "max_iou": float(res_df["iou"].max()),
        "mean_dice": float(res_df["dice"].mean()),
        "mean_precision": float(res_df["precision"].mean()),
        "mean_recall": float(res_df["recall"].mean()),
        "mean_area_error_pct": float(res_df["area_error_pct"].mean()),
        "mean_count_error": float(res_df["count_error"].mean()),
        "mean_runtime_s": float(res_df["runtime_s"].mean()),
        "total_runtime_s": float(res_df["runtime_s"].sum()),
        "per_image_csv": per_img_csv.as_posix(),
    }

    if save_figures and cached_samples:
        cached_samples.sort(key=lambda item: item[0])
        fig_dir = get_project_root() / "experiments" / "figures"
        worst_iou, worst_id, w_img, w_gt, w_pred = cached_samples[0]
        best_iou, best_id, b_img, b_gt, b_pred = cached_samples[-1]
        safe_w = worst_id.replace("/", "_")
        safe_b = best_id.replace("/", "_")
        save_comparison_figure(
            w_img,
            w_gt,
            w_pred,
            fig_dir / f"{pipeline_name}_{split_name}_worst_{safe_w}.png",
            f"{pipeline_name} ({split_name}) Worst: {worst_id} | IoU={worst_iou:.4f}",
        )
        save_comparison_figure(
            b_img,
            b_gt,
            b_pred,
            fig_dir / f"{pipeline_name}_{split_name}_best_{safe_b}.png",
            f"{pipeline_name} ({split_name}) Best: {best_id} | IoU={best_iou:.4f}",
        )

    sec_metrics = json.dumps(
        {
            "std_iou": round(summary["std_iou"], 6),
            "mean_dice": round(summary["mean_dice"], 6),
            "mean_precision": round(summary["mean_precision"], 6),
            "mean_recall": round(summary["mean_recall"], 6),
            "mean_area_err_pct": round(summary["mean_area_error_pct"], 6),
            "mean_count_err": round(summary["mean_count_error"], 4),
            "n": summary["num_images"],
        }
    )
    if append_to_log:
        log_experiment(
            {
                "run_id": cfg.get("run_id", f"EXP-{pipeline_name}"),
                "author": author,
                "pipeline": pipeline_name,
                "stage": "segmentation_baseline",
                "method": str(
                    cfg.get("segmentation", {}).get("method", pipeline_name)
                ),
                "parameters": json.dumps(cfg.get("segmentation", {})),
                "random_seed": cfg.get("random_seed", 42),
                "processing_time_s": round(summary["total_runtime_s"], 4),
                "dataset_split": split_name,
                "metric_name": "mean_iou",
                "metric_value": round(summary["mean_iou"], 6),
                "secondary_metrics": sec_metrics,
                "config_file": Path(config_file).as_posix()
                if config_file
                else "",
                "notes": f"Evaluated {summary['num_images']} images on {split_name}",
            },
            log_csv=log_csv,
        )
    return summary


def run_failure_analysis(
    per_image_csv: str | Path,
    out_dir: str | Path,
    top_k: int = 20,
) -> list[dict[str, Any]]:
    """Select and group the `top_k` worst IoU cases for failure taxonomy."""
    raise NotImplementedError(
        "Planned for Milestone 4 — assigned to Member 4. "
        "TODO(M4): Sort test results ascending by IoU and categorize."
    )


def summarize_stage_runtimes(
    stage_timings: list[dict[str, float]],
) -> dict[str, float]:
    """Aggregate per-stage mean and total CPU runtime across a split."""
    raise NotImplementedError(
        "Planned for Milestone 4 — assigned to Member 1. "
        "TODO(M4): Verify total batch runtime remains well under 10 min CPU."
    )
