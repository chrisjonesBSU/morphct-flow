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


@on_container
@directives(ngpu=1)
@MyProject.operation
def run_charge_transport(job):
    pass

if __name__ == "__main__":
    MyProject().main()
