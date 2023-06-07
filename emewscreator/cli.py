import click
import sys
import os
import colorama
from eqsql import db_tools

from emewscreator import __version__

from . import generate


class NotRequiredIf(click.Option):

    def __init__(self, *args, **kwargs):
        self.not_required_if: list = kwargs.pop("not_required_if")
        assert self.not_required_if, "'not_required_if' parameter required"
        kwargs['required'] = False
        kwargs["help"] = kwargs.get("help", "") + '  [required if any command line arguments are missing]'
        super(NotRequiredIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        if self.name not in opts:
            self.required = False
            for opt_name in self.not_required_if:
                self.required = opt_name not in opts
                if self.required:
                    break

            if self.required:
                option_list = [x.replace('_', '-') for x in self.not_required_if]
                if len(self.not_required_if) == 1:
                    missing_msg = 'if option "--{}" is omitted'.format(option_list[0])
                else:
                    missing_msg = ', '.join(['--{}'.format(s) for s in option_list[:-1]])
                    missing_msg = 'if any of the options "{}, or --{}" are omitted'.format(missing_msg,
                                                                                           option_list[-1])
                msg = """option '-c' / '--config' is required {}""".format(missing_msg)
                raise click.UsageError(msg)

        return super(NotRequiredIf, self).handle_parse_result(ctx, opts, args)


def version_msg():
    """Return the emewscreator version, location and Python running it."""
    python_version = sys.version[:3]
    location = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return f'Emewscreator %(version)s from {location} (Python {python_version})'


def validate_config(ctx, param, value):
    if value is not None and (not (os.path.exists(value) and os.path.isfile(value))):
        raise click.BadParameter(f"file '{value}' not found")
    return value

# def validate_extra_context(ctx, param, value):
#     """Validate extra context."""
#     for s in value:
#         if '=' not in s:
#             raise click.BadParameter(
#                 'EXTRA_CONTEXT should contain items of the form key=value; '
#                 "'{}' doesn't match that form".format(s)
#             )

#     # Convert tuple -- e.g.: (u'program_name=foobar', u'startsecs=66')
#     # to dict -- e.g.: {'program_name': 'foobar', 'startsecs': '66'}
#     return collections.OrderedDict(s.split('=', 1) for s in value) or None


class TemplateInfo:

    def __init__(self, out_dir, model_name, overwrite):
        self.out_dir = out_dir
        self.model_name = model_name
        self.overwrite = overwrite


@click.group(context_settings=dict(help_option_names=[u'-h', u'--help']))
@click.version_option(__version__, '-V', '--version', message=version_msg())
@click.option(
    '-o',
    '--output-dir',
    default='.',
    type=click.Path(),
    help='Directory into which the project template will be generated. Defaults to the current directory',
)
@click.option(
    '-m',
    '--model-name',
    default='model',
    help='Name of the model application. Defaults to "model".'
)
@click.option(
    '-w',
    '--overwrite',
    is_flag=True,
    help='Overwrite existing files'
)
@click.pass_context
def cli(ctx, output_dir, model_name, overwrite):
    ctx.obj = TemplateInfo(output_dir, model_name, overwrite)


# Sweep
@cli.command('sweep', short_help='create a sweep workflow')
@click.option(
    '-c',
    '--config',
    type=click.Path(),
    cls=NotRequiredIf, not_required_if=['workflow_name'],
    callback=validate_config,
    help='Path to the template configuration file ',
)
@click.option(
    '-n',
    '--workflow-name',
    required=False,
    help='Name of the workflow'
)
@click.pass_obj
def sweep(obj: TemplateInfo, config, workflow_name):
    base_config = generate.generate_base_config(obj.out_dir, config, workflow_name, obj.model_name)
    generate.generate_sweep(obj.out_dir, base_config, not obj.overwrite)


# EQPy
@cli.command('eqpy', short_help='create an eqpy workflow')
@click.option(
    '-c',
    '--config',
    type=click.Path(),
    cls=NotRequiredIf, not_required_if=['workflow_name', 'module_name', 'me_cfg_file',
                                        'model_output_file_name'],
    callback=validate_config,
    help='Path to the template configuration file',
)
@click.option(
    '-n',
    '--workflow-name',
    required=False,
    help='Name of the workflow'
)
@click.option(
    '--module-name',
    help='Python model exploration algorithm module name'
)
@click.option(
    '--me-cfg-file',
    type=click.Path(),
    help='Configuration file for the model exploration algorithm'
)
@click.option(
    '--trials',
    type=click.INT,
    help='Number of trials / replicates to perform for each model run. Defaults to 1'
)
@click.option(
    '--model-output-file-name',
    help='Model output base file name, file name only (e.g., "output.csv")'
)
@click.option(
    '--eqpy-dir',
    type=click.Path(),
    help='Directory where the eqpy extension is located. If the extension does not exist at this location it will be installed there. Defaults to {output_dir}/ext/EQ-Py'
)
@click.pass_obj
def eqpy(obj: TemplateInfo, **kwargs):
    config = kwargs.pop('config')
    workflow_name = kwargs.pop('workflow_name')
    base_config = generate.generate_base_config(obj.out_dir, config, workflow_name, obj.model_name)
    generate.override_base_config(base_config, kwargs, {'trials': 1})
    generate.generate_eqpy(obj.out_dir, base_config, not obj.overwrite)


# EQR
@cli.command('eqr', short_help='create an eqr workflow')
@click.option(
    '-c',
    '--config',
    type=click.Path(),
    cls=NotRequiredIf, not_required_if=['workflow_name', 'script_file', 'me_cfg_file',
                                        'model_output_file_name'],
    callback=validate_config,
    help='Path to the template configuration file',
)
@click.option(
    '-n',
    '--workflow-name',
    required=False,
    help='Name of the workflow'
)
@click.option(
    '--script-file',
    help='Path to the R model exploration algorithm'
)
@click.option(
    '--me-cfg-file',
    type=click.Path(),
    help='Configuration file for the model exploration algorithm'
)
@click.option(
    '--trials',
    type=click.INT,
    help='Number of trials / replicates to perform for each model run',
)
@click.option(
    '--model-output-file-name',
    help='Model output base file name, file name only (e.g., "output.csv")'
)
@click.option(
    '--eqr-dir',
    type=click.Path(),
    help='Directory where the eqr extension is located. If the extension does not exist at this location it will be installed there. Defaults to {output_dir}/ext/EQ-R'
)
@click.pass_obj
def eqr(obj: TemplateInfo, **kwargs):
    config = kwargs.pop('config')
    workflow_name = kwargs.pop('workflow_name')
    base_config = generate.generate_base_config(obj.out_dir, config, workflow_name, obj.model_name)
    generate.override_base_config(base_config, kwargs, {'trials': 1})
    generate.generate_eqr(obj.out_dir, base_config, not obj.overwrite)


@cli.command('init_db', short_help='initialize an eqsql database')
@click.option(
    '-d',
    '--db-path',
    required=True,
    type=click.Path(),
    help='Database directory path. The database will be created in this directory.'
)
@click.option(
    '-p',
    '--port',
    required=False,
    type=click.INT,
    help="The database port, if any."
)
@click.pass_obj
def init_db(obj: TemplateInfo, **kwargs):
    colorama.init(autoreset=True)
    print(colorama.Fore.GREEN + 'Initializing Database')
    db_path = kwargs['db_path']
    result = db_tools.init_eqsql_db(db_path, db_port=kwargs['port'])
    if result is None:
        print(colorama.Fore.RED + 'Database Initialization Failed')
    else:
        print(colorama.Fore.GREEN + 'Database Initialization Succeeded')
        print(colorama.Fore.GREEN + f'DB_PATH: {result[0]}\nDB_USER: {result[1]}\nDB_NAME: {result[2]}')
        if kwargs['port'] is not None:
            print(f'DB_PORT: {result[3]}')


# EQSQL
@cli.command('eqsql', short_help='create an eqsql workflow')
@click.option(
    '-c',
    '--config',
    type=click.Path(),
    cls=NotRequiredIf, not_required_if=['workflow_name', 'module_name', 'me_cfg_file',
                                        'model_output_file_name'],
    callback=validate_config,
    help='Path to the template configuration file',
)
@click.option(
    '-n',
    '--workflow-name',
    required=False,
    help='Name of the workflow'
)
@click.option(
    '--module-name',
    help='Python model exploration algorithm module name'
)
@click.option(
    '--me-cfg-file',
    type=click.Path(),
    help='Configuration file for the model exploration algorithm'
)
@click.option(
    '--trials',
    type=click.INT,
    help='Number of trials / replicates to perform for each model run. Defaults to 1'
)
@click.option(
    '--model-output-file-name',
    help='Model output base file name, file name only (e.g., "output.csv")'
)
@click.pass_obj
def eqsql(obj: TemplateInfo, **kwargs):
    config = kwargs.pop('config')
    workflow_name = kwargs.pop('workflow_name')
    base_config = generate.generate_base_config(obj.out_dir, config, workflow_name, obj.model_name)
    # trials:1 - is default if doesn't exist
    generate.override_base_config(base_config, kwargs, {'trials': 1})
    generate.generate_eqsql(obj.out_dir, base_config, not obj.overwrite)
