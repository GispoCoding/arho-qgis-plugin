# ARHO feature template
![tests](https://github.com/GispoCoding/arho/actions/workflows/plugin-tests.yml/badge.svg)
[![codecov.io](https://codecov.io/github/GispoCoding/arho-feature-template/coverage.svg?branch=main)](https://codecov.io/github/GispoCoding/arho-feature-template?branch=main)
![release](https://github.com/GispoCoding/arho/actions/workflows/plugin-release.yml/badge.svg)

[![GPLv2 license](https://img.shields.io/badge/License-GPLv2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

This is a QGIS plugin for producing land use plans and is compatible with [Ryhti](https://ryhti.syke.fi/en/), the Finnish national built environment information system.

The plugin supports QGIS 3.40 (LTR) and newer, including QGIS 4.

The plugin is used with the [ARHO backend](../backend/README.md), which provides the necessary database and backend services.

## Development

The plugin is in the `plugin/` folder of the ARHO repository. Clone the repository with
the [qgis_plugin_tools](https://github.com/GispoCoding/qgis_plugin_tools) submodule:

```
git clone --recurse-submodules https://github.com/GispoCoding/arho.git
```

[docs/development.md](../docs/development.md) has the setup for Windows, macOS and
Ubuntu: the virtual environment, the link from the QGIS profile to the plugin package,
and the tests.

### Backend setup

Use a local backend for development. It is in the [`backend/`](../backend/README.md)
folder of this repository and runs in Docker containers.

### VsCode setup

On VS Code open the `plugin/` folder with the workspace [arho-feature-template.code-workspace](arho-feature-template.code-workspace).
The workspace contains all the settings and extensions needed for development.

Select the Python interpreter with Command Palette (Ctrl+Shift+P). Select `Python: Select Interpreter` and choose
the one with the path `.venv\Scripts\python.exe`.

## License
This plugin is distributed under the terms of the [GNU General Public License, version 2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html) license.

See [LICENSE](LICENSE) for more information.

### Attributations
<a href="https://www.flaticon.com/free-icons/open" title="open icons">Open icons created by Smashicons - Flaticon</a>
<a href="https://www.flaticon.com/free-icons/land-use" title="land use icons">Land use icons created by Fusion5085 - Flaticon</a>
