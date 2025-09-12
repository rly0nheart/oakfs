import grp
import locale
import os
import pwd
import stat
import typing as t
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


class Oak:
    def __init__(self, path: Path, **kwargs: t.Union[bool, t.Any]):
        self._path = path
        self._dt_now: datetime = datetime.now()
        self._show_all = kwargs.get("_all", False)
        self._show_group = kwargs.get("group", False)
        self._dirs_only = kwargs.get("dirs", False)
        self._files_only = kwargs.get("files", False)
        self._symlinks_only = kwargs.get("symlinks", False)
        self._reverse = kwargs.get("reverse", False)
        self._dt_format: t.Literal["locale", "concise"] = kwargs.get(
            "dt_format", "locale"
        )

        self._table = Table(
            show_header=True,
            header_style="bold",
            box=getattr(box, kwargs.get("table_style", "ROUNDED")),
            highlight=True,
            expand=True,
        )
        self._table.add_column("path", no_wrap=True)
        self._table.add_column("size", justify="right")
        self._table.add_column("modified")
        self._table.add_column("type", style="#B7CAD4")
        if self._show_group:
            self._table.add_column("owner")
            self._table.add_column("group")
            self._table.add_column("permissions", style="dim")

    def summary(self, directories: int, files: int, symlinks: int):

        summary_msg: str = ""

        if self._files_only:
            summary_msg = f"found {files} files"
        if self._dirs_only:
            summary_msg = f"found {directories} directories"
        if self._symlinks_only:
            summary_msg = f"found {symlinks} symlinks"
        elif not any([self._dirs_only, self._files_only, self._symlinks_only]):
            summary_msg = f"found {directories} directories, {files} files, and {symlinks} symlinks"

        print(f"\n[bold]{summary_msg}[/bold]")

    def _get_entry_metadata(self, entry: os.DirEntry[str]) -> dict:
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
            f"{humanize.naturaltime(self._dt_now - mtime)}"
            if self._dt_format == "concise"
            else mtime.strftime("%c")
        )
        permissions: str = stat.filemode(entry_stat.st_mode)
        try:
            owner = pwd.getpwuid(entry_stat.st_uid).pw_name
        except KeyError:
            owner = str(stat_result.st_uid)

        try:
            group = grp.getgrgid(entry_stat.st_gid).gr_name
        except KeyError:
            group = str(stat_result.st_gid)

        if entry.is_dir(follow_symlinks=False):
            entry_type = "dir"
        elif entry.is_symlink():
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
    def _set_entry_name(metadata: dict) -> Text:
        """
        Style filename based on its extension or special type.
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

    def tree(self):
        root_name = os.path.basename(os.path.abspath(self._path)) or self._path
        root_tree = Tree(
            f"[bold blue] {root_name}[/bold blue]",
            guide_style="dim",
            highlight=True,
        )

        def add_nodes(directory: str, tree: Tree) -> tuple[int, int, int]:
            entries: list[os.DirEntry] = list(os.scandir(directory))
            entries.sort(key=lambda e: e.name.lower(), reverse=self._reverse)

            files_count: int = 0
            dirs_count: int = 0
            symlinks_count: int = 0

            for entry in entries:
                if not self._show_all and entry.name.startswith("."):
                    continue
                if self._dirs_only and not entry.is_dir(follow_symlinks=False):
                    continue
                if self._files_only and not entry.is_file(follow_symlinks=False):
                    continue

                with Status(f"[bold green]processing:[/] {entry.name}"):
                    if entry.is_file(follow_symlinks=False):
                        files_count += 1
                    elif entry.is_dir(follow_symlinks=False):
                        dirs_count += 1
                    elif entry.is_symlink():
                        symlinks_count += 1

                    metadata = self._get_entry_metadata(entry=entry)
                    filename = self._set_entry_name(metadata=metadata)

                    if entry.is_dir(follow_symlinks=False):
                        branch = tree.add(filename)
                        sub_files, sub_dirs, sub_syms = add_nodes(entry.path, branch)
                        files_count += sub_files
                        dirs_count += sub_dirs
                        symlinks_count += sub_syms
                    else:
                        tree.add(filename)

            return files_count, dirs_count, symlinks_count

        files, directories, symlinks = add_nodes(
            directory=str(self._path), tree=root_tree
        )

        print(root_tree)
        self.summary(directories=directories, files=files, symlinks=symlinks)

    def file(self): ...
    def table(self):
        """
        List contents of a directory.
        """

        entries = list(os.scandir(self._path))

        rows: list = []
        files_count: int = 0
        directories_count: int = 0
        symlinks_count: int = 0

        for entry in entries:
            if entry.is_dir(follow_symlinks=False):
                directories_count += 1
            if entry.is_file(follow_symlinks=False):
                files_count += 1
            if entry.is_symlink():
                symlinks_count += 1

            if not self._show_all and entry.name.startswith("."):
                continue
            if self._dirs_only and not entry.is_dir():
                continue
            if self._files_only and not entry.is_file():
                continue

            if self._symlinks_only and not entry.is_symlink():
                continue

            metadata = self._get_entry_metadata(entry=entry)

            rows.append(
                [
                    metadata["filename"],
                    metadata,
                    self._set_entry_name(metadata=metadata),
                ]
            )

        # sort alphabetically by filename
        rows.sort(key=lambda row: row[0].lower(), reverse=self._reverse)

        # add rows to the table
        for _, metadata, filename in rows:
            if self._show_group:
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
        self.summary(
            directories=directories_count, files=files_count, symlinks=symlinks_count
        )
