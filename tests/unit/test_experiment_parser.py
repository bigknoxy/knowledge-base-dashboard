from pathlib import Path

import pytest

from core.experiment_parser import (
    calculate_confidence,
    calculate_noise_floor,
    find_all_jsonl,
    parse_jsonl,
)
from tests.conftest import FIXTURES_DIR


def test_parse_sample_returns_two_sessions():
    sessions = parse_jsonl(FIXTURES_DIR / "sample_autoresearch.jsonl")
    assert len(sessions) == 2


def test_parse_bundle_session_stats():
    sessions = parse_jsonl(FIXTURES_DIR / "sample_autoresearch.jsonl")
    bundle = next(s for s in sessions if s.session_name == "bundle_size_opt")
    assert bundle.total_runs == 5
    assert bundle.kept_runs == 4
    assert bundle.discarded_runs == 1
    assert bundle.crashed_runs == 0
    assert bundle.metric_name == "bundle_size_kb"
    assert bundle.direction == "lower"


def test_best_metric_is_minimum_kept():
    sessions = parse_jsonl(FIXTURES_DIR / "sample_autoresearch.jsonl")
    bundle = next(s for s in sessions if s.session_name == "bundle_size_opt")
    assert bundle.best_metric == 820.5


def test_parse_large_jsonl():
    sessions = parse_jsonl(FIXTURES_DIR / "large_jsonl.jsonl")
    assert len(sessions) == 10  # 1000 runs / 100 per session


def test_parse_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        parse_jsonl(Path("/nonexistent/file.jsonl"))


def test_noise_floor_with_stable_values():
    noise = calculate_noise_floor([100.0, 100.1, 99.9, 100.2, 99.8])
    assert noise < 1.0


def test_noise_floor_with_volatile_values():
    noise = calculate_noise_floor([50.0, 100.0, 75.0, 120.0, 30.0])
    assert noise > 5.0


def test_noise_floor_too_few_values():
    assert calculate_noise_floor([1.0, 2.0]) == 0.0


def test_confidence_no_noise():
    assert calculate_confidence(5.0, 0.0) == 1.0


def test_confidence_clamped():
    assert 0.0 <= calculate_confidence(100.0, 1.0) <= 1.0
    assert 0.0 <= calculate_confidence(0.0, 10.0) <= 1.0


def test_find_all_jsonl(tmp_path):
    (tmp_path / "a.jsonl").write_text("")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "autoresearch.jsonl").write_text("")
    results = find_all_jsonl(tmp_path, "autoresearch.jsonl")
    assert len(results) == 1
    assert results[0].name == "autoresearch.jsonl"
