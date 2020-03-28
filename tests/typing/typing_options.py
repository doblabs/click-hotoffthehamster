"""From https://click.palletsprojects.com/en/8.1.x/quickstart/#adding-parameters"""
from typing_extensions import assert_type

import click_hotoffthehamster


@click_hotoffthehamster.command()
@click_hotoffthehamster.option("--count", default=1, help="number of greetings")
@click_hotoffthehamster.argument("name")
def hello(count: int, name: str) -> None:
    for _ in range(count):
        click_hotoffthehamster.echo(f"Hello {name}!")


assert_type(hello, click_hotoffthehamster.Command)
