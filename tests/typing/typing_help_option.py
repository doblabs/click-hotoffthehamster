from typing_extensions import assert_type

import click_hotoffthehamster


@click_hotoffthehamster.command()
@click_hotoffthehamster.help_option("-h", "--help")
def hello() -> None:
    """Simple program that greets NAME for a total of COUNT times."""
    click_hotoffthehamster.echo("Hello!")


assert_type(hello, click_hotoffthehamster.Command)
