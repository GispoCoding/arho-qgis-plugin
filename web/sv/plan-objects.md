# Planobjekt (Kaavakohteet)

## Rita planobjekt

1.  Börja skapa ett planobjekt genom att välja Skapa planobjekt (*Luo kaavakohde*). Välj typ av planobjekt bland knapparna beroende på vilket objekt du vill rita.

    ![Knappen ”Luo kaavakohde” markerad i Arhos verktygsfält](images/plan-objects-1.png) ![Panelen ”Luo kaavakohde” med knappar för planobjektets typ: ”Aluevaraus”, ”Osa-alue”, ”Viiva” och ”Piste”](images/plan-objects-2.png){ width="297" }

2.  När du har valt planobjektstyp kan du rita objektet på kartan genom att trycka på musen.

3.  Se tips om inställningarna för digitalisering, snappning och spårning i QGIS i bilagan [QGIS-inställningar för digitalisering, spårning och snappning](digitizing.md).

## Koppla planbestämmelser till ett planobjekt

När ett planobjekt har ritats öppnas ett fönster där du kan koppla planbestämmelser till objektet. Välj lämpliga planbestämmelsegrupper och planbestämmelser för objektet genom att ***dubbelklicka*** på önskad planbestämmelsegrupp under *Kaavamääräysryhmäkirjastot*. Observera att du kan välja vilket bibliotek du vill använda för tillfället (detaljplane-, generalplane-, landskapsplanebiblioteket, *Käytössä olevat* eller ett självskapat bibliotek). Med hjälp av sökfältet kan du söka efter en lämplig planbestämmelsegrupp med ordsökning.

![Menyn ”Kaavamääräysryhmäkirjastot” öppen med biblioteken per plantyp och ”Käytössä olevat kaavamääräysryhmät”](images/plan-objects-3.png){ width="438" }

![Planobjektets formulär där en planbestämmelsegrupp som hittats med sökningen ”virkis” har kopplats till objektet](images/plan-objects-4.png)

Du kan söka efter lämpliga grupper med sökfunktionen. När du hittar rätt planbestämmelsegrupp, ***dubbelklicka på objektet*** så att det blir valt. Gör de ändringar som behövs.

