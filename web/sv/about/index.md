# Om Arho

Arho är ett verktyg för planläggare. Med Arho gör man datamodellbaserade planer i QGIS och för dem till det nationella Ryhti-systemet. Arho är öppen källkod.

Arho är fortfarande under utveckling. Nya funktioner tillkommer, och befintliga funktioner kan ändras.

## Varför Arho? { #why }

Lagen förpliktar kommunerna och landskapsförbunden att producera plandata i datamodellbaserad form till Datasystemet för den byggda miljön, Ryhti. Plandata kan redan nu föras till Ryhti, och från och med år 2029 är det obligatoriskt. Med Arho gör planläggaren en datamodellbaserad plan i den välbekanta QGIS-miljön, validerar den och för den till Ryhti.

## Vad består Arho av? { #parts }

Arho är inte bara ett insticksprogram. Det är en helhet där alla delar behövs:

- **QGIS**: ett GIS-program med öppen källkod där planen görs.
- **Insticksprogrammet Arho**: ett insticksprogram för QGIS med verktygen för att göra planen.
- **Arhos QGIS-projektfil** (projektet *kaavoitus*): kartlager och inställningar som Arho behöver.
- **Bakgrundssystemet** (backend), som körs i molntjänsten AWS. Det innehåller:
    - en databas där plandata sparas
    - ett verktyg för uppdatering av kodverk
    - verktyg för Ryhti-gränssnitt
    - en SSH-tunnelserver
    - ett verktyg för databashantering och databasmigrering
    - vid behov en anslutningsserver för informationsleden.

## Öppen källkod och deltagande { #open-source }

Arhos källkod är öppen:

- Insticksprogrammet Arho: [GispoCoding/arho-qgis-plugin](https://github.com/GispoCoding/arho-qgis-plugin), licens GPL v2
- Bakgrundssystemet: [GispoCoding/arho-backend](https://github.com/GispoCoding/arho-backend), licens MIT

Så här kan du delta:

- Rapportera ett fel eller föreslå en förbättring som ett issue på GitHub: [insticksprogrammet](https://github.com/GispoCoding/arho-qgis-plugin/issues), [bakgrundssystemet](https://github.com/GispoCoding/arho-backend/issues).
- Rätta den här manualen: knappen för redigering uppe till höger på sidan öppnar sidan på GitHub.

Gispo utvecklar Arho tillsammans med de organisationer som använder det, i partnerutvecklingsprojekt.

Läs sedan hur Arho [tas i bruk](deployment.md).
