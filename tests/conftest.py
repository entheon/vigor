"""Shared test fixtures for vigor tests."""

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory that is cleaned up after the test."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_dir_with_files(temp_dir: Path) -> Path:
    """Create a temporary directory with some test files."""
    (temp_dir / "file1.txt").write_text("content1")
    (temp_dir / "file2.txt").write_text("content2")
    (temp_dir / "subdir1").mkdir()
    (temp_dir / "subdir1" / "file3.txt").write_text("content3")
    (temp_dir / "subdir2").mkdir()
    return temp_dir


@pytest.fixture
def temp_dir_with_media(temp_dir: Path) -> Path:
    """Create a temporary directory structure for media pruning tests."""
    (temp_dir / "has_video").mkdir()
    (temp_dir / "has_video" / "movie.mp4").write_bytes(b"fake video")

    (temp_dir / "empty_dir").mkdir()

    (temp_dir / "no_video").mkdir()
    (temp_dir / "no_video" / "readme.txt").write_text("no video here")

    (temp_dir / "nested_empty").mkdir()
    (temp_dir / "nested_empty" / "child1").mkdir()
    (temp_dir / "nested_empty" / "child2").mkdir()

    return temp_dir


@pytest.fixture
def temp_dir_with_pdfs(temp_dir: Path) -> Path:
    """Create a temporary directory with PDF files for testing."""
    from pypdf import PdfWriter

    for name in ["doc_1.pdf", "doc_2.pdf", "doc_10.pdf"]:
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        with open(temp_dir / name, "wb") as f:
            writer.write(f)

    return temp_dir


@pytest.fixture
def temp_dir_with_images(temp_dir: Path) -> Path:
    """Create a temporary directory with image files for testing."""
    from PIL import Image

    for name in ["img_1.png", "img_2.png", "img_10.png"]:
        img = Image.new("RGB", (10, 10), color="red")
        img.save(temp_dir / name)

    return temp_dir


@pytest.fixture
def temp_git_repos(temp_dir: Path) -> Path:
    """Create temporary git repositories for testing."""
    import subprocess

    clean_repo = temp_dir / "clean_repo"
    clean_repo.mkdir()
    subprocess.run(["git", "init"], cwd=clean_repo, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=clean_repo,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"], cwd=clean_repo, capture_output=True
    )
    (clean_repo / "file.txt").write_text("content")
    subprocess.run(["git", "add", "."], cwd=clean_repo, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "initial"], cwd=clean_repo, capture_output=True
    )

    dirty_repo = temp_dir / "dirty_repo"
    dirty_repo.mkdir()
    subprocess.run(["git", "init"], cwd=dirty_repo, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=dirty_repo,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"], cwd=dirty_repo, capture_output=True
    )
    (dirty_repo / "file.txt").write_text("content")
    subprocess.run(["git", "add", "."], cwd=dirty_repo, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "initial"], cwd=dirty_repo, capture_output=True
    )
    (dirty_repo / "uncommitted.txt").write_text("uncommitted")

    not_a_repo = temp_dir / "not_a_repo"
    not_a_repo.mkdir()
    (not_a_repo / "file.txt").write_text("content")

    return temp_dir
