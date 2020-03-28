import re

import pytest

import click_hotoffthehamster


def test_other_command_invoke(runner):
    @click_hotoffthehamster.command()
    @click_hotoffthehamster.pass_context
    def cli(ctx):
        return ctx.invoke(other_cmd, arg=42)

    @click_hotoffthehamster.command()
    @click_hotoffthehamster.argument("arg", type=click_hotoffthehamster.INT)
    def other_cmd(arg):
        click_hotoffthehamster.echo(arg)

    result = runner.invoke(cli, [])
    assert not result.exception
    assert result.output == "42\n"


def test_other_command_forward(runner):
    cli = click_hotoffthehamster.Group()

    @cli.command()
    @click_hotoffthehamster.option("--count", default=1)
    def test(count):
        click_hotoffthehamster.echo(f"Count: {count:d}")

    @cli.command()
    @click_hotoffthehamster.option("--count", default=1)
    @click_hotoffthehamster.pass_context
    def dist(ctx, count):
        ctx.forward(test)
        ctx.invoke(test, count=42)

    result = runner.invoke(cli, ["dist"])
    assert not result.exception
    assert result.output == "Count: 1\nCount: 42\n"


def test_forwarded_params_consistency(runner):
    cli = click_hotoffthehamster.Group()

    @cli.command()
    @click_hotoffthehamster.option("-a")
    @click_hotoffthehamster.pass_context
    def first(ctx, **kwargs):
        click_hotoffthehamster.echo(f"{ctx.params}")

    @cli.command()
    @click_hotoffthehamster.option("-a")
    @click_hotoffthehamster.option("-b")
    @click_hotoffthehamster.pass_context
    def second(ctx, **kwargs):
        click_hotoffthehamster.echo(f"{ctx.params}")
        ctx.forward(first)

    result = runner.invoke(cli, ["second", "-a", "foo", "-b", "bar"])
    assert not result.exception
    assert result.output == "{'a': 'foo', 'b': 'bar'}\n{'a': 'foo', 'b': 'bar'}\n"


def test_auto_shorthelp(runner):
    @click_hotoffthehamster.group()
    def cli():
        pass

    @cli.command()
    def short():
        """This is a short text."""

    @cli.command()
    def special_chars():
        """Login and store the token in ~/.netrc."""

    @cli.command()
    def long():
        """This is a long text that is too long to show as short help
        and will be truncated instead."""

    result = runner.invoke(cli, ["--help"])
    assert (
        re.search(
            r"Usage: cli \[OPTIONS\] COMMAND \[ARGS\]\.\.\.\n\n\s*"
            r"Options:\n\s+"
            r"--help\s+Show this message and exit\.\n\n\s*"
            r"Commands:\n\s+"
            r"long\s+This is a long text that is too long to show as short help"
            r"\.\.\.\n\s+"
            r"short\s+This is a short text\.\n\s+"
            r"special-chars\s+Login and store the token in ~/.netrc\.\s*",
            result.output,
        )
        is not None
    )


def test_no_args_is_help(runner):
    @click_hotoffthehamster.command(no_args_is_help=True)
    def cli():
        pass

    result = runner.invoke(cli, [])
    assert result.exit_code == 0
    assert "Show this message and exit." in result.output


def test_default_maps(runner):
    @click_hotoffthehamster.group()
    def cli():
        pass

    @cli.command()
    @click_hotoffthehamster.option("--name", default="normal")
    def foo(name):
        click_hotoffthehamster.echo(name)

    result = runner.invoke(cli, ["foo"], default_map={"foo": {"name": "changed"}})

    assert not result.exception
    assert result.output == "changed\n"


@pytest.mark.parametrize(
    ("args", "exit_code", "expect"),
    [
        (["obj1"], 2, "Error: Missing command."),
        (["obj1", "--help"], 0, "Show this message and exit."),
        (["obj1", "move"], 0, "obj=obj1\nmove\n"),
        ([], 0, "Show this message and exit."),
    ],
)
def test_group_with_args(runner, args, exit_code, expect):
    @click_hotoffthehamster.group()
    @click_hotoffthehamster.argument("obj")
    def cli(obj):
        click_hotoffthehamster.echo(f"obj={obj}")

    @cli.command()
    def move():
        click_hotoffthehamster.echo("move")

    result = runner.invoke(cli, args)
    assert result.exit_code == exit_code
    assert expect in result.output


