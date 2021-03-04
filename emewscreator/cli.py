import click
import sys
import os
import collections

from emewscreator import __version__
from emewscreator.generate import *


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
    help=u'Where to output the generated project dir into',
)
# @click.argument('extra_context', nargs=-1, callback=validate_extra_context)
def main(template, output_dir):
    if template == 'help':
        click.echo(click.get_current_context().get_help())
        sys.exit(0)

    else:
        func = f'generate_{template}'
        globals()[func](output_dir)


if __name__ == '__main__':
    main()
