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

import sys, csv, math

"""Convenience class for tracking marker points in 3D space."""
class Point:
    
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")"

    def distanceTo(self, other):
        return math.sqrt((self.x - other.x) ** 2 +
                         (self.y - other.y) ** 2 +
                         (self.z - other.z) ** 2)

if __name__ == "__main__":
    
    # Check for proper amount of command-line arguments
    if not len(sys.argv) == 2:
        print("Wrong amount of command line arguments specified. Script takes "
              "one TSV file as input.")
        sys.exit()

    # Initialize loop variables
    frame_count = 0
    marker_names = {}
    hand_marker = None
    motion_nodes = []

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

            # Display available markers to user
            print("\nFound the following available markers:")
            for name in marker_names:
                print(name, end = "   ")
            print("\n")

            # Request user input for hand marker
            while True:
                hand_marker = input("Specify hand marker: ")
                if hand_marker not in marker_names:
                    print("\nInvalid marker name.")
                else:
                    print()
                    break

            # Request user input for motion nodes
            current_node = 1
            while True:
                node = input("Specify node " + str(current_node) + " (leave "
                             "blank for last node): ")
                if node == "":
                    if current_node > 2:
                        break
                    else:
                        print("\nThere must be at least two motion nodes.")
                elif node not in marker_names:
                    print("\nInvalid marker name.")
                elif node == hand_marker:
                    print("\nMotion nodes cannot include the hand marker.")
                else:
                    print()
                    motion_nodes += [node]
                    current_node += 1

            # Print confirmation to user
            print("\nParsing", frame_count, "frames for motion [", end = "")
            for node in motion_nodes[:-1]:
                print(node, end = " -> ")
            print(motion_nodes[-1] + "] using hand marker:", hand_marker)

            # Initialize frame iteration variables
            target_node = motion_nodes[0]
            last_node = motion_nodes[-1]
            
            # Iterate through frames
            for row in reader:
                hand_idx = marker_names[hand_marker] * 3
                hand_point = Point(float(row[hand_idx]),
                                   float(row[hand_idx + 1]),
                                   float(row[hand_idx + 2]))

                print(hand_point)

    # If the file does not exist
    except FileNotFoundError:
        print("Couldn't find matching file for '" + str(sys.argv[1]) + "'")
