#!/usr/bin/env python3

import os
import shutil
from dataclasses import dataclass, field
from typing import Optional

import click

MEDIA_EXTENSIONS: set[str] = {
    ".mp4",
    ".avi",
    ".mkv",
    ".mov",
    ".wmv",
    ".flv",
    ".webm",
    ".m4v",
    ".mpg",
    ".mpeg",
    ".3gp",
    ".ts",
    ".mts",
    ".m2ts",
    ".vob",
    ".ogv",
}


@dataclass
class DirectoryNode:
    path: str
    has_direct_media: bool = False
    children: dict[str, "DirectoryNode"] = field(default_factory=dict)
    parent: Optional["DirectoryNode"] = None

    @property
    def has_any_media(self) -> bool:
        if self.has_direct_media:
            return True
        return any(child.has_any_media for child in self.children.values())

    @property
    def is_empty(self) -> bool:
        return not os.listdir(self.path) if os.path.exists(self.path) else True


def has_media_files(directory: str) -> bool:
    try:
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                _, ext = os.path.splitext(item.lower())
                if ext in MEDIA_EXTENSIONS:
                    return True
    except (OSError, PermissionError):
        pass
    return False


def build_directory_tree(root_dir: str) -> DirectoryNode:
    root_node = DirectoryNode(path=root_dir, has_direct_media=has_media_files(root_dir))

    def build_subtree(node: DirectoryNode) -> None:
        try:
            for item in os.listdir(node.path):
                item_path = os.path.join(node.path, item)
                if os.path.isdir(item_path):
                    child_node = DirectoryNode(
                        path=item_path,
                        has_direct_media=has_media_files(item_path),
                        parent=node,
                    )
                    node.children[item] = child_node
                    build_subtree(child_node)
        except (OSError, PermissionError):
            pass

    build_subtree(root_node)
    return root_node


def find_empty_branches(node: DirectoryNode, results: list[DirectoryNode]) -> None:
    if not node.has_any_media:
        results.append(node)
        return

    for child in node.children.values():
        find_empty_branches(child, results)


def consolidate_deletions(candidates: list[DirectoryNode]) -> list[DirectoryNode]:
    if not candidates:
        return []

    candidate_paths = {node.path for node in candidates}
    consolidated: list[DirectoryNode] = []

    for node in candidates:
        parent = node.parent
        parent_is_candidate = False
        while parent is not None:
            if parent.path in candidate_paths:
                parent_is_candidate = True
                break
            parent = parent.parent

        if not parent_is_candidate:
            consolidated.append(node)

    return consolidated


def count_subdirectories(node: DirectoryNode) -> int:
    count = len(node.children)
    for child in node.children.values():
        count += count_subdirectories(child)
    return count


def get_deletion_reason(node: DirectoryNode) -> str:
    if node.is_empty:
        return "Empty directory"

    subdir_count = count_subdirectories(node)
    if subdir_count > 0:
        return f"No media in tree ({subdir_count} subdirs)"
    return "No media files"


@click.command()
@click.argument("root_dir", type=click.Path(exists=True, file_okay=False))
@click.option(
    "--dry-run", is_flag=True, default=False, help="Show dirs without deleting"
)
def delete_empty_media_directory(root_dir: str, dry_run: bool) -> None:
    """
    Scans ROOT_DIR for directories without media files and suggests deletions.

    Intelligently consolidates suggestions - if a parent and all children have
    no media, only the parent is suggested for deletion.
    """
    root_dir = os.path.abspath(root_dir)
    tree = build_directory_tree(root_dir)

    candidates: list[DirectoryNode] = []
    for child in tree.children.values():
        find_empty_branches(child, candidates)

    consolidated = consolidate_deletions(candidates)

    if not consolidated:
        click.echo("No empty media directories found.")
        return

    click.echo(f"Found {len(consolidated)} directories to delete:")
    for node in consolidated:
        reason = get_deletion_reason(node)
        click.echo(f"  {node.path} - {reason}")

    if dry_run:
        click.echo("\nDry run mode - no directories were deleted.")
        return

    if not click.confirm(f"\nProceed with deleting {len(consolidated)} directories?"):
        click.echo("Operation cancelled.")
        return

    deleted_count = 0
    for node in consolidated:
        try:
            if os.path.exists(node.path):
                shutil.rmtree(node.path)
                click.echo(f"Deleted: {node.path}")
                deleted_count += 1
        except OSError as e:
            click.echo(f"Error deleting {node.path}: {e}", err=True)

    click.echo(f"\nSuccessfully deleted {deleted_count} directories.")


if __name__ == "__main__":
    delete_empty_media_directory()
