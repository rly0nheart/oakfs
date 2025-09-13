import grp
import locale
import os
import pwd
import stat
import typing as t
from contextlib import nullcontext
from datetime import datetime
from os import stat_result
from pathlib import Path

import humanize
from rich import box
from rich import print
from rich.status import Status
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from . import __pkg__

CWD = Path.cwd()

ENTRY_STYLES: dict = {
    "special": {
        "dir": {"style": "bold blue", "icon": ""},
        "symlink": {"style": "blue underline", "icon": ""},
        "file": {"style": "dim white", "icon": ""},
        "other": {"style": "dim", "icon": ""},
    },
    "groups": [
        {
            "extensions": [
                ".txt",
                ".rst",
                ".rtf",
                ".xml",
                ".ini",
                ".cfg",
                ".log",
                ".pub",
            ],
            "style": "#B7CAD4",
            "icon": "",
        },
        {
            "extensions": [
                ".plist",
                ".db",
                ".db3",
                ".sqlite",
                ".sqlite3",
                ".sql",
                ".mdb",
                ".accdb",
                ".parquet",
                ".avro",
                ".orc",
                ".hdf5",
                ".h5",
                ".msgpack",
                ".tsv",
            ],
            "style": "#7193FF",
            "icon": "",
        },
        {
            "extensions": [".odt", ".epub"],
            "style": "yellow",
            "icon": "",
        },
        {
            "extensions": [
                ".jpg",
                ".ico",
                ".jpeg",
                ".png",
                ".gif",
                ".bmp",
                ".svg",
                ".tiff",
                ".webp",
                ".heic",
                ".psd",
                ".xcf",
                ".cr2",
                ".nef",
                ".arw",
                ".orf",
                ".rw2",
            ],
            "style": "magenta",
            "icon": "",
        },
        {
            "extensions": [
                ".mp4",
                ".mkv",
                ".avi",
                ".mov",
                ".wmv",
                ".webm",
                ".flv",
                ".mpeg",
                ".mpg",
                ".3gp",
            ],
            "style": "red",
            "icon": "",
        },
        {
            "extensions": [
                ".mp3",
                ".wav",
                ".flac",
                ".aac",
                ".ogg",
                ".m4a",
                ".wma",
                ".alac",
                ".aiff",
                ".opus",
                ".pcm",
                ".dsd",
                ".mid",
                ".midi",
                ".aifc",
                ".caf",
            ],
            "style": "green",
            "icon": "",
        },
        {
            "extensions": [
                ".zip",
                ".tar",
                ".gz",
                ".rar",
                ".7z",
                ".bz2",
                ".xz",
                ".tgz",
                ".tbz2",
                ".txz",
                ".zst",
                ".lzma",
                ".cab",
                ".dmg",
                ".arj",
                ".lzh",
                ".z",
                ".jar",
                ".apk",
                ".cpio",
            ],
            "style": "yellow",
            "icon": "",
        },
        {
            "extensions": [
                ".md5",
                ".sha1",
                ".sha256",
                ".sha512",
                ".sfv",
                ".sig",
                ".asc",
                ".gpg",
                ".pgp",
            ],
            "style": "#6e6e6e",
            "icon": "",
        },
        {
            "extensions": [".py", ".pyi", ".pyc"],
            "style": "#3572A5",
            "icon": "",
        },
        {
            "extensions": [".json", ".jsonl", ".ndjson"],
            "style": "purple",
            "icon": "",
        },
        {"extensions": [".docx", ".doc"], "style": "", "icon": "󰈬"},
        {"extensions": [".xlsx", ".xls"], "style": "", "icon": "󰈛"},
        {"extensions": [".pptx", ".ppt"], "style": "", "icon": "󰈧"},
        {"extensions": [".ps1"], "style": "green", "icon": "󰨊"},
        {"extensions": [".tex"], "style": "", "icon": ""},
        {"extensions": [".csv"], "style": "", "icon": ""},
        {"extensions": [".pdf"], "style": "", "icon": ""},
        {"extensions": [".sock"], "style": "cyan", "icon": "󰐧"},
        {"extensions": [".iso"], "style": "", "icon": "󰗮"},
        {"extensions": [".md"], "style": "white", "icon": "󰍔"},
        {"extensions": [".js", ".mjs"], "style": "#f1e05a", "icon": ""},
        {"extensions": [".ts"], "style": "#3178c6", "icon": ""},
        {
            "extensions": [".tsx"],
            "style": "#3178c6",
            "icon": "",
        },
        {
            "extensions": [".jsx"],
            "style": "#61dafb",
            "icon": "",
        },
        {"extensions": [".java"], "style": "#b07219", "icon": ""},
        {"extensions": [".c"], "style": "#555555", "icon": ""},
        {"extensions": [".cpp"], "style": "#f34b7d", "icon": ""},
        {
            "extensions": [".cs"],
            "style": "#178600",
            "icon": "",
        },
        {"extensions": [".go"], "style": "#00ADD8", "icon": ""},
        {"extensions": [".php"], "style": "#4F5D95", "icon": ""},
        {"extensions": [".rb"], "style": "#701516", "icon": ""},
        {"extensions": [".rs"], "style": "#dea584", "icon": ""},
        {"extensions": [".kt"], "style": "#A97BFF", "icon": ""},
        {"extensions": [".swift"], "style": "#ffac45", "icon": ""},
        {"extensions": [".pl"], "style": "#0298c3", "icon": ""},
        {
            "extensions": [".sh", ".zsh"],
            "style": "#89e051",
            "icon": "",
        },
        {"extensions": [".html"], "style": "#e34c26", "icon": ""},
        {"extensions": [".lock"], "style": "", "icon": "󰌾"},
        {"extensions": [".desktop"], "style": "", "icon": "󰘔"},
        {"extensions": [".css"], "style": "#563d7c", "icon": ""},
        {"extensions": [".scss"], "style": "#c6538c", "icon": ""},
        {
            "extensions": [".toml", ".iml", ".yml", ".yaml", ".ini"],
            "style": "dim white",
            "icon": "",
        },
    ],
}


