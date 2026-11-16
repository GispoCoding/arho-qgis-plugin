# Planläggningsprojekt (Kaavoitusprojekti) i QGIS

I QGIS arbetar man med projekt. Varje gång något är öppet och arbete utförs, är även en projektfil öppen. För användningen av Arho har ett eget projekt kallat ***kaavoitus*** (planläggning) utarbetats. Det innehåller bland annat kartlager som är väsentliga för användningen. Denna projektfil är en viktig del av Arho-helheten och dess funktioner; utan den fungerar inte Arho. Ändra därför inte projektet efter eget tycke, eftersom ändringar av exempelvis lagernamn leder till att Arho slutar fungera.

## Ibruktagande av projektfilen för planläggning

Projektfilen *kaavoitus* har sparats i databasen. Varje användare måste spara en egen version av planläggningsprojektet.

1.  Tryck upp PostgreSQL-lagren i QGIS-panelen Datakällor (*Selain*) så att du under ***Arho-databasanslutningen*** hittar schemat `qgis_projects` eller `public` (beroende på projektet) och där under projektet *kaavoitusprojekti* (i exemplet heter databasen `arho_test`).

    ![QGIS-panelen Datakällor: PostgreSQL → arho_test → qgis_projects med kaavoitusprojekti-projekten](images/project-1.png)

2.  Öppna planläggningsprojektet genom att till exempel dubbelklicka med vänster musknapp på projektfilen.

3.  Spara projektet på nytt direkt genom att välja *Projekti* → *Tallenna tiedostoon* → *PostgreSQL*.

    ![Menyn ”Projekti” i QGIS med ”Tallenna tiedostoon” → ”PostgreSQL...” valt](images/project-2.png)

4.  I fönstret som öppnas ska du se till att du sparar ditt eget projekt i samma schema som planläggningsprojektet låg i (`qgis_projects` eller `public`) och ge projektet namnet `kaavoitus_dittförnamn` i fältet *Projekti*. Tryck slutligen på **OK**. Nu har du ett eget projekt som du kan öva med.

    ![Fönstret ”Tallenna projekti PostgreSQL:ään” med fälten ”Yhteys”, ”Skeema” och ”Projekti”](images/project-3.png){ width="325" }

!!! warning "Obs!"

    Använd inte andras projekt och ta inte bort något som du inte själv har skapat.

## Uppdatering av projektfilen

När Arho-implementationen uppdateras kan det bli nödvändigt att även uppdatera projektfilen *Kaavoitus*. Hämta i så fall en ny projektfil från schemat `public` i databasen och spara den på samma sätt som när du tog projektet i bruk för första gången.

## Borttagning av projekt

Efter några utvecklingsrundor kan du ha för många projekt och du vill kanske ta bort några emellanåt. Att ta bort ett projekt från databasen görs via samma menyfunktion som när man sparar projektet i databasen, det vill säga *Projekti* → *Tallenna tiedostoon* → *PostgreSQL*:

![Menyn ”Projekti” i QGIS med ”Tallenna tiedostoon” → ”PostgreSQL…” valt](images/project-4.png){ width="328" }

I fönstret som öppnas väljer du först det projekt du vill ta bort, och därefter väljer du *Poista projekti* under knappen *Hallitse projekteja*.

![Fönstret ”Tallenna projekti PostgreSQL:ään” med ”Poista projekti” valt under ”Hallitse projekteja”](images/project-5.png){ width="337" }
