import os
import sys
import click
from . import client


@click.group()
def cli():
    """VRP Client"""
    pass


@cli.command("connect")
def connect():
    click.echo("VR Projector Client Connection...")
    sys.exit(client.connect())


@cli.command("play", context_settings={"allow_extra_args": True})
@click.argument(
    "filepaths",
    nargs=-1,
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, writable=False, readable=True
    ),
)
def play(filepaths):
    """
    TODO: Add help
    """
    click.echo("VRP Player...")
    for path in filepaths:
        click.echo(os.path.abspath(path))
