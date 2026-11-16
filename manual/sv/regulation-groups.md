# Planbestämmelsegrupper (Kaavamääräysryhmät)

## Panelen för planbestämmelsegrupper (Kaavamääräysryhmäpaneeli)

Planbestämmelsegrupper hanteras med knappen *Kaavamääräysryhmät*. Knappen öppnar en panel där de planbestämmelsegrupper som används eller som användaren själv har skapat listas. Med detta verktyg kan du dessutom redigera bestämmelsegrupper för flera planobjekt samtidigt.

1.  En ny planbestämmelsegrupp **skapas** med knappen ![Knappen ”Luo uusi kaavamääräysryhmä”](images/regulation-groups-1.png){ .icon } i *Kaavamääräysryhmät*-panelen.

2.  Genom att välja en befintlig planbestämmelsegrupp i listan så att den blir aktiv (raden blir blå) och trycka på Redigera (***Muokkaa***), kommer du åt att redigera planbestämmelserna. Genom att trycka på Ta bort (***Poista***) kan du radera den.

3.  *Kaavakohdetoiminnot* är massfunktioner som gör det möjligt för dig att hantera flera planobjekt och planbestämmelsegrupper samtidigt.

    ![Panelen ”Kaavamääräysryhmät” med en vald grupp i blått, knapparna och menyn ”Kaavakohdetoiminnot”](images/regulation-groups-2.png)

## Skapa och redigera planbestämmelsegrupper { #create-edit }

1.  En ny planbestämmelsegrupp skapas med knappen ***Luo kaavamääräysryhmä*** ![Knappen ”Luo uusi kaavamääräysryhmä”](images/regulation-groups-1.png){ .icon }. Du kan välja att skapa en ny helt från början (tom) eller utifrån en mall.

    ![Plusknappens meny i panelen ”Kaavamääräysryhmät” med valen ”Tyhjä” och ”Pohjasta”](images/regulation-groups-3.png)

    1.  Med *Tyhjä* får du bygga upp planbestämmelsegruppen helt själv från grunden.

    2.  Med *Pohja* kan du välja till exempel en bestämmelse som följer Katja-förordningen och redigera den vidare för dina egna behov. Välj först bibliotek och sedan den planbestämmelsegrupp som ska användas som mall.

    3.  Oavsett vilket sätt du väljer öppnas fönstret *Luo kaavamääräysryhmä*, vilket är mycket likt fönstret för redigering av planbestämmelsegrupp *Muokkaa kaavamääräysryhmää* som presenteras härnäst.

2.  På fliken ***Kaavamääräysryhmän tiedot***: Det rekommenderas att du anger en rubrik (*otsikko*) och en bokstavsbeteckning (*kirjaintunnus*). Typ av planbestämmelse (*Tyyppi*) är en obligatorisk uppgift.

    ![Fliken ”Kaavamääräysryhmän tiedot” i fönstret ”Luo kaavamääräysryhmä” där ”Tyyppi” är obligatoriskt](images/regulation-groups-4.png){ width="366" }

