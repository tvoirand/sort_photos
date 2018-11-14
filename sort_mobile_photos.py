"""
Sorts mobile photos per date.

Works with Python 3 on Mac

Version 0.2 of the 20181001

parameters:
-input      input directory
-output     output directory
"""

import argparse
import os
import datetime

parser = argparse.ArgumentParser(description="Rename photos per date.")
parser.add_argument("-time", action="store_true", help="add image creation time")
required_arguments = parser.add_argument_group("required arguments")
required_arguments.add_argument("-input", required=True, help="input directory")
required_arguments.add_argument("-output", required=True, help="output directory")
args = parser.parse_args()

def get_creation_date_and_time(file_name):
    """
    Returns creation date of a file in a specific format.

    Input:
    -file_name      string
    Output:
    -creation_date  string
    """

    stat = os.stat(file_name)

    year = str(datetime.datetime.fromtimestamp(stat.st_birthtime).year).zfill(4)

    month = str(datetime.datetime.fromtimestamp(stat.st_birthtime).month).zfill(2)

    day = str(datetime.datetime.fromtimestamp(stat.st_birthtime).day).zfill(2)

    creation_date = year + month + day

    hour = str(datetime.datetime.fromtimestamp(stat.st_birthtime).hour).zfill(2)

    minute = str(datetime.datetime.fromtimestamp(stat.st_birthtime).minute).zfill(2)

    creation_time = hour + minute

    return creation_date, creation_time

for file in os.listdir(args.input):

    if file != ".DS_Store":

        creation_date, creation_time = get_creation_date_and_time(args.input + file)

        if args.time:

            os.system("cp {} {}".format(
                args.input + file,
                args.output + creation_date + "_" + creation_time + "_" + file
            ))

        else:

            os.system("cp {} {}".format(
                args.input + file,
                args.output + creation_date + "_" + file
            ))
