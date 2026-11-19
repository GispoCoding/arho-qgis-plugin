# Bilaga: QGIS-inställningar för digitalisering, spårning och snappning

Tabellen nedan visar rekommenderade QGIS-inställningar när du digitaliserar i Arho.

| Vad digitaliseras? | Snappning ![Knappen ”Ota tarttuminen käyttöön” (magnet)](images/digitizing-snapping.png){ .icon } ![Knappen Självsnappning](images/digitizing-snapping-2.png){ .icon } | Topologisk redigering ![Knappen Topologisk redigering](images/digitizing-topology.png){ .icon } | Överlappning ![Knappen för överlappningsinställning](images/digitizing-overlap.png){ .icon } | Spårning ![Knappen Aktivera spårning](images/digitizing-tracing.png){ .icon } |
|---|---|---|---|---|
| **Planens yttre gräns** (*Kaavan ulkoraja*) | Aktivera om du vill att planens yttre gräns ska gränsa exakt mot andra yttre plangränser i databasen. | Inaktivera. Om topologisk redigering är aktiverad och din plangräns gränsar till en annan plangräns, kommer du att redigera båda gränserna när du ändrar den ena, vilket sällan är ändamålsenligt. | Tillåt överlappning om planens yttre gräns får överlappa med en annan; undvik om den inte får göra det. | Aktivera om planens yttre gräns ska gränsa exakt mot en intilliggande plangräns. |
| **Områdesreservering** (*Aluevaraus*) | Aktivera. Det rekommenderas att ställa in snappning till det aktiva lagret och till brytpunkter (*taitepisteet*). Detta hjälper till att skapa en enhetlig bas av områdesreserveringar. | Aktivera. När två områden har en gemensam gräns ändras båda områdena när den gemensamma gränsen redigeras. Detta hjälper till att bibehålla en enhetlig planbas. Varning för oavsiktliga redigeringar av intilliggande områden, så var noggrann. | Ställ in på **Undvik överlappning**. Områdesreserveringar får inte överlappa varandra, och denna inställning förhindrar det. | Aktivera, så gränsar din områdesreservering exakt mot andra områdesreserveringar och planens yttre gräns. Kan även utnyttjas mot andra material som du använder som hjälp. |
| **Delområde** (*Osa-alue*) | Utnyttja om du använder andra (vektor)material som hjälp när du ritar delområdet. | Aktivera om du vill att objekt som har gemensamma noder eller segment ska redigeras samtidigt. | Tillåt överlappning. Om **Undvik överlappning** är aktiverat kan du inte rita delområden ovanpå andra områden. | Utnyttja om du använder andra (vektor)material som hjälp när du ritar delområdet. |
| **Linje** (*Viiva*) | Aktivera om du utnyttjar ett annat material. Om du vill att linjen ska snappa till en områdesgräns mellan brytpunkter, välj snappning till segment. | Aktivera om du vill att objekt som har gemensamma noder eller segment ska redigeras samtidigt. | | Aktivera om du vill att linjen ska följa en annan linje eller ett område. Genom att ange ett offset-värde följer linjen den andra linjen eller området på ett bestämt avstånd. |
| **Punkt** (*Piste*) | Aktivera om du utnyttjar ett annat material och det är viktigt att punkten hamnar på exakt rätt ställe. | | | |

Det rekommenderas att topologisk redigering alltid hålls aktiverad, utom i de fall då man specifikt inte vill att intilliggande objekt ska flyttas. När det här alternativet är aktiverat identifierar QGIS gemensamma gränser. När du flyttar gemensamma noder eller segment flyttar QGIS dem även i grannobjektens geometrier, vilket gör att man undviker överlappande områdesreserveringar eller glapp mellan områdesreserveringarna.

![QGIS snappningsverktygsfält där knappen för topologisk redigering är markerad med rött](images/digitizing-1.png)

Dessutom rekommenderas att snappning till linjer och noder (vertexer) används. Om man snappar till en linje samtidigt som topologisk redigering är aktiverad, skapas en ny nod i det objekt som ritas utifrån det andra objektets geometri.

![QGIS verktygsfält för snappning med magnetknappen för snappning markerad med rött](images/digitizing-2.png)

Du kan läsa mer om funktionerna i QGIS redigerings- och digitaliseringsverktyg i [QGIS användarhandbok](https://docs.qgis.org/3.40/en/docs/user_manual/working_with_vector/editing_geometry_attributes.html#editing).
