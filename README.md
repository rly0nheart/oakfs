<p align="center">
  <img src="https://i.imgur.com/BpRXcOW.png" alt="oakfs logo" width="350"/>
  <br>
  <strong>oakfs</strong> is a cute filesystem visualisation tool... for cute humans 🙂.<br/>
  It provides a colorful, human-friendly way to explore your filesystem in the terminal using either a <b>tree view</b> or a <b>table view</b>.
</p>

## ✨ Features

- 🌳 **Tree view**: Visualise your filesystem hierarchy like `tree` but prettier.
- 📊 **Table view**: Display directories in a sortable table with file size, type, permissions, and modified time.
- 🎨 **Rich styling**: Icons and colors for file types (documents, images, audio, code, archives, etc.).
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

oakfs is available on [PyPI](https://pypi.org/project/pypi). You can install it using pip:

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

## ⚙️ Options

| Option                                                                    | Description                                        |
|---------------------------------------------------------------------------|----------------------------------------------------|
| `-t, --tree`                                                              | show filesystem hierarchy in a tree view structure |
| `-f, --files`                                                             | show files only                                    |
| `-d, --directories`                                                       | show directories only                              |
| `-s, --symlinks`                                                          | show symlinks only                                 |
| `-j, --junctions`                                                         | show junctions only <Windows>                      |
| `-a, --all`                                                               | show hidden files and directories                  |
| `-g, --groups`                                                            | show file owner, group, and permissions            |
| `--dt-format [relative\|locale]`                                          | format modified date/time (default: relative)      |
| `--table-style  [ASCII\|ROUNDED\|SQUARE\|HEAVY\|DOUBLE\|SIMPLE\|MINIMAL]` | table border style (default: ROUNDED)              |
| `-r, --reverse`                                                           | reverse sort order                                 |
| `-h, --help`                                                              | show help message and exit                         |
| `--version`                                                               | show version and exit                              |

<p align="center">
  <strong>ok. that's all (for now).</strong>
</p>