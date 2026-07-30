"""Loads factory-log/validator.py by file path.

`factory-log` is not a valid Python package name (hyphen), so this loads the
module directly via importlib rather than a normal import — keeps the
validator itself in one canonical place (factory-log/validator.py, versioned
alongside factory-log/SCHEMA.md) instead of duplicating it into the backend.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_VALIDATOR_PATH = Path(__file__).resolve().parents[3] / "factory-log" / "validator.py"


def _load():
    spec = importlib.util.spec_from_file_location("factory_log_validator", _VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load factory-log validator from {_VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["factory_log_validator"] = module
    spec.loader.exec_module(module)
    return module


factory_log_validator = _load()
