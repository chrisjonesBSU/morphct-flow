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


class Kestrel(DefaultSlurmEnvironment):
    hostname_pattern = "kestrel"
    template = "kestrel.sh"

    @classmethod
    def add_args(cls, parser):
        parser.add_argument(
            "--partition",
            default="batch",
            help="Specify the partition to submit to."
        )


def get_paths(path, job):
    # job.ws will be the path to the job e.g.,
    # path/to/morphct-flow/workspace/jobid
    # this is the root dir e.g.,
    # path/to/morphct-flow
    file_path = os.path.abspath(path.join(job.ws, "..", "..", path))
    if path.isfile(path):
        return path
    elif path.isfile(file_path):
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


@on_morphct
@directives(ngpu=1)
@MyProject.operation
def run_charge_transport(job):
    import numpy as np

    from morphct.system import System

    if job.sp.forcefield == "gaff":
        from morphct.chromophores import amber_dict
        conversion_dict = amber_dict
    else:
        raise NotImplementedError(
            f"Conversion dictionary for {job.sp.forcefield} does not exist."
        )

    gsdfile = get_paths(job.sp.input, job)

    system = System(
        gsdfile,
        os.path.join(job.ws,"output"),
        frame=job.sp.frame,
        scale=job.sp.scale,
        conversion_dict=conversion_dict
    )

    n_mols = system.snap.particles.N // job.sp.mol_length
    mol_length = job.sp.mol_length

    try:
        a_file = get_paths(job.sp.acceptors, job)
        a_inds = np.loadtxt(a_file, dtype=int)
        if len(a_inds.shape) > 1:
            acc_inds = [
                item for sublist in
                [[x + i * mol_length for x in a_inds] for i in range(n_mols)]
                for item in sublist
            ]
        else:
            acc_inds = [a_inds + i * mol_length for i in range(n_mols)]

        system.add_chromophores(
            acc_inds,
            "acceptor",
            chromophore_kwargs={
                "reorganization_energy": job.sp.reorganization_energy,
                "charge": job.sp.acceptor_charge,
                }
        )

    except FileNotFoundError:
        # no acceptors
        pass

    try:
        d_file = get_paths(job.sp.donors, job)
        d_inds = np.loadtxt(d_file, dtype=int)
        if len(d_inds.shape) > 1:
            don_inds = [
                item for sublist in
                [[x + i * mol_length for x in d_inds] for i in range(n_mols)]
                for item in sublist
            ]
        else:
            don_inds = [d_inds + i * mol_length for i in range(n_mols)]

        system.add_chromophores(
            don_inds,
            "donor",
            chromophore_kwargs={
                "reorganization_energy": job.sp.reorganization_energy,
                "charge": job.sp.donor_charge,
                }
        )

    except FileNotFoundError:
        # no donors
        pass

    system.compute_energies()
    system.set_energies()

    system.run_kmc(
        job.sp.lifetimes,
        job.sp.temperature,
        n_holes=job.sp.n_holes,
        n_elec=job.sp.n_elec,
        verbose=1
    )

if __name__ == "__main__":
    MyProject().main()
