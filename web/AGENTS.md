# ARHO website

Website with the user manual of the ARHO plugin, in Finnish and Swedish, built with
Zensical. `README.md` has the layout, the writing rules and the commands: read it before
you add or change a page.

Run everything from `web/`.

## Rules

- The manual describes the plugin in `../plugin/`. Take button names, menu paths and
  dialog texts from its code and `.ui` files.
- The site addresses use the GitHub Pages path `arho-qgis-plugin`, the current repository
  name. Keep them as they are until the repository is renamed.

## Check

`uv run --no-project --with-requirements requirements.txt python build.py --strict`
passes. It is the build of `.github/workflows/web-pages.yml` and fails on a broken link
or a missing image. Then run `pre-commit run --all-files` from the repository root.
