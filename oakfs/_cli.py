import sys
from pathlib import Path

import rich_click as click
from rich import print

from . import __pkg__, __version__
from ._main import Oak, CWD

TABLE_STYLES = ["ASCII", "ROUNDED", "SQUARE", "HEAVY", "DOUBLE", "SIMPLE", "MINIMAL"]
DATETIME_FORMAT = ["concise", "locale"]


@click.group(
    invoke_without_command=True,
    no_args_is_help=False,
)
@click.version_option(__version__, prog_name=__pkg__)
@click.option("-f", "--files", is_flag=True, help="show files only.")
@click.option("-d", "--dirs", is_flag=True, help="show directories only.")
@click.option("-s", "--symlinks", is_flag=True, help="show symlinks only.")
@click.option(
    "-t",
    "--dt-format",
    type=click.Choice(DATETIME_FORMAT),
    default="locale",
    show_default=True,
    help="specify the datetime format.",
)
@click.option(
    "-g", "--group", is_flag=True, help="show file groups and owners in the table."
)
@click.option(
    "-a", "--all", "_all", is_flag=True, help="show hidden files and directories."
)
@click.option("-r", "--reverse", is_flag=True, help="reverse the sort order.")
@click.pass_context
def cli(
    ctx: click.Context,
    dirs: bool,
    files: bool,
    symlinks: bool,
    _all: bool,
    reverse: bool,
    group: bool,
    dt_format: str,
):
    """
    oakfs: a cute filesystem visualisation tool... for cute humans 🙂
    """
    ctx.ensure_object(dict)
    ctx.obj["dirs"] = dirs
    ctx.obj["files"] = files
    ctx.obj["symlinks"] = symlinks
    ctx.obj["all"] = _all
    ctx.obj["group"] = group
    ctx.obj["dt_format"] = dt_format
    ctx.obj["reverse"] = reverse

    if ctx.invoked_subcommand is None:
        ctx.get_usage()


@cli.command()
@click.argument("path", type=click.Path(path_type=Path, resolve_path=True), default=CWD)
@click.pass_context
def table(
    ctx: click.Context,
    path: Path,
):
    """Show files and directories in a table."""
    oak = Oak(
        path=path,
        dirs=ctx.obj["dirs"],
        files=ctx.obj["files"],
        symlinks_only=ctx.obj["symlinks"],
        reverse=ctx.obj["reverse"],
        show_all=ctx.obj["all"],
        show_group=ctx.obj["group"],
        dt_format=ctx.obj["dt_format"],
    )
    oak.table()


@cli.command()
@click.argument("path", type=click.Path(path_type=Path, resolve_path=True), default=CWD)
@click.pass_context
def tree(ctx: click.Context, path: Path):
    """Show files and directories in a tree."""
    oak = Oak(
        path=path,
        reverse=ctx.obj["reverse"],
        show_all=ctx.obj["all"],
        dirs=ctx.obj["dirs"],
        files=ctx.obj["files"],
        symlinks_only=ctx.obj["symlinks"],
    )
    oak.tree()


def start():
    try:
        cli(obj={})
    except FileNotFoundError as e:
        print(f"{__pkg__}: cannot access '{e.filename}': No such file or directory")
        sys.exit(2)
    except PermissionError as e:
        print(f"{__pkg__}: cannot open directory '{e.filename}': Permission denied")
        sys.exit(1)
    except Exception as e:
        print(f"{__pkg__}: {e}")
        sys.exit(1)
