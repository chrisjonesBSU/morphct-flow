#!/usr/bin/env python
"""Initialize the project's data space.

Iterates over all defined state points and initializes
the associated job workspace directories."""
from itertools import product

import signac


project_name = "morphct"

# Parameters used for generating the morphology
parameters = {
    # input structure (path to a gsd file)
    "input": ["itic-trajectory.gsd"],

    "mol_length": [186],

    # chromophore specification
    "acceptors": ["itic_all_ids.csv"],
    "donors": [None],

    "acceptor_charge": [0],
    "donor_charge": [0],

    # frame index
    "frame": [-1],

    # scale needed to convert lengths to Angstrom
    # (from planckton use the ref_distance in job doc)
    "scale": [3.5636],

    "forcefield": ["gaff"],

    "reorganization_energy": [0.15],

    # Temperatures specified in Kelvin
    "temperature": [300],

    "lifetimes": [[1e-13,1e-12]],

    "n_holes": [0],
    "n_elec": [10],
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
