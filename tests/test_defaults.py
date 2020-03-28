import click_hotoffthehamster


def test_basic_defaults(runner):
    @click_hotoffthehamster.command()
    @click_hotoffthehamster.option("--foo", default=42, type=click_hotoffthehamster.FLOAT)
    def cli(foo):
        assert type(foo) is float
        click_hotoffthehamster.echo(f"FOO:[{foo}]")

    result = runner.invoke(cli, [])
    assert not result.exception
    assert "FOO:[42.0]" in result.output


def test_multiple_defaults(runner):
    @click_hotoffthehamster.command()
    @click_hotoffthehamster.option("--foo", default=[23, 42], type=click_hotoffthehamster.FLOAT, multiple=True)
    def cli(foo):
        for item in foo:
            assert type(item) is float
            click_hotoffthehamster.echo(item)

    result = runner.invoke(cli, [])
    assert not result.exception
    assert result.output.splitlines() == ["23.0", "42.0"]


def test_nargs_plus_multiple(runner):
    @click_hotoffthehamster.command()
    @click_hotoffthehamster.option(
        "--arg", default=((1, 2), (3, 4)), nargs=2, multiple=True, type=click_hotoffthehamster.INT
    )
    def cli(arg):
        for a, b in arg:
            click_hotoffthehamster.echo(f"<{a:d}|{b:d}>")

    result = runner.invoke(cli, [])
    assert not result.exception
    assert result.output.splitlines() == ["<1|2>", "<3|4>"]


def test_multiple_flag_default(runner):
    """Default default for flags when multiple=True should be empty tuple."""

    @click_hotoffthehamster.command
    # flag due to secondary token
    @click_hotoffthehamster.option("-y/-n", multiple=True)
    # flag due to is_flag
    @click_hotoffthehamster.option("-f", is_flag=True, multiple=True)
    # flag due to flag_value
    @click_hotoffthehamster.option("-v", "v", flag_value=1, multiple=True)
    @click_hotoffthehamster.option("-q", "v", flag_value=-1, multiple=True)
    def cli(y, f, v):
        return y, f, v

    result = runner.invoke(cli, standalone_mode=False)
    assert result.return_value == ((), (), ())

    result = runner.invoke(cli, ["-y", "-n", "-f", "-v", "-q"], standalone_mode=False)
    assert result.return_value == ((True, False), (True,), (1, -1))
