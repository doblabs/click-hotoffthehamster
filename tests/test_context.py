from contextlib import contextmanager

import pytest

import click_hotoffthehamster
from click_hotoffthehamster.core import ParameterSource
from click_hotoffthehamster.decorators import pass_meta_key


def test_ensure_context_objects(runner):
    class Foo:
        def __init__(self):
            self.title = "default"

    pass_foo = click_hotoffthehamster.make_pass_decorator(Foo, ensure=True)

    @click_hotoffthehamster.group()
    @pass_foo
    def cli(foo):
        pass

    @cli.command()
    @pass_foo
    def test(foo):
        click_hotoffthehamster.echo(foo.title)

    result = runner.invoke(cli, ["test"])
    assert not result.exception
    assert result.output == "default\n"


def test_get_context_objects(runner):
    class Foo:
        def __init__(self):
            self.title = "default"

    pass_foo = click_hotoffthehamster.make_pass_decorator(Foo, ensure=True)

    @click_hotoffthehamster.group()
    @click_hotoffthehamster.pass_context
    def cli(ctx):
        ctx.obj = Foo()
        ctx.obj.title = "test"

    @cli.command()
    @pass_foo
    def test(foo):
        click_hotoffthehamster.echo(foo.title)

    result = runner.invoke(cli, ["test"])
    assert not result.exception
    assert result.output == "test\n"


def test_get_context_objects_no_ensuring(runner):
    class Foo:
        def __init__(self):
            self.title = "default"

    pass_foo = click_hotoffthehamster.make_pass_decorator(Foo)

    @click_hotoffthehamster.group()
    @click_hotoffthehamster.pass_context
    def cli(ctx):
        ctx.obj = Foo()
        ctx.obj.title = "test"

    @cli.command()
    @pass_foo
    def test(foo):
        click_hotoffthehamster.echo(foo.title)

    result = runner.invoke(cli, ["test"])
    assert not result.exception
    assert result.output == "test\n"


def test_get_context_objects_missing(runner):
    class Foo:
        pass

    pass_foo = click_hotoffthehamster.make_pass_decorator(Foo)

    @click_hotoffthehamster.group()
    @click_hotoffthehamster.pass_context
    def cli(ctx):
        pass

    @cli.command()
    @pass_foo
    def test(foo):
        click_hotoffthehamster.echo(foo.title)

    result = runner.invoke(cli, ["test"])
    assert result.exception is not None
    assert isinstance(result.exception, RuntimeError)
    assert (
        "Managed to invoke callback without a context object of type"
        " 'Foo' existing" in str(result.exception)
    )


def test_multi_enter(runner):
    called = []

    @click_hotoffthehamster.command()
    @click_hotoffthehamster.pass_context
    def cli(ctx):
        def callback():
            called.append(True)

        ctx.call_on_close(callback)

        with ctx:
            pass
        assert not called

    result = runner.invoke(cli, [])
    assert result.exception is None
    assert called == [True]


def test_global_context_object(runner):
    @click_hotoffthehamster.command()
    @click_hotoffthehamster.pass_context
    def cli(ctx):
        assert click_hotoffthehamster.get_current_context() is ctx
        ctx.obj = "FOOBAR"
        assert click_hotoffthehamster.get_current_context().obj == "FOOBAR"

    assert click_hotoffthehamster.get_current_context(silent=True) is None
    runner.invoke(cli, [], catch_exceptions=False)
    assert click_hotoffthehamster.get_current_context(silent=True) is None


def test_context_meta(runner):
    LANG_KEY = f"{__name__}.lang"

    def set_language(value):
        click_hotoffthehamster.get_current_context().meta[LANG_KEY] = value

    def get_language():
        return click_hotoffthehamster.get_current_context().meta.get(LANG_KEY, "en_US")

    @click_hotoffthehamster.command()
    @click_hotoffthehamster.pass_context
    def cli(ctx):
        assert get_language() == "en_US"
        set_language("de_DE")
        assert get_language() == "de_DE"

    runner.invoke(cli, [], catch_exceptions=False)


def test_make_pass_meta_decorator(runner):
    @click_hotoffthehamster.group()
    @click_hotoffthehamster.pass_context
    def cli(ctx):
        ctx.meta["value"] = "good"

    @cli.command()
    @pass_meta_key("value")
    def show(value):
        return value

    result = runner.invoke(cli, ["show"], standalone_mode=False)
    assert result.return_value == "good"


def test_make_pass_meta_decorator_doc():
    pass_value = pass_meta_key("value")
    assert "the 'value' key from :attr:`click_hotoffthehamster.Context.meta`" in pass_value.__doc__
    pass_value = pass_meta_key("value", doc_description="the test value")
    assert "passes the test value" in pass_value.__doc__


def test_context_pushing():
    rv = []

    @click_hotoffthehamster.command()
    def cli():
        pass

    ctx = click_hotoffthehamster.Context(cli)

    @ctx.call_on_close
    def test_callback():
        rv.append(42)

    with ctx.scope(cleanup=False):
        # Internal
        assert ctx._depth == 2

    assert rv == []

    with ctx.scope():
        # Internal
        assert ctx._depth == 1

    assert rv == [42]