- Via kugghjulsikonen ![Kugghjulsknappen](images/plan-objects-5.png){ .icon } kommer du åt att redigera planbestämmelsegruppens uppgifter, planbestämmelsen/-bestämmelserna och planrekommendationerna (se [Skapa och redigera planbestämmelsegrupper](regulation-groups.md#create-edit)).
- ![Papperskorgsknappen](images/plan-objects-6.png){ .icon } Papperskorgen tar bort planbestämmelsegruppen.
- ![Plusknappen med rullgardinsmeny](images/plan-objects-7.png){ .icon } Via plusknappen kan du definiera ämnestaggar (*Aihetunniste*), plantema (*Kaavoitusteema*) och ytterligare information (*Lisätieto*).

    ![Plusknappens meny med valen ”Aihetunniste”, ”Kaavoitusteema” och ”Lisätieto”](images/plan-objects-8.png)

- Om du valde *Sanallinen määräys*, ange den skriftliga beskrivningen av bestämmelsen i fältet *Arvo* och välj en lämplig typ av skriftlig bestämmelse (*Sanallisen määräyksen laji*) för den.

Tryck slutligen på **OK**.

## Redigera och ta bort ett befintligt planobjekt

![Arhos verktygsfält där verktyget ”Muokkaa kaavakohteita” är markerat med rött](images/plan-objects-10.png){ width="215" }

1.  Om du vill redigera befintliga planobjekt, välj *Muokkaa kaavakohteita*.

    1.  Om du vill redigera ett objekts uppgifter, tryck på objektet med musen så att dess formulär öppnas.

        ![Formuläret ”Kaavamääräys” med fältet ”Arvo” markerat och ”Sanallisen määräyksen laji” under det](images/plan-objects-9.png)

    2.  Om du vill redigera ett objekts geometri, välj till exempel QGIS brytpunktsverktyg (*Taitepistetyökalu*) eller något av tilläggsverktygen för digitalisering, och redigera det önskade objektet.

2.  Om du vill ta bort ett planobjekt, välj objektet på kartan och tryck på **Delete**, eller ta bort objektet via attributtabellen.

## Planobjektspanelen (Kaavakohdepaneeli) { #panel }

Från verktyget *Kaavakohteet* ![Knappen ”Kaavakohteet”](images/plan-objects-11.png){ .icon } öppnas planobjektspanelen.

![Panelen ”Kaavakohteet” med typknappar, sökfält och en lista över planobjekt](images/plan-objects-12.png)

I denna tabellvy kan du se alla planobjekt som finns i ditt planutkast. Eftersom det kan finnas många objekt kan det vara praktiskt att filtrera dem efter typ eller söka med ett sökord.

Du kan använda planobjektspanelen för att välja planobjekt. När du väljer en rad i panelen blir objektet också valt på kartan, och vice versa.

Genom att högerklicka på ett objekts rad får du tillgång till fyra (eller fem) funktioner:

![Snabbmenyn för en rad i planobjektspanelen med bland annat ”Näytä lomake”, ”Zoomaa kohteeseen” och ”Väläytä kohdetta”](images/plan-objects-13.png)

- *Näytä lomake* öppnar planobjektets formulär. Formuläret kan också öppnas genom att dubbelklicka på raden. I formuläret kan du redigera objektets uppgifter.
- *Zoomaa kohteeseen* zoomar in kartvyn till det valda objektet.
- *Vieritä kohteeseen* behåller samma skala och centrerar kartan till det valda objektet.
- *Väläytä kohdetta* högmarkerar objektet tillfälligt så att du lättare hittar det på kartan.
- *Tallenna kaavakohdepohjakirjastoon* är tillgängligt om du har skapat ett planobjektsmallsbibliotek (se [Planobjektsmallsbibliotek](libraries.md#plan-object-templates)).

## Importera planobjekt

Arho gör det möjligt att importera objekt från andra material med verktyget *Tuo kaavakohteita*.

![Arhos verktygsfält med knappen ”Tuo kaavakohteita” markerad](images/plan-objects-14.png)

När du väljer verktyget öppnas fönstret *Tuo kaavakohteita*.

![Fönstret ”Tuo kaavakohteita” där importlager, mållager, uppgifter som kopieras och planbestämmelsegrupper väljs](images/plan-objects-15.png)

### Lager (Tasot)

Obligatoriska fält är importlagret (***tuontitaso***) och mållagret (***kohdetaso***). Importlagret är det vektorlager från vilket du vill importera planobjekt. Observera att du kan välja att endast importera valda objekt; du kan alltså från det önskade lagret välja ut precis de objekt som du vill importera. Mållager är det planobjektslager i Arho som objekten ska importeras till, och det beror därmed på vilken typ av planobjekt som importeras. Geometritypen för importlagret och mållagret måste vara densamma.

### Information som kopieras från importlagret (tuontitaso)

På grund av plandatamodellens komplexitet kan man till Arho huvudsakligen importera objektens geometrier. Information som är möjlig att importera är namn och beskrivning. I inställningarna för den information som kopieras från importlagret kan du definiera i vilka av importlagrets fält denna information finns, samt på vilket språk informationen är.

### Information som tilldelas alla objekt

Slutligen kan du definiera information som kopplas till alla objekt du importerar: objektens typ av underjordiskhet (*maanalaisuuden laji*) samt vilka planbestämmelsegrupper som ska tilldelas. Eftersom ett planobjekts underjordiskhet måste vara definierat i Ryhti, kan valet *maanalaisuuden laji* inte lämnas tomt. Det är inställt på ”Ovan jord” (*Maanpäällinen*) som standard.

För att kunna koppla planbestämmelser till objekten som importeras har biblioteken för planbestämmelsegrupper gjorts tillgängliga i fönstret. Användaren kan välja vilka planbestämmelsegrupper som ska kopplas till objekten genom att dubbelklicka på dem. Det är inte obligatoriskt att koppla planbestämmelsegrupper i detta skede.

!!! note "Observera"

    Både typ av underjordiskhet och planbestämmelsegrupper kopplas till alla importerade objekt, oberoende av eventuell attributdata på importlagret. I praktiken måste planobjekt därför importeras i sådana partier som ska ha samma planbestämmelsegrupper, ifall man vill tilldela planbestämmelsegrupperna redan i importskedet och inte senare.

När inställningarna har valts trycker du på knappen **Import** för att starta importprocessen.
