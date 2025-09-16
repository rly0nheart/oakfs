# Noticeable Changes Starting from Version 0.1.3

## 0.1.3

* Android icon for `.apk`, and `.xapk` files.
* Apple icon for `.app`, `.ipa`, and `.pkg` files.
* Added `.cjs` extensions for JavaScript files.

## 0.2.0

### Changed

- **CLI structure simplified**:  
  Removed `tree` / `table` subcommands. Instead:
    - `oak [PATH]` → shows a table view (default).
    - `oak -t [PATH]` → shows a tree view.
    - Shorthand `-T` for `--dt-format`.
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