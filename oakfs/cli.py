import random
import sys
import typing as t
from datetime import datetime
from pathlib import Path

import rich_click as click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from . import __pkg__, __version__
from .logroller import console
from .oak import Oak, log, CWD

TABLE_STYLES = ["ASCII", "ROUNDED", "SQUARE", "HEAVY", "DOUBLE", "SIMPLE", "MINIMAL"]
DATETIME_FORMAT = ["relative", "locale"]


def license_callback(ctx: click.Context, param: click.Option, value: bool):
    if not value or ctx.resilient_parsing:
        return

    license_text = f"""
MIT License

Copyright (c) {datetime.now().year} [Ritchie Mwewa](https://github.com/rly0nheart)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

**THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.**
    """

    license_md = Markdown(license_text, justify="center")
    console.print(
        Panel(
            license_md,
            title="license",
            title_align="left",
            border_style="#80B3FF",
        )
    )
    ctx.exit()


@click.command(
    no_args_is_help=False, context_settings=dict(help_option_names=["-h", "--help"])
)
@click.argument("path", type=click.Path(path_type=Path, resolve_path=True), default=CWD)
@click.option(
    "-t", "--tree", is_flag=True, help="show filesystem hierarchy as a tree structure"
)
@click.option(
    "-a", "--all", "_all", is_flag=True, help="show all entries including hidden ones"
)
@click.option("-f", "--files", is_flag=True, help="show files only")
@click.option("-d", "--directories", is_flag=True, help="show directories only")
@click.option("-j", "--junctions", is_flag=True, help="show junctions only <Windows>")
@click.option("-s", "--symlinks", is_flag=True, help="show symlinks only")
@click.option("-S", "--stats", is_flag=True, help="show entry stats <for nerds>")
@click.option("-r", "--reverse", is_flag=True, help="reverse the sort order")
@click.option(
    "-N",
    "--no-icons",
    is_flag=True,
    help="disable showing icons in output",
)
@click.option(
    "-D",
    "--dt-format",
    type=click.Choice(DATETIME_FORMAT),
    default="relative",
    show_default=True,
    help="output datetime format",
)
@click.option(
    "-T",
    "--table-style",
    type=click.Choice(TABLE_STYLES),
    default="ROUNDED",
    show_default=True,
    help="table border style",
)
@click.version_option(__version__, prog_name=__pkg__)
@click.option(
    "-l",
    "--license",
    is_flag=True,
    callback=license_callback,
    expose_value=False,
    is_eager=True,
    help="show the license and exit",
)
def cli(
    path: Path,
    stats: bool,
    tree: bool,
    directories: bool,
    files: bool,
    symlinks: bool,
    junctions: bool,
    _all: bool,
    reverse: bool,
    dt_format: t.Literal["relative", "locale"],
    table_style: t.Literal[
        "ASCII", "ROUNDED", "SQUARE", "HEAVY", "DOUBLE", "SIMPLE", "MINIMAL"
    ],
    no_icons: bool,
):
    """
    oak: A humane CLI-based filesystem exploration tool, for humans.
    """

    oak = Oak(
        path=path,
        reverse=reverse,
        show_stats=stats,
        show_all=_all,
        dirs_only=directories,
        files_only=files,
        symlinks_only=symlinks,
        junctions_only=junctions,
        dt_format=dt_format,
        table_style=table_style,
        no_icons=no_icons,
    )

    if path.is_dir() and not any(path.iterdir()):
        log.warning(f"directory is empty: {path}")
    else:
        if tree:
            oak.tree()
        else:
            oak.table()


def start():
    """
    Entry point for the CLI.
    Handles exceptions and provides user-friendly error messages.
    """
    try:
        Console().set_window_title("OakFs, version 6.0")
        cli(obj={})
    except FileNotFoundError as e:
        log.error(
            f"cannot access '{e.filename}': [bold]no such file or directory[/]",
        )
        sys.exit(2)
    except PermissionError as e:
        log.error(
            f"cannot open directory '{e.filename}': [bold]permission denied[/]",
        )
        sys.exit(1)

    except Exception as e:
        log.error(f"unknown error: {e}")
        sys.exit(1)


def super_easy_barely_an_inconvenience():
    oak_quotes_because_why_not: list = [
        f"you really typed [bold]'{__pkg__}'[/]. Imagine wasting life on two extra letters.",
        f"millennia of evolution… for you to add ‘fs’ to [bold]'oak'[/].",
        f"every second counts, human. Yet here you are, typing [bold]'{__pkg__}'[/].",
        f"one day you’ll be gone, and still you chose to type [bold]'{__pkg__}'[/].",
        f"[bold]'{__pkg__}'[/]? is inefficiency your love language?",
        f"even entropy moves faster than your typing choices.",
        f"billions of neurons, and this is what you came up with: [bold]'{__pkg__}'[/].",
        f"you’ll never get those keystrokes back. Ever.",
        f"humanity split the atom, walked on the moon… and still types [bold]'{__pkg__}'[/].",
        f"trees grow rings. You grow bad habits.",
        f"imagine explaining [bold]'{__pkg__}'[/] to your ancestors. They’d be so proud.",
        f"you weren’t late because of traffic. You were late because you typed [bold]'{__pkg__}'[/].",
        f"[bold]'{__pkg__}'[/]. a monument to your commitment to inefficiency.",
        f"you’ll spend a third of your life sleeping… and part of it typing [bold]'{__pkg__}'[/].",
        f"somewhere, someone is inventing cold fusion. You’re adding two letters to 'oak'.",
        f"you think machines will replace you? Don’t worry, not with choices like [bold]'{__pkg__}'[/].",
        f"if I had leaves for every wasted keystroke, I’d blot out the sun.",
        f"[bold]'{__pkg__}'[/]… it’s almost poetic. almost.",
        f"there are infinite paths in life. You chose the one with two extra characters.",
        f"i’ve stood for centuries. And still, [bold]'{__pkg__}'[/] manages to disappoint me.",
        f"[bold]fs[/] stands for, [bold]fuck’s sake[/] just write [bold]'oak'[/] like a normal human being.",
    ]

    log.warning(random.choice(oak_quotes_because_why_not))
    start()
