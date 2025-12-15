"""Tests for vigor.scripts.files.delete_empty_media_directory module."""

from pathlib import Path

from click.testing import CliRunner

from vigor.scripts.files.delete_empty_media_directory import (
    DirectoryNode,
    build_directory_tree,
    consolidate_deletions,
    delete_empty_media_directory,
    find_empty_branches,
    has_media_files,
)


def test_has_media_files_true(temp_dir: Path) -> None:
    (temp_dir / "video.mp4").write_bytes(b"fake video")
    assert has_media_files(str(temp_dir)) is True


def test_has_media_files_false(temp_dir: Path) -> None:
    (temp_dir / "document.txt").write_text("text")
    assert has_media_files(str(temp_dir)) is False


def test_has_media_files_empty(temp_dir: Path) -> None:
    assert has_media_files(str(temp_dir)) is False


def test_build_directory_tree(temp_dir_with_media: Path) -> None:
    tree = build_directory_tree(str(temp_dir_with_media))

    assert tree.path == str(temp_dir_with_media)
    assert "has_video" in tree.children
    assert "empty_dir" in tree.children
    assert "no_video" in tree.children
    assert "nested_empty" in tree.children


def test_build_directory_tree_detects_media(temp_dir_with_media: Path) -> None:
    tree = build_directory_tree(str(temp_dir_with_media))

    assert tree.children["has_video"].has_direct_media is True
    assert tree.children["no_video"].has_direct_media is False
    assert tree.children["empty_dir"].has_direct_media is False


def test_find_empty_branches(temp_dir_with_media: Path) -> None:
    tree = build_directory_tree(str(temp_dir_with_media))
    candidates: list[DirectoryNode] = []
    for child in tree.children.values():
        find_empty_branches(child, candidates)

    candidate_names = {Path(c.path).name for c in candidates}
    assert "empty_dir" in candidate_names
    assert "no_video" in candidate_names
    assert "nested_empty" in candidate_names
    assert "has_video" not in candidate_names


def test_consolidate_deletions() -> None:
    parent = DirectoryNode(path="/parent", has_direct_media=False)
    child1 = DirectoryNode(path="/parent/child1", has_direct_media=False, parent=parent)
    child2 = DirectoryNode(path="/parent/child2", has_direct_media=False, parent=parent)
    parent.children = {"child1": child1, "child2": child2}

    candidates = [parent, child1, child2]
    consolidated = consolidate_deletions(candidates)

    assert len(consolidated) == 1
    assert consolidated[0].path == "/parent"


def test_delete_empty_media_directory_dry_run(temp_dir_with_media: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        delete_empty_media_directory, [str(temp_dir_with_media), "--dry-run"]
    )

    assert result.exit_code == 0
    assert "Dry run mode" in result.output
    assert (temp_dir_with_media / "empty_dir").exists()
    assert (temp_dir_with_media / "no_video").exists()


def test_delete_empty_media_directory(temp_dir_with_media: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        delete_empty_media_directory, [str(temp_dir_with_media)], input="y\n"
    )

    assert result.exit_code == 0
    assert "Successfully deleted" in result.output
    assert (temp_dir_with_media / "has_video").exists()
    assert not (temp_dir_with_media / "empty_dir").exists()
    assert not (temp_dir_with_media / "no_video").exists()


def test_delete_empty_media_directory_cancelled(temp_dir_with_media: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        delete_empty_media_directory, [str(temp_dir_with_media)], input="n\n"
    )

    assert result.exit_code == 0
    assert "Operation cancelled" in result.output
    assert (temp_dir_with_media / "empty_dir").exists()


def test_delete_empty_media_directory_no_empty(temp_dir: Path) -> None:
    (temp_dir / "subdir").mkdir()
    (temp_dir / "subdir" / "video.mkv").write_bytes(b"video")

    runner = CliRunner()
    result = runner.invoke(delete_empty_media_directory, [str(temp_dir)])

    assert result.exit_code == 0
    assert "No empty media directories found" in result.output
