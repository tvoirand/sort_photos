"""
Sorts mobile photos per date.
"""

from pathlib import Path
import os
import sys
import shutil
import argparse
import datetime

import exifread


def get_camera_name(file_name):
    """
    Returns creation date of a file in a specific format.

    Input:
        -file_name      string
    Output:
        -camera_name    string
    """

    # identify camera
    if file_name.startswith("IMG_") and len(file_name) == 12:
        return "iphone"
    elif file_name.startswith("P") and len(file_name) == 12:
        return "lumix"
    elif len(file_name) == 23:
        return "huawei"
    else:
        return "other"


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
            target_filename.parent
            / f"{target_filename.stem}_{i}{target_filename.suffix}"
        )
        while resulting_filename.is_file():
            # increase trailing number as long as alternative filename exists
            i += 1
            resulting_filename = (
                target_filename.parent
                / f"{target_filename.stem}_{i}{target_filename.suffix}"
            )
    else:
        resulting_filename = target_filename
    return resulting_filename


def get_creation_date_and_time(file_name):
    """
    Returns creation date of a file in a specific format.

    Input:
        -file_name      Path
    Output:
        -creation_date  string
    """

    # reading exif data
    with open(file_name, "rb") as f:
        exif_tags = exifread.process_file(f)

    try:

        datetime_str = exif_tags["Image DateTime"].values

        year = datetime_str[:4]
        month = datetime_str[5:7]
        day = datetime_str[8:10]
        hour = datetime_str[11:13]
        minute = datetime_str[14:16]

    except KeyError:  # use os if exif data not correctly read

        stat = os.stat(file_name)

        year = str(datetime.datetime.fromtimestamp(stat.st_birthtime).year).zfill(4)
        month = str(datetime.datetime.fromtimestamp(stat.st_birthtime).month).zfill(2)
        day = str(datetime.datetime.fromtimestamp(stat.st_birthtime).day).zfill(2)
        hour = str(datetime.datetime.fromtimestamp(stat.st_birthtime).hour).zfill(2)
        minute = str(datetime.datetime.fromtimestamp(stat.st_birthtime).minute).zfill(2)

    creation_date = "{}{}{}".format(year, month, day)
    creation_time = "{}{}".format(hour, minute)

    return creation_date, creation_time


def sort_mobile_photos(input_dir, output_dir, write_time, place_name):
    """
    Sort mobile photos per file creation date.
    Input:
        -input_dir      Path
        -output_dir     Path or None
        -write_time     bool
        -place_name     string
    """

    # create output directory if necessary
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)

    # process each file in the input dir
    for infile in [f for f in input_dir.iterdir() if not f.name.startswith(".")]:

        # get creation date and time and camera name
        creation_date, creation_time = get_creation_date_and_time(infile)
        camera_name = get_camera_name(infile.name)

        if write_time:
            # create new filename with creation date and time as filename stem
            output_filename = (
                f"{creation_date}_{creation_time}_{place_name}_{camera_name}{infile.suffix}"
            )

        else:
            # create new filename with creation date as filename stem
            output_filename = f"{creation_date}_{place_name}_{camera_name}{infile.suffix}"

        if output_dir is not None:
            # copy input file to output dir with new filename
            output_filename = add_trailing_number(output_dir / output_filename)
            shutil.copy(infile, output_dir / output_filename)
        else:
            # rename input file with new filename
            output_filename = add_trailing_number(input_dir / output_filename)
            infile.rename(input_dir / output_filename)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Rename photos per date.")
    parser.add_argument(
        "-t", "--time", action="store_true", help="optional: add image creation time"
    )
    parser.add_argument(
        "-o", "--output", help="optional: copy renamed files in output directory"
    )
    required_arguments = parser.add_argument_group("required arguments")
    required_arguments.add_argument(
        "-i", "--input", required=True, help="input directory"
    )
    required_arguments.add_argument(
        "-p", "--place", required=True, help="name of place to include in sorted files"
    )
    args = parser.parse_args()

    sort_mobile_photos(
        Path(args.input), None if args.output is None else Path(args.output), args.time, args.place
    )
