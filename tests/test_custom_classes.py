import click_hotoffthehamster


def test_command_context_class():
    """A command with a custom ``context_class`` should produce a
    context using that type.
    """

    class CustomContext(click_hotoffthehamster.Context):
        pass

    class CustomCommand(click_hotoffthehamster.Command):
        context_class = CustomContext

    command = CustomCommand("test")
    context = command.make_context("test", [])
    assert isinstance(context, CustomContext)


def test_context_invoke_type(runner):
    """A command invoked from a custom context should have a new
    context with the same type.
    """

    class CustomContext(click_hotoffthehamster.Context):
        pass

    class CustomCommand(click_hotoffthehamster.Command):
        context_class = CustomContext

    @click_hotoffthehamster.command()
    @click_hotoffthehamster.argument("first_id", type=int)
    @click_hotoffthehamster.pass_context
    def second(ctx, first_id):
        assert isinstance(ctx, CustomContext)
        assert id(ctx) != first_id

    @click_hotoffthehamster.command(cls=CustomCommand)
    @click_hotoffthehamster.pass_context
    def first(ctx):
        assert isinstance(ctx, CustomContext)
        ctx.invoke(second, first_id=id(ctx))

    assert not runner.invoke(first).exception


def test_context_formatter_class():
    """A context with a custom ``formatter_class`` should format help
    using that type.
    """

    class CustomFormatter(click_hotoffthehamster.HelpFormatter):
        def write_heading(self, heading):
            heading = click_hotoffthehamster.style(heading, fg="yellow")
            return super().write_heading(heading)

    class CustomContext(click_hotoffthehamster.Context):
        formatter_class = CustomFormatter

    context = CustomContext(
        click_hotoffthehamster.Command("test", params=[click_hotoffthehamster.Option(["--value"])]), color=True
    )
    assert "\x1b[33mOptions\x1b[0m:" in context.get_help()


def test_group_command_class(runner):
    """A group with a custom ``command_class`` should create subcommands
    of that type by default.
    """

    class CustomCommand(click_hotoffthehamster.Command):
        pass

    class CustomGroup(click_hotoffthehamster.Group):
        command_class = CustomCommand

    group = CustomGroup()
    subcommand = group.command()(lambda: None)
    assert type(subcommand) is CustomCommand
    subcommand = group.command(cls=click_hotoffthehamster.Command)(lambda: None)
    assert type(subcommand) is click_hotoffthehamster.Command


def test_group_group_class(runner):
    """A group with a custom ``group_class`` should create subgroups
    of that type by default.
    """

    class CustomSubGroup(click_hotoffthehamster.Group):
        pass

    class CustomGroup(click_hotoffthehamster.Group):
        group_class = CustomSubGroup

    group = CustomGroup()
    subgroup = group.group()(lambda: None)
    assert type(subgroup) is CustomSubGroup
    subgroup = group.command(cls=click_hotoffthehamster.Group)(lambda: None)
    assert type(subgroup) is click_hotoffthehamster.Group


def test_group_group_class_self(runner):
    """A group with ``group_class = type`` should create subgroups of
    the same type as itself.
    """

    class CustomGroup(click_hotoffthehamster.Group):
        group_class = type

    group = CustomGroup()
    subgroup = group.group()(lambda: None)
    assert type(subgroup) is CustomGroup
