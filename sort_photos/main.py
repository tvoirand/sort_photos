"""Rename photos to easily sort them by date."""

import datetime
import logging
import re
import shutil
from pathlib import Path

import exifread
import typer
from typing_extensions import Annotated

from sort_photos.cli.common import path_autocomplete

logger = logging.getLogger()

app = typer.Typer()


def simplify_camera_model(string: str) -> str:
    """Simplifies camera model name to create concise file names."""
    string = "".join(string.split()).lower()  # remove whitespaces and convert to lowercase
    string = re.sub(r"[^a-z0-9]", "", string)  # remove special characters
    return string


def add_trailing_number(target_filename: Path) -> Path:
    """Add trailing number to target filename if a file already exists with that name."""
    if target_filename.is_file():
        # Initiate alternative filename with trailing number
        i = 2
        resulting_filename = (
            target_filename.parent / f"{target_filename.stem}_{i}{target_filename.suffix}"
        )
        while resulting_filename.is_file():
            # Increase trailing number as long as alternative filename exists
            i += 1
            resulting_filename = (
                target_filename.parent / f"{target_filename.stem}_{i}{target_filename.suffix}"
            )
        return resulting_filename
    else:
        return target_filename


@app.command(no_args_is_help=True)
def sort_photos(
    input_dir: Annotated[
        Path, typer.Argument(help="Input directory", shell_complete=path_autocomplete())
    ],
    output_dir: Annotated[
        Path,
        typer.Option(
            "-o",
            "--output-dir",
            help="Copy renamed files in output directory",
            shell_complete=path_autocomplete(),
        ),
    ] = None,
    write_time: Annotated[
        bool, typer.Option("-t", "--write-time", help="Add image creation time")
    ] = False,
    tag: Annotated[str, typer.Option(help="Add a tag to include in sorted files names")] = None,
):
    """Rename photos to easily sort them by date."""

    # Create output directory if necessary
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)

    # Process each file in the input dir
    for input_file in [f for f in input_dir.iterdir() if not f.name.startswith(".")]:

        with open(input_file, "rb") as f:
            exif_tags = exifread.process_file(f, details=False)

        # Get acquisition date and time
        try:
            datetime_tag = exif_tags["Image DateTime"]
            acquisition_datetime = datetime.datetime.strptime(
                datetime_tag.values, "%Y:%m:%d %H:%M:%S"
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            logger.warning(
                f"Couldn't find datetime EXIF tag for {input_file}, using file creation date"
            )
            acquisition_datetime = datetime.datetime.fromtimestamp(input_file.stat().st_birthtime)

        # Get camera model
        model = None
        try:
            model_tag = exif_tags["Image Model"]
            model = simplify_camera_model(model_tag.values)
        except KeyError:
            logger.warning(f"Couldn't find camera model EXIF tag for {input_file}")

        # Create output filename based on desired options
        filename_parts = [acquisition_datetime.strftime("%Y%m%d")]
        if write_time:
            filename_parts.append(acquisition_datetime.strftime("%H%M%S"))
        if tag is not None:
            filename_parts.append(tag)
        if model is not None:
            filename_parts.append(model)
        output_filename = "_".join(filename_parts) + input_file.suffix

        if output_dir is not None:
            # Copy input file to output dir with new filename
            output_filename = add_trailing_number(output_dir / output_filename)
            shutil.copy(input_file, output_dir / output_filename)
        else:
            # Rename input file with new filename
            output_filename = add_trailing_number(input_dir / output_filename)
            input_file.rename(input_dir / output_filename)


if __name__ == "__main__":
    app()
