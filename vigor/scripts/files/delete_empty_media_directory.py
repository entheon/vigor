#!/usr/bin/env python3

import os
from typing import List, Tuple

import click

to_delete: List[Tuple[str, str]] = []

# Video file extensions
MEDIA_EXTENSIONS = {
    # Videos
    '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg',
    '.mpeg', '.3gp', '.ts', '.mts', '.m2ts', '.vob', '.ogv'
}


def contains_video_files(directory: str, recursive_check: bool = False) -> bool:
    """
    Check if a directory contains any video files.

    Args:
        directory (str): Path to the directory to check
        recursive_check (bool): Whether to check subdirectories recursively for video files

    Returns:
        bool: True if directory contains video files, False otherwise
    """
    try:
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                _, ext = os.path.splitext(item.lower())
                if ext in MEDIA_EXTENSIONS:
                    return True
            elif os.path.isdir(item_path) and recursive_check:
                # Recursively check subdirectories if flag is enabled
                if contains_video_files(item_path, recursive_check=True):
                    return True
    except (OSError, PermissionError):
        # If we can't read the directory, assume it contains video to be safe
        return True
    return False


def scan_directory(root_dir: str, recursive: bool = False, recursive_check: bool = False) -> None:
    """
    Scan directory for empty video directories and add them to to_delete list.

    Args:
        root_dir (str): Root directory to scan
        recursive (bool): Whether to scan recursively
        recursive_check (bool): Whether to check subdirectories recursively for video files
    """
    try:
        for item in os.listdir(root_dir):
            item_path = os.path.join(root_dir, item)

            if os.path.isdir(item_path):
                # Check if this directory contains video files
                if not contains_video_files(item_path, recursive_check=recursive_check):
                    # Check if directory is completely empty or only contains non-video files
                    try:
                        dir_contents = os.listdir(item_path)
                        if not dir_contents:
                            # Empty directory
                            to_delete.append((item_path, "Empty directory"))
                        else:
                            # Directory with only non-video files
                            desc = "No video files found (deep scan)" if recursive_check else "No video files found"
                            to_delete.append((item_path, desc))
                    except (OSError, PermissionError):
                        pass

                # If recursive, scan subdirectories
                if recursive:
                    scan_directory(item_path, recursive=True, recursive_check=recursive_check)

    except (OSError, PermissionError) as e:
        click.echo(f"Error scanning directory {root_dir}: {e}", err=True)


@click.command()
@click.argument("root_dir")
@click.option("--dry-run", is_flag=True, default=False, help="Dry Run")
@click.option(
    "-r",
    "--recursive",
    is_flag=True,
    default=False,
    help="Should recursively check sub-directories",
)
@click.option(
    "--deep",
    is_flag=True,
    default=False,
    help="Recursively check subdirectories within each directory for video files",
)
def delete_empty_media_directory(root_dir: str, dry_run: bool, recursive: bool, deep: bool) -> None:
    """
    Finds folders in root_dir do not contain any video files and removes them.

    Args:
        root_dir (str): Root Directory to scan. Only looks at first level
        subdirectories unless --recursive is used.

    Options:
        --dry-run: Show what would be deleted without actually deleting
        -r/--recursive: Scan subdirectories recursively for empty directories
        --deep: Check subdirectories within each directory for video files
    """
    # Validate root directory
    if not os.path.exists(root_dir):
        click.echo(f"Error: Directory '{root_dir}' does not exist.", err=True)
        return

    if not os.path.isdir(root_dir):
        click.echo(f"Error: '{root_dir}' is not a directory.", err=True)
        return

    # Clear the to_delete list in case of multiple runs
    to_delete.clear()

    # Scan for empty video directories
    scan_directory(root_dir, recursive, deep)

    if not to_delete:
        click.echo("No empty video directories found.")
        return

    # Display what will be deleted
    click.echo(f"Found {len(to_delete)} directories to delete:")
    for dir_path, reason in to_delete:
        click.echo(f"  {dir_path} - {reason}")

    if dry_run:
        click.echo("\nDry run mode - no directories were actually deleted.")
        return

    # Ask for confirmation before deleting
    if not click.confirm(f"\nProceed with deleting {len(to_delete)} directories?"):
        click.echo("Operation cancelled.")
        return

    # Delete directories
    deleted_count = 0
    for dir_path, reason in to_delete:
        try:
            # Use rmdir for empty directories, or handle non-empty ones
            if os.path.exists(dir_path):
                import shutil
                shutil.rmtree(dir_path)
                click.echo(f"Deleted: {dir_path}")
                deleted_count += 1
        except OSError as e:
            click.echo(f"Error deleting {dir_path}: {e}", err=True)

    click.echo(f"\nSuccessfully deleted {deleted_count} directories.")


if __name__ == "__main__":
    delete_empty_media_directory()
