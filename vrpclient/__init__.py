import os
import sys
import click
from . import client

SAMPLE_MEDIA = {
    name: os.path.abspath(name)
    for name in os.listdir(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "media"))
    )
}


@click.group()
@click.option("-d", "--debug", is_flag=True)
@click.option("-v", "--verbose", is_flag=True)
@click.pass_context
def cli(ctx, debug, verbose):
    """VRP Client"""
    ctx.ensure_object(dict)
    ctx.obj.update({"DEBUG": debug, "VERBOSE": verbose})


@cli.command("connect")
@click.pass_context
def connect():
    """Connect to a """
    click.echo("VR Projector Client Connection...")
    sys.exit(client.connect())


@cli.command("play")
@click.argument(
    "filepaths",
    nargs=-1,
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
    ),
)
@click.pass_context
def play(ctx, filepaths):
    """Play media files using VLC."""

    debug = ctx.obj["DEBUG"]
    verbose = ctx.obj["VERBOSE"] if not debug else debug

    if not debug and not filepaths:
        raise click.UsageError('Error: Missing argument "FILEPATHS".')

    if debug:
        click.echo("Debug is on")
        if not filepaths:  # load a default video for debugging
            filepaths = [SAMPLE_MEDIA["360video_2min.mp4"]]

    click.echo("Media files:")
    for p in filepaths:
        is_sample = p in SAMPLE_MEDIA.values()
        file_disp = click.format_filename(p, shorten=not verbose or is_sample)
        click.echo(f'{file_disp}{" (sample media)" if is_sample else None}')
