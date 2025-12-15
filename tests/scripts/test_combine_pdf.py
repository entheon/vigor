"""Tests for vigor.scripts.files.combine_pdf module."""

from pathlib import Path

from click.testing import CliRunner

from vigor.scripts.files.combine_pdf import combine_pdf, natural_sort_key


def test_natural_sort_key() -> None:
    items = ["doc_1.pdf", "doc_10.pdf", "doc_2.pdf", "doc_20.pdf"]
    sorted_items = sorted(items, key=natural_sort_key)
    assert sorted_items == ["doc_1.pdf", "doc_2.pdf", "doc_10.pdf", "doc_20.pdf"]


def test_natural_sort_key_mixed() -> None:
    items = ["a1b2.pdf", "a10b1.pdf", "a2b1.pdf"]
    sorted_items = sorted(items, key=natural_sort_key)
    assert sorted_items == ["a1b2.pdf", "a2b1.pdf", "a10b1.pdf"]


def test_combine_pdf_dry_run(temp_dir_with_pdfs: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(combine_pdf, [str(temp_dir_with_pdfs), "--dry-run"])

    assert result.exit_code == 0
    assert "PDFs to merge (3 files)" in result.output
    assert "doc_1.pdf" in result.output
    assert "Dry run mode" in result.output
    assert not (temp_dir_with_pdfs / "combined.pdf").exists()


def test_combine_pdf(temp_dir_with_pdfs: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(combine_pdf, [str(temp_dir_with_pdfs)], input="y\n")

    assert result.exit_code == 0
    assert "Merged PDF saved" in result.output
    assert (temp_dir_with_pdfs / "combined.pdf").exists()


def test_combine_pdf_custom_output(temp_dir_with_pdfs: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        combine_pdf, [str(temp_dir_with_pdfs), "-o", "merged.pdf"], input="y\n"
    )

    assert result.exit_code == 0
    assert (temp_dir_with_pdfs / "merged.pdf").exists()


def test_combine_pdf_no_pdfs(temp_dir: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(combine_pdf, [str(temp_dir)])

    assert result.exit_code == 0
    assert "No PDF files found" in result.output


def test_combine_pdf_overwrite_declined(temp_dir_with_pdfs: Path) -> None:
    (temp_dir_with_pdfs / "combined.pdf").write_bytes(b"existing")

    runner = CliRunner()
    result = runner.invoke(combine_pdf, [str(temp_dir_with_pdfs)], input="n\n")

    assert result.exit_code == 0
    assert "Operation cancelled" in result.output
