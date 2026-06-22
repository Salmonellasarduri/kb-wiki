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


# --- A2: retry-cap / discard policy --------------------------------------------------


def test_classify_fail_reason_buckets():
    kb = _load_kb()
    assert kb._classify_fail_reason("Error code: 404 not_found_error model: x") == "model_invalid"
    assert kb._classify_fail_reason("Connection timeout") == "transient"
    assert kb._classify_fail_reason("overloaded_error 529") == "transient"
    assert kb._classify_fail_reason("No valid frontmatter after retry") == "content_invalid"
    assert kb._classify_fail_reason("something unexpected") == "other"


def test_status_after_failure_policy():
    kb = _load_kb()
    # model_invalid never blocks (recovers when KB_COMPILE_MODEL is fixed)
    assert kb._status_after_failure(99, "model_invalid") == ("failed", None)
    # under budget -> keep retrying
    assert kb._status_after_failure(1, "transient") == ("failed", None)
    # exhausted -> blocked with structured reason
    assert kb._status_after_failure(kb.MAX_COMPILE_ATTEMPTS, "content_invalid") == (
        "blocked", "retry_exhausted")


def test_record_compile_failure_blocks_after_budget(monkeypatch):
    kb = _load_kb()
    monkeypatch.setattr(kb, "_append_log", lambda *a, **k: None)  # no log.md side effect
    item = {"compile_attempts": kb.MAX_COMPILE_ATTEMPTS - 1}
    kb._record_compile_failure(item, "No valid frontmatter after retry", "src1")
    assert item["status"] == "blocked"
    assert item["blocked_reason"] == "retry_exhausted"
    assert item["fail_reason"] == "content_invalid"
    assert item["compile_attempts"] == kb.MAX_COMPILE_ATTEMPTS


def test_record_compile_failure_keeps_model_invalid_retryable(monkeypatch):
    kb = _load_kb()
    monkeypatch.setattr(kb, "_append_log", lambda *a, **k: None)
    item = {"compile_attempts": 99}  # well over budget
    kb._record_compile_failure(item, "404 not_found_error model: claude-x", "src2")
    assert item["status"] == "failed"  # model_invalid is never blocked
    assert item["fail_reason"] == "model_invalid"
