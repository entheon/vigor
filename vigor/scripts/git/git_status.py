#!/usr/bin/env python3

import os
from pathlib import Path

import click
from git import InvalidGitRepositoryError, Repo


def check_repo_status(repo_path: str, quiet: bool) -> bool:
    """
    Check and display status for a single git repository.

    Returns True if the repo has changes, False otherwise.
    """
    try:
        repo = Repo(repo_path)
        if repo.bare:
            return False

        repo_name = os.path.basename(repo_path)
        branch = repo.active_branch

        has_changes = (
            repo.is_dirty()
            or repo.untracked_files
            or len(list(repo.iter_commits(f"{branch}@{{u}}..{branch}"))) != 0
        )

        if has_changes:
            click.echo("=" * 70)
            click.echo(f"Changes in {repo_name} ({repo_path})")
            click.echo(repo.git.status())
            click.echo()
            return True
        elif not quiet:
            click.echo("=" * 70)
            click.echo(f"Clean: {repo_name} ({repo_path})")
            click.echo()

        return False

    except InvalidGitRepositoryError:
        return False
    except Exception:
        return False


@click.command()
@click.option(
    "--root-dir",
    type=click.Path(exists=True, file_okay=False),
    default=Path.home(),
    help="Root directory to scan for git repositories",
)
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    default=False,
    help="Only show repositories with changes",
)
@click.option(
    "-r",
    "--recursive",
    is_flag=True,
    default=False,
    help="Recursively scan subdirectories for git repositories",
)
def git_status(root_dir: str, quiet: bool, recursive: bool) -> None:
    """
    Check git status for all repositories under ROOT_DIR.

    By default, only scans immediate subdirectories. Use -r to scan recursively.
    """
    root_dir = str(root_dir)

    if not os.path.exists(root_dir):
        click.echo(f"Error: Directory '{root_dir}' does not exist.", err=True)
        return

    repos_with_changes = 0
    repos_checked = 0

    if recursive:
        for dirpath, dirnames, _ in os.walk(root_dir):
            if ".git" in dirnames:
                repos_checked += 1
                if check_repo_status(dirpath, quiet):
                    repos_with_changes += 1
                dirnames.remove(".git")
    else:
        for item in os.scandir(root_dir):
            if item.is_dir():
                repos_checked += 1
                if check_repo_status(item.path, quiet):
                    repos_with_changes += 1

    click.echo("=" * 70)
    click.echo(f"Summary: {repos_with_changes}/{repos_checked} repos have changes")


if __name__ == "__main__":
    git_status()
