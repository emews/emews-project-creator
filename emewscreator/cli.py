import click
import sys
import os
import collections

from click.exceptions import ClickException

from emewscreator import __version__

from . import generate

# TODO make this such that external generates can be added
generators = {'emews': generate.generate_emews, 'sweep': generate.generate_sweep}


class NotRequiredIfT(click.Option):
    def __init__(self, *args, **kwargs):
        self.not_required_if: list = kwargs.pop("not_required_if")

        assert self.not_required_if, "'not_required_if' parameter required"
        kwargs["help"] = (kwargs.get("help", "") + "Option is mutually exclusive with " + ", ".join(self.not_required_if) + ".").strip()
        super(NotRequiredIfT, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        template = opts['template']
        if template in self.not_required_if:
            # raise click.UsageError("Illegal usage: '" + str(self.name) + "' not required with " + str(template) + ".")
            if self.name in opts:
                click.echo(f'{self.name} option not required for {template} template and will be ignored.')
            self.required = False
        return super(NotRequiredIfT, self).handle_parse_result(ctx, opts, args)


def version_msg():
    """Return the emewscreator version, location and Python powering it."""
    python_version = sys.version[:3]
    location = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return f'Emewscreator %(version)s from {location} (Python {python_version})'


def validate_extra_context(ctx, param, value):
    """Validate extra context."""
    for s in value:
        if '=' not in s:
            raise click.BadParameter(
                'EXTRA_CONTEXT should contain items of the form key=value; '
                "'{}' doesn't match that form".format(s)
            )

    # Convert tuple -- e.g.: (u'program_name=foobar', u'startsecs=66')
    # to dict -- e.g.: {'program_name': 'foobar', 'startsecs': '66'}
    return collections.OrderedDict(s.split('=', 1) for s in value) or None


@click.command(context_settings=dict(help_option_names=[u'-h', u'--help']))
@click.version_option(__version__, '-V', '--version', message=version_msg())
@click.argument('template')
@click.option(
    '-o',
    '--output-dir',
    default='.',
    type=click.Path(),
    help='Directory into whch the project template will be generated.',
)
@click.option(
    '-c',
    '--config',
    type=click.Path(),
    required=True,
    cls=NotRequiredIfT, not_required_if=['emews'],
    help='Path to the template configuration file',
)
# @click.argument('extra_context', nargs=-1, callback=validate_extra_context)
def main(template, output_dir, config):
    if template == 'help':
        click.echo(click.get_current_context().get_help())
        sys.exit(0)
    else:
        if config is not None:
            if (not (os.path.exists(config) and os.path.isfile(config))):
                raise ClickException(f"Config file '{config}' not found.")
        if template not in generators:
            raise ClickException(f'Unknown template "{template}"')
        else:
            generators[template](output_dir, config)


if __name__ == '__main__':
    main()
