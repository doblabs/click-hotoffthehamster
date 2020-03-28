"""
From https://click.palletsprojects.com/en/8.1.x/options/#callbacks-and-eager-options.
"""
from typing_extensions import assert_type

import click_hotoffthehamster


@click_hotoffthehamster.command()
@click_hotoffthehamster.version_option("0.1")
def hello() -> None:
    click_hotoffthehamster.echo("Hello World!")


assert_type(hello, click_hotoffthehamster.Command)
