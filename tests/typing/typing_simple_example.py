"""The simple example from https://github.com/pallets/click#a-simple-example."""
from typing_extensions import assert_type

import click_hotoffthehamster


@click_hotoffthehamster.command()
@click_hotoffthehamster.option("--count", default=1, help="Number of greetings.")
@click_hotoffthehamster.option(
    "--name", prompt="Your name", help="The person to greet."
)
def hello(count: int, name: str) -> None:
    """Simple program that greets NAME for a total of COUNT times."""
    for _ in range(count):
        click_hotoffthehamster.echo(f"Hello, {name}!")


assert_type(hello, click_hotoffthehamster.Command)
