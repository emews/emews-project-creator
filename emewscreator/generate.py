import os

from cookiecutter.main import cookiecutter

this_path = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(this_path, '../templates')


def generate_emews(output_dir):
    emews_template = os.path.join(templates_dir, 'emews')
    cookiecutter(emews_template, output_dir=output_dir, overwrite_if_exists=True)
