# Bibliotek (Kirjastot)

Ett bibliotek är en samling av mallar som har skapats för att underlätta skapandet av planbestämmelsegrupper eller planobjekt. Det är möjligt för användaren att skapa egna bibliotek och lägga till mallar i dem för att effektivisera arbetet. Utifrån mallarna kan man skapa nya planbestämmelsegrupper eller planobjekt med tillhörande planbestämmelsegrupper. Biblioteken innehåller alltså en sorts recept eller ritningar för hur planbestämmelsegrupper och planobjekt ska skapas. Ett bibliotek kan även delas med en annan användare som en YAML-fil. Biblioteken underlättar arbetet eftersom planbestämmelsegrupper och planobjekt (med sina länkade planbestämmelsegrupper) inte behöver utarbetas helt från grunden varje gång.

Biblioteken hanteras via Arhos knapp *Kirjastot*, vilket öppnar fönstret för bibliotekshantering (*Kirjastojen hallinta*).

## Bibliotek för planbestämmelsegrupper (Kaavamääräysryhmäkirjastot)

Arho innehåller färdiga bibliotek med planbestämmelsegrupper som följer Katja. Hanteringen av egna bibliotek för planbestämmelsegrupper sker i fönstret *Kirjastojen hallinta*, som öppnas bakom knappen ***Kirjastot***.

### Skapa ett bibliotek

1.  Välj fliken ***Kaavamääräysryhmäpohjat***.
2.  Skapa ett nytt bibliotek i fönstret som öppnas genom att trycka på den översta knappen ![](images/libraries-1.png){ .icon }.
3.  Ge biblioteket ett namn.
4.  Ange lagringssökvägen för biblioteket via knappen med tre punkter ![](images/libraries-2.png){ .icon }.
5.  Utforma och lägg till de planbestämmelsegrupper du vill ha i biblioteket med knappen ![](images/libraries-3.png){ .icon }. Formuläret som öppnas är mycket likt det som används när man skapar vanliga planbestämmelsegrupper.
6.  Tryck slutligen på *Tallenna*.

![](images/libraries-4.png){ width="549" }

### Redigera ett bibliotek

1.  Öppna *Kirjastojen hallinta* via knappen *Kirjastot*.
2.  Välj det bibliotek som du vill redigera och gör dina ändringar.

![](images/libraries-5.png){ width="503" }

### Använda ett bibliotek

1.  Det sparade biblioteket blir synligt under biblioteken för planbestämmelsegrupper.

    ![](images/libraries-6.png)

2.  Du kan använda ditt eget bibliotek för att koppla planbestämmelsegrupper till planobjekt.

## Planobjektsmallsbibliotek (Kaavakohdepohjakirjasto) { #plan-object-templates }

En planobjektsmall (*kaavakohdepohja*) är en uppsättning planbestämmelsegrupper. Genom att använda en planobjektsmall kan du rita objektets geometri, varpå de planbestämmelsegrupper som ska kopplas till objektet (det kan vara flera) hämtas direkt från mallen.

### Skapa och redigera ett bibliotek

Bibliotek för planobjektsmallar hanteras på samma sätt som bibliotek för planbestämmelsegrupper.

1.  Öppna *Kirjastojen hallinta* genom att trycka på knappen *Kirjastot*.

2.  Välj fliken ***Kaavakohdepohjat***.

3.  Ge biblioteket ett namn.

4.  Skapa ett nytt bibliotek för planobjektsmallar i fönstret som öppnas genom att trycka på den översta knappen ![](images/libraries-1.png){ .icon }.

5.  Ange lagringssökvägen för biblioteket via knappen med tre punkter ![](images/libraries-2.png){ .icon }.

6.  Lägg till en ny mall i biblioteket med knappen ![](images/libraries-3.png){ .icon }.

    1.  Välj det geometrilager som planobjektsmallen ska utarbetas för.
    2.  Utforma planbestämmelsegruppen (*kaavamääräysryhmä*).
    3.  Tryck på *Tallenna kaavakohdepohjakirjastoon*.
    4.  Tryck på **OK** när du är klar.

7.  Tryck slutligen på *Tallenna* och stäng.

### Använd planobjektsmallar

1.  Planobjektsmallarna tas i bruk från QGIS-panelen ***Luo kaavakohde***.
2.  Välj först planobjektets geometrityp under ***Kaavakohteen tyyppi***.
3.  Under ***Alusta kaavakohde pohjasta*** välj en lämplig mall och digitalisera objektet.

![](images/libraries-7.png)
