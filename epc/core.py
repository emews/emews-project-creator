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


def find_templates(ctx):
    templates = []
    name_suffix = '_template'
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(ctx['__template_root__']))
    for k in ctx:
        if k.endswith(name_suffix):
            t_path = os.path.join(ctx['__template_root__'], ctx[k]['location'])
            t_name = k[:-len(name_suffix)]
            t = template.Template(t_name, t_path, env)
            templates.append(t)
    return templates
            

