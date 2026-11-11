# ARHO

Monorepo of ARHO, a land use planning system for the Finnish Ryhti data model.

- `plugin/`: the QGIS plugin `arho_feature_template`. Read `plugin/AGENTS.md` before work there.
- `backend/`: the PostGIS database, the AWS lambdas and the Terraform. Read
  `backend/AGENTS.md` before work there.
- `docs/`: documents about both sides. `docs/development.md` has the setup for
  Windows, macOS and Ubuntu.

Each side is its own Python project with its own `pyproject.toml`, virtual environment
and tests. Run the commands of a side from its folder.

## The contract between the sides

- Tables: the plugin edits the database through QGIS layers. `backend/database/models.py`
  and `backend/database/codes.py` define the tables that the plugin layers and
  `plugin/qgisprojekti.qgz` read and write.
- Lambda: the plugin calls the `ryhti_client` lambda.
  `backend/lambdas/ryhti_client/lambda_function.py` is the server side,
  `plugin/arho_feature_template/core/lambda_service.py` the client side, and
  `backend/docs/ryhti-client-jobs.md` the API.

Change both sides of a contract in the same pull request.

## Checks

- `pre-commit run --all-files` from the repository root. One config serves both sides;
  each ruff and mypy hook filters on `^plugin/` or `^backend/`.
- Each CI workflow in `.github/workflows/` has a `plugin-` or `backend-` prefix and a
  `paths:` filter. Add a path there when a workflow starts to depend on it.
- Text files use LF line endings on every platform (`.gitattributes`).

## Git

- Keep commit messages brief: a subject line, and body lines only for what the diff
  does not show.
- Commit messages and pull request descriptions carry no session link.
- Merge with a merge commit or a rebase when the history of the commits matters.
