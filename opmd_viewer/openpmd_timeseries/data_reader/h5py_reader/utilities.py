"""
This file is part of the openPMD-viewer.

It defines a set of helper data and functions which
are used by the other files.

Copyright 2015-2016, openPMD-viewer contributors
Authors: Remi Lehe, Axel Huebl
License: 3-Clause-BSD-LBNL
"""
import os
import h5py
import numpy as np


def open_file( filename ):
    """
    TODO
    """
    return h5py.File( filename, 'r' )


def close_file( file_handle ):
    """
    TODO
    """
    file_handle.close()


def list_files(path_to_dir):
    """
    Return a list of the hdf5 files in this directory,
    and a list of the corresponding iterations

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

    # Select the hdf5 files
    iters_and_names = []
    for filename in all_files:
        # Use only the name that end with .h5 or .hdf5
        if filename.endswith('.h5') or filename.endswith('.hdf5'):
            full_name = os.path.join(
                os.path.abspath(path_to_dir), filename)
            # extract all iterations from hdf5 file
            f = h5py.File(full_name, 'r')
            iterations = list(f['/data'].keys())
            f.close()
            # for each found iteration create list of tuples
            # (which can be sorted together)
            for key_iteration in iterations:
                iters_and_names.append((int(key_iteration), full_name))

    # Sort the list of tuples according to the iteration
    iters_and_names.sort()
    # Extract the list of filenames and iterations
    filenames = [name for (it, name) in iters_and_names]
    iterations = np.array([it for (it, name) in iters_and_names])

    return(filenames, iterations)


def get_bpath(f):
    """
    Return a string that corresponds to the base path of the data.

    NB: For openPMD 1.0.0, the basePath is always of the form
    '/data/%T' where %T is replaced by the actual iteration which
    is present in the file.

    Parameters:
    -----------
    f: am h5py.File object
    """
    iteration = list(f['/data'].keys())[0]
    return('/data/%s' % iteration)


def is_scalar_record(record):
    """
    Determine whether a record is a scalar record or a vector record

    Parameter
    ---------
    record: an h5py Dataset or an h5py Group

    Return
    ------
    A boolean indicating whether the record is scalar
    """
    scalar = False
    if 'value' in record.attrs:
        scalar = True
    elif isinstance(record, h5py.Dataset):
        scalar = True

    return(scalar)


def get_data(dset, i_slice=None, pos_slice=None, output_type=np.float64):
    """
    Extract the data from a (possibly constant) dataset
    Slice the data according to the parameters i_slice and pos_slice

    Parameters:
    -----------
    dset: an h5py.Dataset or h5py.Group (when constant)
        The object from which the data is extracted

    pos_slice: int or list of int, optional
        Slice direction(s).
        When None, no slicing is performed

    i_slice: int or list of int, optional
       Indices of slices to be taken.

    output_type: a numpy type
       The type to which the returned array should be converted

    Returns:
    --------
    An np.ndarray (non-constant dataset) or a single double (constant dataset)
    """
    # For back-compatibility: Convert pos_slice and i_slice to
    # single-element lists if they are not lists (e.g. float
    # and int respectively).
    if pos_slice is not None and not isinstance(pos_slice, list):
        pos_slice = [pos_slice]
    if i_slice is not None and not isinstance(i_slice, list):
        i_slice = [i_slice]
    # Case of a constant dataset
    if isinstance(dset, h5py.Group):
        shape = dset.attrs['shape']
        # Restrict the shape if slicing is enabled
        if pos_slice is not None:
            shape = [ x for index, x in enumerate(shape) if
                      index not in pos_slice ]
        # Create the corresponding dataset
        data = dset.attrs['value'] * np.ones(shape)

    # Case of a non-constant dataset
    elif isinstance(dset, h5py.Dataset):
        if pos_slice is None:
            data = dset[...]
        else:
            # Get largest element of pos_slice
            max_pos = max(pos_slice)
            # Create list of indices list_index of type
            # [:, :, :, ...] where Ellipsis starts at max_pos + 1
            list_index = [np.s_[:]] * (max_pos + 2)
            list_index[max_pos + 1] = np.s_[...]
            # Fill list_index with elements of i_slice
            for count, dir_index in enumerate(pos_slice):
                list_index[dir_index] = i_slice[count]
            # Convert list_index into a tuple
            tuple_index = tuple(list_index)
            # Slice dset according to tuple_index
            data = dset[tuple_index]

    # Convert to the right type
    if data.dtype != output_type:
        data = data.astype( output_type )
    # Scale by the conversion factor
    if output_type in [ np.float64, np.float32, np.float16 ]:
        if dset.attrs['unitSI'] != 1.0:
            data *= dset.attrs['unitSI']

    return(data)


def get_shape(dset):
    """
    Extract the shape of a (possibly constant) dataset

    Parameters:
    -----------
    dset: an h5py.Dataset or h5py.Group (when constant)
        The object whose shape is extracted

    Returns:
    --------
    A tuple corresponding to the shape
    """
    # Case of a constant dataset
    if isinstance(dset, h5py.Group):
        shape = dset.attrs['shape']
    # Case of a non-constant dataset
    elif isinstance(dset, h5py.Dataset):
        shape = dset.shape

    return(shape)


def join_infile_path(*paths):
    """
    Join path components using '/' as separator.
    This method is defined as an alternative to os.path.join, which uses '\\'
    as separator in Windows environments and is therefore not valid to navigate
    within data files.

    Parameters:
    -----------
    *paths: all strings with path components to join

    Returns:
    --------
    A string with the complete path using '/' as separator.
    """
    # Join path components
    path = '/'.join(paths)
    # Correct double slashes, if any is present
    path = path.replace('//', '/')

    return path
