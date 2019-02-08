import sys
import click
from . import client


@click.group(chain=True)
def cli():
    """VR Projector Client"""
    pass


@cli.command("connect")
def connect():
    click.echo("VR Projector Client Connection...")
    sys.exit(client.connect())
