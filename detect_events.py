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

import os, sys, csv, math

""" Global constants """
APPROACH_THRESHOLD = 0.35   # Ratio to begin tracking; should be less than 0.5
APPROACH_BUFFER = 5         # Minimum amount of frames to track

""" Convenience class for tracking marker points in 3D space. """
class Point:
    
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

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
    frequency = 1
    marker_names = {}
    hand_marker = None
    motion_nodes = []

    # Begin load of TSV document
    try:
        save_file = os.path.splitext(sys.argv[1])[0] + "_events.csv"
        with open(sys.argv[1], 'r') as load:
            reader = csv.reader(load, delimiter='\t')

            # Parse header tags
            for row in reader:
                
                # Get frame count
                if (row[0] == "NO_OF_FRAMES"):
                    frame_count = int(row[1])

                # Get frequency
                elif (row[0] == "FREQUENCY"):
                    frequency = int(row[1])
                    
                # Populate marker dictionary
                elif (row[0] == "MARKER_NAMES"):
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
                node = input("Specify node " + str(current_node) + " of motion"
                             " (leave blank if complete): ")
                if node == "":
                    if current_node > 2:
                        break
                    else:
                        print("\nThere must be at least two motion nodes.")
                elif node not in marker_names:
                    print("\nInvalid marker name.")
                elif node == hand_marker:
                    print("\nMotion nodes cannot include the hand marker.")
                elif len(motion_nodes) > 0 and node == motion_nodes[-1]:
                    print("\nNode cannot be the same as the previous node.")
                else:
                    print()
                    motion_nodes += [node]
                    current_node += 1

            # Print confirmation to user
            print("\n\nParsing", frame_count, "frames for motion [", end = "")
            for node in motion_nodes[:-1]:
                print(node, end = " -> ")
            print(motion_nodes[-1] + "] using hand marker:", hand_marker)

            # Initialize frame iteration variables
            current_frame = 1
            bad_frames = 0

            event_num = 1
            motion_start = -1
            motion_end = -1
            tracking = False
            buffer = 0
            frame_store = []
            events = []

            target_idx = 0
            target_node = motion_nodes[target_idx]
            previous_node = motion_nodes[target_idx - 1]
            zero_point = Point(0, 0, 0)

            # Iterate through mocap data
            for row in reader:
                # Create 3D point for hand marker
                hand_col = marker_names[hand_marker] * 3
                hand_point = Point(float(row[hand_col]),
                                   float(row[hand_col + 1]),
                                   float(row[hand_col + 2]))

                if hand_point == zero_point:
                    bad_frames += 1
                    continue

                # Create 3D point for target node
                target_col = marker_names[target_node] * 3
                target_point = Point(float(row[target_col]),
                                     float(row[target_col + 1]),
                                     float(row[target_col + 2]))

                if target_point == zero_point:
                    bad_frames += 1
                    continue

                # Create 3D point for previous node
                previous_col = marker_names[previous_node] * 3
                previous_point = Point(float(row[previous_col]),
                                       float(row[previous_col + 1]),
                                       float(row[previous_col + 2]))

                if previous_point == zero_point:
                    bad_frames += 1
                    continue

                # Determine the ratio between target and previous node distances
                target_distance = hand_point.distanceTo(target_point)
                previous_distance = hand_point.distanceTo(previous_point)
                approach_ratio = target_distance / previous_distance

                buffer -= 1
                
                if approach_ratio <= APPROACH_THRESHOLD:
                    if not tracking:
                        # We are entering the target node approach area
                        tracking = True
                        buffer = APPROACH_BUFFER
                    frame_store += [(target_distance, current_frame)]
                else:
                    if tracking and buffer <= 0:
                        # We are leaving the target node approach area
                        if target_idx == 0:
                            # If we are at the beginning of the motion
                            motion_start = min(frame_store)[1]
                            
                        elif target_idx == (len(motion_nodes) - 1):
                            # If we are at the end of the motion
                            motion_end = min(frame_store)[1]

                            # Register our event with the event list
                            event = [event_num,
                                     motion_start,
                                     motion_end,
                                     round((motion_end - motion_start) /
                                           frequency, 2)]
                            events += [event]
                            
                            # Reset motion variables
                            event_num += 1
                            motion_start = -1
                            motion_end = -1

                        # Reset tracking variables
                        tracking = False
                        frame_store = []

                        # Rotate target and previous nodes
                        target_idx = (target_idx + 1) % len(motion_nodes)
                        target_node = motion_nodes[target_idx]
                        previous_node = motion_nodes[target_idx - 1]

                # Bump our frame count
                current_frame += 1

            # Give completion feedback to user
            print("\n\nFinished reading frames. Found", event_num - 1,
                  "events. ", end = '')

            # Check if any events were actually recorded
            if len(events) > 0:
                save_file = os.path.splitext(sys.argv[1])[0] + "_events.csv"
                try:
                    with open(save_file, 'w', newline = '') as save:
                        writer = csv.writer(save, delimiter=',')

                        # Write file header
                        writer.writerow(["Motion",
                                         "Start Frame",
                                         "End Frame",
                                         "Length (sec)"])

                        # Write each event
                        for event in events:
                            writer.writerow(event)

                    print("Output written to '" + save_file + "'.")

                # Can't write to file
                except IOError:
                    print("Unable to write file '" + save_file + "'")

            else:
                print()

            # Declare if any bad frames were skipped
            if bad_frames > 0:
                print("Warning: skipped", bad_frames, "frames (" +
                      str(round((bad_frames / frame_count) * 100, 2)) +
                      "%) due to invalid hand or station markers.")

    # If the file does not exist
    except FileNotFoundError:
        print("Couldn't find matching file for '" + sys.argv[1] + "'")
