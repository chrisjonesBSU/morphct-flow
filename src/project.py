"""Define the project's workflow logic and operation functions.

Execute this script directly from the command line, to view your project's
status, execute operations and submit them to a cluster. See also:

    $ python src/project.py --help
"""
import flow
from flow import FlowProject, directives
from flow.environment import DefaultSlurmEnvironment
from flow.environments.xsede import Bridges2Environment
import os


class MyProject(FlowProject):
    pass


class Bridges2Custom(Bridges2Environment):
    template = "bridges2custom.sh"

    @classmethod
    def add_args(cls, parser):
        super(Bridges2Environment, cls).add_args(parser)
        parser.add_argument(
            "--partition",
            default="GPU-shared",
            help="Specify the partition to submit to.",
        )


class Fry(DefaultSlurmEnvironment):
    hostname_pattern = "fry.boisestate.edu"
    template = "fry.sh"

    @classmethod
    def add_args(cls, parser):
        parser.add_argument(
            "--partition",
            default="batch",
            help="Specify the partition to submit to."
        )
        parser.add_argument(
            "--nodelist",
            help="Specify the node to submit to."
        )


class R2(DefaultSlurmEnvironment):
    hostname_pattern = "r2"
    template = "r2.sh"

    @classmethod
    def add_args(cls, parser):
        parser.add_argument(
            "--partition",
            default="defq",
            help="Specify the partition to submit to."
        )


def get_paths(path, job):
    if path is None:
        raise FileNotFoundError
    # job.ws will be the path to the job e.g.,
    # path/to/morphct-flow/workspace/jobid
    # this is the root dir e.g.,
    # path/to/morphct-flow
    file_path = os.path.abspath(os.path.join(job.ws, "..", "..", path))
    if os.path.isfile(path):
        return path
    elif os.path.isfile(file_path):
        return file_path
    raise FileNotFoundError(
        "Please provide either a path to a file (the absolute path or the "
        "relative path in the morphct-flow root directory)."
        f"You provided: {path}"
    )


# Definition of project-related labels (classification)
def on_morphct(func):
    return flow.directives(
        executable='singularity exec --nv $MORPHCT_SIMG python'
    )(func)


@MyProject.label
def CT_calced(job):
    return job.isfile("output/kmc/results.csv")


@directives(N=1)
@directives(n=16)
@MyProject.operation
@MyProject.post(CT_calced)
def run_charge_transport(job):
    import numpy as np
    import polybinderCG.coarse_grain as cg
    from morphct.system import System
    print(f"Starting job {job.id}")

    if job.sp.forcefield == "gaff":
        from morphct.chromophores import amber_dict
        conversion_dict = amber_dict
    elif job.sp.forcefield == "opls":
        from morphct.chromophores import opls_dict
        conversion_dict = opls_dict
    else:
        raise NotImplementedError(
            f"Conversion dictionary for {job.sp.forcefield} does not exist."
        )

    gsdfile = get_paths(job.sp.input, job)
    print("GSD path found.")

    system = System(
        gsdfile,
        os.path.join(job.ws,"output"),
        frame=job.sp.frame,
        scale=job.sp.scale,
        conversion_dict=conversion_dict
    )
    print("System initialized.")

    chromo_ids = []
    cg_sys = cg.System(gsd_file=gsdfile, compound="PPS")
    for mon in cg_sys.monomers():
        mon.generate_components(index_mapping="ring_plus_linkage_AA")
    for component in cg_sys.components():
        chromo_ids.append(component.atom_indices)

    system.add_chromophores(chromo_ids, job.sp.carrier_type)
    print("Chromophores added.")

    system.compute_energies()
    print("Energies calculated")
    system.set_energies()
    print("Energies set")

    print("Starting KMC run")
    system.run_kmc(
        job.sp.lifetimes,
        job.sp.temperature,
        n_holes=job.sp.n_holes,
        n_elec=job.sp.n_elec,
        verbose=1
    )
    print("Finished KMC run")


if __name__ == "__main__":
    MyProject().main()
