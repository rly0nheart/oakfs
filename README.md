<p align="center">
  <img src="https://i.imgur.com/BpRXcOW.png" alt="oakfs logo" width="350"/>
  <br>
  <strong>Oakfs</strong> is a humane CLI-based filesystem exploration tool, for humans.<br/>
  It provides a colourful, human-friendly way to explore your filesystem in the terminal using either a <b>tree</b> or <b>table view</b>.
</p>

## ✨ Features

- 🌳 **Tree view**: Visualise your filesystem hierarchy like `tree` but prettier.
- 📊 **Table view**: Display directories in a sortable table with file size, type, permissions, and modified time.
- 🎨 **Rich styling**: Icons and colours for file types (documents, images, audio, code, archives, etc.).
- 🔍 **Filtering**:
    - `-a, --all`: include hidden files
    - `-d, --directories`: show only directories
    - `-f, --files`: show only files
    - `-s, --symlinks`: show only symlinks
    - `-j, --junctions`: show only junctions (Windows)

- 👥 **Ownership info**: Show owner, group, and permissions with `--groups`.
- 🕒 **Timestamps**: Choose between `relative` relative times (`3 minutes ago`) or `locale` formatted dates.
- 🔄 **Sorting**: Reverse order with `--reverse`.

> [!Note]
> To make your experience more pleasant, you'll need to have Nerd Fonts installed. Check out
> the [Nerd Fonts website](https://www.nerdfonts.com/) for instructions on how to install them.

## 📦 Installation

**Oakfs** is available on [PyPI](https://pypi.org/project/pypi), and can be installed with pip:

```bash
pip install oakfs
```

This will install `oak` as a CLI command.

## 🚀 Usage

Run `oak` from the command line:

### Table view (default)

```bash
oak [PATH]
```

Example:

```bash
oak ~/projects
```

### Tree view

```bash
oak --tree [PATH]
```

Example:

```bash
oak --tree ~/projects
```

> [!Note]
> If no path is provided, it defaults to the current working directory.

> [!Tip]
> If you decide not to install Nerd Fonts (because you've decided to become a caveperson for some reason), you can
> always run oak with the `-N, --no-icons` option.
> This will help you embrace the **unga bunga** in you.

## ⚙️ Options

| Option                                                                        | Description                                        |
|-------------------------------------------------------------------------------|----------------------------------------------------|
| `-t, --tree`                                                                  | show filesystem hierarchy in a tree view structure |
| `-a, --all`                                                                   | show hidden files and/or directories               |
| `-f, --files`                                                                 | show files only                                    |
| `-d, --directories`                                                           | show directories only                              |
| `-s, --symlinks`                                                              | show symlinks only                                 |
| `-j, --junctions`                                                             | show junctions only <Windows>                      |
| `-r, --reverse`                                                               | reverse sort order                                 |
| `-g, --groups`                                                                | show groups                                        |
| `-o, --owners`                                                                | show owners                                        |
| `-p, --permissions`                                                           | show permissions                                   |
| `-m, --mimetypes`                                                             | show mimetypes                                     |
| `-v, --verbose`                                                               | enable verbose output                              |
| `-N, --no-icons`                                                              | disable showing icons in output                    |
| `-D, --dt-format [relative\|locale]`                                          | output datetime format (default:                   |
| relative)                                                                     |                                                    |
| `-T, --table-style  [ASCII\|ROUNDED\|SQUARE\|HEAVY\|DOUBLE\|SIMPLE\|MINIMAL]` | table border style (default:                       |
| ROUNDED)                                                                      |                                                    |
| `-h, --help`                                                                  | show help message and exit                         |
| `--version`                                                                   | show version and exit                              |

> [!Note]
> The following options are available only in the default (table) view: `-o, --owners`, `-p, --permissions`,
`-g, --groups`, `-m, --mimetypes`, `-D, --dt-format`, and obviously `-T, --table-style`


<p align="center">
  <strong>ok. that's all (for now).</strong>
</p>