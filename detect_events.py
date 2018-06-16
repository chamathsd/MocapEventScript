#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Author: Chamath "Jake" Dharmasiri
Date: 06/15/2018

Script to automate the detection of motion events between predetermined nodes
for the purpose of mocap data analysis.

This script takes as its only command-line argument the relative or absolute
path to the exported TSV file of the mocap data. From there, the user will be
asked to specify the nodes that define the motion event.
"""


import sys, csv

# Check for proper amount of command-line arguments
if not len(sys.argv) == 2:
    print("Wrong amount of command line arguments specified. Script takes one"
          " TSV file as input.")
    sys.exit()

# Begin load of TSV document
try:
    with open(sys.argv[1]) as tsv:
        reader = csv.DictReader(tsv, delimiter='\t')

# If the file does not exist
except FileNotFoundError:
    print("Couldn't find matching file for '" + str(sys.argv[1]) + "'")
