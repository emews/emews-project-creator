# -*- coding: utf-8 -*-

import os
import jinja2

class Template:

    def __init__(self, name, description, root_path, env):
        self.name = name
        self.root_path = root_path
        self.description = description

        self.dirs = []
        self.files = []
        for root, dirs, files in os.walk(root_path):
            relative_root = root[len(self.root_path):]
            for d in dirs:
                self.dirs.append(os.path.join(relative_root, d))
            for f in files:
                if f != ".retain":
                    self.files.append(os.path.join(relative_root, f))
        
        self.env = env
        
    def is_templated(self, value):
        return "{{" in value and "}}" in value

    def apply_template(self, template_string, ctx):
        if self.is_templated(template_string):
            template = jinja2.Template(template_string)
            template_string = template.render(ctx)
        return template_string

    def generate(self, ctx):
        # template the directories
        output_path = ctx['project']['path']
        for d in self.dirs:
            new_dir = os.path.join(output_path, d)
            new_dir = self.apply_template(new_dir, ctx)
            if not os.path.exists(new_dir):
                os.makedirs(new_dir)
        
        base = os.path.basename(os.path.normpath(self.root_path))
        for f in self.files:
            new_f = os.path.join(output_path, f)
            new_f = self.apply_template(new_f, ctx)
            with open(new_f, 'w') as f_out:
                t_name = os.path.join(base, f)
                text = self.env.get_template(t_name).render(ctx)
                f_out.write(text)
