"""
This file is part of the openPMD-viewer.

It defines a function that can read standard parameters from an openPMD file.

Copyright 2015-2018, openPMD-viewer contributors
Authors: Remi Leh
License: 3-Clause-BSD-LBNL
"""
import os
import numpy as np
import yt

# Exclude typical derived types that are not actual fields, or are duplicates
excluded_field_keys = [ 'cell_volume', 'current_', 'dx', 'dy', 'dz',
    'x', 'y', 'z', 'Bx', 'By', 'Bz', 'Ex', 'Ey', 'Ez', 'Jx', 'Jy', 'Jz' ]
# The above are duplicates because they are also present as 'B_x', etc.
excluded_field_roots = [ 'current_', 'electric_', 'magnetic_',
    'path_element_', 'relative_magnetic_', 'vertex_' ]
excluded_particle_keys = [ 'particle_position', 'mesh_id',
    'particle_ones', 'particle_weight', 'particle_radius' ]
excluded_particle_roots = [
    'relative_particle_', 'particle_position_relative',
    'particle_positionCoarse_', 'particle_positionOffset_',
    'particle_spherical_position_', 'particle_position_spherical_',
    'particle_position_cylindrical', 'particle_velocity',
    'particle_cylindrical' ]

def read_openPMD_params(filename, extract_parameters=True):
    """
    Extract the time and some openPMD parameters from a file

    Parameter
    ---------
    filename: string
        The path to the file from which parameters should be extracted

    extract_parameters: bool, optional
        Whether to extract all parameters or only the time
        (Function execution is faster when extract_parameters is False)

    Returns
    -------
    A tuple with:
    - A float corresponding to the time of this iteration in SI units
    - A dictionary containing several parameters, such as the geometry, etc.
      When extract_parameters is False, the second argument returned is None.
    """
    # Open the file, and do a version check
    ds = yt.load( filename )

    # Extract the time
    t = ds.current_time.to_value()

    # If the user did not request more parameters, exit now.
    if not extract_parameters:
        return(t, None)

    # Otherwise, extract the rest of the parameters
    params = {}

    # Find out supported openPMD extensions claimed by this file
    # WARNING: For now, for the yt reader, we skip the extensions
    params['extensions'] = []

    # Find out whether fields are present and extract their metadata
    avail_fields = [ key[1] for key in ds.derived_field_list \
                    if key[0] == 'mesh']
    if len(avail_fields) > 0:
        params['avail_fields'] = []
        params['fields_metadata'] = {}

        # Loop through the available fields
        for key in avail_fields:

            # Filter out all the excluded fields
            if key in excluded_field_keys or \
                any( key.startswith(root) for root in excluded_field_roots ):
                # Skip to the next key
                continue

            # Detect vector fields
            if any( key.endswith(root) for root in ['_x', '_y', '_z']):
                field_name = key[:-2]
                if field_name in params['avail_fields']:
                    continue  # Already registered; skip to next key
                is_scalar_record = False
            else:
                field_name = key
                is_scalar_record = True

            # Create metadata object
            metadata = {}
            metadata['geometry'] = "{:d}dcartesian".format(ds.dimensionality)
            metadata['avail_circ_modes'] = []
            metadata['axis_labels'] = [ 'x', 'y', 'z' ] # Standard in yt
            # Check whether the field is a vector or a scalar
            if is_scalar_record:
                metadata['type'] = 'scalar'
            else:
                metadata['type'] = 'vector'

            params['avail_fields'].append( field_name )
            params['fields_metadata'][field_name] = metadata
    else:
        params['avail_fields'] = None

    # Find out whether particles are present, and if yes of which species
    avail_species = [ key for key in ds.particle_types if key != 'all' ]
    if len(avail_species) > 0:
        # Particles are present ; extract the species
        params['avail_species'] = avail_species
        # dictionary with list of record components for each species
        record_components = {}
        # Go through all species
        for species_name in avail_species:
            record_components[species_name] = []

        # Go through all the available records
        for key in ds.derived_field_list:
            if not key[0] in avail_species:
                continue
            else:
                species_name = key[0]
                quantity = key[1]

            # Filter out all the excluded particle quantities
            if quantity in excluded_particle_keys or any( \
                quantity.startswith(root) for root in excluded_particle_roots):
                # Skip to the next key
                continue

            # Register the quantity name, without the preceding `particle_`
            record_components[species_name].append(quantity[len('particle_'):])

        # Simplify the name of some standard openPMD records
        for species_name in avail_species:
            record_components[species_name] = \
                simplify_record(record_components[species_name])
        params['avail_record_components'] = record_components
        # deprecated
        first_species_name = next(iter(params['avail_species']))
        params['avail_ptcl_quantities'] = \
            record_components[first_species_name]
    else:
        # Particles are absent
        params['avail_species'] = None
        params['avail_record_components'] = None
        # deprecated
        params['avail_ptcl_quantities'] = None

    return(t, params)


def simplify_record(record_comps):
    """
    Replace the names of some standard record by shorter names

    Parameter
    ---------
    record_comps: a list of strings
        A list of available particle record components

    Returns
    -------
    A list with shorter names, where applicable
    """
    # Replace the names of the positions
    if 'position_x' in record_comps:
        record_comps.remove('position_x')
        record_comps.append('x')
    if 'position_y' in record_comps:
        record_comps.remove('position_y')
        record_comps.append('y')
    if 'position_z' in record_comps:
        record_comps.remove('position_z')
        record_comps.append('z')

    # Replace the names of the momenta
    if 'momentum_x' in record_comps:
        record_comps.remove('momentum_x')
        record_comps.append('ux')
    if 'momentum_y' in record_comps:
        record_comps.remove('momentum_y')
        record_comps.append('uy')
    if 'momentum_z' in record_comps:
        record_comps.remove('momentum_z')
        record_comps.append('uz')

    # Replace the name for 'weights'
    if 'weighting' in record_comps:
        record_comps.remove('weighting')
        record_comps.append('w')

    return(record_comps)
