---
template: home.html
hero_title: Arho
hero_text: Datamodellbaserad planläggning med QGIS.
hero_buttons:
  - text: Läs användarmanualen
    link: manual/
  - text: Källkoden på GitHub
    href: https://github.com/GispoCoding/arho-qgis-plugin
hide:
  - navigation
  - toc
---

Arho är ett verktyg med öppen källkod för planläggare. Med Arho gör du en datamodellbaserad plan i QGIS, validerar den och för den till Ryhti-systemet. Läs mer [om Arho](about/index.md).
{ .arho-lead }

## Vad kan man göra med Arho? { #features }

<div class="grid cards arho-features" markdown>

-   :lucide-map-pinned: **Planobjekt och bestämmelser**

    Rita eller importera planobjekt och koppla planbestämmelsegrupper till dem, till exempel färdiga grupper enligt Katja-förordningen.

    [Planobjekt](manual/plan-objects.md), [Planbestämmelsegrupper](manual/regulation-groups.md)

-   :lucide-library-big: **Bibliotek**

    Spara ofta använda planbestämmelsegrupper och planobjekt som mallar i ett bibliotek och använd dem igen.

    [Bibliotek](manual/libraries.md)

-   :lucide-refresh-cw: **Livscykel**

    Gör ett planutkast för varje livscykelskede från anhängiggörande till ikraftträdande, även planändringar med uppgifter om upphävande.

    [Livscykelskeden](manual/lifecycle/index.md), [Planändring](manual/plan-amendment.md)

-   :lucide-list-checks: **Validering**

    Kontrollera planen mot Ryhtis plandatamodell och se det felaktiga objektet på kartan.

    [Validering](manual/validation.md)

-   :lucide-cloud-upload: **Ryhti**

    Spara planen som en JSON-fil i Ryhti-format och validera planärendet via informationsleden.

    [Export till JSON](manual/plan/export.md), [Informationsleden](manual/ryhti.md)

-   :lucide-palette: **Visualiseringar**

    Visa planen på kartan med regelbaserade stilar och gör en bestämmelsedel och en plankarta av den.

    [Visualiseringar](manual/styling/index.md), [Bestämmelsedel](manual/legend.md), [Plankarta](manual/geotiff.md)

</div>
