"""
This file is part of the openPMD-viewer.

It defines a set of helper data and functions which
are used by the other files.

Copyright 2015-2018, openPMD-viewer contributors
Authors: Remi Lehe
License: 3-Clause-BSD-LBNL
"""
import os
import numpy as np
import yt


def open_file( filename ):
    """
    TODO
    """
    return yt.load( filename ) 


def close_file( file_handle ):
    """
    TODO
    """
    pass # Not sure if a yt DataSet can be closed


def list_files(path_to_dir):
    """
    Return a list of the files in this directory,
    and a list of the corresponding iterations

    WARNING: For the moment, the yt reader does not read the iteration!

    Parameter
    ---------
    path_to_dir : string
        The path to the directory where the hdf5 files are.

    Returns
    -------
    A tuple with:
    - a list of strings which correspond to the absolute path of each file
    - an array of integers which correspond to the iteration of each file
    """
    # Find all the files in the provided directory
    all_files = os.listdir(path_to_dir)

    # Select all files
    filenames = []
    for filename in all_files:
        full_name = os.path.join(
            os.path.abspath(path_to_dir), filename)
        filenames.append( full_name )

    # Sort the list of tuples according to the iteration
    iterations = np.arange( len(filenames), dtype='int64' )

    return(filenames, iterations)
