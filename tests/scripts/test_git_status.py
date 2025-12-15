"""Tests for vigor.scripts.git.git_status module."""

from pathlib import Path

from click.testing import CliRunner

from vigor.scripts.git.git_status import check_repo_status, git_status


def test_git_status_with_repos(temp_git_repos: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(git_status, ["--root-dir", str(temp_git_repos)])

    assert result.exit_code == 0
    assert "Summary:" in result.output
    assert "repos have changes" in result.output


def test_git_status_quiet_mode(temp_git_repos: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(git_status, ["--root-dir", str(temp_git_repos), "-q"])

    assert result.exit_code == 0
    assert "dirty_repo" in result.output
    assert "clean_repo" not in result.output or "Clean:" not in result.output


def test_git_status_empty_dir(temp_dir: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(git_status, ["--root-dir", str(temp_dir)])

    assert result.exit_code == 0
    assert "Summary: 0/0" in result.output


def test_check_repo_status_clean(temp_git_repos: Path) -> None:
    clean_repo = temp_git_repos / "clean_repo"
    has_changes = check_repo_status(str(clean_repo), quiet=False)
    assert has_changes is False


def test_check_repo_status_dirty(temp_git_repos: Path) -> None:
    dirty_repo = temp_git_repos / "dirty_repo"
    has_changes = check_repo_status(str(dirty_repo), quiet=False)
    assert has_changes is True


def test_check_repo_status_not_a_repo(temp_git_repos: Path) -> None:
    not_a_repo = temp_git_repos / "not_a_repo"
    has_changes = check_repo_status(str(not_a_repo), quiet=False)
    assert has_changes is False


def test_git_status_nonexistent_dir() -> None:
    runner = CliRunner()
    result = runner.invoke(git_status, ["--root-dir", "/nonexistent/path"])

    assert result.exit_code != 0
