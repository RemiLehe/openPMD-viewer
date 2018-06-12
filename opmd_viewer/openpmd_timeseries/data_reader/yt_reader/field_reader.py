"""
This file is part of the openPMD-viewer.

It defines functions that can read the fields from an openPMD file.

Copyright 2015-2016, openPMD-viewer contributors
Author: Remi Lehe
License: 3-Clause-BSD-LBNL
"""
import numpy as np
import yt
from opmd_viewer.openpmd_timeseries.field_metainfo import FieldMetaInformation


def read_field_cartesian( filename, field, coord, axis_labels,
                          slicing, slicing_dir ):
    """
    Extract a given field from an openPMD file,
    when the geometry is cartesian (1d, 2d or 3d).

    Parameters
    ----------
    filename : string
       The absolute path to the openPMD file

    field : string, optional
       Which field to extract

    coord : string, optional
       Which component of the field to extract

    axis_labels: list of strings
       The name of the dimensions of the array (e.g. ['x', 'y', 'z'])

    slicing : list of float or None
       Number(s) between -1 and 1 that indicate where to slice the data,
       along the directions in `slicing_dir`
       -1 : lower edge of the simulation box
       0 : middle of the simulation box
       1 : upper edge of the simulation box

    slicing_dir : list of str or None
       Direction(s) along which to slice the data
       Elements can be:
         - 1d: 'z'
         - 2d: 'x' and/or 'z'
         - 3d: 'x' and/or 'y' and/or 'z'
       Returned array is reduced by 1 dimension per slicing.

    Returns
    -------
    A tuple with
       F : a ndarray containing the required field
       info : a FieldMetaInformation object
       (contains information about the grid; see the corresponding docstring)
    """
    # Open the file
    ds = yt.load(filename)

    # Extract the full array of the fields
    ad0 = ds.covering_grid(level=0, left_edge=ds.domain_left_edge,
                           dims=ds.domain_dimensions)
    if coord is None:
        field_yt = 'field'
    else:
        field_yt = field + '_' + coord
    F = ad0[field_yt].to_ndarray()

    # Dimensions of the grid
    shape = list( ds.domain_dimensions.astype('int') )
    grid_spacing = list( ds.domain_width.to_ndarray() / ds.domain_dimensions )
    global_offset = list( ds.domain_left_edge.to_ndarray() )
    grid_unit_si = 1.
    grid_position = [0.] * ds.dimensionality

    # Slice selection
    if slicing_dir is not None:
        # Get the integer that correspond to the slicing direction
        list_slicing_index = []
        for count, slicing_dir_item in enumerate(slicing_dir):
            slicing_index = axis_labels.index(slicing_dir_item)
            list_slicing_index.append(slicing_index)
            # Number of cells along the slicing direction
            n_cells = shape[ slicing_index ]
            # Index of the slice (prevent stepping out of the array)
            i_cell = int( 0.5 * (slicing[count] + 1.) * n_cells )
            i_cell = max( i_cell, 0 )
            i_cell = min( i_cell, n_cells - 1)
            F = np.take( F, [i_cell], axis=slicing_index )
        F = np.squeeze( F )

        # Remove metainformation relative to the slicing index
        shape = [ x for index, x in enumerate(shape)
                  if index not in list_slicing_index ]
        grid_spacing = [ x for index, x in enumerate(grid_spacing)
                         if index not in list_slicing_index ]
        global_offset = [ x for index, x in enumerate(global_offset)
                          if index not in list_slicing_index ]
        axis_labels = [ x for index, x in enumerate(axis_labels)
                         if index not in list_slicing_index ]
        grid_position = [ x for index, x in enumerate(grid_position)
                         if index not in list_slicing_index ]

    # Create the meta information object
    axes = { i: axis_labels[i] for i in range(len(axis_labels)) }
    info = FieldMetaInformation( axes, shape, grid_spacing,
        global_offset, grid_unit_si, grid_position )

    return( F, info )


def read_field_circ( filename, field, coord, slicing, slicing_dir, m=0,
                     theta=0. ):
    """
    Extract field for cylindrical geometry
    Not implemented for the yt backend
    """
    raise NotImplementedError(
        "The `yt` backend is unable to read cylindrical data.")


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
    grid_spacing = ds.domain_width.to_ndarray() / ds.domain_dimensions
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
