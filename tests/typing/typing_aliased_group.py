"""Example from https://click.palletsprojects.com/en/8.1.x/advanced/#command-aliases"""
from __future__ import annotations

from typing_extensions import assert_type

import click_hotoffthehamster


class AliasedGroup(click_hotoffthehamster.Group):
    def get_command(self, ctx: click_hotoffthehamster.Context, cmd_name: str) -> click_hotoffthehamster.Command | None:
        rv = click_hotoffthehamster.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx) if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click_hotoffthehamster.Group.get_command(self, ctx, matches[0])
        ctx.fail(f"Too many matches: {', '.join(sorted(matches))}")

    def resolve_command(
        self, ctx: click_hotoffthehamster.Context, args: list[str]
    ) -> tuple[str | None, click_hotoffthehamster.Command, list[str]]:
        # always return the full command name
        _, cmd, args = super().resolve_command(ctx, args)
        assert cmd is not None
        return cmd.name, cmd, args


@click_hotoffthehamster.command(cls=AliasedGroup)
def cli() -> None:
    pass


assert_type(cli, AliasedGroup)


@cli.command()
def push() -> None:
    pass


@cli.command()
def pop() -> None:
    pass
