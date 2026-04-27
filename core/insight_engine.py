from typing import Literal

from models.insight import InsightModel
from models.pattern import PatternModel

SUGGESTION_TEMPLATES = {
    "optimizing bundle_size": (
        "Have you tried code splitting with dynamic imports() for "
        "route-based chunking?"
    ),
    "optimizing p95_latency": (
        "Consider connection pooling and query caching if you haven't "
        "tried them yet."
    ),
    "optimizing memory": (
        "Profile heap allocations with py-spy or valgrind to find the "
        "real bottleneck."
    ),
}


def generate_insights(patterns: list[PatternModel]) -> list[InsightModel]:
    insights: list[InsightModel] = []
    for pattern in patterns:
        if pattern.id is None:
            continue

        # Look for matching template
        suggestion = None
        for keyword, template in SUGGESTION_TEMPLATES.items():
            if keyword in pattern.trigger.lower():
                suggestion = template
                break

        if not suggestion:
            suggestion = (
                f"You frequently try '{pattern.action}' when "
                f"{pattern.trigger}. Consider exploring an alternative "
                f"approach to see if you can break through the plateau."
            )

        if pattern.frequency >= 5:
            urgency: Literal["low", "medium", "high"] = "high"
        elif pattern.frequency >= 3:
            urgency = "medium"
        else:
            urgency = "low"

        insights.append(InsightModel(
            pattern_id=pattern.id,
            suggestion=suggestion,
            urgency=urgency,
        ))

    return insights
