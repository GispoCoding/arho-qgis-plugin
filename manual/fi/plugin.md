# Arho-lisäosa

## Arho-lisäosan asennus

Arho-lisäosa asennetaan QGISin **Lisäosat > Hallitse ja asenna lisäosia** -valikosta. Arho asennetaan kokeellisena lisäosana osoitteesta:

```text
https://github.com/GispoCoding/arho-feature-template/releases/latest/download/plugins.xml
```

Tarkemmat ohjeet lisäosan asennukseen löytyvät käyttöönotto-ohjeesta.

## Lisäosan päivitys

Kun Arho kehittyy, tulee lisäosasta saataville uudempi versio. Päivitä lisäosa QGISissä kohdasta **Hallitse ja asenna lisäosia**.

## Arhon käyttöliittymä

Arho-lisäosan mukana QGISiin tulee Arhon työkalupalkki.

![Arhon työkalupalkki, jossa mm. ”Kaava-asia”- ja ”Kaavasuunnitelma”-valikot sekä ”Validointi” ja ”Asetukset”](images/plugin-1.png)

Työkalut ovat harmaina, jos niitä ei sillä hetkellä voi käyttää. Esimerkiksi jos auki ei ole yhtään aktiivista kaavasuunnitelmaa, eivät myöskään kaavakohteiden ja kaavamääräysryhmien työkalut ole aktiivisina.

Tämä käyttöohje käsittelee näitä työkaluja ja niiden alta löytyviä toimintoja omissa osioissaan.

QGISin **Lisäosat**-valikon alta pääsee myös käsiksi Arhon asetuksiin ja työkaluihin.

![QGISin ”Lisäosat”-valikko ja sen ”ARHOfeaturetemplate”-alavalikko Arhon toimintoineen ja asetuksineen](images/plugin-2.png)

Viimeisenä listalla oleva **Avaa lokikansio** vie käyttäjän kansioon, johon Arho tallentaa käyttäjän toimia. Tämä tiedosto on tarpeen, kun haluaa raportoida ongelman Arhossa, sillä se auttaa kehittäjiä selvittämään ongelman.

Karttaikkunaan tulee kaavoitusprojektin myötä tieto, mikä kaava-asia ja mikä kaavasuunnitelma ikkunassa on aktiivisena. Jos kohta on tyhjä, mikään ei ole aktiivisena. Esimerkiksi alla on aktiivinen kaava-asia, mutta ei yhtään aktiivista kaavasuunnitelmaa.

![Karttaikkunan teksti, jossa näkyy aktiivinen kaava-asia, mutta ”Kaavasuunnitelma”-kohta on tyhjä](images/plugin-3.png)
