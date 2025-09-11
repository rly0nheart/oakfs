import sys
import typing as t
from pathlib import Path

import rich_click as click
from rich import print

from . import __pkg__, __version__
from ._main import Oakfs, CWD

TABLE_STYLES = ["ASCII", "ROUNDED", "SQUARE", "HEAVY", "DOUBLE", "SIMPLE", "MINIMAL"]
DATETIME_FORMAT = ["concise", "locale"]


@click.group(
    invoke_without_command=True,
    no_args_is_help=False,
)
@click.version_option(__version__, prog_name=__pkg__)
@click.option(
    "-a", "--show-all", is_flag=True, help="show hidden files and directories."
)
@click.option("-r", "--reverse", is_flag=True, help="reverse the sort order.")
@click.pass_context
def cli(ctx: click.Context, show_all: bool, reverse: bool):
    """
    oakfs: a cute filesystem visualisation tool... for cute humans 🙂
    """
    ctx.ensure_object(dict)
    ctx.obj["show_all"] = show_all
    ctx.obj["reverse"] = reverse
    if ctx.invoked_subcommand is None:
        ctx.get_usage()


@cli.command()
@click.argument("path", type=click.Path(path_type=Path, resolve_path=True), default=CWD)
@click.option(
    "-g", "--show-group", is_flag=True, help="show groups and owners in the table."
)
@click.option(
    "-dt",
    "--datetime-format",
    type=click.Choice(DATETIME_FORMAT),
    default="locale",
    show_default=True,
    help="specify the datetime format.",
)
@click.option(
    "--table-style",
    type=click.Choice(TABLE_STYLES),
    default="ROUNDED",
    show_default=True,
    help="table style.",
)
@click.pass_context
def table(
    ctx: click.Context,
    path: Path,
    show_group: bool,
    datetime_format: t.Literal["concise", "locale"],
    table_style: str,
):
    """Show files and directories in a table."""
    oak = Oakfs(
        path=path,
        reverse=ctx.obj["reverse"],
        show_all=ctx.obj["show_all"],
        show_group=show_group,
        table_style=table_style,
        dt_format=datetime_format,
    )
    oak.table()


@cli.command()
@click.argument("path", type=click.Path(path_type=Path, resolve_path=True), default=CWD)
@click.pass_context
def tree(ctx: click.Context, path: Path):
    """Show files and directories in a tree."""
    oak = Oakfs(
        path=path,
        reverse=ctx.obj["reverse"],
        show_all=ctx.obj["show_all"],
    )
    oak.tree()


def start():
    try:
        cli(obj={})
    except FileNotFoundError as e:
        print(f"{__pkg__}: cannot access '{e.filename}': No such file or directory\n")
        sys.exit(2)
    except PermissionError as e:
        print(f"{__pkg__}: cannot open directory '{e.filename}': Permission denied\n")
        sys.exit(1)
    except Exception as e:
        print(f"{__pkg__}: error: {e}\n")
        sys.exit(1)
