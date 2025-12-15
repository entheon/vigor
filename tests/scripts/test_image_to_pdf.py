"""Tests for vigor.scripts.files.image_to_pdf module."""

from pathlib import Path

from click.testing import CliRunner

from vigor.scripts.files.image_to_pdf import image_to_pdf, natural_sort_key


def test_natural_sort_key() -> None:
    items = ["img_1.png", "img_10.png", "img_2.png"]
    sorted_items = sorted(items, key=natural_sort_key)
    assert sorted_items == ["img_1.png", "img_2.png", "img_10.png"]


def test_image_to_pdf_dry_run(temp_dir_with_images: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(image_to_pdf, [str(temp_dir_with_images), "--dry-run"])

    assert result.exit_code == 0
    assert "Images to convert (3 files)" in result.output
    assert "Dry run mode" in result.output
    assert not (temp_dir_with_images / "output.pdf").exists()


def test_image_to_pdf(temp_dir_with_images: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(image_to_pdf, [str(temp_dir_with_images)], input="y\n")

    assert result.exit_code == 0
    assert "PDF saved" in result.output
    assert (temp_dir_with_images / "output.pdf").exists()


def test_image_to_pdf_custom_output(temp_dir_with_images: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        image_to_pdf, [str(temp_dir_with_images), "-o", "images.pdf"], input="y\n"
    )

    assert result.exit_code == 0
    assert (temp_dir_with_images / "images.pdf").exists()


def test_image_to_pdf_no_images(temp_dir: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(image_to_pdf, [str(temp_dir)])

    assert result.exit_code == 0
    assert "No image files found" in result.output


def test_image_to_pdf_overwrite_declined(temp_dir_with_images: Path) -> None:
    (temp_dir_with_images / "output.pdf").write_bytes(b"existing")

    runner = CliRunner()
    result = runner.invoke(image_to_pdf, [str(temp_dir_with_images)], input="n\n")

    assert result.exit_code == 0
    assert "Operation cancelled" in result.output
