import pytest

import click_hotoffthehamster.types

# Common (obj, expect) pairs used to construct multiple tests.
STRING_PARAM_TYPE = (click_hotoffthehamster.STRING, {"param_type": "String", "name": "text"})
INT_PARAM_TYPE = (click_hotoffthehamster.INT, {"param_type": "Int", "name": "integer"})
BOOL_PARAM_TYPE = (click_hotoffthehamster.BOOL, {"param_type": "Bool", "name": "boolean"})
HELP_OPTION = (
    None,
    {
        "name": "help",
        "param_type_name": "option",
        "opts": ["--help"],
        "secondary_opts": [],
        "type": BOOL_PARAM_TYPE[1],
        "required": False,
        "nargs": 1,
        "multiple": False,
        "default": False,
        "envvar": None,
        "help": "Show this message and exit.",
        "prompt": None,
        "is_flag": True,
        "flag_value": True,
        "count": False,
        "hidden": False,
    },
)
NAME_ARGUMENT = (
    click_hotoffthehamster.Argument(["name"]),
    {
        "name": "name",
        "param_type_name": "argument",
        "opts": ["name"],
        "secondary_opts": [],
        "type": STRING_PARAM_TYPE[1],
        "required": True,
        "nargs": 1,
        "multiple": False,
        "default": None,
        "envvar": None,
    },
)
NUMBER_OPTION = (
    click_hotoffthehamster.Option(["-c", "--count", "number"], default=1),
    {
        "name": "number",
        "param_type_name": "option",
        "opts": ["-c", "--count"],
        "secondary_opts": [],
        "type": INT_PARAM_TYPE[1],
        "required": False,
        "nargs": 1,
        "multiple": False,
        "default": 1,
        "envvar": None,
        "help": None,
        "prompt": None,
        "is_flag": False,
        "flag_value": False,
        "count": False,
        "hidden": False,
    },
)
HELLO_COMMAND = (
    click_hotoffthehamster.Command("hello", params=[NUMBER_OPTION[0]]),
    {
        "name": "hello",
        "params": [NUMBER_OPTION[1], HELP_OPTION[1]],
        "help": None,
        "epilog": None,
        "short_help": None,
        "hidden": False,
        "deprecated": False,
    },
)
HELLO_GROUP = (
    click_hotoffthehamster.Group("cli", [HELLO_COMMAND[0]]),
    {
        "name": "cli",
        "params": [HELP_OPTION[1]],
        "help": None,
        "epilog": None,
        "short_help": None,
        "hidden": False,
        "deprecated": False,
        "commands": {"hello": HELLO_COMMAND[1]},
        "chain": False,
    },
)


