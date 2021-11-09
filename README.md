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

EMEWS Creator is run from the command line.

```
$ python -m emewscreator -h
Usage: emewscreator [OPTIONS] TEMPLATE

Options:
  -V, --version          Show the version and exit.
  -o, --output-dir PATH  Directory into whch the project template will be
                         generated.

  -c, --config PATH      Path to the template configuration file.   [required]
  -w, --overwrite        Overwrite existing files
  -h, --help             Show this message and exit.
  ```

where TEMPLATE is one of the three workflow types: `sweep`, `eqpy`, or `eqr`.
EMEWS Creator will create a directory structure and the appropriate
files within the directory specified by the `-o / --output-dir` argument. Each
workflow template requires a user provided configuration file in yaml format, specified
using the `-c / --config` argument. Sample
configuration files can be found [here](https://github.com/emews/emews-project-creator/tree/master/example_cfgs)
in the `example_cfgs` directory in the EMEWS Creator github repository. 
By default, any existing files within the directory will not be overwritten. 
The `-w / --overwrite` argument reverses this behavior. When it is
present, any existing files will be overwritten. This should be used
with caution.

## EMEWS Project Structure ##

Each of the templates will create the default EMEWS project  structure
in `emews_root_directory` beneath the directory specified with the `-o / --output-dir`
argument. `emews_root_directory` is specified in the templates configuration file. 

### Directories ###

Given an `emews_root_directory` of `swift_project`, the default structure is as follows:

```
swift_project/
  data/
  etc/
  ext/
  python/
    test/
  R/
    test/
  scripts/
  swift/
    cfgs/
  README.md
```

The directories are intended to contain the following:

 * `data` - model and algorithm input etc. data
 * `etc` - additional code used by EMEWS
 * `ext` - swift-t extensions, including the default emews utility code extension as well as
 the eqr and eqpy extensions
 * `python` - python code (e.g., model exploration algorithms written in python)
 * `python\test` - tests of the python code
 * `R` - R code (e.g., model exploration algorithms written R)
 * `R\test` - tests of the R code
 * `scripts` - any necessary scripts (e.g., scripts to launch an application), excluding scripts used to run the workflow
 * `swift` - swift code and scripts used to submit and run the workflow


 ### Files ###

Each of the templates will generate the following files. The file names
are derived from parameters specified in the template configuration
file. The names of those parameters are included in curly brackets
in the file names below.

* `swift/run_{workflow_name}.sh` - a bash script used to launch the workflow
* `swift/{workflow_name}.swift` - the swift script that implements the template's workflow.
* `scripts/run_{model_name}_X.sh` - a bash script used to run the model application.
Here, X will be replaced by the template type (i.e., sweep, eqr, eqpy) as each
model launch script is designed to work a particular type of wokflow.
* `cfgs/{workflow_name}.cfg` - a configuration file for running the workflow

These files may requre some user customization before they can be used. The 
relevant sections are marked with `TODO`.

Once any edits have been completed, the workflows can be run with:

```
$ run_{workflow_name}.sh <experiment_name> cfgs/{workflow_name}.cfg
```

## Templates ##

Each workflow template requires a user provided configuration file in yaml format, specified
using the `-c / --config` argument. The following configuration parameters are
common to all the templates.

* `emews_root_directory` - the directory in which the workflow directories and files will be placed. If
this doesn't exist, it will be created. 
* `workflow_name` - the name of the workflow. This will be used as the file name for the workflow configuration, 
submission, and swift script files. Spaces will be replaced by underscores.
* `model_name` - the name of the model to run during the sweep. This will be used in the model execution
bash script. Spaces will be replaced by underscores.

The configuration file can also contain entries for running the workflow on an HPC system
where a job is submitted via an HPC scheduler (e.g., the slurm scheduler).
See your HPC resource's documentation for details on how to set these. For non-HPC
runs these can be omitted.

* `walltime` - the estimated duration of the workflow job. The value must be surrounded by single quotes in order to parse correctly.
* `queue` - the queue to run the workflow job on
* `project` - the project to run the workflow job with
* `nodes` - the number of nodes to allocate to the workflow job
* `ppn` - the number of processes per node to allocate to the workflow job

### Sweep ###

The sweep template creates a sweep workflow in which EMEWS reads an input file,
and runs an application (e.g., a simulation model) using each line of the input file
as input to an application run.

Usage:
```
$ python -m emewscreator sweep -o SampleModel -c sweep_config.yaml
```

In addition to the common configuration parameters described [above](#templates),
the configuration file for a sweep requires an additional parameter.

* `upf` - the location of the unrolled parameter file (UPF) containing the collection of model 
input parameters (one run per line) to sweep over.

A sample sweep configuration file can be found [here](https://github.com/emews/emews-project-creator/blob/master/example_cfgs/sweep.yaml).

For a more thorough explanation of the sweep workflow, see the [EMEWS Tutorial](https://www.mcs.anl.gov/~emews/tutorial/)

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

In addition to the default set of files described in the
[EMEWS Project Structure](#emews-project-structure) section, the eqpy template will also
install the EQ/Py EMEWS Swift-t extension in `ext/EQ-Py`. The extension
consists of the following files.

* `ext/EQ-Py/eqpy.py`
* `ext/EQ-Py/EQPy.swift`

These should not be edited by the user.

For a more thorough explanation of EMEWS Queues and ME workflows, see the [EMEWS Tutorial](https://www.mcs.anl.gov/~emews/tutorial/)

### EQR ###

The EQR template creates a workflow that uses emews queues for R (EQR) to 
run an application (e.g., a simulation model) using input parameters provided by a
R model exploration (ME) algorithm. The workflow will start the R ME
which then iteratively provides json format input parameters for model
execution.

*Note*: The EQR extension requires an additional compilation step. Once the template has been run,
see `{emews_root_directory}/ext/EQ-R/src/README.md` for compilation instructions.

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

In addition to the default set of files described in the
[EMEWS Project Structure](#emews-project-structure) section, the eqr template will also
install the source for EQ/R EMEWS Swift-t extension in `ext/EQ-R/src`. The extension needs 
to be compiled before it can be used. See `ext/EQ-R/src/README.md` for compilation instructions.

For additional explanation of EMEWS Queues and ME workflows, see the [EMEWS Tutorial](https://www.mcs.anl.gov/~emews/tutorial/)
