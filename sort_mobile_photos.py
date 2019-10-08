"""
Sorts mobile photos per date.
"""

import argparse
import os
import datetime
import exifread



def get_creation_date_and_time(file_name):
    """
    Returns creation date of a file in a specific format.

    Input:
    -file_name      string
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

    except KeyError: # use os if exif data not correctly read

        stat = os.stat(file_name)

        year = str(datetime.datetime.fromtimestamp(stat.st_birthtime).year).zfill(4)
        month = str(datetime.datetime.fromtimestamp(stat.st_birthtime).month).zfill(2)
        day = str(datetime.datetime.fromtimestamp(stat.st_birthtime).day).zfill(2)
        hour = str(datetime.datetime.fromtimestamp(stat.st_birthtime).hour).zfill(2)
        minute = str(datetime.datetime.fromtimestamp(stat.st_birthtime).minute).zfill(2)

    creation_date = year + month + day
    creation_time = hour + minute

    return creation_date, creation_time


def sort_mobile_photos(input_dir, output_dir, write_time):
    """
    Sort mobile photos per file creation date.
    Input:
        -input_dir      str
        -output_dir     str
        -write_time     bool
    """

    if not output_dir == "" and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file in os.listdir(input_dir):

        if file != ".DS_Store":

            creation_date, creation_time = get_creation_date_and_time(input_dir + file)

            if write_time:

                os.system(
                    "cp {} {}".format(
                        os.path.join(input_dir, file),
                        os.path.join(
                            output_dir, "_".join((creation_date, creation_time, file))
                        ),
                    )
                )

            else:

                os.system(
                    "cp {} {}".format(
                        os.path.join(input_dir, file),
                        os.path.join(output_dir, "_".join((creation_date, file))),
                    )
                )


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Rename photos per date.")
    parser.add_argument("-t", "--time", action="store_true", help="add image creation time")
    required_arguments = parser.add_argument_group("required arguments")
    required_arguments.add_argument("-i", "--input", required=True, help="input directory")
    required_arguments.add_argument("-o", "--output", required=True, help="output directory")
    args = parser.parse_args()

    sort_mobile_photos(args.input, args.output, args.time)
