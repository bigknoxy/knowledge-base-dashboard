import hashlib
import json
import subprocess
from datetime import datetime
from pathlib import Path

from models.repo import RepoModel

MANIFEST_STACK_MAP = {
    "package.json": lambda d: _parse_npm_stack(d),
    "pyproject.toml": lambda d: ["Python"],
    "Cargo.toml": lambda d: ["Rust"],
    "go.mod": lambda d: ["Go"],
    "Gemfile": lambda d: ["Ruby"],
    "pom.xml": lambda d: ["Java", "Maven"],
    "build.gradle": lambda d: ["Java", "Gradle"],
}

LANG_EXT_MAP = {
    ".py": "Python", ".rs": "Rust", ".go": "Go", ".ts": "TypeScript",
    ".tsx": "TypeScript", ".js": "JavaScript", ".jsx": "JavaScript",
    ".rb": "Ruby", ".java": "Java", ".kt": "Kotlin", ".swift": "Swift",
    ".c": "C", ".cpp": "C++", ".h": "C/C++", ".cs": "C#",
    ".ex": "Elixir", ".exs": "Elixir",
}


def _repo_id(path: Path) -> str:
    return hashlib.sha256(str(path.resolve()).encode()).hexdigest()[:16]


def _run_git(args: list[str], cwd: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(cwd)] + args,
        capture_output=True, text=True, timeout=15
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def _parse_npm_stack(content: str) -> list[str]:
    try:
        data = json.loads(content)
        deps = (
            list(data.get("dependencies", {}).keys())
            + list(data.get("devDependencies", {}).keys())
        )
        stack = ["JavaScript"]
        known = {
            "react": "React", "vue": "Vue", "svelte": "Svelte",
            "next": "Next.js", "nuxt": "Nuxt", "typescript": "TypeScript",
            "vite": "Vite", "webpack": "Webpack", "tailwindcss": "Tailwind CSS",
        }
        for dep in deps:
            for key, label in known.items():
                if key in dep.lower() and label not in stack:
                    stack.append(label)
        return stack
    except Exception:
        return ["JavaScript"]


def detect_languages(repo_path: Path) -> dict[str, float]:
    counts: dict[str, int] = {}
    total = 0
    for f in repo_path.rglob("*"):
        if f.is_file() and ".git" not in f.parts:
            lang = LANG_EXT_MAP.get(f.suffix.lower())
            if lang:
                counts[lang] = counts.get(lang, 0) + 1
                total += 1
    if total == 0:
        return {}
    return {lang: round(count / total * 100, 1) for lang, count in
            sorted(counts.items(), key=lambda x: -x[1])}


def detect_stack(repo_path: Path) -> list[str]:
    stack: list[str] = []
    for manifest, parser in MANIFEST_STACK_MAP.items():
        manifest_path = repo_path / manifest
        if manifest_path.exists():
            content = manifest_path.read_text(errors="replace")
            items = parser(content)  # type: ignore[no-untyped-call]
            for item in items:
                if item not in stack:
                    stack.append(item)
    return stack


def scan_repo(path: Path) -> RepoModel | None:
    git_dir = path / ".git"
    if not git_dir.exists():
        return None

    try:
        repo_id = _repo_id(path)
        name = path.name

        first_commit_str = _run_git(["log", "--reverse", "--format=%cI", "--max-count=1"], path)
        last_commit_str = _run_git(["log", "--format=%cI", "--max-count=1"], path)
        total_str = _run_git(["rev-list", "--count", "HEAD"], path)
        branch_str = _run_git(["branch", "--list"], path)

        first_commit = datetime.fromisoformat(first_commit_str) if first_commit_str else None
        last_commit = datetime.fromisoformat(last_commit_str) if last_commit_str else None
        total_commits = int(total_str) if total_str.isdigit() else 0
        branch_count = len([b for b in branch_str.splitlines() if b.strip()])

        langs = detect_languages(path)
        primary_lang = list(langs.keys())[0] if langs else None
        stack = detect_stack(path)

        remote = _run_git(["remote", "get-url", "origin"], path) or None

        readme_path = next((path / f for f in ["README.md", "readme.md", "README.txt"]
                            if (path / f).exists()), None)
        description = None
        if readme_path:
            lines = readme_path.read_text(errors="replace").splitlines()
            for line in lines:
                stripped = line.strip().lstrip("#").strip()
                if stripped and not stripped.startswith("!"):
                    description = stripped[:200]
                    break

        return RepoModel(
            id=repo_id,
            path=str(path.resolve()),
            name=name,
            description=description,
            url=remote,
            created_at=first_commit,
            last_active=last_commit,
            total_commits=total_commits,
            branch_count=max(branch_count, 1),
            primary_lang=primary_lang,
            stack=stack,
            status="active",
            scanned_at=datetime.utcnow(),
        )
    except Exception:
        return None


def scan_directory(root: Path, max_depth: int = 5) -> list[RepoModel]:
    repos: list[RepoModel] = []
    root = root.expanduser().resolve()
    if not root.exists():
        return repos

    def _walk(current: Path, depth: int) -> None:
        if depth > max_depth:
            return
        if (current / ".git").exists():
            repo = scan_repo(current)
            if repo:
                repos.append(repo)
            return
        try:
            for child in sorted(current.iterdir()):
                if child.is_dir() and not child.name.startswith("."):
                    _walk(child, depth + 1)
        except PermissionError:
            pass

    _walk(root, 0)
    return repos
