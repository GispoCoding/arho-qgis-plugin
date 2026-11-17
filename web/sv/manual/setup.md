# Ibruktagande

Innan du börjar använda Arho behöver du QGIS, insticksprogrammet Arho och en fungerande anslutning till Arhos databas. Anslutningen och installationen beskrivs steg för steg i en separat manual (på finska): [Arho tekninen ohje – käyttöönotto ja pääkäyttäjä](https://docs.google.com/document/d/1HaIzgdJiOIgSZ1bA6tcsnur_4W45OwxJv8bEWOxZIeM/edit?usp=sharing).

## QGIS { #qgis }

Arho används ovanpå QGIS. Det rekommenderas att använda LTR-versionen av QGIS (i skrivande stund version **QGIS 3.44**).

Det är rekommenderat att använda en specifik användarprofil som skapats för Arho i QGIS. I denna profil sparas Arho-insticksprogrammet, databasanslutningen och dess tillhörande autentisering, samt senare information om de projektfiler som har använts i profilen.

## Installation av Arho-insticksprogrammet { #install }

Arho-insticksprogrammet installeras via QGIS-menyn *Lisäosat* → *Hallitse ja asenna lisäosia*. Arho installeras som ett experimentellt insticksprogram från URL-adressen:

```text
https://github.com/GispoCoding/arho-feature-template/releases/latest/download/plugins.xml
```

## Kontroll av anslutningen { #connection }

Innan du använder Arho bör du försäkra dig om att din Arho-anslutning är öppen och att anslutningen till databasen fungerar. Om QGIS ber om användarnamn och lösenord för databasen är det något fel på anslutningen eller på åtgärderna vid ibruktagandet, eftersom QGIS borde hitta och använda inloggningsuppgifterna från den sparade autentiseringen.

## Uppdatering av insticksprogrammet { #update }

När Arho utvecklas blir nyare versioner av insticksprogrammet tillgängliga. Uppdatera insticksprogrammet i QGIS under *Hallitse ja asenna lisäosia*.

## Nästa steg

När QGIS, insticksprogrammet och anslutningen fungerar, ta i bruk [planläggningsprojektet](project.md).