3.  På fliken ***Kaavamääräykset*** utformas själva planbestämmelsegruppen genom att du lägger till bestämmelser.

    1.  I listan ser du de bestämmelser som hör till [kodverket för slag av planbestämmelse (Kaavamääräyslaji)](https://koodistot.suomi.fi/codescheme;registryCode=rytj;schemeCode=RY_Kaavamaarayslaji).

    2.  Genom att välja ett slag av bestämmelse ser du dess beskrivning.

    3.  Du kan söka efter bestämmelser med sökfältet eller genom att bläddra i listan.

    4.  När du hittar den bestämmelse som behövs, ***dubbelklicka*** på den så att bestämmelsen flyttas till rutan till höger. Där kan du sedan ge den till exempel en ämnestagg (*aihetunniste*), ett planläggningstema (*kaavoitusteema*) osv.

    ![Fliken ”Kaavamääräykset” i fönstret ”Luo kaavamääräysryhmä” där ”Virkistysalue” har lagts till i rutan till höger](images/regulation-groups-5.png){ width="599" }

4.  På fliken ***Suositukset*** kan du lägga till rekommendationer för gruppen.

5.  Med verktyget ***Muokkaa valittua kaavamääräysryhmää*** ![Knappen ”Muokkaa valittua kaavamääräysryhmää”](images/regulation-groups-6.png){ .icon } öppnas fönstret för den planbestämmelsegrupp som har markerats med blått i panelen för planbestämmelsegrupper, där du kan redigera gruppen. Fönstret *Muokkaa kaavamääräysryhmää* är mycket likt fönstret *Luo kaavamääräysryhmä*.

    1.  På fliken ***Kaavamääräysryhmän tiedot*** kan du ange basuppgifter för gruppen och definiera dess typ (områdesreservering, delområde osv.).

        Observera den blå texten som talar om hur många objekt gruppen används på. Om samma planbestämmelsegrupp har kopplats till många planobjekt är det bra att överväga om man verkligen vill redigera gruppen, eftersom ändringen då påverkar alla dessa objekt.

    2.  På fliken ***Kaavamääräykset*** kan du lägga till planbestämmelser i gruppen.

6.  När du har skapat önskad grupp eller gjort ändringar i en befintlig, tryck på **OK**.

7.  Den nya gruppen flyttas till ***Käytössä olevat kaavamääräysryhmät*** och du kan använda den för nya och befintliga planobjekt.

    ![Menyn ”Kaavamääräysryhmäkirjastot” öppen med biblioteken per plantyp och ”Käytössä olevat kaavamääräysryhmät”](images/plan-objects-3.png){ width="438" }

    I fönstret som öppnas efter att du har ritat ett planobjekt är ett av de tillgängliga biblioteken *Käytössä olevat kaavamääräysryhmät*.

## Planobjektsfunktioner för planbestämmelsegrupper

Från panelen *Kaavakohteet* kan du hantera hur planbestämmelsegrupper kopplas till planobjekt. Du kan lägga till och ta bort valda planbestämmelsegrupper för valda planobjekt. Alla dessa funktioner förutsätter att du först väljer de planobjekt på kartan vars planbestämmelsegrupper du vill påverka.

![Menyn ”Kaavakohdetoiminnot” med funktioner för att lägga till och ta bort grupper för valda objekt](images/regulation-groups-7.png)

1.  **Lägg till valda grupper till valda objekt** (*Lisää valitut ryhmät valituille kohteille*)

    1.  Välj de objekt på kartan med QGIS vanliga markeringsverktyg ![Verktyget Välj objekt](images/regulation-groups-8.png){ .icon } som du vill lägga till en eller flera planbestämmelsegrupper till.

    2.  Välj därefter den eller de planbestämmelsegrupper i listan som du vill lägga till för objekten (gruppen markeras med blått). Välj slutligen ***Kaavakohdetoiminnot*** → ***Lisää valitut ryhmät valituille kohteille***.

        ![Menyn ”Kaavakohdetoiminnot” öppen med valet ”Lisää valitut ryhmät valituille kohteille” markerat](images/regulation-groups-9.png){ width="354" }

2.  **Ta bort alla grupper från valda objekt** (*Poista kaikki ryhmät valituilta kohteilta*)

    1.  Välj de objekt på kartan med QGIS vanliga markeringsverktyg som du vill ta bort planbestämmelsegrupper från.

    2.  Välj ***Kaavakohdetoiminnot*** → ***Poista kaikki ryhmät valituilta kohteilta***.

3.  **Ta bort valda grupper från valda objekt** (*Poista valitut ryhmät valituilta kohteilta*)

    1.  Välj de objekt på kartan med QGIS vanliga markeringsverktyg som du vill ta bort grupper från.

    2.  Välj den grupp i listan som du vill ta bort från objekten.

        ![Panelen ”Kaavamääräysryhmät” där gruppen ”VR - Retkeily- ja ulkoilualue” är vald i listan](images/regulation-groups-10.png)

    3.  Välj ***Kaavakohdetoiminnot*** → ***Poista valitut ryhmät valituilta kohteilta***.

## Tips för tillämpning av planbestämmelsegrupper

Fliken *Kaavamääräysryhmän tiedot*:

![Fliken ”Kaavamääräysryhmän tiedot” i fönstret ”Muokkaa kaavamääräysryhmää” med uppgift om gruppens användning](images/regulation-groups-11.png)

Rubriken (*Otsikko*) och bokstavsbeteckningen (*kirjaintunnus*) rekommenderas att följa Katja-förordningen, förutsatt att en liknande planbestämmelsegrupp finns i Katja. Om det finns små skillnader i bestämmelserna kan man lägga till ett index till bokstavsbeteckningen (t.ex. A-1 och A-2).

Den blå texten talar om hur många objekt planbestämmelsegruppen har kopplats till i planutkastet.

Färgkodsvärdet (*Värikoodi*) kan användas för mindre anpassningar av visualiseringar.
