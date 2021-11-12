import os
import shutil
import yaml
import json
import pathlib

from typing import Dict, List

from . import util

from cookiecutter.main import cookiecutter
from cookiecutter.vcs import clone


this_path = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(this_path, 'templates')
j2s_dir = os.path.join(templates_dir, 'common/j2s')
common_j2s = os.path.join(j2s_dir, 'common')
common_hooks = os.path.join(templates_dir, 'common/hooks')
common_files = os.path.join(templates_dir, 'common/files')
template_emews_root = '{{cookiecutter.emews_root_directory}}'

emews_wd = os.path.join(str(pathlib.Path.home()), '.emews')
emews_tag_file = '.CREATED_BY_EC'

DEFAULT_EQPY_EXT = '$EMEWS_PROJECT_ROOT/ext/EQ-Py'
DEFAULT_EQR_EXT = '$EMEWS_PROJECT_ROOT/ext/EQR'
OUTPUT_DIR_KEY = 'output_dir'


def copy_template_to_wd(template: str, template_dir, ):
    os.makedirs(emews_wd, exist_ok=True)
    template_wd = os.path.join(emews_wd, template)
    shutil.rmtree(template_wd, ignore_errors=True)
    os.makedirs(template_wd)
    util.copytree(template_dir, template_wd)
    return template_wd


def generate_base_config(emews_root: str, config_file: str, workflow_name: str) -> Dict:
    """Creates the base shared configuration by reading the yaml config file and
    adding / updating configuration parameters as necessary.
    """
    with open(config_file) as f_in:
        config = yaml.load(f_in, Loader=yaml.SafeLoader)

    # User specifies the emews root, but cookiecutter actually
    # resolves the templates into the parent directory of emews root.
    # So, here we split the path into those parts.
    config['emews_root_directory'] = os.path.basename(emews_root)
    config[OUTPUT_DIR_KEY] = os.path.dirname(emews_root)
    config['_copy_without_render'] = ['etc/emews_utils.sh']

    if workflow_name is not None:
        config['workflow_name'] = workflow_name
    return config


def config_to_cc(template_dir: str, base_config: Dict, additional_context: List=[]) -> Dict:
    """Updates a copy of the specified base_config with any additional context and
    writes the config to json as a cookiecutter configuration file.

    Return:
        The updated copy of the base config dict.
    """
    config = base_config.copy()
    for ctx in additional_context:
        ctx(config)

    with open(os.path.join(template_dir, 'cookiecutter.json'), 'w') as f_out:
        json.dump(config, f_out, indent=4)

    return config


def copy_common(proj_dir, j2s: List=[]):
    proj_common = os.path.join(proj_dir, template_emews_root, 'common')
    os.mkdir(proj_common)
    util.copytree(common_j2s, proj_common)

    for j2 in j2s:
        src = os.path.join(j2s_dir, j2)
        util.copytree(src, proj_common)

    hooks = os.path.join(proj_dir, 'hooks')
    os.mkdir(hooks)
    util.copytree(common_hooks, hooks)

    return proj_common


def generate_emews(emews_root, base_config: Dict, keep_existing):
    emews_template = os.path.join(templates_dir, 'emews')
    emews_wd = copy_template_to_wd('emews', emews_template)
    config = config_to_cc(emews_wd, base_config, [])
    output_dir = config[OUTPUT_DIR_KEY]
    cookiecutter(emews_wd, output_dir=output_dir, skip_if_file_exists=keep_existing, overwrite_if_exists=True, no_input=True)
    pathlib.Path('{}/{}'.format(emews_root, emews_tag_file)).touch()


def check_gen_emews(emews_root: str, base_config: Dict, keep_existing):
    p = pathlib.Path('{}/{}'.format(emews_root, emews_tag_file))
    if not p.exists():
        generate_emews(emews_root, base_config, keep_existing)


def config_for_all(config: Dict):
    workflow_fname = util.clean_filename(config['workflow_name'])
    config['cfg_file_name'] = workflow_fname.lower()
    config['wf_file_name'] = workflow_fname.lower()
    config['submit_wf_file_name'] = f'run_{workflow_fname}'
    clean_model_name = util.clean_filename(config['model_name']).lower()
    config['model_launcher_name'] = f'run_{clean_model_name}'

    hpc_schedule_defaults = {'walltime': '01:00:00', 'queue': 'queue', 'project': 'project',
                             'nodes': 4, 'ppn': 4}
    # add HPC defaults 'walltime' etc. to the config, if the user hasn't
    # in order to prevent cookiecutter from failing.
    for k, v in hpc_schedule_defaults.items():
        if k not in config:
            config[k] = v


def config_for_eqpy(config: Dict):
    config['eq_call_prefix'] = 'EQPy'
    config['me_output_type'] = 'json'

    if 'eqpy_location' not in config:
        config['eqpy_location'] = DEFAULT_EQPY_EXT


