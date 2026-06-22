"""A1: COMPILE_MODEL is env-overridable and model-invalid failures are detectable.

Loads tools/kb.py fresh per case (no package import / no API calls) so the
module-level env read is exercised deterministically.
"""
import importlib.util
from pathlib import Path

KB_PY = Path(__file__).resolve().parent.parent / "tools" / "kb.py"


def _load_kb():
    spec = importlib.util.spec_from_file_location("kb_under_test", KB_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_is_model_error_detects_retired_model_404():
    kb = _load_kb()
    err = ("Error code: 404 - {'type': 'not_found_error', "
           "'message': 'model: claude-sonnet-4-20250514'}")
    assert kb._is_model_error(err) is True


def test_is_model_error_excludes_fetch_404_and_transient():
    kb = _load_kb()
    # fetch-side 404 has no 'model' token -> must not be misclassified as a model error
    assert kb._is_model_error("fetch failed: HTTP 404") is False
    assert kb._is_model_error("Connection timeout") is False
    assert kb._is_model_error("overloaded_error 529") is False


def test_compile_model_defaults_to_current():
    kb = _load_kb()
    assert kb.COMPILE_MODEL == "claude-sonnet-4-6"


def test_compile_model_env_override(monkeypatch):
    monkeypatch.setenv("KB_COMPILE_MODEL", "claude-test-override")
    kb = _load_kb()
    assert kb.COMPILE_MODEL == "claude-test-override"