def test_custom_parser(runner):
    import optparse

    @click_hotoffthehamster.group()
    def cli():
        pass

    class OptParseCommand(click_hotoffthehamster.Command):
        def __init__(self, name, parser, callback):
            super().__init__(name)
            self.parser = parser
            self.callback = callback

        def parse_args(self, ctx, args):
            try:
                opts, args = parser.parse_args(args)
            except Exception as e:
                ctx.fail(str(e))
            ctx.args = args
            ctx.params = vars(opts)

        def get_usage(self, ctx):
            return self.parser.get_usage()

        def get_help(self, ctx):
            return self.parser.format_help()

        def invoke(self, ctx):
            ctx.invoke(self.callback, ctx.args, **ctx.params)

    parser = optparse.OptionParser(usage="Usage: foo test [OPTIONS]")
    parser.add_option(
        "-f", "--file", dest="filename", help="write report to FILE", metavar="FILE"
    )
    parser.add_option(
        "-q",
        "--quiet",
        action="store_false",
        dest="verbose",
        default=True,
        help="don't print status messages to stdout",
    )

    def test_callback(args, filename, verbose):
        click_hotoffthehamster.echo(" ".join(args))
        click_hotoffthehamster.echo(filename)
        click_hotoffthehamster.echo(verbose)

    cli.add_command(OptParseCommand("test", parser, test_callback))

    result = runner.invoke(cli, ["test", "-f", "f.txt", "-q", "q1.txt", "q2.txt"])
    assert result.exception is None
    assert result.output.splitlines() == ["q1.txt q2.txt", "f.txt", "False"]

    result = runner.invoke(cli, ["test", "--help"])
    assert result.exception is None
    assert result.output.splitlines() == [
        "Usage: foo test [OPTIONS]",
        "",
        "Options:",
        "  -h, --help            show this help message and exit",
        "  -f FILE, --file=FILE  write report to FILE",
        "  -q, --quiet           don't print status messages to stdout",
    ]


def test_object_propagation(runner):
    for chain in False, True:

        @click_hotoffthehamster.group(chain=chain)
        @click_hotoffthehamster.option("--debug/--no-debug", default=False)
        @click_hotoffthehamster.pass_context
        def cli(ctx, debug):
            if ctx.obj is None:
                ctx.obj = {}
            ctx.obj["DEBUG"] = debug

        @cli.command()
        @click_hotoffthehamster.pass_context
        def sync(ctx):
            click_hotoffthehamster.echo(f"Debug is {'on' if ctx.obj['DEBUG'] else 'off'}")

        result = runner.invoke(cli, ["sync"])
        assert result.exception is None
        assert result.output == "Debug is off\n"


def test_other_command_invoke_with_defaults(runner):
    @click_hotoffthehamster.command()
    @click_hotoffthehamster.pass_context
    def cli(ctx):
        return ctx.invoke(other_cmd)

    @click_hotoffthehamster.command()
    @click_hotoffthehamster.option("-a", type=click_hotoffthehamster.INT, default=42)
    @click_hotoffthehamster.option("-b", type=click_hotoffthehamster.INT, default="15")
    @click_hotoffthehamster.option("-c", multiple=True)
    @click_hotoffthehamster.pass_context
    def other_cmd(ctx, a, b, c):
        return ctx.info_name, a, b, c

    result = runner.invoke(cli, standalone_mode=False)
    # invoke should type cast default values, str becomes int, empty
    # multiple should be empty tuple instead of None
    assert result.return_value == ("other", 42, 15, ())


def test_invoked_subcommand(runner):
    @click_hotoffthehamster.group(invoke_without_command=True)
    @click_hotoffthehamster.pass_context
    def cli(ctx):
        if ctx.invoked_subcommand is None:
            click_hotoffthehamster.echo("no subcommand, use default")
            ctx.invoke(sync)
        else:
            click_hotoffthehamster.echo("invoke subcommand")

    @cli.command()
    def sync():
        click_hotoffthehamster.echo("in subcommand")

    result = runner.invoke(cli, ["sync"])
    assert not result.exception
    assert result.output == "invoke subcommand\nin subcommand\n"

    result = runner.invoke(cli)
    assert not result.exception
    assert result.output == "no subcommand, use default\nin subcommand\n"