@pytest.mark.parametrize(
    ("obj", "expect"),
    [
        pytest.param(
            click_hotoffthehamster.types.FuncParamType(range),
            {"param_type": "Func", "name": "range", "func": range},
            id="Func ParamType",
        ),
        pytest.param(
            click_hotoffthehamster.UNPROCESSED,
            {"param_type": "Unprocessed", "name": "text"},
            id="UNPROCESSED ParamType",
        ),
        pytest.param(*STRING_PARAM_TYPE, id="STRING ParamType"),
        pytest.param(
            click_hotoffthehamster.Choice(["a", "b"]),
            {
                "param_type": "Choice",
                "name": "choice",
                "choices": ["a", "b"],
                "case_sensitive": True,
            },
            id="Choice ParamType",
        ),
        pytest.param(
            click_hotoffthehamster.DateTime(["%Y-%m-%d"]),
            {"param_type": "DateTime", "name": "datetime", "formats": ["%Y-%m-%d"]},
            id="DateTime ParamType",
        ),
        pytest.param(*INT_PARAM_TYPE, id="INT ParamType"),
        pytest.param(
            click_hotoffthehamster.IntRange(0, 10, clamp=True),
            {
                "param_type": "IntRange",
                "name": "integer range",
                "min": 0,
                "max": 10,
                "min_open": False,
                "max_open": False,
                "clamp": True,
            },
            id="IntRange ParamType",
        ),
        pytest.param(
            click_hotoffthehamster.FLOAT, {"param_type": "Float", "name": "float"}, id="FLOAT ParamType"
        ),
        pytest.param(
            click_hotoffthehamster.FloatRange(-0.5, 0.5),
            {
                "param_type": "FloatRange",
                "name": "float range",
                "min": -0.5,
                "max": 0.5,
                "min_open": False,
                "max_open": False,
                "clamp": False,
            },
            id="FloatRange ParamType",
        ),
        pytest.param(*BOOL_PARAM_TYPE, id="Bool ParamType"),
        pytest.param(
            click_hotoffthehamster.UUID, {"param_type": "UUID", "name": "uuid"}, id="UUID ParamType"
        ),
        pytest.param(
            click_hotoffthehamster.File(),
            {"param_type": "File", "name": "filename", "mode": "r", "encoding": None},
            id="File ParamType",
        ),
        pytest.param(
            click_hotoffthehamster.Path(),
            {
                "param_type": "Path",
                "name": "path",
                "exists": False,
                "file_okay": True,
                "dir_okay": True,
                "writable": False,
                "readable": True,
                "allow_dash": False,
            },
            id="Path ParamType",
        ),
        pytest.param(
            click_hotoffthehamster.Tuple((click_hotoffthehamster.STRING, click_hotoffthehamster.INT)),
            {
                "param_type": "Tuple",
                "name": "<text integer>",
                "types": [STRING_PARAM_TYPE[1], INT_PARAM_TYPE[1]],
            },
            id="Tuple ParamType",
        ),
        pytest.param(*NUMBER_OPTION, id="Option"),
        pytest.param(
            click_hotoffthehamster.Option(["--cache/--no-cache", "-c/-u"]),
            {
                "name": "cache",
                "param_type_name": "option",
                "opts": ["--cache", "-c"],
                "secondary_opts": ["--no-cache", "-u"],
                "type": BOOL_PARAM_TYPE[1],
                "required": False,
                "nargs": 1,
                "multiple": False,
                "default": False,
                "envvar": None,
                "help": None,
                "prompt": None,
                "is_flag": True,
                "flag_value": True,
                "count": False,
                "hidden": False,
            },
            id="Flag Option",
        ),
        pytest.param(*NAME_ARGUMENT, id="Argument"),
    ],
)
def test_parameter(obj, expect):
    out = obj.to_info_dict()
    assert out == expect


@pytest.mark.parametrize(
    ("obj", "expect"),
    [
        pytest.param(*HELLO_COMMAND, id="Command"),
        pytest.param(*HELLO_GROUP, id="Group"),
        pytest.param(
            click_hotoffthehamster.Group(
                "base",
                [click_hotoffthehamster.Command("test", params=[NAME_ARGUMENT[0]]), HELLO_GROUP[0]],
            ),
            {
                "name": "base",
                "params": [HELP_OPTION[1]],
                "help": None,
                "epilog": None,
                "short_help": None,
                "hidden": False,
                "deprecated": False,
                "commands": {
                    "cli": HELLO_GROUP[1],
                    "test": {
                        "name": "test",
                        "params": [NAME_ARGUMENT[1], HELP_OPTION[1]],
                        "help": None,
                        "epilog": None,
                        "short_help": None,
                        "hidden": False,
                        "deprecated": False,
                    },
                },
                "chain": False,
            },
            id="Nested Group",
        ),
    ],
)
def test_command(obj, expect):
    ctx = click_hotoffthehamster.Context(obj)
    out = obj.to_info_dict(ctx)
    assert out == expect


def test_context():
    ctx = click_hotoffthehamster.Context(HELLO_COMMAND[0])
    out = ctx.to_info_dict()
    assert out == {
        "command": HELLO_COMMAND[1],
        "info_name": None,
        "allow_extra_args": False,
        "allow_interspersed_args": True,
        "ignore_unknown_options": False,
        "auto_envvar_prefix": None,
    }


def test_paramtype_no_name():
    class TestType(click_hotoffthehamster.ParamType):
        pass

    assert TestType().to_info_dict()["name"] == "TestType"
