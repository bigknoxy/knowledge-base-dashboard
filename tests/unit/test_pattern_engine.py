from core.insight_engine import generate_insights
from core.pattern_engine import detect_patterns
from models.experiment import ExperimentRun, ExperimentSession
from models.pattern import PatternModel


def make_session(name: str, metric: str, runs_data: list[tuple]) -> ExperimentSession:
    """Helper: make session from list of (value, status, description) tuples."""
    runs = [
        ExperimentRun(run_order=i+1, value=v, status=s, description=d)
        for i, (v, s, d) in enumerate(runs_data)
    ]
    return ExperimentSession(
        session_name=name, metric_name=metric, metric_unit="ms",
        direction="lower", jsonl_path="/tmp/test.jsonl", runs=runs
    )


def test_detect_patterns_requires_min_2_occurrences():
    sess = make_session("s1", "latency", [(100, "keep", "baseline")])
    patterns = detect_patterns([sess])
    # Only 1 session → no patterns (frequency < 2)
    assert all(p.frequency >= 2 for p in patterns)


def test_detect_patterns_finds_repeated_first_action():
    sessions = [
        make_session(f"s{i}", "latency", [
            (100, "keep", "try redis cache"),
            (90, "keep", "tune index"),
        ])
        for i in range(3)
    ]
    patterns = detect_patterns(sessions)
    assert len(patterns) >= 1
    triggers = [p.trigger for p in patterns]
    assert any("latency" in t for t in triggers)


def test_pattern_confidence_range():
    sessions = [
        make_session(f"s{i}", "perf", [(100, "keep", "baseline")])
        for i in range(5)
    ]
    patterns = detect_patterns(sessions)
    for p in patterns:
        assert 0.0 <= p.confidence <= 1.0


def test_generate_insights_produces_one_per_pattern():
    patterns = [
        PatternModel(id=1, trigger="optimizing bundle_size", action="remove lodash",
                     frequency=3, confidence=0.6),
        PatternModel(id=2, trigger="optimizing memory", action="reduce allocations",
                     frequency=2, confidence=0.4),
    ]
    insights = generate_insights(patterns)
    assert len(insights) == 2
    assert all(i.urgency in ["low", "medium", "high"] for i in insights)


def test_generate_insights_skips_pattern_without_id():
    pattern = PatternModel(trigger="optimizing x", action="try y", frequency=3, confidence=0.5)
    insights = generate_insights([pattern])
    assert len(insights) == 0
