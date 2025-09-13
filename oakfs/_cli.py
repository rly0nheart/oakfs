import random
import sys
from pathlib import Path

import rich_click as click

from . import __version__, __pkg__, __project__
from ._main import logroller, Oak, CWD

TABLE_STYLES = ["ASCII", "ROUNDED", "SQUARE", "HEAVY", "DOUBLE", "SIMPLE", "MINIMAL"]
DATETIME_FORMAT = ["concise", "locale"]
from rich.prompt import Prompt


@click.group(
    invoke_without_command=True,
    no_args_is_help=False,
)
@click.version_option(__version__, prog_name=__pkg__)
@click.option("-f", "--files", is_flag=True, help="show files only.")
@click.option("-d", "--dirs", is_flag=True, help="show directories only.")
@click.option("-s", "--symlinks", is_flag=True, help="show symlinks only.")
@click.option("-j", "--junctions", is_flag=True, help="show junctions only (Windows).")
@click.option(
    "-T",
    "--dt-format",
    type=click.Choice(DATETIME_FORMAT),
    default="concise",
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
@click.option("-V", "--verbose", is_flag=True, help="enable verbose output.")
@click.pass_context
def cli(
    ctx: click.Context,
    dirs: bool,
    files: bool,
    symlinks: bool,
    junctions: bool,
    _all: bool,
    reverse: bool,
    group: bool,
    dt_format: str,
    verbose: bool,
):
    """
    oakfs: a cute filesystem visualisation tool... for cute humans 🙂
    """
    ctx.ensure_object(dict)
    ctx.obj["dirs"] = dirs
    ctx.obj["files"] = files
    ctx.obj["symlinks"] = symlinks
    ctx.obj["junctions"] = junctions
    ctx.obj["all"] = _all
    ctx.obj["group"] = group
    ctx.obj["dt_format"] = dt_format
    ctx.obj["reverse"] = reverse
    ctx.obj["verbose"] = verbose

    if ctx.invoked_subcommand is None:
        # Prompt the user to choose a view if no subcommand is provided
        choice = Prompt.ask(
            f"[dim]{__project__}[/]: [bold yellow]missing command[/bold yellow]: enter a preferred view",
            choices=["table", "tree"],
            default="table",
        )
        ctx.invoke(globals()[choice], path=CWD)


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
        reverse=ctx.obj["reverse"],
        dt_format=ctx.obj["dt_format"],
        dirs_only=ctx.obj["dirs"],
        files_only=ctx.obj["files"],
        symlinks_only=ctx.obj["symlinks"],
        junctions_only=ctx.obj["junctions"],
        show_all=ctx.obj["all"],
        show_group=ctx.obj["group"],
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
        dirs_only=ctx.obj["dirs"],
        files_only=ctx.obj["files"],
        symlinks_only=ctx.obj["symlinks"],
        junctions_only=ctx.obj["junctions"],
    )
    oak.tree()


def start():
    """
    Entry point for the CLI.
    Handles exceptions and provides user-friendly error messages.
    """
    try:
        cli(obj={})
    except FileNotFoundError as e:
        logroller.warning(
            f"cannot access '{e.filename}': [bold]no such file or directory[/]",
        )
        sys.exit(2)
    except PermissionError as e:
        logroller.warning(
            f"cannot open directory '{e.filename}': [bold]permission denied[/]",
        )
        sys.exit(1)

    except Exception as e:
        logroller.error(f"unknown error: {e}")
        sys.exit(1)


def super_easy_barely_an_inconvenience():
    oakfs_quotes_because_why_not: list = [
        f"You really typed [bold]'{__pkg__}'[/]. Imagine wasting life on two extra letters.",
        f"Millennia of evolution… for you to add ‘fs’ to [bold]'oak'[/].",
        f"Every second counts, human. Yet here you are, typing [bold]'{__pkg__}'[/].",
        f"One day you’ll be gone, and still you chose to type [bold]'{__pkg__}'[/].",
        f"[bold]'{__pkg__}'[/]? Is inefficiency your love language?",
        f"Even entropy moves faster than your typing choices.",
        f"Billions of neurons, and this is what you came up with: [bold]'{__pkg__}'[/].",
        f"You’ll never get those keystrokes back. Ever.",
        f"Humanity split the atom, walked on the moon… and still types [bold]'{__pkg__}'[/].",
        f"Trees grow rings. You grow bad habits.",
        f"Imagine explaining [bold]'{__pkg__}'[/] to your ancestors. They’d be so proud.",
        f"You weren’t late because of traffic. You were late because you typed [bold]'{__pkg__}'[/].",
        f"[bold]'{__pkg__}'[/]. A monument to your commitment to inefficiency.",
        f"You’ll spend a third of your life sleeping… and part of it typing [bold]'{__pkg__}'[/].",
        f"Somewhere, someone is inventing cold fusion. You’re adding two letters.",
        f"You think machines will replace you? Don’t worry, not with choices like [bold]'{__pkg__}'[/].",
        f"If I had leaves for every wasted keystroke, I’d blot out the sun.",
        f"[bold]'{__pkg__}'[/]… it’s almost poetic. Almost.",
        f"There are infinite paths in life. You chose the one with two extra characters.",
        f"I’ve stood for centuries. And still, [bold]'{__pkg__}'[/] manages to disappoint me.",
        f"[bold]'fs'[/] stands for [bold]'fuck's sake'[/] just write [bold]'oak'[/] like a normal human being.",
    ]

    logroller.warning(random.choice(oakfs_quotes_because_why_not))
    start()
