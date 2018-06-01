"""
This file is part of the openPMD-viewer.

It defines functions that can read the fields from an HDF5 file.

Copyright 2015-2016, openPMD-viewer contributors
Author: Remi Lehe
License: 3-Clause-BSD-LBNL
"""

def get_grid_parameters( ds, avail_fields, metadata ):
    """
    Return the parameters of the spatial grid (grid size and grid range)
    in two dictionaries

    Parameters:
    -----------
    ds: a yt Dataset object
       The file from which to extract the information

    avail_fields: list
       A list of the available fields
       e.g. ['B', 'E', 'rho']

    metadata: dictionary
      A dictionary whose keys are the fields of `avail_fields` and
      whose values are dictionaries that contain metadata (e.g. geometry)

    Returns:
    --------
    A tuple with `grid_size_dict` and `grid_range_dict`
    Both objects are dictionaries, with their keys being the labels of the axis
    of the grid (e.g. 'x', 'y', 'z')
    The values of `grid_size_dict` are the number of gridpoints along each axis
    The values of `grid_range_dict` are lists of two floats, which correspond
    to the min and max of the grid, along each axis.
    """
    # Pick the first field
    field_name = avail_fields[ 0 ]

    # Extract relevant quantities
    labels = metadata[field_name]['axis_labels']
    grid_spacing = ds.domain_width.to_ndarray()/ds.domain_dimensions
    grid_offset = ds.domain_left_edge.to_ndarray()
    grid_size = ds.domain_dimensions

    # Build the dictionaries grid_size_dict and grid_range_dict
    grid_size_dict = {}
    grid_range_dict = {}
    for i in range(len(labels)):
        coord = labels[i]
        grid_size_dict[coord] = grid_size[i]
        grid_range_dict[coord] = \
            [ grid_offset[i], grid_offset[i] + grid_size[i] * grid_spacing[i] ]

    return( grid_size_dict, grid_range_dict )
