from datetime import datetime
from pathlib import Path

from core.db import db_conn


def generate_html_report(db_path: Path, out_path: Path) -> None:
    with db_conn(db_path) as conn:
        repos = conn.execute(
            "SELECT name, primary_lang, total_commits, last_active, status, stack_json "
            "FROM repos ORDER BY last_active DESC"
        ).fetchall()
        experiments = conn.execute(
            "SELECT session_name, metric_name, total_runs, kept_runs, best_metric "
            "FROM experiments ORDER BY completed_at DESC"
        ).fetchall()
        patterns = conn.execute(
            "SELECT trigger, action, frequency, confidence FROM patterns ORDER BY frequency DESC"
        ).fetchall()

    repo_rows = "\n".join(
        f"<tr><td>{r['name']}</td><td>{r['primary_lang'] or ''}</td>"
        f"<td>{r['total_commits']}</td><td>{str(r['last_active'] or '')[:10]}</td>"
        f"<td>{r['status']}</td></tr>"
        for r in repos
    )

    exp_rows = "\n".join(
        f"<tr><td>{e['session_name']}</td><td>{e['metric_name']}</td>"
        f"<td>{e['kept_runs']}/{e['total_runs']}</td><td>{e['best_metric'] or ''}</td></tr>"
        for e in experiments
    )

    pattern_rows = "\n".join(
        f"<tr><td>{p['trigger']}</td><td>{p['action']}</td>"
        f"<td>{p['frequency']}</td><td>{p['confidence']:.2f}</td></tr>"
        for p in patterns
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Knowledge Base Dashboard Report</title>
<style>
  body {{
    font-family: -apple-system, sans-serif;
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
  }}
  h1 {{ color: #1a1a2e; }}
  h2 {{
    color: #16213e;
    border-bottom: 2px solid #0f3460;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 2rem;
  }}
  th {{
    background: #0f3460;
    color: white;
    padding: 0.5rem 1rem;
    text-align: left;
  }}
  td {{
    padding: 0.4rem 1rem;
    border-bottom: 1px solid #eee;
  }}
  tr:hover {{ background: #f8f9fa; }}
  .stats {{
    display: flex;
    gap: 2rem;
    margin-bottom: 2rem;
  }}
  .stat {{
    background: #f8f9fa;
    padding: 1rem 2rem;
    border-radius: 8px;
  }}
  .stat h3 {{
    margin: 0;
    font-size: 2rem;
    color: #0f3460;
  }}
</style>
</head>
<body>
<h1>🧠 Knowledge Base Dashboard</h1>
<p>Generated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}</p>
<div class="stats">
  <div class="stat"><h3>{len(repos)}</h3><p>Repositories</p></div>
  <div class="stat"><h3>{len(experiments)}</h3><p>Experiments</p></div>
  <div class="stat"><h3>{len(patterns)}</h3><p>Patterns</p></div>
</div>
<h2>Repositories</h2>
<table>
<thead>
<tr>
<th>Name</th><th>Language</th><th>Commits</th>
<th>Last Active</th><th>Status</th>
</tr>
</thead>
<tbody>{repo_rows}</tbody>
</table>
<h2>Experiments</h2>
<table>
<thead>
<tr>
<th>Session</th><th>Metric</th>
<th>Kept/Total</th><th>Best</th>
</tr>
</thead>
<tbody>{exp_rows}</tbody>
</table>
<h2>Patterns</h2>
<table>
<thead>
<tr>
<th>Trigger</th><th>Action</th>
<th>Frequency</th><th>Confidence</th>
</tr>
</thead>
<tbody>{pattern_rows}</tbody>
</table>
</body></html>"""

    out_path.write_text(html, encoding="utf-8")
