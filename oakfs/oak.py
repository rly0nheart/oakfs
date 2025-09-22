import os
import typing as t
from datetime import datetime
from pathlib import Path

from rich import box, print
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from .filesystem import EntryScanner, EntryStats, ENTRY_STYLES, style_text
from .logroller import LogRoller

__all__ = ["Oak", "log", "CWD"]

log = LogRoller()
CWD = Path.cwd()


class Oak:
    def __init__(
        self,
        path: Path,
        reverse: bool,
        show_all: bool,
        dirs_only: bool,
        files_only: bool,
        symlinks_only: bool,
        junctions_only: bool,
        **kwargs: t.Any,
    ):
        """
        Initialise the Oak filesystem visualiser.

        :param path: Path to scan
        :param reverse: Reverse the sort order
        :param show_all: Show hidden files and directories
        :param show_mimetypes: Show mimetypes in the table
        :param dirs_only: Show directories only
        :param files_only: Show files only
        :param symlinks_only: Show symlinks only
        :param junctions_only: Show junctions only (Windows)
        :param kwargs: Additional keyword arguments for configuration options such as table style,
        datetime format, verbosity, and display of groups, owners, and permissions.
        """

        self.path = path
        self.reverse = reverse
        self.show_all = show_all
        self.files_only = files_only
        self.dirs_only = dirs_only
        self.symlinks_only = symlinks_only
        self.junctions_only = junctions_only

        self.table_style = kwargs.get("table_style", "ROUNDED")
        self.stats: bool = kwargs.get("show_stats", False)

        self.scanner = EntryScanner(
            path,
            reverse=self.reverse,
            show_all=self.show_all,
            no_icons=kwargs.get("no_icons", True),
            dirs_only=self.dirs_only,
            files_only=self.files_only,
            symlinks_only=self.symlinks_only,
            junctions_only=self.junctions_only,
            dt_format=kwargs.get("dt_format"),
            dt_now=datetime.now(),
        )

    def tree(self):
        """
        Display the directory structure as a tree.
        """

        root_styles: dict = ENTRY_STYLES["special"]["inode/directory"]
        root_name = os.path.basename(os.path.abspath(self.path)) or self.path

        root_tree = Tree(
            Text(
                str(
                    style_text(
                        filename=root_name,
                        mimetype="inode/directory",
                        no_icons=self.scanner.no_icons,
                        extension="",
                    )
                ),
                style=root_styles["style"],
            ),
            guide_style="dim",
            highlight=True,
        )

        collected: list[EntryStats] = []

        def add_nodes(directory: str, tree: Tree):
            """
            Recursively add nodes to the tree.

            :param directory: string path of the directory to scan
            :param tree: current Tree node to add entries to
            """
            for entry in self.scanner.entries(directory=directory):
                collected.append(entry)
                filename: Text = entry.style_name()

                if entry.path.is_dir(follow_symlinks=False):
                    branch = tree.add(filename)
                    add_nodes(directory=str(entry.path), tree=branch)
                else:
                    tree.add(filename)

        add_nodes(directory=str(self.path), tree=root_tree)
        print(root_tree)
        log.summary(self.scanner.summary(entries=collected))

    def table(self):
        """
        Display the directory contents in a table.
        """

        def make_table() -> Table:
            table = Table(
                show_header=True,
                header_style="bold",
                box=getattr(box, self.table_style.upper()),
                highlight=True,
                expand=True,
                border_style="dim",
            )

            table.add_column("name", overflow="ellipsis")
            table.add_column("size", justify="right")
            table.add_column("type", overflow="fold", style="dim #8BA2AD")
            table.add_column("last seen", justify="right", style="italic")
            table.add_column("updated", justify="right", style="italic")

            if self.stats:
                table.add_column("mimetype", style="cyan")
                table.add_column("inode")
                table.add_column("hardlinks")
                table.add_column("group", style="yellow")
                table.add_column("owner", style="green")
                table.add_column("permissions", style="bold red")

            return table

        entry_table: Table = make_table()
        rows: list[EntryStats] = list(self.scanner.entries(directory=self.path))

        for entry in rows:
            row: list = [
                entry.style_name(),
                entry.size.lower(),
                entry.filetype.lower(),
                entry.atime,
                entry.mtime,
            ]

            if self.stats:
                row.append(entry.mimetype)
                row.append(str(entry.inode))
                row.append(str(entry.hardlinks))
                row.append(entry.group)
                row.append(entry.owner)
                row.append(entry.permissions)

            entry_table.add_row(*row)

        print(entry_table)
        log.summary(self.scanner.summary(entries=rows))
