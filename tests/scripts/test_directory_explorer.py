"""Tests for vigor.scripts.files.directory_explorer module."""

from pathlib import Path

from click.testing import CliRunner

from vigor.scripts.files.directory_explorer import directory_explorer


def test_directory_explorer(temp_dir_with_files: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(directory_explorer, [str(temp_dir_with_files)])

    assert result.exit_code == 0
    assert "file1.txt" in result.output
    assert "file2.txt" in result.output
    assert "file3.txt" in result.output
    assert "Grand Total" in result.output


def test_directory_explorer_empty(temp_dir: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(directory_explorer, [str(temp_dir)])

    assert result.exit_code == 0
    assert "Grand Total: 0 files" in result.output


def test_directory_explorer_shows_sizes(temp_dir: Path) -> None:
    (temp_dir / "test.txt").write_text("x" * 1000)

    runner = CliRunner()
    result = runner.invoke(directory_explorer, [str(temp_dir)])

    assert result.exit_code == 0
    assert "test.txt" in result.output
    assert "1K" in result.output or "1000" in result.output


def test_directory_explorer_nonexistent_dir() -> None:
    runner = CliRunner()
    result = runner.invoke(directory_explorer, ["/nonexistent/path"])

    assert result.exit_code != 0
