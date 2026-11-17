# Skapa ett nytt planutkast

När det första planutkastet skapas för ett planärende används Arho-verktyget *Uusi kaavasuunnitelma*. Att skapa ett planutkast påbörjas genom att definiera dess yttre gräns. Detta kan göras antingen genom att rita (digitalisera), genom att importera den yttre gränsen från ett annat lager eller en fil, eller genom att använda plangränsen från ett aktivt planutkast.

## Planutkastets yttre gräns

### Rita planutkastets yttre gräns

1.  Börja skapa en ny plan genom att välja *Uusi kaavasuunnitelma* → *Luo uusi kaavasuunnitelma piirtämällä ulkoraja*.

    ![Menyn ”Uusi kaavasuunnitelma” öppen med valet ”Luo uusi kaavasuunnitelma piirtämällä ulkoraja” markerat](../images/plan-create-1.png)

2.  När du ritar en ny yttre gräns visas de yttre gränserna för andra planutkast som finns i databasen i kartfönstret, så att du vid behov kan fästa dig (snap) till dem.

3.  Digitalisera planutkastets yttre gräns med vänster musknapp och avsluta digitaliseringen med höger musknapp.

    !!! warning "Obs!"

        Använd inte QGIS traditionella digitalisering, utan påbörja alltid digitaliseringen genom att starta insticksprogrammets *Luo uusi kaavasuunnitelma* eller *Luo kaavakohde*.

4.  Fyll i uppgifterna i formuläret som öppnas. Obligatoriska fält är markerade med en röd stjärna \*. Grå färg hänvisar till information som inte överförs till Ryhti. Tryck slutligen på **OK**.

!!! tip "Tips"

    Se QGIS inställningar för spårning och snappning i bilagan [QGIS-inställningar för digitalisering, spårning och snappning](../digitizing.md).

### Importera planutkastets yttre gräns

1.  Innan du börjar importera planutkastets yttre gräns, kontrollera inställningarna för QGIS snappnings- och topologiverktyg. Om det är möjligt att den nya gränsen kan överlappa med objekt som redan finns på kartan, se till att du inte har förbjudit överlappning av objekt i topologiverktygen (*Salli päällekkäisyys*).

    ![QGIS meny för överlappning öppen med ”Salli päällekkäisyys” valt](../images/plan-create-2.png)

2.  När topologiinställningarna är i ordning påbörjar du importen av planutkastets yttre gräns: Välj det objekt på något av lagren i QGIS-projektet som du vill importera som planens yttre gräns. T.ex. väljs ett landskap från landskapslagret som aktivt med QGIS markeringsverktyg ![Verktyget Välj objekt](../images/plan-create-3.png){ .icon }.

    ![Karta där ett landskap är markerat (gult) för att importeras som planens yttre gräns](../images/plan-create-4.png)

3.  Välj sedan *Uusi kaava* → *Tuo kaavan ulkoraja*. Fyll i nödvändig information om planen i formuläret som öppnas.

    ![Menyn ”Kaavasuunnitelma” där ”Luo uusi kaavasuunnitelma tuomalla ulkoraja” är valt under ”Uusi kaavasuunnitelma”](../images/plan-create-5.png)

4.  ***Se till före importen att koordinatsystemet för det lager som importeras är detsamma som i projektet (oftast EPSG:3067).***

## Nytt planutkast från ett befintligt planutkast { #from-existing }

***Denna funktion kan endast användas om minst ett planutkast redan har skapats för planärendet.***

1.  Öppna planutkasten (*Kaavasuunnitelmat*) och tryck på plustecknet ![Plusknappen ”Luo uusi kaavasuunnitelma”](../images/plan-create-6.png){ .icon } i det övre vänstra hörnet av fönstret.

2.  Ange namn och livscykelskede för det nya planutkastet i fönstret som öppnas, och välj vilket planutkast du vill utgå ifrån.

    ![Plusknappen i fönstret ”Kaavasuunnitelmat” markerad och fönstret ”Uusi kaavasuunnitelma” öppet](../images/sv-plan-create-1.png){ width="553" }

3.  Tryck på **OK**, varvid det nya planutkastet skapas, men det ställs inte in som aktivt.

4.  Om du vill ställa in det skapade planutkastet som aktivt, väljer du det nyskapade planutkastet i listan och trycker på *Avaa*.

## Uppgifter om planutkastet

### Basuppgifter

När planutkastet har en yttre gräns öppnas ett fönster där uppgifterna om planutkastet matas in. Du kommer även till planutkastets formulär via menyn *Kaavasuunnitelma* under *Kaavasuunnitelman tiedot* eller genom att dubbelklicka på utkastets rad i fönstret för planutkast.

![Fliken ”Perustiedot” i formuläret ”Kaava” där planutkastets uppgifter matas in](../images/plan-create-8.png)

Planutkastets namn visas i listan över planutkast i Arho och är en obligatorisk uppgift för användningen av Arho, men det överförs inte till Ryhti. Det lönar sig att ge planutkastet ett namn som följer den egna organisationens namngivningspraxis och som är beskrivande för internt bruk.

### Allmänna bestämmelser

Allmänna bestämmelser (*yleismääräykset*) anges på en egen flik. Lägg först till en allmän bestämmelsegrupp.

![Fliken ”Yleismääräysryhmät” i fönstret ”Kaavasuunnitelma” med en grupp tillagd via knappen ”Lisää yleismääräysryhmä”](../images/plan-create-9.png)

Lägg sedan till bestämmelser och rekommendationer till den allmänna bestämmelsegruppen. Ge bestämmelserna ett värde och välj rätt typ av skriftlig bestämmelse. Vid behov kan du lägga till flera typer för en bestämmelse.

![Fliken ”Yleismääräysryhmät” i fönstret ”Kaavasuunnitelma” med fälten ”Arvo” och ”Laji” för en skriftlig bestämmelse](../images/plan-create-10.png)

### Dokument

Arho tillåter att man sparar information om dokument som hör till planen. För närvarande utvecklas Arho dock inte i en riktning för bredare möjligheter till dokumenthantering, så det är inte nödvändigt att använda denna sektion.
