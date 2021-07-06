#!/usr/bin/env python
"""Initialize the project's data space.

Iterates over all defined state points and initializes
the associated job workspace directories."""
from itertools import product

import signac


project_name = "my_project"

# Parameters used for generating the morphology
parameters = {
    # input can be the path to a molecule file or a SMILES string
    # or a key to the COMPOUND dictionary in PlanckTon (shown below)
    # The compounds ending with "-gaff" are designed to be used with the
    # "gaff-custom" forcefield; if using a smiles string, use just "gaff".
    # Mixtures can be specified like so
    # "input" = [["PCBM-gaff", "P3HT-16-gaff"]]
    # note the additional brackets
    "input": [
        "path/to/input"
        ],

    # Temperatures specified in Kelvin
    "temperature": [300],,
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