class EntryScanner:
    def __init__(
        self,
        path: Path,
        *,
        reverse: bool,
        show_all: bool,
        dirs_only: bool,
        files_only: bool,
        symlinks_only: bool,
        junctions_only: bool,
        verbose: bool,
        dt_now: datetime,
        dt_format: t.Literal["locale", "concise"],
    ):
        """
        Initialise the EntryScanner.

        :param path: Path to scan
        :param reverse: Reverse the sort order
        :param show_all: Show hidden files and directories
        :param dirs_only: Show directories only
        :param files_only: Show files only
        :param symlinks_only: Show symlinks only
        :param junctions_only: Show junctions only (Windows)
        :param verbose: Enable verbose output
        :param dt_now: Current datetime for relative time calculations
        :param dt_format: Specify the datetime format (locale or concise)
        """

        # disable junction filtering on non-Windows
        if not self.on_windows():
            junctions_only = False

        self.path = path
        self.reverse = reverse
        self.show_all = show_all
        self.dirs_only = dirs_only
        self.files_only = files_only
        self.symlinks_only = symlinks_only
        self.junctions_only = junctions_only
        self.verbose = verbose
        self.dt_now = dt_now or datetime.now()
        self.dt_format = dt_format

    @staticmethod
    def on_windows() -> bool:
        """
        Check if the operating system is Windows.
        """
        return os.name == "nt"

    def entry_type(self, entry: os.DirEntry) -> str:
        """
        Determine the type of a directory entry.

        :param entry: Directory entry to check
        :return: Type as a string ("dir", "symlink", "file", or "no idea")
        """

        if entry.is_dir(follow_symlinks=False) and not entry.is_symlink():
            return "dir"
        elif entry.is_symlink():
            if self.on_windows() and entry.is_dir(follow_symlinks=False):
                return "junction"
            return "symlink"
        elif entry.is_file(follow_symlinks=False):
            return "file"
        else:
            return "do idea, lol"

    def iter_entries(
        self, directory: t.Union[str, Path]
    ) -> t.Iterator[t.Tuple[os.DirEntry, t.Dict]]:
        """
        Iterate over directory entries, yielding each entry and its metadata.

        :param directory: Directory path to scan
        :return: Iterator of tuples containing directory entry and its metadata
        """

        entries: list[os.DirEntry] = list(os.scandir(directory))
        entries.sort(key=lambda e: e.name.lower(), reverse=self.reverse)

        status_context = (
            Status("scanning directory...") if self.verbose else nullcontext()
        )
        with status_context as status:
            for entry in entries:
                if self.verbose:
                    status.update(
                        f"[bold]scanning <{self.entry_type(entry=entry)}>[/]: [dim]{entry.name}[/]"
                    )

                if not self.show_all and entry.name.startswith("."):
                    continue
                if self.dirs_only and not entry.is_dir(follow_symlinks=False):
                    continue
                if self.files_only and not entry.is_file(follow_symlinks=False):
                    continue
                if self.symlinks_only and not entry.is_symlink():
                    continue
                if self.junctions_only and not (
                    self.on_windows()
                    and entry.is_symlink()
                    and entry.is_dir(follow_symlinks=False)
                ):
                    continue

                yield entry, self.get_entry_metadata(entry=entry)

    def classify_entry(self, entry: os.DirEntry) -> t.Tuple[int, int, int, int]:
        """
        Classify the entry as file, directory, or symlink.

        :param entry: Directory entry to classify
        :return: Tuple with counts of (files, directories, symlinks, junctions)
        """

        files = dirs = symlinks = junctions = 0

        if entry.is_file(follow_symlinks=False):
            files = 1
        elif entry.is_dir(follow_symlinks=False) and not entry.is_symlink():
            dirs = 1
        elif entry.is_symlink():
            if self.on_windows() and entry.is_dir(follow_symlinks=False):
                junctions = 1
            else:
                symlinks = 1

        return files, dirs, symlinks, junctions

    def get_entry_metadata(self, entry: os.DirEntry) -> t.Dict:
        """
        Collect metadata from a directory entry.

        :param entry: Directory entry
        :return: Metadata dictionary
        """

        locale.setlocale(locale.LC_TIME, "")

        entry_stat: stat_result = entry.stat(follow_symlinks=False)
        mtime: datetime = datetime.fromtimestamp(entry_stat.st_mtime)
        size: str = humanize.naturalsize(entry_stat.st_size, binary=True)

        mod_time = (
            f"{humanize.naturaltime(self.dt_now - mtime)}"
            if self.dt_format == "concise"
            else mtime.strftime("%c")
        )
        permissions: str = stat.filemode(entry_stat.st_mode)
        try:
            owner = pwd.getpwuid(entry_stat.st_uid).pw_name
        except KeyError:
            owner = str(entry_stat.st_uid)

        try:
            group = grp.getgrgid(entry_stat.st_gid).gr_name
        except KeyError:
            group = str(entry_stat.st_gid)

        if entry.is_dir(follow_symlinks=False) and not entry.is_symlink():
            entry_type = "dir"
        elif entry.is_symlink():
            if self.on_windows() and entry.is_dir(follow_symlinks=False):
                entry_type = "junction"
            else:
                entry_type = "symlink"
        else:
            _, ext = os.path.splitext(entry.name)
            entry_type = ext.lower() if ext else "file"

        return {
            "filename": entry.name,
            "path": entry.path,
            "size": size,
            "mod_time": mod_time,
            "type": entry_type,
            "permissions": permissions,
            "owner": owner,
            "group": group,
        }

    @staticmethod
    def style_entry_name(metadata: dict) -> Text:
        """
        Style the entry name based on its type and extension.

        :param metadata: Metadata dictionary of the entry
        :return: Styled Text object
        """

        entry_type = metadata["type"]
        filename = metadata["filename"]
        extension = os.path.splitext(filename)[1].lower()

        # Handle special types first (dir, symlink, etc.)
        if entry_type in ENTRY_STYLES["special"]:
            style_info = ENTRY_STYLES["special"][entry_type]
            return Text(
                f"{style_info['icon']} {filename}",
                style=style_info["style"],
            )

        # Extension-based lookup from groups
        for group in ENTRY_STYLES["groups"]:
            if extension in group["extensions"]:
                return Text(
                    f"{group['icon']} {filename}",
                    style=group["style"],
                )

        # Fallback to generic file
        style_info = ENTRY_STYLES["special"]["file"]
        return Text(
            f"{style_info['icon']} {filename}",
            style=style_info["style"],
        )


