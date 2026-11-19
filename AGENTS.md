# ARHO

Monorepo of ARHO, a land use planning system for the Finnish Ryhti data model.

- `plugin/`: the QGIS plugin `arho_feature_template`. Read `plugin/AGENTS.md` before work there.
- `backend/`: the PostGIS database, the AWS lambdas and the Terraform. Read
  `backend/AGENTS.md` before work there.
- `web/`: the website with the user manual of the plugin, built with Zensical. Read
  `web/AGENTS.md` before work there.
- `docs/`: documents about all parts. `docs/development.md` has the setup for
  Windows, macOS and Ubuntu.

Each part is its own project with its own `pyproject.toml` and virtual environment.
Run the commands of a part from its folder.

## Contracts between the parts

- Tables: the plugin edits the database through QGIS layers. `backend/database/models.py`
  and `backend/database/codes.py` define the tables that the plugin layers and
  `plugin/qgisprojekti.qgz` read and write.
- Lambda: the plugin calls the `ryhti_client` lambda.
  `backend/lambdas/ryhti_client/lambda_function.py` is the server side,
  `plugin/arho_feature_template/core/lambda_service.py` the client side, and
  `backend/docs/ryhti-client-jobs.md` the API.
- User manual: `USER_MANUAL_URL` in `plugin/arho_feature_template/plugin.py` opens the
  `manual/` section of the website in `web/`.

Change both sides of a contract in the same pull request.

## Checks

- `pre-commit run --all-files` from the repository root. One config serves all parts;
  each ruff and mypy hook filters on `^plugin/`, `^backend/` or `^web/`.
- A CI workflow in `.github/workflows/` that serves one part has a `plugin-`, `backend-`
  or `web-` prefix and a `paths:` filter. Add a path there when a workflow starts to
  depend on it.
- Text files use LF line endings on every platform (`.gitattributes`).

## Git

- Keep commit messages brief: a subject line, and body lines only for what the diff
  does not show.
- Start the subject with the part the commit changes: `plugin: `, `backend: `, `web: `,
  or `repo: ` for the shared root files (`AGENTS.md`, `.github/`, `docs/`). A workflow
  that serves one part takes that part's prefix. Split a change to several parts into one
  commit per part.
- End every commit message and pull request description with the line
  `Assisted-by: Claude Code`. It replaces the `Co-Authored-By` trailer and the session
  link: those stay out.
- Merge with a merge commit or a rebase when the history of the commits matters.
