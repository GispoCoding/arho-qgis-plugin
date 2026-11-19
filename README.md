# ARHO

ARHO is a land use planning system that is compatible with
[Ryhti](https://ryhti.syke.fi/en/), the Finnish national built environment information
system. This repository holds both parts of it.

| Folder | What | License |
| --- | --- | --- |
| [`plugin/`](plugin/README.md) | QGIS plugin for drawing land use plans | [GPL v2](plugin/LICENSE) |
| [`backend/`](backend/README.md) | PostGIS database, AWS lambdas and Terraform | [MIT](backend/LICENSE) |

Each part is its own Python project. The README of each part has its details.

## Documentation

The user manual is on the Arho website in Finnish and Swedish: <https://gispocoding.github.io/arho-qgis-plugin/>

## Development

Clone with the submodule of the plugin:

```console
git clone --recurse-submodules https://github.com/GispoCoding/arho.git
```

Then follow [docs/development.md](docs/development.md). It covers Windows, macOS and
Ubuntu.

One `pre-commit` config at the root checks both parts:

```console
pre-commit install
pre-commit run --all-files
```

Each CI workflow runs only when its own part changes (`plugin-*.yml`, `backend-*.yml`).
The releases of this repository are plugin releases.
