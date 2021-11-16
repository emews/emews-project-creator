import click
import sys
import os

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
                if len(self.not_required_if) == 1:
                    missing_msg = 'if option --{} is omitted'.format(self.not_required_if[0])
                else:
                    missing_msg = ','.join(['--{}'.format(s) for s in self.not_required_if[:-1]])
                    missing_msg = 'if any of the options {}, or --{} is omitted'.format(missing_msg,
                                                                                        self.not_required_if[-1])
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
    cls=NotRequiredIf, not_required_if=['workflow_name'],
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
@click.options(
    '--module-cfg-file',
    type=click.Path,
    help='Configuration file for the model exploration algorithm'
)
@click.option(
    '--trials',
    type=click.INT,
    help='Number of trials / replicates to perform for each model run'
)
@click.option(
    '--model-output-file-name',
    help='Model output base file name, file name only without extension (e.g., "output")'
)
@click.option(
    '--model-output-file-extension',
    help='Model output base file name extension (e.g., "csv"'
)
@click.pass_obj
def eqpy(obj: TemplateInfo, **kwargs):
    # after making base config, add kwargs to the config
    # except for workflow_name which is handled in base config
    pass
