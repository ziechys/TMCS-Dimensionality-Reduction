#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pre-processing of xyz files into
a object wrapping a 3N x M 
numpy array.
"""

import numpy as np
from collections import defaultdict
import rmsd


def cast_positive_int(in_string: str) -> int:
    """
    Checks that a string is a valid
    positive integer
    :param in_string:
    :type in_string: object
    :return:
    """
    try:
        int(in_string)
    except ValueError:
        raise ValueError(f"Cannot turn {in_string} into an integer")
    if int(in_string) != float(in_string):
        raise ValueError(f"{in_string} is floating point number, not an int")

    out_int = int(in_string)
    if out_int == 0:
        raise ValueError(f"This integer cannot be zero.")

    if out_int < 0:
        raise ValueError(f"This integer cannot be negative.")

    return out_int


class XYZFile:
    """
    Class for an xyz file that
    creates a trajectory.
    """
    def __init__(self, filename):
        self.filename = filename
        self.num_atoms = 0  # Set this in "parse_xyz_file"
        self.num_frames = 0
        self.atom_labels = None
        self.frames = self.parse_xyz_file(filename)

    def __str__(self):
        return f"{self.filename}, with {self.num_atoms} atoms in {self.num_frames} frames"

    def parse_atom_labels(self, lines: list) -> list:
        """
        Parses a simple frame into a
        3N array of which atomic is in which
        position.
        :param lines:
        :return:
        """
        seen_atoms = defaultdict(lambda: 0)
        atom_labels = []
        for line in lines:
            atom = line.split()[0]
            atom = f"{atom}{seen_atoms[atom]}"
            atom_labels.extend([f"{atom}_x", f"{atom}_y", f"{atom}_z"])
            seen_atoms[atom] += 1
        assert len(atom_labels) == self.num_atoms * 3, "Did not find 3N atomic labels."
        return atom_labels

    @staticmethod
    def parse_one_frame(lines: list):
        """
        Parses a simple frame into
        a 3xN vector.
        :param lines:
        :return:
        """
        frame = []
        for line in lines:
            elements = line.split()[1:]
            elements = np.asfarray(elements, float)
            frame.extend(elements)
        frame=np.array(frame).reshape(-1,3)

        # shift coordinates
        frame = frame - rmsd.centroid(frame)
        return frame.ravel()

    def parse_xyz_file(self, filename: str):
        """
        Loads in an .xyz file into
        a set of 3N atom coordinates x M steps.
        :param filename:
        :return:
        """

        assert filename.endswith(".xyz"), "File must be in .xyz format."
        xyz_header_lines = 2
        with open(filename, "r") as infile:
            lines = infile.readlines()
            self.num_atoms = cast_positive_int(lines[0])

            self.num_frames = cast_positive_int(len(lines) / (self.num_atoms + xyz_header_lines))

            frames = np.empty([self.num_frames, self.num_atoms * 3])
            self.atom_labels = self.parse_atom_labels(lines[xyz_header_lines: xyz_header_lines + self.num_atoms])
            for i in range(self.num_frames):
                start_index = i * (self.num_atoms + xyz_header_lines) + xyz_header_lines
                end_index = (i + 1) * (self.num_atoms + xyz_header_lines)

                frame_num_atoms_index = start_index - 2
                frame_num_atoms = cast_positive_int(lines[frame_num_atoms_index])
                assert frame_num_atoms == self.num_atoms, f"""
                                                           num_atoms at line {frame_num_atoms_index }inconsistent.
                                                           Got {frame_num_atoms}, expected {self.num_atoms}.
                                                           """

                frame_lines = lines[start_index: end_index]
                frame = self.parse_one_frame(frame_lines)
                frames[i, :] = frame
                assert len(frame_lines) == self.num_atoms

        return frames

    def writeOutXYYZ(self, fileName):
        #print(self.frames)


        fileOut = open(fileName,'w+')

        for frame in self.frames:

            fileOut.write(str(self.num_atoms)+'\n')
            fileOut.write('Shifted XYZ'+'\n')

            for index in range(len(frame)//3):
                x = frame[3 * index]
                y = frame[3 * index + 1]
                z = frame[3 * index + 2]
                fileOut.write(str(self.atom_labels[index])+'\t'+str(x)+'\t'+str(y)+'\t'+str(z)+'\n')





if __name__ == "__main__":
    input_file = XYZFile("./Resources/malonaldehyde_IRC.xyz")
    input_file.writeOutXYYZ("./Resources/malonaldehyde_IRC_Shifted.xyz")
