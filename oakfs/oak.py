import os
import typing as t
from datetime import datetime
from pathlib import Path

import humanize
from rich import box
from rich import print
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from .logroller import LogRoller
from .scanner import EntryScanner

__all__ = ["Oak", "log", "CWD"]

log = LogRoller()
CWD = Path.cwd()


class Oak:

    def __init__(
        self,
        path: Path,
        reverse: bool,
        groups: bool,
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
        :param dirs_only: Show directories only
        :param files_only: Show files only
        :param symlinks_only: Show symlinks only
        :param junctions_only: Show junctions only (Windows)
        :param groups: Show file groups and owners
        :param verbose: Enable verbose output
        :param kwargs: Additional keyword arguments for table style and datetime format
        """
        self.dt_now = datetime.now()

        self.path = path
        self.reverse = reverse
        self.groups = groups
        self.show_all = show_all

        self.files_only = files_only
        self.dirs_only = dirs_only
        self.symlinks_only = symlinks_only
        self.junctions_only = junctions_only

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
            dt_now=self.dt_now,
            verbose=kwargs.get("verbose", True),
        )

        self._table = Table(
            show_header=True,
            header_style="bold",
            box=getattr(box, kwargs.get("table_style", "ROUNDED").upper()),
            highlight=True,
            expand=True,
            border_style="#80B3FF",
        )
        self._table.add_column("path", no_wrap=True)
        self._table.add_column("size", justify="right", style="bold")
        self._table.add_column("modified", style="italic")
        self._table.add_column("type", style="#8BA2AD", no_wrap=True)
        if self.groups:
            self._table.add_column("owner", justify="right")
            self._table.add_column("group")
            self._table.add_column("permissions", style="bold red")

    def summary(self, directories: int, files: int, symlinks: int, junctions: int):
        """
        Print a summary of the scan results.

        :param directories: Number of directories found
        :param files: Number of files found
        :param symlinks: Number of symlinks found
        :param junctions: Number of junctions found
        """

        parts: list[str] = []

        # Respect filters (files_only, dirs_only, etc.)
        if self.files_only and files > 0:
            parts.append(f"{files} file{'s' if files != 1 else ''}")
        elif self.dirs_only and directories > 0:
            parts.append(f"{directories} director{'y' if directories == 1 else 'ies'}")
        elif self.symlinks_only and symlinks > 0:
            parts.append(f"{symlinks} symlink{'s' if symlinks != 1 else ''}")
        elif self.scanner.is_windows() and self.junctions_only and junctions > 0:
            parts.append(f"{junctions} junction{'s' if junctions != 1 else ''}")

        # Default case: show all non-zero counts
        elif not any(
            [self.dirs_only, self.files_only, self.symlinks_only, self.junctions_only]
        ):
            if directories > 0:
                parts.append(
                    f"{directories} director{'y' if directories == 1 else 'ies'}"
                )
            if files > 0:
                parts.append(f"{files} file{'s' if files != 1 else ''}")
            if symlinks > 0:
                parts.append(f"{symlinks} symlink{'s' if symlinks != 1 else ''}")
            if self.scanner.is_windows() and junctions > 0:
                parts.append(f"{junctions} junction{'s' if junctions != 1 else ''}")

        if len(parts) == 1:
            summary_msg = parts[0]
        else:
            summary_msg = ", ".join(parts[:-1]) + f", and {parts[-1]}"

        log.info(
            f"scanned {summary_msg} (in {humanize.naturaldelta(datetime.now() - self.dt_now)}).",
        )

    def tree(self):
        """
        Display the directory structure as a tree.
        """

        root_name = os.path.basename(os.path.abspath(self.path)) or self.path
        root_tree = Tree(
            self.scanner.style_entry_name(
                metadata={"filename": root_name, "type": "dir"}
            ),
            guide_style="dim",
            highlight=True,
        )

        def add_nodes(directory: str, tree: Tree) -> tuple[int, int, int, int]:
            """
            Recursively add nodes to the tree.

            :param directory: string path of the directory to scan
            :param tree: current Tree node to add entries to
            :return: Tuple with counts of (files, directories, symlinks, junctions)
            """

            num_files = num_dirs = num_symlinks = num_junctions = 0

            for entry, metadata in self.scanner.entries(directory=directory):
                f, d, s, j = self.scanner.classify_entry(entry=entry)
                num_files += f
                num_dirs += d
                num_symlinks += s
                num_junctions += j

                filename: Text = self.scanner.style_entry_name(metadata=metadata)

                if entry.is_dir(follow_symlinks=False):
                    branch = tree.add(filename)
                    sub_files, sub_dirs, sub_syms, sub_juncs = add_nodes(
                        directory=entry.path, tree=branch
                    )
                    num_files += sub_files
                    num_dirs += sub_dirs
                    num_symlinks += sub_syms
                    num_junctions += sub_juncs
                else:
                    tree.add(filename)

            return num_files, num_dirs, num_symlinks, num_junctions

        files, directories, symlinks, junctions = add_nodes(
            directory=str(self.path), tree=root_tree
        )

        print(root_tree)

        if self.scanner.verbose:
            self.summary(
                directories=directories,
                files=files,
                symlinks=symlinks,
                junctions=junctions,
            )

    def table(self):
        """
        Display the directory contents in a table.
        """

        rows: list = []
        num_files = num_dirs = num_symlinks = num_junctions = 0

        for entry, metadata in self.scanner.entries(directory=self.path):
            files, dirs, symlinks, junctions = self.scanner.classify_entry(entry=entry)
            num_files += files
            num_dirs += dirs
            num_symlinks += symlinks
            num_junctions += junctions

            rows.append(
                [
                    metadata["filename"],
                    metadata,
                    self.scanner.style_entry_name(metadata=metadata),
                ]
            )

        rows.sort(key=lambda row: row[0].lower(), reverse=self.scanner.reverse)

        for _, metadata, filename in rows:
            if self.groups:
                self._table.add_row(
                    filename,
                    metadata["size"],
                    metadata["mod_time"],
                    metadata["type"].strip("."),
                    metadata["owner"],
                    metadata["group"],
                    metadata["permissions"],
                )
            else:
                self._table.add_row(
                    filename,
                    metadata["size"],
                    metadata["mod_time"],
                    metadata["type"].strip("."),
                )

        print(self._table)

        if self.scanner.verbose:
            self.summary(
                directories=num_dirs,
                files=num_files,
                symlinks=num_symlinks,
                junctions=num_junctions,
            )
