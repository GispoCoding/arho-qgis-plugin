# Käyttöönotto

Ennen kuin aloitat Arhon käytön, tarvitset QGISin, Arho-lisäosan ja toimivan yhteyden Arhon tietokantaan. Yhteyden muodostamisen ja asennuksen tarkemmat vaiheet kuvataan erillisessä ohjeessa: [Arho tekninen ohje – käyttöönotto ja pääkäyttäjä](https://docs.google.com/document/d/1HaIzgdJiOIgSZ1bA6tcsnur_4W45OwxJv8bEWOxZIeM/edit?usp=sharing).

## QGIS { #qgis }

Arhoa käytetään QGISin päällä. QGISistä on suositeltavaa käyttää LTR-versiota (tätä kirjoitettaessa versio **QGIS 3.44**).

QGISissä on suositeltavaa käyttää Arhoa varten luotua käyttäjäprofiilia, johon tallentuu Arho-lisäosa, tietokantayhteys ja sen tarvitsema autentikointi ja myöhemmin tieto profiililla käytetyistä projektitiedostoista.

## Arho-lisäosan asennus { #install }

Arho-lisäosa asennetaan QGISin **Lisäosat > Hallitse ja asenna lisäosia** -valikosta. Arho asennetaan kokeellisena lisäosana osoitteesta:

```text
https://github.com/GispoCoding/arho-feature-template/releases/latest/download/plugins.xml
```

## Yhteyden tarkistus { #connection }

Ennen Arhon käyttöä varmistu, että Arho-yhteytesi on auki ja yhteys tietokantaan toimii. Jos QGIS kysyy tietokannan käyttäjätunnusta ja salasanaa, on yhteydessä tai käyttöönoton toimenpiteissä jotain vialla, sillä QGISin pitäisi löytää ja käyttää kirjautumistiedot tallennetusta autentikoinnista.

## Lisäosan päivitys { #update }

Kun Arho kehittyy, tulee lisäosasta saataville uudempi versio. Päivitä lisäosa QGISissä kohdasta **Hallitse ja asenna lisäosia**.

## Seuraavaksi

Kun QGIS, lisäosa ja yhteys toimivat, ota käyttöön [kaavoitusprojekti](project.md).
