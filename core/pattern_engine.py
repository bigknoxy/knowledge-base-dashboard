from collections import Counter
from datetime import datetime

from models.experiment import ExperimentSession
from models.pattern import PatternModel


def detect_patterns(sessions: list[ExperimentSession]) -> list[PatternModel]:
    """
    Detect recurring patterns: when optimizing METRIC, always try ACTION first.
    Simple approach: find (metric_name, first_kept_description) pairs that appear
    across multiple sessions.
    """
    patterns: list[PatternModel] = []

    # Pattern 1: "when optimizing X, first action is Y"
    first_actions: Counter[tuple[str, str]] = Counter()
    for session in sessions:
        kept = [r for r in session.runs if r.status == "keep"]
        if kept:
            trigger = f"optimizing {session.metric_name}"
            action = kept[0].description[:60] if kept[0].description else "unknown"
            first_actions[(trigger, action)] += 1

    for (trigger, action), freq in first_actions.items():
        if freq >= 2:
            confidence = min(1.0, freq / 5.0)
            patterns.append(PatternModel(
                trigger=trigger,
                action=action,
                frequency=freq,
                confidence=confidence,
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow(),
            ))

    # Pattern 2: "always discards runs when description contains X"
    discard_desc_counter: Counter[str] = Counter()
    for session in sessions:
        for run in session.runs:
            if run.status == "discard" and run.description:
                key = run.description[:40]
                discard_desc_counter[key] += 1

    for desc, count in discard_desc_counter.items():
        if count >= 2:
            patterns.append(PatternModel(
                trigger="attempting optimization",
                action=f"discarded: {desc}",
                frequency=count,
                confidence=min(1.0, count / 4.0),
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow(),
            ))

    return patterns
