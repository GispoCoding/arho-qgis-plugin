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
pip install -r requirements-dev.txt -r requirements-test.txt
```

For more detailed development instructions see [development](docs/development.md).

### Testing the plugin on QGIS

A symbolic link / directory junction should be created to the directory containing the installed plugins pointing to the dev plugin package.

It is recomennded also to use a specifig QGIS profile for development.

On Windows Command promt
```console
set QGIS_PROFILE=arho-dev
mkdir -p %AppData%\QGIS\QGIS3\profiles\%QGIS_PROFILE%\python\plugins
mklink /J %AppData%\QGIS\QGIS3\profiles\%QGIS_PROFILE%\python\plugins\arho_feature_template .\arho_feature_template
C:\OSGeo4W\bin\qgis-ltr.bat --profile %QGIS_PROFILE%
```

On Windows PowerShell
```console
$env:QGIS_PROFILE = "arho-dev"
New-Item -ItemType Directory -Force ${env:APPDATA}\QGIS\QGIS3\profiles\${env:QGIS_PROFILE}\python\plugins
New-Item -ItemType Junction -Path ${env:APPDATA}\QGIS\QGIS3\profiles\${env:QGIS_PROFILE}\python\plugins\arho_feature_template -Value ${pwd}\arho_feature_template
C:\OSGeo4W\bin\qgis-ltr.bat --profile $env:QGIS_PROFILE
```

On Linux
```console
export QGIS_PROFILE=arho-dev
ln -s arho_feature_template/ ~/.local/share/QGIS/QGIS3/profiles/$QGIS_PROFILE/python/plugins/arho_feature_template
qgis --profile $QGIS_PROFILE
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

### Attributations
<a href="https://www.flaticon.com/free-icons/open" title="open icons">Open icons created by Smashicons - Flaticon</a>
<a href="https://www.flaticon.com/free-icons/land-use" title="land use icons">Land use icons created by Fusion5085 - Flaticon</a>
