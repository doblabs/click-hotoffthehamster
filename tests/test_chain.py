import sys

import pytest

import click_hotoffthehamster


def debug():
    click_hotoffthehamster.echo(
        f"{sys._getframe(1).f_code.co_name}"
        f"={'|'.join(click_hotoffthehamster.get_current_context().args)}"
    )


def test_basic_chaining(runner):
    @click_hotoffthehamster.group(chain=True)
    def cli():
        pass

    @cli.command("sdist")
    def sdist():
        click_hotoffthehamster.echo("sdist called")

    @cli.command("bdist")
    def bdist():
        click_hotoffthehamster.echo("bdist called")

    result = runner.invoke(cli, ["bdist", "sdist", "bdist"])
    assert not result.exception
    assert result.output.splitlines() == [
        "bdist called",
        "sdist called",
        "bdist called",
    ]


@pytest.mark.parametrize(
    ("args", "expect"),
    [
        (["--help"], "COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]..."),
        (["--help"], "ROOT HELP"),
        (["sdist", "--help"], "SDIST HELP"),
        (["bdist", "--help"], "BDIST HELP"),
        (["bdist", "sdist", "--help"], "SDIST HELP"),
    ],
)
def test_chaining_help(runner, args, expect):
    @click_hotoffthehamster.group(chain=True)
    def cli():
        """ROOT HELP"""
        pass

    @cli.command("sdist")
    def sdist():
        """SDIST HELP"""
        click_hotoffthehamster.echo("sdist called")

    @cli.command("bdist")
    def bdist():
        """BDIST HELP"""
        click_hotoffthehamster.echo("bdist called")

    result = runner.invoke(cli, args)
    assert not result.exception
    assert expect in result.output


def test_chaining_with_options(runner):
    @click_hotoffthehamster.group(chain=True)
    def cli():
        pass

    @cli.command("sdist")
    @click_hotoffthehamster.option("--format")
    def sdist(format):
        click_hotoffthehamster.echo(f"sdist called {format}")

    @cli.command("bdist")
    @click_hotoffthehamster.option("--format")
    def bdist(format):
        click_hotoffthehamster.echo(f"bdist called {format}")

    result = runner.invoke(cli, ["bdist", "--format=1", "sdist", "--format=2"])
    assert not result.exception
    assert result.output.splitlines() == ["bdist called 1", "sdist called 2"]


@pytest.mark.parametrize(("chain", "expect"), [(False, "1"), (True, "[]")])
def test_no_command_result_callback(runner, chain, expect):
    """When a group has ``invoke_without_command=True``, the result
    callback is always invoked. A regular group invokes it with
    its return value, a chained group with ``[]``.
    """

    @click_hotoffthehamster.group(invoke_without_command=True, chain=chain)
    def cli():
        return 1

    @cli.result_callback()
    def process_result(result):
        click_hotoffthehamster.echo(result, nl=False)

    result = runner.invoke(cli, [])
    assert result.output == expect


def test_chaining_with_arguments(runner):
    @click_hotoffthehamster.group(chain=True)
    def cli():
        pass

    @cli.command("sdist")
    @click_hotoffthehamster.argument("format")
    def sdist(format):
        click_hotoffthehamster.echo(f"sdist called {format}")

    @cli.command("bdist")
    @click_hotoffthehamster.argument("format")
    def bdist(format):
        click_hotoffthehamster.echo(f"bdist called {format}")

    result = runner.invoke(cli, ["bdist", "1", "sdist", "2"])
    assert not result.exception
    assert result.output.splitlines() == ["bdist called 1", "sdist called 2"]


@pytest.mark.parametrize(
    ("args", "input", "expect"),
    [
        (["-f", "-"], "foo\nbar", ["foo", "bar"]),
        (["-f", "-", "strip"], "foo \n bar", ["foo", "bar"]),
        (["-f", "-", "strip", "uppercase"], "foo \n bar", ["FOO", "BAR"]),
    ],
)
def test_pipeline(runner, args, input, expect):
    @click_hotoffthehamster.group(chain=True, invoke_without_command=True)
    @click_hotoffthehamster.option("-f", type=click_hotoffthehamster.File("r"))
    def cli(f):
        pass

    @cli.result_callback()
    def process_pipeline(processors, f):
        iterator = (x.rstrip("\r\n") for x in f)
        for processor in processors:
            iterator = processor(iterator)
        for item in iterator:
            click_hotoffthehamster.echo(item)

    @cli.command("uppercase")
    def make_uppercase():
        def processor(iterator):
            for line in iterator:
                yield line.upper()

        return processor

    @cli.command("strip")
    def make_strip():
        def processor(iterator):
            for line in iterator:
                yield line.strip()

        return processor

    result = runner.invoke(cli, args, input=input)
    assert not result.exception
    assert result.output.splitlines() == expect


def test_args_and_chain(runner):
    @click_hotoffthehamster.group(chain=True)
    def cli():
        debug()

    @cli.command()
    def a():
        debug()

    @cli.command()
    def b():
        debug()

    @cli.command()
    def c():
        debug()

    result = runner.invoke(cli, ["a", "b", "c"])
    assert not result.exception
    assert result.output.splitlines() == ["cli=", "a=", "b=", "c="]


def test_group_arg_behavior(runner):
    with pytest.raises(RuntimeError):

        @click_hotoffthehamster.group(chain=True)
        @click_hotoffthehamster.argument("forbidden", required=False)
        def bad_cli():
            pass

    with pytest.raises(RuntimeError):

        @click_hotoffthehamster.group(chain=True)
        @click_hotoffthehamster.argument("forbidden", nargs=-1)
        def bad_cli2():
            pass

    @click_hotoffthehamster.group(chain=True)
    @click_hotoffthehamster.argument("arg")
    def cli(arg):
        click_hotoffthehamster.echo(f"cli:{arg}")

    @cli.command()
    def a():
        click_hotoffthehamster.echo("a")

    result = runner.invoke(cli, ["foo", "a"])
    assert not result.exception
    assert result.output.splitlines() == ["cli:foo", "a"]


@pytest.mark.xfail
def test_group_chaining(runner):
    @click_hotoffthehamster.group(chain=True)
    def cli():
        debug()

    @cli.group()
    def l1a():
        debug()

    @l1a.command()
    def l2a():
        debug()

    @l1a.command()
    def l2b():
        debug()

    @cli.command()
    def l1b():
        debug()

    result = runner.invoke(cli, ["l1a", "l2a", "l1b"])
    assert not result.exception
    assert result.output.splitlines() == ["cli=", "l1a=", "l2a=", "l1b="]
