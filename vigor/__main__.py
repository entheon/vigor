"""Entry point for running vigor as a module: python -m vigor."""

import click

from vigor import __version__


@click.group()
@click.version_option(version=__version__, prog_name="vigor")
def cli() -> None:
    """Vigor - A collection of useful Python scripts and CLI tools."""


@cli.command()
def version() -> None:
    """Show version information."""
    click.echo(f"vigor {__version__}")


if __name__ == "__main__":
    cli()
