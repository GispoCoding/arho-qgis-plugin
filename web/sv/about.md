# Om Arho

Arho är ett planläggningsverktyg baserat på öppen källkod som körs ovanpå QGIS. Det kan användas för att skapa datamodellbaserade planer som exporteras till det nationella Ryhti-systemet. Arho har utvecklats inom ramen för partnertestningsprojekt, och denna manual har skapats och uppdaterats inom samma projekt.

Denna manual innehåller instruktioner för hur du använder Arho. Manualen uppdateras i takt med att Arho utvecklas. Det finns en separat manual för ibruktagande och för huvudanvändare (på finska): [Arho tekninen ohje – käyttöönotto ja pääkäyttäjä](https://docs.google.com/document/d/1HaIzgdJiOIgSZ1bA6tcsnur_4W45OwxJv8bEWOxZIeM/edit?usp=sharing).

## Vad är Arho?

Arho är ett planläggningsverktyg baserat på öppen källkod som fungerar tillsammans med GIS-programvaran QGIS. Med verktyget kan man producera lagstadgad, datamodellbaserad plandata.

Arho är en helhet där användargränssnittet består av QGIS och insticksprogrammet (pluginet) Arho. En QGIS-projektfil som har utarbetats för Arho är en central del i användningen av programmet. Bakgrundssystemet (backend) har implementerats i molntjänsten AWS och innehåller:

- en databas där plandata sparas
- ett verktyg för uppdatering av kodverk
- verktyg för Ryhti-gränssnitt
- en SSH-tunnelserver
- ett verktyg för databashantering och databasmigrering
- (en anslutningsserver för informationsleden).

Arho är alltså inte bara ett insticksprogram, utan en helhet där alla delar behövs.

## Ibruktagande av Arho

För ibruktagandet av Arho finns en separat, mer teknisk manual som går igenom följande steg:

- skapande av SSH-tunnel och upprättande av anslutning (används i test- och experimenteringsmiljöer)
- skapande av en stödfil för databasanslutningen (`PGSERVICEFILE`)
- skapande av QGIS-profil, miljöinställningar i QGIS samt lagring av autentiseringsuppgifter i QGIS.
