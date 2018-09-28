#!/usr/bin/env python3
#
# Description: Run this script to retrieve all installed license keys
# Usage:
# ./get_licenses.py
# ./get_licenses.py > mylicenses.txt


import subprocess
import json


# Get all solutions and convert to a string
vropscmd = 'vropscli getSolution solution | awk \'{print $2}\' | tr -d , '
results = str(subprocess.check_output(vropscmd, shell=True))


# Remove prepended "b'" from byte array to string conversion
if results[0] == 'b' and results[1] == "'":
    results = results[2:]


# Build an empty dict. This will hold our k/v pairs for
# solutions/license keys
solutions = {}


for result in results.split("\\n"):
    # Filter out bad solution names (somtimes we get
    # a single quote as a solution)
    if len(result) > 2:
        # set the solution name, and remove the surrounding quotes
        solution = result.strip('"')

        # get the license key for the given solution
        vropscmd = 'vropscli getSolutionLicense "' + solution + '" | awk \'{print $5}\' | tr -d "," | tr -d \\"'
        license = str(subprocess.check_output(vropscmd, shell=True))


        # Remove prepended "b'" from byte array to string conversion
        if license[0] == 'b' and license[1] == "'":
            license = license[2:]

        # Remove trailing new line from each string
        license = license.replace('\\n\'','')

        # Do not use if license is not there
        if len(license) != 0:

            # add the solution and license
            solutions[solution] = license


# Nicely print the solution / licens pairs
for solution in solutions:
    print(solution + ": " + solutions[solution])
