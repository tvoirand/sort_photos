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


def sort_mobile_photos(input_dir, output_dir, write_time):
    """
    Sort mobile photos per file creation date.
    Input:
        -input_dir      Path
        -output_dir     Path
        -write_time     bool
    """

    # create output directory if necessary
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)

    # process each file in the input dir
    for infile in [f for f in input_dir.iterdir() if not f.name.startswith(".")]:

        # get creation date and time and camera name
        creation_date, creation_time = get_creation_date_and_time(infile)

        if write_time:
            # create new filename with creation date and time as filename stem
            output_filename = f"{creation_date}_{creation_time}_{infile.name}"

        else:
            # create new filename with creation date as filename stem
            output_filename = f"{creation_date}_{infile.name}"

        if output_dir is not None:
            # copy input file to output dir with new filename
            shutil.copy(infile, output_dir / output_filename)
        else:
            # rename input file with new filename
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
    args = parser.parse_args()

    sort_mobile_photos(
        Path(args.input), None if args.output is None else Path(args.output), args.time
    )
