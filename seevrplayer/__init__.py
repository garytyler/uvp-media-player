import os
import sys
import click
from . import client
from . import player
from . import viewer


MEDIA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "media"))
SAMPLE_MEDIA = {name: os.path.join(MEDIA_DIR, name) for name in os.listdir(MEDIA_DIR)}


@click.group()
@click.option("-d", "--debug", is_flag=True)
@click.option("-v", "--verbose", is_flag=True)
@click.pass_context
def cli(ctx, debug, verbose):
    """VRP Client"""
    ctx.ensure_object(dict)
    ctx.obj.update({"DEBUG": debug, "VERBOSE": verbose})
    ctx.color = True


@cli.command("connect")
@click.pass_context
def connect():
    """Connect to a VRP Server instance."""
    click.echo("VRP Client Connection...")
    sys.exit(client.connect())


@cli.command("play")
@click.option("-f", "--fullscreen", is_flag=True)
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
def play(ctx, fullscreen, filepaths):
    """Play media files using VLC."""

    debug = ctx.obj["DEBUG"]
    verbose = ctx.obj["VERBOSE"] if not debug else debug

    if not debug and not filepaths:
        raise click.UsageError('Missing argument "FILEPATHS".')

    if debug:
        click.echo("Debug is on")
        if not filepaths:  # load a sample video for debugging
            filepaths = [SAMPLE_MEDIA["360video_2min.mp4"]]

    click.echo(click.style("Media files:", fg="bright_blue", underline=True))
    for filepath in filepaths:
        sample_flair = "(sample media)" if filepath in SAMPLE_MEDIA.values() else ""
        file_disp = click.format_filename(filepath, shorten=not verbose or sample_flair)
        click.echo(f"{file_disp} {click.style(sample_flair, fg='bright_red')}")

        viewer.play(filepath)
        # if fullscreen:
        #     viewer.play(filepath)
        # else:
        #     player.play(filepath)
