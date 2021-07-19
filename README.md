# MorphCT-flow

MorphCT-flow is a lightweight dataspace manager that leverages the [Signac](https://docs.signac.io/en/latest/) framework to submit Kinetic Monte Carlo simulations of charge transport in organic photovoltaics using [MorphCT](https://github.com/cmelab/morphct). MorphCT-flow works with [Singularity](https://sylabs.io/guides/latest/user-guide/) and is designed for use on supercomputing clusters.

### Install

MorphCT-flow uses the [conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) package manager. Before using MorphCT-flow, please install Miniconda.

1. First download MorphCT-flow:

    ```bash
    git clone git@github.com:cmelab/morphct-flow.git
    cd morphct-flow
    ```

2. Then install its requirements:

    ```bash
    conda env create -f environment.yml
    conda activate morphct-flow
    ```

    MorphCT-flow is not a python package, so it does not need to be installed.

3. In order to use MorphCT-flow, the MorphCT container must be pulled to your machine and its location assigned the environment variable `$MORPHCT_SIMG`. 
    
    The following example shows the container pulled to a directory called `~/images`:

    ```bash
    cd ~/images
    singularity pull docker://cmelab/morphct:latest
    export MORPHCT_SIMG=$(pwd)/morphct_latest.sif
    ```

    Or you can run this command (while still in the directory where you pulled the image) to add the image location to your bashrc file so you never have to run this step again

    ```bash
    echo "export MORPHCT_SIMG=$(pwd)/morphct_latest.sif" >> ~/.bashrc
    ```

And that's it--you are ready to run simulations!

### Run
<details>
    <summary>Pre-run steps (Click to expand):</summary>

(These commands can be added to your .bashrc to save time.)
1. Make sure singularity is available,
    
    Fry:
    ```bash
    module load singularity
    ```
    Bridges2: singularity is loaded by default
        
2. CUDA libraries are on your path,

    Fry:
    ```bash
    module load cuda
    ```
    Bridges2:
    ```bash
    module load cuda/10
    ```
3. The conda environment is active, 
    ```bash
    conda activate morphct-flow
    ```
4. And the `MORPHCT_SIMG` variable is set, 

</details>

The basic workflow is something like this:

1. Edit the init file to define state point space

    ```bash
    vim src/init.py
    ```
    
2. Run the init script to create a workspace

    ```bash
    python src/init.py
    ```
    
3. Check to make sure your jobs look correct

    ```bash
    python src/project.py submit --pretend 
    ```

4. Submit the project script to run your simulations

    ```bash
    python src/project.py submit
    ```
    
    `src/project.py` contains all of the job operations.

## Cluster support

Beyond the officially supported [flow environments](https://docs.signac.io/projects/flow/en/latest/supported_environments.html#supported-environments) we support:

* Fry
* Kestrel

