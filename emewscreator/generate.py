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


def copy_template_to_wd(template: str, template_dir, ):
    os.makedirs(emews_wd, exist_ok=True)
    template_wd = os.path.join(emews_wd, template)
    shutil.rmtree(template_wd, ignore_errors=True)
    os.makedirs(template_wd)
    util.copytree(template_dir, template_wd)
    return template_wd


def config_to_cc(template_dir, config_file, additional_context: List=[]) -> Dict:
    """Converts a yaml config file to a cookiecutter json

    Returns:
        A dictionary holding the configuration info.
    """
    with open(config_file) as f_in:
        config = yaml.load(f_in, Loader=yaml.SafeLoader)

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

    # files = os.path.join(proj_dir, 'files')
    # os.mkdir(files)
    # util.copytree(common_files, files)

    return proj_common


def generate_emews(output_dir, config_file):
    emews_template = os.path.join(templates_dir, 'emews')
    emews_wd = copy_template_to_wd('emews', emews_template)
    config = config_to_cc(emews_wd, config_file, [])
    cookiecutter(emews_template, output_dir=output_dir, overwrite_if_exists=True, no_input=True)
    emews_root_dir = config['emews_root_directory']
    pathlib.Path('{}/{}/{}'.format(output_dir, emews_root_dir, emews_tag_file)).touch()


def check_gen_emews(config: Dict, output_dir: str, config_file: str):
    emews_root_dir = config['emews_root_directory']
    p = pathlib.Path('{}/{}/{}'.format(output_dir, emews_root_dir, emews_tag_file))
    if not p.exists():
        generate_emews(output_dir, config_file)


def config_for_all(config: Dict):
    workflow_fname = util.clean_filename(config['workflow_name'])
    config['cfg_file_name'] = workflow_fname.lower()
    config['wf_file_name'] = workflow_fname.lower()
    config['submit_wf_file_name'] = f'run_{workflow_fname}'
    clean_model_name = util.clean_filename(config['model_name']).lower()
    config['model_launcher_name'] = f'run_{clean_model_name}'


def config_for_eqpy(config: Dict):
    pass


def config_for_eqr(config: Dict):
    pass


def generate_sweep(output_dir, config_file):
    sweep_template = os.path.join(templates_dir, 'sweep')
    sweep_wd = copy_template_to_wd('sweep', sweep_template)
    config = config_to_cc(sweep_wd, config_file, [config_for_all])
    copy_common(sweep_wd, ['sweep'])
    check_gen_emews(config, output_dir, config_file)
    cookiecutter(sweep_wd, output_dir=output_dir, overwrite_if_exists=True, no_input=True)


def rename_gitignore(source_dir):
    src = os.path.join(source_dir, 'gitignore.txt')
    dst = os.path.join(source_dir, '.gitignore')
    os.rename(src, dst)


def copy_eqpy_code(eqpy_wd):
    clone('https://github.com/emews/EQ-Py.git', clone_to_dir=emews_wd, no_input=True)
    src = os.path.join(emews_wd, 'EQ-Py/src')
    dst = os.path.join(eqpy_wd, template_emews_root, 'ext/EQ-Py')
    util.copy_files(src, dst, ['eqpy.py', 'EQPy.swift'])
    shutil.rmtree(os.path.join(emews_wd, 'EQ-Py'), ignore_errors=True)
    return dst


def copy_eqr_code(eqr_wd):
    clone('https://github.com/emews/EQ-R.git', clone_to_dir=emews_wd, no_input=True)
    src = os.path.join(emews_wd, 'EQ-R/src')
    dst = os.path.join(eqr_wd, template_emews_root, 'ext/EQ-R')
    # TODO Compile and copy the correct files
    util.copy_files(src, dst, ['EQR.swift'])
    shutil.rmtree(os.path.join(emews_wd, 'EQ-R'), ignore_errors=True)
    return dst


def generate_eqpy(output_dir, config_file):
    eqpy_template = os.path.join(templates_dir, 'eqpy')
    # copies template to .emews
    eqpy_wd = copy_template_to_wd('eqpy', eqpy_template)
    eqpy_ext_dir = copy_eqpy_code(eqpy_wd)
    rename_gitignore(eqpy_ext_dir)
    config = config_to_cc(eqpy_wd, config_file, [config_for_all, config_for_eqpy])
    copy_common(eqpy_wd, ['eq', 'eqpy'])
    check_gen_emews(config, output_dir, config_file)
    cookiecutter(eqpy_wd, output_dir=output_dir, overwrite_if_exists=True, no_input=True)


def generate_eqr(output_dir, config_file):
    eqr_template = os.path.join(templates_dir, 'eqr')
    eqr_wd = copy_template_to_wd('eqr', eqr_template)
    eqr_ext_dir = copy_eqr_code(eqr_wd)
    rename_gitignore(eqr_ext_dir)
    config = config_to_cc(eqr_wd, config_file, [config_for_all, config_for_eqr])
    copy_common(eqr_wd, ['eq', 'eqr'])
    check_gen_emews(config, output_dir, config_file)
    cookiecutter(eqr_wd, output_dir=output_dir, overwrite_if_exists=True, no_input=True)
