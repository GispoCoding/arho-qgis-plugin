# Redigera och ta bort ett befintligt planutkast

1.  Om du vill granska redan skapade planer, välj *Kaavasuunnitelma* → *Kaavasuunnitelmat* och välj önskad plan i listan.

2.  Om du vill redigera uppgifterna för ett befintligt planutkast, väljer du *Kaavasuunnitelman tiedot* eller dubbelklickar på önskad rad för planutkastet i fönstret *Kaavasuunnitelmat*. Obs! Om planen har godkänts kan du inte längre redigera den.

3.  Om du vill redigera planutkastets yttre gräns, använd QGIS digitaliseringsverktyg. Flyttning av brytpunkter görs med digitaliseringsverktygens **brytpunktsverktyg** (*Taitepistetyökalu*) ![](../images/plan-edit-1.png){ .icon }. Observera att du kan välja vilket lager verktygets funktioner ska riktas mot.

    ![](../images/plan-edit-2.png)

4.  Planutkast och planärenden kan endast **tas bort** av en person som har admin-behörighet i databasen. När du vill ta bort ett planutkast:

    1.  Ta först bort alla planobjekt som finns i utkastet.

    2.  Välj *kaavasuunnitelma* som aktivt i lagerpanelen (*Tasot*), välj planens yttre gräns som aktiv på kartan med markeringsverktyget ![](../images/plan-edit-3.png){ .icon } och tryck på **Delete**. Kom ihåg att se till att lagret är redigerbart, det vill säga att redigeringsläget är aktiverat ![](../images/plan-edit-4.png){ .icon }.

    3.  Om det uppstår problem med att spara eller ta bort planen eller planobjektet, välj ikonen Nuvarande redigeringar (***Nykyiset muokkaukset***) i digitaliseringsverktyget och ett lämpligt alternativ, t.ex. Återställ för alla lager (*Peruutus kaikille tasoille*). Denna åtgärd återställer projektet till utgångsläget före den senaste redigeringen.

        ![](../images/plan-edit-5.png)
