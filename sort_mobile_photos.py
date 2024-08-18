"""
Sorts mobile photos per date.
"""

import argparse
import datetime
import logging
import re
import shutil
from pathlib import Path

import exifread

logger = logging.getLogger()


def simplify_camera_model(string):
    """Simplifies camera model name to create concise file names."""
    string = "".join(string.split()).lower()  # remove whitespaces and convert to lowercase
    string = re.sub(r"[^a-z0-9]", "", string)  # remove special characters
    return string


def add_trailing_number(target_filename):
    """
    Add trailing number to target filename if a file already exists with that name.

    Input:
        -filename   Path
    Output:
        -           Path
    """
    if target_filename.is_file():
        # initiate alternative filename with trailing number
        i = 2
        resulting_filename = (
            target_filename.parent / f"{target_filename.stem}_{i}{target_filename.suffix}"
        )
        while resulting_filename.is_file():
            # increase trailing number as long as alternative filename exists
            i += 1
            resulting_filename = (
                target_filename.parent / f"{target_filename.stem}_{i}{target_filename.suffix}"
            )
    else:
        resulting_filename = target_filename
    return resulting_filename


def sort_mobile_photos(input_dir, output_dir, write_time, place_name):
    """
    Sort mobile photos per file creation date.
    Input:
        -input_dir      Path
        -output_dir     Path or None
        -write_time     bool
        -place_name     string or None
    """

    # create output directory if necessary
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)

    # process each file in the input dir
    for input_file in [f for f in input_dir.iterdir() if not f.name.startswith(".")]:

        with open(input_file, "rb") as f:
            exif_tags = exifread.process_file(f, details=False)

        # get acquisition date and time
        try:
            datetime_tag = exif_tags["Image Datetime"]
            acquisition_datetime = datetime.datetime.strptime(
                datetime_tag.values, "%Y:%m:%d %H:%M:%S"
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            logger.warning(
                f"Couldn't find datetime EXIF tag for {input_file}, using file creation date"
            )
            acquisition_datetime = datetime.datetime.fromtimestamp(input_file.stat().st_birthtime)

        # get camera model
        try:
            model_tag = exif_tags["Image Model"]
            model = simplify_camera_model(model_tag.values)
        except KeyError:
            logger.warning(f"Couldn't find camera model EXIF tag for {input_file}")
            model = "other"

        # create output filename based on desired options
        filename_parts = [acquisition_datetime.strftime("%Y%m%d")]
        if write_time:
            filename_parts.append(acquisition_datetime.strftime("%H%M%S"))
        if place_name is not None:
            filename_parts.append(f"{place_name}")
        filename_parts.append(f"{model}{input_file.suffix}")
        output_filename = "_".join(filename_parts)

        if output_dir is not None:
            # copy input file to output dir with new filename
            output_filename = add_trailing_number(output_dir / output_filename)
            shutil.copy(input_file, output_dir / output_filename)
        else:
            # rename input file with new filename
            output_filename = add_trailing_number(input_dir / output_filename)
            input_file.rename(input_dir / output_filename)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Rename photos per date.")
    parser.add_argument("-t", "--time", action="store_true", help="Add image creation time")
    parser.add_argument("-o", "--output", help="Copy renamed files in output directory")
    parser.add_argument("-p", "--place", help="Name of place to include in sorted files")
    required_arguments = parser.add_argument_group("required arguments")
    required_arguments.add_argument("-i", "--input", required=True, help="Input directory")
    args = parser.parse_args()

    sort_mobile_photos(
        Path(args.input),
        None if args.output is None else Path(args.output),
        args.time,
        args.place,
    )
