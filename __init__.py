"""SolarEye — Classical Digital Image Processing for PV EL Defect Inspection.

Phase 1 (Milestones 1 and 2) repository package. Strictly classical DIP:
no machine learning, deep learning, or pretrained models are permitted.
"""

from __future__ import annotations

__version__ = "0.1.0-m1m2"

CANONICAL_SEED = 42
CANONICAL_MASK_VALUES = (0, 1)
CANONICAL_BORDER_MODE = "reflect"
EXPERIMENT_LOG_COLUMNS = [
    "run_id",
    "date",
    "author",
    "pipeline",
    "stage",
    "method",
    "parameters",
    "random_seed",
    "processing_time_s",
    "dataset_split",
    "metric_name",
    "metric_value",
    "secondary_metrics",
    "config_file",
    "git_commit",
    "notes",
]

__all__ = [
    "__version__",
    "CANONICAL_SEED",
    "CANONICAL_MASK_VALUES",
    "CANONICAL_BORDER_MODE",
    "EXPERIMENT_LOG_COLUMNS",
]
