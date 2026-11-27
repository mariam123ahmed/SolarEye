"""SolarEye Interactive Classical DIP Inspection Dashboard (Phase 1 Active).

Owner: Member 1 (Tech Lead, Integration & Metrics).
Implements functional Phase 1 Baseline Inspection across verified Baselines
0 and 1, with Pipelines A, B, and C disabled until Milestone 3 verification.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

import cv2
import numpy as np
import pandas as pd
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import get_project_root, load_config
from src.data import add_gaussian_noise, add_salt_pepper_noise
from src.metrics import (
    compute_area_error,
    compute_count_error,
    compute_dice,
    compute_iou,
    compute_precision_recall,
)
from src.pipeline import run_single_image

ACADEMIC_DISCLAIMER = (
    "Academic Classical DIP Prototype (CSE281): Outputs reflect experimental "
    "image-level defect morphology on Electroluminescence (EL) images only. "
    "They do NOT measure electrical power loss, do NOT certify PV safety, "
    "and conventional smartphone photos cannot reveal EL-only micro-cracks."
)

VERIFIED_PIPELINES: tuple[str, ...] = ("baseline_0", "baseline_1")
PLANNED_PIPELINES: tuple[str, ...] = (
    "pipeline_a",
    "pipeline_b",
    "pipeline_c",
)


def load_app_config(pipeline_name: str = "baseline_1") -> dict[str, Any]:
    """Load the selected YAML configuration relative to repository root."""
    cfg_path = get_project_root() / "configs" / f"{pipeline_name}.yaml"
    return load_config(cfg_path)


def decode_uploaded_image(file_obj: Any) -> np.ndarray:
    """Decode an uploaded image file into 2D `uint8` `[0, 255]` grayscale."""
    with Image.open(file_obj) as img:
        arr = np.asarray(img.convert("L"), dtype=np.uint8)
    return arr


def decode_uploaded_mask(
    file_obj: Any,
    expected_shape: tuple[int, int],
) -> np.ndarray:
    """Decode an uploaded ground-truth mask into `{0, 1}` matching shape."""
    with Image.open(file_obj) as img:
        if img.mode in ("P", "RGBA", "LA"):
            arr = np.asarray(img.convert("RGB"))
        else:
            arr = np.asarray(img)
    if arr.ndim == 3 and arr.shape[2] >= 3:
        binary = np.any(arr[..., :3] > 0, axis=2).astype(np.uint8)
    elif arr.ndim == 2:
        binary = (arr > 0).astype(np.uint8)
    else:
        raise ValueError(f"Unsupported mask shape: {arr.shape}")
    if binary.shape != expected_shape:
        binary = cv2.resize(
            binary,
            (expected_shape[1], expected_shape[0]),
            interpolation=cv2.INTER_NEAREST,
        )
        binary = (binary > 0).astype(np.uint8)
    return binary


def render_overlay_with_boxes(
    gray: np.ndarray,
    mask: np.ndarray,
    components: list[dict[str, Any]],
) -> np.ndarray:
    """Render RGB overlay highlighting defects in red and boxes in gold."""
    rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
    overlay = rgb.copy()
    overlay[mask == 1] = [231, 76, 60]
    blended = cv2.addWeighted(rgb, 0.65, overlay, 0.35, 0.0)
    for comp in components:
        x, y, w, h = comp["bbox_xywh"]
        cv2.rectangle(
            blended, (x, y), (x + w, y + h), (241, 196, 15), thickness=1
        )
    return blended


def apply_controlled_degradation(
    gray: np.ndarray,
    gauss_sigma: float = 0.0,
    sp_density: float = 0.0,
    contrast_alpha: float = 1.0,
    illum_strength: float = 0.0,
    blur_ksize: int = 1,
    seed: int = 42,
) -> np.ndarray:
    """Apply real controlled degradations in the Robustness Laboratory."""
    out = gray.astype(np.float64)
    if contrast_alpha != 1.0:
        out = 128.0 + contrast_alpha * (out - 128.0)
    if illum_strength > 0.0:
        h, w = out.shape
        xx = np.linspace(-1.0, 1.0, w, dtype=np.float64)
        yy = np.linspace(-1.0, 1.0, h, dtype=np.float64)
        grid_y, grid_x = np.meshgrid(yy, xx, indexing="ij")
        ramp = 1.0 - illum_strength * (0.5 * (grid_x + 1.0) + 0.3 * grid_y)
        out = out * np.clip(ramp, 0.2, 1.5)
    degraded = np.clip(np.rint(out), 0.0, 255.0).astype(np.uint8)
    if blur_ksize >= 3 and blur_ksize % 2 == 1:
        degraded = cv2.GaussianBlur(
            degraded, (blur_ksize, blur_ksize), 0, borderType=cv2.BORDER_REFLECT_101
        )
    if gauss_sigma > 0.0:
        degraded = add_gaussian_noise(degraded, sigma=gauss_sigma, seed=seed)
    if sp_density > 0.0:
        degraded = add_salt_pepper_noise(
            degraded, density=sp_density, salt_ratio=0.5, seed=seed
        )
    return degraded


def compute_centered_log_fft(gray: np.ndarray) -> np.ndarray:
    """Compute centered 2D FFT log-magnitude `[0, 255]` for display."""
    fshift = np.fft.fftshift(np.fft.fft2(gray.astype(np.float64)))
    mag = np.log1p(np.abs(fshift))
    max_val = float(mag.max())
    if max_val <= 0.0:
        return np.zeros_like(gray, dtype=np.uint8)
    return np.clip(np.rint(255.0 * mag / max_val), 0, 255).astype(np.uint8)


def run_ui_pipeline_hook(
    image: np.ndarray,
    pipeline_name: str,
) -> dict[str, Any]:
    """Execute a verified pipeline from `src.pipeline` on `image`."""
    if pipeline_name not in VERIFIED_PIPELINES:
        raise ValueError(
            f"Pipeline '{pipeline_name}' is planned for Milestone 3 and not "
            "yet verified for interactive execution."
        )
    cfg = load_app_config(pipeline_name)
    return run_single_image(image, cfg)


def build_inspection_report_md(
    image_name: str,
    pipeline_name: str,
    result: dict[str, Any],
    gt_metrics: dict[str, float] | None,
) -> str:
    """Build an exportable Markdown inspection summary report."""
    stats = result["stats"]
    lines = [
        "# SolarEye Experimental EL Inspection Report",
        f"- **Image:** `{image_name}`",
        f"- **Pipeline:** `{pipeline_name}`",
        f"- **Runtime (s):** `{result['runtime_s']:.6f}`",
        f"- **Detected Regions:** `{stats['defect_count']}`",
        f"- **Defective Area (%):** `{stats['area_pct']:.4f}%`",
        f"- **Defective Pixels:** `{stats['total_area_px']}`",
    ]
    if gt_metrics is not None:
        lines.extend(
            [
                f"- **IoU vs GT:** `{gt_metrics['iou']:.4f}`",
                f"- **Dice vs GT:** `{gt_metrics['dice']:.4f}`",
                f"- **Precision / Recall:** `{gt_metrics['precision']:.4f}` / "
                f"`{gt_metrics['recall']:.4f}`",
                f"- **Area Error (% pt):** `{gt_metrics['area_error_pct']:.4f}`",
                f"- **Count Error:** `{gt_metrics['count_error']}`",
            ]
        )
    lines.append("")
    lines.append(f"> **Disclaimer:** {ACADEMIC_DISCLAIMER}")
    return "\n".join(lines)


def main() -> None:
    """Render the SolarEye renewable-energy classical DIP dashboard."""
    try:
        import streamlit as st  # type: ignore
    except ImportError as exc:  # pragma: no cover - optional UI dependency
        raise RuntimeError(
            "Streamlit is not installed. Run `pip install -r requirements.txt`."
        ) from exc

    st.set_page_config(
        page_title="SolarEye | PV EL Classical DIP",
        layout="wide",
    )
    st.markdown(
        """
        <style>
        .solar-banner {
            padding: 0.9rem 1.2rem;
            border-radius: 8px;
            background: linear-gradient(90deg, #0b3b5b 0%, #146c53 100%);
            color: #ffffff;
            margin-bottom: 1rem;
        }
        </style>
        <div class="solar-banner">
          <h2 style="margin:0;">SolarEye — Classical PV EL Defect Inspection</h2>
          <p style="margin:0.2rem 0 0 0;">
            CSE281 Digital Image Processing | Phase 1 (Baselines 0 &amp; 1 Verified;
            Pipelines A/B/C Pending Milestone 3)
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.warning(ACADEMIC_DISCLAIMER)

    st.sidebar.header("Inspection Controls")
    pipeline_choice = st.sidebar.selectbox(
        "Verified Pipeline (Active)",
        list(VERIFIED_PIPELINES),
        index=1,
    )
    st.sidebar.caption(
        "Planned for M3 (disabled until verified): "
        + ", ".join(PLANNED_PIPELINES)
    )
    uploaded_img = st.sidebar.file_uploader(
        "Upload EL PV Cell Image (.png/.jpg/.bmp/.tif)",
        type=["png", "jpg", "jpeg", "bmp", "tif", "tiff"],
    )
    uploaded_gt = st.sidebar.file_uploader(
        "Optional Ground-Truth Mask (same dimensions)",
        type=["png", "jpg", "jpeg", "bmp", "tif", "tiff"],
    )

    sample_gray: np.ndarray | None = None
    sample_name = "no_image"
    if uploaded_img is not None:
        sample_gray = decode_uploaded_image(uploaded_img)
        sample_name = uploaded_img.name
    else:
        dev_csv = get_project_root() / "data" / "splits" / "dev_manifest.csv"
        if dev_csv.exists():
            dev_df = pd.read_csv(dev_csv)
            if not dev_df.empty and st.sidebar.checkbox(
                "Load Sample from Dev Manifest", value=True
            ):
                pick = st.sidebar.selectbox(
                    "Dev Sample ID", dev_df["image_id"].head(25).tolist()
                )
                row = dev_df[dev_df["image_id"] == pick].iloc[0]
                img_path = get_project_root() / str(row["image_path"])
                if img_path.exists():
                    with Image.open(img_path) as im:
                        sample_gray = np.asarray(im.convert("L"), dtype=np.uint8)
                    sample_name = str(pick)

    tabs = st.tabs(
        [
            "Image Inspection",
            "Pipeline Explorer",
            "Robustness Laboratory",
            "Algorithm Comparison",
            "Experiment Dashboard",
            "Inspection Report",
        ]
    )

    if sample_gray is None:
        for tab in tabs:
            with tab:
                st.info(
                    "Upload an EL solar cell image in the sidebar (or generate "
                    "dev_manifest.csv) to run verified Baseline 0 / Baseline 1."
                )
        return

    res = run_ui_pipeline_hook(sample_gray, pipeline_choice)
    gt_mask: np.ndarray | None = None
    gt_metrics: dict[str, float] | None = None
    if uploaded_gt is not None:
        gt_mask = decode_uploaded_mask(uploaded_gt, sample_gray.shape)
        p_val, r_val = compute_precision_recall(res["mask"], gt_mask)
        gt_metrics = {
            "iou": compute_iou(res["mask"], gt_mask),
            "dice": compute_dice(res["mask"], gt_mask),
            "precision": p_val,
            "recall": r_val,
            "area_error_pct": compute_area_error(res["mask"], gt_mask),
            "count_error": float(compute_count_error(res["mask"], gt_mask)),
        }

    with tabs[0]:
        c1, c2, c3 = st.columns(3)
        c1.image(sample_gray, caption=f"Input EL ({sample_name})", clamp=True)
        c2.image(
            (res["mask"] * 255).astype(np.uint8),
            caption="Binary Defect Mask {0,1}",
            clamp=True,
        )
        overlay = render_overlay_with_boxes(
            sample_gray, res["mask"], res["stats"]["components"]
        )
        c3.image(overlay, caption="Defect Overlay & Bounding Boxes")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Defective Area (%)", f"{res['stats']['area_pct']:.4f}%")
        m2.metric("Connected Regions", int(res["stats"]["defect_count"]))
        m3.metric("Runtime (ms)", f"{res['runtime_s'] * 1000.0:.2f}")
        m4.metric(
            "IoU vs GT" if gt_metrics else "Ground Truth",
            f"{gt_metrics['iou']:.4f}" if gt_metrics else "Not Uploaded",
        )

    with tabs[1]:
        st.subheader(f"Stage-by-Stage Inspection ({pipeline_choice})")
        stage_cols = st.columns(len(res["stages"]) + 1)
        for idx, (s_name, s_img) in enumerate(res["stages"].items()):
            stage_cols[idx].image(s_img, caption=s_name, clamp=True)
        fft_img = compute_centered_log_fft(sample_gray)
        stage_cols[-1].image(fft_img, caption="Centered Log-FFT", clamp=True)
        hist = np.bincount(sample_gray.ravel(), minlength=256)
        st.bar_chart(hist)

    with tabs[2]:
        st.subheader("Controlled Degradation Laboratory (Simulated)")
        g_sig = st.slider("Gaussian Sigma", 0.0, 40.0, 0.0, 1.0)
        sp_den = st.slider("Salt & Pepper Density", 0.0, 0.15, 0.0, 0.01)
        c_alp = st.slider("Contrast Gain", 0.5, 2.0, 1.0, 0.1)
        illum = st.slider("Uneven Illumination Ramp", 0.0, 0.7, 0.0, 0.05)
        blur_k = st.select_slider("Gaussian Blur Kernel", [1, 3, 5, 7], 1)
        seed_val = int(st.number_input("Random Seed", value=42, step=1))
        deg = apply_controlled_degradation(
            sample_gray, g_sig, sp_den, c_alp, illum, blur_k, seed_val
        )
        deg_res = run_ui_pipeline_hook(deg, pipeline_choice)
        rc1, rc2, rc3 = st.columns(3)
        rc1.image(deg, caption="Degraded EL Input", clamp=True)
        rc2.image(
            (deg_res["mask"] * 255).astype(np.uint8),
            caption="Degraded Output Mask",
            clamp=True,
        )
        rc3.metric(
            "Degraded Defect Area (%)", f"{deg_res['stats']['area_pct']:.4f}%"
        )

    with tabs[3]:
        st.subheader("Verified Baseline Comparison")
        comp_cols = st.columns(len(VERIFIED_PIPELINES))
        for idx, pname in enumerate(VERIFIED_PIPELINES):
            pres = run_ui_pipeline_hook(sample_gray, pname)
            comp_cols[idx].image(
                (pres["mask"] * 255).astype(np.uint8),
                caption=(
                    f"{pname} | area={pres['stats']['area_pct']:.3f}% | "
                    f"{pres['runtime_s'] * 1000:.1f} ms"
                ),
                clamp=True,
            )

    with tabs[4]:
        st.subheader("Central Experiment Log")
        log_p = get_project_root() / "experiments" / "experiment_log.csv"
        if log_p.exists():
            log_df = pd.read_csv(log_p)
            st.dataframe(log_df, use_container_width=True)
        else:
            st.info("No experiment_log.csv found yet.")

    with tabs[5]:
        md_rep = build_inspection_report_md(
            sample_name, pipeline_choice, res, gt_metrics
        )
        st.markdown(md_rep)
        st.download_button(
            "Download Inspection Report (Markdown)",
            data=md_rep,
            file_name=f"{sample_name}_{pipeline_choice}_report.md",
            mime="text/markdown",
        )
        st.download_button(
            "Download Inspection JSON",
            data=json.dumps(
                {
                    "image": sample_name,
                    "pipeline": pipeline_choice,
                    "stats": res["stats"],
                    "gt_metrics": gt_metrics,
                },
                indent=2,
            ),
            file_name=f"{sample_name}_{pipeline_choice}_report.json",
            mime="application/json",
        )


if __name__ == "__main__":
    main()
