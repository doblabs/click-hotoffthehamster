from typing_extensions import assert_type

import click_hotoffthehamster


@click_hotoffthehamster.group(context_settings={})
def hello() -> None:
    pass


assert_type(hello, click_hotoffthehamster.Group)
