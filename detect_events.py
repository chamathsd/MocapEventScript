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

if __name__ == "__main__":
    
    # Check for proper amount of command-line arguments
    if not len(sys.argv) == 2:
        print("Wrong amount of command line arguments specified. Script takes one"
              " TSV file as input.")
        sys.exit()

    # Initialize loop variables
    frame_count = 0
    marker_names = {}

    # Begin load of TSV document
    try:
        with open(sys.argv[1]) as tsv:
            reader = csv.reader(tsv, delimiter='\t')

            # Parse header tags
            for row in reader:
                
                # Get frame count
                if (row[0] == "NO_OF_FRAMES"):
                    frame_count = int(row[1])
                    
                # Populate marker dictionary
                if (row[0] == "MARKER_NAMES"):
                    for idx in range(1, len(row)):
                        
                        suffix = 0
                        name = row[idx]

                        # Add suffix as necessary for ambiguous markers
                        while name in marker_names:
                            suffix += 1
                            name = "%s_%d" % (row[idx], suffix)
                        marker_names[name] = idx - 1
                    break

            # Iterate through frames
            for row in reader:
                print(row[0])
                

    # If the file does not exist
    except FileNotFoundError:
        print("Couldn't find matching file for '" + str(sys.argv[1]) + "'")
