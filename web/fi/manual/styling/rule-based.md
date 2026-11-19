# Sääntöpohjaisen visualisoinnin tekeminen QGISissä

Jos käyttäjä haluaa tehdä omia visualisointeja, tulee niille luoda omat erilliset QML-tiedostot. Jos käyttäjä vain muokkaa Arhon oletustyylejä, muutokset tulevat ylikirjoitetuiksi seuraavan lisäosapäivityksen yhteydessä.

Sääntöpohjaiset visualisoinnit voidaan luoda kaavakohteille seuraavasti:

1.  Avaa **Tason tyylit** -paneeli ![”Tason tyylit” -paneelin painike](../images/styling-rule-based-1.png){ .icon } -painikkeella (tai **Näytä > Paneelit > Tason tyylit**).

2.  Valitse tyyliteltävä taso alasvetovalikosta.

3.  Valitse välilehdeltä **Kuvaustekniikka** alasvetovalikosta **Sääntöpohjainen**.

    ![”Tason tyylit” -paneeli, jossa korostettuna tyyliteltävä taso ja kuvaustekniikka ”Sääntöpohjainen”](../images/styling-rule-based-2.png)

4.  Valitse tai digitoi tyyliteltävä kaavakohde ja lisää sille sopiva kaavamääräysryhmä.

5.  Tarkastele tyyliteltävän kohteen tietoja käyttäen **Näytä kohteen tiedot** -työkalua ![Näytä kohteen tiedot -työkalu](../images/styling-rule-based-3.png){ .icon }.

6.  Kohteen tiedoista löytyy kenttä `primary_use` (aluevaraus), `sub_area` (osa-alueet), `type_regulations` (pisteet ja viivat) tai `regulation_values` (osa-alueet, pisteet). Tämän kentän sisältämän JSONin avulla voidaan luoda kohteen kaavamääräysryhmän yksilöivä suodatin. Joissain tapauksissa kohteen tiedot voivat sisältää useamman kentän (osa-alueet). Katso ohjeet suodattimien luomiseen kohdasta [Suodattimet](filters.md).

    ![”Kohteen tiedot” -paneeli, jossa aluevarauksen ”primary_use”-kentän JSON-arvo korostettuna](../images/styling-rule-based-4.png){ width="526" }

7.  Lisää uusi sääntö ![Lisää-painike](../images/styling-rule-based-5.png){ .icon } -painikkeella (myös aiemman säännön kopiointi ja liittäminen on mahdollista).

8.  Anna säännölle nimiö (katso [Nimiöt](symbols-labels.md#labels)) ja lisää suodatin (katso [Suodattimet](filters.md)). **Testi**-painikkeella voit kokeilla, kuinka monta kohdetta suodatin palauttaa.

    ![Tason tyylit -paneelin säännön muokkaus, jossa ”Filter”-lauseke ja ”Test”-painike on korostettu punaisella](../images/styling-rule-based-6.png)

9.  Muokkaa symbolia ja sen väriä haluamallasi tavalla.
