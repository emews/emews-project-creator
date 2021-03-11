import os
import shutil
import yaml
import json
import pathlib

from typing import Dict, List

from . import util

from cookiecutter.main import cookiecutter

this_path = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(this_path, '../templates')
common_templates = os.path.join(templates_dir, 'common/templates')
common_hooks = os.path.join(templates_dir, 'common/hooks')
template_emews_root = '{{cookiecutter.emews_root_directory}}'

emews_wd = os.path.join(str(pathlib.Path.home()), '.emews')


def copy_template_to_wd(template: str, template_dir, ):
    os.makedirs(emews_wd, exist_ok=True)
    template_wd = os.path.join(emews_wd, template)
    shutil.rmtree(template_wd, ignore_errors=True)
    os.makedirs(template_wd)
    util.copytree(template_dir, template_wd)
    return template_wd


def config_to_cc(template_dir, config_file, additional_context=None):
    """Converts a yaml config file to a cookiecutter json
    """
    with open(config_file) as f_in:
        config = yaml.load(f_in, Loader=yaml.SafeLoader)

    if additional_context is not None:
        additional_context(config)

    with open(os.path.join(template_dir, 'cookiecutter.json'), 'w') as f_out:
        json.dump(config, f_out, indent=4)


def copy_common(template_dir):
    template_common = os.path.join(template_dir, template_emews_root, 'common')
    os.mkdir(template_common)
    util.copytree(common_templates, template_common)

    hooks = os.path.join(template_dir, 'hooks')
    os.mkdir(hooks)
    util.copytree(common_hooks, hooks)

    return template_common


def generate_emews(output_dir, config_file):
    emews_template = os.path.join(templates_dir, 'emews')
    cookiecutter(emews_template, output_dir=output_dir, overwrite_if_exists=True)


def config_for_sweep(config: Dict):
    workflow_fname = util.clean_filename(config['workflow_name'])
    config['cfg_file_name'] = workflow_fname.lower()
    config['wf_file_name'] = workflow_fname.lower()
    config['submit_wf_file_name'] = f'run_{workflow_fname}'
    clean_model_name = util.clean_filename(config['model_name']).lower()
    config['model_launcher_name'] = f'run_{clean_model_name}'


def generate_sweep(output_dir, config_file):
    sweep_template = os.path.join(templates_dir, 'sweep')
    sweep_wd = copy_template_to_wd('sweep', sweep_template)
    config_to_cc(sweep_wd, config_file, config_for_sweep)
    copy_common(sweep_wd)
    cookiecutter(sweep_wd, output_dir=output_dir, overwrite_if_exists=True, no_input=True)