class Oak:
    def __init__(
        self,
        path: Path,
        reverse: bool = False,
        verbose: bool = False,
        show_all: bool = False,
        dirs_only: bool = False,
        files_only: bool = False,
        symlinks_only: bool = False,
        junctions_only: bool = False,
        show_group: bool = False,
        dt_format: t.Literal["locale", "concise"] = "concise",
    ):
        """
        Initialise the Oak filesystem visualiser.

        :param path: Path to scan
        :param reverse: Reverse the sort order
        :param verbose: Enable verbose output
        :param show_all: Show hidden files and directories
        :param dirs_only: Show directories only
        :param files_only: Show files only
        :param symlinks_only: Show symlinks only
        :param junctions_only: Show junctions only (Windows)
        :param show_group: Show file groups and owners
        :param dt_format: Specify the datetime format (locale or concise)
        """

        self.path = path
        self.reverse = reverse
        self.verbose = verbose
        self.dt_now = datetime.now()
        self.dt_format = dt_format
        self.show_group = show_group

        self.files_only = files_only
        self.dirs_only = dirs_only
        self.symlinks_only = symlinks_only
        self.junctions_only = junctions_only
        self.show_all = show_all

        self.scanner = EntryScanner(
            path,
            reverse=self.reverse,
            show_all=self.show_all,
            dirs_only=self.dirs_only,
            files_only=self.files_only,
            symlinks_only=self.symlinks_only,
            junctions_only=self.junctions_only,
            verbose=self.verbose,
            dt_format=self.dt_format,
            dt_now=self.dt_now,
        )

        self._table = Table(
            show_header=True,
            header_style="bold",
            box=box.ROUNDED,
            highlight=True,
            expand=True,
        )
        self._table.add_column("path", no_wrap=True)
        self._table.add_column("size", justify="right")
        self._table.add_column("modified", style="bold")
        self._table.add_column("type", style="#B7CAD4")
        if self.show_group:
            self._table.add_column("owner")
            self._table.add_column("group")
            self._table.add_column("permissions", style="dim")

    def summary(self, directories: int, files: int, symlinks: int, junctions: int):
        """
        Print a summary of the scan results.

        :param directories: Number of directories found
        :param files: Number of files found
        :param symlinks: Number of symlinks found
        :param junctions: Number of junctions found
        """

        summary_msg: str = ""

        if self.files_only:
            summary_msg = f"{files} files"
        if self.dirs_only:
            summary_msg = f"{directories} directories"
        if self.symlinks_only:
            summary_msg = f"{symlinks} symlinks"
        elif self.scanner.on_windows() and self.junctions_only:
            summary_msg = f"{junctions} junctions"

        elif not any(
            [self.dirs_only, self.files_only, self.symlinks_only, self.junctions_only]
        ):
            if self.scanner.on_windows():
                summary_msg = (
                    f"{directories} directories, {files} files, "
                    f"{symlinks} symlinks, and {junctions} junctions"
                )
            else:
                summary_msg = (
                    f"{directories} directories, {files} files, {symlinks} symlinks"
                )
        print(
            f"\n{__pkg__}: scanned {summary_msg} in {humanize.naturaldelta(datetime.now() - self.dt_now)}"
        )

    def tree(self):
        """
        Display the directory structure as a tree.
        """

        root_name = os.path.basename(os.path.abspath(self.path)) or self.path
        root_tree = Tree(
            f"[bold blue] {root_name}[/bold blue]",
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

            for entry, metadata in self.scanner.iter_entries(directory=directory):
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

        if self.verbose:
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
        rows: t.List = []
        num_files = num_dirs = num_symlinks = num_junctions = 0

        for entry, metadata in self.scanner.iter_entries(directory=self.path):
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
            if self.show_group:
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

        if self.verbose:
            self.summary(
                directories=num_dirs,
                files=num_files,
                symlinks=num_symlinks,
                junctions=num_junctions,
            )
