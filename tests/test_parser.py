import pytest

import click_hotoffthehamster
from click_hotoffthehamster.parser import _OptionParser
from click_hotoffthehamster.shell_completion import split_arg_string


@pytest.mark.parametrize(
    ("value", "expect"),
    [
        ("cli a b c", ["cli", "a", "b", "c"]),
        ("cli 'my file", ["cli", "my file"]),
        ("cli 'my file'", ["cli", "my file"]),
        ("cli my\\", ["cli", "my"]),
        ("cli my\\ file", ["cli", "my file"]),
    ],
)
def test_split_arg_string(value, expect):
    assert split_arg_string(value) == expect


def test_parser_default_prefixes():
    parser = _OptionParser()
    assert parser._opt_prefixes == {"-", "--"}


def test_parser_collects_prefixes():
    ctx = click_hotoffthehamster.Context(click_hotoffthehamster.Command("test"))
    parser = _OptionParser(ctx)
    click_hotoffthehamster.Option("+p", is_flag=True).add_to_parser(parser, ctx)
    click_hotoffthehamster.Option("!e", is_flag=True).add_to_parser(parser, ctx)
    assert parser._opt_prefixes == {"-", "--", "+", "!"}
