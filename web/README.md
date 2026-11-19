# ARHO website

The website of ARHO with the user manual of the ARHO plugin, in Finnish and Swedish, built with
[Zensical](https://zensical.org/) and published on GitHub Pages:

- Finnish: <https://gispocoding.github.io/arho-qgis-plugin/>
- Swedish: <https://gispocoding.github.io/arho-qgis-plugin/sv/>

The Markdown files here are the only source. There is no Word version.

## Edit a page

1. Open the page on the site and click the pencil button ("Muokkaa tätä sivua" / "Redigera sidan").
2. GitHub opens the file in its editor. Make the change.
3. Propose the change. It becomes a pull request. After the merge to `main`, the site updates in a few minutes.

## Layout

| Path | What |
|---|---|
| `fi/`, `sv/` | Pages, one folder per language. The same file name in both, for example `fi/manual/plan/create.md` and `sv/manual/plan/create.md`. |
| `fi/index.md`, `sv/index.md` | Home page (tab "Etusivu" / "Startsida"). The band title, text and buttons are in the front matter (see `overrides/home.html`). |
| `fi/about/`, `sv/about/` | About Arho and its deployment (tab "Arhosta" / "Om Arho"). |
| `fi/manual/`, `sv/manual/` | The user manual (tab "Käyttöohje" / "Användarmanual"). |
| `fi/manual/images/` | All screenshots, shared by both languages. `build.py` copies them to `sv/manual/images/` (not in git). |
| `zensical-base.yml` | Settings shared by both sites. |
| `zensical-fi.yml`, `zensical-sv.yml` | Site name, address and menu (`nav`, one top item per tab) of each language. |
| `overrides/` | Gispo look: CSS, templates, logos, favicon, language switch script. |
| `build.py` | Builds both sites into `site/` (Finnish) and `site/sv/` (Swedish). |
| `requirements.txt` | The pinned Zensical version. |
| `pyproject.toml` | The ruff settings of `build.py`. |

## Writing rules

- **New page**: add the file in both languages and add it to `nav` in both `zensical-fi.yml` and `zensical-sv.yml`. Use a short English file name without ä or ö.
- **Not translated yet**: if the Swedish text is missing, add a Swedish page with only the title and this box:

  ```markdown
  !!! info "Inte översatt ännu"

      Det här kapitlet finns bara på finska än så länge. Läs den finska versionen: [Otsikko](/arho-qgis-plugin/manual/<path>/).
  ```

- **Screenshots**: put the PNG file in `fi/manual/images/` with a name that starts with the page name, for example `plan-create-11.png`. Every image needs an alt text in the page language: `![Kaavasuunnitelma-valikko auki](../images/plan-create-11.png)`. A small button inside a sentence gets `{ .icon }`: `![Tallenna-painike](images/plan-export-3.png){ .icon }`. For a smaller image, add a width in pixels: `{ width="400" }`.
- **Features that are not released yet**: put the new text in a box, so readers know which version has it:

  ```markdown
  !!! new "Uusi versiossa 1.5"

      Tekstiä uudesta toiminnosta.
  ```

  In Swedish: `!!! new "Nytt i version 1.5"`. Remove the box some releases later.
- **Other boxes**: `!!! tip "Vinkki"` / `"Tips"`, `!!! note "Huomaa"` / `"Observera"`, `!!! warning "Huom."` / `"Obs!"`.
- **Links between pages**: use the relative path of the Markdown file, for example `[Kaava-asia](../plan-matter.md)`. A heading that other pages link to gets a fixed English id: `## Kaavakohdepaneeli { #panel }`.

## Build and preview locally

From `web/`, with [uv](https://docs.astral.sh/uv/):

```console
uv run --no-project --with-requirements requirements.txt python build.py --serve
```

Open <http://localhost:8000/arho-qgis-plugin/>. Run the command again after changes.
For live reload of the Finnish site, use `zensical serve` (the language switch and,
for the Swedish site, the screenshots work only through `build.py`):

```console
uv run --no-project --with-requirements requirements.txt zensical serve -f zensical-fi.yml
```

## Publish

`.github/workflows/web-pages.yml` builds and publishes the site when a push to `main`
changes `web/` or the workflow file. To publish without a change, open
**Actions > Website > Run workflow**. A pull request that changes `web/`
gets a build check that fails on warnings, for example a broken link or a missing image.

## Privacy

Visitors' browsers load files only from the site itself. The `privacy` plugin
downloads the Google fonts (Inter, Karla, JetBrains Mono) and the image zoom script at build time,
and `overrides/partials/source.html` shows the GitHub repository link without the
star and fork counts, which the theme would fetch from the GitHub API.
Do not add scripts, fonts or images from other servers.

## Update Zensical

Zensical is in beta and releases often, so the version is pinned in `requirements.txt`.
To update: change the version, build locally, check both languages in light and dark mode,
and then commit.
