# Skapa en regelbaserad visualisering i QGIS

Om användaren vill göra egna visualiseringar måste egna separata QML-filer skapas. Om användaren bara redigerar Arhos standardstilar kommer ändringarna att skrivas över i samband med nästa uppdatering av insticksprogrammet.

Regelbaserade visualiseringar kan skapas för planobjekt på följande sätt:

1.  Öppna panelen Lagerstilar (*Tason tyylit*) via dess knapp ![Knappen för panelen Lagerstilar (”Tason tyylit”)](../images/styling-rule-based-1.png){ .icon } (eller *Näytä* → *Paneelit* → *Tason tyylit*).

2.  Välj det lager som ska stilsättas i rullgardinsmenyn.

3.  På fliken Symbologi (*Kuvaustekniikka*), välj Regelbaserad (*Sääntöpohjainen*) i rullgardinsmenyn.

    ![Panelen ”Tason tyylit” (Lagerstilar) med lagret och renderaren ”Sääntöpohjainen” markerade](../images/styling-rule-based-2.png)

4.  Välj eller digitalisera det planobjekt som ska stilsättas och lägg till en lämplig planbestämmelsegrupp för det.

5.  Granska uppgifterna för objektet som ska stilsättas med verktyget Identifiera objekt (*Näytä kohteen tiedot*) ![Verktyget Identifiera objekt](../images/styling-rule-based-3.png){ .icon }.

6.  I objektets information finns fältet `primary_use` (områdesreservering), `sub_area` (delområden), `type_regulations` (punkter och linjer) eller `regulation_values` (delområden, punkter). Med hjälp av den JSON som detta fält innehåller kan man skapa ett unikt filter för objektets planbestämmelsegrupp. I vissa fall kan objektets information innehålla flera fält (delområden). Se instruktioner för att skapa filter i avsnittet [Filter](filters.md).

    ![Panelen ”Kohteen tiedot” med JSON-värdet i fältet ”primary_use” för en områdesreservering markerat](../images/styling-rule-based-4.png){ width="526" }

7.  Lägg till en ny regel via knappen ![Knappen Lägg till](../images/styling-rule-based-5.png){ .icon } (det är också möjligt att kopiera och klistra in en tidigare regel).

8.  Ge regeln en etikett (*nimiö*) (se [Etiketter](symbols-labels.md#labels)) och lägg till ett filter (se [Filter](filters.md)). Med *Testi*-knappen kan du prova hur många objekt filtret returnerar.

    ![Regelredigering i panelen Lagerstilar där filteruttrycket ”Filter” och knappen ”Test” är markerade med rött](../images/styling-rule-based-6.png)

9.  Redigera symbolen och dess färg på det sätt du önskar.
