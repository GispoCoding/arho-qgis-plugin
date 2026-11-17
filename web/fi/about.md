# Arhosta

Arho on QGISin päällä toimiva avoimen lähdekoodin kaavoitustyökalu, jolla voidaan tehdä tietomallimuotoista kaavaa vietäväksi valtakunnalliseen Ryhti-järjestelmään. Arhoa on kehitetty kumppanitestaushankkeissa, samoissa hankkeissa on luotu ja päivitetty tämä ohje.

Tämä ohje sisältää ohjeet Arhon käyttämiseen. Ohje päivittyy Arhon kehittyessä. Käyttöönottoa ja pääkäyttäjää varten on erillinen ohje: [Arho tekninen ohje – käyttöönotto ja pääkäyttäjä](https://docs.google.com/document/d/1HaIzgdJiOIgSZ1bA6tcsnur_4W45OwxJv8bEWOxZIeM/edit?usp=sharing).

## Mikä Arho on?

Arho on avoimeen lähdekoodiin perustuva QGIS-paikkatieto-ohjelman kanssa toimiva kaavoitustyökalu, jolla voidaan tuottaa lain vaatimaa tietomallimuotoista kaavatietoa.

Arho on kokonaisuus, jossa käyttöliittymän muodostavat QGIS ja Arho-lisäosa. Arholle laadittu QGIS-projektitiedosto on keskeinen osa Arhon käyttöä. Taustajärjestelmä (backend) on toteutettu AWS-pilvipalveluun, ja se sisältää:

- tietokannan, johon kaavatiedot tallentuvat
- koodistojen päivitystyökalun
- Ryhti-rajapintatyökalut
- SSH-tunnelipalvelimen
- tietokannan hallinta- ja migraatiotyökalun
- (Palveluväylän liityntäpalvelimen).

Arho ei siis ole pelkkä lisäosa, vaan kokonaisuus, jonka kaikkia osia tarvitaan.

## Arhon käyttöönotto

Arhon käyttöönottoa varten on erillinen teknisempi ohje, jossa käydään läpi seuraavat vaiheet:

- SSH-tunnelin luonti ja yhteyden muodostaminen (käytössä testi- ja kokeiluympäristöissä)
- tietokantayhteyden aputiedoston (`PGSERVICEFILE`) luominen
- QGIS-profiilin luonti, QGISin ympäristöasetukset ja autentikointitietojen tallennus QGISiin.
