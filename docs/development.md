# Development setup

The repository has two Python projects. `plugin/` needs the Python of a QGIS
installation. `backend/` needs Python 3.13, Docker and GNU Make; its infrastructure
tools (Terraform, Ansible, sops, the AWS CLI) run on Linux and macOS only.

Use one clone for both parts, so that one branch can change both.

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

## Line endings

`.gitattributes` gives every text file LF line endings on every platform, whatever your
`core.autocrlf` setting is. Shell scripts and Makefiles with CRLF fail on Linux and in
Docker.

## Checks

Install the hooks once at the repository root with `pre-commit install`. The same config
runs in CI.
