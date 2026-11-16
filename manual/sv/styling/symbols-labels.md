# Symboler och etiketter samt lagring av dessa

## Symboler

Visualiseringar och symboler kan redigeras på den första fliken i panelen Lagerstilar (*Tason tyylit*). Först skapas en ny regel på ovan nämnda sätt eller så väljs en av de tidigare skapade reglerna. Efter detta kan symbolen redigeras i den nedre delen av panelen (se bilden nedan). Nya symboler kan läggas till via knappen ![](../images/styling-rule-based-5.png){ .icon }. I exemplet nedan har en rektangulär symbol skapats med en transparent fyllnadsfärg, där den yttre gränsens (linjens) färg är R 182, G 77, B 81 och tjockleken är 3 punkter. Linjestilen är solid (fast).

![](../images/styling-symbols-labels-1.png)

Ofta är symbolen som ska skapas mer komplex och kräver flera överlappande symboler. I följande exempel har en symbol skapats för att beskriva en järnväg. Den består av två överlappande symboler. Först har en 2 punkter tjock svart horisontell linje skapats, under vilken det finns vertikala linjer där varje linjes tjocklek är 1,5 punkter och avståndet mellan dem är 5 punkter. De vertikala linjernas längd är 3 millimeter.

![](../images/styling-symbols-labels-2.png)

![](../images/styling-symbols-labels-3.png)

![](../images/styling-symbols-labels-4.png)

![](../images/styling-symbols-labels-5.png)

Det är möjligt att kopiera regler, symboler och deras färger, vilket underlättar skapandet av nya symboler. Kopiering av regler och symboler görs med höger musknapp.

![](../images/styling-symbols-labels-6.png)

Symbolens färg kan kopieras (och klistras in) på det sätt som visas i bilden nedan.

![](../images/styling-symbols-labels-7.png)

## Etiketter (Nimiöt) { #labels }

Etiketter (*nimiöt*) kan redigeras på den andra fliken i panelen Lagerstilar. För olika symboler kan det vara nödvändigt att ställa in olika storlekar på etiketterna. Detta kan uppnås genom att skapa en regelbaserad etikettering (*sääntöpohjainen nimiöinti*). Om det inte finns behov av olika storlekar eller färger på teckensnitten räcker det med en enkel etikettering.

![](../images/styling-symbols-labels-8.png)

En ny regel kan läggas till via knappen ![](../images/styling-rule-based-5.png){ .icon }. Lägg till en unik beskrivning för regeln (t.ex. ”Teckenstorlek 6”). Liksom i fallet med symboler behöver även regelbaserade etiketter filter (se [Filter](filters.md)). Efter att filtret har ställts in kontrollerar man att etiketterna är aktiverade för den aktuella regeln (kryssruta). Dessutom lägger man till `array_to_string("short_names", '/')` i fältet Värde (*Arvo*). Efter detta kan själva etiketten redigeras: i den nedre delen av panelen finns flikar för textformatering och placering samt för att skapa buffert, masker, bakgrund osv.

![](../images/styling-symbols-labels-9.png)

Vid etikettering av polygonobjekt är det bra att under fliken Placering (*Sijoittaminen*) aktivera inställningen ”Tvinga in punkt i polygon” (*Pakota piste monikulmion sisään*), så att etiketten inte i vissa fall hamnar utanför polygonen.

![](../images/styling-symbols-labels-10.png)

## Spara symboler och etiketter { #save }

Lagrens stilar sparas i QGIS-projektfilen (++ctrl+s++ eller *Projekti* → *Tallenna*). För att visualiseringarna ska vara tillgängliga både för andra användare och efter att projektfilen har uppdaterats, lönar det sig att spara stilarna i QML-filer. Observera att en egen QML-fil måste skapas för varje lager.

!!! warning "Obs!"

    Att öppna samma eller en ny plan leder till att stilarna laddas om från QML-filerna, vilket leder till att de stilar som sparats i projektet skrivs över. På grund av detta rekommenderas det att spara nya stilar i filerna i takt med att man skapar dem.

Lagringen görs på fliken Symbolbiblioteket (*Tyylien hallinta*). Först väljs rätt lager i rullgardinsmenyn och sedan trycker man på knappen ![](../images/styling-symbols-labels-11.png){ .icon }.

![](../images/styling-symbols-labels-12.png){ width="395" }

Knappen Spara stil (*Tallenna tyyli*) öppnar fönstret som visas nedan. Först väljs ”En QGIS QML-stilfil” (*QGIS QML -tyylitiedostona*) i rullgardinsmenyn Spara stil (*Tallenna tyyli*). Sedan ställs sökvägen in för filen som ska sparas via knappen ![](../images/styling-symbols-labels-13.png){ .icon }. Efter detta väljs de kategorier som ska sparas. Av dessa räcker det att välja Symbologi (*Kuvaustekniikka*) och Etiketter (*Nimiöt*). Tryck slutligen på **OK**.

![](../images/styling-symbols-labels-14.png){ width="283" }

En stil som sparats i en QML-fil kan tas i bruk via knappen ![](../images/styling-symbols-labels-15.png){ .icon }. Först väljs ”From file” i rullgardinsmenyn och QML-filens lagringssökväg ställs in med knappen ![](../images/styling-symbols-labels-13.png){ .icon }. Återigen räcker det att välja Symbologi och Etiketter som kategorier. Tryck därefter på Läs in stil (*Lataa tyyli*).

![](../images/styling-symbols-labels-16.png){ width="283" }

## Slå samman QML-filer

De regelbaserade visualiseringarna och etiketterna från två (eller flera) QML-stilfiler kan enklast slås samman på följande sätt: Ladda in stilarna från den första QML-filen på det lager vars stilar du vill slå samman (se [Spara symboler och etiketter](#save)).

Skapa därefter ett nytt temporärt minneslager. Knappen ![](../images/styling-symbols-labels-17.png){ .icon } finns i verktygsfältet för datakällshantering (*Tietolähteiden hallinta*) ![](../images/styling-symbols-labels-18.png){ .icon }, som kan göras synligt via *Näytä* → *Työkalut* → *Tietolähteiden hallinnan työkalupalkki*.

Välj rätt geometrityp (multipunkt, multilinje eller multipolygon) och projektets koordinatsystem (EPSG:3067). Inga fält behöver skapas. Tryck slutligen på **OK**.

![](../images/styling-symbols-labels-19.png)

Öppna panelen *Lagerstilar* och välj detta nyss skapade temporära minneslager i rullgardinsmenyn. Därefter laddas stilarna från den andra QML-filen in på det temporära minneslagret på det sätt som beskrivs i avsnittet [Spara symboler och etiketter](#save).

![](../images/styling-symbols-labels-20.png)

Markera alla de regler som du vill kopiera, tryck på höger musknapp och välj Kopiera (++ctrl+c++ fungerar inte nödvändigtvis).

![](../images/styling-symbols-labels-21.png)

Välj nu det önskade mållagret i rullgardinsmenyn, tryck på höger musknapp i regelfältet och välj Klistra in (*Liitä*).

![](../images/styling-symbols-labels-22.png)

Denna process kan upprepas om du vill slå samman fler än två QML-filer. Observera att de temporära minneslagren inte är sparade i en fil och att de försvinner när QGIS stängs.
