"""
This file is part of the openPMD-viewer.

It defines a function that reads a species record component (data & meta)
from an openPMD file

Copyright 2015-2016, openPMD-viewer contributors
Authors: Remi Lehe, Axel Huebl
License: 3-Clause-BSD-LBNL
"""


def read_species_data(ds, species, record_comp, extensions):
    """
    Extract a given species' record_comp

    Parameters
    ----------
    ds: a yt.Dataset object
        The dataset from which to extract data

    species: string
        The name of the species to extract (in the openPMD file)

    record_comp: string
        The record component to extract
        Either 'x', 'y', 'z', 'ux', 'uy', 'uz', or 'w'

    extensions: list of strings
        The extensions that the current OpenPMDTimeSeries complies with
    """
    # Translate the record component to the openPMD format
    dict_record_comp = {'x': 'position_x',
                        'y': 'position_y',
                        'z': 'position_z',
                        'ux': 'momentum_x',
                        'uy': 'momentum_y',
                        'uz': 'momentum_z',
                        'w': 'weighting'}
    if record_comp in dict_record_comp:
        opmd_record_comp = dict_record_comp[record_comp]
    else:
        opmd_record_comp = record_comp
    opmd_record_comp = 'particle_' + opmd_record_comp

    # Extract the right dataset
    ad = ds.all_data()
    data = ad[ (species, opmd_record_comp) ].to_ndarray()

    # - Return momentum in normalized units
#    elif record_comp in ['ux', 'uy', 'uz' ]:
#        m = get_data(species_grp['mass'])
#        # Normalize only if the particle mass is non-zero
#        if np.all( m != 0 ):
#            norm_factor = 1. / (m * constants.c)
#            data *= norm_factor

    # Return the data
    return(data)
