# Käyttöönotto

Tämä sivu kertoo, miten organisaatio ottaa Arhon käyttöön. Jos olet Arhon käyttäjä ja haluat vain aloittaa, lue käyttöohjeen sivu [Käyttöönotto](../manual/setup.md).

## Mitä tarvitset { #requirements }

- **QGIS**, mieluiten LTR-versio
- **Arho-lisäosa**
- **Arhon QGIS-projektitiedosto**
- **taustajärjestelmä**, johon kaavatiedot tallentuvat ja joka hoitaa yhteydet Ryhtiin

Osat kuvataan tarkemmin sivulla [Arhosta](index.md#parts).

## Lisäosa { #plugin }

Arho-lisäosa asennetaan GitHubista kokeellisena lisäosana. Ohje on käyttöohjeen sivulla [Käyttöönotto](../manual/setup.md#install).

## Taustajärjestelmä { #backend }

Taustajärjestelmän lähdekoodi on [arho-backend](https://github.com/GispoCoding/arho-backend)-repositoriossa. Taustajärjestelmä toimii AWS-pilvipalvelussa, ja se asennetaan Terraformilla. Asennusohje on repositorion tiedostossa [infra/README.md](https://github.com/GispoCoding/arho-backend/blob/main/infra/README.md).

## Apua käyttöönottoon { #help }

Gispo tarjoaa Arhoa myös palveluna: ylläpidon, käyttöönoton ja tuen. Lisätietoa on osoitteessa [gispo.fi/arho](https://www.gispo.fi/arho).

## Ohjeet { #guides }

- **Käyttäjät**: aloita käyttöohjeen sivulta [Käyttöönotto](../manual/setup.md).
- **Pääkäyttäjät**: käyttöönoton tekniset vaiheet ja pääkäyttäjän tehtävät ovat erillisessä ohjeessa: [Arho tekninen ohje – käyttöönotto ja pääkäyttäjä](https://docs.google.com/document/d/1HaIzgdJiOIgSZ1bA6tcsnur_4W45OwxJv8bEWOxZIeM/edit?usp=sharing).
