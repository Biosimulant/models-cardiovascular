# SPDX-FileCopyrightText: 2025-present Demi <bjaiye1@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Auto-generated tests for Guyton1972AntidiuretichormoneModel0911309080Model.

These tests intentionally avoid requiring simulator dependencies. They should pass
even when a wrapper falls back to stub outputs (e.g., simulator not installed).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest


_MODEL_DIR = Path(__file__).resolve().parents[1]


def _find_bsim_src(start: Path) -> Path | None:
    for parent in [start, *start.parents]:
        for candidate in (parent / "biosim" / "src", parent / "bsim-active" / "biosim" / "src"):
            if (candidate / "biosim").is_dir():
                return candidate
    return None


def _ensure_test_paths() -> None:
    model_dir = str(_MODEL_DIR)
    if model_dir not in sys.path:
        sys.path.insert(0, model_dir)

    bsim_src = _find_bsim_src(_MODEL_DIR)
    if bsim_src is not None and str(bsim_src) not in sys.path:
        sys.path.insert(0, str(bsim_src))


_ensure_test_paths()


from src.guyton1972_antidiuretichormone_model0911309080_model import Guyton1972AntidiuretichormoneModel0911309080Model  # noqa: E402
from biosim.signals import (AcceptedSignalProfile, ArraySignal, BioSignal, EventSignal, RecordSignal, ScalarSignal, SignalSpec)


def _advance_or_skip_optional_runtime(module, start: float, end: float) -> None:
    try:
        module.advance_window(start, end)
    except ModuleNotFoundError as exc:
        pytest.skip(f"Optional runtime dependency missing: {exc.name or exc}")
    except ImportError as exc:
        pytest.skip(f"Optional runtime dependency missing: {exc}")


def test_instantiation() -> None:
    module = Guyton1972AntidiuretichormoneModel0911309080Model()
    assert module.integration_step > 0
    assert isinstance(module.inputs(), dict)
    assert isinstance(module.outputs(), dict)
    assert len(module.outputs()) > 0


def test_advance_produces_outputs() -> None:
    module = Guyton1972AntidiuretichormoneModel0911309080Model(integration_step=0.1)
    _advance_or_skip_optional_runtime(module, 0.0, 0.1)
    outputs = module.get_outputs()
    for name in module.outputs():
        assert name in outputs
        signal = outputs[name]
        assert isinstance(signal, BioSignal)
        assert signal.source is not None
        assert signal.emitted_at == 0.1


def test_output_keys_match() -> None:
    module = Guyton1972AntidiuretichormoneModel0911309080Model(integration_step=0.1)
    _advance_or_skip_optional_runtime(module, 0.0, 0.1)
    assert set(module.get_outputs().keys()) == set(module.outputs())


def test_reset() -> None:
    module = Guyton1972AntidiuretichormoneModel0911309080Model(integration_step=0.1)
    _advance_or_skip_optional_runtime(module, 0.0, 0.1)
    if hasattr(module, "reset"):
        module.reset()
        _advance_or_skip_optional_runtime(module, 0.0, 0.1)
        assert set(module.get_outputs().keys()) == set(module.outputs())
