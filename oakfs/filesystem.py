import grp
import os
import pwd
import stat
import typing as t
from collections import Counter
from datetime import datetime
from pathlib import Path

import humanize
import puremagic
from puremagic import PureMagicWithConfidence
from rich.status import Status
from rich.text import Text

ENTRY_STYLES: dict = {
    "special": {
        "inode/directory": {"style": "bold blue", "icon": ""},
        "inode/symlink": {"style": "blue", "icon": ""},
        "junction": {"style": "", "icon": ""},
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
            "icon": "",
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


IS_WINDOWS: bool = os.name == "nt"


def _is_dir_no_follow(path: Path) -> bool:
    """
    Check if path is a directory without following symlinks.
    Compatible with Python 3.12 and earlier.

    :param path: Entry path.
    :return: True if entry is a directory. Otherwise, false
    """

    try:
        st = path.lstat()
        return stat.S_ISDIR(st.st_mode)
    except (OSError, AttributeError):
        return False


def _is_file_no_follow(path: Path) -> bool:
    """
    Check if path is a regular file without following symlinks.
    Compatible with Python 3.12 and earlier.

    :param path: Entry path.
    :return: True if entry is a file. Otherwise, false
    """

    try:
        st = path.lstat()
        return stat.S_ISREG(st.st_mode)
    except (OSError, AttributeError):
        return False


def style_text(filename: str, mimetype: str, extension: str, no_icons: bool) -> Text:
    """
    Return a styled Rich Text object for a filename.

    :param filename: The entry's filename
    :param mimetype: The entry's mimetype or special type (e.g. "inode/directory")
    :param extension: File extension (lowercase, including dot)
    :param no_icons: Whether to hide icons
    """

    # Special types
    if mimetype in ENTRY_STYLES["special"]:
        style_info = ENTRY_STYLES["special"][mimetype]
        icon = "" if no_icons else style_info["icon"]
        return Text(
            f"{icon} {filename}" if icon else filename, style=style_info["style"]
        )

    # Extension-based groups
    for group in ENTRY_STYLES["groups"]:
        if extension in group["extensions"]:
            icon = "" if no_icons else group["icon"]
            return Text(
                f"{icon} {filename}" if icon else filename, style=group["style"]
            )

    # Fallback
    style_info = ENTRY_STYLES["special"]["file"]
    icon = "" if no_icons else style_info["icon"]
    return Text(f"{icon} {filename}" if icon else filename, style=style_info["style"])


class EntryStats:
    def __init__(self, path: Path, dt_now: datetime, dt_format: str, no_icons: bool):
        """
        Initialise the EntryStats object. Collects metadata for a given filesystem entry.

        :param path: Path object representing the file or directory
        :param dt_now: Current datetime for relative time calculations
        :param dt_format: Specify the datetime format (relative or locale)
        :param no_icons: Disable showing nerdfont icons in output
        """
        self.path = path
        self.dt_now = dt_now
        self.dt_format = dt_format
        self.no_icons = no_icons

        self._stat: os.stat_result = path.stat(follow_symlinks=False)
        self._load_metadata()

    def _load_metadata(self):
        """
        Load and process metadata for the entry.
        """

        st = self._stat

        # Basic file info
        self.filename: str = self.path.name
        self.size: str = humanize.naturalsize(value=st.st_size, binary=True)
        self.permissions: str = stat.filemode(st.st_mode)

        # inode + link count
        self.inode: int = st.st_ino
        self.hardlinks: int = st.st_nlink

        # Timestamps (with humanized formatting)
        atime: datetime = datetime.fromtimestamp(st.st_atime)
        self.atime: str = (
            humanize.naturaltime(self.dt_now - atime)
            if self.dt_format == "relative"
            else atime.strftime("%c")
        )

        mtime: datetime = datetime.fromtimestamp(st.st_mtime)
        self.mtime: str = (
            humanize.naturaltime(self.dt_now - mtime)
            if self.dt_format == "relative"
            else mtime.strftime("%c")
        )

        ctime: datetime = datetime.fromtimestamp(st.st_ctime)
        self.ctime: str = (
            humanize.naturaltime(self.dt_now - ctime)
            if self.dt_format == "relative"
            else ctime.strftime("%c")
        )

        # Owner (Unix) or UID fallback
        if pwd:
            try:
                self.owner: str = pwd.getpwuid(st.st_uid).pw_name
            except KeyError:
                self.owner = str(st.st_uid)
        else:
            self.owner = str(st.st_uid)

        # Group (Unix) or GID fallback
        if grp:
            try:
                self.group: str = grp.getgrgid(st.st_gid).gr_name
            except KeyError:
                self.group = str(st.st_gid)
        else:
            self.group = str(st.st_gid)

        # File type (via puremagic or fallback)
        self.mimetype, self.filetype = self._detect_type()

    def _detect_type(self) -> tuple[str, str]:
        """
        Detect the file type using PureMagic and prefer the match with highest confidence.
        """
        if self.path.is_dir(follow_symlinks=False):
            if not any(self.path.iterdir()):
                return "inode/directory", (
                    "Folder" if IS_WINDOWS else "Directory (Empty)"
                )
            return "inode/directory", "Folder" if IS_WINDOWS else "Directory"

        if self.path.is_symlink():
            return "inode/symlink", "Symbolic Link"

        if hasattr(self.path, "is_junction") and self.path.is_junction():
            return "inode/junction", "Junction"

        if self.path.is_file(follow_symlinks=False) and self.path.stat().st_size > 0:
            matches: list[PureMagicWithConfidence] = puremagic.magic_file(
                filename=str(self.path)
            )
            if matches:
                best_match: PureMagicWithConfidence = max(
                    matches, key=lambda m: m.confidence
                )
                return best_match.mime_type, best_match.name

        if self.path.is_file(follow_symlinks=False):
            if self._stat.st_size == 0:
                return "application/empty", "Empty File"

        return "application/octet-stream", "Unknown File"

    def style_name(self) -> Text:
        """
        Style this entry’s name based on its type and extension.
        """

        return style_text(
            filename=self.filename,
            mimetype=self.mimetype,
            extension=os.path.splitext(self.filename)[1].lower(),
            no_icons=self.no_icons,
        )


class EntryScanner:
    def __init__(
        self,
        path: Path,
        reverse: bool,
        show_all: bool,
        dirs_only: bool,
        files_only: bool,
        symlinks_only: bool,
        junctions_only: bool,
        no_icons: bool,
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
        :param no_icons: Disable showing nerdfont icons in output
        :param dt_now: Current datetime for relative time calculations
        :param dt_format: Specify the datetime format (relative or locale)
        """

        # disable junction filtering on non-Windows
        if not IS_WINDOWS:
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
        self.no_icons = no_icons

    def entries(self, directory: t.Union[str, Path]) -> t.Iterator[EntryStats]:
        """
        Iterate over directory entries, yielding EntryStats objects.

        :param directory: Directory path to scan
        :return: Iterator of EntryStats objects
        """
        entries: t.List[os.DirEntry] = list(os.scandir(directory))
        entries.sort(key=lambda e: e.name.lower(), reverse=self.reverse)

        with Status("...") as status:
            for entry in entries:
                if not self.show_all and entry.name.startswith("."):
                    continue
                if self.dirs_only and not entry.is_dir(follow_symlinks=False):
                    continue
                if self.files_only and not entry.is_file(follow_symlinks=False):
                    continue
                if self.symlinks_only and not entry.is_symlink():
                    continue
                if self.junctions_only and not (
                    IS_WINDOWS
                    and entry.is_symlink()
                    and entry.is_dir(follow_symlinks=False)
                ):
                    continue

                entry_stats = EntryStats(
                    path=Path(entry.path),
                    dt_now=self.dt_now,
                    dt_format=self.dt_format,
                    no_icons=self.no_icons,
                )
                status.update(
                    f"[bold]scanning[/bold]: [dim italic]{entry.name}[/dim italic]"
                )
                yield entry_stats

    def summary(self, entries: t.Iterable[EntryStats]) -> str:
        """
        Generate a human-readable summary of the scanned entries.

        :param entries: Iterable of EntryStats objects
        :return: Human-readable summary string
        """
        counts: Counter[str] = Counter()
        for entry in entries:
            if _is_dir_no_follow(path=entry.path):
                counts["directories"] += 1
            elif entry.path.is_symlink():
                if IS_WINDOWS and _is_dir_no_follow(entry.path):
                    counts["junctions"] += 1
                else:
                    counts["symlinks"] += 1
            else:
                counts["files"] += 1

        parts: list[str] = []
        if counts["directories"]:
            parts.append(
                f"{counts['directories']} director{'y' if counts['directories'] == 1 else 'ies'}"
            )
        if counts["files"]:
            parts.append(f"{counts['files']} file{'s' if counts['files'] != 1 else ''}")
        if counts["symlinks"]:
            parts.append(
                f"{counts['symlinks']} symlink{'s' if counts['symlinks'] != 1 else ''}"
            )
        if counts["junctions"]:
            parts.append(
                f"{counts['junctions']} junction{'s' if counts['junctions'] != 1 else ''}"
            )

        if len(parts) == 1:
            summary_msg: str = parts[0]
        else:
            summary_msg: str = ", ".join(parts[:-1]) + f", and {parts[-1]}"

        elapsed: str = humanize.naturaldelta(datetime.now() - self.dt_now)
        return f"scanned {summary_msg} in {elapsed}."
