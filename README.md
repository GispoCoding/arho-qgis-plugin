# ARHO feature template
![tests](https://github.com/GispoCoding/arho-feature-template/workflows/Tests/badge.svg)
[![codecov.io](https://codecov.io/github/GispoCoding/arho-feature-template/coverage.svg?branch=main)](https://codecov.io/github/GispoCoding/arho-feature-template?branch=main)
![release](https://github.com/GispoCoding/arho-feature-template/workflows/Release/badge.svg)

[![GPLv2 license](https://img.shields.io/badge/License-GPLv2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

## Development

Create a virtual environment activate it and install needed dependencies with the following commands:
```console
python create_qgis_venv.py
.venv\Scripts\activate # On Linux and macOS run `source .venv\bin\activate`
pip install -r requirements-dev.txt
```

For more detailed development instructions see [development](docs/development.md).

### Testing the plugin on QGIS

A symbolic link / directory junction should be made to the directory containing the installed plugins pointing to the dev plugin package.

On Windows Command promt
```console
mklink /J %AppData%\QGIS\QGIS3\profiles\default\python\plugins\arho_feature_template .\src\arho_feature_template
```

On Windows PowerShell
```console
New-Item -ItemType SymbolicLink -Path ${env:APPDATA}\QGIS\QGIS3\profiles\default\python\plugins\arho_feature_template -Value ${pwd}\src\arho_feature_template
```

On Linux
```console
ln -s src/arho_feature_template/ ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/arho_feature_template
```

After that you should be able to enable the plugin in the QGIS Plugin Manager.

### VsCode setup

On VS Code use the workspace [arho-feature-template.code-workspace](arho-feature-template.code-workspace).
The workspace contains all the settings and extensions needed for development.

Select the Python interpreter with Command Palette (Ctrl+Shift+P). Select `Python: Select Interpreter` and choose
the one with the path `.venv\Scripts\python.exe`.

## License
This plugin is distributed under the terms of the [GNU General Public License, version 2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html) license.

See [LICENSE](LICENSE) for more information.