def config_for_eqr(config: Dict):
    config['eq_call_prefix'] = 'EQR'
    config['me_output_type'] = 'json'
    # tell cookiecutter to copy these files, but don't run
    # jinja on them
    config['_copy_without_render'].append('ext/EQ-R/src/*')

    if 'eqr_location' not in config:
        config['eqr_location'] = DEFAULT_EQR_EXT


def generate_sweep(emews_root, base_config, keep_existing):
    sweep_template = os.path.join(templates_dir, 'sweep')
    sweep_wd = copy_template_to_wd('sweep', sweep_template)
    config = config_to_cc(sweep_wd, base_config, [config_for_all])
    output_dir = config[OUTPUT_DIR_KEY]
    copy_common(sweep_wd, ['sweep'])
    check_gen_emews(emews_root, base_config, keep_existing)
    # overwrite_if_exists prevents errors if the directory structure already exists
    # skip_if_file_exists controls where existing files get overwritten
    cookiecutter(sweep_wd, output_dir=output_dir, skip_if_file_exists=keep_existing, overwrite_if_exists=True,
                 no_input=True)


def rename_gitignore(source_dir):
    src = os.path.join(source_dir, 'gitignore.txt')
    if os.path.exists(src):
        dst = os.path.join(source_dir, '.gitignore')
        os.rename(src, dst)


def copy_eqpy_code(eqpy_location):
    clone('https://github.com/emews/EQ-Py.git', clone_to_dir=emews_wd, no_input=True)
    src = os.path.join(emews_wd, 'EQ-Py/src')
    util.copy_files(src, eqpy_location, ['eqpy.py', 'EQPy.swift'])
    shutil.rmtree(os.path.join(emews_wd, 'EQ-Py'), ignore_errors=True)


def copy_eqr_code(eqr_location):
    clone('https://github.com/emews/EQ-R.git', clone_to_dir=emews_wd, no_input=True)
    src = os.path.join(emews_wd, 'EQ-R/src')
    util.copy_files(src, eqr_location, ['EQR.swift', 'BlockingQueue.h', 'EQR.cpp', 'EQR.h',
                                        'EQR.i', 'Makefile.in', 'bootstrap', 'configure.ac',
                                        'find-tcl.sh', 'make-package.tcl', 'settings.mk.in'])
    shutil.rmtree(os.path.join(emews_wd, 'EQ-R'), ignore_errors=True)


def generate_eqpy(emews_root, base_config, keep_existing):
    eqpy_template = os.path.join(templates_dir, 'eqpy')
    # copies template to .emews
    eqpy_wd = copy_template_to_wd('eqpy', eqpy_template)
    config = config_to_cc(eqpy_wd, base_config, [config_for_all, config_for_eqpy])
    eqpy_location = config['eqpy_location']
    if eqpy_location == DEFAULT_EQPY_EXT:
        eqpy_location = os.path.join(eqpy_wd, template_emews_root, 'ext/EQ-Py')
        copy_eqpy_code(eqpy_location)
    elif not os.path.exists(eqpy_location):
        os.makedirs(eqpy_location)
        copy_eqpy_code(eqpy_location)
    rename_gitignore(eqpy_location)
    copy_common(eqpy_wd, ['eq', 'eqpy'])
    check_gen_emews(emews_root, base_config, keep_existing)
    # overwrite_if_exists prevents errors if the directory structure already exists
    # skip_if_file_exists controls where existing files get overwritten
    output_dir = config[OUTPUT_DIR_KEY]
    cookiecutter(eqpy_wd, output_dir=output_dir, skip_if_file_exists=keep_existing, overwrite_if_exists=True,
                 no_input=True)


def generate_eqr(emews_root, base_config, keep_existing):
    eqr_template = os.path.join(templates_dir, 'eqr')
    eqr_wd = copy_template_to_wd('eqr', eqr_template)
    config = config_to_cc(eqr_wd, base_config, [config_for_all, config_for_eqr])
    eqr_location = config['eqr_location']
    if eqr_location == DEFAULT_EQR_EXT:
        eqr_location = os.path.join(eqr_wd, template_emews_root, 'ext/EQ-R/src')
        copy_eqr_code(eqr_location)
    elif not os.path.exists(eqr_location):
        eqr_location = os.path.join(eqr_location, 'src')
        os.makedirs(eqr_location)
        copy_eqr_code(eqr_location)
    rename_gitignore(eqr_location)
    copy_common(eqr_wd, ['eq', 'eqr'])
    check_gen_emews(emews_root, base_config, keep_existing)
    # overwrite_if_exists prevents errors if the directory structure already exists
    # skip_if_file_exists controls where existing files get overwritten
    output_dir = config[OUTPUT_DIR_KEY]
    cookiecutter(eqr_wd, output_dir=output_dir, skip_if_file_exists=keep_existing, overwrite_if_exists=True,
                 no_input=True)
