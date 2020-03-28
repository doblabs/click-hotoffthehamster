import pytest

import click_hotoffthehamster


def test_command_no_parens(runner):
    @click_hotoffthehamster.command
    def cli():
        click_hotoffthehamster.echo("hello")

    result = runner.invoke(cli)
    assert result.exception is None
    assert result.output == "hello\n"


def test_custom_command_no_parens(runner):
    class CustomCommand(click_hotoffthehamster.Command):
        pass

    class CustomGroup(click_hotoffthehamster.Group):
        command_class = CustomCommand

    @click_hotoffthehamster.group(cls=CustomGroup)
    def grp():
        pass

    @grp.command
    def cli():
        click_hotoffthehamster.echo("hello custom command class")

    result = runner.invoke(cli)
    assert result.exception is None
    assert result.output == "hello custom command class\n"


def test_group_no_parens(runner):
    @click_hotoffthehamster.group
    def grp():
        click_hotoffthehamster.echo("grp1")

    @grp.command
    def cmd1():
        click_hotoffthehamster.echo("cmd1")

    @grp.group
    def grp2():
        click_hotoffthehamster.echo("grp2")

    @grp2.command
    def cmd2():
        click_hotoffthehamster.echo("cmd2")

    result = runner.invoke(grp, ["cmd1"])
    assert result.exception is None
    assert result.output == "grp1\ncmd1\n"

    result = runner.invoke(grp, ["grp2", "cmd2"])
    assert result.exception is None
    assert result.output == "grp1\ngrp2\ncmd2\n"


def test_params_argument(runner):
    opt = click_hotoffthehamster.Argument(["a"])

    @click_hotoffthehamster.command(params=[opt])
    @click_hotoffthehamster.argument("b")
    def cli(a, b):
        click_hotoffthehamster.echo(f"{a} {b}")

    assert cli.params[0].name == "a"
    assert cli.params[1].name == "b"
    result = runner.invoke(cli, ["1", "2"])
    assert result.output == "1 2\n"


@pytest.mark.parametrize(
    "name",
    [
        "init_data",
        "init_data_command",
        "init_data_cmd",
        "init_data_group",
        "init_data_grp",
    ],
)
def test_generate_name(name: str) -> None:
    def f():
        pass

    f.__name__ = name
    f = click_hotoffthehamster.command(f)
    assert f.name == "init-data"
