"""Define the project's workflow logic and operation functions.

Execute this script directly from the command line, to view your project's
status, execute operations and submit them to a cluster. See also:

    $ python src/project.py --help
"""
import flow
from flow import FlowProject, directives
from flow.environment import DefaultSlurmEnvironment
from flow.environments.xsede import Bridges2Environment
from os import path


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


# Definition of project-related labels (classification)
def on_container(func):
    return flow.directives(
        executable='singularity exec --nv $MORPHCT_SIMG python'
    )(func)


#@on_container
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

    system = System(
        gsdfile,
        "output",
        frame=job.sp.frame,
        scale=job.sp.scale,
        conversion_dict=conversion_dict
    )

    n_mols = system.snap.particles.N // job.sp.mol_length
    mol_length = job.sp.mol_length

    try:
        a_inds = np.loadtxt(job.sp.acceptors, dtype=int)
        if len(a_inds.shape) > 1:
            acc_inds = [
                item for sublist in
                [[x + i * mol_length for x in a_inds] for i in range(n_mols)]
                for item in sublist
            ]
        else:
            acc_inds = [a_inds + i * mol_length for i in range(n_mols)]
    except ValueError:
        # no acceptors
        pass

    try:
        d_inds = np.loadtxt(job.sp.donors, dtype=int)
        if len(d_inds.shape) > 1:
            don_inds = [
                item for sublist in
                [[x + i * mol_length for x in d_inds] for i in range(n_mols)]
                for item in sublist
            ]
        else:
            don_inds = [d_inds + i * mol_length for i in range(n_mols)]

    except ValueError:
        # no donors
        pass

if __name__ == "__main__":
    MyProject().main()
