# EMEWS Creator

EMEWS Creator is a python package for creating workflow projects for the Extreme-scale Model Exploration with Swift (EMEWS). The EMEWS framework enables the direct integration of multi-language model exploration (ME) algorithms
while scaling dynamic computational experiments to very large numbers (millions) of models on all major
HPC platforms. EMEWS has been designed for any "black box" application code, such as agent-based and 
microsimulation models or training of machine learning models, that require multiple runs as part of
heuristic model explorations. One of the main goals of EMEWS is to democratize the use of large-scale
computing resources by making them accessible to more researchers in many more science domains.
EMEWS is built on the Swift/T parallel scripting language.

See the [EMEWS Site](https://emews.github.io/index.html) for more information.

## Installation

EMEWS Creator can be downloaded and installed from PyPI using pip.

```
pip install emewscreator
```

## Using EMEWS Creator

The following provides an overview of how to use EMEWSCreator to create
project workflows. For a more comprehensive explanation see the
[EMEWS Tutorial](https://www.mcs.anl.gov/~emews/tutorial/).

EMEWSCreator is run from the command line.

```
$ python -m emewscreator -h
Usage: emewscreator [OPTIONS] TEMPLATE

Options:
  -V, --version          Show the version and exit.
  -o, --output-dir PATH  Directory into which the project template will be
                         generated.

  -c, --config PATH      Path to the template configuration file. Option is
                         mutually exclusive with emews.  [required]

  -h, --help             Show this message and exit.
  ```

where TEMPLATE is one of the three workflow types: `sweep`, `eqpy`, or `eqr`. Each
workflow template requires a user provided configuration file that is used to
create the various files and directories that make up the workflow. Sample
configuration files can be found [here](https://github.com/emews/emews-project-creator/tree/master/example_cfgs)
in the `example_cfgs` directory in the EMEWS Creator github repository.

### Sweep ###

The sweep template creates a sweep workflow in which EMEWS reads an input file,
and runs an application (e.g., a simulation model) using each line of the input file
as input to an application run.

Usage:
```
$ python -m emewscreator sweep -o SampleModel -c sweep_config.yaml
```

The configuration file has the following entries:

* `emews_root_directory` - the directory in which the workflow directories and files will be placed. If
this doesn't exist, it will be created. 
* `workflow_name` - the name of the workflow. This will be used as the file name for the workflow configuration, 
submission, and swift script files. Spaces will be replaced by underscores.
* `model_name` - the name of the model to run during the sweep. This will be used in the model execution
bash script. Spaces will be replaced by underscores.
* `upf` - the location of the unrolled parameter file (UPF) containing the collection of model 
input parameters (one run per line) to sweep over.

The configuration file can also contain entries for running the workflow on an HPC system
where a job is submitted via an HPC scheduler (e.g., the slurm scheduler).
See your HPC resource's documentation for details on how to set these. For non-HPC
runs these can be omitted.

* `walltime` - the estimated duration of the workflow job. The value must be surrounded by single quotes in order to parse correctly.
* `queue` - the queue to run the workflow job on
* `project` - the project to run the workflow job with
* `nodes` - the number of nodes to allocate to the workflow job
* `ppn` - the number of processes per node to allocate to the workflow job

A sample sweep configuration file can be found [here](https://github.com/emews/emews-project-creator/blob/master/example_cfgs/sweep.yaml).

For additional explanation of the sweep workflow, see the [EMEWS Tutorial](https://www.mcs.anl.gov/~emews/tutorial/)

### EQPy ###

The EQPy template creates a workflow that uses emews queues for Python (EQPy) to 
run an application (e.g., a simulation model) using input parameters provided by a
Python model exploration (ME) algorithm. The workflow will start the Python ME
which then iteratively provides json format input parameters for model
execution.

Usage:

```
$ python -m emewscreator eqpy -o SampleModel -c eqpy_config.yaml
```

The configuration file has the following entries:

* `emews_root_directory` - the directory in which the workflow directories and files will be placed. If
this doesn't exist, it will be created. 
* `workflow_name` - the name of the workflow. This will be used as the file name for the workflow configuration, 
submission, and swift script files. Spaces will be replaced by underscores.
* `model_name` - the name of the model to run during the sweep. This will be used in the model execution
bash script. Spaces will be replaced by underscores.
* `me_algo_cfg_file_name` - the path to a configuration file for the Python ME algorithm. This
path will be passed to the Python ME when it is initialized.
* `me_module` - the Python module implementing the ME algorithm.
* `trials` - the number of trials or replicates to perform for each model run.
* `model_output_file_name` - each model run is passed a file path for writing its output.
This is the name of that file.
* `model_output_file_ext` - the file extension (e.g., `csv`) of the `model_output_file_name`

The configuration file can also contain entries for running the workflow on an HPC system
where a job is submitted via an HPC scheduler (e.g., the slurm scheduler).
See your HPC resource's documentation for details on how to set these. For non-HPC
runs these can be omitted.

* `walltime` - the estimated duration of the workflow job. The value must be surrounded by single quotes in order to parse correctly.
* `queue` - the queue to run the workflow job on
* `project` - the project to run the workflow job with
* `nodes` - the number of nodes to allocate to the workflow job
* `ppn` - the number of processes per node to allocate to the workflow job

A sample EQPy configuration file can be found [here](https://github.com/emews/emews-project-creator/blob/master/example_cfgs/eqpy.yaml).

For additional explanation of EMEWS Queues and ME workflows, see the [EMEWS Tutorial](https://www.mcs.anl.gov/~emews/tutorial/)

### EQR ###

The EQR template creates a workflow that uses emews queues for R (EQR) to 
run an application (e.g., a simulation model) using input parameters provided by a
R model exploration (ME) algorithm. The workflow will start the R ME
which then iteratively provides json format input parameters for model
execution.

*Note*: The EQR extension requires an additional compilation step. Once the template has been run,
see `ext/EQ-R/src/README.md` for compliation instructions. 

Usage:

```
$ python -m emewscreator eqr -o SampleModel -c eqr_config.yaml
```

The configuration file has the following entries:

* `emews_root_directory` - the directory in which the workflow directories and files will be placed. If
this doesn't exist, it will be created. 
* `workflow_name` - the name of the workflow. This will be used as the file name for the workflow configuration, 
submission, and swift script files. Spaces will be replaced by underscores.
* `model_name` - the name of the model to run during the sweep. This will be used in the model execution
bash script. Spaces will be replaced by underscores.
* `me_algo_cfg_file_name` - the path to a configuration file for the R ME algorithm. This
path will be passed to the R ME when it is initialized.
* `me_scrpt` - the path to the R script implementing the ME algorithm.
* `trials` - the number of trials or replicates to perform for each model run.
* `model_output_file_name` - each model run is passed a file path for writing its output.
This is the name of that file.
* `model_output_file_ext` - the file extension (e.g., `csv`) of the `model_output_file_name`

The configuration file can also contain entries for running the workflow on an HPC system
where a job is submitted via a HPC scheduler (e.g., the slurm scheduler).
See your HPC resource's documentation for details on how to set these. For non-HPC
runs these can be omitted.

* `walltime` - the estimated duration of the workflow job. The value must be surrounded by single quotes in order to parse correctly.
* `queue` - the queue to run the workflow job on
* `project` - the project to run the workflow job with
* `nodes` - the number of nodes to allocate to the workflow job
* `ppn` - the number of processes per node to allocate to the workflow job

A sample EQR configuration file can be found [here](https://github.com/emews/emews-project-creator/blob/master/example_cfgs/eqr.yaml).

For additional explanation of EMEWS Queues and ME workflows, see the [EMEWS Tutorial](https://www.mcs.anl.gov/~emews/tutorial/)
