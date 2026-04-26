import json
import random
from pathlib import Path

random.seed(42)
out = Path(__file__).parent / "large_jsonl.jsonl"
lines = []
for i in range(1000):
    session = f"session_{i // 100}"
    lines.append(json.dumps({
        "session": session,
        "metric": "perf_score",
        "unit": "points",
        "direction": "higher",
        "run": i % 100 + 1,
        "value": round(random.uniform(50, 100), 2),
        "status": random.choice(["keep", "keep", "keep", "discard", "crash"]),
        "description": f"run {i} experiment",
        "timestamp": f"2024-0{(i % 9)+1}-10T09:00:00Z",
    }))
out.write_text("\n".join(lines))
print(f"Generated {len(lines)} lines")
