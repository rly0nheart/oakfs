import grp
import locale
import os
import pwd
import stat
import typing as t
from datetime import datetime
from pathlib import Path

import humanize
from rich.status import Status
from rich.text import Text

ENTRY_STYLES: dict = {
    "special": {
        "directory": {"style": "bold blue", "icon": ""},
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
            "style": "#7193FF",
            "icon": "",
            "filetypes": ["plaintext"],
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
            "filetypes": ["database"],
        },
        {
            "extensions": [".odt", ".epub"],
            "style": "yellow",
            "icon": "",
            "filetypes": ["document", "ebook"],
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
                ".arj",
                ".lzh",
                ".z",
                ".jar",
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
        {"extensions": [".iso", ".dmg"], "style": "", "icon": "󰗮"},
        {"extensions": [".ipa", ".app", ".pkg"], "style": "", "icon": ""},
        {"extensions": [".apk", ".xapk"], "style": "green", "icon": ""},
        {"extensions": [".xlsx", ".xls"], "style": "", "icon": "󰈛"},
        {"extensions": [".pptx", ".ppt"], "style": "", "icon": "󰈧"},
        {"extensions": [".ps1"], "style": "green", "icon": "󰨊"},
        {"extensions": [".tex"], "style": "", "icon": ""},
        {"extensions": [".csv"], "style": "", "icon": ""},
        {"extensions": [".pdf"], "style": "", "icon": ""},
        {"extensions": [".sock"], "style": "cyan", "icon": "󰐧"},
        {"extensions": [".md"], "style": "white", "icon": "󰍔"},
        {"extensions": [".js", ".mjs", "cjs"], "style": "#f1e05a", "icon": ""},
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

FILETYPE_MAP: dict[str, list[str]] = {
    # Textual
    "plaintext": [".txt", ".rst", ".rtf", ".pub"],
    "config": [".xml", ".ini", ".cfg", ".toml", ".iml", ".yml", ".yaml"],
    "log": [".log"],
    # Data / structured
    "database": [
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
    "json": [".json", ".jsonl", ".ndjson"],
    "markdown": [".md"],
    "ssh": [".pub", ".pem", ".key"],
    "record": [".csv"],
    # Documents
    "document": [".docx", ".doc", ".odt", ".pdf", ".tex"],
    "spreadsheet": [".xlsx", ".xls"],
    "presentation": [".pptx", ".ppt"],
    "ebook": [".epub"],
    # Media
    "image": [
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
    "video": [
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
    "audio": [
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
    "archive": [
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
        ".arj",
        ".lzh",
        ".z",
        ".jar",
        ".cpio",
    ],
    "binary": [".bin", ".so", ".dylib", ".out"],
    "executable": [".exe", ".bat", ".cmd", ".dll"],
    "diskimage": [".iso", ".dmg"],
    "package": [".ipa", ".app", ".pkg", ".apk", ".xapk"],
    "checksum": [".md5", ".sha1", ".sha256", ".sha512", ".sfv"],
    "signature": [".sig", ".asc", ".gpg", ".pgp"],
    "header": [".h", ".hh", ".hpp", ".hxx"],
    "code": [
        ".py",
        ".pyi",
        ".pyc",
        ".ps1",
        ".js",
        ".mjs",
        ".cjs",
        ".ts",
        ".tsx",
        ".jsx",
        ".java",
        ".c",
        ".cc",
        ".cpp",
        ".cs",
        ".go",
        ".php",
        ".rb",
        ".rs",
        ".kt",
        ".swift",
        ".pl",
        ".sh",
        ".zsh",
        ".html",
        ".css",
        ".scss",
    ],
    # Misc
    "socket": [".sock"],
    "desktop": [".desktop"],
    "lockfile": [".lock"],
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
        dt_now: datetime,
        dt_format: t.Literal["locale", "relative"],
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
        :param dt_now: Current datetime for relative time calculations
        :param dt_format: Specify the datetime format (locale or relative)
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
        self.dt_now = dt_now or datetime.now()
        self.dt_format = dt_format

    @staticmethod
    def on_windows() -> bool:
        """
        Check if the operating system is Windows.
        """
        return os.name == "nt"

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

        with Status("wait...") as status:
            for entry in entries:
                status.update(
                    f"[bold]scanning[/bold]:::[bold #8BA2AD]{self.get_entry_type(path=Path(entry.path))}[/bold #8BA2AD]:: [dim italic]{entry.name}[/dim italic]"
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

        entry_stat: os.stat_result = entry.stat(follow_symlinks=False)
        mtime: datetime = datetime.fromtimestamp(entry_stat.st_mtime)
        size: str = humanize.naturalsize(entry_stat.st_size, binary=True)

        mod_time = (
            f"{humanize.naturaltime(self.dt_now - mtime)}"
            if self.dt_format == "relative"
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

        return {
            "filename": entry.name,
            "path": entry.path,
            "size": size,
            "mod_time": mod_time,
            "type": self.get_entry_type(path=Path(entry.path)),
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

        # Handle special types first (directory, symlink, etc.)
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

    @staticmethod
    def get_entry_type(path: Path) -> str:
        """
        Get the filetype of a given entry based on its attributes and extension.

        :param path: Path object representing the file or directory
        :return: Filetype as a string ("directory", "symlink", "junction", "file", e.t.c)
        """
        _filetype: str = "file"
        if path.is_dir(follow_symlinks=False):
            _filetype = "directory"
        if path.is_symlink():
            _filetype = "symlink"
        if hasattr(path, "is_junction") and path.is_junction():
            _filetype = "junction"

        extension = path.suffix.lower()
        for filetype, extensions in FILETYPE_MAP.items():
            if extension in extensions:
                _filetype = filetype

        return _filetype
