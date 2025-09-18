Noticeable Changes Starting from Version 0.1.3

# 0.1.3

* Android icon for `.apk`, and `.xapk` files.
* Apple icon for `.app`, `.ipa`, and `.pkg` files.
* Added `.cjs` extensions for JavaScript files.

# 0.2.0

### Changed

- **CLI structure simplified**:  
  Removed `tree` / `table` subcommands. Instead:
    - `oak [PATH]` → shows a table view (default).
    - `oak -t [PATH]` → shows a tree view.

- Option names updated for consistency:
    - `--dirs` → `--directories`
    - `--group` → `--groups`
    - `--dt-format` values changed from `concise`/`locale` to `relative`/`locale` (`relative` being the default).

### Added

- `-h` as a short alias for `--help`.
- More informative error handling with friendly messages.
- Show filetype in table view... seriously, actually showing filetypes. There's an exhaustive process behind this.
- Show an informative message when a directory is empty.
- `--table-style` option to customize table border styles (options: `ASCII`, `ROUNDED`, `SQUARE`, `HEAVY`, `DOUBLE`,
  `SIMPLE`, `MINIMAL`; default: `ROUNDED`).
- `--version` option to display the current version of oakfs.

### Removed

- `--verbose` option (temporarily dropped, may return later).
- Shorthand `-T` for `--dt-format`.

# 0.3.0

### Changed

- Using `python-magic` to determine file types instead of manual mapping.
- Minimum Python version requirement increased to 3.12 from 3.11
- Bring back the `-v, --verbose` option to show debug information.
- Bring back the shorthand for `--dt-format` as `-D`.
- Refactor icon mapping logic for the `-N, --no-icons` option.

### Added

- `-T` shorthand for `--table-style`.
- `-N, --no-icons` option to enable/disable icons in the output.

# 0.3.1

### Patched

- Fix version string in __init__.py

# 0.4.0

### Changed

- Refactored the codebase to improve maintainability and readability.
- Showing nerdfont icons in the table headers

### Added

- `-m, --mimetypes` option to show entry mimetypes in the table.
- '-g, --groups' option to show entry groups in the table.
- `-o, --owners` option to show entry owners in the table.
- `-p, --permissions` option to show entry permissions in the table.

### Removed

- `python-magic` dependency. Now using `puremagic` for better cross-platform compatibility. (I recently found out that
  `python-magic` can be a pain to install or use on Windows systems).

# 0.4.1

### Changed

- Update README.md
- Spelling corrections, and minor updates in code