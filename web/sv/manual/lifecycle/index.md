# Livscykelskeden (Elinkaaren vaiheet)

!!! info "Inte översatt ännu"

    Det här kapitlet finns i sin helhet bara på finska. Läs den finska versionen: [Elinkaaren vaiheet ja niiden hallinta Arhossa](/arho-qgis-plugin/manual/lifecycle/). Nedan finns en kort sammanfattning på svenska.

Ryhti definierar planens livscykelskeden i plandatamodellens [livscykel- och kvalitetsregler](https://ryhti.syke.fi/alueidenkaytto/tietomallimuotoinen-kaavoitus/kaavatietomallin-elinkaari-ja-laatusaannot/). Med Arho är det möjligt att producera planmaterial i alla planens livscykelskeden. Varje livscykelskede behöver ett eget planutkast, som kan skapas utifrån det föregående skedets planutkast (se [Nytt planutkast från ett befintligt planutkast](../plan/create.md#from-existing)) eller helt från början.

!!! warning "Obs!"

    Överföringen av planen till nästa skede sker aldrig genom att redigera livscykelskedet i planutkastets uppgifter, utan alltid genom att skapa ett nytt planutkast.

När du skapar en ny version av ett planutkast och ger det ett livscykelskede, betyder det att du börjar arbeta på ett planutkast som i slutet av arbetet bildar planmaterialet för det aktuella livscykelskedet och kan exporteras till Ryhti som material för detta skede. Om du alltså väljer ”Gällande” (*Voimassa*) som livscykelskede betyder det inte att planutkastet du skapar omedelbart markeras som gällande, utan att du arbetar på en version som är avsedd att bli den gällande planen.
