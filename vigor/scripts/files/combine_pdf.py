#!/usr/bin/env python3

import os
import re

import click
from pypdf import PdfWriter


def natural_sort_key(s: str) -> list[int | str]:
    """
    Return a key for natural sorting that handles numbers within text.
    For example: ['doc_1.pdf', 'doc_2.pdf', 'doc_10.pdf'] will sort correctly.
    """

    def try_int(text: str) -> int | str:
        try:
            return int(text)
        except ValueError:
            return text.lower()

    return [try_int(c) for c in re.split(r"(\d+)", s)]


@click.command()
@click.argument("pdf_dir", type=click.Path(exists=True, file_okay=False))
@click.option("--output", "-o", default="combined.pdf", help="Output filename")
@click.option(
    "--dry-run", is_flag=True, default=False, help="Show files without merging"
)
def combine_pdf(pdf_dir: str, output: str, dry_run: bool) -> None:
    """
    Merges all PDFs in PDF_DIR into a single PDF file.

    PDFs are sorted naturally (doc_1.pdf, doc_2.pdf, doc_10.pdf).
    """
    pdf_dir = os.path.abspath(pdf_dir)
    files = os.listdir(pdf_dir)
    pdfs = sorted(
        [item for item in files if item.lower().endswith(".pdf")], key=natural_sort_key
    )

    if not pdfs:
        click.echo("No PDF files found in directory.")
        return

    click.echo(f"PDFs to merge ({len(pdfs)} files):")
    for pdf in pdfs:
        click.echo(f"  {pdf}")

    if dry_run:
        click.echo("\nDry run mode - no files were merged.")
        return

    output_path = os.path.join(pdf_dir, output)

    if os.path.exists(output_path):
        if not click.confirm(f"\n'{output}' already exists. Overwrite?"):
            click.echo("Operation cancelled.")
            return

    merger = PdfWriter()
    for pdf in pdfs:
        merger.append(os.path.join(pdf_dir, pdf))

    merger.write(output_path)
    merger.close()

    click.echo(f"\nMerged PDF saved: {output_path}")


if __name__ == "__main__":
    combine_pdf()
