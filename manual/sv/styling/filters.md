# Filter (Suodattimet)

Nödvändiga QGIS-funktioner för att skapa filter:

| QGIS-funktion | Vad gör den? | Exempel |
|---|---|---|
| `map_akeys` | Returnerar alla nycklar i en nyckel-värdetabell (map) som en tabell. | `map_akeys("primary_use")` |
| `array` | Skapar en tabell av de värden som anges som parametrar. | `array('teollisuusalue', 'varastoalue')` |
| `map_exist` | Returnerar TRUE om nyckeln som angetts som parameter finns i nyckel-värdetabellen (map). | `map_exist("primary_use", 'teollisuusalue')` |
| `map_get` | Returnerar det värde som motsvarar den angivna nyckeln från en nyckel-värdetabell (map). Om nyckeln inte finns i nyckel-värdetabellen returnerar funktionen NULL. | `map_get("type_regulations", 'tie')` |
| `array_sort` | Sorterar text och nummer i en lista. | `array_sort(array('varastoalue', 'teollisuusalue'))` |
| `array_contains` | Returnerar TRUE om värdet som angetts som parameter finns i tabellen. | `array_contains(map_akeys(map_get("type_regulations", 'valtatie')), 'uusi')` |
| `array_length` | Returnerar antalet element i en tabell. | `array_length(map_akeys(map_get("type_regulations", 'tie'))) = 0` |
| `array_foreach` | Returnerar en tabell där det angivna uttrycket (expression) har körts för varje objekt. | `array_foreach(map_get(map_get("sub_area", 'kehittamisvyohyke'), 'kayttotarkoituskohdistus'), map_get(@element, 'code_value'))` |

## Enkelt filter

Planobjekt kan filtreras utifrån det ovan nämnda JSON-fältet med hjälp av följande typer av uttryck:

```sql
map_akeys("fältets_namn") = array('nyckelns_namn')
```

eller

```sql
map_exist("fältets_namn", 'nyckelns_namn')
```

Av dessa tar det förstnämnda uttrycket (`map_akeys`) alla nycklar som finns i JSON-strukturen och skapar en tabell av dem, medan det sistnämnda (`map_exist`) endast kontrollerar om den efterfrågade nyckeln existerar i fältet. Observera att olika typer av citattecken används för att hänvisa till fältets namn (`"fältets_namn"`) respektive nyckel (`'nyckelns_namn'`).

Exempel:

```sql
map_akeys("primary_use") = array('taajamatoimintojenAlue')
```

eller

```sql
map_exist("primary_use", 'taajamatoimintojenAlue')
```

## Flera nycklar

Om planobjektets JSON innehåller flera nycklar kan objektet filtreras till exempel på följande sätt:

```sql
array_sort(map_akeys("primary_use")) = array('teollisuusalue', 'varastoalue')
```

I detta uttryck sorterar `array_sort` nycklarna i alfabetisk ordning.

## Nyckelns värde

Om en nyckel i objektets JSON har ett visst värde, t.ex. ”ny” (`uusi`), krävs ett något mer komplext uttryck:

```json
{
  "valtatie": {
    "uusi": {}
  }
}
```

Uttryck kan kedjas samman med hjälp av operatorerna AND (eller OR):

```sql
map_akeys("type_regulations") = array('valtatie')
AND
array_contains(map_akeys(map_get("type_regulations", 'valtatie')), 'uusi')
```

Det sistnämnda uttrycket hämtar värdet som motsvarar nyckeln `'valtatie'` (riksväg) från fältet `"type_regulations"`. Funktionen `map_akeys` gör om detta sökresultat till en tabell och funktionen `array_contains` kontrollerar om värdet `'uusi'` finns i denna lista.

## Mer detaljerade filter

Ibland kan det vara nödvändigt att skapa ännu mer detaljerade och unika filter. Anta till exempel att vi har två planobjekt, där det första har följande JSON-struktur:

```json
{
  "teollisuusalue": {
    "paakayttotarkoitus": {}
  },
  "varastoalue": {
    "paakayttotarkoitus": {}
  }
}
```

och det andra har följande struktur:

