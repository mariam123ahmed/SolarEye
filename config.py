"""Configuration dataclasses and YAML/JSON loader for SolarEye (Milestone 1).

Owner: Member 1 (Tech Lead, Integration & Metrics).
Uses `pathlib.Path` relative to the repository root with zero hardcoded
machine paths and enforces canonical SolarEye contracts (`random_seed=42`,
`dark_defects=True`, `mask_values=[0, 1]`, `border_mode="reflect"`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - fallback when PyYAML absent
    yaml = None

DEFAULT_SEED: int = 42
ALLOWED_PIPELINES: tuple[str, ...] = (
    "baseline_0",
    "baseline_1",
    "pipeline_a",
    "pipeline_b",
    "pipeline_c",
)


@dataclass(frozen=True)
class ContractConfig:
    """Canonical SolarEye data and reproducibility contract."""

    random_seed: int = 42
    grayscale: bool = True
    dark_defects: bool = True
    mask_values: tuple[int, int] = (0, 1)
    border_mode: str = "reflect"


@dataclass
class DatasetConfig:
    """Dataset location and split manifest configuration."""

    dataset_name: str = "msps"
    source_doi: str = "10.5281/zenodo.21549573"
    raw_dir: Path = Path("data/raw/msps")
    splits_dir: Path = Path("data/splits")
    dev_manifest: Path = Path("data/splits/dev_manifest.csv")
    test_manifest: Path = Path("data/splits/test_manifest.csv")
    test_ratio: float = 0.30
    random_seed: int = 42
    grayscale: bool = True
    target_size: tuple[int, int] | None = None
    dark_defects: bool = True
    mask_values: list[int] = field(default_factory=lambda: [0, 1])
    border_mode: str = "reflect"


@dataclass
class BaselineConfig:
    """Configuration schema for Baseline 0 and Baseline 1."""

    run_id: str
    pipeline: str
    milestone: str = "M2"
    random_seed: int = 42
    dark_defects: bool = True
    mask_values: list[int] = field(default_factory=lambda: [0, 1])
    border_mode: str = "reflect"
    threshold: int = 127
    opening_ksize: int = 3
    opening_shape: str = "rect"


@dataclass
class PipelineConfig:
    """Configuration schema for Pipelines A, B, and C (Milestone 3/4)."""

    run_id: str
    pipeline: str
    milestone: str = "M3"
    random_seed: int = 42
    dark_defects: bool = True
    mask_values: list[int] = field(default_factory=lambda: [0, 1])
    border_mode: str = "reflect"
    dataset: dict[str, Any] = field(default_factory=dict)
    noise: dict[str, Any] = field(default_factory=dict)
    restoration: dict[str, Any] = field(default_factory=dict)
    frequency: dict[str, Any] = field(default_factory=dict)
    enhancement: dict[str, Any] = field(default_factory=dict)
    segmentation: dict[str, Any] = field(default_factory=dict)
    morphology: dict[str, Any] = field(default_factory=dict)
    quantification: dict[str, Any] = field(default_factory=dict)


def get_project_root() -> Path:
    """Return the SolarEye repository root directory relative to this file."""
    return Path(__file__).resolve().parent.parent


def _parse_scalar(raw_val: str) -> Any:
    """Parse a scalar YAML token into Python bool, int, float, None, or str."""
    text = raw_val.strip()
    if text in ("null", "Null", "NULL", "~", ""):
        return None
    if text in ("true", "True", "TRUE"):
        return True
    if text in ("false", "False", "FALSE"):
        return False
    if text == "{}":
        return {}
    if text == "[]":
        return []
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(item) for item in inner.split(",")]
    if (text.startswith('"') and text.endswith('"')) or (
        text.startswith("'") and text.endswith("'")
    ):
        return text[1:-1]
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        return text


def _strip_yaml_comment(line: str) -> str:
    """Strip inline `#` comments outside single or double quotes."""
    in_single = False
    in_double = False
    for idx, ch in enumerate(line):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            return line[:idx]
    return line


def _fallback_yaml_load(text: str) -> dict[str, Any]:
    """Parse simple nested key-value YAML mappings when PyYAML is absent."""
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for raw_line in text.splitlines():
        cleaned = _strip_yaml_comment(raw_line).rstrip()
        if not cleaned.strip():
            continue
        indent = len(cleaned) - len(cleaned.lstrip(" "))
        stripped = cleaned.strip()
        if ":" not in stripped:
            raise ValueError(f"Unsupported YAML syntax line: {raw_line}")
        key, rest = stripped.split(":", 1)
        key = key.strip()
        val_str = rest.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if val_str == "":
            nested: dict[str, Any] = {}
            parent[key] = nested
            stack.append((indent, nested))
        else:
            parent[key] = _parse_scalar(val_str)
    return root


def validate_config(cfg: dict[str, Any]) -> dict[str, Any]:
    """Validate mandatory SolarEye contract invariants on loaded config."""
    if not isinstance(cfg, dict):
        raise ValueError("Configuration root must be a mapping/dictionary.")

    seed = cfg.get("random_seed", DEFAULT_SEED)
    if seed != DEFAULT_SEED:
        raise ValueError(
            f"Canonical random_seed must be {DEFAULT_SEED}, got {seed}."
        )

    if cfg.get("dark_defects", True) is not True:
        raise ValueError(
            "SolarEye EL contract requires dark_defects=True."
        )

    mask_vals = cfg.get("mask_values", [0, 1])
    if list(mask_vals) != [0, 1]:
        raise ValueError(
            f"Canonical mask_values must be [0, 1], got {mask_vals}."
        )

    border_mode = cfg.get("border_mode", "reflect")
    if border_mode != "reflect":
        raise ValueError(
            f"Canonical border_mode must be 'reflect', got {border_mode}."
        )

    if "pipeline" in cfg:
        pipeline_name = cfg["pipeline"]
        if pipeline_name not in ALLOWED_PIPELINES:
            raise ValueError(
                f"Unknown pipeline '{pipeline_name}'. "
                f"Expected one of {ALLOWED_PIPELINES}."
            )
    return cfg


def load_config(config_path: str | Path) -> dict[str, Any]:
    """Load and validate a YAML or JSON SolarEye configuration file."""
    path = Path(config_path)
    if not path.is_absolute() and not path.exists():
        candidate = get_project_root() / path
        if candidate.exists():
            path = candidate
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    raw_text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        loaded = json.loads(raw_text)
    elif yaml is not None:
        loaded = yaml.safe_load(raw_text)
    else:
        loaded = _fallback_yaml_load(raw_text)

    return validate_config(loaded)


def build_pipeline_config(cfg: dict[str, Any]) -> PipelineConfig:
    """Construct a typed `PipelineConfig` from a validated dictionary."""
    validated = validate_config(cfg)
    if "run_id" not in validated or "pipeline" not in validated:
        raise ValueError(
            "Pipeline config requires 'run_id' and 'pipeline' keys."
        )
    return PipelineConfig(
        run_id=str(validated["run_id"]),
        pipeline=str(validated["pipeline"]),
        milestone=str(validated.get("milestone", "M3")),
        random_seed=int(validated.get("random_seed", DEFAULT_SEED)),
        dark_defects=bool(validated.get("dark_defects", True)),
        mask_values=list(validated.get("mask_values", [0, 1])),
        border_mode=str(validated.get("border_mode", "reflect")),
        dataset=dict(validated.get("dataset", {})),
        noise=dict(validated.get("noise", {})),
        restoration=dict(validated.get("restoration", {})),
        frequency=dict(validated.get("frequency", {})),
        enhancement=dict(validated.get("enhancement", {})),
        segmentation=dict(validated.get("segmentation", {})),
        morphology=dict(validated.get("morphology", {})),
        quantification=dict(validated.get("quantification", {})),
    )
