# Insticksprogrammet Arho

## Installation av Arho-insticksprogrammet

Arho-insticksprogrammet installeras via QGIS-menyn *Lisäosat* → *Hallitse ja asenna lisäosia*. Arho installeras som ett experimentellt insticksprogram från URL-adressen:

```text
https://github.com/GispoCoding/arho-feature-template/releases/latest/download/plugins.xml
```

Närmare instruktioner för installationen av insticksprogrammet hittar du i ibruktagningsmanualen.

## Uppdatering av insticksprogrammet

När Arho utvecklas blir nyare versioner av insticksprogrammet tillgängliga. Uppdatera insticksprogrammet i QGIS under *Hallitse ja asenna lisäosia*.

## Arhos användargränssnitt

I och med Arho-insticksprogrammet läggs Arhos verktygsfält till i QGIS.

![](images/plugin-1.png)

Verktygen är gråmarkerade om de inte kan användas för tillfället. Om det till exempel inte finns något aktivt planutkast (*kaavasuunnitelma*) öppet, är inte heller verktygen för planobjekt (*kaavakohde*) och planbestämmelsegrupper (*kaavamääräysryhmät*) aktiva.

Denna användarmanual behandlar dessa verktyg och de funktioner som finns under dem i egna avsnitt.

Under QGIS-menyn för insticksprogram (*Lisäosat*) kommer du även åt Arhos inställningar och verktyg.

![](images/plugin-2.png)

Det sista alternativet i listan, *Avaa lokikansio*, tar användaren till mappen där Arho sparar användarens aktiviteter. Den här filen behövs när man vill rapportera ett problem i Arho, eftersom den hjälper utvecklarna att utreda problemet.

När du startat ett planläggningsprojekt så visas information i kartfönstret om vilket planärende (*kaava-asia*) och vilket planutkast (*kaavasuunnitelma*) som är aktivt i fönstret. Om fältet är tomt betyder det att ingenting är aktivt. I exemplet nedan finns ett aktivt planärende, men inte ett enda planutkast.

![](images/plugin-3.png)
