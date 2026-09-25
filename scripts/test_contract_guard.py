"""S1-03 AC3: contract_guard on a throwaway git repository."""

import subprocess
import sys
from pathlib import Path

import pytest

GUARD = Path(__file__).with_name("contract_guard.py")


def tech_md(version: str, ready: bool) -> str:
    status = "готов" if ready else "не готов"
    return f"# tech.md\n\n- Версия: {version}\n- Каркас: {status}\n"


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


def write(repo: Path, path: str, text: str) -> None:
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def make_repo(tmp_path: Path, *, ready: bool) -> Path:
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "config", "user.email", "test@example.com")
    git(tmp_path, "config", "user.name", "test")
    write(tmp_path, "tech.md", tech_md("v5", ready))
    write(tmp_path, "backend/apps/core/enums.py", "A = 1\n")
    write(tmp_path, "README.md", "readme\n")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-q", "-m", "base")
    git(tmp_path, "checkout", "-q", "-b", "feature")
    return tmp_path


def commit(repo: Path, files: dict[str, str]) -> None:
    for path, text in files.items():
        write(repo, path, text)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "change")


def run_guard(repo: Path, *labels: str) -> subprocess.CompletedProcess[str]:
    args = [sys.executable, str(GUARD), "--base", "main", "--labels", ",".join(labels)]
    return subprocess.run(
        args, cwd=repo, capture_output=True, text=True, encoding="utf-8", check=False
    )


def test_ac3_not_ready_prints_frozen_paths_and_passes(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, ready=False)
    commit(repo, {"backend/apps/core/enums.py": "A = 2\n", "contracts/openapi.yaml": "x: 1\n"})
    result = run_guard(repo)
    assert result.returncode == 0
    assert "backend/apps/core/enums.py" in result.stdout
    assert "contracts/openapi.yaml" in result.stdout


def test_ac3_ready_without_bump_fails(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, ready=True)
    commit(repo, {"frontend/src/lib/components/ui/button/button.svelte": "<button></button>\n"})
    result = run_guard(repo)
    assert result.returncode == 1
    assert "frontend/src/lib/components/ui/button/button.svelte" in result.stdout


def test_ac3_ready_with_version_bump_passes(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, ready=True)
    commit(repo, {".env.example": "A=1\n", "tech.md": tech_md("v6", True)})
    assert run_guard(repo).returncode == 0


def test_ac3_ready_with_bypass_label_passes(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, ready=True)
    commit(repo, {"backend/apps/leads/sheets/row.py": "HEADERS = ()\n"})
    assert run_guard(repo, "bug", "no-contract-change").returncode == 0


@pytest.mark.parametrize("ready", [True, False])
def test_ac3_untouched_frozen_paths_pass(tmp_path: Path, ready: bool) -> None:
    repo = make_repo(tmp_path, ready=ready)
    commit(repo, {"README.md": "changed\n", "backend/apps/content/models.py": "x = 1\n"})
    result = run_guard(repo)
    assert result.returncode == 0
    assert "backend/apps/content/models.py" not in result.stdout
