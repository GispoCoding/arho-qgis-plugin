# Suodattimet

Suodattimien tekemiseen tarpeelliset QGIS-funktiot:

| QGIS-funktio | Mitä tekee? | Esimerkki |
|---|---|---|
| `map_akeys` | Palauttaa kaikki avain-arvotaulukon avaimet taulukkona. | `map_akeys("primary_use")` |
| `array` | Luo taulukon parametrina annettavista arvoista. | `array('teollisuusalue', 'varastoalue')` |
| `map_exist` | Palauttaa TRUE, jos parametrina annettu avain on avain-arvotaulukossa (map). | `map_exist("primary_use", 'teollisuusalue')` |
| `map_get` | Palauttaa parametrina annettua avainta vastaavan arvon avain-arvotaulukosta (map). Jos avain ei esiinny avain-arvotaulukossa, funktio palauttaa NULL. | `map_get("type_regulations", 'tie')` |
| `array_sort` | Järjestää listan merkkijonot ja numerot. | `array_sort(array('varastoalue', 'teollisuusalue'))` |
| `array_contains` | Palauttaa TRUE, jos parametrina annettu arvo on taulukossa. | `array_contains(map_akeys(map_get("type_regulations", 'valtatie')), 'uusi')` |
| `array_length` | Palauttaa taulukon elementtien lukumäärän. | `array_length(map_akeys(map_get("type_regulations", 'tie'))) = 0` |
| `array_foreach` | Palauttaa taulukon, jossa annettu lauseke on suoritettu jokaiselle kohteelle. | `array_foreach(map_get(map_get("sub_area", 'kehittamisvyohyke'), 'kayttotarkoituskohdistus'), map_get(@element, 'code_value'))` |

## Yksinkertainen suodatin

Kaavakohteita voidaan suodattaa edellä mainitun JSON-kentän perusteella käyttäen seuraavanlaisia lausekkeita:

```sql
map_akeys("kentan_nimi") = array('avaimen_nimi')
```

tai

```sql
map_exist("kentan_nimi", 'avaimen_nimi')
```

Näistä edellinen (`map_akeys`) ottaa kaikki JSONista löytyvät avaimet ja tekee niistä taulukon, kun taas jälkimmäinen (`map_exist`) tarkastelee vain, löytyykö kentästä kysyttyä avainta. Huomaa, että kentän nimeen ja avaimeen viittaamiseen käytetään erilaisia lainausmerkkejä: kentän nimi on lainausmerkeissä (`"kentan_nimi"`) ja avain heittomerkeissä (`'avaimen_nimi'`).

Esimerkki:

```sql
map_akeys("primary_use") = array('taajamatoimintojenAlue')
```

tai

```sql
map_exist("primary_use", 'taajamatoimintojenAlue')
```

## Useita avaimia

Jos kaavakohteen JSONissa on useita avaimia, voidaan kohde suodattaa esimerkiksi seuraavasti:

```sql
array_sort(map_akeys("primary_use")) = array('teollisuusalue', 'varastoalue')
```

Lausekkeessa `array_sort` asettaa avaimet aakkosjärjestykseen.

## Avaimen arvo

Jos kohteen JSONin avaimella on jokin arvo, esim. `uusi`, tarvitaan hieman monimutkaisempi lauseke.

```json
{
  "valtatie": {
    "uusi": {}
  }
}
```

Lausekkeita voidaan niputtaa yhteen käyttäen AND- (tai OR-) operaattoreita.

```sql
map_akeys("type_regulations") = array('valtatie')
AND
array_contains(map_akeys(map_get("type_regulations", 'valtatie')), 'uusi')
```

Jälkimmäinen lauseke hakee avainta `'valtatie'` vastaavan arvon `"type_regulations"`-kentästä. Funktio `map_akeys` tekee tästä hakutuloksesta taulukon, ja funktio `array_contains` tarkistaa, löytyykö tästä taulukosta arvo `'uusi'`.

## Tarkemmat suodattimet

Joskus voi olla tarpeen luoda vieläkin yksityiskohtaisempia yksilöiviä suodattimia. Esimerkiksi kahdelle kaavakohteelle, joista ensimmäisellä on

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

ja toisella

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

seuraava lauseke ei ole tarpeeksi yksilöivä, koska se löytää molemmat kohteet:

```sql
array_sort(map_akeys("type_regulations")) = array('teollisuusalue', 'varastoalue')
AND
array_contains(map_akeys(map_get("type_regulations", 'teollisuusalue')), 'paakayttotarkoitus')
AND
array_contains(map_akeys(map_get("type_regulations", 'varastoalue')), 'paakayttotarkoitus')
```

Sen sijaan kaavakohteelle, jolla on ensimmäinen JSON, voidaan käyttää esim. seuraavaa lauseketta:

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

Jälkimmäisen kohteen suodattamiseksi sopii seuraava lauseke:

```sql
map_exist("type_regulations", 'teollisuusalue')
AND
map_exist("type_regulations", 'varastoalue')
AND
map_exist("type_regulations"['teollisuusalue'], 'VaarallistenKemikaalienValmistusJaVarastointiSallittu')
AND
map_exist("type_regulations"['varastoalue'], 'VaarallistenKemikaalienValmistusJaVarastointiSallittu')
```

## Avain ilman tietoja

Joskus suodattimella halutaan rajata vain kaavamääräysryhmiä, joilla tietyn avaimen alla on ainoastaan tietty tietue. Alla olevalla esimerkkilausekkeella valitaan vain kaavamääräysryhmät, jotka sisältävät vain kaavamääräyksen `tie`, joka ei sisällä mitään tietoa.

```sql
array_sort(map_akeys("type_regulations")) = array('tie')
AND
array_length(map_akeys(map_get("type_regulations", 'tie'))) = 0
```

## Useita samannimisiä lisätiedon lajeja

Jos kaavamääräysryhmä sisältää useamman samannimisen lisätiedon lajin, voidaan käyttää seuraavaa lauseketta:

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

Lauseke tarkistaa ensin, että `"sub_area"`-kenttä sisältää täsmälleen yhden avaimen `'kehittamisvyohyke'`.

```sql
array_sort(map_akeys("sub_area")) = array('kehittamisvyohyke')
```

Sitten lausekkeessa käydään läpi `'kehittamisvyohyke'`-avaimen alla olevien `'kayttotarkoituskohdistus'`-avainten `'code_value'`-arvot. Näistä muodostetaan lista. Lauseke tarkistaa, että `'code_value'`-arvot ovat täsmälleen `'matkailupalvelujenAlue'` ja `'virkistysalue'`.

```sql
array_sort(
  array_foreach(
    map_get(map_get("sub_area", 'kehittamisvyohyke'), 'kayttotarkoituskohdistus'),
    map_get(@element, 'code_value')
  )
) = array('matkailupalvelujenAlue', 'virkistysalue')
```

Lopuksi vielä tarkistetaan, että kaavamääräysryhmä sisältää sanallisen määräyksen eli `regulation_values`-kenttä sisältää avaimen `'sanallinenMaarays'`.

```sql
array_sort(map_akeys("regulation_values")) = array('sanallinenMaarays')
```
