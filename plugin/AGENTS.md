# ARHO feature template (QGIS plugin)

QGIS plugin, Python package `arho_feature_template`. It must run on QGIS 3 (Qt 5 / PyQt5)
and QGIS 4 (Qt 6 / PyQt6). `arho_feature_template/qgis_plugin_tools` is a git submodule:
change it in its own repository.

`CONTEXT.md` has the domain terms in Finnish and English.

## Skills

- Use the `pyqgis-dev` skill for any PyQGIS, PyQt or `.ui` work. Check every API fact
  against the live QGIS Python, the SIP files or the sources; stubs and memory are wrong
  too often.
- Use the `qgis4-migration` skill for QGIS 4 / Qt 6 compatibility work.

## Pythons and commands

Run everything from `plugin/`. The paths below are for Windows; on macOS and Linux the
interpreter is `.venv/bin/python`.

- `.venv\Scripts\python.exe` = QGIS 3 / Qt 5 (main). `.venv-qt6\Scripts\python.exe` = QGIS 4 / Qt 6.
- Tests: `.venv\Scripts\python.exe -m pytest tests -q`, then the same with `.venv-qt6`.
- Lint and format: `pre-commit run --all-files` from the repository root (ruff, ruff-format, mypy).
- `.ui` files: `check_ui.py` from the `pyqgis-dev` skill under both Pythons, then `render_ui.py` to look.

## Rules

- Import Qt only through `qgis.PyQt`. Scoped enums. `exec()`, not `exec_()`.
- Nulls: `QgsVariantUtils.isNull(v)` or `v == NULL`. `v is None` misses the `QVariant`
  that Qt 5 gives.
- Custom widgets used in `.ui` files take `parent=None` as their first argument.
- Ownership: store map tools, layers shown in a canvas, and parent-less QObjects on `self`.
- `qgisprojekti.qgz` is saved with QGIS 3.40; a pre-commit hook checks it.

## Release

A published GitHub release with a `v<version>` tag starts
`.github/workflows/plugin-release.yml`. It copies `plugin/` into a throwaway repository,
because `qgis-plugin-ci` needs the package at the top of a repository.
