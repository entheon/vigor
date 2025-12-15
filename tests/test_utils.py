"""Tests for vigor.utils module."""

from pathlib import Path

import pytest

from vigor.utils import get_immediate_subdirectories


def test_get_immediate_subdirectories(temp_dir_with_files: Path) -> None:
    result = get_immediate_subdirectories(str(temp_dir_with_files))
    assert set(result) == {"subdir1", "subdir2"}


def test_get_immediate_subdirectories_with_ignore(temp_dir_with_files: Path) -> None:
    result = get_immediate_subdirectories(str(temp_dir_with_files), ignore=["subdir1"])
    assert result == ["subdir2"]


def test_get_immediate_subdirectories_empty(temp_dir: Path) -> None:
    result = get_immediate_subdirectories(str(temp_dir))
    assert result == []


def test_get_immediate_subdirectories_relative_path_raises() -> None:
    with pytest.raises(ValueError, match="must be an Absolute Path"):
        get_immediate_subdirectories("relative/path")


def test_get_immediate_subdirectories_ignores_files(temp_dir: Path) -> None:
    (temp_dir / "file.txt").write_text("content")
    (temp_dir / "subdir").mkdir()

    result = get_immediate_subdirectories(str(temp_dir))
    assert result == ["subdir"]
