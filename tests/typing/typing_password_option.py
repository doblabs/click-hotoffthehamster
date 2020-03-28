import codecs

from typing_extensions import assert_type

import click_hotoffthehamster


@click_hotoffthehamster.command()
@click_hotoffthehamster.password_option()
def encrypt(password: str) -> None:
    click_hotoffthehamster.echo(f"encoded: to {codecs.encode(password, 'rot13')}")


assert_type(encrypt, click_hotoffthehamster.Command)
