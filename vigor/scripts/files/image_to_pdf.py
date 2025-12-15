#!/usr/bin/env python3

import os
import re

import click
from PIL import Image

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".gif")


def natural_sort_key(s: str) -> list[int | str]:
    """
    Return a key for natural sorting that handles numbers within text.
    For example: ['img_1.jpg', 'img_2.jpg', 'img_10.jpg'] will sort correctly.
    """

    def try_int(text: str) -> int | str:
        try:
            return int(text)
        except ValueError:
            return text.lower()

    return [try_int(c) for c in re.split(r"(\d+)", s)]


@click.command()
@click.argument("image_dir", type=click.Path(exists=True, file_okay=False))
@click.option("--output", "-o", default="output.pdf", help="Output filename")
@click.option(
    "--dry-run", is_flag=True, default=False, help="Show files without converting"
)
def image_to_pdf(image_dir: str, output: str, dry_run: bool) -> None:
    """
    Converts all images in IMAGE_DIR to a single PDF file.

    Images are sorted naturally (img_1.jpg, img_2.jpg, img_10.jpg).
    Supports: PNG, JPG, JPEG, WebP, BMP, TIFF, GIF.
    """
    image_dir = os.path.abspath(image_dir)
    files = os.listdir(image_dir)

    images = sorted(
        [item for item in files if item.lower().endswith(IMAGE_EXTENSIONS)],
        key=natural_sort_key,
    )

    if not images:
        click.echo("No image files found in directory.")
        return

    click.echo(f"Images to convert ({len(images)} files):")
    for image_name in images:
        click.echo(f"  {image_name}")

    if dry_run:
        click.echo("\nDry run mode - no files were converted.")
        return

    output_path = os.path.join(image_dir, output)

    if os.path.exists(output_path):
        if not click.confirm(f"\n'{output}' already exists. Overwrite?"):
            click.echo("Operation cancelled.")
            return

    image_paths = [os.path.join(image_dir, name) for name in images]
    image_objects: list[Image.Image] = []

    try:
        for path in image_paths:
            image = Image.open(path).convert("RGB")
            image_objects.append(image)

        image_objects[0].save(
            output_path, "PDF", save_all=True, append_images=image_objects[1:]
        )

        click.echo(f"\nPDF saved: {output_path}")
    finally:
        for image in image_objects:
            image.close()


if __name__ == "__main__":
    image_to_pdf()