```json
{
  "teollisuusalue": {
    "VaarallistenKemikaalienValmistusJaVarastointiSallittu": {},
    "paakayttotarkoitus": {}
  },
  "varastoalue": {
    "VaarallistenKemikaalienValmistusJaVarastointiSallittu": {},
    "paakayttotarkoitus": {}
  }
}
```

I detta fall är följande uttryck inte tillräckligt unikt, eftersom det hittar båda objekten:

```sql
array_sort(map_akeys("type_regulations")) = array('teollisuusalue', 'varastoalue')
AND
array_contains(map_akeys(map_get("type_regulations", 'teollisuusalue')), 'paakayttotarkoitus')
AND
array_contains(map_akeys(map_get("type_regulations", 'varastoalue')), 'paakayttotarkoitus')
```

Däremot kan man för det planobjekt som har den första JSON-strukturen använda exempelvis följande uttryck:

```sql
array_sort(map_akeys("type_regulations")) = array('teollisuusalue', 'varastoalue')
AND
array_contains(map_akeys(map_get("type_regulations", 'teollisuusalue')), 'paakayttotarkoitus')
AND
array_contains(map_akeys(map_get("type_regulations", 'varastoalue')), 'paakayttotarkoitus')
AND
NOT array_contains(
  map_akeys(map_get("type_regulations", 'teollisuusalue')),
  'VaarallistenKemikaalienValmistusJaVarastointiSallittu'
)
```

För att filtrera fram det sistnämnda objektet passar följande uttryck:

```sql
map_exist("type_regulations", 'teollisuusalue')
AND
map_exist("type_regulations", 'varastoalue')
AND
map_exist("type_regulations"['teollisuusalue'], 'VaarallistenKemikaalienValmistusJaVarastointiSallittu')
AND
map_exist("type_regulations"['varastoalue'], 'VaarallistenKemikaalienValmistusJaVarastointiSallittu')
```

## Nyckel utan information

Ibland vill man med filtret avgränsa endast sådana planbestämmelsegrupper där det under en viss nyckel endast finns en specifik information. Med följande exempeluttryck väljs endast de planbestämmelsegrupper som enbart innehåller planbestämmelsen `tie` (väg), vilken inte innehåller någon information:

```sql
array_sort(map_akeys("type_regulations")) = array('tie')
AND
array_length(map_akeys(map_get("type_regulations", 'tie'))) = 0
```

## Flera tilläggsinformationstyper med samma namn

Om en planbestämmelsegrupp innehåller flera tilläggsinformationstyper med samma namn, kan följande uttryck användas:

```sql
(
  array_sort(map_akeys("sub_area")) = array('kehittamisvyohyke')
  AND
  array_sort(
    array_foreach(
      map_get(map_get("sub_area", 'kehittamisvyohyke'), 'kayttotarkoituskohdistus'),
      map_get(@element, 'code_value')
    )
  ) = array('matkailupalvelujenAlue', 'virkistysalue')
)
AND
array_sort(map_akeys("regulation_values")) = array('sanallinenMaarays')
```

Uttrycket kontrollerar först att fältet `"sub_area"` innehåller exakt en nyckel: `'kehittamisvyohyke'` (utvecklingszon).

```sql
array_sort(map_akeys("sub_area")) = array('kehittamisvyohyke')
```

Sedan går uttrycket igenom värdet för `code_value` under de `kayttotarkoituskohdistus`-nycklar som finns under `'kehittamisvyohyke'`. Av dessa bildas en lista. Uttrycket kontrollerar att dessa `'code_value'`-värden är exakt `'matkailupalvelujenAlue'` och `'virkistysalue'`.

```sql
array_sort(
  array_foreach(
    map_get(map_get("sub_area", 'kehittamisvyohyke'), 'kayttotarkoituskohdistus'),
    map_get(@element, 'code_value')
  )
) = array('matkailupalvelujenAlue', 'virkistysalue')
```

Slutligen kontrolleras att planbestämmelsegruppen innehåller en skriftlig bestämmelse, det vill säga att fältet `"regulation_values"` innehåller nyckeln `'sanallinenMaarays'`.

```sql
array_sort(map_akeys("regulation_values")) = array('sanallinenMaarays')
```
