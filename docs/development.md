# Development setup

The repository has three projects. `plugin/` needs the Python of a QGIS
installation. `backend/` needs Python 3.13, Docker and GNU Make; its infrastructure
tools (Terraform, Ansible, sops, the AWS CLI) run on Linux and macOS only. `web/` needs
[uv](https://docs.astral.sh/uv/).

Use one clone for all parts, so that one branch can change several.

## Where to clone

| Platform | Clone location | Backend tools run in |
| --- | --- | --- |
| Ubuntu | anywhere | the same shell |
| macOS | anywhere | the same shell |
| Windows | a Windows drive, for example `D:\projects\arho` | WSL 2, at `/mnt/d/projects/arho/backend` |

On Windows the clone stays on a Windows drive because QGIS links the plugin folder into
its profile, and a link from Windows into the WSL file system does not work.

## Plugin

All commands run in `plugin/`.

1. Create the virtual environment from your QGIS installation and install the
   dependencies.

   Windows (PowerShell):

   ```console
   python create_qgis_venv.py
   .venv\Scripts\activate
   pip install -r requirements-dev.txt -r requirements-test.txt
   ```

   macOS and Ubuntu:

   ```console
   python3 create_qgis_venv.py
   source .venv/bin/activate
   pip install -r requirements-dev.txt -r requirements-test.txt
   ```

2. Link the plugin package into a QGIS profile. Use a profile of its own, for example
   `arho-dev`. For QGIS 4 the folder is `QGIS4` instead of `QGIS3`.

   Windows (PowerShell; a junction needs no administrator rights):

   ```console
   $plugins = "$env:APPDATA\QGIS\QGIS3\profiles\arho-dev\python\plugins"
   New-Item -ItemType Directory -Force $plugins
   New-Item -ItemType Junction -Path "$plugins\arho_feature_template" -Value "$pwd\arho_feature_template"
   ```

   macOS:

   ```console
   plugins="$HOME/Library/Application Support/QGIS/QGIS3/profiles/arho-dev/python/plugins"
   mkdir -p "$plugins"
   ln -s "$PWD/arho_feature_template" "$plugins/arho_feature_template"
   ```

   Ubuntu:

   ```console
   plugins="$HOME/.local/share/QGIS/QGIS3/profiles/arho-dev/python/plugins"
   mkdir -p "$plugins"
   ln -s "$PWD/arho_feature_template" "$plugins/arho_feature_template"
   ```

3. Start QGIS with `--profile arho-dev` and enable the plugin in the plugin manager.

4. Run the tests: `python -m pytest tests -q`.

## Backend

All commands run in `backend/`. [backend/README.md](../backend/README.md) has the steps
(virtual environment, `.env`, `make dev-setup-db`, tests).

### Windows: run the backend in WSL 2

1. Install WSL 2 with Ubuntu, and Docker Desktop with the WSL integration on (or Docker
   inside WSL).
2. In WSL, go to the clone on the Windows drive:

   ```console
   cd /mnt/d/projects/arho/backend
   ```

3. Keep the virtual environment in the WSL home folder. A virtual environment on
   `/mnt/` is slow.

   ```console
   python3.13 -m venv ~/.venvs/arho-backend
   source ~/.venvs/arho-backend/bin/activate
   pip install pip-tools
   pip-sync requirements.txt requirements-dev.txt
   ```

4. Run `make`, `pytest`, Terraform and Ansible from that WSL shell.
5. Run `git` from Windows only. The Windows git and the WSL git do not agree on file
   modes, so a second git on the same clone shows changes that are not there.

The files of the repository are small, so the slower `/mnt/` file access costs little.
If it is too slow for you, make a second clone in the WSL home folder for backend work.

### macOS and Ubuntu

Install Python 3.13, Docker and GNU Make, then follow
[backend/README.md](../backend/README.md) directly.

## Web

All commands run in `web/`, on every platform. [web/README.md](../web/README.md) has the
build, the local preview and the writing rules.

## VS Code

Open `arho.code-workspace` at the repository root (**File > Open Workspace from File**).
Opening the root or one side as a plain folder gives none of the team settings.

The workspace has four folders: `plugin`, `backend`, `web` and `arho (root)` for the
shared files. Each part has its own Python interpreter and ruff configuration; the plugin
and the backend also have their own test tree and mypy configuration.

### Interpreters

Run **Python: Select Interpreter** once for each part and pick the `.venv` of that folder.

| Folder | Interpreter | Made with |
| --- | --- | --- |
| `plugin` | `plugin/.venv` (QGIS 3) | `create_qgis_venv.py`, see [Plugin](#plugin) |
| `backend` | `backend/.venv` (Python 3.13) | see [backend/README.md](../backend/README.md) |
| `web` | `web/.venv` (for the editor only) | `uv venv` and `uv pip install -r requirements.txt` in `web/` |

The Test Explorer runs the plugin tests with `plugin/.venv`. For the QGIS 4 tests run
the task **plugin: pytest (Qt 6)** (**Terminal > Run Task**), which uses
`plugin/.venv-qt6`.

On Windows the backend runs in WSL, and a Windows VS Code window cannot use the WSL
virtual environment. Make a second one for the editor only, with a Windows Python 3.13:

```console
cd backend
py -3.13 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
```

It gives code completion, ruff and mypy in the editor. Keep running `make` and `pytest`
in the WSL shell. If `ansible-core` does not install on Windows, remove its lines from a
copy of `requirements-dev.txt` and install from the copy: the editor does not need it.

### Debugging

| Launch configuration | Attaches to | Port |
| --- | --- | --- |
| plugin: attach to QGIS | QGIS started with `QGIS_PLUGIN_USE_DEBUGGER=debugpy` and the profile `arho-dev` | 5678 |
| backend: attach to ryhti_client (docker) | the container started with `make dev-debug-ryhti` | 5679 |

Both can be attached at the same time.

### Team and personal settings

- Team settings, launch configurations, tasks and extension recommendations are in
  `arho.code-workspace`.
- Personal settings go into `plugin/.vscode/settings.json`,
  `backend/.vscode/settings.json` and `web/.vscode/settings.json`. Git ignores those
  folders, and their settings win over the workspace file.
- In the Settings editor, use the **Folder** tab for a personal setting. The
  **Workspace** tab writes to `arho.code-workspace`.
- `.vscode/settings.json` at the repository root is tracked. It holds the settings of
  the `arho (root)` folder only.

## Line endings

`.gitattributes` gives every text file LF line endings on every platform, whatever your
`core.autocrlf` setting is. Shell scripts and Makefiles with CRLF fail on Linux and in
Docker.

## Checks

Install the hooks once at the repository root with `pre-commit install`. The same config
runs in CI.