def test_aliased_command_canonical_name(runner):
    class AliasedGroup(click_hotoffthehamster.Group):
        def get_command(self, ctx, cmd_name):
            return push

        def resolve_command(self, ctx, args):
            _, command, args = super().resolve_command(ctx, args)
            return command.name, command, args

    cli = AliasedGroup()

    @cli.command()
    def push():
        click_hotoffthehamster.echo("push command")

    result = runner.invoke(cli, ["pu", "--help"])
    assert not result.exception
    assert result.output.startswith("Usage: root push [OPTIONS]")


def test_group_add_command_name(runner):
    cli = click_hotoffthehamster.Group("cli")
    cmd = click_hotoffthehamster.Command("a", params=[click_hotoffthehamster.Option(["-x"], required=True)])
    cli.add_command(cmd, "b")
    # Check that the command is accessed through the registered name,
    # not the original name.
    result = runner.invoke(cli, ["b"], default_map={"b": {"x": 3}})
    assert result.exit_code == 0


def test_unprocessed_options(runner):
    @click_hotoffthehamster.command(context_settings=dict(ignore_unknown_options=True))
    @click_hotoffthehamster.argument("args", nargs=-1, type=click_hotoffthehamster.UNPROCESSED)
    @click_hotoffthehamster.option("--verbose", "-v", count=True)
    def cli(verbose, args):
        click_hotoffthehamster.echo(f"Verbosity: {verbose}")
        click_hotoffthehamster.echo(f"Args: {'|'.join(args)}")

    result = runner.invoke(cli, ["-foo", "-vvvvx", "--muhaha", "x", "y", "-x"])
    assert not result.exception
    assert result.output.splitlines() == [
        "Verbosity: 4",
        "Args: -foo|-x|--muhaha|x|y|-x",
    ]


@pytest.mark.parametrize("doc", ["CLI HELP", None])
def test_deprecated_in_help_messages(runner, doc):
    @click_hotoffthehamster.command(deprecated=True, help=doc)
    def cli():
        pass

    result = runner.invoke(cli, ["--help"])
    assert "(Deprecated)" in result.output


def test_deprecated_in_invocation(runner):
    @click_hotoffthehamster.command(deprecated=True)
    def deprecated_cmd():
        pass

    result = runner.invoke(deprecated_cmd)
    assert "DeprecationWarning:" in result.output


def test_command_parse_args_collects_option_prefixes():
    @click_hotoffthehamster.command()
    @click_hotoffthehamster.option("+p", is_flag=True)
    @click_hotoffthehamster.option("!e", is_flag=True)
    def test(p, e):
        pass

    ctx = click_hotoffthehamster.Context(test)
    test.parse_args(ctx, [])

    assert ctx._opt_prefixes == {"-", "--", "+", "!"}


def test_group_parse_args_collects_base_option_prefixes():
    @click_hotoffthehamster.group()
    @click_hotoffthehamster.option("~t", is_flag=True)
    def group(t):
        pass

    @group.command()
    @click_hotoffthehamster.option("+p", is_flag=True)
    def command1(p):
        pass

    @group.command()
    @click_hotoffthehamster.option("!e", is_flag=True)
    def command2(e):
        pass

    ctx = click_hotoffthehamster.Context(group)
    group.parse_args(ctx, ["command1", "+p"])

    assert ctx._opt_prefixes == {"-", "--", "~"}


def test_group_invoke_collects_used_option_prefixes(runner):
    opt_prefixes = set()

    @click_hotoffthehamster.group()
    @click_hotoffthehamster.option("~t", is_flag=True)
    def group(t):
        pass

    @group.command()
    @click_hotoffthehamster.option("+p", is_flag=True)
    @click_hotoffthehamster.pass_context
    def command1(ctx, p):
        nonlocal opt_prefixes
        opt_prefixes = ctx._opt_prefixes

    @group.command()
    @click_hotoffthehamster.option("!e", is_flag=True)
    def command2(e):
        pass

    runner.invoke(group, ["command1"])
    assert opt_prefixes == {"-", "--", "~", "+"}


@pytest.mark.parametrize("exc", (EOFError, KeyboardInterrupt))
def test_abort_exceptions_with_disabled_standalone_mode(runner, exc):
    @click_hotoffthehamster.command()
    def cli():
        raise exc("catch me!")

    rv = runner.invoke(cli, standalone_mode=False)
    assert rv.exit_code == 1
    assert isinstance(rv.exception.__cause__, exc)
    assert rv.exception.__cause__.args == ("catch me!",)
