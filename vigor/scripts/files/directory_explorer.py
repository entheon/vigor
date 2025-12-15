#!/usr/bin/env python3

import os

import click
from hurry.filesize import size


def print_directory(directory_path: str, directory_files: list[str]) -> None:
    total_size = 0

    click.echo("=" * 60)
    click.echo(f"Directory: {directory_path}")

    for file_name in directory_files:
        file_path = os.path.join(directory_path, file_name)
        try:
            current_size = os.path.getsize(file_path)
            click.echo(f"  {file_name} | {size(current_size)}")
            total_size += current_size
        except OSError:
            click.echo(f"  {file_name} | (unable to read)")

    click.echo(f"Total: {size(total_size)}")


@click.command()
@click.argument("root_dir", type=click.Path(exists=True, file_okay=False))
def directory_explorer(root_dir: str) -> None:
    """
    Walks through ROOT_DIR and displays all files with their sizes.
    """
    root_dir = os.path.abspath(root_dir)
    total_size = 0
    total_files = 0

    for dirpath, _, filenames in os.walk(root_dir):
        if filenames:
            print_directory(dirpath, filenames)
            for file_name in filenames:
                file_path = os.path.join(dirpath, file_name)
                try:
                    total_size += os.path.getsize(file_path)
                    total_files += 1
                except OSError:
                    pass

    click.echo("=" * 60)
    click.echo(f"Grand Total: {total_files} files, {size(total_size)}")


if __name__ == "__main__":
    directory_explorer()
