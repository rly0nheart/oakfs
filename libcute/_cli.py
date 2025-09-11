import typing as t
from pathlib import Path

import rich_click as click
from rich import print

from . import __version__
from ._main import LibCute, CWD

TABLE_STYLES = ["ASCII", "ROUNDED", "SQUARE", "HEAVY", "DOUBLE", "SIMPLE", "MINIMAL"]
DATETIME_FORMAT = ["concise", "locale"]


@click.command()
@click.argument("path", type=click.Path(path_type=Path, resolve_path=True), default=CWD)
@click.option(
    "-a", "--show-all", is_flag=True, help="Show hidden files and directories."
)
@click.option("-r", "--reverse", is_flag=True, help="Reverse the sort order.")
@click.option(
    "-g", "--show-group", is_flag=True, help="Show groups and owners in the table."
)
@click.option(
    "-dt",
    "--datetime-format",
    type=click.Choice(DATETIME_FORMAT),
    default="locale",
    show_default=True,
    help="Specify the datetime format.",
)
@click.option(
    "--table-style",
    type=click.Choice(TABLE_STYLES),
    default="ROUNDED",
    show_default=True,
    help="Table style.",
)
@click.version_option(__version__, prog_name="ptable")
def ctable(
    path: Path,
    show_all: bool,
    reverse: bool,
    show_group: bool,
    datetime_format: t.Literal["concise", "locale"],
    table_style: str,
):
    """Show files and directories in a table."""
    try:
        libcute = LibCute(
            path=path,
            reverse=reverse,
            show_all=show_all,
            show_group=show_group,
            table_style=table_style,
            dt_format=datetime_format,
        )
        libcute.table()
    except Exception as e:
        print(f"ctable: [bold red]{e}[/bold red]")


@click.command()
@click.argument("path", type=click.Path(path_type=Path, resolve_path=True), default=CWD)
@click.option(
    "-a", "--show-all", is_flag=True, help="Show hidden files and directories."
)
@click.option("-r", "--reverse", is_flag=True, help="Reverse the sort order.")
@click.version_option(__version__, prog_name="ptree")
def ctree(path: Path, show_all: bool, reverse: bool):
    """Show files and directories in a tree."""
    try:
        libcute = LibCute(
            path=path,
            reverse=reverse,
            show_all=show_all,
        )
        libcute.tree()
    except Exception as e:
        print(f"ctree: [bold red]{e}[/bold red]")