def test_pass_obj(runner):
    @click_hotoffthehamster.group()
    @click_hotoffthehamster.pass_context
    def cli(ctx):
        ctx.obj = "test"

    @cli.command()
    @click_hotoffthehamster.pass_obj
    def test(obj):
        click_hotoffthehamster.echo(obj)

    result = runner.invoke(cli, ["test"])
    assert not result.exception
    assert result.output == "test\n"


def test_close_before_pop(runner):
    called = []

    @click_hotoffthehamster.command()
    @click_hotoffthehamster.pass_context
    def cli(ctx):
        ctx.obj = "test"

        @ctx.call_on_close
        def foo():
            assert click_hotoffthehamster.get_current_context().obj == "test"
            called.append(True)

        click_hotoffthehamster.echo("aha!")

    result = runner.invoke(cli, [])
    assert not result.exception
    assert result.output == "aha!\n"
    assert called == [True]


def test_with_resource():
    @contextmanager
    def manager():
        val = [1]
        yield val
        val[0] = 0

    ctx = click_hotoffthehamster.Context(click_hotoffthehamster.Command("test"))

    with ctx.scope():
        rv = ctx.with_resource(manager())
        assert rv[0] == 1

    assert rv == [0]


def test_make_pass_decorator_args(runner):
    """
    Test to check that make_pass_decorator doesn't consume arguments based on
    invocation order.
    """

    class Foo:
        title = "foocmd"

    pass_foo = click_hotoffthehamster.make_pass_decorator(Foo)

    @click_hotoffthehamster.group()
    @click_hotoffthehamster.pass_context
    def cli(ctx):
        ctx.obj = Foo()

    @cli.command()
    @click_hotoffthehamster.pass_context
    @pass_foo
    def test1(foo, ctx):
        click_hotoffthehamster.echo(foo.title)

    @cli.command()
    @pass_foo
    @click_hotoffthehamster.pass_context
    def test2(ctx, foo):
        click_hotoffthehamster.echo(foo.title)

    result = runner.invoke(cli, ["test1"])
    assert not result.exception
    assert result.output == "foocmd\n"

    result = runner.invoke(cli, ["test2"])
    assert not result.exception
    assert result.output == "foocmd\n"


def test_propagate_show_default_setting(runner):
    """A context's ``show_default`` setting defaults to the value from
    the parent context.
    """
    group = click_hotoffthehamster.Group(
        commands={
            "sub": click_hotoffthehamster.Command("sub", params=[click_hotoffthehamster.Option(["-a"], default="a")]),
        },
        context_settings={"show_default": True},
    )
    result = runner.invoke(group, ["sub", "--help"])
    assert "[default: a]" in result.output


def test_exit_not_standalone():
    @click_hotoffthehamster.command()
    @click_hotoffthehamster.pass_context
    def cli(ctx):
        ctx.exit(1)

    assert cli.main([], "test_exit_not_standalone", standalone_mode=False) == 1

    @click_hotoffthehamster.command()
    @click_hotoffthehamster.pass_context
    def cli(ctx):
        ctx.exit(0)

    assert cli.main([], "test_exit_not_standalone", standalone_mode=False) == 0


@pytest.mark.parametrize(
    ("option_args", "invoke_args", "expect"),
    [
        pytest.param({}, {}, ParameterSource.DEFAULT, id="default"),
        pytest.param(
            {},
            {"default_map": {"option": 1}},
            ParameterSource.DEFAULT_MAP,
            id="default_map",
        ),
        pytest.param(
            {},
            {"args": ["-o", "1"]},
            ParameterSource.COMMANDLINE,
            id="commandline short",
        ),
        pytest.param(
            {},
            {"args": ["--option", "1"]},
            ParameterSource.COMMANDLINE,
            id="commandline long",
        ),
        pytest.param(
            {},
            {"auto_envvar_prefix": "TEST", "env": {"TEST_OPTION": "1"}},
            ParameterSource.ENVIRONMENT,
            id="environment auto",
        ),
        pytest.param(
            {"envvar": "NAME"},
            {"env": {"NAME": "1"}},
            ParameterSource.ENVIRONMENT,
            id="environment manual",
        ),
    ],
)
def test_parameter_source(runner, option_args, invoke_args, expect):
    @click_hotoffthehamster.command()
    @click_hotoffthehamster.pass_context
    @click_hotoffthehamster.option("-o", "--option", default=1, **option_args)
    def cli(ctx, option):
        return ctx.get_parameter_source("option")

    rv = runner.invoke(cli, standalone_mode=False, **invoke_args)
    assert rv.return_value == expect


def test_propagate_opt_prefixes():
    parent = click_hotoffthehamster.Context(click_hotoffthehamster.Command("test"))
    parent._opt_prefixes = {"-", "--", "!"}
    ctx = click_hotoffthehamster.Context(click_hotoffthehamster.Command("test2"), parent=parent)

    assert ctx._opt_prefixes == {"-", "--", "!"}
