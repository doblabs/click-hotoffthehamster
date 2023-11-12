"""From https://click.palletsprojects.com/en/8.1.x/options/#yes-parameters"""
from typing_extensions import assert_type

import click_hotoffthehamster


@click_hotoffthehamster.command()
@click_hotoffthehamster.confirmation_option(
    prompt="Are you sure you want to drop the db?"
)
def dropdb() -> None:
    click_hotoffthehamster.echo("Dropped all tables!")


assert_type(dropdb, click_hotoffthehamster.Command)
