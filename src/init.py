#!/usr/bin/env python
"""Initialize the project's data space.

Iterates over all defined state points and initializes
the associated job workspace directories."""
from itertools import product

import signac


project_name = "morphct"

# Parameters used for generating the morphology
parameters = {
    # Structure and chemistry
    #------------------------
    # Input structure (path to a gsd file)
    "input": ["pps-amorph-polydisperse.gsd"],

    # Pickle file
    "pickle": [None],

    # System name
    "name": ["pps-amorphous"],

    # Index of the frame in the input gsd trajectory to use
    "frame": [-1, -3, -5],

    # Chemistry-specific reorganization energy in eV
    "reorganization_energy": [
        #0.15  # ITIC
        #0.3064 # P3HT
        1.0
    ],

    # Charge carrier type
    "carrier_type": ["acceptor"],

    # If the pyscf calculation errors out due to electron spin, a charge
    # can be specified here to fix it.
    "acceptor_charge": [0],
    "donor_charge": [0],

    # scale needed to convert lengths to Angstrom
    "scale": [3.5636],

    "forcefield": ["opls"],

    # KMC Parameters
    #---------------
    # Temperatures specified in Kelvin
    "temperature": [300, 400, 500, 600],

    # Carrier lifetimes in seconds
    "lifetimes": [[1e-8, 5e-7, 1e-7, 5e-6]],

    # Number of holes (for donor) and/or electrons (for acceptor)
    "n_holes": [0],
    "n_elec": [25],
}


def get_parameters(parameters):
    return list(parameters.keys()), list(product(*parameters.values()))


def main(parameters):
    project = signac.init_project(project_name)
    param_names, param_combinations = get_parameters(parameters)
    # Create the generate jobs
    for params in param_combinations:
        parent_statepoint = dict(zip(param_names, params))
        parent_job = project.open_job(parent_statepoint)
        parent_job.init()
    project.write_statepoints()
    print(f"Initialized. ({len(param_combinations)} total jobs)")


if __name__ == "__main__":
    main(parameters)
