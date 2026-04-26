import json
from pathlib import Path

import typer

app = typer.Typer(name="kbd", help="Knowledge Base Dashboard — your coding patterns, visualized.")


def _get_db_path() -> Path:
    from core.config import AppConfig
    cfg = AppConfig.from_toml()
    return Path(cfg.database.path)


@app.command()
def scan(
    paths: list[str] | None = typer.Argument(None, help="Directories to scan"),
    db: str | None = typer.Option(None, "--db", help="Database path"),
):
    """Scan git repositories and ingest experiment logs."""
    from datetime import datetime

    from rich.console import Console

    from core.config import AppConfig
    from core.db import (
        create_tables,
        db_conn,
        insert_experiment,
        insert_insight,
        insert_run,
        upsert_pattern,
        upsert_repo,
    )
    from core.experiment_parser import find_all_jsonl, parse_jsonl
    from core.git_scanner import scan_directory
    from core.insight_engine import generate_insights
    from core.pattern_engine import detect_patterns

    console = Console()
    cfg = AppConfig.from_toml()
    db_path = Path(db) if db else Path(cfg.database.path)
    scan_paths = paths or cfg.scan.paths

    create_tables(db_path)
    console.print(f"[bold]Scanning {len(scan_paths)} path(s)...[/bold]")

    all_repos = []
    for raw_path in scan_paths:
        p = Path(raw_path).expanduser()
        console.print(f"  Scanning {p}...")
        repos = scan_directory(p, max_depth=cfg.scan.max_depth)
        all_repos.extend(repos)
        console.print(f"  Found {len(repos)} repos")

    console.print(f"\n[green]Saving {len(all_repos)} repos to database...[/green]")
    with db_conn(db_path) as conn:
        for repo in all_repos:
            upsert_repo(conn, repo.to_db_dict())

    # Ingest experiment logs
    all_sessions = []
    for raw_path in scan_paths:
        jsonl_files = find_all_jsonl(Path(raw_path).expanduser(), cfg.autoresearch.filename
                                      if hasattr(cfg, 'autoresearch') else "autoresearch.jsonl")
        for jf in jsonl_files:
            try:
                sessions = parse_jsonl(jf)
                all_sessions.extend(sessions)
                with db_conn(db_path) as conn:
                    for sess in sessions:
                        exp_id = insert_experiment(conn, {
                            "repo_id": None,
                            "jsonl_path": sess.jsonl_path,
                            "session_name": sess.session_name,
                            "metric_name": sess.metric_name,
                            "metric_unit": sess.metric_unit,
                            "direction": sess.direction,
                            "total_runs": sess.total_runs,
                            "kept_runs": sess.kept_runs,
                            "discarded_runs": sess.discarded_runs,
                            "crashed_runs": sess.crashed_runs,
                            "best_metric": sess.best_metric,
                            "noise_floor": None,
                            "started_at": None,
                            "completed_at": datetime.utcnow().isoformat(),
                        })
                        for run in sess.runs:
                            insert_run(conn, {
                                "experiment_id": exp_id,
                                "commit": run.commit,
                                "metric": run.value,
                                "status": run.status,
                                "description": run.description,
                                "extra_metrics": json.dumps(run.extra_metrics),
                                "duration_ms": run.duration_ms,
                                "run_order": run.run_order,
                                "created_at": run.timestamp.isoformat() if run.timestamp else None,
                            })
            except Exception as e:
                console.print(f"  [yellow]Warning: could not parse {jf}: {e}[/yellow]")

    # Detect patterns
    if all_sessions:
        patterns = detect_patterns(all_sessions)
        with db_conn(db_path) as conn:
            for pat in patterns:
                pat_id = upsert_pattern(conn, pat.trigger, pat.action, pat.confidence)
                pat.id = pat_id
        insights = generate_insights(patterns)
        with db_conn(db_path) as conn:
            for ins in insights:
                insert_insight(conn, ins.pattern_id, ins.suggestion, ins.urgency)

    console.print("\n[bold green]Scan complete![/bold green]")
    console.print(f"  Repos: {len(all_repos)}")
    console.print(f"  Experiments: {len(all_sessions)}")


@app.command()
def dashboard(
    db: str | None = typer.Option(None, "--db", help="Database path"),
):
    """Launch the interactive TUI dashboard."""
    from ui.dashboard import KBDApp
    db_path = db or str(_get_db_path())
    KBDApp(db_path=db_path).run()


@app.command()
def health(
    db: str | None = typer.Option(None, "--db", help="Database path"),
):
    """Show database health and stats."""
    from rich.console import Console

    from core.db import db_conn

    console = Console()
    db_path = Path(db) if db else _get_db_path()
    if not db_path.exists():
        console.print("[red]No database found. Run: kbd scan[/red]")
        raise typer.Exit(1)
    with db_conn(db_path) as conn:
        repo_count = conn.execute("SELECT COUNT(*) FROM repos").fetchone()[0]
        exp_count = conn.execute("SELECT COUNT(*) FROM experiments").fetchone()[0]
        pattern_count = conn.execute("SELECT COUNT(*) FROM patterns").fetchone()[0]
        insight_count = conn.execute("SELECT COUNT(*) FROM insights WHERE resolved=0").fetchone()[0]
    size_mb = round(db_path.stat().st_size / 1024 / 1024, 2)
    console.print("\n[bold]Knowledge Base Dashboard — Health Check[/bold]")
    console.print(f"  Database: {db_path} ({size_mb} MB)")
    console.print(f"  Repos: {repo_count}")
    console.print(f"  Experiments: {exp_count}")
    console.print(f"  Patterns detected: {pattern_count}")
    console.print(f"  Pending insights: {insight_count}")


@app.command()
def export(
    output: str = typer.Option("exports/report.html", "--output", "-o"),
    db: str | None = typer.Option(None, "--db"),
):
    """Export dashboard data to an HTML report."""
    from rich.console import Console

    from export.html_report import generate_html_report

    console = Console()
    db_path = Path(db) if db else _get_db_path()
    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    generate_html_report(db_path, out_path)
    console.print(f"[green]Report written to: {out_path}[/green]")


if __name__ == "__main__":
    app()
