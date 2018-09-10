# -*- coding: utf-8 -*-

import os.path
import json
from . import template
from collections import OrderedDict
import jinja2

def load_context(template_path, fname='template.json'):
    template_file = os.path.join(template_path, fname)
    if not os.path.exists(template_file): 
        raise FileNotFoundError("Invalid template: {} not found".format(template_file))
    try:
        with open(template_file) as f_in:
            ctx = json.load(f_in, object_pairs_hook=OrderedDict)

    except ValueError as e: 
        full_fpath = os.path.abspath(template_file)
        json_message = str(e)
        msg = 'JSON decoding error while loading "{0}": {1}'.format(full_fpath, json_message)
        raise ValueError(msg)


    if type(ctx) != type(OrderedDict()):
        full_fpath = os.path.abspath(template_file)
        msg = 'JSON decoding error while loading "{0}": not a valid JSON map'.format(full_fpath)
        raise ValueError(msg)

    ctx['__template_root__'] = os.path.dirname(os.path.abspath(template_file))

    return ctx

def basename(path):
    return os.path.basename(path)

def dirname(path):
    return os.path.dirname(path)

def find_templates(ctx):
    templates = {}
    name_suffix = '_template'

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(ctx['__template_root__']))
    env.filters['basename'] = basename
    env.filters['dirname']  = dirname

    for k in ctx:
        if k.endswith(name_suffix):
            t_dict = ctx[k]
            t_path = os.path.join(ctx['__template_root__'], t_dict['location'])
            t_name = k[:-len(name_suffix)]
            description = ''
            if 'description'in t_dict:
                description = t_dict['description']
            t = template.Template(t_name, description, t_path, env)
            templates[t_name] = t

    return templates


def list_templates(template_path):
    ctx = load_context(template_path)
    templates = find_templates(ctx)
    for name, template in templates.items():
        print(name)
        print("Description: {}".format(template.description))

def run_template(template_path, name, project_path):
    ctx = load_context(template_path)
    templates = find_templates(ctx)
    if name in templates:
        template = templates[name]
        template_ctx = ctx['{}_template'.format(name)]
        project_path = os.path.abspath(project_path)
        template_ctx['project'] = {'path' : project_path}
        print("Generating {}".format(name))
        template.generate(template_ctx)
        if os.path.exists(os.path.join(project_path, 'README.md')):
            print("show readme")
    else:
        print("Template {} not found".format(name))



            

