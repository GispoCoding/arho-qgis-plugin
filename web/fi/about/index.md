# Arhosta

Arho on kaavoittajan työkalu. Sillä tehdään tietomallimuotoisia kaavoja QGISissä ja viedään ne valtakunnalliseen Ryhti-järjestelmään. Arho on avointa lähdekoodia.

Arho on vielä kehitysvaiheessa. Siihen tulee uusia toimintoja, ja vanhat voivat muuttua.

## Miksi Arho? { #why }

Laki velvoittaa kunnat ja maakuntien liitot tuottamaan kaavatiedon tietomallimuotoisena Rakennetun ympäristön tietojärjestelmään eli Ryhtiin. Kaavatietoa voi viedä Ryhtiin jo nyt, ja vuodesta 2029 alkaen se on pakollista. Arholla kaavoittaja tekee tietomallimuotoisen kaavan tutussa QGIS-ympäristössä, validoi sen ja vie sen Ryhtiin.

## Mistä Arho koostuu? { #parts }

Arho ei ole pelkkä lisäosa. Se on kokonaisuus, jonka kaikkia osia tarvitaan:

- **QGIS**: avoimen lähdekoodin paikkatieto-ohjelma, jossa kaava tehdään.
- **Arho-lisäosa**: QGISin lisäosa, jonka työkaluilla kaava tehdään.
- **Arhon QGIS-projektitiedosto** (*kaavoitus*-projekti): karttatasot ja asetukset, joita Arho tarvitsee.
- **Taustajärjestelmä** (backend), joka toimii AWS-pilvipalvelussa. Se sisältää:
    - tietokannan, johon kaavatiedot tallentuvat
    - koodistojen päivitystyökalun
    - Ryhti-rajapintatyökalut
    - SSH-tunnelipalvelimen
    - tietokannan hallinta- ja migraatiotyökalun
    - tarvittaessa Palveluväylän liityntäpalvelimen.

## Avoin lähdekoodi ja osallistuminen { #open-source }

Arhon lähdekoodi on avointa:

- Arho-lisäosa: [GispoCoding/arho-qgis-plugin](https://github.com/GispoCoding/arho-qgis-plugin), GPL v2 -lisenssi
- Taustajärjestelmä: [GispoCoding/arho-backend](https://github.com/GispoCoding/arho-backend), MIT-lisenssi

Voit osallistua näin:

- Ilmoita virheestä tai ehdota parannusta GitHubin issueissa: [lisäosa](https://github.com/GispoCoding/arho-qgis-plugin/issues), [taustajärjestelmä](https://github.com/GispoCoding/arho-backend/issues).
- Korjaa tätä ohjetta: sivun oikeassa yläkulmassa on muokkauspainike, joka avaa sivun GitHubissa.

Gispo kehittää Arhoa yhdessä sitä käyttävien organisaatioiden kanssa kumppanikehityshankkeissa.

Lue seuraavaksi, miten Arho [otetaan käyttöön](deployment.md).
