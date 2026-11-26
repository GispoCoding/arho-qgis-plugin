# ARHO

ARHO is a land use planning system that is compatible with
[Ryhti](https://ryhti.syke.fi/en/), the Finnish national built environment information
system. This repository holds all its parts.

| Folder | What | License |
| --- | --- | --- |
| [`plugin/`](plugin/README.md) | QGIS plugin for drawing land use plans | [GPL v2](plugin/LICENSE) |
| [`backend/`](backend/README.md) | PostGIS database, AWS lambdas and Terraform | [MIT](backend/LICENSE) |
| [`web/`](web/README.md) | Website with the user manual, built with Zensical | [GPL v2](plugin/LICENSE) |

Each part is its own project, with its own `pyproject.toml` and virtual environment. Run
the commands of a part from its folder. The README of each part has its details.

## Documentation

The user manual is on the Arho website in Finnish and Swedish: <https://gispocoding.github.io/arho-qgis-plugin/>

## Development

Clone with the submodule of the plugin:

```console
git clone --recurse-submodules https://github.com/GispoCoding/arho.git
```

Then follow [docs/development.md](docs/development.md). It covers Windows, macOS and
Ubuntu.

One `pre-commit` config at the root checks all parts:

```console
pre-commit install
pre-commit run --all-files
```

Each CI workflow of a part runs only when that part changes (`plugin-*.yml`,
`backend-*.yml`, `web-*.yml`). When a workflow starts to depend on a new path, add the
path to the `paths:` filter of the workflow. `code-style.yml` runs on every pull request.

### Commit messages

- Start the subject with the part the commit changes: `plugin: `, `backend: `, `web: `,
  or `repo: ` for the shared root files. For example `plugin: Add a user manual action`.
- Split a change to several parts into one commit per part.
- Keep the message brief: a subject line, and body lines only for what the diff does
  not show.
- When an AI assistant helped, end the commit message and the pull request description
  with an `Assisted-by:` trailer that names the tool, for example
  `Assisted-by: Claude Code`.

### Contracts between the parts

Change both sides of a contract in the same pull request.

| Contract | One side | Other side |
| --- | --- | --- |
| Tables | `backend/database/models.py`, `backend/database/codes.py` | the plugin layers, `plugin/qgisprojekti.qgz` |
| Lambda | `backend/lambdas/ryhti_client/lambda_function.py`, `backend/docs/ryhti-client-jobs.md` | `plugin/arho_feature_template/core/lambda_service.py` |
| User manual | the `manual/` section of `web/` | `USER_MANUAL_URL` in `plugin/arho_feature_template/plugin.py` |

### Pull request labels

- The [labeler](.github/workflows/labeler.yml) workflow adds the `plugin`, `backend` and `web` labels by the paths a pull request
  changes.
- A changelog label is still required: `feature`, `enhancement`, `fix`, `bug`,
  `internal`, `chore`, `documentation` or `skip-changelog`. The branch prefixes
  `feature/`, `fix/` and `chore/` add one automatically.

### Releases

For now, the releases of this repository are plugin releases only. The [Release
Drafter](.github/workflows/release-drafter.yml) workflow lists only pull requests that change `plugin/`, and a published `v<version>` release
runs `plugin-release.yml`. The release strategy of the backend will be defined later.
