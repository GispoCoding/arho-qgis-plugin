<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.40.3-Bratislava" styleCategories="Symbology|Labeling" labelsEnabled="1">
  <renderer-v2 type="RuleRenderer" referencescale="-1" symbollevels="0" forceraster="0" enableorderby="0">
    <rules key="{178e2009-9047-4176-9ebc-9cb596008dd4}">
      <rule key="{67098b2b-c7b1-4727-bd83-4d2a5febcd08}" symbol="0" label="Nykyinen tie" filter="array_sort(map_akeys(&quot;type_regulations&quot;)) = array('tie')&#xd;&#xa;AND&#xd;&#xa;array_length(map_akeys(map_get(&quot;type_regulations&quot;, 'tie'))) = 0"/>
      <rule key="{71233534-3647-4254-ab4e-2187e3ab0742}" symbol="1" label="Moottori- tai moottoriliikennetie" filter="map_akeys(&quot;type_regulations&quot;) = array('moottoriTaiMoottoriliikenneTie')"/>
      <rule key="{903c9f98-cd42-4ffd-83d5-a079d3fcc05b}" symbol="2" label="Kaksiajoratainen tie tai katu" filter="map_akeys(&quot;type_regulations&quot;) = array('kaksiajoratainenTieTaiKatu')&#xa;"/>
      <rule key="{6101e3f2-3657-494a-ba45-850bbbc7fd1a}" symbol="3" label="Valtatie tai kantatie" filter="array_sort(map_akeys(&quot;type_regulations&quot;)) = array('kantatie', 'valtatie')"/>
      <rule key="{7fd7f716-8a76-48fb-a7f9-c76001237174}" symbol="4" label="Valtatie" filter="array_sort(map_akeys(&quot;type_regulations&quot;)) = array('valtatie')&#xd;&#xa;AND array_length(map_akeys(map_get(&quot;type_regulations&quot;, 'valtatie'))) = 0"/>
      <rule key="{d0c7fc7b-9ff1-49cf-aab4-75aada06ccaf}" symbol="5" label="Kantatie" filter="map_akeys(&quot;type_regulations&quot;) = array('kantatie')"/>
      <rule key="{44525622-070c-4471-a3a7-46f008ba8620}" symbol="6" label="Seututie tai pääkatu" filter="array_sort(map_akeys(&quot;type_regulations&quot;)) = array('paakatu', 'seututie')"/>
      <rule key="{6a34abbc-f383-4161-a5af-abe469946ddc}" symbol="7" label="Seututie" filter="map_akeys(&quot;type_regulations&quot;) = array('seututie')"/>
      <rule key="{792a7b80-beaf-4c1d-a197-5203a90c62c1}" symbol="8" label="Pääkatu" filter="map_akeys(&quot;type_regulations&quot;) = array('paakatu')"/>
      <rule key="{7b22538e-f2b4-4311-ba19-8bcb222a154a}" symbol="9" label="Yhdystie" filter="map_akeys(&quot;type_regulations&quot;) = array('yhdystie')"/>
      <rule key="{a98bce27-0290-4dfb-858f-073cc2c872c4}" symbol="10" label="Rautatie" filter="array_sort(map_akeys(&quot;type_regulations&quot;)) = array('raideliikenteenAlue')&#xd;&#xa;AND array_length(map_akeys(map_get(&quot;type_regulations&quot;, 'raideliikenteenAlue'))) = 0"/>
      <rule key="{8f4efa89-4f16-4b9e-959c-3c678ce4eb9a}" symbol="11" label="Päärata" filter="map_akeys(&quot;type_regulations&quot;) = array('paarata')"/>
      <rule key="{e036841f-7968-4755-bbaf-2eccc1895778}" symbol="12" label="Yhdysrata" filter="map_akeys(&quot;type_regulations&quot;) = array('yhdysrata')"/>
      <rule key="{b78e78f6-b84a-46df-98e1-95f765d962b0}" symbol="13" label="Sivurata" filter="map_akeys(&quot;type_regulations&quot;) = array('sivurata')"/>
      <rule key="{0603add6-11ca-428e-a0d4-fbef5c3ee594}" symbol="14" label="Kaupunkirata" filter="map_akeys(&quot;type_regulations&quot;) = array('kaupunkirata')"/>
      <rule key="{37891b3d-4865-41ad-82fa-aa03f5727092}" symbol="15" label="Liikennetunneli" filter="map_akeys(&quot;type_regulations&quot;) = array('liikennetunneli')"/>
      <rule key="{30a4ce73-39f2-4b3d-94e5-77d9ce2bb7fb}" symbol="16" label="Moottorikelkkailureitti" filter="map_akeys(&quot;type_regulations&quot;) = array('moottorikelkkailureitti')"/>
      <rule key="{44e49c43-0c54-4c38-9e16-1d5c5f43a5c2}" symbol="17" label="Laivaväylä" filter="map_akeys(&quot;type_regulations&quot;) = array('laivavayla')"/>
      <rule key="{620ed046-20ad-41cc-a218-22ec1828c84b}" symbol="18" label="Veneväylä" filter="map_akeys(&quot;type_regulations&quot;) = array('venevayla')"/>
      <rule key="{f60df711-5cc6-4c66-93d5-75524ce4a506}" symbol="19" label="Lossi- tai lauttayhteys" filter="map_akeys(&quot;type_regulations&quot;) = array('lossiTaiLauttaYhteys')"/>
      <rule key="{5e62f549-e28d-400b-98be-6cce6338161e}" symbol="20" label="Nykyinen tie - olemassa oleva" filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'tie')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'tie')), 'olemassaOleva')"/>
      <rule key="{5eb48288-6088-4741-a782-c8332c4ac895}" symbol="21" label="Uusi tie" filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'tie')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'tie')), 'uusi')"/>
      <rule key="{43fc452b-c793-40d4-a03b-5d4cccba7a1d}" symbol="22" label="Merkittävästi parannettava tie" filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'tie')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'tie')), 'merkittavastiParannettava')"/>
      <rule key="{ff18458f-6403-4ed1-8477-c3341ad5b4c2}" symbol="23" label="Valtatie - olemassa oleva" filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'valtatie')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'valtatie')), 'olemassaOleva')"/>
      <rule key="{89ab51ca-9860-4610-a4bb-4696907e941e}" symbol="24" label="Uusi valtatie" filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'valtatie')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'valtatie')), 'uusi')"/>
      <rule key="{29b8e7aa-0354-4d55-a108-0e66af591a3c}" symbol="25" label="Merkittävästi parannettava valtatie" filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'valtatie')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'valtatie')), 'merkittavastiParannettava')"/>
      <rule key="{23054690-65d4-45e7-a5c6-42843ee054ea}" symbol="26" label="Tieliikenteen yhteystarve" filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'tie')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'tie')), 'yhteystarve')"/>
      <rule key="{6251c84e-c449-487c-81c7-ed638d6a2cd9}" symbol="27" label="Valtatien yhteystarve" filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'valtatie')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'valtatie')), 'yhteystarve')"/>
      <rule key="{f7d6210b-b460-467d-b9ff-dbbdc8ba9da2}" symbol="28" label="Ohjeellinen valtatie" filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'valtatie')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'valtatie')), 'ohjeellinenSijainti')"/>
      <rule key="{38105b36-b91a-4a72-8e13-c3f620ff5421}" symbol="29" label="Vaihtoehtoinen valtatie" filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'valtatie')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'valtatie')), 'vaihtoehtoinen')"/>
      <rule key="{1f55ab69-7e60-4a63-94cc-1b83d6b6458b}" symbol="30" label="Raideliikenteen yhteystarve" filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'raideliikenteenAlue')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'raideliikenteenAlue')), 'yhteystarve')"/>
      <rule key="{84e0192a-04c2-4529-8cbc-f434616051cf}" symbol="31" label="Joukkoliikenteen kehittämiskäytävä" filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'joukkoliikenteenAlue')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'joukkoliikenteenAlue')), 'kehitettava')"/>
      <rule key="{65e1875c-e1b4-4dfe-acf0-947c78eff78f}" symbol="32" label="Jalankulun ja pyöräilyn yhteystarve" filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'jalankulkualue')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'jalankulkualue')), 'yhteystarve')&#xa;AND&#xa;array_contains(map_akeys(&quot;type_regulations&quot;), 'pyorailyalue')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'pyorailyalue')), 'yhteystarve')"/>
      <rule key="{31db06af-f599-457a-b7ce-06b8433cc5ca}" symbol="33" label="Jalankulun yhteystarve" filter="map_akeys(&quot;type_regulations&quot;) = array('jalankulkualue')&#xa;AND&#xa;map_akeys(map_get(&quot;type_regulations&quot;, 'jalankulkualue')) = array('yhteystarve')"/>
      <rule key="{be570d05-afb3-42d8-ac59-3a5ed1c1600c}" symbol="34" label="Pyöräilyn yhteystarve" filter="map_akeys(&quot;type_regulations&quot;) = array('pyorailyalue')&#xa;AND&#xa;map_akeys(map_get(&quot;type_regulations&quot;, 'pyorailyalue')) = array('yhteystarve')"/>
      <rule key="{fa229435-2ad4-4b8f-a334-b3effc7a53c0}" symbol="35" label="Viheryhteys" filter="array_sort(map_akeys(&quot;type_regulations&quot;)) = array('viheryhteys')&#xd;&#xa;AND array_length(map_akeys(map_get(&quot;type_regulations&quot;, 'viheryhteys'))) = 0"/>
      <rule key="{6077dce3-b7c5-46e2-a096-dc76c43fca4c}" symbol="36" label="Viheryhteystarve" filter="map_akeys(&quot;type_regulations&quot;) = array('viheryhteys')&#xa;AND&#xa;map_akeys(map_get(&quot;type_regulations&quot;, 'viheryhteys')) = array('yhteystarve')"/>
      <rule key="{874ed9d8-89f9-4c73-a4f8-373cd066112d}" symbol="37" label="Sähkölinja tai voimajohto" filter="array_sort(map_akeys(&quot;type_regulations&quot;)) = array('sahkolinja')&#xd;&#xa;AND array_length(map_akeys(map_get(&quot;type_regulations&quot;, 'sahkolinja'))) = 0"/>
      <rule key="{6644aed6-61f7-46f7-94f6-b154c7186dc2}" symbol="38" label="Vesijohto tai viemäri" filter="array_sort(map_akeys(&quot;type_regulations&quot;)) = array('vesijohtoTaiViemari')&#xd;&#xa;AND array_length(map_akeys(map_get(&quot;type_regulations&quot;, 'vesijohtoTaiViemari'))) = 0"/>
      <rule key="{6274e6f7-0236-49a2-a434-97fe984faebb}" symbol="39" label="Kaasulinja" filter="array_sort(map_akeys(&quot;type_regulations&quot;)) = array('kaasulinja')&#xd;&#xa;AND array_length(map_akeys(map_get(&quot;type_regulations&quot;, 'kaasulinja'))) = 0"/>
      <rule key="{202bbd74-afd1-4045-bb53-5ab5f90b0cfa}" symbol="40" label="Uusi sähkölinja tai voimajohto" filter="map_akeys(&quot;type_regulations&quot;) = array('sahkolinja')&#xa;AND&#xa;map_akeys(map_get(&quot;type_regulations&quot;, 'sahkolinja')) = array('uusi')"/>
      <rule key="{b0f66703-7f3c-4fff-a9ea-9f62faeb1d0f}" symbol="41" label="Uusi vesijohto tai viemäri" filter="map_akeys(&quot;type_regulations&quot;) = array('vesijohtoTaiViemari')&#xa;AND&#xa;map_akeys(map_get(&quot;type_regulations&quot;, 'vesijohtoTaiViemari')) = array('uusi')"/>
      <rule key="{f8275de9-3676-4d13-8562-85c9f444baef}" symbol="42" label="Uusi kaasulinja" filter="map_akeys(&quot;type_regulations&quot;) = array('kaasulinja')&#xa;AND&#xa;map_akeys(map_get(&quot;type_regulations&quot;, 'kaasulinja')) = array('uusi')"/>
      <rule key="{3f0060c1-1911-4c66-b36e-bdcdff2f7e9d}" symbol="43" label="Sähkölinjan tai voimajohdon yhteystarve" filter="map_akeys(&quot;type_regulations&quot;) = array('sahkolinja')&#xa;AND&#xa;map_akeys(map_get(&quot;type_regulations&quot;, 'sahkolinja')) = array('yhteystarve')"/>
      <rule key="{21f000d1-7099-4e51-9685-39e73e6aaed6}" symbol="44" label="Vesijohdon tai viemärin yhteystarve" filter="map_akeys(&quot;type_regulations&quot;) = array('vesijohtoTaiViemari')&#xa;AND&#xa;map_akeys(map_get(&quot;type_regulations&quot;, 'vesijohtoTaiViemari')) = array('yhteystarve')"/>
      <rule key="{2bca7222-658a-472a-b5ef-7923b0e9bc53}" symbol="45" label="Kaasulinjan yhteystarve" filter="map_akeys(&quot;type_regulations&quot;) = array('kaasulinja')&#xa;AND&#xa;map_akeys(map_get(&quot;type_regulations&quot;, 'kaasulinja')) = array('yhteystarve')"/>
      <rule key="{0236b4c3-7fc6-4478-acbd-dec99c141f86}" symbol="46" label="Historiallinen tie" filter="array_sort(map_akeys(&quot;type_regulations&quot;)) = array('historiallinenKohde')&#xd;&#xa;AND array_length(map_akeys(map_get(&quot;type_regulations&quot;, 'historiallinenKohde'))) = 0&#xd;&#xa;"/>
      <rule key="{41f233b8-d959-4cce-a00e-fbe5d40910a8}" symbol="47" label="Ulkoilu- tai virkistysreitti" filter="array_sort(map_akeys(&quot;type_regulations&quot;)) = array('ulkoiluTaiVirkistysReitti')&#xd;&#xa;AND&#xd;&#xa;array_length(map_akeys(map_get(&quot;type_regulations&quot;, 'ulkoiluTaiVirkistysReitti'))) = 0"/>
      <rule key="{d5652e83-42d2-4615-a2ad-53b855bb3182}" symbol="48" label="Uusi ulkoilu- tai virkistysreitti" filter="map_akeys(&quot;type_regulations&quot;) = array('ulkoiluTaiVirkistysReitti')&#xa;AND&#xa;map_akeys(map_get(&quot;type_regulations&quot;, 'ulkoiluTaiVirkistysReitti')) = array('uusi')"/>
      <rule key="{c62c9297-0f9a-46cf-9e48-9e77385b9e7a}" symbol="49" label="Ulkoilu- tai virkistysreitin yhteystarve" filter="map_akeys(&quot;type_regulations&quot;) = array('ulkoiluTaiVirkistysReitti')&#xa;AND&#xa;map_akeys(map_get(&quot;type_regulations&quot;, 'ulkoiluTaiVirkistysReitti')) = array('yhteystarve')"/>
      <rule key="{f163734d-0d48-4b8a-8ad1-91a8d908de7a}" symbol="50" label="Valtakunnallisesti merkittävä rakennettu kulttuuriympäristö" filter="map_exist(&#xd;&#xa;  &quot;type_regulations&quot;,&#xd;&#xa;  'merkittavaRakennettuKulttuuriymparisto'&#xd;&#xa;)&#xd;&#xa;AND  array_contains(map_akeys( map_get(&#xd;&#xa;  &quot;type_regulations&quot;, 'merkittavaRakennettuKulttuuriymparisto')),&#xd;&#xa;  'osaAlue')&#xd;&#xa;AND  array_contains(map_akeys( map_get(&#xd;&#xa;  &quot;type_regulations&quot;, 'merkittavaRakennettuKulttuuriymparisto')),&#xd;&#xa;  'valtakunnallinen')"/>
      <rule key="{4d0bd845-1b4c-4785-a671-21d154a1f647}" symbol="51" label="Natura 2000 -verkostoon kuuluva alue" filter="map_exist(&#xd;&#xa;  &quot;type_regulations&quot;,&#xd;&#xa;  'natura2000VerkostonAlue'&#xd;&#xa;)&#xd;&#xa;AND map_exist(&#xd;&#xa;  &quot;type_regulations&quot;['natura2000VerkostonAlue'],&#xd;&#xa;  'osaAlue'&#xd;&#xa;)"/>
      <rule key="{2f802cb9-1fcf-41ca-a746-185b562f22d5}" symbol="52" label="Luonnon &#xa;monimuotoisuuden kannalta erityisen tärkeä alue" filter="map_exist(&#xd;&#xa;  &quot;type_regulations&quot;,&#xd;&#xa;  'luonnonMonimuotoisuudenKannaltaErityisenTarkeaAlue'&#xd;&#xa;)&#xd;&#xa;AND map_exist(&#xd;&#xa;  &quot;type_regulations&quot;['luonnonMonimuotoisuudenKannaltaErityisenTarkeaAlue'],&#xd;&#xa;  'osaAlue'&#xd;&#xa;)"/>
      <rule key="{1c73678f-9182-4917-91ac-d3be82a21409}" symbol="53" label="Yhdyskuntarakenteen laajenemissuunta" filter="map_akeys(&quot;type_regulations&quot;) = array('yhdyskuntarakenteenLaajenemissuunta')"/>
      <rule key="{46e91e2d-23d2-4412-b4a2-f7fbaeab1f4a}" symbol="54" label="Liikenteen yhteystarve" filter="map_akeys(&quot;type_regulations&quot;) = array('liikennealue')&#xa;AND&#xa;map_akeys(map_get(&quot;type_regulations&quot;, 'liikennealue')) = array('yhteystarve')"/>
      <rule key="{4f8ad91e-b296-4cfe-a919-249ce0983787}" symbol="55" label="Joki tai muu avouoma" filter="map_akeys(&quot;type_regulations&quot;) = array('vesialue')"/>
      <rule key="{1d96a987-f519-46d9-a4cd-2ba523435440}" symbol="56" label="Yhdystie tai kokoojakatu" filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'yhdystie')&#xd;&#xa;AND&#xd;&#xa;array_contains(map_akeys(&quot;type_regulations&quot;), 'kokoojakatu')&#xd;&#xa;"/>
      <rule key="{4c4474aa-7fe6-469e-9cd3-9fc94c8eb955}" symbol="57" label="Kokoojakatu" filter="map_akeys(&quot;type_regulations&quot;) = array('kokoojakatu')"/>
      <rule key="{3e9356f7-cd52-4e11-936b-0a0f1c7950ef}" symbol="58" label="Maantie tai katu" filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'maantie')&#xa;AND NOT&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'maantie')), 'kayttotarkoituskohdistus')&#xa;AND&#xa;array_contains(map_akeys(&quot;type_regulations&quot;), 'katu')&#xa;AND NOT&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'katu')), 'kayttotarkoituskohdistus')"/>
      <rule key="{1df33761-3f24-4069-ade0-5fa85549bafb}" symbol="59" label="Maantie" filter="map_akeys(&quot;type_regulations&quot;) = array('maantie')"/>
      <rule key="{6213917f-ea56-4a07-8b96-c36d1713dec7}" symbol="60" label="Katu" filter="map_akeys(&quot;type_regulations&quot;) = array('katu')"/>
      <rule key="{c1c53cd6-748d-49b7-9f34-2213c48318a0}" symbol="61" label="Joukkoliikenteelle varattu tie tai katu" filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'maantie')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'maantie')), 'kayttotarkoituskohdistus')&#xa;AND&#xa;array_contains(map_akeys(&quot;type_regulations&quot;), 'katu')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'katu')), 'kayttotarkoituskohdistus')"/>
      <rule key="{e6c94b19-fb6c-492c-900c-d7df9fc0d26f}" symbol="62" label="Joukkoliikenteelle varattu katu" filter="map_akeys(&quot;type_regulations&quot;) = array('katu')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'katu')), 'kayttotarkoituskohdistus')"/>
      <rule key="{46dbc55c-79bf-4dc7-9109-6275428b68e3}" symbol="63" label="Metro" filter="map_akeys(&quot;type_regulations&quot;) = array('metro')"/>
      <rule key="{4e2d5c9f-bf31-4f4b-bc76-6e4313e937cb}" symbol="64" label="Raitiotie" filter="map_akeys(&quot;type_regulations&quot;) = array('raitiotie')"/>
      <rule key="{c0956cfa-4a93-4eb9-9fcb-d0db86aa9853}" symbol="65" label="Jalankulku- ja pyöräilyreitti" filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'jalankulkualue')&#xa;AND NOT&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'jalankulkualue')), 'yhteystarve')&#xa;AND&#xa;array_contains(map_akeys(&quot;type_regulations&quot;), 'pyorailyalue')&#xa;AND NOT&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'pyorailyalue')), 'yhteystarve')"/>
      <rule key="{10b48d9f-c289-42cb-8bc1-1a5d6c6febad}" symbol="66" label="Pyöräilyreitti" filter="map_akeys(&quot;type_regulations&quot;) = array('pyorailyalue')&#xa;AND NOT&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'pyorailyalue')), 'yhteystarve')"/>
      <rule key="{27c8cfeb-cf00-4817-b4ea-5515954ea189}" symbol="67" label="Jalankulkureitti" filter="map_akeys(&quot;type_regulations&quot;) = array('jalankulkualue')&#xa;AND NOT&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'jalankulkualue')), 'yhteystarve')"/>
      <rule key="{34655fd4-6ca8-4ddc-b8fc-417d66d73526}" symbol="68" label="Ohjeellinen tie" filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'tie')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'tie')), 'ohjeellinenSijainti')"/>
      <rule key="{10301bef-9818-4f39-8b1d-1d4d6235d541}" symbol="69" label="Vaihtoehtoinen tie" filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'tie')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'tie')), 'vaihtoehtoinen')"/>
      <rule key="{bcb27fe5-73fb-478f-a256-d65db2a0df02}" symbol="70" filter="ELSE"/>
    </rules>
    <symbols>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="0">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{8ad0c838-9845-4e87-88d7-4222d703f5c4}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="7" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="1">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{25c4fb42-15ec-424f-997d-3fbfcd0d24da}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="2" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="-2.5" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="Point" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer locked="0" pass="0" class="SimpleLine" id="{61e84333-9081-418c-9840-8a0bedf23d3d}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="2" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="2.5" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="Point" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer locked="0" pass="0" class="SimpleLine" id="{713ea345-8053-41b3-bd94-bfab2ee2b903}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="1" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="Point" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="10">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="HashLine" id="{e8e74edc-9f4c-4872-952a-71dc3d78f6ae}" enabled="1">
          <Option type="Map">
            <Option value="4" type="QString" name="average_angle_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
            <Option value="MM" type="QString" name="average_angle_unit"/>
            <Option value="0" type="QString" name="hash_angle"/>
            <Option value="3" type="QString" name="hash_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="hash_length_map_unit_scale"/>
            <Option value="MM" type="QString" name="hash_length_unit"/>
            <Option value="5" type="QString" name="interval"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
            <Option value="Point" type="QString" name="interval_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="0" type="QString" name="offset_along_line"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_along_line_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="true" type="bool" name="place_on_every_part"/>
            <Option value="Interval|LastVertex|FirstVertex" type="QString" name="placements"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="1" type="QString" name="rotate"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@10@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleLine" id="{8ece23c8-3575-4aab-82ae-f29f412552e6}" enabled="1">
              <Option type="Map">
                <Option value="0" type="QString" name="align_dash_pattern"/>
                <Option value="square" type="QString" name="capstyle"/>
                <Option value="5;2" type="QString" name="customdash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                <Option value="Point" type="QString" name="customdash_unit"/>
                <Option value="0" type="QString" name="dash_pattern_offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
                <Option value="0" type="QString" name="draw_inside_polygon"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
                <Option value="solid" type="QString" name="line_style"/>
                <Option value="1.5" type="QString" name="line_width"/>
                <Option value="Point" type="QString" name="line_width_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="0" type="QString" name="trim_distance_end"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                <Option value="Point" type="QString" name="trim_distance_end_unit"/>
                <Option value="0" type="QString" name="trim_distance_start"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                <Option value="Point" type="QString" name="trim_distance_start_unit"/>
                <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                <Option value="0" type="QString" name="use_custom_dash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer locked="0" pass="0" class="SimpleLine" id="{583d8817-83d0-4417-a21c-bc8a0f5962c3}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="2" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="11">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="HashLine" id="{e8e74edc-9f4c-4872-952a-71dc3d78f6ae}" enabled="1">
          <Option type="Map">
            <Option value="4" type="QString" name="average_angle_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
            <Option value="MM" type="QString" name="average_angle_unit"/>
            <Option value="0" type="QString" name="hash_angle"/>
            <Option value="3" type="QString" name="hash_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="hash_length_map_unit_scale"/>
            <Option value="MM" type="QString" name="hash_length_unit"/>
            <Option value="5" type="QString" name="interval"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
            <Option value="Point" type="QString" name="interval_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="0" type="QString" name="offset_along_line"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_along_line_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="true" type="bool" name="place_on_every_part"/>
            <Option value="Interval|LastVertex|FirstVertex" type="QString" name="placements"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="1" type="QString" name="rotate"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@11@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleLine" id="{8ece23c8-3575-4aab-82ae-f29f412552e6}" enabled="1">
              <Option type="Map">
                <Option value="0" type="QString" name="align_dash_pattern"/>
                <Option value="square" type="QString" name="capstyle"/>
                <Option value="5;2" type="QString" name="customdash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                <Option value="Point" type="QString" name="customdash_unit"/>
                <Option value="0" type="QString" name="dash_pattern_offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
                <Option value="0" type="QString" name="draw_inside_polygon"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
                <Option value="solid" type="QString" name="line_style"/>
                <Option value="1.5" type="QString" name="line_width"/>
                <Option value="Point" type="QString" name="line_width_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="0" type="QString" name="trim_distance_end"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                <Option value="Point" type="QString" name="trim_distance_end_unit"/>
                <Option value="0" type="QString" name="trim_distance_start"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                <Option value="Point" type="QString" name="trim_distance_start_unit"/>
                <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                <Option value="0" type="QString" name="use_custom_dash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer locked="0" pass="0" class="SimpleLine" id="{583d8817-83d0-4417-a21c-bc8a0f5962c3}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="2" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="12">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="HashLine" id="{e8e74edc-9f4c-4872-952a-71dc3d78f6ae}" enabled="1">
          <Option type="Map">
            <Option value="4" type="QString" name="average_angle_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
            <Option value="MM" type="QString" name="average_angle_unit"/>
            <Option value="0" type="QString" name="hash_angle"/>
            <Option value="3" type="QString" name="hash_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="hash_length_map_unit_scale"/>
            <Option value="MM" type="QString" name="hash_length_unit"/>
            <Option value="5" type="QString" name="interval"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
            <Option value="Point" type="QString" name="interval_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="0" type="QString" name="offset_along_line"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_along_line_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="true" type="bool" name="place_on_every_part"/>
            <Option value="Interval|LastVertex|FirstVertex" type="QString" name="placements"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="1" type="QString" name="rotate"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@12@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleLine" id="{8ece23c8-3575-4aab-82ae-f29f412552e6}" enabled="1">
              <Option type="Map">
                <Option value="0" type="QString" name="align_dash_pattern"/>
                <Option value="square" type="QString" name="capstyle"/>
                <Option value="5;2" type="QString" name="customdash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                <Option value="Point" type="QString" name="customdash_unit"/>
                <Option value="0" type="QString" name="dash_pattern_offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
                <Option value="0" type="QString" name="draw_inside_polygon"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
                <Option value="solid" type="QString" name="line_style"/>
                <Option value="1.5" type="QString" name="line_width"/>
                <Option value="Point" type="QString" name="line_width_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="0" type="QString" name="trim_distance_end"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                <Option value="Point" type="QString" name="trim_distance_end_unit"/>
                <Option value="0" type="QString" name="trim_distance_start"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                <Option value="Point" type="QString" name="trim_distance_start_unit"/>
                <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                <Option value="0" type="QString" name="use_custom_dash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer locked="0" pass="0" class="SimpleLine" id="{583d8817-83d0-4417-a21c-bc8a0f5962c3}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="2" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="13">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="HashLine" id="{e8e74edc-9f4c-4872-952a-71dc3d78f6ae}" enabled="1">
          <Option type="Map">
            <Option value="4" type="QString" name="average_angle_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
            <Option value="MM" type="QString" name="average_angle_unit"/>
            <Option value="0" type="QString" name="hash_angle"/>
            <Option value="3" type="QString" name="hash_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="hash_length_map_unit_scale"/>
            <Option value="MM" type="QString" name="hash_length_unit"/>
            <Option value="5" type="QString" name="interval"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
            <Option value="Point" type="QString" name="interval_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="0" type="QString" name="offset_along_line"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_along_line_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="true" type="bool" name="place_on_every_part"/>
            <Option value="Interval|LastVertex|FirstVertex" type="QString" name="placements"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="1" type="QString" name="rotate"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@13@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleLine" id="{8ece23c8-3575-4aab-82ae-f29f412552e6}" enabled="1">
              <Option type="Map">
                <Option value="0" type="QString" name="align_dash_pattern"/>
                <Option value="square" type="QString" name="capstyle"/>
                <Option value="5;2" type="QString" name="customdash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                <Option value="Point" type="QString" name="customdash_unit"/>
                <Option value="0" type="QString" name="dash_pattern_offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
                <Option value="0" type="QString" name="draw_inside_polygon"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
                <Option value="solid" type="QString" name="line_style"/>
                <Option value="1.5" type="QString" name="line_width"/>
                <Option value="Point" type="QString" name="line_width_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="0" type="QString" name="trim_distance_end"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                <Option value="Point" type="QString" name="trim_distance_end_unit"/>
                <Option value="0" type="QString" name="trim_distance_start"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                <Option value="Point" type="QString" name="trim_distance_start_unit"/>
                <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                <Option value="0" type="QString" name="use_custom_dash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer locked="0" pass="0" class="SimpleLine" id="{583d8817-83d0-4417-a21c-bc8a0f5962c3}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="2" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="14">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="HashLine" id="{e8e74edc-9f4c-4872-952a-71dc3d78f6ae}" enabled="1">
          <Option type="Map">
            <Option value="4" type="QString" name="average_angle_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
            <Option value="MM" type="QString" name="average_angle_unit"/>
            <Option value="0" type="QString" name="hash_angle"/>
            <Option value="3" type="QString" name="hash_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="hash_length_map_unit_scale"/>
            <Option value="MM" type="QString" name="hash_length_unit"/>
            <Option value="5" type="QString" name="interval"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
            <Option value="Point" type="QString" name="interval_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="0" type="QString" name="offset_along_line"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_along_line_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="true" type="bool" name="place_on_every_part"/>
            <Option value="Interval|LastVertex|FirstVertex" type="QString" name="placements"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="1" type="QString" name="rotate"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@14@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleLine" id="{8ece23c8-3575-4aab-82ae-f29f412552e6}" enabled="1">
              <Option type="Map">
                <Option value="0" type="QString" name="align_dash_pattern"/>
                <Option value="square" type="QString" name="capstyle"/>
                <Option value="5;2" type="QString" name="customdash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                <Option value="Point" type="QString" name="customdash_unit"/>
                <Option value="0" type="QString" name="dash_pattern_offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
                <Option value="0" type="QString" name="draw_inside_polygon"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
                <Option value="solid" type="QString" name="line_style"/>
                <Option value="1.5" type="QString" name="line_width"/>
                <Option value="Point" type="QString" name="line_width_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="0" type="QString" name="trim_distance_end"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                <Option value="Point" type="QString" name="trim_distance_end_unit"/>
                <Option value="0" type="QString" name="trim_distance_start"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                <Option value="Point" type="QString" name="trim_distance_start_unit"/>
                <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                <Option value="0" type="QString" name="use_custom_dash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer locked="0" pass="0" class="SimpleLine" id="{583d8817-83d0-4417-a21c-bc8a0f5962c3}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="2" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="15">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="HashLine" id="{5c39f1f5-4b0b-4be7-a2b6-13b41c7167d5}" enabled="1">
          <Option type="Map">
            <Option value="4" type="QString" name="average_angle_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
            <Option value="MM" type="QString" name="average_angle_unit"/>
            <Option value="90" type="QString" name="hash_angle"/>
            <Option value="3" type="QString" name="hash_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="hash_length_map_unit_scale"/>
            <Option value="MM" type="QString" name="hash_length_unit"/>
            <Option value="15" type="QString" name="interval"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
            <Option value="Point" type="QString" name="interval_unit"/>
            <Option value="1.9" type="QString" name="offset"/>
            <Option value="0" type="QString" name="offset_along_line"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_along_line_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="true" type="bool" name="place_on_every_part"/>
            <Option value="Interval" type="QString" name="placements"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="1" type="QString" name="rotate"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@15@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleLine" id="{8d9ec6c7-5d58-40dc-bb74-01bf746b0802}" enabled="1">
              <Option type="Map">
                <Option value="0" type="QString" name="align_dash_pattern"/>
                <Option value="square" type="QString" name="capstyle"/>
                <Option value="5;2" type="QString" name="customdash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                <Option value="Point" type="QString" name="customdash_unit"/>
                <Option value="0" type="QString" name="dash_pattern_offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
                <Option value="0" type="QString" name="draw_inside_polygon"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
                <Option value="solid" type="QString" name="line_style"/>
                <Option value="2" type="QString" name="line_width"/>
                <Option value="Point" type="QString" name="line_width_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="0" type="QString" name="trim_distance_end"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                <Option value="Point" type="QString" name="trim_distance_end_unit"/>
                <Option value="0" type="QString" name="trim_distance_start"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                <Option value="Point" type="QString" name="trim_distance_start_unit"/>
                <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                <Option value="0" type="QString" name="use_custom_dash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer locked="0" pass="0" class="HashLine" id="{751c1e16-d2fe-467e-af1e-d3f52fffc4bb}" enabled="1">
          <Option type="Map">
            <Option value="4" type="QString" name="average_angle_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
            <Option value="MM" type="QString" name="average_angle_unit"/>
            <Option value="90" type="QString" name="hash_angle"/>
            <Option value="3" type="QString" name="hash_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="hash_length_map_unit_scale"/>
            <Option value="MM" type="QString" name="hash_length_unit"/>
            <Option value="15" type="QString" name="interval"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
            <Option value="Point" type="QString" name="interval_unit"/>
            <Option value="-1.9" type="QString" name="offset"/>
            <Option value="0" type="QString" name="offset_along_line"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_along_line_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="true" type="bool" name="place_on_every_part"/>
            <Option value="Interval" type="QString" name="placements"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="1" type="QString" name="rotate"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@15@1">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleLine" id="{25a29b12-86f5-45d4-808b-451b0058b8c7}" enabled="1">
              <Option type="Map">
                <Option value="0" type="QString" name="align_dash_pattern"/>
                <Option value="square" type="QString" name="capstyle"/>
                <Option value="5;2" type="QString" name="customdash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                <Option value="Point" type="QString" name="customdash_unit"/>
                <Option value="0" type="QString" name="dash_pattern_offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
                <Option value="0" type="QString" name="draw_inside_polygon"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
                <Option value="solid" type="QString" name="line_style"/>
                <Option value="2" type="QString" name="line_width"/>
                <Option value="Point" type="QString" name="line_width_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="0" type="QString" name="trim_distance_end"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                <Option value="Point" type="QString" name="trim_distance_end_unit"/>
                <Option value="0" type="QString" name="trim_distance_start"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                <Option value="Point" type="QString" name="trim_distance_start_unit"/>
                <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                <Option value="0" type="QString" name="use_custom_dash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="16">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="HashLine" id="{8f2a7c15-775f-49ec-bb29-8a6c014f884a}" enabled="1">
          <Option type="Map">
            <Option value="4" type="QString" name="average_angle_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
            <Option value="MM" type="QString" name="average_angle_unit"/>
            <Option value="90" type="QString" name="hash_angle"/>
            <Option value="5" type="QString" name="hash_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="hash_length_map_unit_scale"/>
            <Option value="Point" type="QString" name="hash_length_unit"/>
            <Option value="10" type="QString" name="interval"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
            <Option value="Point" type="QString" name="interval_unit"/>
            <Option value="-3" type="QString" name="offset"/>
            <Option value="3" type="QString" name="offset_along_line"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
            <Option value="Point" type="QString" name="offset_along_line_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="Point" type="QString" name="offset_unit"/>
            <Option value="true" type="bool" name="place_on_every_part"/>
            <Option value="Interval" type="QString" name="placements"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="1" type="QString" name="rotate"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@16@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleLine" id="{0c095a22-8dd9-4e65-9784-4bc178f6ce8e}" enabled="1">
              <Option type="Map">
                <Option value="0" type="QString" name="align_dash_pattern"/>
                <Option value="square" type="QString" name="capstyle"/>
                <Option value="5;2" type="QString" name="customdash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                <Option value="MM" type="QString" name="customdash_unit"/>
                <Option value="0" type="QString" name="dash_pattern_offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
                <Option value="0" type="QString" name="draw_inside_polygon"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
                <Option value="solid" type="QString" name="line_style"/>
                <Option value="1" type="QString" name="line_width"/>
                <Option value="Point" type="QString" name="line_width_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="MM" type="QString" name="offset_unit"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="0" type="QString" name="trim_distance_end"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                <Option value="MM" type="QString" name="trim_distance_end_unit"/>
                <Option value="0" type="QString" name="trim_distance_start"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                <Option value="MM" type="QString" name="trim_distance_start_unit"/>
                <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                <Option value="0" type="QString" name="use_custom_dash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer locked="0" pass="0" class="HashLine" id="{dd88cfd4-0cde-43d0-b51b-602719f8af27}" enabled="1">
          <Option type="Map">
            <Option value="4" type="QString" name="average_angle_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
            <Option value="MM" type="QString" name="average_angle_unit"/>
            <Option value="90" type="QString" name="hash_angle"/>
            <Option value="5" type="QString" name="hash_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="hash_length_map_unit_scale"/>
            <Option value="Point" type="QString" name="hash_length_unit"/>
            <Option value="10" type="QString" name="interval"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
            <Option value="Point" type="QString" name="interval_unit"/>
            <Option value="3" type="QString" name="offset"/>
            <Option value="3" type="QString" name="offset_along_line"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
            <Option value="Point" type="QString" name="offset_along_line_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="Point" type="QString" name="offset_unit"/>
            <Option value="true" type="bool" name="place_on_every_part"/>
            <Option value="Interval" type="QString" name="placements"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="1" type="QString" name="rotate"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@16@1">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleLine" id="{8d1da158-9c47-4089-ae61-34550acf3a95}" enabled="1">
              <Option type="Map">
                <Option value="0" type="QString" name="align_dash_pattern"/>
                <Option value="square" type="QString" name="capstyle"/>
                <Option value="5;2" type="QString" name="customdash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                <Option value="Point" type="QString" name="customdash_unit"/>
                <Option value="0" type="QString" name="dash_pattern_offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
                <Option value="0" type="QString" name="draw_inside_polygon"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
                <Option value="solid" type="QString" name="line_style"/>
                <Option value="1" type="QString" name="line_width"/>
                <Option value="Point" type="QString" name="line_width_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="0" type="QString" name="trim_distance_end"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                <Option value="Point" type="QString" name="trim_distance_end_unit"/>
                <Option value="0" type="QString" name="trim_distance_start"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                <Option value="Point" type="QString" name="trim_distance_start_unit"/>
                <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                <Option value="0" type="QString" name="use_custom_dash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer locked="0" pass="0" class="HashLine" id="{c7fcb617-7ccd-4853-9b09-e7ede2a2b5e8}" enabled="1">
          <Option type="Map">
            <Option value="4" type="QString" name="average_angle_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
            <Option value="MM" type="QString" name="average_angle_unit"/>
            <Option value="0" type="QString" name="hash_angle"/>
            <Option value="5" type="QString" name="hash_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="hash_length_map_unit_scale"/>
            <Option value="Point" type="QString" name="hash_length_unit"/>
            <Option value="10" type="QString" name="interval"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
            <Option value="Point" type="QString" name="interval_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="0" type="QString" name="offset_along_line"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_along_line_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="true" type="bool" name="place_on_every_part"/>
            <Option value="Interval" type="QString" name="placements"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="1" type="QString" name="rotate"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@16@2">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleLine" id="{ff95c9f2-daff-4264-b75f-490a7caeb416}" enabled="1">
              <Option type="Map">
                <Option value="0" type="QString" name="align_dash_pattern"/>
                <Option value="square" type="QString" name="capstyle"/>
                <Option value="5;2" type="QString" name="customdash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                <Option value="Point" type="QString" name="customdash_unit"/>
                <Option value="0" type="QString" name="dash_pattern_offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
                <Option value="0" type="QString" name="draw_inside_polygon"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
                <Option value="solid" type="QString" name="line_style"/>
                <Option value="1" type="QString" name="line_width"/>
                <Option value="Point" type="QString" name="line_width_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="0" type="QString" name="trim_distance_end"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                <Option value="Point" type="QString" name="trim_distance_end_unit"/>
                <Option value="0" type="QString" name="trim_distance_start"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                <Option value="Point" type="QString" name="trim_distance_start_unit"/>
                <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                <Option value="0" type="QString" name="use_custom_dash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="17">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="MarkerLine" id="{8f748a90-fa04-4d9f-a1b7-35450d03ace7}" enabled="1">
          <Option type="Map">
            <Option value="4" type="QString" name="average_angle_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
            <Option value="MM" type="QString" name="average_angle_unit"/>
            <Option value="13" type="QString" name="interval"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
            <Option value="Point" type="QString" name="interval_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="0" type="QString" name="offset_along_line"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_along_line_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="true" type="bool" name="place_on_every_part"/>
            <Option value="Interval" type="QString" name="placements"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="1" type="QString" name="rotate"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="marker" force_rhr="0" clip_to_extent="1" is_animated="0" name="@17@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleMarker" id="{dc1bd9e5-d02e-4e8f-bfbc-f5f542fbcc7f}" enabled="1">
              <Option type="Map">
                <Option value="0" type="QString" name="angle"/>
                <Option value="square" type="QString" name="cap_style"/>
                <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="color"/>
                <Option value="1" type="QString" name="horizontal_anchor_point"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="circle" type="QString" name="name"/>
                <Option value="0,0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="outline_color"/>
                <Option value="solid" type="QString" name="outline_style"/>
                <Option value="0" type="QString" name="outline_width"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="outline_width_map_unit_scale"/>
                <Option value="Point" type="QString" name="outline_width_unit"/>
                <Option value="diameter" type="QString" name="scale_method"/>
                <Option value="6" type="QString" name="size"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="size_map_unit_scale"/>
                <Option value="Point" type="QString" name="size_unit"/>
                <Option value="1" type="QString" name="vertical_anchor_point"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer locked="0" pass="0" class="SimpleLine" id="{2abfdf4f-4a9a-45e5-9bbe-e4aa29c087c5}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="1" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="18">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="MarkerLine" id="{8f748a90-fa04-4d9f-a1b7-35450d03ace7}" enabled="1">
          <Option type="Map">
            <Option value="4" type="QString" name="average_angle_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
            <Option value="MM" type="QString" name="average_angle_unit"/>
            <Option value="15" type="QString" name="interval"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
            <Option value="Point" type="QString" name="interval_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="0" type="QString" name="offset_along_line"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_along_line_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="true" type="bool" name="place_on_every_part"/>
            <Option value="Interval" type="QString" name="placements"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="1" type="QString" name="rotate"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="marker" force_rhr="0" clip_to_extent="1" is_animated="0" name="@18@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleMarker" id="{dc1bd9e5-d02e-4e8f-bfbc-f5f542fbcc7f}" enabled="1">
              <Option type="Map">
                <Option value="0" type="QString" name="angle"/>
                <Option value="square" type="QString" name="cap_style"/>
                <Option value="255,255,255,255,rgb:1,1,1,1" type="QString" name="color"/>
                <Option value="1" type="QString" name="horizontal_anchor_point"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="circle" type="QString" name="name"/>
                <Option value="0,0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="outline_color"/>
                <Option value="solid" type="QString" name="outline_style"/>
                <Option value="1" type="QString" name="outline_width"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="outline_width_map_unit_scale"/>
                <Option value="Point" type="QString" name="outline_width_unit"/>
                <Option value="diameter" type="QString" name="scale_method"/>
                <Option value="6" type="QString" name="size"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="size_map_unit_scale"/>
                <Option value="Point" type="QString" name="size_unit"/>
                <Option value="1" type="QString" name="vertical_anchor_point"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer locked="0" pass="0" class="HashLine" id="{0d357d8a-d521-453e-92ba-f5b974037921}" enabled="1">
          <Option type="Map">
            <Option value="4" type="QString" name="average_angle_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
            <Option value="MM" type="QString" name="average_angle_unit"/>
            <Option value="90" type="QString" name="hash_angle"/>
            <Option value="8" type="QString" name="hash_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="hash_length_map_unit_scale"/>
            <Option value="Point" type="QString" name="hash_length_unit"/>
            <Option value="15" type="QString" name="interval"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
            <Option value="Point" type="QString" name="interval_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="7" type="QString" name="offset_along_line"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
            <Option value="Point" type="QString" name="offset_along_line_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="true" type="bool" name="place_on_every_part"/>
            <Option value="Interval" type="QString" name="placements"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="1" type="QString" name="rotate"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@18@1">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleLine" id="{a75de32d-2071-4543-896a-cd329adc0907}" enabled="1">
              <Option type="Map">
                <Option value="0" type="QString" name="align_dash_pattern"/>
                <Option value="square" type="QString" name="capstyle"/>
                <Option value="5;2" type="QString" name="customdash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                <Option value="Point" type="QString" name="customdash_unit"/>
                <Option value="0" type="QString" name="dash_pattern_offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
                <Option value="0" type="QString" name="draw_inside_polygon"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
                <Option value="solid" type="QString" name="line_style"/>
                <Option value="1" type="QString" name="line_width"/>
                <Option value="Point" type="QString" name="line_width_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="0" type="QString" name="trim_distance_end"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                <Option value="Point" type="QString" name="trim_distance_end_unit"/>
                <Option value="0" type="QString" name="trim_distance_start"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                <Option value="Point" type="QString" name="trim_distance_start_unit"/>
                <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                <Option value="0" type="QString" name="use_custom_dash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="19">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="MarkerLine" id="{8f748a90-fa04-4d9f-a1b7-35450d03ace7}" enabled="1">
          <Option type="Map">
            <Option value="4" type="QString" name="average_angle_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
            <Option value="MM" type="QString" name="average_angle_unit"/>
            <Option value="13" type="QString" name="interval"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
            <Option value="Point" type="QString" name="interval_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="0" type="QString" name="offset_along_line"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_along_line_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="true" type="bool" name="place_on_every_part"/>
            <Option value="Interval" type="QString" name="placements"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="1" type="QString" name="rotate"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="marker" force_rhr="0" clip_to_extent="1" is_animated="0" name="@19@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleMarker" id="{dc1bd9e5-d02e-4e8f-bfbc-f5f542fbcc7f}" enabled="1">
              <Option type="Map">
                <Option value="0" type="QString" name="angle"/>
                <Option value="square" type="QString" name="cap_style"/>
                <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="color"/>
                <Option value="1" type="QString" name="horizontal_anchor_point"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="circle" type="QString" name="name"/>
                <Option value="0,0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="outline_color"/>
                <Option value="solid" type="QString" name="outline_style"/>
                <Option value="0" type="QString" name="outline_width"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="outline_width_map_unit_scale"/>
                <Option value="Point" type="QString" name="outline_width_unit"/>
                <Option value="diameter" type="QString" name="scale_method"/>
                <Option value="6" type="QString" name="size"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="size_map_unit_scale"/>
                <Option value="Point" type="QString" name="size_unit"/>
                <Option value="1" type="QString" name="vertical_anchor_point"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer locked="0" pass="0" class="SimpleLine" id="{2abfdf4f-4a9a-45e5-9bbe-e4aa29c087c5}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="1" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="2">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{68b416ff-0f22-4a27-95a1-c4546fc5f21f}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="3" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="3" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="Point" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer locked="0" pass="0" class="SimpleLine" id="{7f1e5810-df05-4546-aa14-23b5373f1844}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="3" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="-3" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="Point" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="20">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{8ad0c838-9845-4e87-88d7-4222d703f5c4}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="Point" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="7" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="Point" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="Point" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="Point" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="21">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{8ad0c838-9845-4e87-88d7-4222d703f5c4}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="Point" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="7" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="Point" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="Point" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="Point" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="22">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{8ad0c838-9845-4e87-88d7-4222d703f5c4}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="Point" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="7" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="Point" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="Point" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="Point" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer locked="0" pass="0" class="SimpleLine" id="{358cf78f-0827-4563-90a2-287dcc41d797}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="2.25" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="23">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{8ad0c838-9845-4e87-88d7-4222d703f5c4}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="Point" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="7" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="Point" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="Point" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="Point" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="24">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{8ad0c838-9845-4e87-88d7-4222d703f5c4}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="Point" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="7" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="Point" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="Point" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="Point" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="25">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{8ad0c838-9845-4e87-88d7-4222d703f5c4}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="Point" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="7" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="Point" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="Point" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="Point" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer locked="0" pass="0" class="SimpleLine" id="{358cf78f-0827-4563-90a2-287dcc41d797}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="2.25" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="26">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="ArrowLine" id="{91533b6d-d7a6-450e-8706-eac1f6a25d34}" enabled="1">
          <Option type="Map">
            <Option value="1" type="QString" name="arrow_start_width"/>
            <Option value="MM" type="QString" name="arrow_start_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_start_width_unit_scale"/>
            <Option value="0" type="QString" name="arrow_type"/>
            <Option value="0" type="QString" name="arrow_width"/>
            <Option value="Point" type="QString" name="arrow_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_width_unit_scale"/>
            <Option value="10" type="QString" name="head_length"/>
            <Option value="Point" type="QString" name="head_length_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_length_unit_scale"/>
            <Option value="10" type="QString" name="head_thickness"/>
            <Option value="Point" type="QString" name="head_thickness_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_thickness_unit_scale"/>
            <Option value="2" type="QString" name="head_type"/>
            <Option value="1" type="QString" name="is_curved"/>
            <Option value="1" type="QString" name="is_repeated"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="Point" type="QString" name="offset_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_unit_scale"/>
            <Option value="0" type="QString" name="ring_filter"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="fill" force_rhr="0" clip_to_extent="1" is_animated="0" name="@26@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleFill" id="{4ca734c4-5a47-4d49-a06a-7509f417212d}" enabled="1">
              <Option type="Map">
                <Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/>
                <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="color"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="0,0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="outline_color"/>
                <Option value="no" type="QString" name="outline_style"/>
                <Option value="0" type="QString" name="outline_width"/>
                <Option value="Point" type="QString" name="outline_width_unit"/>
                <Option value="solid" type="QString" name="style"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer locked="0" pass="0" class="GeometryGenerator" id="{622dfad4-c787-40f2-b02a-3acdfb1e35b4}" enabled="1">
          <Option type="Map">
            <Option value="Line" type="QString" name="SymbolType"/>
            <Option value="CASE&#xa;    WHEN length($geometry) > ( (5 + 2) * 2 ) THEN&#xa;        line_substring(&#xa;            $geometry,&#xa;            (5 + 2),&#xa;            length($geometry) - (5 + 2)&#xa;        )&#xa;    ELSE&#xa;        $geometry&#xa;END&#xa;" type="QString" name="geometryModifier"/>
            <Option value="Point" type="QString" name="units"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@26@1">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="HashLine" id="{410325a0-e6d3-4692-8772-82224a61351d}" enabled="1">
              <Option type="Map">
                <Option value="4" type="QString" name="average_angle_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
                <Option value="Point" type="QString" name="average_angle_unit"/>
                <Option value="90" type="QString" name="hash_angle"/>
                <Option value="1" type="QString" name="hash_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="hash_length_map_unit_scale"/>
                <Option value="Point" type="QString" name="hash_length_unit"/>
                <Option value="12" type="QString" name="interval"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
                <Option value="Point" type="QString" name="interval_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="0" type="QString" name="offset_along_line"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_along_line_unit"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="true" type="bool" name="place_on_every_part"/>
                <Option value="Interval" type="QString" name="placements"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="1" type="QString" name="rotate"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
              <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@@26@1@0">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleLine" id="{98bf797c-2285-4ed3-97b8-1716b341c8c4}" enabled="1">
                  <Option type="Map">
                    <Option value="0" type="QString" name="align_dash_pattern"/>
                    <Option value="square" type="QString" name="capstyle"/>
                    <Option value="5;2" type="QString" name="customdash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                    <Option value="Point" type="QString" name="customdash_unit"/>
                    <Option value="0" type="QString" name="dash_pattern_offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
                    <Option value="0" type="QString" name="draw_inside_polygon"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="line_color"/>
                    <Option value="solid" type="QString" name="line_style"/>
                    <Option value="7" type="QString" name="line_width"/>
                    <Option value="Point" type="QString" name="line_width_unit"/>
                    <Option value="0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="offset_unit"/>
                    <Option value="0" type="QString" name="ring_filter"/>
                    <Option value="0" type="QString" name="trim_distance_end"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_end_unit"/>
                    <Option value="0" type="QString" name="trim_distance_start"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_start_unit"/>
                    <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                    <Option value="0" type="QString" name="use_custom_dash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="27">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="ArrowLine" id="{91533b6d-d7a6-450e-8706-eac1f6a25d34}" enabled="1">
          <Option type="Map">
            <Option value="1" type="QString" name="arrow_start_width"/>
            <Option value="MM" type="QString" name="arrow_start_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_start_width_unit_scale"/>
            <Option value="0" type="QString" name="arrow_type"/>
            <Option value="0" type="QString" name="arrow_width"/>
            <Option value="Point" type="QString" name="arrow_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_width_unit_scale"/>
            <Option value="10" type="QString" name="head_length"/>
            <Option value="Point" type="QString" name="head_length_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_length_unit_scale"/>
            <Option value="10" type="QString" name="head_thickness"/>
            <Option value="Point" type="QString" name="head_thickness_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_thickness_unit_scale"/>
            <Option value="2" type="QString" name="head_type"/>
            <Option value="1" type="QString" name="is_curved"/>
            <Option value="1" type="QString" name="is_repeated"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="Point" type="QString" name="offset_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_unit_scale"/>
            <Option value="0" type="QString" name="ring_filter"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="fill" force_rhr="0" clip_to_extent="1" is_animated="0" name="@27@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleFill" id="{4ca734c4-5a47-4d49-a06a-7509f417212d}" enabled="1">
              <Option type="Map">
                <Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/>
                <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="color"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="0,0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="outline_color"/>
                <Option value="no" type="QString" name="outline_style"/>
                <Option value="0" type="QString" name="outline_width"/>
                <Option value="Point" type="QString" name="outline_width_unit"/>
                <Option value="solid" type="QString" name="style"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer locked="0" pass="0" class="GeometryGenerator" id="{622dfad4-c787-40f2-b02a-3acdfb1e35b4}" enabled="1">
          <Option type="Map">
            <Option value="Line" type="QString" name="SymbolType"/>
            <Option value="CASE&#xa;    WHEN length($geometry) > ( (5 + 2) * 2 ) THEN&#xa;        line_substring(&#xa;            $geometry,&#xa;            (5 + 2),&#xa;            length($geometry) - (5 + 2)&#xa;        )&#xa;    ELSE&#xa;        $geometry&#xa;END&#xa;" type="QString" name="geometryModifier"/>
            <Option value="Point" type="QString" name="units"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@27@1">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="HashLine" id="{410325a0-e6d3-4692-8772-82224a61351d}" enabled="1">
              <Option type="Map">
                <Option value="4" type="QString" name="average_angle_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
                <Option value="Point" type="QString" name="average_angle_unit"/>
                <Option value="90" type="QString" name="hash_angle"/>
                <Option value="1" type="QString" name="hash_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="hash_length_map_unit_scale"/>
                <Option value="Point" type="QString" name="hash_length_unit"/>
                <Option value="12" type="QString" name="interval"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
                <Option value="Point" type="QString" name="interval_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="0" type="QString" name="offset_along_line"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_along_line_unit"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="true" type="bool" name="place_on_every_part"/>
                <Option value="Interval" type="QString" name="placements"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="1" type="QString" name="rotate"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
              <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@@27@1@0">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleLine" id="{98bf797c-2285-4ed3-97b8-1716b341c8c4}" enabled="1">
                  <Option type="Map">
                    <Option value="0" type="QString" name="align_dash_pattern"/>
                    <Option value="square" type="QString" name="capstyle"/>
                    <Option value="5;2" type="QString" name="customdash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                    <Option value="Point" type="QString" name="customdash_unit"/>
                    <Option value="0" type="QString" name="dash_pattern_offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
                    <Option value="0" type="QString" name="draw_inside_polygon"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="line_color"/>
                    <Option value="solid" type="QString" name="line_style"/>
                    <Option value="7" type="QString" name="line_width"/>
                    <Option value="Point" type="QString" name="line_width_unit"/>
                    <Option value="0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="offset_unit"/>
                    <Option value="0" type="QString" name="ring_filter"/>
                    <Option value="0" type="QString" name="trim_distance_end"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_end_unit"/>
                    <Option value="0" type="QString" name="trim_distance_start"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_start_unit"/>
                    <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                    <Option value="0" type="QString" name="use_custom_dash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="28">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="GeometryGenerator" id="{622dfad4-c787-40f2-b02a-3acdfb1e35b4}" enabled="1">
          <Option type="Map">
            <Option value="Line" type="QString" name="SymbolType"/>
            <Option value="CASE&#xa;    WHEN length($geometry) > ( (5 + 2) * 2 ) THEN&#xa;        line_substring(&#xa;            $geometry,&#xa;            (5 + 2),&#xa;            length($geometry) - (5 + 2)&#xa;        )&#xa;    ELSE&#xa;        $geometry&#xa;END&#xa;" type="QString" name="geometryModifier"/>
            <Option value="Point" type="QString" name="units"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@28@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="HashLine" id="{410325a0-e6d3-4692-8772-82224a61351d}" enabled="1">
              <Option type="Map">
                <Option value="4" type="QString" name="average_angle_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
                <Option value="Point" type="QString" name="average_angle_unit"/>
                <Option value="90" type="QString" name="hash_angle"/>
                <Option value="3" type="QString" name="hash_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="hash_length_map_unit_scale"/>
                <Option value="Point" type="QString" name="hash_length_unit"/>
                <Option value="15" type="QString" name="interval"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
                <Option value="Point" type="QString" name="interval_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="0" type="QString" name="offset_along_line"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_along_line_unit"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="true" type="bool" name="place_on_every_part"/>
                <Option value="Interval" type="QString" name="placements"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="1" type="QString" name="rotate"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
              <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@@28@0@0">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleLine" id="{98bf797c-2285-4ed3-97b8-1716b341c8c4}" enabled="1">
                  <Option type="Map">
                    <Option value="0" type="QString" name="align_dash_pattern"/>
                    <Option value="square" type="QString" name="capstyle"/>
                    <Option value="5;2" type="QString" name="customdash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                    <Option value="Point" type="QString" name="customdash_unit"/>
                    <Option value="0" type="QString" name="dash_pattern_offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
                    <Option value="0" type="QString" name="draw_inside_polygon"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="line_color"/>
                    <Option value="solid" type="QString" name="line_style"/>
                    <Option value="7" type="QString" name="line_width"/>
                    <Option value="Point" type="QString" name="line_width_unit"/>
                    <Option value="0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="offset_unit"/>
                    <Option value="0" type="QString" name="ring_filter"/>
                    <Option value="0" type="QString" name="trim_distance_end"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_end_unit"/>
                    <Option value="0" type="QString" name="trim_distance_start"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_start_unit"/>
                    <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                    <Option value="0" type="QString" name="use_custom_dash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="29">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="GeometryGenerator" id="{622dfad4-c787-40f2-b02a-3acdfb1e35b4}" enabled="1">
          <Option type="Map">
            <Option value="Line" type="QString" name="SymbolType"/>
            <Option value="CASE&#xa;    WHEN length($geometry) > ( (5 + 2) * 2 ) THEN&#xa;        line_substring(&#xa;            $geometry,&#xa;            (5 + 2),&#xa;            length($geometry) - (5 + 2)&#xa;        )&#xa;    ELSE&#xa;        $geometry&#xa;END&#xa;" type="QString" name="geometryModifier"/>
            <Option value="Point" type="QString" name="units"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@29@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="HashLine" id="{410325a0-e6d3-4692-8772-82224a61351d}" enabled="1">
              <Option type="Map">
                <Option value="4" type="QString" name="average_angle_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
                <Option value="Point" type="QString" name="average_angle_unit"/>
                <Option value="90" type="QString" name="hash_angle"/>
                <Option value="0.5" type="QString" name="hash_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="hash_length_map_unit_scale"/>
                <Option value="Point" type="QString" name="hash_length_unit"/>
                <Option value="12" type="QString" name="interval"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
                <Option value="Point" type="QString" name="interval_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="0" type="QString" name="offset_along_line"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_along_line_unit"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="true" type="bool" name="place_on_every_part"/>
                <Option value="Interval" type="QString" name="placements"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="1" type="QString" name="rotate"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
              <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@@29@0@0">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleLine" id="{98bf797c-2285-4ed3-97b8-1716b341c8c4}" enabled="1">
                  <Option type="Map">
                    <Option value="0" type="QString" name="align_dash_pattern"/>
                    <Option value="square" type="QString" name="capstyle"/>
                    <Option value="5;2" type="QString" name="customdash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                    <Option value="Point" type="QString" name="customdash_unit"/>
                    <Option value="0" type="QString" name="dash_pattern_offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
                    <Option value="0" type="QString" name="draw_inside_polygon"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="line_color"/>
                    <Option value="solid" type="QString" name="line_style"/>
                    <Option value="7" type="QString" name="line_width"/>
                    <Option value="Point" type="QString" name="line_width_unit"/>
                    <Option value="0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="offset_unit"/>
                    <Option value="0" type="QString" name="ring_filter"/>
                    <Option value="0" type="QString" name="trim_distance_end"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_end_unit"/>
                    <Option value="0" type="QString" name="trim_distance_start"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_start_unit"/>
                    <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                    <Option value="0" type="QString" name="use_custom_dash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="3">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{c1fbaa3b-6edf-46d1-be03-12db49ccc062}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="7" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="30">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{583d8817-83d0-4417-a21c-bc8a0f5962c3}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="1" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="2" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="Point" type="QString" name="trim_distance_end_unit"/>
            <Option value="2" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="Point" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer locked="0" pass="0" class="ArrowLine" id="{61921724-1c3f-41d4-b76c-2b6311851808}" enabled="1">
          <Option type="Map">
            <Option value="1" type="QString" name="arrow_start_width"/>
            <Option value="MM" type="QString" name="arrow_start_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_start_width_unit_scale"/>
            <Option value="0" type="QString" name="arrow_type"/>
            <Option value="1" type="QString" name="arrow_width"/>
            <Option value="Point" type="QString" name="arrow_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_width_unit_scale"/>
            <Option value="10" type="QString" name="head_length"/>
            <Option value="Point" type="QString" name="head_length_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_length_unit_scale"/>
            <Option value="10" type="QString" name="head_thickness"/>
            <Option value="Point" type="QString" name="head_thickness_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_thickness_unit_scale"/>
            <Option value="0" type="QString" name="head_type"/>
            <Option value="1" type="QString" name="is_curved"/>
            <Option value="1" type="QString" name="is_repeated"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_unit_scale"/>
            <Option value="0" type="QString" name="ring_filter"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="fill" force_rhr="0" clip_to_extent="1" is_animated="0" name="@30@1">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleFill" id="{453c2540-89fc-4a30-af74-a6ecefb378f9}" enabled="1">
              <Option type="Map">
                <Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/>
                <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="color"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="4,0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="outline_color"/>
                <Option value="no" type="QString" name="outline_style"/>
                <Option value="0" type="QString" name="outline_width"/>
                <Option value="Point" type="QString" name="outline_width_unit"/>
                <Option value="solid" type="QString" name="style"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer locked="0" pass="0" class="ArrowLine" id="{865926a8-eeb9-4820-b7fa-c4458ac10990}" enabled="1">
          <Option type="Map">
            <Option value="1" type="QString" name="arrow_start_width"/>
            <Option value="MM" type="QString" name="arrow_start_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_start_width_unit_scale"/>
            <Option value="0" type="QString" name="arrow_type"/>
            <Option value="1" type="QString" name="arrow_width"/>
            <Option value="Point" type="QString" name="arrow_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_width_unit_scale"/>
            <Option value="10" type="QString" name="head_length"/>
            <Option value="Point" type="QString" name="head_length_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_length_unit_scale"/>
            <Option value="10" type="QString" name="head_thickness"/>
            <Option value="Point" type="QString" name="head_thickness_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_thickness_unit_scale"/>
            <Option value="1" type="QString" name="head_type"/>
            <Option value="1" type="QString" name="is_curved"/>
            <Option value="1" type="QString" name="is_repeated"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="Point" type="QString" name="offset_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_unit_scale"/>
            <Option value="0" type="QString" name="ring_filter"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="fill" force_rhr="0" clip_to_extent="1" is_animated="0" name="@30@2">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleFill" id="{645e90a1-f468-411c-a6d7-c428aab2afa8}" enabled="1">
              <Option type="Map">
                <Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/>
                <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="color"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="-4,0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="outline_color"/>
                <Option value="no" type="QString" name="outline_style"/>
                <Option value="0.26" type="QString" name="outline_width"/>
                <Option value="MM" type="QString" name="outline_width_unit"/>
                <Option value="solid" type="QString" name="style"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer locked="0" pass="0" class="GeometryGenerator" id="{be35e3da-0861-4706-908f-d2ac57c7331b}" enabled="1">
          <Option type="Map">
            <Option value="Line" type="QString" name="SymbolType"/>
            <Option value="@geometry" type="QString" name="geometryModifier"/>
            <Option value="MapUnit" type="QString" name="units"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@30@3">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="HashLine" id="{df7b1142-8c98-4ffe-9245-df391b5cc6ac}" enabled="1">
              <Option type="Map">
                <Option value="4" type="QString" name="average_angle_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
                <Option value="MM" type="QString" name="average_angle_unit"/>
                <Option value="0" type="QString" name="hash_angle"/>
                <Option value="3" type="QString" name="hash_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="hash_length_map_unit_scale"/>
                <Option value="MM" type="QString" name="hash_length_unit"/>
                <Option value="4" type="QString" name="interval"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
                <Option value="Point" type="QString" name="interval_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="0" type="QString" name="offset_along_line"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
                <Option value="MM" type="QString" name="offset_along_line_unit"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="MM" type="QString" name="offset_unit"/>
                <Option value="true" type="bool" name="place_on_every_part"/>
                <Option value="Interval|LastVertex|FirstVertex" type="QString" name="placements"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="1" type="QString" name="rotate"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
              <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@@30@3@0">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleLine" id="{8ece23c8-3575-4aab-82ae-f29f412552e6}" enabled="1">
                  <Option type="Map">
                    <Option value="0" type="QString" name="align_dash_pattern"/>
                    <Option value="square" type="QString" name="capstyle"/>
                    <Option value="5;2" type="QString" name="customdash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                    <Option value="Point" type="QString" name="customdash_unit"/>
                    <Option value="0" type="QString" name="dash_pattern_offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
                    <Option value="0" type="QString" name="draw_inside_polygon"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="line_color"/>
                    <Option value="solid" type="QString" name="line_style"/>
                    <Option value="1" type="QString" name="line_width"/>
                    <Option value="Point" type="QString" name="line_width_unit"/>
                    <Option value="0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="offset_unit"/>
                    <Option value="0" type="QString" name="ring_filter"/>
                    <Option value="0" type="QString" name="trim_distance_end"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_end_unit"/>
                    <Option value="0" type="QString" name="trim_distance_start"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_start_unit"/>
                    <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                    <Option value="0" type="QString" name="use_custom_dash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="31">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="ArrowLine" id="{91533b6d-d7a6-450e-8706-eac1f6a25d34}" enabled="1">
          <Option type="Map">
            <Option value="1" type="QString" name="arrow_start_width"/>
            <Option value="MM" type="QString" name="arrow_start_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_start_width_unit_scale"/>
            <Option value="0" type="QString" name="arrow_type"/>
            <Option value="0" type="QString" name="arrow_width"/>
            <Option value="Point" type="QString" name="arrow_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_width_unit_scale"/>
            <Option value="10" type="QString" name="head_length"/>
            <Option value="Point" type="QString" name="head_length_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_length_unit_scale"/>
            <Option value="10" type="QString" name="head_thickness"/>
            <Option value="Point" type="QString" name="head_thickness_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_thickness_unit_scale"/>
            <Option value="2" type="QString" name="head_type"/>
            <Option value="1" type="QString" name="is_curved"/>
            <Option value="1" type="QString" name="is_repeated"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="Point" type="QString" name="offset_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_unit_scale"/>
            <Option value="0" type="QString" name="ring_filter"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="fill" force_rhr="0" clip_to_extent="1" is_animated="0" name="@31@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleFill" id="{4ca734c4-5a47-4d49-a06a-7509f417212d}" enabled="1">
              <Option type="Map">
                <Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/>
                <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="color"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="0,0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="outline_color"/>
                <Option value="no" type="QString" name="outline_style"/>
                <Option value="0" type="QString" name="outline_width"/>
                <Option value="Point" type="QString" name="outline_width_unit"/>
                <Option value="solid" type="QString" name="style"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer locked="0" pass="0" class="GeometryGenerator" id="{622dfad4-c787-40f2-b02a-3acdfb1e35b4}" enabled="1">
          <Option type="Map">
            <Option value="Line" type="QString" name="SymbolType"/>
            <Option value="CASE&#xa;    WHEN length($geometry) > ( (5 + 2) * 2 ) THEN&#xa;        line_substring(&#xa;            $geometry,&#xa;            (5 + 2),&#xa;            length($geometry) - (5 + 2)&#xa;        )&#xa;    ELSE&#xa;        $geometry&#xa;END&#xa;" type="QString" name="geometryModifier"/>
            <Option value="Point" type="QString" name="units"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@31@1">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="HashLine" id="{410325a0-e6d3-4692-8772-82224a61351d}" enabled="1">
              <Option type="Map">
                <Option value="4" type="QString" name="average_angle_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
                <Option value="Point" type="QString" name="average_angle_unit"/>
                <Option value="90" type="QString" name="hash_angle"/>
                <Option value="1" type="QString" name="hash_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="hash_length_map_unit_scale"/>
                <Option value="Point" type="QString" name="hash_length_unit"/>
                <Option value="12" type="QString" name="interval"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
                <Option value="Point" type="QString" name="interval_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="0" type="QString" name="offset_along_line"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_along_line_unit"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="true" type="bool" name="place_on_every_part"/>
                <Option value="Interval" type="QString" name="placements"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="1" type="QString" name="rotate"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
              <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@@31@1@0">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleLine" id="{98bf797c-2285-4ed3-97b8-1716b341c8c4}" enabled="1">
                  <Option type="Map">
                    <Option value="0" type="QString" name="align_dash_pattern"/>
                    <Option value="square" type="QString" name="capstyle"/>
                    <Option value="5;2" type="QString" name="customdash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                    <Option value="Point" type="QString" name="customdash_unit"/>
                    <Option value="0" type="QString" name="dash_pattern_offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
                    <Option value="0" type="QString" name="draw_inside_polygon"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="line_color"/>
                    <Option value="solid" type="QString" name="line_style"/>
                    <Option value="7" type="QString" name="line_width"/>
                    <Option value="Point" type="QString" name="line_width_unit"/>
                    <Option value="0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="offset_unit"/>
                    <Option value="0" type="QString" name="ring_filter"/>
                    <Option value="0" type="QString" name="trim_distance_end"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_end_unit"/>
                    <Option value="0" type="QString" name="trim_distance_start"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_start_unit"/>
                    <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                    <Option value="0" type="QString" name="use_custom_dash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="32">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="ArrowLine" id="{91533b6d-d7a6-450e-8706-eac1f6a25d34}" enabled="1">
          <Option type="Map">
            <Option value="1" type="QString" name="arrow_start_width"/>
            <Option value="MM" type="QString" name="arrow_start_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_start_width_unit_scale"/>
            <Option value="0" type="QString" name="arrow_type"/>
            <Option value="0" type="QString" name="arrow_width"/>
            <Option value="Point" type="QString" name="arrow_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_width_unit_scale"/>
            <Option value="10" type="QString" name="head_length"/>
            <Option value="Point" type="QString" name="head_length_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_length_unit_scale"/>
            <Option value="10" type="QString" name="head_thickness"/>
            <Option value="Point" type="QString" name="head_thickness_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_thickness_unit_scale"/>
            <Option value="2" type="QString" name="head_type"/>
            <Option value="1" type="QString" name="is_curved"/>
            <Option value="1" type="QString" name="is_repeated"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="Point" type="QString" name="offset_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_unit_scale"/>
            <Option value="0" type="QString" name="ring_filter"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="fill" force_rhr="0" clip_to_extent="1" is_animated="0" name="@32@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleFill" id="{4ca734c4-5a47-4d49-a06a-7509f417212d}" enabled="1">
              <Option type="Map">
                <Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/>
                <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="color"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="0,0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="outline_color"/>
                <Option value="no" type="QString" name="outline_style"/>
                <Option value="0" type="QString" name="outline_width"/>
                <Option value="Point" type="QString" name="outline_width_unit"/>
                <Option value="solid" type="QString" name="style"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer locked="0" pass="0" class="GeometryGenerator" id="{622dfad4-c787-40f2-b02a-3acdfb1e35b4}" enabled="1">
          <Option type="Map">
            <Option value="Line" type="QString" name="SymbolType"/>
            <Option value="CASE&#xa;    WHEN length($geometry) > ( (5 + 2) * 2 ) THEN&#xa;        line_substring(&#xa;            $geometry,&#xa;            (5 + 2),&#xa;            length($geometry) - (5 + 2)&#xa;        )&#xa;    ELSE&#xa;        $geometry&#xa;END&#xa;" type="QString" name="geometryModifier"/>
            <Option value="Point" type="QString" name="units"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@32@1">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="HashLine" id="{410325a0-e6d3-4692-8772-82224a61351d}" enabled="1">
              <Option type="Map">
                <Option value="4" type="QString" name="average_angle_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
                <Option value="Point" type="QString" name="average_angle_unit"/>
                <Option value="90" type="QString" name="hash_angle"/>
                <Option value="1" type="QString" name="hash_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="hash_length_map_unit_scale"/>
                <Option value="Point" type="QString" name="hash_length_unit"/>
                <Option value="12" type="QString" name="interval"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
                <Option value="Point" type="QString" name="interval_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="0" type="QString" name="offset_along_line"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_along_line_unit"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="true" type="bool" name="place_on_every_part"/>
                <Option value="Interval" type="QString" name="placements"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="1" type="QString" name="rotate"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
              <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@@32@1@0">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleLine" id="{98bf797c-2285-4ed3-97b8-1716b341c8c4}" enabled="1">
                  <Option type="Map">
                    <Option value="0" type="QString" name="align_dash_pattern"/>
                    <Option value="square" type="QString" name="capstyle"/>
                    <Option value="5;2" type="QString" name="customdash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                    <Option value="Point" type="QString" name="customdash_unit"/>
                    <Option value="0" type="QString" name="dash_pattern_offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
                    <Option value="0" type="QString" name="draw_inside_polygon"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="line_color"/>
                    <Option value="solid" type="QString" name="line_style"/>
                    <Option value="7" type="QString" name="line_width"/>
                    <Option value="Point" type="QString" name="line_width_unit"/>
                    <Option value="0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="offset_unit"/>
                    <Option value="0" type="QString" name="ring_filter"/>
                    <Option value="0" type="QString" name="trim_distance_end"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_end_unit"/>
                    <Option value="0" type="QString" name="trim_distance_start"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_start_unit"/>
                    <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                    <Option value="0" type="QString" name="use_custom_dash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="33">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="ArrowLine" id="{91533b6d-d7a6-450e-8706-eac1f6a25d34}" enabled="1">
          <Option type="Map">
            <Option value="1" type="QString" name="arrow_start_width"/>
            <Option value="MM" type="QString" name="arrow_start_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_start_width_unit_scale"/>
            <Option value="0" type="QString" name="arrow_type"/>
            <Option value="0" type="QString" name="arrow_width"/>
            <Option value="Point" type="QString" name="arrow_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_width_unit_scale"/>
            <Option value="10" type="QString" name="head_length"/>
            <Option value="Point" type="QString" name="head_length_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_length_unit_scale"/>
            <Option value="10" type="QString" name="head_thickness"/>
            <Option value="Point" type="QString" name="head_thickness_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_thickness_unit_scale"/>
            <Option value="2" type="QString" name="head_type"/>
            <Option value="1" type="QString" name="is_curved"/>
            <Option value="1" type="QString" name="is_repeated"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="Point" type="QString" name="offset_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_unit_scale"/>
            <Option value="0" type="QString" name="ring_filter"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="fill" force_rhr="0" clip_to_extent="1" is_animated="0" name="@33@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleFill" id="{4ca734c4-5a47-4d49-a06a-7509f417212d}" enabled="1">
              <Option type="Map">
                <Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/>
                <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="color"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="0,0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="outline_color"/>
                <Option value="no" type="QString" name="outline_style"/>
                <Option value="0" type="QString" name="outline_width"/>
                <Option value="Point" type="QString" name="outline_width_unit"/>
                <Option value="solid" type="QString" name="style"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer locked="0" pass="0" class="GeometryGenerator" id="{622dfad4-c787-40f2-b02a-3acdfb1e35b4}" enabled="1">
          <Option type="Map">
            <Option value="Line" type="QString" name="SymbolType"/>
            <Option value="CASE&#xa;    WHEN length($geometry) > ( (5 + 2) * 2 ) THEN&#xa;        line_substring(&#xa;            $geometry,&#xa;            (5 + 2),&#xa;            length($geometry) - (5 + 2)&#xa;        )&#xa;    ELSE&#xa;        $geometry&#xa;END&#xa;" type="QString" name="geometryModifier"/>
            <Option value="Point" type="QString" name="units"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@33@1">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="HashLine" id="{410325a0-e6d3-4692-8772-82224a61351d}" enabled="1">
              <Option type="Map">
                <Option value="4" type="QString" name="average_angle_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
                <Option value="Point" type="QString" name="average_angle_unit"/>
                <Option value="90" type="QString" name="hash_angle"/>
                <Option value="1" type="QString" name="hash_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="hash_length_map_unit_scale"/>
                <Option value="Point" type="QString" name="hash_length_unit"/>
                <Option value="12" type="QString" name="interval"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
                <Option value="Point" type="QString" name="interval_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="0" type="QString" name="offset_along_line"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_along_line_unit"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="true" type="bool" name="place_on_every_part"/>
                <Option value="Interval" type="QString" name="placements"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="1" type="QString" name="rotate"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
              <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@@33@1@0">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleLine" id="{98bf797c-2285-4ed3-97b8-1716b341c8c4}" enabled="1">
                  <Option type="Map">
                    <Option value="0" type="QString" name="align_dash_pattern"/>
                    <Option value="square" type="QString" name="capstyle"/>
                    <Option value="5;2" type="QString" name="customdash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                    <Option value="Point" type="QString" name="customdash_unit"/>
                    <Option value="0" type="QString" name="dash_pattern_offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
                    <Option value="0" type="QString" name="draw_inside_polygon"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="line_color"/>
                    <Option value="solid" type="QString" name="line_style"/>
                    <Option value="7" type="QString" name="line_width"/>
                    <Option value="Point" type="QString" name="line_width_unit"/>
                    <Option value="0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="offset_unit"/>
                    <Option value="0" type="QString" name="ring_filter"/>
                    <Option value="0" type="QString" name="trim_distance_end"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_end_unit"/>
                    <Option value="0" type="QString" name="trim_distance_start"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_start_unit"/>
                    <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                    <Option value="0" type="QString" name="use_custom_dash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="34">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="ArrowLine" id="{91533b6d-d7a6-450e-8706-eac1f6a25d34}" enabled="1">
          <Option type="Map">
            <Option value="1" type="QString" name="arrow_start_width"/>
            <Option value="MM" type="QString" name="arrow_start_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_start_width_unit_scale"/>
            <Option value="0" type="QString" name="arrow_type"/>
            <Option value="0" type="QString" name="arrow_width"/>
            <Option value="Point" type="QString" name="arrow_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_width_unit_scale"/>
            <Option value="10" type="QString" name="head_length"/>
            <Option value="Point" type="QString" name="head_length_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_length_unit_scale"/>
            <Option value="10" type="QString" name="head_thickness"/>
            <Option value="Point" type="QString" name="head_thickness_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_thickness_unit_scale"/>
            <Option value="2" type="QString" name="head_type"/>
            <Option value="1" type="QString" name="is_curved"/>
            <Option value="1" type="QString" name="is_repeated"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="Point" type="QString" name="offset_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_unit_scale"/>
            <Option value="0" type="QString" name="ring_filter"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="fill" force_rhr="0" clip_to_extent="1" is_animated="0" name="@34@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleFill" id="{4ca734c4-5a47-4d49-a06a-7509f417212d}" enabled="1">
              <Option type="Map">
                <Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/>
                <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="color"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="0,0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="outline_color"/>
                <Option value="no" type="QString" name="outline_style"/>
                <Option value="0" type="QString" name="outline_width"/>
                <Option value="Point" type="QString" name="outline_width_unit"/>
                <Option value="solid" type="QString" name="style"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer locked="0" pass="0" class="GeometryGenerator" id="{622dfad4-c787-40f2-b02a-3acdfb1e35b4}" enabled="1">
          <Option type="Map">
            <Option value="Line" type="QString" name="SymbolType"/>
            <Option value="CASE&#xa;    WHEN length($geometry) > ( (5 + 2) * 2 ) THEN&#xa;        line_substring(&#xa;            $geometry,&#xa;            (5 + 2),&#xa;            length($geometry) - (5 + 2)&#xa;        )&#xa;    ELSE&#xa;        $geometry&#xa;END&#xa;" type="QString" name="geometryModifier"/>
            <Option value="Point" type="QString" name="units"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@34@1">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="HashLine" id="{410325a0-e6d3-4692-8772-82224a61351d}" enabled="1">
              <Option type="Map">
                <Option value="4" type="QString" name="average_angle_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
                <Option value="Point" type="QString" name="average_angle_unit"/>
                <Option value="90" type="QString" name="hash_angle"/>
                <Option value="1" type="QString" name="hash_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="hash_length_map_unit_scale"/>
                <Option value="Point" type="QString" name="hash_length_unit"/>
                <Option value="12" type="QString" name="interval"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
                <Option value="Point" type="QString" name="interval_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="0" type="QString" name="offset_along_line"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_along_line_unit"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="true" type="bool" name="place_on_every_part"/>
                <Option value="Interval" type="QString" name="placements"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="1" type="QString" name="rotate"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
              <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@@34@1@0">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleLine" id="{98bf797c-2285-4ed3-97b8-1716b341c8c4}" enabled="1">
                  <Option type="Map">
                    <Option value="0" type="QString" name="align_dash_pattern"/>
                    <Option value="square" type="QString" name="capstyle"/>
                    <Option value="5;2" type="QString" name="customdash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                    <Option value="Point" type="QString" name="customdash_unit"/>
                    <Option value="0" type="QString" name="dash_pattern_offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
                    <Option value="0" type="QString" name="draw_inside_polygon"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="line_color"/>
                    <Option value="solid" type="QString" name="line_style"/>
                    <Option value="7" type="QString" name="line_width"/>
                    <Option value="Point" type="QString" name="line_width_unit"/>
                    <Option value="0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="offset_unit"/>
                    <Option value="0" type="QString" name="ring_filter"/>
                    <Option value="0" type="QString" name="trim_distance_end"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_end_unit"/>
                    <Option value="0" type="QString" name="trim_distance_start"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_start_unit"/>
                    <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                    <Option value="0" type="QString" name="use_custom_dash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="35">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="ArrowLine" id="{93c298c0-123a-4d08-9582-9e409d858110}" enabled="1">
          <Option type="Map">
            <Option value="1" type="QString" name="arrow_start_width"/>
            <Option value="MM" type="QString" name="arrow_start_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_start_width_unit_scale"/>
            <Option value="0" type="QString" name="arrow_type"/>
            <Option value="7" type="QString" name="arrow_width"/>
            <Option value="Point" type="QString" name="arrow_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_width_unit_scale"/>
            <Option value="10" type="QString" name="head_length"/>
            <Option value="Point" type="QString" name="head_length_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_length_unit_scale"/>
            <Option value="10" type="QString" name="head_thickness"/>
            <Option value="Point" type="QString" name="head_thickness_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_thickness_unit_scale"/>
            <Option value="2" type="QString" name="head_type"/>
            <Option value="1" type="QString" name="is_curved"/>
            <Option value="1" type="QString" name="is_repeated"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_unit_scale"/>
            <Option value="0" type="QString" name="ring_filter"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="fill" force_rhr="0" clip_to_extent="1" is_animated="0" name="@35@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleFill" id="{1c9e73ae-d42d-4bae-a385-2d99a32d32f9}" enabled="1">
              <Option type="Map">
                <Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/>
                <Option value="25,104,64,255,rgb:0.09803921568627451,0.40784313725490196,0.25098039215686274,1" type="QString" name="color"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="0,0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="MM" type="QString" name="offset_unit"/>
                <Option value="213,180,60,255,rgb:0.83529411764705885,0.70588235294117652,0.23529411764705882,1" type="QString" name="outline_color"/>
                <Option value="no" type="QString" name="outline_style"/>
                <Option value="0" type="QString" name="outline_width"/>
                <Option value="MM" type="QString" name="outline_width_unit"/>
                <Option value="solid" type="QString" name="style"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="36">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="ArrowLine" id="{91533b6d-d7a6-450e-8706-eac1f6a25d34}" enabled="1">
          <Option type="Map">
            <Option value="1" type="QString" name="arrow_start_width"/>
            <Option value="MM" type="QString" name="arrow_start_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_start_width_unit_scale"/>
            <Option value="0" type="QString" name="arrow_type"/>
            <Option value="0" type="QString" name="arrow_width"/>
            <Option value="Point" type="QString" name="arrow_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_width_unit_scale"/>
            <Option value="10" type="QString" name="head_length"/>
            <Option value="Point" type="QString" name="head_length_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_length_unit_scale"/>
            <Option value="10" type="QString" name="head_thickness"/>
            <Option value="Point" type="QString" name="head_thickness_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_thickness_unit_scale"/>
            <Option value="2" type="QString" name="head_type"/>
            <Option value="1" type="QString" name="is_curved"/>
            <Option value="1" type="QString" name="is_repeated"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="Point" type="QString" name="offset_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_unit_scale"/>
            <Option value="0" type="QString" name="ring_filter"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="fill" force_rhr="0" clip_to_extent="1" is_animated="0" name="@36@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleFill" id="{4ca734c4-5a47-4d49-a06a-7509f417212d}" enabled="1">
              <Option type="Map">
                <Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/>
                <Option value="25,104,64,255,rgb:0.09803921568627451,0.40784313725490196,0.25098039215686274,1" type="QString" name="color"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="0,0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="outline_color"/>
                <Option value="no" type="QString" name="outline_style"/>
                <Option value="0" type="QString" name="outline_width"/>
                <Option value="Point" type="QString" name="outline_width_unit"/>
                <Option value="solid" type="QString" name="style"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer locked="0" pass="0" class="GeometryGenerator" id="{622dfad4-c787-40f2-b02a-3acdfb1e35b4}" enabled="1">
          <Option type="Map">
            <Option value="Line" type="QString" name="SymbolType"/>
            <Option value="CASE&#xa;    WHEN length($geometry) > ( (5 + 2) * 2 ) THEN&#xa;        line_substring(&#xa;            $geometry,&#xa;            (5 + 2),&#xa;            length($geometry) - (5 + 2)&#xa;        )&#xa;    ELSE&#xa;        $geometry&#xa;END&#xa;" type="QString" name="geometryModifier"/>
            <Option value="Point" type="QString" name="units"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@36@1">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="HashLine" id="{410325a0-e6d3-4692-8772-82224a61351d}" enabled="1">
              <Option type="Map">
                <Option value="4" type="QString" name="average_angle_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
                <Option value="Point" type="QString" name="average_angle_unit"/>
                <Option value="90" type="QString" name="hash_angle"/>
                <Option value="1" type="QString" name="hash_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="hash_length_map_unit_scale"/>
                <Option value="Point" type="QString" name="hash_length_unit"/>
                <Option value="12" type="QString" name="interval"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
                <Option value="Point" type="QString" name="interval_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="0" type="QString" name="offset_along_line"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_along_line_unit"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="true" type="bool" name="place_on_every_part"/>
                <Option value="Interval" type="QString" name="placements"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="1" type="QString" name="rotate"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
              <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@@36@1@0">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleLine" id="{98bf797c-2285-4ed3-97b8-1716b341c8c4}" enabled="1">
                  <Option type="Map">
                    <Option value="0" type="QString" name="align_dash_pattern"/>
                    <Option value="square" type="QString" name="capstyle"/>
                    <Option value="5;2" type="QString" name="customdash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                    <Option value="Point" type="QString" name="customdash_unit"/>
                    <Option value="0" type="QString" name="dash_pattern_offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
                    <Option value="0" type="QString" name="draw_inside_polygon"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="25,104,64,255,rgb:0.09803921568627451,0.40784313725490196,0.25098039215686274,1" type="QString" name="line_color"/>
                    <Option value="solid" type="QString" name="line_style"/>
                    <Option value="7" type="QString" name="line_width"/>
                    <Option value="Point" type="QString" name="line_width_unit"/>
                    <Option value="0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="offset_unit"/>
                    <Option value="0" type="QString" name="ring_filter"/>
                    <Option value="0" type="QString" name="trim_distance_end"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_end_unit"/>
                    <Option value="0" type="QString" name="trim_distance_start"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_start_unit"/>
                    <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                    <Option value="0" type="QString" name="use_custom_dash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="37">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{a1f5798e-b1ac-4301-a01c-4d2d9586ad2f}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="1" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="38">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{a1f5798e-b1ac-4301-a01c-4d2d9586ad2f}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="1" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="39">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{a1f5798e-b1ac-4301-a01c-4d2d9586ad2f}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="1" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="4">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{c1fbaa3b-6edf-46d1-be03-12db49ccc062}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="7" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="40">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{a1f5798e-b1ac-4301-a01c-4d2d9586ad2f}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="229,31,45,255,rgb:0.89803921568627454,0.12156862745098039,0.17647058823529413,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="1" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="41">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{a1f5798e-b1ac-4301-a01c-4d2d9586ad2f}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="229,31,45,255,rgb:0.89803921568627454,0.12156862745098039,0.17647058823529413,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="1" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="42">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{a1f5798e-b1ac-4301-a01c-4d2d9586ad2f}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="229,31,45,255,rgb:0.89803921568627454,0.12156862745098039,0.17647058823529413,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="1" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="43">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="ArrowLine" id="{91533b6d-d7a6-450e-8706-eac1f6a25d34}" enabled="1">
          <Option type="Map">
            <Option value="1" type="QString" name="arrow_start_width"/>
            <Option value="MM" type="QString" name="arrow_start_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_start_width_unit_scale"/>
            <Option value="0" type="QString" name="arrow_type"/>
            <Option value="0" type="QString" name="arrow_width"/>
            <Option value="Point" type="QString" name="arrow_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_width_unit_scale"/>
            <Option value="10" type="QString" name="head_length"/>
            <Option value="Point" type="QString" name="head_length_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_length_unit_scale"/>
            <Option value="4" type="QString" name="head_thickness"/>
            <Option value="Point" type="QString" name="head_thickness_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_thickness_unit_scale"/>
            <Option value="2" type="QString" name="head_type"/>
            <Option value="1" type="QString" name="is_curved"/>
            <Option value="1" type="QString" name="is_repeated"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="Point" type="QString" name="offset_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_unit_scale"/>
            <Option value="0" type="QString" name="ring_filter"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="fill" force_rhr="0" clip_to_extent="1" is_animated="0" name="@43@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleFill" id="{4ca734c4-5a47-4d49-a06a-7509f417212d}" enabled="1">
              <Option type="Map">
                <Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/>
                <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="color"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="0,0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="outline_color"/>
                <Option value="no" type="QString" name="outline_style"/>
                <Option value="0" type="QString" name="outline_width"/>
                <Option value="Point" type="QString" name="outline_width_unit"/>
                <Option value="solid" type="QString" name="style"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer locked="0" pass="0" class="GeometryGenerator" id="{622dfad4-c787-40f2-b02a-3acdfb1e35b4}" enabled="1">
          <Option type="Map">
            <Option value="Line" type="QString" name="SymbolType"/>
            <Option value="CASE&#xa;    WHEN length($geometry) > ( (5 + 2) * 2 ) THEN&#xa;        line_substring(&#xa;            $geometry,&#xa;            (5 + 2),&#xa;            length($geometry) - (5 + 2)&#xa;        )&#xa;    ELSE&#xa;        $geometry&#xa;END&#xa;" type="QString" name="geometryModifier"/>
            <Option value="Point" type="QString" name="units"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@43@1">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="HashLine" id="{410325a0-e6d3-4692-8772-82224a61351d}" enabled="1">
              <Option type="Map">
                <Option value="4" type="QString" name="average_angle_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
                <Option value="Point" type="QString" name="average_angle_unit"/>
                <Option value="90" type="QString" name="hash_angle"/>
                <Option value="1" type="QString" name="hash_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="hash_length_map_unit_scale"/>
                <Option value="Point" type="QString" name="hash_length_unit"/>
                <Option value="4" type="QString" name="interval"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
                <Option value="Point" type="QString" name="interval_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="0" type="QString" name="offset_along_line"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_along_line_unit"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="true" type="bool" name="place_on_every_part"/>
                <Option value="Interval" type="QString" name="placements"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="1" type="QString" name="rotate"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
              <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@@43@1@0">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleLine" id="{98bf797c-2285-4ed3-97b8-1716b341c8c4}" enabled="1">
                  <Option type="Map">
                    <Option value="0" type="QString" name="align_dash_pattern"/>
                    <Option value="square" type="QString" name="capstyle"/>
                    <Option value="5;2" type="QString" name="customdash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                    <Option value="Point" type="QString" name="customdash_unit"/>
                    <Option value="0" type="QString" name="dash_pattern_offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
                    <Option value="0" type="QString" name="draw_inside_polygon"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="line_color"/>
                    <Option value="solid" type="QString" name="line_style"/>
                    <Option value="1" type="QString" name="line_width"/>
                    <Option value="Point" type="QString" name="line_width_unit"/>
                    <Option value="0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="offset_unit"/>
                    <Option value="0" type="QString" name="ring_filter"/>
                    <Option value="0" type="QString" name="trim_distance_end"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_end_unit"/>
                    <Option value="0" type="QString" name="trim_distance_start"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_start_unit"/>
                    <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                    <Option value="0" type="QString" name="use_custom_dash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="44">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="ArrowLine" id="{91533b6d-d7a6-450e-8706-eac1f6a25d34}" enabled="1">
          <Option type="Map">
            <Option value="1" type="QString" name="arrow_start_width"/>
            <Option value="MM" type="QString" name="arrow_start_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_start_width_unit_scale"/>
            <Option value="0" type="QString" name="arrow_type"/>
            <Option value="0" type="QString" name="arrow_width"/>
            <Option value="Point" type="QString" name="arrow_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_width_unit_scale"/>
            <Option value="10" type="QString" name="head_length"/>
            <Option value="Point" type="QString" name="head_length_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_length_unit_scale"/>
            <Option value="4" type="QString" name="head_thickness"/>
            <Option value="Point" type="QString" name="head_thickness_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_thickness_unit_scale"/>
            <Option value="2" type="QString" name="head_type"/>
            <Option value="1" type="QString" name="is_curved"/>
            <Option value="1" type="QString" name="is_repeated"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="Point" type="QString" name="offset_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_unit_scale"/>
            <Option value="0" type="QString" name="ring_filter"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="fill" force_rhr="0" clip_to_extent="1" is_animated="0" name="@44@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleFill" id="{4ca734c4-5a47-4d49-a06a-7509f417212d}" enabled="1">
              <Option type="Map">
                <Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/>
                <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="color"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="0,0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="outline_color"/>
                <Option value="no" type="QString" name="outline_style"/>
                <Option value="0" type="QString" name="outline_width"/>
                <Option value="Point" type="QString" name="outline_width_unit"/>
                <Option value="solid" type="QString" name="style"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer locked="0" pass="0" class="GeometryGenerator" id="{622dfad4-c787-40f2-b02a-3acdfb1e35b4}" enabled="1">
          <Option type="Map">
            <Option value="Line" type="QString" name="SymbolType"/>
            <Option value="CASE&#xa;    WHEN length($geometry) > ( (5 + 2) * 2 ) THEN&#xa;        line_substring(&#xa;            $geometry,&#xa;            (5 + 2),&#xa;            length($geometry) - (5 + 2)&#xa;        )&#xa;    ELSE&#xa;        $geometry&#xa;END&#xa;" type="QString" name="geometryModifier"/>
            <Option value="Point" type="QString" name="units"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@44@1">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="HashLine" id="{410325a0-e6d3-4692-8772-82224a61351d}" enabled="1">
              <Option type="Map">
                <Option value="4" type="QString" name="average_angle_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
                <Option value="Point" type="QString" name="average_angle_unit"/>
                <Option value="90" type="QString" name="hash_angle"/>
                <Option value="1" type="QString" name="hash_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="hash_length_map_unit_scale"/>
                <Option value="Point" type="QString" name="hash_length_unit"/>
                <Option value="4" type="QString" name="interval"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
                <Option value="Point" type="QString" name="interval_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="0" type="QString" name="offset_along_line"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_along_line_unit"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="true" type="bool" name="place_on_every_part"/>
                <Option value="Interval" type="QString" name="placements"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="1" type="QString" name="rotate"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
              <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@@44@1@0">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleLine" id="{98bf797c-2285-4ed3-97b8-1716b341c8c4}" enabled="1">
                  <Option type="Map">
                    <Option value="0" type="QString" name="align_dash_pattern"/>
                    <Option value="square" type="QString" name="capstyle"/>
                    <Option value="5;2" type="QString" name="customdash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                    <Option value="Point" type="QString" name="customdash_unit"/>
                    <Option value="0" type="QString" name="dash_pattern_offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
                    <Option value="0" type="QString" name="draw_inside_polygon"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="line_color"/>
                    <Option value="solid" type="QString" name="line_style"/>
                    <Option value="1" type="QString" name="line_width"/>
                    <Option value="Point" type="QString" name="line_width_unit"/>
                    <Option value="0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="offset_unit"/>
                    <Option value="0" type="QString" name="ring_filter"/>
                    <Option value="0" type="QString" name="trim_distance_end"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_end_unit"/>
                    <Option value="0" type="QString" name="trim_distance_start"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_start_unit"/>
                    <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                    <Option value="0" type="QString" name="use_custom_dash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="45">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="ArrowLine" id="{91533b6d-d7a6-450e-8706-eac1f6a25d34}" enabled="1">
          <Option type="Map">
            <Option value="1" type="QString" name="arrow_start_width"/>
            <Option value="MM" type="QString" name="arrow_start_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_start_width_unit_scale"/>
            <Option value="0" type="QString" name="arrow_type"/>
            <Option value="0" type="QString" name="arrow_width"/>
            <Option value="Point" type="QString" name="arrow_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_width_unit_scale"/>
            <Option value="10" type="QString" name="head_length"/>
            <Option value="Point" type="QString" name="head_length_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_length_unit_scale"/>
            <Option value="4" type="QString" name="head_thickness"/>
            <Option value="Point" type="QString" name="head_thickness_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_thickness_unit_scale"/>
            <Option value="2" type="QString" name="head_type"/>
            <Option value="1" type="QString" name="is_curved"/>
            <Option value="1" type="QString" name="is_repeated"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="Point" type="QString" name="offset_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_unit_scale"/>
            <Option value="0" type="QString" name="ring_filter"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="fill" force_rhr="0" clip_to_extent="1" is_animated="0" name="@45@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleFill" id="{4ca734c4-5a47-4d49-a06a-7509f417212d}" enabled="1">
              <Option type="Map">
                <Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/>
                <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="color"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="0,0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="outline_color"/>
                <Option value="no" type="QString" name="outline_style"/>
                <Option value="0" type="QString" name="outline_width"/>
                <Option value="Point" type="QString" name="outline_width_unit"/>
                <Option value="solid" type="QString" name="style"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer locked="0" pass="0" class="GeometryGenerator" id="{622dfad4-c787-40f2-b02a-3acdfb1e35b4}" enabled="1">
          <Option type="Map">
            <Option value="Line" type="QString" name="SymbolType"/>
            <Option value="CASE&#xa;    WHEN length($geometry) > ( (5 + 2) * 2 ) THEN&#xa;        line_substring(&#xa;            $geometry,&#xa;            (5 + 2),&#xa;            length($geometry) - (5 + 2)&#xa;        )&#xa;    ELSE&#xa;        $geometry&#xa;END&#xa;" type="QString" name="geometryModifier"/>
            <Option value="Point" type="QString" name="units"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@45@1">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="HashLine" id="{410325a0-e6d3-4692-8772-82224a61351d}" enabled="1">
              <Option type="Map">
                <Option value="4" type="QString" name="average_angle_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
                <Option value="Point" type="QString" name="average_angle_unit"/>
                <Option value="90" type="QString" name="hash_angle"/>
                <Option value="1" type="QString" name="hash_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="hash_length_map_unit_scale"/>
                <Option value="Point" type="QString" name="hash_length_unit"/>
                <Option value="4" type="QString" name="interval"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
                <Option value="Point" type="QString" name="interval_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="0" type="QString" name="offset_along_line"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_along_line_unit"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="true" type="bool" name="place_on_every_part"/>
                <Option value="Interval" type="QString" name="placements"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="1" type="QString" name="rotate"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
              <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@@45@1@0">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleLine" id="{98bf797c-2285-4ed3-97b8-1716b341c8c4}" enabled="1">
                  <Option type="Map">
                    <Option value="0" type="QString" name="align_dash_pattern"/>
                    <Option value="square" type="QString" name="capstyle"/>
                    <Option value="5;2" type="QString" name="customdash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                    <Option value="Point" type="QString" name="customdash_unit"/>
                    <Option value="0" type="QString" name="dash_pattern_offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
                    <Option value="0" type="QString" name="draw_inside_polygon"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="line_color"/>
                    <Option value="solid" type="QString" name="line_style"/>
                    <Option value="1" type="QString" name="line_width"/>
                    <Option value="Point" type="QString" name="line_width_unit"/>
                    <Option value="0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="offset_unit"/>
                    <Option value="0" type="QString" name="ring_filter"/>
                    <Option value="0" type="QString" name="trim_distance_end"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_end_unit"/>
                    <Option value="0" type="QString" name="trim_distance_start"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_start_unit"/>
                    <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                    <Option value="0" type="QString" name="use_custom_dash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="46">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{8ad0c838-9845-4e87-88d7-4222d703f5c4}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="124,217,204,255,rgb:0.48627450980392156,0.85098039215686272,0.80000000000000004,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="7" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="47">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="MarkerLine" id="{be582606-510c-4a5f-a69e-01bfa27474ff}" enabled="1">
          <Option type="Map">
            <Option value="4" type="QString" name="average_angle_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
            <Option value="MM" type="QString" name="average_angle_unit"/>
            <Option value="3" type="QString" name="interval"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
            <Option value="MM" type="QString" name="interval_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="0" type="QString" name="offset_along_line"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_along_line_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="true" type="bool" name="place_on_every_part"/>
            <Option value="Interval" type="QString" name="placements"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="1" type="QString" name="rotate"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="marker" force_rhr="0" clip_to_extent="1" is_animated="0" name="@47@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleMarker" id="{ae6c71f4-836a-4a67-8e8a-ce20728f47e2}" enabled="1">
              <Option type="Map">
                <Option value="0" type="QString" name="angle"/>
                <Option value="square" type="QString" name="cap_style"/>
                <Option value="255,255,255,255,rgb:1,1,1,1" type="QString" name="color"/>
                <Option value="1" type="QString" name="horizontal_anchor_point"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="circle" type="QString" name="name"/>
                <Option value="0,0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="MM" type="QString" name="offset_unit"/>
                <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="outline_color"/>
                <Option value="solid" type="QString" name="outline_style"/>
                <Option value="0.5" type="QString" name="outline_width"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="outline_width_map_unit_scale"/>
                <Option value="Point" type="QString" name="outline_width_unit"/>
                <Option value="diameter" type="QString" name="scale_method"/>
                <Option value="2" type="QString" name="size"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="size_map_unit_scale"/>
                <Option value="MM" type="QString" name="size_unit"/>
                <Option value="1" type="QString" name="vertical_anchor_point"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="48">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="MarkerLine" id="{be582606-510c-4a5f-a69e-01bfa27474ff}" enabled="1">
          <Option type="Map">
            <Option value="4" type="QString" name="average_angle_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
            <Option value="MM" type="QString" name="average_angle_unit"/>
            <Option value="3" type="QString" name="interval"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
            <Option value="MM" type="QString" name="interval_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="0" type="QString" name="offset_along_line"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_along_line_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="true" type="bool" name="place_on_every_part"/>
            <Option value="Interval" type="QString" name="placements"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="1" type="QString" name="rotate"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="marker" force_rhr="0" clip_to_extent="1" is_animated="0" name="@48@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleMarker" id="{ae6c71f4-836a-4a67-8e8a-ce20728f47e2}" enabled="1">
              <Option type="Map">
                <Option value="0" type="QString" name="angle"/>
                <Option value="square" type="QString" name="cap_style"/>
                <Option value="255,255,255,255,rgb:1,1,1,1" type="QString" name="color"/>
                <Option value="1" type="QString" name="horizontal_anchor_point"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="circle" type="QString" name="name"/>
                <Option value="0,0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="MM" type="QString" name="offset_unit"/>
                <Option value="229,31,45,255,rgb:0.89803921568627454,0.12156862745098039,0.17647058823529413,1" type="QString" name="outline_color"/>
                <Option value="solid" type="QString" name="outline_style"/>
                <Option value="0.5" type="QString" name="outline_width"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="outline_width_map_unit_scale"/>
                <Option value="Point" type="QString" name="outline_width_unit"/>
                <Option value="diameter" type="QString" name="scale_method"/>
                <Option value="2" type="QString" name="size"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="size_map_unit_scale"/>
                <Option value="MM" type="QString" name="size_unit"/>
                <Option value="1" type="QString" name="vertical_anchor_point"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="49">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="GeometryGenerator" id="{644c1d0a-ce9b-4e3a-8e27-3930a6b21a8f}" enabled="1">
          <Option type="Map">
            <Option value="Line" type="QString" name="SymbolType"/>
            <Option value="CASE&#xa;    WHEN length($geometry) > (2) THEN&#xa;        line_substring(&#xa;            $geometry,&#xa;            10,&#xa;            length($geometry) - 8&#xa;        )&#xa;    ELSE&#xa;        $geometry&#xa;END&#xa;" type="QString" name="geometryModifier"/>
            <Option value="Point" type="QString" name="units"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@49@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="MarkerLine" id="{2d99c1db-caad-4488-af10-7fe52e51b266}" enabled="1">
              <Option type="Map">
                <Option value="4" type="QString" name="average_angle_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
                <Option value="MM" type="QString" name="average_angle_unit"/>
                <Option value="3" type="QString" name="interval"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
                <Option value="MM" type="QString" name="interval_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="0" type="QString" name="offset_along_line"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
                <Option value="MM" type="QString" name="offset_along_line_unit"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="MM" type="QString" name="offset_unit"/>
                <Option value="true" type="bool" name="place_on_every_part"/>
                <Option value="Interval" type="QString" name="placements"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="1" type="QString" name="rotate"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
              <symbol alpha="1" frame_rate="10" type="marker" force_rhr="0" clip_to_extent="1" is_animated="0" name="@@49@0@0">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleMarker" id="{ae6c71f4-836a-4a67-8e8a-ce20728f47e2}" enabled="1">
                  <Option type="Map">
                    <Option value="0" type="QString" name="angle"/>
                    <Option value="square" type="QString" name="cap_style"/>
                    <Option value="255,255,255,255,rgb:1,1,1,1" type="QString" name="color"/>
                    <Option value="1" type="QString" name="horizontal_anchor_point"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="circle" type="QString" name="name"/>
                    <Option value="0,0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="MM" type="QString" name="offset_unit"/>
                    <Option value="229,31,45,255,rgb:0.89803921568627454,0.12156862745098039,0.17647058823529413,1" type="QString" name="outline_color"/>
                    <Option value="solid" type="QString" name="outline_style"/>
                    <Option value="0.5" type="QString" name="outline_width"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="outline_width_map_unit_scale"/>
                    <Option value="Point" type="QString" name="outline_width_unit"/>
                    <Option value="diameter" type="QString" name="scale_method"/>
                    <Option value="2" type="QString" name="size"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="size_map_unit_scale"/>
                    <Option value="MM" type="QString" name="size_unit"/>
                    <Option value="1" type="QString" name="vertical_anchor_point"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
        <layer locked="0" pass="0" class="ArrowLine" id="{9ff3dc2f-4946-4e73-baf9-11d695921d98}" enabled="1">
          <Option type="Map">
            <Option value="1" type="QString" name="arrow_start_width"/>
            <Option value="MM" type="QString" name="arrow_start_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_start_width_unit_scale"/>
            <Option value="0" type="QString" name="arrow_type"/>
            <Option value="0" type="QString" name="arrow_width"/>
            <Option value="Point" type="QString" name="arrow_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_width_unit_scale"/>
            <Option value="2" type="QString" name="head_length"/>
            <Option value="MM" type="QString" name="head_length_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_length_unit_scale"/>
            <Option value="2" type="QString" name="head_thickness"/>
            <Option value="MM" type="QString" name="head_thickness_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_thickness_unit_scale"/>
            <Option value="2" type="QString" name="head_type"/>
            <Option value="1" type="QString" name="is_curved"/>
            <Option value="1" type="QString" name="is_repeated"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_unit_scale"/>
            <Option value="0" type="QString" name="ring_filter"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="fill" force_rhr="0" clip_to_extent="1" is_animated="0" name="@49@1">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleFill" id="{d31c8c7c-3653-40b7-9cad-9d01be6cbb48}" enabled="1">
              <Option type="Map">
                <Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/>
                <Option value="229,31,45,255,rgb:0.89803921568627454,0.12156862745098039,0.17647058823529413,1" type="QString" name="color"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="0,0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="35,35,35,0,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,0" type="QString" name="outline_color"/>
                <Option value="no" type="QString" name="outline_style"/>
                <Option value="0" type="QString" name="outline_width"/>
                <Option value="Point" type="QString" name="outline_width_unit"/>
                <Option value="solid" type="QString" name="style"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="5">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{c1fbaa3b-6edf-46d1-be03-12db49ccc062}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="7" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="50">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{f57eba6b-1712-4eb0-a30d-1cef77422d06}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="111,168,218,255,rgb:0.43529411764705883,0.6588235294117647,0.85490196078431369,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="1.25" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="51">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="MarkerLine" id="{394de993-20d3-4bd0-9c6c-358039a3eb8d}" enabled="1">
          <Option type="Map">
            <Option value="4" type="QString" name="average_angle_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
            <Option value="MM" type="QString" name="average_angle_unit"/>
            <Option value="3" type="QString" name="interval"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
            <Option value="Point" type="QString" name="interval_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="0" type="QString" name="offset_along_line"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_along_line_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="true" type="bool" name="place_on_every_part"/>
            <Option value="Interval" type="QString" name="placements"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="1" type="QString" name="rotate"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="marker" force_rhr="0" clip_to_extent="1" is_animated="0" name="@51@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleMarker" id="{022f2612-398f-4d5f-b472-4f659b787a08}" enabled="1">
              <Option type="Map">
                <Option value="0" type="QString" name="angle"/>
                <Option value="square" type="QString" name="cap_style"/>
                <Option value="150,150,150,255,rgb:0.58823529411764708,0.58823529411764708,0.58823529411764708,1" type="QString" name="color"/>
                <Option value="1" type="QString" name="horizontal_anchor_point"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="circle" type="QString" name="name"/>
                <Option value="0,0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="outline_color"/>
                <Option value="no" type="QString" name="outline_style"/>
                <Option value="0" type="QString" name="outline_width"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="outline_width_map_unit_scale"/>
                <Option value="Point" type="QString" name="outline_width_unit"/>
                <Option value="diameter" type="QString" name="scale_method"/>
                <Option value="2" type="QString" name="size"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="size_map_unit_scale"/>
                <Option value="Point" type="QString" name="size_unit"/>
                <Option value="1" type="QString" name="vertical_anchor_point"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer locked="0" pass="0" class="SimpleLine" id="{9ab10eaf-e5c1-448b-be3d-ba056ed209ce}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="150,150,150,255,rgb:0.58823529411764708,0.58823529411764708,0.58823529411764708,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="0.75" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="52">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{8ecf55d0-a946-461d-9ae9-6f1c30fc5e62}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="25,104,64,255,rgb:0.09803921568627451,0.40784313725490196,0.25098039215686274,1" type="QString" name="line_color"/>
            <Option value="dash dot" type="QString" name="line_style"/>
            <Option value="1" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="53">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="ArrowLine" id="{50275a2d-a0cc-4563-a4bf-a99f2011a7aa}" enabled="1">
          <Option type="Map">
            <Option value="5" type="QString" name="arrow_start_width"/>
            <Option value="Point" type="QString" name="arrow_start_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_start_width_unit_scale"/>
            <Option value="0" type="QString" name="arrow_type"/>
            <Option value="5" type="QString" name="arrow_width"/>
            <Option value="Point" type="QString" name="arrow_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_width_unit_scale"/>
            <Option value="15" type="QString" name="head_length"/>
            <Option value="Point" type="QString" name="head_length_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_length_unit_scale"/>
            <Option value="7.5" type="QString" name="head_thickness"/>
            <Option value="Point" type="QString" name="head_thickness_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_thickness_unit_scale"/>
            <Option value="0" type="QString" name="head_type"/>
            <Option value="1" type="QString" name="is_curved"/>
            <Option value="1" type="QString" name="is_repeated"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_unit_scale"/>
            <Option value="0" type="QString" name="ring_filter"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="fill" force_rhr="0" clip_to_extent="1" is_animated="0" name="@53@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleFill" id="{48d25de5-881f-4d77-8eae-c4fa9a833d07}" enabled="1">
              <Option type="Map">
                <Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/>
                <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="color"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="0,0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="MM" type="QString" name="offset_unit"/>
                <Option value="231,113,72,0,rgb:0.90588235294117647,0.44313725490196076,0.28235294117647058,0" type="QString" name="outline_color"/>
                <Option value="no" type="QString" name="outline_style"/>
                <Option value="0.26" type="QString" name="outline_width"/>
                <Option value="MM" type="QString" name="outline_width_unit"/>
                <Option value="solid" type="QString" name="style"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="54">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="ArrowLine" id="{91533b6d-d7a6-450e-8706-eac1f6a25d34}" enabled="1">
          <Option type="Map">
            <Option value="1" type="QString" name="arrow_start_width"/>
            <Option value="MM" type="QString" name="arrow_start_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_start_width_unit_scale"/>
            <Option value="0" type="QString" name="arrow_type"/>
            <Option value="0" type="QString" name="arrow_width"/>
            <Option value="Point" type="QString" name="arrow_width_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="arrow_width_unit_scale"/>
            <Option value="10" type="QString" name="head_length"/>
            <Option value="Point" type="QString" name="head_length_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_length_unit_scale"/>
            <Option value="10" type="QString" name="head_thickness"/>
            <Option value="Point" type="QString" name="head_thickness_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="head_thickness_unit_scale"/>
            <Option value="2" type="QString" name="head_type"/>
            <Option value="1" type="QString" name="is_curved"/>
            <Option value="1" type="QString" name="is_repeated"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="Point" type="QString" name="offset_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_unit_scale"/>
            <Option value="0" type="QString" name="ring_filter"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="fill" force_rhr="0" clip_to_extent="1" is_animated="0" name="@54@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleFill" id="{4ca734c4-5a47-4d49-a06a-7509f417212d}" enabled="1">
              <Option type="Map">
                <Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/>
                <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="color"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="0,0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="outline_color"/>
                <Option value="no" type="QString" name="outline_style"/>
                <Option value="0" type="QString" name="outline_width"/>
                <Option value="Point" type="QString" name="outline_width_unit"/>
                <Option value="solid" type="QString" name="style"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer locked="0" pass="0" class="GeometryGenerator" id="{622dfad4-c787-40f2-b02a-3acdfb1e35b4}" enabled="1">
          <Option type="Map">
            <Option value="Line" type="QString" name="SymbolType"/>
            <Option value="CASE&#xa;    WHEN length($geometry) > ( (5 + 2) * 2 ) THEN&#xa;        line_substring(&#xa;            $geometry,&#xa;            (5 + 2),&#xa;            length($geometry) - (5 + 2)&#xa;        )&#xa;    ELSE&#xa;        $geometry&#xa;END&#xa;" type="QString" name="geometryModifier"/>
            <Option value="Point" type="QString" name="units"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@54@1">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="HashLine" id="{410325a0-e6d3-4692-8772-82224a61351d}" enabled="1">
              <Option type="Map">
                <Option value="4" type="QString" name="average_angle_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
                <Option value="Point" type="QString" name="average_angle_unit"/>
                <Option value="90" type="QString" name="hash_angle"/>
                <Option value="1" type="QString" name="hash_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="hash_length_map_unit_scale"/>
                <Option value="Point" type="QString" name="hash_length_unit"/>
                <Option value="12" type="QString" name="interval"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
                <Option value="Point" type="QString" name="interval_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="0" type="QString" name="offset_along_line"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_along_line_unit"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="true" type="bool" name="place_on_every_part"/>
                <Option value="Interval" type="QString" name="placements"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="1" type="QString" name="rotate"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
              <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@@54@1@0">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleLine" id="{98bf797c-2285-4ed3-97b8-1716b341c8c4}" enabled="1">
                  <Option type="Map">
                    <Option value="0" type="QString" name="align_dash_pattern"/>
                    <Option value="square" type="QString" name="capstyle"/>
                    <Option value="5;2" type="QString" name="customdash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                    <Option value="Point" type="QString" name="customdash_unit"/>
                    <Option value="0" type="QString" name="dash_pattern_offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
                    <Option value="0" type="QString" name="draw_inside_polygon"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="line_color"/>
                    <Option value="solid" type="QString" name="line_style"/>
                    <Option value="7" type="QString" name="line_width"/>
                    <Option value="Point" type="QString" name="line_width_unit"/>
                    <Option value="0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="offset_unit"/>
                    <Option value="0" type="QString" name="ring_filter"/>
                    <Option value="0" type="QString" name="trim_distance_end"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_end_unit"/>
                    <Option value="0" type="QString" name="trim_distance_start"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_start_unit"/>
                    <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                    <Option value="0" type="QString" name="use_custom_dash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="55">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{e5ff37ef-d0d9-44c3-94e7-a4765b94a4bd}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="Point" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="193,221,245,255,rgb:0.75686274509803919,0.8666666666666667,0.96078431372549022,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="3" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="Point" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="Point" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="Point" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="56">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{c1fbaa3b-6edf-46d1-be03-12db49ccc062}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="3" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="57">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{c1fbaa3b-6edf-46d1-be03-12db49ccc062}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="3" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="58">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{c052811d-9eda-4001-85b3-83dcb53d0923}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="2.5" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="1.665" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer locked="0" pass="0" class="SimpleLine" id="{f7edbb7f-8d68-4b12-87c1-17186e35cebf}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="2.5" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="-1.665" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="59">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{c052811d-9eda-4001-85b3-83dcb53d0923}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="2.5" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="1.665" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer locked="0" pass="0" class="SimpleLine" id="{f7edbb7f-8d68-4b12-87c1-17186e35cebf}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="2.5" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="-1.665" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="6">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{c1fbaa3b-6edf-46d1-be03-12db49ccc062}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="5" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="60">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{c052811d-9eda-4001-85b3-83dcb53d0923}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="2.5" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="1.665" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer locked="0" pass="0" class="SimpleLine" id="{f7edbb7f-8d68-4b12-87c1-17186e35cebf}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="2.5" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="-1.665" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="61">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{c052811d-9eda-4001-85b3-83dcb53d0923}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="2.5" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="1.665" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer locked="0" pass="0" class="SimpleLine" id="{f7edbb7f-8d68-4b12-87c1-17186e35cebf}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="2.5" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="-1.665" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="62">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{c052811d-9eda-4001-85b3-83dcb53d0923}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="2.5" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="1.665" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer locked="0" pass="0" class="SimpleLine" id="{f7edbb7f-8d68-4b12-87c1-17186e35cebf}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="2.5" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="-1.665" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="63">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="HashLine" id="{e8e74edc-9f4c-4872-952a-71dc3d78f6ae}" enabled="1">
          <Option type="Map">
            <Option value="4" type="QString" name="average_angle_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
            <Option value="MM" type="QString" name="average_angle_unit"/>
            <Option value="0" type="QString" name="hash_angle"/>
            <Option value="3" type="QString" name="hash_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="hash_length_map_unit_scale"/>
            <Option value="MM" type="QString" name="hash_length_unit"/>
            <Option value="5" type="QString" name="interval"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
            <Option value="Point" type="QString" name="interval_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="0" type="QString" name="offset_along_line"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_along_line_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="true" type="bool" name="place_on_every_part"/>
            <Option value="Interval|LastVertex|FirstVertex" type="QString" name="placements"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="1" type="QString" name="rotate"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@63@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleLine" id="{8ece23c8-3575-4aab-82ae-f29f412552e6}" enabled="1">
              <Option type="Map">
                <Option value="0" type="QString" name="align_dash_pattern"/>
                <Option value="square" type="QString" name="capstyle"/>
                <Option value="5;2" type="QString" name="customdash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                <Option value="Point" type="QString" name="customdash_unit"/>
                <Option value="0" type="QString" name="dash_pattern_offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
                <Option value="0" type="QString" name="draw_inside_polygon"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
                <Option value="solid" type="QString" name="line_style"/>
                <Option value="1.5" type="QString" name="line_width"/>
                <Option value="Point" type="QString" name="line_width_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="0" type="QString" name="trim_distance_end"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                <Option value="Point" type="QString" name="trim_distance_end_unit"/>
                <Option value="0" type="QString" name="trim_distance_start"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                <Option value="Point" type="QString" name="trim_distance_start_unit"/>
                <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                <Option value="0" type="QString" name="use_custom_dash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer locked="0" pass="0" class="SimpleLine" id="{583d8817-83d0-4417-a21c-bc8a0f5962c3}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="2" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="64">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="HashLine" id="{e8e74edc-9f4c-4872-952a-71dc3d78f6ae}" enabled="1">
          <Option type="Map">
            <Option value="4" type="QString" name="average_angle_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
            <Option value="MM" type="QString" name="average_angle_unit"/>
            <Option value="0" type="QString" name="hash_angle"/>
            <Option value="3" type="QString" name="hash_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="hash_length_map_unit_scale"/>
            <Option value="MM" type="QString" name="hash_length_unit"/>
            <Option value="5" type="QString" name="interval"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
            <Option value="Point" type="QString" name="interval_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="0" type="QString" name="offset_along_line"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_along_line_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="true" type="bool" name="place_on_every_part"/>
            <Option value="Interval|LastVertex|FirstVertex" type="QString" name="placements"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="1" type="QString" name="rotate"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@64@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleLine" id="{8ece23c8-3575-4aab-82ae-f29f412552e6}" enabled="1">
              <Option type="Map">
                <Option value="0" type="QString" name="align_dash_pattern"/>
                <Option value="square" type="QString" name="capstyle"/>
                <Option value="5;2" type="QString" name="customdash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                <Option value="Point" type="QString" name="customdash_unit"/>
                <Option value="0" type="QString" name="dash_pattern_offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
                <Option value="0" type="QString" name="draw_inside_polygon"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
                <Option value="solid" type="QString" name="line_style"/>
                <Option value="1.5" type="QString" name="line_width"/>
                <Option value="Point" type="QString" name="line_width_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="0" type="QString" name="trim_distance_end"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                <Option value="Point" type="QString" name="trim_distance_end_unit"/>
                <Option value="0" type="QString" name="trim_distance_start"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                <Option value="Point" type="QString" name="trim_distance_start_unit"/>
                <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                <Option value="0" type="QString" name="use_custom_dash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer locked="0" pass="0" class="SimpleLine" id="{583d8817-83d0-4417-a21c-bc8a0f5962c3}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="2" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="65">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="MarkerLine" id="{2d48c339-7219-4853-9455-482ff36db9cb}" enabled="1">
          <Option type="Map">
            <Option value="4" type="QString" name="average_angle_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
            <Option value="MM" type="QString" name="average_angle_unit"/>
            <Option value="3" type="QString" name="interval"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
            <Option value="MM" type="QString" name="interval_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="0" type="QString" name="offset_along_line"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_along_line_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="Point" type="QString" name="offset_unit"/>
            <Option value="true" type="bool" name="place_on_every_part"/>
            <Option value="Interval" type="QString" name="placements"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="1" type="QString" name="rotate"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="marker" force_rhr="0" clip_to_extent="1" is_animated="0" name="@65@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleMarker" id="{ed7d9090-ad54-45eb-8c54-9297ac414bb7}" enabled="1">
              <Option type="Map">
                <Option value="0" type="QString" name="angle"/>
                <Option value="square" type="QString" name="cap_style"/>
                <Option value="0,0,0,255,hsv:0,1,0,1" type="QString" name="color"/>
                <Option value="1" type="QString" name="horizontal_anchor_point"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="circle" type="QString" name="name"/>
                <Option value="0,0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="outline_color"/>
                <Option value="no" type="QString" name="outline_style"/>
                <Option value="0" type="QString" name="outline_width"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="outline_width_map_unit_scale"/>
                <Option value="Point" type="QString" name="outline_width_unit"/>
                <Option value="diameter" type="QString" name="scale_method"/>
                <Option value="5" type="QString" name="size"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="size_map_unit_scale"/>
                <Option value="Point" type="QString" name="size_unit"/>
                <Option value="1" type="QString" name="vertical_anchor_point"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="66">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="MarkerLine" id="{2d48c339-7219-4853-9455-482ff36db9cb}" enabled="1">
          <Option type="Map">
            <Option value="4" type="QString" name="average_angle_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
            <Option value="MM" type="QString" name="average_angle_unit"/>
            <Option value="3" type="QString" name="interval"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
            <Option value="MM" type="QString" name="interval_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="0" type="QString" name="offset_along_line"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_along_line_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="Point" type="QString" name="offset_unit"/>
            <Option value="true" type="bool" name="place_on_every_part"/>
            <Option value="Interval" type="QString" name="placements"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="1" type="QString" name="rotate"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="marker" force_rhr="0" clip_to_extent="1" is_animated="0" name="@66@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleMarker" id="{ed7d9090-ad54-45eb-8c54-9297ac414bb7}" enabled="1">
              <Option type="Map">
                <Option value="0" type="QString" name="angle"/>
                <Option value="square" type="QString" name="cap_style"/>
                <Option value="0,0,0,255,hsv:0,1,0,1" type="QString" name="color"/>
                <Option value="1" type="QString" name="horizontal_anchor_point"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="circle" type="QString" name="name"/>
                <Option value="0,0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="outline_color"/>
                <Option value="no" type="QString" name="outline_style"/>
                <Option value="0" type="QString" name="outline_width"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="outline_width_map_unit_scale"/>
                <Option value="Point" type="QString" name="outline_width_unit"/>
                <Option value="diameter" type="QString" name="scale_method"/>
                <Option value="5" type="QString" name="size"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="size_map_unit_scale"/>
                <Option value="Point" type="QString" name="size_unit"/>
                <Option value="1" type="QString" name="vertical_anchor_point"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="67">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="MarkerLine" id="{2d48c339-7219-4853-9455-482ff36db9cb}" enabled="1">
          <Option type="Map">
            <Option value="4" type="QString" name="average_angle_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
            <Option value="MM" type="QString" name="average_angle_unit"/>
            <Option value="3" type="QString" name="interval"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
            <Option value="MM" type="QString" name="interval_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="0" type="QString" name="offset_along_line"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_along_line_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="Point" type="QString" name="offset_unit"/>
            <Option value="true" type="bool" name="place_on_every_part"/>
            <Option value="Interval" type="QString" name="placements"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="1" type="QString" name="rotate"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="marker" force_rhr="0" clip_to_extent="1" is_animated="0" name="@67@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleMarker" id="{ed7d9090-ad54-45eb-8c54-9297ac414bb7}" enabled="1">
              <Option type="Map">
                <Option value="0" type="QString" name="angle"/>
                <Option value="square" type="QString" name="cap_style"/>
                <Option value="0,0,0,255,hsv:0,1,0,1" type="QString" name="color"/>
                <Option value="1" type="QString" name="horizontal_anchor_point"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="circle" type="QString" name="name"/>
                <Option value="0,0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="outline_color"/>
                <Option value="no" type="QString" name="outline_style"/>
                <Option value="0" type="QString" name="outline_width"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="outline_width_map_unit_scale"/>
                <Option value="Point" type="QString" name="outline_width_unit"/>
                <Option value="diameter" type="QString" name="scale_method"/>
                <Option value="5" type="QString" name="size"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="size_map_unit_scale"/>
                <Option value="Point" type="QString" name="size_unit"/>
                <Option value="1" type="QString" name="vertical_anchor_point"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="68">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="GeometryGenerator" id="{622dfad4-c787-40f2-b02a-3acdfb1e35b4}" enabled="1">
          <Option type="Map">
            <Option value="Line" type="QString" name="SymbolType"/>
            <Option value="CASE&#xa;    WHEN length($geometry) > ( (5 + 2) * 2 ) THEN&#xa;        line_substring(&#xa;            $geometry,&#xa;            (5 + 2),&#xa;            length($geometry) - (5 + 2)&#xa;        )&#xa;    ELSE&#xa;        $geometry&#xa;END&#xa;" type="QString" name="geometryModifier"/>
            <Option value="Point" type="QString" name="units"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@68@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="HashLine" id="{410325a0-e6d3-4692-8772-82224a61351d}" enabled="1">
              <Option type="Map">
                <Option value="4" type="QString" name="average_angle_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
                <Option value="Point" type="QString" name="average_angle_unit"/>
                <Option value="90" type="QString" name="hash_angle"/>
                <Option value="3" type="QString" name="hash_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="hash_length_map_unit_scale"/>
                <Option value="Point" type="QString" name="hash_length_unit"/>
                <Option value="15" type="QString" name="interval"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
                <Option value="Point" type="QString" name="interval_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="0" type="QString" name="offset_along_line"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_along_line_unit"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="true" type="bool" name="place_on_every_part"/>
                <Option value="Interval" type="QString" name="placements"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="1" type="QString" name="rotate"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
              <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@@68@0@0">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleLine" id="{98bf797c-2285-4ed3-97b8-1716b341c8c4}" enabled="1">
                  <Option type="Map">
                    <Option value="0" type="QString" name="align_dash_pattern"/>
                    <Option value="square" type="QString" name="capstyle"/>
                    <Option value="5;2" type="QString" name="customdash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                    <Option value="Point" type="QString" name="customdash_unit"/>
                    <Option value="0" type="QString" name="dash_pattern_offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
                    <Option value="0" type="QString" name="draw_inside_polygon"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="line_color"/>
                    <Option value="solid" type="QString" name="line_style"/>
                    <Option value="7" type="QString" name="line_width"/>
                    <Option value="Point" type="QString" name="line_width_unit"/>
                    <Option value="0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="offset_unit"/>
                    <Option value="0" type="QString" name="ring_filter"/>
                    <Option value="0" type="QString" name="trim_distance_end"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_end_unit"/>
                    <Option value="0" type="QString" name="trim_distance_start"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_start_unit"/>
                    <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                    <Option value="0" type="QString" name="use_custom_dash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="69">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="GeometryGenerator" id="{622dfad4-c787-40f2-b02a-3acdfb1e35b4}" enabled="1">
          <Option type="Map">
            <Option value="Line" type="QString" name="SymbolType"/>
            <Option value="CASE&#xa;    WHEN length($geometry) > ( (5 + 2) * 2 ) THEN&#xa;        line_substring(&#xa;            $geometry,&#xa;            (5 + 2),&#xa;            length($geometry) - (5 + 2)&#xa;        )&#xa;    ELSE&#xa;        $geometry&#xa;END&#xa;" type="QString" name="geometryModifier"/>
            <Option value="Point" type="QString" name="units"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@69@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="HashLine" id="{410325a0-e6d3-4692-8772-82224a61351d}" enabled="1">
              <Option type="Map">
                <Option value="4" type="QString" name="average_angle_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
                <Option value="Point" type="QString" name="average_angle_unit"/>
                <Option value="90" type="QString" name="hash_angle"/>
                <Option value="0.5" type="QString" name="hash_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="hash_length_map_unit_scale"/>
                <Option value="Point" type="QString" name="hash_length_unit"/>
                <Option value="12" type="QString" name="interval"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
                <Option value="Point" type="QString" name="interval_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="0" type="QString" name="offset_along_line"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_along_line_unit"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="Point" type="QString" name="offset_unit"/>
                <Option value="true" type="bool" name="place_on_every_part"/>
                <Option value="Interval" type="QString" name="placements"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="1" type="QString" name="rotate"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
              <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@@69@0@0">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleLine" id="{98bf797c-2285-4ed3-97b8-1716b341c8c4}" enabled="1">
                  <Option type="Map">
                    <Option value="0" type="QString" name="align_dash_pattern"/>
                    <Option value="square" type="QString" name="capstyle"/>
                    <Option value="5;2" type="QString" name="customdash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                    <Option value="Point" type="QString" name="customdash_unit"/>
                    <Option value="0" type="QString" name="dash_pattern_offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="dash_pattern_offset_unit"/>
                    <Option value="0" type="QString" name="draw_inside_polygon"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1" type="QString" name="line_color"/>
                    <Option value="solid" type="QString" name="line_style"/>
                    <Option value="7" type="QString" name="line_width"/>
                    <Option value="Point" type="QString" name="line_width_unit"/>
                    <Option value="0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="Point" type="QString" name="offset_unit"/>
                    <Option value="0" type="QString" name="ring_filter"/>
                    <Option value="0" type="QString" name="trim_distance_end"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_end_unit"/>
                    <Option value="0" type="QString" name="trim_distance_start"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                    <Option value="Point" type="QString" name="trim_distance_start_unit"/>
                    <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                    <Option value="0" type="QString" name="use_custom_dash"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="7">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{c1fbaa3b-6edf-46d1-be03-12db49ccc062}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="5" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="70">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="HashLine" id="{bff5a665-c20a-4b9c-8fe9-d41b7e19539f}" enabled="1">
          <Option type="Map">
            <Option value="4" type="QString" name="average_angle_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
            <Option value="MM" type="QString" name="average_angle_unit"/>
            <Option value="45" type="QString" name="hash_angle"/>
            <Option value="1" type="QString" name="hash_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="hash_length_map_unit_scale"/>
            <Option value="MM" type="QString" name="hash_length_unit"/>
            <Option value="2" type="QString" name="interval"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
            <Option value="MM" type="QString" name="interval_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="0" type="QString" name="offset_along_line"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_along_line_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="true" type="bool" name="place_on_every_part"/>
            <Option value="Interval" type="QString" name="placements"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="1" type="QString" name="rotate"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="@70@0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" pass="0" class="SimpleLine" id="{5ddeaaf4-9263-4cf3-bf10-9622178b4a1f}" enabled="1">
              <Option type="Map">
                <Option value="0" type="QString" name="align_dash_pattern"/>
                <Option value="square" type="QString" name="capstyle"/>
                <Option value="5;2" type="QString" name="customdash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                <Option value="MM" type="QString" name="customdash_unit"/>
                <Option value="0" type="QString" name="dash_pattern_offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
                <Option value="0" type="QString" name="draw_inside_polygon"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="221,35,35,255,rgb:0.8666666666666667,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
                <Option value="solid" type="QString" name="line_style"/>
                <Option value="0.26" type="QString" name="line_width"/>
                <Option value="MM" type="QString" name="line_width_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="MM" type="QString" name="offset_unit"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="0" type="QString" name="trim_distance_end"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                <Option value="MM" type="QString" name="trim_distance_end_unit"/>
                <Option value="0" type="QString" name="trim_distance_start"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                <Option value="MM" type="QString" name="trim_distance_start_unit"/>
                <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                <Option value="0" type="QString" name="use_custom_dash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="8">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{c1fbaa3b-6edf-46d1-be03-12db49ccc062}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="5" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="9">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{c1fbaa3b-6edf-46d1-be03-12db49ccc062}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="3" type="QString" name="line_width"/>
            <Option value="Point" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
    <data-defined-properties>
      <Option type="Map">
        <Option value="" type="QString" name="name"/>
        <Option name="properties"/>
        <Option value="collection" type="QString" name="type"/>
      </Option>
    </data-defined-properties>
  </renderer-v2>
  <selection mode="Default">
    <selectionColor invalid="1"/>
    <selectionSymbol>
      <symbol alpha="1" frame_rate="10" type="line" force_rhr="0" clip_to_extent="1" is_animated="0" name="">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" class="SimpleLine" id="{caf62504-e233-4f5d-a577-bd90a633f492}" enabled="1">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="0.26" type="QString" name="line_width"/>
            <Option value="MM" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </selectionSymbol>
  </selection>
  <labeling type="rule-based">
    <rules key="{efa0acfc-7dc1-45fb-926d-2a397aecacd7}">
      <rule description="Liikennetunneli" key="{38588f16-c3c0-4f1b-81e8-7bb41850db1d}" filter="map_akeys(&quot;type_regulations&quot;) = array('liikennetunneli')">
        <settings calloutType="simple">
          <text-style fontLetterSpacing="0" tabStopDistance="80" multilineHeightUnit="Percentage" fieldName="array_to_string(&quot;short_names&quot;, '/')" useSubstitutions="0" textOrientation="horizontal" capitalization="0" textOpacity="1" tabStopDistanceUnit="Point" multilineHeight="1" forcedItalic="0" tabStopDistanceMapUnitScale="3x:0,0,0,0,0,0" namedStyle="Normal" previewBkgrdColor="255,255,255,255,rgb:1,1,1,1" fontSizeUnit="Point" fontKerning="1" blendMode="0" fontWeight="50" legendString="Aa" textColor="50,50,50,255,rgb:0.19607843137254902,0.19607843137254902,0.19607843137254902,1" fontItalic="0" allowHtml="0" fontWordSpacing="0" fontStrikeout="0" fontFamily="Arial" fontUnderline="0" fontSize="10" forcedBold="0" fontSizeMapUnitScale="3x:0,0,0,0,0,0" isExpression="1">
            <families/>
            <text-buffer bufferJoinStyle="128" bufferDraw="0" bufferBlendMode="0" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferColor="250,250,250,255,rgb:0.98039215686274506,0.98039215686274506,0.98039215686274506,1" bufferSize="1" bufferSizeUnits="MM" bufferOpacity="1" bufferNoFill="1"/>
            <text-mask maskedSymbolLayers="" maskOpacity="1" maskSizeUnits="MM" maskJoinStyle="128" maskSize="1.5" maskType="0" maskEnabled="0" maskSize2="1.5" maskSizeMapUnitScale="3x:0,0,0,0,0,0"/>
            <background shapeBorderWidth="0" shapeBorderWidthUnit="Point" shapeType="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeJoinStyle="64" shapeSizeX="0" shapeRadiiUnit="Point" shapeRadiiY="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiX="0" shapeOffsetX="0" shapeDraw="0" shapeSVGFile="" shapeSizeY="0" shapeOffsetUnit="Point" shapeBlendMode="0" shapeRotationType="0" shapeBorderColor="128,128,128,255,rgb:0.50196078431372548,0.50196078431372548,0.50196078431372548,1" shapeOffsetY="0" shapeSizeUnit="Point" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeFillColor="255,255,255,255,rgb:1,1,1,1" shapeRotation="0" shapeSizeType="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeOpacity="1">
              <symbol alpha="1" frame_rate="10" type="marker" force_rhr="0" clip_to_extent="1" is_animated="0" name="markerSymbol">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleMarker" id="" enabled="1">
                  <Option type="Map">
                    <Option value="0" type="QString" name="angle"/>
                    <Option value="square" type="QString" name="cap_style"/>
                    <Option value="141,90,153,255,rgb:0.55294117647058827,0.35294117647058826,0.59999999999999998,1" type="QString" name="color"/>
                    <Option value="1" type="QString" name="horizontal_anchor_point"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="circle" type="QString" name="name"/>
                    <Option value="0,0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="MM" type="QString" name="offset_unit"/>
                    <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="outline_color"/>
                    <Option value="solid" type="QString" name="outline_style"/>
                    <Option value="0" type="QString" name="outline_width"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="outline_width_map_unit_scale"/>
                    <Option value="MM" type="QString" name="outline_width_unit"/>
                    <Option value="diameter" type="QString" name="scale_method"/>
                    <Option value="2" type="QString" name="size"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="size_map_unit_scale"/>
                    <Option value="MM" type="QString" name="size_unit"/>
                    <Option value="1" type="QString" name="vertical_anchor_point"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
              <symbol alpha="1" frame_rate="10" type="fill" force_rhr="0" clip_to_extent="1" is_animated="0" name="fillSymbol">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleFill" id="" enabled="1">
                  <Option type="Map">
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/>
                    <Option value="255,255,255,255,rgb:1,1,1,1" type="QString" name="color"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="0,0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="MM" type="QString" name="offset_unit"/>
                    <Option value="128,128,128,255,rgb:0.50196078431372548,0.50196078431372548,0.50196078431372548,1" type="QString" name="outline_color"/>
                    <Option value="no" type="QString" name="outline_style"/>
                    <Option value="0" type="QString" name="outline_width"/>
                    <Option value="Point" type="QString" name="outline_width_unit"/>
                    <Option value="solid" type="QString" name="style"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowDraw="0" shadowUnder="0" shadowRadiusUnit="MM" shadowOpacity="0.69999999999999996" shadowOffsetAngle="135" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetGlobal="1" shadowScale="100" shadowOffsetUnit="MM" shadowRadius="1.5" shadowColor="0,0,0,255,rgb:0,0,0,1" shadowOffsetDist="1" shadowBlendMode="6" shadowRadiusAlphaOnly="0"/>
            <dd_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format multilineAlign="0" leftDirectionSymbol="&lt;" autoWrapLength="0" placeDirectionSymbol="0" reverseDirectionSymbol="0" plussign="0" addDirectionSymbol="0" wrapChar="" decimals="3" formatNumbers="0" rightDirectionSymbol=">" useMaxLineLengthForAutoWrap="1"/>
          <placement maximumDistanceMapUnitScale="3x:0,0,0,0,0,0" overrunDistanceUnit="MM" fitInPolygonOnly="0" offsetType="0" rotationAngle="0" priority="5" geometryGeneratorType="PointGeometry" polygonPlacementFlags="2" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" xOffset="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" placementFlags="10" centroidWhole="0" distUnits="Point" lineAnchorClipping="0" lineAnchorTextPoint="FollowPlacement" offsetUnits="MM" placement="2" yOffset="0" centroidInside="0" repeatDistance="100" distMapUnitScale="3x:0,0,0,0,0,0" maximumDistance="0" quadOffset="4" layerType="LineGeometry" maximumDistanceUnit="MM" preserveRotation="1" rotationUnit="AngleDegrees" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" lineAnchorType="0" dist="-6" overlapHandling="PreventOverlap" lineAnchorPercent="0.5" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" overrunDistance="0" maxCurvedCharAngleOut="-25" prioritization="PreferCloser" geometryGenerator="" repeatDistanceUnits="Point" maxCurvedCharAngleIn="25" allowDegraded="0" geometryGeneratorEnabled="0"/>
          <rendering mergeLines="0" fontLimitPixelSize="0" fontMinPixelSize="3" labelPerPart="0" obstacleFactor="1" limitNumLabels="0" scaleMin="0" zIndex="0" fontMaxPixelSize="10000" upsidedownLabels="0" minFeatureSize="0" scaleMax="0" obstacle="1" scaleVisibility="0" unplacedVisibility="0" obstacleType="1" maxNumLabels="2000" drawLabels="1"/>
          <dd_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option value="pole_of_inaccessibility" type="QString" name="anchorPoint"/>
              <Option value="0" type="int" name="blendMode"/>
              <Option type="Map" name="ddProperties">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
              <Option value="false" type="bool" name="drawToAllParts"/>
              <Option value="0" type="QString" name="enabled"/>
              <Option value="point_on_exterior" type="QString" name="labelAnchorPoint"/>
              <Option value="&lt;symbol alpha=&quot;1&quot; frame_rate=&quot;10&quot; type=&quot;line&quot; force_rhr=&quot;0&quot; clip_to_extent=&quot;1&quot; is_animated=&quot;0&quot; name=&quot;symbol&quot;>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; type=&quot;QString&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; type=&quot;QString&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;layer locked=&quot;0&quot; pass=&quot;0&quot; class=&quot;SimpleLine&quot; id=&quot;{bdec80e5-7b98-428d-8f73-2f9193e43c18}&quot; enabled=&quot;1&quot;>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;align_dash_pattern&quot;/>&lt;Option value=&quot;square&quot; type=&quot;QString&quot; name=&quot;capstyle&quot;/>&lt;Option value=&quot;5;2&quot; type=&quot;QString&quot; name=&quot;customdash&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;customdash_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;customdash_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;draw_inside_polygon&quot;/>&lt;Option value=&quot;bevel&quot; type=&quot;QString&quot; name=&quot;joinstyle&quot;/>&lt;Option value=&quot;60,60,60,255,rgb:0.23529411764705882,0.23529411764705882,0.23529411764705882,1&quot; type=&quot;QString&quot; name=&quot;line_color&quot;/>&lt;Option value=&quot;solid&quot; type=&quot;QString&quot; name=&quot;line_style&quot;/>&lt;Option value=&quot;0.3&quot; type=&quot;QString&quot; name=&quot;line_width&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;line_width_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;offset&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;offset_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;offset_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;ring_filter&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;trim_distance_end&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;trim_distance_end_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;trim_distance_end_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;trim_distance_start&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;trim_distance_start_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;trim_distance_start_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;use_custom_dash&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;width_map_unit_scale&quot;/>&lt;/Option>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; type=&quot;QString&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; type=&quot;QString&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>" type="QString" name="lineSymbol"/>
              <Option value="0" type="double" name="minLength"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="minLengthMapUnitScale"/>
              <Option value="MM" type="QString" name="minLengthUnit"/>
              <Option value="0" type="double" name="offsetFromAnchor"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="offsetFromAnchorMapUnitScale"/>
              <Option value="MM" type="QString" name="offsetFromAnchorUnit"/>
              <Option value="0" type="double" name="offsetFromLabel"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="offsetFromLabelMapUnitScale"/>
              <Option value="MM" type="QString" name="offsetFromLabelUnit"/>
            </Option>
          </callout>
        </settings>
      </rule>
      <rule description="Sähkölinja, vesijohto, kaasulinja" key="{b59bcfc9-0a0a-4181-84b7-96c8647635ec}" filter="(&#xd;&#xa;array_sort(map_akeys(&quot;type_regulations&quot;)) = array('sahkolinja')&#xd;&#xa;AND array_length(map_akeys(map_get(&quot;type_regulations&quot;, 'sahkolinja'))) = 0&#xd;&#xa;)&#xd;&#xa;OR&#xd;&#xa;(&#xd;&#xa;array_sort(map_akeys(&quot;type_regulations&quot;)) = array('vesijohtoTaiViemari')&#xd;&#xa;AND array_length(map_akeys(map_get(&quot;type_regulations&quot;, 'vesijohtoTaiViemari'))) = 0&#xd;&#xa;)&#xd;&#xa;OR&#xd;&#xa;(&#xd;&#xa;array_sort(map_akeys(&quot;type_regulations&quot;)) = array('kaasulinja')&#xd;&#xa;AND array_length(map_akeys(map_get(&quot;type_regulations&quot;, 'kaasulinja'))) = 0&#xd;&#xa;)">
        <settings calloutType="simple">
          <text-style fontLetterSpacing="0" tabStopDistance="80" multilineHeightUnit="Percentage" fieldName="array_to_string(&quot;short_names&quot;, '/')" useSubstitutions="0" textOrientation="horizontal" capitalization="0" textOpacity="1" tabStopDistanceUnit="Point" multilineHeight="1" forcedItalic="0" tabStopDistanceMapUnitScale="3x:0,0,0,0,0,0" namedStyle="Lihavoitu" previewBkgrdColor="255,255,255,255,rgb:1,1,1,1" fontSizeUnit="Point" fontKerning="1" blendMode="0" fontWeight="75" legendString="Aa" textColor="50,50,50,255,rgb:0.19607843137254902,0.19607843137254902,0.19607843137254902,1" fontItalic="0" allowHtml="0" fontWordSpacing="0" fontStrikeout="0" fontFamily="Arial" fontUnderline="0" fontSize="10" forcedBold="0" fontSizeMapUnitScale="3x:0,0,0,0,0,0" isExpression="1">
            <families/>
            <text-buffer bufferJoinStyle="128" bufferDraw="0" bufferBlendMode="0" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferColor="250,250,250,255,rgb:0.98039215686274506,0.98039215686274506,0.98039215686274506,1" bufferSize="1" bufferSizeUnits="MM" bufferOpacity="1" bufferNoFill="1"/>
            <text-mask maskedSymbolLayers="" maskOpacity="1" maskSizeUnits="MM" maskJoinStyle="128" maskSize="1.5" maskType="0" maskEnabled="0" maskSize2="1.5" maskSizeMapUnitScale="3x:0,0,0,0,0,0"/>
            <background shapeBorderWidth="0.75" shapeBorderWidthUnit="Point" shapeType="3" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeJoinStyle="64" shapeSizeX="0" shapeRadiiUnit="Point" shapeRadiiY="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiX="0" shapeOffsetX="0" shapeDraw="1" shapeSVGFile="" shapeSizeY="0" shapeOffsetUnit="Point" shapeBlendMode="0" shapeRotationType="0" shapeBorderColor="0,0,0,255,rgb:0,0,0,1" shapeOffsetY="0" shapeSizeUnit="Point" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeFillColor="255,255,255,255,rgb:1,1,1,1" shapeRotation="0" shapeSizeType="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeOpacity="1">
              <symbol alpha="1" frame_rate="10" type="marker" force_rhr="0" clip_to_extent="1" is_animated="0" name="markerSymbol">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleMarker" id="" enabled="1">
                  <Option type="Map">
                    <Option value="0" type="QString" name="angle"/>
                    <Option value="square" type="QString" name="cap_style"/>
                    <Option value="183,72,75,255,rgb:0.71764705882352942,0.28235294117647058,0.29411764705882354,1" type="QString" name="color"/>
                    <Option value="1" type="QString" name="horizontal_anchor_point"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="circle" type="QString" name="name"/>
                    <Option value="0,0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="MM" type="QString" name="offset_unit"/>
                    <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="outline_color"/>
                    <Option value="solid" type="QString" name="outline_style"/>
                    <Option value="0" type="QString" name="outline_width"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="outline_width_map_unit_scale"/>
                    <Option value="MM" type="QString" name="outline_width_unit"/>
                    <Option value="diameter" type="QString" name="scale_method"/>
                    <Option value="2" type="QString" name="size"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="size_map_unit_scale"/>
                    <Option value="MM" type="QString" name="size_unit"/>
                    <Option value="1" type="QString" name="vertical_anchor_point"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
              <symbol alpha="1" frame_rate="10" type="fill" force_rhr="0" clip_to_extent="1" is_animated="0" name="fillSymbol">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleFill" id="" enabled="1">
                  <Option type="Map">
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/>
                    <Option value="255,255,255,255,rgb:1,1,1,1" type="QString" name="color"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="0,0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="MM" type="QString" name="offset_unit"/>
                    <Option value="0,0,0,255,rgb:0,0,0,1" type="QString" name="outline_color"/>
                    <Option value="solid" type="QString" name="outline_style"/>
                    <Option value="0.75" type="QString" name="outline_width"/>
                    <Option value="Point" type="QString" name="outline_width_unit"/>
                    <Option value="solid" type="QString" name="style"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowDraw="0" shadowUnder="0" shadowRadiusUnit="MM" shadowOpacity="0.69999999999999996" shadowOffsetAngle="135" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetGlobal="1" shadowScale="100" shadowOffsetUnit="MM" shadowRadius="1.5" shadowColor="0,0,0,255,rgb:0,0,0,1" shadowOffsetDist="1" shadowBlendMode="6" shadowRadiusAlphaOnly="0"/>
            <dd_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format multilineAlign="0" leftDirectionSymbol="&lt;" autoWrapLength="0" placeDirectionSymbol="0" reverseDirectionSymbol="0" plussign="0" addDirectionSymbol="0" wrapChar="" decimals="3" formatNumbers="0" rightDirectionSymbol=">" useMaxLineLengthForAutoWrap="1"/>
          <placement maximumDistanceMapUnitScale="3x:0,0,0,0,0,0" overrunDistanceUnit="MM" fitInPolygonOnly="0" offsetType="0" rotationAngle="0" priority="5" geometryGeneratorType="PointGeometry" polygonPlacementFlags="2" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" xOffset="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" placementFlags="9" centroidWhole="0" distUnits="Point" lineAnchorClipping="0" lineAnchorTextPoint="FollowPlacement" offsetUnits="MM" placement="2" yOffset="0" centroidInside="0" repeatDistance="100" distMapUnitScale="3x:0,0,0,0,0,0" maximumDistance="0" quadOffset="4" layerType="LineGeometry" maximumDistanceUnit="MM" preserveRotation="1" rotationUnit="AngleDegrees" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" lineAnchorType="0" dist="-5" overlapHandling="PreventOverlap" lineAnchorPercent="0.5" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" overrunDistance="0" maxCurvedCharAngleOut="-25" prioritization="PreferCloser" geometryGenerator="" repeatDistanceUnits="Point" maxCurvedCharAngleIn="25" allowDegraded="0" geometryGeneratorEnabled="0"/>
          <rendering mergeLines="0" fontLimitPixelSize="0" fontMinPixelSize="3" labelPerPart="0" obstacleFactor="1" limitNumLabels="0" scaleMin="0" zIndex="0" fontMaxPixelSize="10000" upsidedownLabels="0" minFeatureSize="0" scaleMax="0" obstacle="1" scaleVisibility="0" unplacedVisibility="0" obstacleType="1" maxNumLabels="2000" drawLabels="1"/>
          <dd_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option value="pole_of_inaccessibility" type="QString" name="anchorPoint"/>
              <Option value="0" type="int" name="blendMode"/>
              <Option type="Map" name="ddProperties">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
              <Option value="false" type="bool" name="drawToAllParts"/>
              <Option value="0" type="QString" name="enabled"/>
              <Option value="point_on_exterior" type="QString" name="labelAnchorPoint"/>
              <Option value="&lt;symbol alpha=&quot;1&quot; frame_rate=&quot;10&quot; type=&quot;line&quot; force_rhr=&quot;0&quot; clip_to_extent=&quot;1&quot; is_animated=&quot;0&quot; name=&quot;symbol&quot;>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; type=&quot;QString&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; type=&quot;QString&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;layer locked=&quot;0&quot; pass=&quot;0&quot; class=&quot;SimpleLine&quot; id=&quot;{f3cd6cb4-4d36-49b5-8197-c1483c454a14}&quot; enabled=&quot;1&quot;>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;align_dash_pattern&quot;/>&lt;Option value=&quot;square&quot; type=&quot;QString&quot; name=&quot;capstyle&quot;/>&lt;Option value=&quot;5;2&quot; type=&quot;QString&quot; name=&quot;customdash&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;customdash_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;customdash_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;draw_inside_polygon&quot;/>&lt;Option value=&quot;bevel&quot; type=&quot;QString&quot; name=&quot;joinstyle&quot;/>&lt;Option value=&quot;60,60,60,255,rgb:0.23529411764705882,0.23529411764705882,0.23529411764705882,1&quot; type=&quot;QString&quot; name=&quot;line_color&quot;/>&lt;Option value=&quot;solid&quot; type=&quot;QString&quot; name=&quot;line_style&quot;/>&lt;Option value=&quot;0.3&quot; type=&quot;QString&quot; name=&quot;line_width&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;line_width_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;offset&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;offset_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;offset_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;ring_filter&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;trim_distance_end&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;trim_distance_end_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;trim_distance_end_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;trim_distance_start&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;trim_distance_start_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;trim_distance_start_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;use_custom_dash&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;width_map_unit_scale&quot;/>&lt;/Option>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; type=&quot;QString&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; type=&quot;QString&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>" type="QString" name="lineSymbol"/>
              <Option value="0" type="double" name="minLength"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="minLengthMapUnitScale"/>
              <Option value="MM" type="QString" name="minLengthUnit"/>
              <Option value="0" type="double" name="offsetFromAnchor"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="offsetFromAnchorMapUnitScale"/>
              <Option value="MM" type="QString" name="offsetFromAnchorUnit"/>
              <Option value="0" type="double" name="offsetFromLabel"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="offsetFromLabelMapUnitScale"/>
              <Option value="MM" type="QString" name="offsetFromLabelUnit"/>
            </Option>
          </callout>
        </settings>
      </rule>
      <rule description="Uusi/yhteystarve sähkölinja, kaasulinja tai vesijohto" key="{e17cc1b0-08bd-49ba-baf0-3ad7f49f7b6a}" filter="(&#xa;    map_akeys(&quot;type_regulations&quot;) = array('sahkolinja')&#xa;    AND&#xa;    (&#xa;        map_akeys(map_get(&quot;type_regulations&quot;, 'sahkolinja')) = array('uusi')&#xa;        OR&#xa;        map_akeys(map_get(&quot;type_regulations&quot;, 'sahkolinja')) = array('yhteystarve')&#xa;    )&#xa;)&#xa;OR&#xa;(&#xa;    map_akeys(&quot;type_regulations&quot;) = array('vesijohtoTaiViemari')&#xa;    AND&#xa;&#x9;(&#xa;&#x9;&#x9;map_akeys(map_get(&quot;type_regulations&quot;, 'vesijohtoTaiViemari')) = array('uusi')&#xa;&#x9;&#x9;OR&#xa;&#x9;&#x9;map_akeys(map_get(&quot;type_regulations&quot;, 'vesijohtoTaiViemari')) = array('yhteystarve')&#xa;&#x9;)&#xa;)&#xa;OR&#xa;(&#xa;    map_akeys(&quot;type_regulations&quot;) = array('kaasulinja')&#xa;    AND&#xa;&#x9;(&#xa;&#x9;&#x9;map_akeys(map_get(&quot;type_regulations&quot;, 'kaasulinja')) = array('uusi')&#xa;&#x9;&#x9;OR&#xa;&#x9;&#x9;map_akeys(map_get(&quot;type_regulations&quot;, 'kaasulinja')) = array('yhteystarve')&#xa;&#x9;)&#xa;)">
        <settings calloutType="simple">
          <text-style fontLetterSpacing="0" tabStopDistance="80" multilineHeightUnit="Percentage" fieldName="array_to_string(&quot;short_names&quot;, '/')" useSubstitutions="0" textOrientation="horizontal" capitalization="0" textOpacity="1" tabStopDistanceUnit="Point" multilineHeight="1" forcedItalic="0" tabStopDistanceMapUnitScale="3x:0,0,0,0,0,0" namedStyle="Lihavoitu" previewBkgrdColor="255,255,255,255,rgb:1,1,1,1" fontSizeUnit="Point" fontKerning="1" blendMode="0" fontWeight="75" legendString="Aa" textColor="229,31,45,255,rgb:0.89803921568627454,0.12156862745098039,0.17647058823529413,1" fontItalic="0" allowHtml="0" fontWordSpacing="0" fontStrikeout="0" fontFamily="Arial" fontUnderline="0" fontSize="10" forcedBold="0" fontSizeMapUnitScale="3x:0,0,0,0,0,0" isExpression="1">
            <families/>
            <text-buffer bufferJoinStyle="128" bufferDraw="0" bufferBlendMode="0" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferColor="250,250,250,255,rgb:0.98039215686274506,0.98039215686274506,0.98039215686274506,1" bufferSize="1" bufferSizeUnits="MM" bufferOpacity="1" bufferNoFill="1"/>
            <text-mask maskedSymbolLayers="" maskOpacity="1" maskSizeUnits="MM" maskJoinStyle="128" maskSize="1.5" maskType="0" maskEnabled="0" maskSize2="1.5" maskSizeMapUnitScale="3x:0,0,0,0,0,0"/>
            <background shapeBorderWidth="0.75" shapeBorderWidthUnit="Point" shapeType="3" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeJoinStyle="64" shapeSizeX="0" shapeRadiiUnit="Point" shapeRadiiY="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiX="0" shapeOffsetX="0" shapeDraw="1" shapeSVGFile="" shapeSizeY="0" shapeOffsetUnit="Point" shapeBlendMode="0" shapeRotationType="0" shapeBorderColor="229,31,45,255,rgb:0.89803921568627454,0.12156862745098039,0.17647058823529413,1" shapeOffsetY="0" shapeSizeUnit="Point" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeFillColor="255,255,255,255,rgb:1,1,1,1" shapeRotation="0" shapeSizeType="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeOpacity="1">
              <symbol alpha="1" frame_rate="10" type="marker" force_rhr="0" clip_to_extent="1" is_animated="0" name="markerSymbol">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleMarker" id="" enabled="1">
                  <Option type="Map">
                    <Option value="0" type="QString" name="angle"/>
                    <Option value="square" type="QString" name="cap_style"/>
                    <Option value="255,158,23,255,rgb:1,0.61960784313725492,0.09019607843137255,1" type="QString" name="color"/>
                    <Option value="1" type="QString" name="horizontal_anchor_point"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="circle" type="QString" name="name"/>
                    <Option value="0,0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="MM" type="QString" name="offset_unit"/>
                    <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="outline_color"/>
                    <Option value="solid" type="QString" name="outline_style"/>
                    <Option value="0" type="QString" name="outline_width"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="outline_width_map_unit_scale"/>
                    <Option value="MM" type="QString" name="outline_width_unit"/>
                    <Option value="diameter" type="QString" name="scale_method"/>
                    <Option value="2" type="QString" name="size"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="size_map_unit_scale"/>
                    <Option value="MM" type="QString" name="size_unit"/>
                    <Option value="1" type="QString" name="vertical_anchor_point"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
              <symbol alpha="1" frame_rate="10" type="fill" force_rhr="0" clip_to_extent="1" is_animated="0" name="fillSymbol">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleFill" id="" enabled="1">
                  <Option type="Map">
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/>
                    <Option value="255,255,255,255,rgb:1,1,1,1" type="QString" name="color"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="0,0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="MM" type="QString" name="offset_unit"/>
                    <Option value="229,31,45,255,rgb:0.89803921568627454,0.12156862745098039,0.17647058823529413,1" type="QString" name="outline_color"/>
                    <Option value="solid" type="QString" name="outline_style"/>
                    <Option value="0.75" type="QString" name="outline_width"/>
                    <Option value="Point" type="QString" name="outline_width_unit"/>
                    <Option value="solid" type="QString" name="style"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowDraw="0" shadowUnder="0" shadowRadiusUnit="MM" shadowOpacity="0.69999999999999996" shadowOffsetAngle="135" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetGlobal="1" shadowScale="100" shadowOffsetUnit="MM" shadowRadius="1.5" shadowColor="0,0,0,255,rgb:0,0,0,1" shadowOffsetDist="1" shadowBlendMode="6" shadowRadiusAlphaOnly="0"/>
            <dd_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format multilineAlign="0" leftDirectionSymbol="&lt;" autoWrapLength="0" placeDirectionSymbol="0" reverseDirectionSymbol="0" plussign="0" addDirectionSymbol="0" wrapChar="" decimals="3" formatNumbers="0" rightDirectionSymbol=">" useMaxLineLengthForAutoWrap="1"/>
          <placement maximumDistanceMapUnitScale="3x:0,0,0,0,0,0" overrunDistanceUnit="MM" fitInPolygonOnly="0" offsetType="0" rotationAngle="0" priority="5" geometryGeneratorType="PointGeometry" polygonPlacementFlags="2" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" xOffset="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" placementFlags="9" centroidWhole="0" distUnits="MM" lineAnchorClipping="0" lineAnchorTextPoint="FollowPlacement" offsetUnits="MM" placement="2" yOffset="0" centroidInside="0" repeatDistance="100" distMapUnitScale="3x:0,0,0,0,0,0" maximumDistance="0" quadOffset="4" layerType="LineGeometry" maximumDistanceUnit="MM" preserveRotation="1" rotationUnit="AngleDegrees" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" lineAnchorType="0" dist="0" overlapHandling="PreventOverlap" lineAnchorPercent="0.5" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" overrunDistance="0" maxCurvedCharAngleOut="-25" prioritization="PreferCloser" geometryGenerator="" repeatDistanceUnits="Point" maxCurvedCharAngleIn="25" allowDegraded="0" geometryGeneratorEnabled="0"/>
          <rendering mergeLines="0" fontLimitPixelSize="0" fontMinPixelSize="3" labelPerPart="0" obstacleFactor="1" limitNumLabels="0" scaleMin="0" zIndex="0" fontMaxPixelSize="10000" upsidedownLabels="0" minFeatureSize="0" scaleMax="0" obstacle="1" scaleVisibility="0" unplacedVisibility="0" obstacleType="1" maxNumLabels="2000" drawLabels="1"/>
          <dd_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option value="pole_of_inaccessibility" type="QString" name="anchorPoint"/>
              <Option value="0" type="int" name="blendMode"/>
              <Option type="Map" name="ddProperties">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
              <Option value="false" type="bool" name="drawToAllParts"/>
              <Option value="0" type="QString" name="enabled"/>
              <Option value="point_on_exterior" type="QString" name="labelAnchorPoint"/>
              <Option value="&lt;symbol alpha=&quot;1&quot; frame_rate=&quot;10&quot; type=&quot;line&quot; force_rhr=&quot;0&quot; clip_to_extent=&quot;1&quot; is_animated=&quot;0&quot; name=&quot;symbol&quot;>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; type=&quot;QString&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; type=&quot;QString&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;layer locked=&quot;0&quot; pass=&quot;0&quot; class=&quot;SimpleLine&quot; id=&quot;{e0161c43-c9d4-4862-8f31-0efb003d8405}&quot; enabled=&quot;1&quot;>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;align_dash_pattern&quot;/>&lt;Option value=&quot;square&quot; type=&quot;QString&quot; name=&quot;capstyle&quot;/>&lt;Option value=&quot;5;2&quot; type=&quot;QString&quot; name=&quot;customdash&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;customdash_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;customdash_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;draw_inside_polygon&quot;/>&lt;Option value=&quot;bevel&quot; type=&quot;QString&quot; name=&quot;joinstyle&quot;/>&lt;Option value=&quot;60,60,60,255,rgb:0.23529411764705882,0.23529411764705882,0.23529411764705882,1&quot; type=&quot;QString&quot; name=&quot;line_color&quot;/>&lt;Option value=&quot;solid&quot; type=&quot;QString&quot; name=&quot;line_style&quot;/>&lt;Option value=&quot;0.3&quot; type=&quot;QString&quot; name=&quot;line_width&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;line_width_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;offset&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;offset_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;offset_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;ring_filter&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;trim_distance_end&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;trim_distance_end_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;trim_distance_end_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;trim_distance_start&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;trim_distance_start_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;trim_distance_start_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;use_custom_dash&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;width_map_unit_scale&quot;/>&lt;/Option>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; type=&quot;QString&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; type=&quot;QString&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>" type="QString" name="lineSymbol"/>
              <Option value="0" type="double" name="minLength"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="minLengthMapUnitScale"/>
              <Option value="MM" type="QString" name="minLengthUnit"/>
              <Option value="0" type="double" name="offsetFromAnchor"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="offsetFromAnchorMapUnitScale"/>
              <Option value="MM" type="QString" name="offsetFromAnchorUnit"/>
              <Option value="0" type="double" name="offsetFromLabel"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="offsetFromLabelMapUnitScale"/>
              <Option value="MM" type="QString" name="offsetFromLabelUnit"/>
            </Option>
          </callout>
        </settings>
      </rule>
      <rule description="Valtakunnallisesti merkittävä rakennettu kulttuuriympäristö" key="{c8842d97-f3f6-4d74-ab4b-47463912add9}" filter="map_exist(&#xd;&#xa;  &quot;type_regulations&quot;,&#xd;&#xa;  'merkittavaRakennettuKulttuuriymparisto'&#xd;&#xa;)&#xd;&#xa;AND  array_contains(map_akeys( map_get(&#xd;&#xa;  &quot;type_regulations&quot;, 'merkittavaRakennettuKulttuuriymparisto')),&#xd;&#xa;  'osaAlue')&#xd;&#xa;AND  array_contains(map_akeys( map_get(&#xd;&#xa;  &quot;type_regulations&quot;, 'merkittavaRakennettuKulttuuriymparisto')),&#xd;&#xa;  'valtakunnallinen')">
        <settings calloutType="simple">
          <text-style fontLetterSpacing="0" tabStopDistance="80" multilineHeightUnit="Percentage" fieldName="array_to_string(&quot;short_names&quot;, '/')" useSubstitutions="0" textOrientation="horizontal" capitalization="0" textOpacity="1" tabStopDistanceUnit="Point" multilineHeight="1" forcedItalic="0" tabStopDistanceMapUnitScale="3x:0,0,0,0,0,0" namedStyle="Lihavoitu" previewBkgrdColor="255,255,255,255,rgb:1,1,1,1" fontSizeUnit="Point" fontKerning="1" blendMode="0" fontWeight="75" legendString="Aa" textColor="50,50,50,255,rgb:0.19607843137254902,0.19607843137254902,0.19607843137254902,1" fontItalic="0" allowHtml="0" fontWordSpacing="0" fontStrikeout="0" fontFamily="Arial" fontUnderline="0" fontSize="10" forcedBold="0" fontSizeMapUnitScale="3x:0,0,0,0,0,0" isExpression="1">
            <families/>
            <text-buffer bufferJoinStyle="128" bufferDraw="0" bufferBlendMode="0" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferColor="124,217,204,255,rgb:0.48627450980392156,0.85098039215686272,0.80000000000000004,1" bufferSize="10" bufferSizeUnits="Point" bufferOpacity="1" bufferNoFill="1"/>
            <text-mask maskedSymbolLayers="" maskOpacity="1" maskSizeUnits="Point" maskJoinStyle="128" maskSize="15" maskType="0" maskEnabled="0" maskSize2="15" maskSizeMapUnitScale="3x:0,0,0,0,0,0"/>
            <background shapeBorderWidth="1" shapeBorderWidthUnit="Point" shapeType="2" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeJoinStyle="64" shapeSizeX="2" shapeRadiiUnit="Point" shapeRadiiY="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiX="0" shapeOffsetX="0" shapeDraw="1" shapeSVGFile="" shapeSizeY="0" shapeOffsetUnit="Point" shapeBlendMode="0" shapeRotationType="0" shapeBorderColor="111,168,218,255,rgb:0.43529411764705883,0.6588235294117647,0.85490196078431369,1" shapeOffsetY="-1.5" shapeSizeUnit="Point" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeFillColor="255,255,255,51,rgb:1,1,1,0.20000000000000001" shapeRotation="0" shapeSizeType="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeOpacity="1">
              <symbol alpha="1" frame_rate="10" type="marker" force_rhr="0" clip_to_extent="1" is_animated="0" name="markerSymbol">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleMarker" id="" enabled="1">
                  <Option type="Map">
                    <Option value="0" type="QString" name="angle"/>
                    <Option value="square" type="QString" name="cap_style"/>
                    <Option value="133,182,111,255,rgb:0.52156862745098043,0.71372549019607845,0.43529411764705883,1" type="QString" name="color"/>
                    <Option value="1" type="QString" name="horizontal_anchor_point"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="circle" type="QString" name="name"/>
                    <Option value="0,0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="MM" type="QString" name="offset_unit"/>
                    <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="outline_color"/>
                    <Option value="solid" type="QString" name="outline_style"/>
                    <Option value="0" type="QString" name="outline_width"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="outline_width_map_unit_scale"/>
                    <Option value="MM" type="QString" name="outline_width_unit"/>
                    <Option value="diameter" type="QString" name="scale_method"/>
                    <Option value="2" type="QString" name="size"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="size_map_unit_scale"/>
                    <Option value="MM" type="QString" name="size_unit"/>
                    <Option value="1" type="QString" name="vertical_anchor_point"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
              <symbol alpha="1" frame_rate="10" type="fill" force_rhr="0" clip_to_extent="1" is_animated="0" name="fillSymbol">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleFill" id="" enabled="1">
                  <Option type="Map">
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/>
                    <Option value="255,255,255,51,rgb:1,1,1,0.20000000000000001" type="QString" name="color"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="0,0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="MM" type="QString" name="offset_unit"/>
                    <Option value="111,168,218,255,rgb:0.43529411764705883,0.6588235294117647,0.85490196078431369,1" type="QString" name="outline_color"/>
                    <Option value="solid" type="QString" name="outline_style"/>
                    <Option value="1" type="QString" name="outline_width"/>
                    <Option value="Point" type="QString" name="outline_width_unit"/>
                    <Option value="solid" type="QString" name="style"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowDraw="0" shadowUnder="0" shadowRadiusUnit="MM" shadowOpacity="0.69999999999999996" shadowOffsetAngle="135" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetGlobal="1" shadowScale="100" shadowOffsetUnit="MM" shadowRadius="1.5" shadowColor="0,0,0,255,rgb:0,0,0,1" shadowOffsetDist="1" shadowBlendMode="6" shadowRadiusAlphaOnly="0"/>
            <dd_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format multilineAlign="0" leftDirectionSymbol="&lt;" autoWrapLength="0" placeDirectionSymbol="0" reverseDirectionSymbol="0" plussign="0" addDirectionSymbol="0" wrapChar="" decimals="3" formatNumbers="0" rightDirectionSymbol=">" useMaxLineLengthForAutoWrap="1"/>
          <placement maximumDistanceMapUnitScale="3x:0,0,0,0,0,0" overrunDistanceUnit="MM" fitInPolygonOnly="0" offsetType="0" rotationAngle="0" priority="5" geometryGeneratorType="PointGeometry" polygonPlacementFlags="2" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" xOffset="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" placementFlags="10" centroidWhole="0" distUnits="Point" lineAnchorClipping="0" lineAnchorTextPoint="FollowPlacement" offsetUnits="MM" placement="2" yOffset="0" centroidInside="0" repeatDistance="100" distMapUnitScale="3x:0,0,0,0,0,0" maximumDistance="0" quadOffset="4" layerType="LineGeometry" maximumDistanceUnit="MM" preserveRotation="1" rotationUnit="AngleDegrees" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" lineAnchorType="0" dist="2" overlapHandling="PreventOverlap" lineAnchorPercent="0.5" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" overrunDistance="0" maxCurvedCharAngleOut="-25" prioritization="PreferCloser" geometryGenerator="" repeatDistanceUnits="Point" maxCurvedCharAngleIn="25" allowDegraded="0" geometryGeneratorEnabled="0"/>
          <rendering mergeLines="0" fontLimitPixelSize="0" fontMinPixelSize="3" labelPerPart="0" obstacleFactor="1" limitNumLabels="0" scaleMin="0" zIndex="0" fontMaxPixelSize="10000" upsidedownLabels="0" minFeatureSize="0" scaleMax="0" obstacle="1" scaleVisibility="0" unplacedVisibility="0" obstacleType="1" maxNumLabels="2000" drawLabels="1"/>
          <dd_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option value="pole_of_inaccessibility" type="QString" name="anchorPoint"/>
              <Option value="0" type="int" name="blendMode"/>
              <Option type="Map" name="ddProperties">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
              <Option value="false" type="bool" name="drawToAllParts"/>
              <Option value="0" type="QString" name="enabled"/>
              <Option value="point_on_exterior" type="QString" name="labelAnchorPoint"/>
              <Option value="&lt;symbol alpha=&quot;1&quot; frame_rate=&quot;10&quot; type=&quot;line&quot; force_rhr=&quot;0&quot; clip_to_extent=&quot;1&quot; is_animated=&quot;0&quot; name=&quot;symbol&quot;>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; type=&quot;QString&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; type=&quot;QString&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;layer locked=&quot;0&quot; pass=&quot;0&quot; class=&quot;SimpleLine&quot; id=&quot;{bbd4a37a-a256-427c-9ba4-a5e720e7120b}&quot; enabled=&quot;1&quot;>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;align_dash_pattern&quot;/>&lt;Option value=&quot;square&quot; type=&quot;QString&quot; name=&quot;capstyle&quot;/>&lt;Option value=&quot;5;2&quot; type=&quot;QString&quot; name=&quot;customdash&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;customdash_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;customdash_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;draw_inside_polygon&quot;/>&lt;Option value=&quot;bevel&quot; type=&quot;QString&quot; name=&quot;joinstyle&quot;/>&lt;Option value=&quot;60,60,60,255,rgb:0.23529411764705882,0.23529411764705882,0.23529411764705882,1&quot; type=&quot;QString&quot; name=&quot;line_color&quot;/>&lt;Option value=&quot;solid&quot; type=&quot;QString&quot; name=&quot;line_style&quot;/>&lt;Option value=&quot;0.3&quot; type=&quot;QString&quot; name=&quot;line_width&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;line_width_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;offset&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;offset_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;offset_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;ring_filter&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;trim_distance_end&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;trim_distance_end_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;trim_distance_end_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;trim_distance_start&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;trim_distance_start_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;trim_distance_start_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;use_custom_dash&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;width_map_unit_scale&quot;/>&lt;/Option>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; type=&quot;QString&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; type=&quot;QString&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>" type="QString" name="lineSymbol"/>
              <Option value="0" type="double" name="minLength"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="minLengthMapUnitScale"/>
              <Option value="MM" type="QString" name="minLengthUnit"/>
              <Option value="0" type="double" name="offsetFromAnchor"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="offsetFromAnchorMapUnitScale"/>
              <Option value="MM" type="QString" name="offsetFromAnchorUnit"/>
              <Option value="0" type="double" name="offsetFromLabel"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="offsetFromLabelMapUnitScale"/>
              <Option value="MM" type="QString" name="offsetFromLabelUnit"/>
            </Option>
          </callout>
        </settings>
      </rule>
      <rule description="Natura 2000" key="{9bd1b358-1195-4ce0-9a26-81dd45eb3ea8}" filter="map_exist(&#xd;&#xa;  &quot;type_regulations&quot;,&#xd;&#xa;  'natura2000VerkostonAlue'&#xd;&#xa;)&#xd;&#xa;AND map_exist(&#xd;&#xa;  &quot;type_regulations&quot;['natura2000VerkostonAlue'],&#xd;&#xa;  'osaAlue'&#xd;&#xa;)">
        <settings calloutType="simple">
          <text-style fontLetterSpacing="0" tabStopDistance="80" multilineHeightUnit="Percentage" fieldName="array_to_string(&quot;short_names&quot;, '/')" useSubstitutions="0" textOrientation="horizontal" capitalization="0" textOpacity="1" tabStopDistanceUnit="Point" multilineHeight="1" forcedItalic="0" tabStopDistanceMapUnitScale="3x:0,0,0,0,0,0" namedStyle="Lihavoitu" previewBkgrdColor="255,255,255,255,rgb:1,1,1,1" fontSizeUnit="Point" fontKerning="1" blendMode="0" fontWeight="75" legendString="Aa" textColor="0,0,0,255,hsv:0,0,0,1" fontItalic="0" allowHtml="0" fontWordSpacing="0" fontStrikeout="0" fontFamily="Arial" fontUnderline="0" fontSize="10" forcedBold="0" fontSizeMapUnitScale="3x:0,0,0,0,0,0" isExpression="1">
            <families/>
            <text-buffer bufferJoinStyle="128" bufferDraw="0" bufferBlendMode="0" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferColor="250,250,250,255,rgb:0.98039215686274506,0.98039215686274506,0.98039215686274506,1" bufferSize="1" bufferSizeUnits="MM" bufferOpacity="1" bufferNoFill="1"/>
            <text-mask maskedSymbolLayers="" maskOpacity="1" maskSizeUnits="MM" maskJoinStyle="128" maskSize="1.5" maskType="0" maskEnabled="0" maskSize2="1.5" maskSizeMapUnitScale="3x:0,0,0,0,0,0"/>
            <background shapeBorderWidth="1" shapeBorderWidthUnit="Point" shapeType="2" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeJoinStyle="64" shapeSizeX="2" shapeRadiiUnit="Point" shapeRadiiY="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiX="0" shapeOffsetX="0" shapeDraw="1" shapeSVGFile="" shapeSizeY="0" shapeOffsetUnit="Point" shapeBlendMode="0" shapeRotationType="0" shapeBorderColor="128,128,128,131,rgb:0.50196078431372548,0.50196078431372548,0.50196078431372548,0.51372549019607838" shapeOffsetY="-1.5" shapeSizeUnit="Point" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeFillColor="255,255,255,51,rgb:1,1,1,0.20000000000000001" shapeRotation="0" shapeSizeType="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeOpacity="1">
              <symbol alpha="1" frame_rate="10" type="marker" force_rhr="0" clip_to_extent="1" is_animated="0" name="markerSymbol">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleMarker" id="" enabled="1">
                  <Option type="Map">
                    <Option value="0" type="QString" name="angle"/>
                    <Option value="square" type="QString" name="cap_style"/>
                    <Option value="229,182,54,255,rgb:0.89803921568627454,0.71372549019607845,0.21176470588235294,1" type="QString" name="color"/>
                    <Option value="1" type="QString" name="horizontal_anchor_point"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="circle" type="QString" name="name"/>
                    <Option value="0,0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="MM" type="QString" name="offset_unit"/>
                    <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="outline_color"/>
                    <Option value="solid" type="QString" name="outline_style"/>
                    <Option value="0" type="QString" name="outline_width"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="outline_width_map_unit_scale"/>
                    <Option value="MM" type="QString" name="outline_width_unit"/>
                    <Option value="diameter" type="QString" name="scale_method"/>
                    <Option value="2" type="QString" name="size"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="size_map_unit_scale"/>
                    <Option value="MM" type="QString" name="size_unit"/>
                    <Option value="1" type="QString" name="vertical_anchor_point"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
              <symbol alpha="1" frame_rate="10" type="fill" force_rhr="0" clip_to_extent="1" is_animated="0" name="fillSymbol">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleFill" id="" enabled="1">
                  <Option type="Map">
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/>
                    <Option value="255,255,255,51,rgb:1,1,1,0.20000000000000001" type="QString" name="color"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="0,0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="MM" type="QString" name="offset_unit"/>
                    <Option value="128,128,128,131,rgb:0.50196078431372548,0.50196078431372548,0.50196078431372548,0.51372549019607838" type="QString" name="outline_color"/>
                    <Option value="solid" type="QString" name="outline_style"/>
                    <Option value="1" type="QString" name="outline_width"/>
                    <Option value="Point" type="QString" name="outline_width_unit"/>
                    <Option value="solid" type="QString" name="style"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowDraw="0" shadowUnder="0" shadowRadiusUnit="MM" shadowOpacity="0.69999999999999996" shadowOffsetAngle="135" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetGlobal="1" shadowScale="100" shadowOffsetUnit="MM" shadowRadius="1.5" shadowColor="0,0,0,255,rgb:0,0,0,1" shadowOffsetDist="1" shadowBlendMode="6" shadowRadiusAlphaOnly="0"/>
            <dd_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format multilineAlign="0" leftDirectionSymbol="&lt;" autoWrapLength="0" placeDirectionSymbol="0" reverseDirectionSymbol="0" plussign="0" addDirectionSymbol="0" wrapChar="" decimals="3" formatNumbers="0" rightDirectionSymbol=">" useMaxLineLengthForAutoWrap="1"/>
          <placement maximumDistanceMapUnitScale="3x:0,0,0,0,0,0" overrunDistanceUnit="MM" fitInPolygonOnly="0" offsetType="0" rotationAngle="0" priority="5" geometryGeneratorType="PointGeometry" polygonPlacementFlags="2" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" xOffset="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" placementFlags="10" centroidWhole="0" distUnits="Point" lineAnchorClipping="0" lineAnchorTextPoint="FollowPlacement" offsetUnits="MM" placement="2" yOffset="0" centroidInside="0" repeatDistance="100" distMapUnitScale="3x:0,0,0,0,0,0" maximumDistance="0" quadOffset="4" layerType="LineGeometry" maximumDistanceUnit="MM" preserveRotation="1" rotationUnit="AngleDegrees" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" lineAnchorType="0" dist="2" overlapHandling="PreventOverlap" lineAnchorPercent="0.5" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" overrunDistance="0" maxCurvedCharAngleOut="-25" prioritization="PreferCloser" geometryGenerator="" repeatDistanceUnits="Point" maxCurvedCharAngleIn="25" allowDegraded="0" geometryGeneratorEnabled="0"/>
          <rendering mergeLines="0" fontLimitPixelSize="0" fontMinPixelSize="3" labelPerPart="0" obstacleFactor="1" limitNumLabels="0" scaleMin="0" zIndex="0" fontMaxPixelSize="10000" upsidedownLabels="0" minFeatureSize="0" scaleMax="0" obstacle="1" scaleVisibility="0" unplacedVisibility="0" obstacleType="1" maxNumLabels="2000" drawLabels="1"/>
          <dd_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option value="pole_of_inaccessibility" type="QString" name="anchorPoint"/>
              <Option value="0" type="int" name="blendMode"/>
              <Option type="Map" name="ddProperties">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
              <Option value="false" type="bool" name="drawToAllParts"/>
              <Option value="0" type="QString" name="enabled"/>
              <Option value="point_on_exterior" type="QString" name="labelAnchorPoint"/>
              <Option value="&lt;symbol alpha=&quot;1&quot; frame_rate=&quot;10&quot; type=&quot;line&quot; force_rhr=&quot;0&quot; clip_to_extent=&quot;1&quot; is_animated=&quot;0&quot; name=&quot;symbol&quot;>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; type=&quot;QString&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; type=&quot;QString&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;layer locked=&quot;0&quot; pass=&quot;0&quot; class=&quot;SimpleLine&quot; id=&quot;{8c8c7e34-545b-4859-bd2a-5b1daf4a1d9f}&quot; enabled=&quot;1&quot;>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;align_dash_pattern&quot;/>&lt;Option value=&quot;square&quot; type=&quot;QString&quot; name=&quot;capstyle&quot;/>&lt;Option value=&quot;5;2&quot; type=&quot;QString&quot; name=&quot;customdash&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;customdash_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;customdash_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;draw_inside_polygon&quot;/>&lt;Option value=&quot;bevel&quot; type=&quot;QString&quot; name=&quot;joinstyle&quot;/>&lt;Option value=&quot;60,60,60,255,rgb:0.23529411764705882,0.23529411764705882,0.23529411764705882,1&quot; type=&quot;QString&quot; name=&quot;line_color&quot;/>&lt;Option value=&quot;solid&quot; type=&quot;QString&quot; name=&quot;line_style&quot;/>&lt;Option value=&quot;0.3&quot; type=&quot;QString&quot; name=&quot;line_width&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;line_width_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;offset&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;offset_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;offset_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;ring_filter&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;trim_distance_end&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;trim_distance_end_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;trim_distance_end_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;trim_distance_start&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;trim_distance_start_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;trim_distance_start_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;use_custom_dash&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;width_map_unit_scale&quot;/>&lt;/Option>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; type=&quot;QString&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; type=&quot;QString&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>" type="QString" name="lineSymbol"/>
              <Option value="0" type="double" name="minLength"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="minLengthMapUnitScale"/>
              <Option value="MM" type="QString" name="minLengthUnit"/>
              <Option value="0" type="double" name="offsetFromAnchor"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="offsetFromAnchorMapUnitScale"/>
              <Option value="MM" type="QString" name="offsetFromAnchorUnit"/>
              <Option value="0" type="double" name="offsetFromLabel"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="offsetFromLabelMapUnitScale"/>
              <Option value="MM" type="QString" name="offsetFromLabelUnit"/>
            </Option>
          </callout>
        </settings>
      </rule>
      <rule description="Luonnon monimuotoisuuden kannalta erityisen tärkeä alue" key="{5a953ee6-61b9-4cd5-9ec7-f2249102b70a}" filter="map_exist(&#xd;&#xa;  &quot;type_regulations&quot;,&#xd;&#xa;  'luonnonMonimuotoisuudenKannaltaErityisenTarkeaAlue'&#xd;&#xa;)&#xd;&#xa;AND map_exist(&#xd;&#xa;  &quot;type_regulations&quot;['luonnonMonimuotoisuudenKannaltaErityisenTarkeaAlue'],&#xd;&#xa;  'osaAlue'&#xd;&#xa;)">
        <settings calloutType="simple">
          <text-style fontLetterSpacing="0" tabStopDistance="80" multilineHeightUnit="Percentage" fieldName="array_to_string(&quot;short_names&quot;, '/')" useSubstitutions="0" textOrientation="horizontal" capitalization="0" textOpacity="1" tabStopDistanceUnit="Point" multilineHeight="1" forcedItalic="0" tabStopDistanceMapUnitScale="3x:0,0,0,0,0,0" namedStyle="Lihavoitu" previewBkgrdColor="255,255,255,255,rgb:1,1,1,1" fontSizeUnit="Point" fontKerning="1" blendMode="0" fontWeight="75" legendString="Aa" textColor="50,50,50,255,rgb:0.19607843137254902,0.19607843137254902,0.19607843137254902,1" fontItalic="0" allowHtml="0" fontWordSpacing="0" fontStrikeout="0" fontFamily="Arial" fontUnderline="0" fontSize="10" forcedBold="0" fontSizeMapUnitScale="3x:0,0,0,0,0,0" isExpression="1">
            <families/>
            <text-buffer bufferJoinStyle="128" bufferDraw="0" bufferBlendMode="0" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferColor="250,250,250,255,rgb:0.98039215686274506,0.98039215686274506,0.98039215686274506,1" bufferSize="1" bufferSizeUnits="MM" bufferOpacity="1" bufferNoFill="1"/>
            <text-mask maskedSymbolLayers="" maskOpacity="1" maskSizeUnits="MM" maskJoinStyle="128" maskSize="1.5" maskType="0" maskEnabled="0" maskSize2="1.5" maskSizeMapUnitScale="3x:0,0,0,0,0,0"/>
            <background shapeBorderWidth="1" shapeBorderWidthUnit="Point" shapeType="2" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeJoinStyle="64" shapeSizeX="2" shapeRadiiUnit="Point" shapeRadiiY="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiX="0" shapeOffsetX="0" shapeDraw="1" shapeSVGFile="" shapeSizeY="0" shapeOffsetUnit="Point" shapeBlendMode="0" shapeRotationType="0" shapeBorderColor="25,104,64,255,rgb:0.09803921568627451,0.40784313725490196,0.25098039215686274,1" shapeOffsetY="-1.5" shapeSizeUnit="Point" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeFillColor="255,255,255,51,rgb:1,1,1,0.20000000000000001" shapeRotation="0" shapeSizeType="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeOpacity="1">
              <symbol alpha="1" frame_rate="10" type="marker" force_rhr="0" clip_to_extent="1" is_animated="0" name="markerSymbol">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleMarker" id="" enabled="1">
                  <Option type="Map">
                    <Option value="0" type="QString" name="angle"/>
                    <Option value="square" type="QString" name="cap_style"/>
                    <Option value="183,72,75,255,rgb:0.71764705882352942,0.28235294117647058,0.29411764705882354,1" type="QString" name="color"/>
                    <Option value="1" type="QString" name="horizontal_anchor_point"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="circle" type="QString" name="name"/>
                    <Option value="0,0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="MM" type="QString" name="offset_unit"/>
                    <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="outline_color"/>
                    <Option value="solid" type="QString" name="outline_style"/>
                    <Option value="0" type="QString" name="outline_width"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="outline_width_map_unit_scale"/>
                    <Option value="MM" type="QString" name="outline_width_unit"/>
                    <Option value="diameter" type="QString" name="scale_method"/>
                    <Option value="2" type="QString" name="size"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="size_map_unit_scale"/>
                    <Option value="MM" type="QString" name="size_unit"/>
                    <Option value="1" type="QString" name="vertical_anchor_point"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
              <symbol alpha="1" frame_rate="10" type="fill" force_rhr="0" clip_to_extent="1" is_animated="0" name="fillSymbol">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleFill" id="" enabled="1">
                  <Option type="Map">
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/>
                    <Option value="255,255,255,51,rgb:1,1,1,0.20000000000000001" type="QString" name="color"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="0,0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="MM" type="QString" name="offset_unit"/>
                    <Option value="25,104,64,255,rgb:0.09803921568627451,0.40784313725490196,0.25098039215686274,1" type="QString" name="outline_color"/>
                    <Option value="solid" type="QString" name="outline_style"/>
                    <Option value="1" type="QString" name="outline_width"/>
                    <Option value="Point" type="QString" name="outline_width_unit"/>
                    <Option value="solid" type="QString" name="style"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowDraw="0" shadowUnder="0" shadowRadiusUnit="MM" shadowOpacity="0.69999999999999996" shadowOffsetAngle="135" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetGlobal="1" shadowScale="100" shadowOffsetUnit="MM" shadowRadius="1.5" shadowColor="0,0,0,255,rgb:0,0,0,1" shadowOffsetDist="1" shadowBlendMode="6" shadowRadiusAlphaOnly="0"/>
            <dd_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format multilineAlign="0" leftDirectionSymbol="&lt;" autoWrapLength="0" placeDirectionSymbol="0" reverseDirectionSymbol="0" plussign="0" addDirectionSymbol="0" wrapChar="" decimals="3" formatNumbers="0" rightDirectionSymbol=">" useMaxLineLengthForAutoWrap="1"/>
          <placement maximumDistanceMapUnitScale="3x:0,0,0,0,0,0" overrunDistanceUnit="MM" fitInPolygonOnly="0" offsetType="0" rotationAngle="0" priority="5" geometryGeneratorType="PointGeometry" polygonPlacementFlags="2" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" xOffset="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" placementFlags="10" centroidWhole="0" distUnits="Point" lineAnchorClipping="0" lineAnchorTextPoint="FollowPlacement" offsetUnits="MM" placement="2" yOffset="0" centroidInside="0" repeatDistance="100" distMapUnitScale="3x:0,0,0,0,0,0" maximumDistance="0" quadOffset="4" layerType="LineGeometry" maximumDistanceUnit="MM" preserveRotation="1" rotationUnit="AngleDegrees" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" lineAnchorType="0" dist="2" overlapHandling="PreventOverlap" lineAnchorPercent="0.5" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" overrunDistance="0" maxCurvedCharAngleOut="-25" prioritization="PreferCloser" geometryGenerator="" repeatDistanceUnits="Point" maxCurvedCharAngleIn="25" allowDegraded="0" geometryGeneratorEnabled="0"/>
          <rendering mergeLines="0" fontLimitPixelSize="0" fontMinPixelSize="3" labelPerPart="0" obstacleFactor="1" limitNumLabels="0" scaleMin="0" zIndex="0" fontMaxPixelSize="10000" upsidedownLabels="0" minFeatureSize="0" scaleMax="0" obstacle="1" scaleVisibility="0" unplacedVisibility="0" obstacleType="1" maxNumLabels="2000" drawLabels="1"/>
          <dd_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option value="pole_of_inaccessibility" type="QString" name="anchorPoint"/>
              <Option value="0" type="int" name="blendMode"/>
              <Option type="Map" name="ddProperties">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
              <Option value="false" type="bool" name="drawToAllParts"/>
              <Option value="0" type="QString" name="enabled"/>
              <Option value="point_on_exterior" type="QString" name="labelAnchorPoint"/>
              <Option value="&lt;symbol alpha=&quot;1&quot; frame_rate=&quot;10&quot; type=&quot;line&quot; force_rhr=&quot;0&quot; clip_to_extent=&quot;1&quot; is_animated=&quot;0&quot; name=&quot;symbol&quot;>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; type=&quot;QString&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; type=&quot;QString&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;layer locked=&quot;0&quot; pass=&quot;0&quot; class=&quot;SimpleLine&quot; id=&quot;{8a8a75b0-c2d8-4e2e-ab30-7d1be84a0206}&quot; enabled=&quot;1&quot;>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;align_dash_pattern&quot;/>&lt;Option value=&quot;square&quot; type=&quot;QString&quot; name=&quot;capstyle&quot;/>&lt;Option value=&quot;5;2&quot; type=&quot;QString&quot; name=&quot;customdash&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;customdash_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;customdash_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;draw_inside_polygon&quot;/>&lt;Option value=&quot;bevel&quot; type=&quot;QString&quot; name=&quot;joinstyle&quot;/>&lt;Option value=&quot;60,60,60,255,rgb:0.23529411764705882,0.23529411764705882,0.23529411764705882,1&quot; type=&quot;QString&quot; name=&quot;line_color&quot;/>&lt;Option value=&quot;solid&quot; type=&quot;QString&quot; name=&quot;line_style&quot;/>&lt;Option value=&quot;0.3&quot; type=&quot;QString&quot; name=&quot;line_width&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;line_width_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;offset&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;offset_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;offset_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;ring_filter&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;trim_distance_end&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;trim_distance_end_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;trim_distance_end_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;trim_distance_start&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;trim_distance_start_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;trim_distance_start_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;use_custom_dash&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;width_map_unit_scale&quot;/>&lt;/Option>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; type=&quot;QString&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; type=&quot;QString&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>" type="QString" name="lineSymbol"/>
              <Option value="0" type="double" name="minLength"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="minLengthMapUnitScale"/>
              <Option value="MM" type="QString" name="minLengthUnit"/>
              <Option value="0" type="double" name="offsetFromAnchor"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="offsetFromAnchorMapUnitScale"/>
              <Option value="MM" type="QString" name="offsetFromAnchorUnit"/>
              <Option value="0" type="double" name="offsetFromLabel"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="offsetFromLabelMapUnitScale"/>
              <Option value="MM" type="QString" name="offsetFromLabelUnit"/>
            </Option>
          </callout>
        </settings>
      </rule>
      <rule description="Maantie tai katu, Joukkoliikenteelle varattu tie tai katu" key="{9f29d7a2-8d4d-4dd9-97ee-dc97b550a2e1}" filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'maantie')&#xa;AND&#xa;array_contains(map_akeys(&quot;type_regulations&quot;), 'katu')">
        <settings calloutType="simple">
          <text-style fontLetterSpacing="0" tabStopDistance="80" multilineHeightUnit="Percentage" fieldName="array_to_string(&quot;short_names&quot;, '/')" useSubstitutions="0" textOrientation="horizontal" capitalization="0" textOpacity="1" tabStopDistanceUnit="Point" multilineHeight="1" forcedItalic="0" tabStopDistanceMapUnitScale="3x:0,0,0,0,0,0" namedStyle="Lihavoitu" previewBkgrdColor="255,255,255,255,rgb:1,1,1,1" fontSizeUnit="Point" fontKerning="1" blendMode="0" fontWeight="75" legendString="Aa" textColor="50,50,50,255,rgb:0.19607843137254902,0.19607843137254902,0.19607843137254902,1" fontItalic="0" allowHtml="0" fontWordSpacing="0" fontStrikeout="0" fontFamily="Arial" fontUnderline="0" fontSize="10" forcedBold="0" fontSizeMapUnitScale="3x:0,0,0,0,0,0" isExpression="1">
            <families/>
            <text-buffer bufferJoinStyle="128" bufferDraw="0" bufferBlendMode="0" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferColor="250,250,250,255,rgb:0.98039215686274506,0.98039215686274506,0.98039215686274506,1" bufferSize="1" bufferSizeUnits="MM" bufferOpacity="1" bufferNoFill="1"/>
            <text-mask maskedSymbolLayers="" maskOpacity="1" maskSizeUnits="MM" maskJoinStyle="128" maskSize="1.5" maskType="0" maskEnabled="0" maskSize2="1.5" maskSizeMapUnitScale="3x:0,0,0,0,0,0"/>
            <background shapeBorderWidth="0" shapeBorderWidthUnit="Point" shapeType="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeJoinStyle="64" shapeSizeX="0" shapeRadiiUnit="Point" shapeRadiiY="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiX="0" shapeOffsetX="0" shapeDraw="0" shapeSVGFile="" shapeSizeY="0" shapeOffsetUnit="Point" shapeBlendMode="0" shapeRotationType="0" shapeBorderColor="128,128,128,255,rgb:0.50196078431372548,0.50196078431372548,0.50196078431372548,1" shapeOffsetY="0" shapeSizeUnit="Point" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeFillColor="255,255,255,255,rgb:1,1,1,1" shapeRotation="0" shapeSizeType="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeOpacity="1">
              <symbol alpha="1" frame_rate="10" type="marker" force_rhr="0" clip_to_extent="1" is_animated="0" name="markerSymbol">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleMarker" id="" enabled="1">
                  <Option type="Map">
                    <Option value="0" type="QString" name="angle"/>
                    <Option value="square" type="QString" name="cap_style"/>
                    <Option value="141,90,153,255,rgb:0.55294117647058827,0.35294117647058826,0.59999999999999998,1" type="QString" name="color"/>
                    <Option value="1" type="QString" name="horizontal_anchor_point"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="circle" type="QString" name="name"/>
                    <Option value="0,0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="MM" type="QString" name="offset_unit"/>
                    <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="outline_color"/>
                    <Option value="solid" type="QString" name="outline_style"/>
                    <Option value="0" type="QString" name="outline_width"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="outline_width_map_unit_scale"/>
                    <Option value="MM" type="QString" name="outline_width_unit"/>
                    <Option value="diameter" type="QString" name="scale_method"/>
                    <Option value="2" type="QString" name="size"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="size_map_unit_scale"/>
                    <Option value="MM" type="QString" name="size_unit"/>
                    <Option value="1" type="QString" name="vertical_anchor_point"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
              <symbol alpha="1" frame_rate="10" type="fill" force_rhr="0" clip_to_extent="1" is_animated="0" name="fillSymbol">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleFill" id="" enabled="1">
                  <Option type="Map">
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/>
                    <Option value="255,255,255,255,rgb:1,1,1,1" type="QString" name="color"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="0,0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="MM" type="QString" name="offset_unit"/>
                    <Option value="128,128,128,255,rgb:0.50196078431372548,0.50196078431372548,0.50196078431372548,1" type="QString" name="outline_color"/>
                    <Option value="no" type="QString" name="outline_style"/>
                    <Option value="0" type="QString" name="outline_width"/>
                    <Option value="Point" type="QString" name="outline_width_unit"/>
                    <Option value="solid" type="QString" name="style"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowDraw="0" shadowUnder="0" shadowRadiusUnit="MM" shadowOpacity="0.69999999999999996" shadowOffsetAngle="135" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetGlobal="1" shadowScale="100" shadowOffsetUnit="MM" shadowRadius="1.5" shadowColor="0,0,0,255,rgb:0,0,0,1" shadowOffsetDist="1" shadowBlendMode="6" shadowRadiusAlphaOnly="0"/>
            <dd_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format multilineAlign="0" leftDirectionSymbol="&lt;" autoWrapLength="0" placeDirectionSymbol="0" reverseDirectionSymbol="0" plussign="0" addDirectionSymbol="0" wrapChar="" decimals="3" formatNumbers="0" rightDirectionSymbol=">" useMaxLineLengthForAutoWrap="1"/>
          <placement maximumDistanceMapUnitScale="3x:0,0,0,0,0,0" overrunDistanceUnit="MM" fitInPolygonOnly="0" offsetType="0" rotationAngle="0" priority="5" geometryGeneratorType="PointGeometry" polygonPlacementFlags="2" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" xOffset="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" placementFlags="9" centroidWhole="0" distUnits="Point" lineAnchorClipping="0" lineAnchorTextPoint="FollowPlacement" offsetUnits="MM" placement="2" yOffset="0" centroidInside="0" repeatDistance="100" distMapUnitScale="3x:0,0,0,0,0,0" maximumDistance="0" quadOffset="4" layerType="LineGeometry" maximumDistanceUnit="MM" preserveRotation="1" rotationUnit="AngleDegrees" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" lineAnchorType="0" dist="-4" overlapHandling="PreventOverlap" lineAnchorPercent="0.5" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" overrunDistance="0" maxCurvedCharAngleOut="-25" prioritization="PreferCloser" geometryGenerator="" repeatDistanceUnits="Point" maxCurvedCharAngleIn="25" allowDegraded="0" geometryGeneratorEnabled="0"/>
          <rendering mergeLines="0" fontLimitPixelSize="0" fontMinPixelSize="3" labelPerPart="0" obstacleFactor="1" limitNumLabels="0" scaleMin="0" zIndex="0" fontMaxPixelSize="10000" upsidedownLabels="0" minFeatureSize="0" scaleMax="0" obstacle="1" scaleVisibility="0" unplacedVisibility="0" obstacleType="1" maxNumLabels="2000" drawLabels="1"/>
          <dd_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option value="pole_of_inaccessibility" type="QString" name="anchorPoint"/>
              <Option value="0" type="int" name="blendMode"/>
              <Option type="Map" name="ddProperties">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
              <Option value="false" type="bool" name="drawToAllParts"/>
              <Option value="0" type="QString" name="enabled"/>
              <Option value="point_on_exterior" type="QString" name="labelAnchorPoint"/>
              <Option value="&lt;symbol alpha=&quot;1&quot; frame_rate=&quot;10&quot; type=&quot;line&quot; force_rhr=&quot;0&quot; clip_to_extent=&quot;1&quot; is_animated=&quot;0&quot; name=&quot;symbol&quot;>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; type=&quot;QString&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; type=&quot;QString&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;layer locked=&quot;0&quot; pass=&quot;0&quot; class=&quot;SimpleLine&quot; id=&quot;{bdec80e5-7b98-428d-8f73-2f9193e43c18}&quot; enabled=&quot;1&quot;>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;align_dash_pattern&quot;/>&lt;Option value=&quot;square&quot; type=&quot;QString&quot; name=&quot;capstyle&quot;/>&lt;Option value=&quot;5;2&quot; type=&quot;QString&quot; name=&quot;customdash&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;customdash_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;customdash_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;draw_inside_polygon&quot;/>&lt;Option value=&quot;bevel&quot; type=&quot;QString&quot; name=&quot;joinstyle&quot;/>&lt;Option value=&quot;60,60,60,255,rgb:0.23529411764705882,0.23529411764705882,0.23529411764705882,1&quot; type=&quot;QString&quot; name=&quot;line_color&quot;/>&lt;Option value=&quot;solid&quot; type=&quot;QString&quot; name=&quot;line_style&quot;/>&lt;Option value=&quot;0.3&quot; type=&quot;QString&quot; name=&quot;line_width&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;line_width_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;offset&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;offset_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;offset_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;ring_filter&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;trim_distance_end&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;trim_distance_end_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;trim_distance_end_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;trim_distance_start&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;trim_distance_start_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;trim_distance_start_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;use_custom_dash&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;width_map_unit_scale&quot;/>&lt;/Option>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; type=&quot;QString&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; type=&quot;QString&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>" type="QString" name="lineSymbol"/>
              <Option value="0" type="double" name="minLength"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="minLengthMapUnitScale"/>
              <Option value="MM" type="QString" name="minLengthUnit"/>
              <Option value="0" type="double" name="offsetFromAnchor"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="offsetFromAnchorMapUnitScale"/>
              <Option value="MM" type="QString" name="offsetFromAnchorUnit"/>
              <Option value="0" type="double" name="offsetFromLabel"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="offsetFromLabelMapUnitScale"/>
              <Option value="MM" type="QString" name="offsetFromLabelUnit"/>
            </Option>
          </callout>
        </settings>
      </rule>
      <rule description="Maantie" key="{0ed10409-2d66-4b0d-ba99-ca2d00fd2584}" filter="map_akeys(&quot;type_regulations&quot;) = array('maantie')">
        <settings calloutType="simple">
          <text-style fontLetterSpacing="0" tabStopDistance="80" multilineHeightUnit="Percentage" fieldName="array_to_string(&quot;short_names&quot;, '/')" useSubstitutions="0" textOrientation="horizontal" capitalization="0" textOpacity="1" tabStopDistanceUnit="Point" multilineHeight="1" forcedItalic="0" tabStopDistanceMapUnitScale="3x:0,0,0,0,0,0" namedStyle="Lihavoitu" previewBkgrdColor="255,255,255,255,rgb:1,1,1,1" fontSizeUnit="Point" fontKerning="1" blendMode="0" fontWeight="75" legendString="Aa" textColor="50,50,50,255,rgb:0.19607843137254902,0.19607843137254902,0.19607843137254902,1" fontItalic="0" allowHtml="0" fontWordSpacing="0" fontStrikeout="0" fontFamily="Arial" fontUnderline="0" fontSize="10" forcedBold="0" fontSizeMapUnitScale="3x:0,0,0,0,0,0" isExpression="1">
            <families/>
            <text-buffer bufferJoinStyle="128" bufferDraw="0" bufferBlendMode="0" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferColor="250,250,250,255,rgb:0.98039215686274506,0.98039215686274506,0.98039215686274506,1" bufferSize="1" bufferSizeUnits="MM" bufferOpacity="1" bufferNoFill="1"/>
            <text-mask maskedSymbolLayers="" maskOpacity="1" maskSizeUnits="MM" maskJoinStyle="128" maskSize="1.5" maskType="0" maskEnabled="0" maskSize2="1.5" maskSizeMapUnitScale="3x:0,0,0,0,0,0"/>
            <background shapeBorderWidth="0" shapeBorderWidthUnit="Point" shapeType="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeJoinStyle="64" shapeSizeX="0" shapeRadiiUnit="Point" shapeRadiiY="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiX="0" shapeOffsetX="0" shapeDraw="0" shapeSVGFile="" shapeSizeY="0" shapeOffsetUnit="Point" shapeBlendMode="0" shapeRotationType="0" shapeBorderColor="128,128,128,255,rgb:0.50196078431372548,0.50196078431372548,0.50196078431372548,1" shapeOffsetY="0" shapeSizeUnit="Point" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeFillColor="255,255,255,255,rgb:1,1,1,1" shapeRotation="0" shapeSizeType="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeOpacity="1">
              <symbol alpha="1" frame_rate="10" type="marker" force_rhr="0" clip_to_extent="1" is_animated="0" name="markerSymbol">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleMarker" id="" enabled="1">
                  <Option type="Map">
                    <Option value="0" type="QString" name="angle"/>
                    <Option value="square" type="QString" name="cap_style"/>
                    <Option value="141,90,153,255,rgb:0.55294117647058827,0.35294117647058826,0.59999999999999998,1" type="QString" name="color"/>
                    <Option value="1" type="QString" name="horizontal_anchor_point"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="circle" type="QString" name="name"/>
                    <Option value="0,0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="MM" type="QString" name="offset_unit"/>
                    <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="outline_color"/>
                    <Option value="solid" type="QString" name="outline_style"/>
                    <Option value="0" type="QString" name="outline_width"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="outline_width_map_unit_scale"/>
                    <Option value="MM" type="QString" name="outline_width_unit"/>
                    <Option value="diameter" type="QString" name="scale_method"/>
                    <Option value="2" type="QString" name="size"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="size_map_unit_scale"/>
                    <Option value="MM" type="QString" name="size_unit"/>
                    <Option value="1" type="QString" name="vertical_anchor_point"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
              <symbol alpha="1" frame_rate="10" type="fill" force_rhr="0" clip_to_extent="1" is_animated="0" name="fillSymbol">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleFill" id="" enabled="1">
                  <Option type="Map">
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/>
                    <Option value="255,255,255,255,rgb:1,1,1,1" type="QString" name="color"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="0,0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="MM" type="QString" name="offset_unit"/>
                    <Option value="128,128,128,255,rgb:0.50196078431372548,0.50196078431372548,0.50196078431372548,1" type="QString" name="outline_color"/>
                    <Option value="no" type="QString" name="outline_style"/>
                    <Option value="0" type="QString" name="outline_width"/>
                    <Option value="Point" type="QString" name="outline_width_unit"/>
                    <Option value="solid" type="QString" name="style"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowDraw="0" shadowUnder="0" shadowRadiusUnit="MM" shadowOpacity="0.69999999999999996" shadowOffsetAngle="135" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetGlobal="1" shadowScale="100" shadowOffsetUnit="MM" shadowRadius="1.5" shadowColor="0,0,0,255,rgb:0,0,0,1" shadowOffsetDist="1" shadowBlendMode="6" shadowRadiusAlphaOnly="0"/>
            <dd_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format multilineAlign="0" leftDirectionSymbol="&lt;" autoWrapLength="0" placeDirectionSymbol="0" reverseDirectionSymbol="0" plussign="0" addDirectionSymbol="0" wrapChar="" decimals="3" formatNumbers="0" rightDirectionSymbol=">" useMaxLineLengthForAutoWrap="1"/>
          <placement maximumDistanceMapUnitScale="3x:0,0,0,0,0,0" overrunDistanceUnit="MM" fitInPolygonOnly="0" offsetType="0" rotationAngle="0" priority="5" geometryGeneratorType="PointGeometry" polygonPlacementFlags="2" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" xOffset="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" placementFlags="9" centroidWhole="0" distUnits="Point" lineAnchorClipping="0" lineAnchorTextPoint="FollowPlacement" offsetUnits="MM" placement="2" yOffset="0" centroidInside="0" repeatDistance="100" distMapUnitScale="3x:0,0,0,0,0,0" maximumDistance="0" quadOffset="4" layerType="LineGeometry" maximumDistanceUnit="MM" preserveRotation="1" rotationUnit="AngleDegrees" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" lineAnchorType="0" dist="-4" overlapHandling="PreventOverlap" lineAnchorPercent="0.5" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" overrunDistance="0" maxCurvedCharAngleOut="-25" prioritization="PreferCloser" geometryGenerator="" repeatDistanceUnits="Point" maxCurvedCharAngleIn="25" allowDegraded="0" geometryGeneratorEnabled="0"/>
          <rendering mergeLines="0" fontLimitPixelSize="0" fontMinPixelSize="3" labelPerPart="0" obstacleFactor="1" limitNumLabels="0" scaleMin="0" zIndex="0" fontMaxPixelSize="10000" upsidedownLabels="0" minFeatureSize="0" scaleMax="0" obstacle="1" scaleVisibility="0" unplacedVisibility="0" obstacleType="1" maxNumLabels="2000" drawLabels="1"/>
          <dd_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option value="pole_of_inaccessibility" type="QString" name="anchorPoint"/>
              <Option value="0" type="int" name="blendMode"/>
              <Option type="Map" name="ddProperties">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
              <Option value="false" type="bool" name="drawToAllParts"/>
              <Option value="0" type="QString" name="enabled"/>
              <Option value="point_on_exterior" type="QString" name="labelAnchorPoint"/>
              <Option value="&lt;symbol alpha=&quot;1&quot; frame_rate=&quot;10&quot; type=&quot;line&quot; force_rhr=&quot;0&quot; clip_to_extent=&quot;1&quot; is_animated=&quot;0&quot; name=&quot;symbol&quot;>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; type=&quot;QString&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; type=&quot;QString&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;layer locked=&quot;0&quot; pass=&quot;0&quot; class=&quot;SimpleLine&quot; id=&quot;{bdec80e5-7b98-428d-8f73-2f9193e43c18}&quot; enabled=&quot;1&quot;>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;align_dash_pattern&quot;/>&lt;Option value=&quot;square&quot; type=&quot;QString&quot; name=&quot;capstyle&quot;/>&lt;Option value=&quot;5;2&quot; type=&quot;QString&quot; name=&quot;customdash&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;customdash_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;customdash_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;draw_inside_polygon&quot;/>&lt;Option value=&quot;bevel&quot; type=&quot;QString&quot; name=&quot;joinstyle&quot;/>&lt;Option value=&quot;60,60,60,255,rgb:0.23529411764705882,0.23529411764705882,0.23529411764705882,1&quot; type=&quot;QString&quot; name=&quot;line_color&quot;/>&lt;Option value=&quot;solid&quot; type=&quot;QString&quot; name=&quot;line_style&quot;/>&lt;Option value=&quot;0.3&quot; type=&quot;QString&quot; name=&quot;line_width&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;line_width_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;offset&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;offset_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;offset_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;ring_filter&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;trim_distance_end&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;trim_distance_end_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;trim_distance_end_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;trim_distance_start&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;trim_distance_start_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;trim_distance_start_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;use_custom_dash&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;width_map_unit_scale&quot;/>&lt;/Option>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; type=&quot;QString&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; type=&quot;QString&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>" type="QString" name="lineSymbol"/>
              <Option value="0" type="double" name="minLength"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="minLengthMapUnitScale"/>
              <Option value="MM" type="QString" name="minLengthUnit"/>
              <Option value="0" type="double" name="offsetFromAnchor"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="offsetFromAnchorMapUnitScale"/>
              <Option value="MM" type="QString" name="offsetFromAnchorUnit"/>
              <Option value="0" type="double" name="offsetFromLabel"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="offsetFromLabelMapUnitScale"/>
              <Option value="MM" type="QString" name="offsetFromLabelUnit"/>
            </Option>
          </callout>
        </settings>
      </rule>
      <rule description="Katu" key="{7440f759-7ff7-4327-86e7-ce639492bbe2}" filter="map_akeys(&quot;type_regulations&quot;) = array('katu') AND&#xa;NOT array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'katu')), 'kayttotarkoituskohdistus')">
        <settings calloutType="simple">
          <text-style fontLetterSpacing="0" tabStopDistance="80" multilineHeightUnit="Percentage" fieldName="array_to_string(&quot;short_names&quot;, '/')" useSubstitutions="0" textOrientation="horizontal" capitalization="0" textOpacity="1" tabStopDistanceUnit="Point" multilineHeight="1" forcedItalic="0" tabStopDistanceMapUnitScale="3x:0,0,0,0,0,0" namedStyle="Lihavoitu" previewBkgrdColor="255,255,255,255,rgb:1,1,1,1" fontSizeUnit="Point" fontKerning="1" blendMode="0" fontWeight="75" legendString="Aa" textColor="50,50,50,255,rgb:0.19607843137254902,0.19607843137254902,0.19607843137254902,1" fontItalic="0" allowHtml="0" fontWordSpacing="0" fontStrikeout="0" fontFamily="Arial" fontUnderline="0" fontSize="10" forcedBold="0" fontSizeMapUnitScale="3x:0,0,0,0,0,0" isExpression="1">
            <families/>
            <text-buffer bufferJoinStyle="128" bufferDraw="0" bufferBlendMode="0" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferColor="250,250,250,255,rgb:0.98039215686274506,0.98039215686274506,0.98039215686274506,1" bufferSize="1" bufferSizeUnits="MM" bufferOpacity="1" bufferNoFill="1"/>
            <text-mask maskedSymbolLayers="" maskOpacity="1" maskSizeUnits="MM" maskJoinStyle="128" maskSize="1.5" maskType="0" maskEnabled="0" maskSize2="1.5" maskSizeMapUnitScale="3x:0,0,0,0,0,0"/>
            <background shapeBorderWidth="0" shapeBorderWidthUnit="Point" shapeType="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeJoinStyle="64" shapeSizeX="0" shapeRadiiUnit="Point" shapeRadiiY="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiX="0" shapeOffsetX="0" shapeDraw="0" shapeSVGFile="" shapeSizeY="0" shapeOffsetUnit="Point" shapeBlendMode="0" shapeRotationType="0" shapeBorderColor="128,128,128,255,rgb:0.50196078431372548,0.50196078431372548,0.50196078431372548,1" shapeOffsetY="0" shapeSizeUnit="Point" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeFillColor="255,255,255,255,rgb:1,1,1,1" shapeRotation="0" shapeSizeType="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeOpacity="1">
              <symbol alpha="1" frame_rate="10" type="marker" force_rhr="0" clip_to_extent="1" is_animated="0" name="markerSymbol">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleMarker" id="" enabled="1">
                  <Option type="Map">
                    <Option value="0" type="QString" name="angle"/>
                    <Option value="square" type="QString" name="cap_style"/>
                    <Option value="141,90,153,255,rgb:0.55294117647058827,0.35294117647058826,0.59999999999999998,1" type="QString" name="color"/>
                    <Option value="1" type="QString" name="horizontal_anchor_point"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="circle" type="QString" name="name"/>
                    <Option value="0,0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="MM" type="QString" name="offset_unit"/>
                    <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="outline_color"/>
                    <Option value="solid" type="QString" name="outline_style"/>
                    <Option value="0" type="QString" name="outline_width"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="outline_width_map_unit_scale"/>
                    <Option value="MM" type="QString" name="outline_width_unit"/>
                    <Option value="diameter" type="QString" name="scale_method"/>
                    <Option value="2" type="QString" name="size"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="size_map_unit_scale"/>
                    <Option value="MM" type="QString" name="size_unit"/>
                    <Option value="1" type="QString" name="vertical_anchor_point"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
              <symbol alpha="1" frame_rate="10" type="fill" force_rhr="0" clip_to_extent="1" is_animated="0" name="fillSymbol">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleFill" id="" enabled="1">
                  <Option type="Map">
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/>
                    <Option value="255,255,255,255,rgb:1,1,1,1" type="QString" name="color"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="0,0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="MM" type="QString" name="offset_unit"/>
                    <Option value="128,128,128,255,rgb:0.50196078431372548,0.50196078431372548,0.50196078431372548,1" type="QString" name="outline_color"/>
                    <Option value="no" type="QString" name="outline_style"/>
                    <Option value="0" type="QString" name="outline_width"/>
                    <Option value="Point" type="QString" name="outline_width_unit"/>
                    <Option value="solid" type="QString" name="style"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowDraw="0" shadowUnder="0" shadowRadiusUnit="MM" shadowOpacity="0.69999999999999996" shadowOffsetAngle="135" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetGlobal="1" shadowScale="100" shadowOffsetUnit="MM" shadowRadius="1.5" shadowColor="0,0,0,255,rgb:0,0,0,1" shadowOffsetDist="1" shadowBlendMode="6" shadowRadiusAlphaOnly="0"/>
            <dd_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format multilineAlign="0" leftDirectionSymbol="&lt;" autoWrapLength="0" placeDirectionSymbol="0" reverseDirectionSymbol="0" plussign="0" addDirectionSymbol="0" wrapChar="" decimals="3" formatNumbers="0" rightDirectionSymbol=">" useMaxLineLengthForAutoWrap="1"/>
          <placement maximumDistanceMapUnitScale="3x:0,0,0,0,0,0" overrunDistanceUnit="MM" fitInPolygonOnly="0" offsetType="0" rotationAngle="0" priority="5" geometryGeneratorType="PointGeometry" polygonPlacementFlags="2" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" xOffset="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" placementFlags="9" centroidWhole="0" distUnits="Point" lineAnchorClipping="0" lineAnchorTextPoint="FollowPlacement" offsetUnits="MM" placement="2" yOffset="0" centroidInside="0" repeatDistance="100" distMapUnitScale="3x:0,0,0,0,0,0" maximumDistance="0" quadOffset="4" layerType="LineGeometry" maximumDistanceUnit="MM" preserveRotation="1" rotationUnit="AngleDegrees" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" lineAnchorType="0" dist="-4" overlapHandling="PreventOverlap" lineAnchorPercent="0.5" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" overrunDistance="0" maxCurvedCharAngleOut="-25" prioritization="PreferCloser" geometryGenerator="" repeatDistanceUnits="Point" maxCurvedCharAngleIn="25" allowDegraded="0" geometryGeneratorEnabled="0"/>
          <rendering mergeLines="0" fontLimitPixelSize="0" fontMinPixelSize="3" labelPerPart="0" obstacleFactor="1" limitNumLabels="0" scaleMin="0" zIndex="0" fontMaxPixelSize="10000" upsidedownLabels="0" minFeatureSize="0" scaleMax="0" obstacle="1" scaleVisibility="0" unplacedVisibility="0" obstacleType="1" maxNumLabels="2000" drawLabels="1"/>
          <dd_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option value="pole_of_inaccessibility" type="QString" name="anchorPoint"/>
              <Option value="0" type="int" name="blendMode"/>
              <Option type="Map" name="ddProperties">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
              <Option value="false" type="bool" name="drawToAllParts"/>
              <Option value="0" type="QString" name="enabled"/>
              <Option value="point_on_exterior" type="QString" name="labelAnchorPoint"/>
              <Option value="&lt;symbol alpha=&quot;1&quot; frame_rate=&quot;10&quot; type=&quot;line&quot; force_rhr=&quot;0&quot; clip_to_extent=&quot;1&quot; is_animated=&quot;0&quot; name=&quot;symbol&quot;>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; type=&quot;QString&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; type=&quot;QString&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;layer locked=&quot;0&quot; pass=&quot;0&quot; class=&quot;SimpleLine&quot; id=&quot;{bdec80e5-7b98-428d-8f73-2f9193e43c18}&quot; enabled=&quot;1&quot;>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;align_dash_pattern&quot;/>&lt;Option value=&quot;square&quot; type=&quot;QString&quot; name=&quot;capstyle&quot;/>&lt;Option value=&quot;5;2&quot; type=&quot;QString&quot; name=&quot;customdash&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;customdash_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;customdash_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;draw_inside_polygon&quot;/>&lt;Option value=&quot;bevel&quot; type=&quot;QString&quot; name=&quot;joinstyle&quot;/>&lt;Option value=&quot;60,60,60,255,rgb:0.23529411764705882,0.23529411764705882,0.23529411764705882,1&quot; type=&quot;QString&quot; name=&quot;line_color&quot;/>&lt;Option value=&quot;solid&quot; type=&quot;QString&quot; name=&quot;line_style&quot;/>&lt;Option value=&quot;0.3&quot; type=&quot;QString&quot; name=&quot;line_width&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;line_width_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;offset&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;offset_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;offset_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;ring_filter&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;trim_distance_end&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;trim_distance_end_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;trim_distance_end_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;trim_distance_start&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;trim_distance_start_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;trim_distance_start_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;use_custom_dash&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;width_map_unit_scale&quot;/>&lt;/Option>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; type=&quot;QString&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; type=&quot;QString&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>" type="QString" name="lineSymbol"/>
              <Option value="0" type="double" name="minLength"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="minLengthMapUnitScale"/>
              <Option value="MM" type="QString" name="minLengthUnit"/>
              <Option value="0" type="double" name="offsetFromAnchor"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="offsetFromAnchorMapUnitScale"/>
              <Option value="MM" type="QString" name="offsetFromAnchorUnit"/>
              <Option value="0" type="double" name="offsetFromLabel"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="offsetFromLabelMapUnitScale"/>
              <Option value="MM" type="QString" name="offsetFromLabelUnit"/>
            </Option>
          </callout>
        </settings>
      </rule>
      <rule description="Joukkoliikenteelle varattu katu" key="{1c47aee1-1be8-43df-b813-e03c3ed80133}" filter="map_akeys(&quot;type_regulations&quot;) = array('katu') AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'katu')), 'kayttotarkoituskohdistus')">
        <settings calloutType="simple">
          <text-style fontLetterSpacing="0" tabStopDistance="80" multilineHeightUnit="Percentage" fieldName="array_to_string(&quot;short_names&quot;, '/')" useSubstitutions="0" textOrientation="horizontal" capitalization="0" textOpacity="1" tabStopDistanceUnit="Point" multilineHeight="1" forcedItalic="0" tabStopDistanceMapUnitScale="3x:0,0,0,0,0,0" namedStyle="Lihavoitu" previewBkgrdColor="255,255,255,255,rgb:1,1,1,1" fontSizeUnit="Point" fontKerning="1" blendMode="0" fontWeight="75" legendString="Aa" textColor="50,50,50,255,rgb:0.19607843137254902,0.19607843137254902,0.19607843137254902,1" fontItalic="0" allowHtml="0" fontWordSpacing="0" fontStrikeout="0" fontFamily="Arial" fontUnderline="0" fontSize="10" forcedBold="0" fontSizeMapUnitScale="3x:0,0,0,0,0,0" isExpression="1">
            <families/>
            <text-buffer bufferJoinStyle="128" bufferDraw="0" bufferBlendMode="0" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferColor="250,250,250,255,rgb:0.98039215686274506,0.98039215686274506,0.98039215686274506,1" bufferSize="1" bufferSizeUnits="MM" bufferOpacity="1" bufferNoFill="1"/>
            <text-mask maskedSymbolLayers="" maskOpacity="1" maskSizeUnits="MM" maskJoinStyle="128" maskSize="1.5" maskType="0" maskEnabled="0" maskSize2="1.5" maskSizeMapUnitScale="3x:0,0,0,0,0,0"/>
            <background shapeBorderWidth="0" shapeBorderWidthUnit="Point" shapeType="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeJoinStyle="64" shapeSizeX="0" shapeRadiiUnit="Point" shapeRadiiY="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiX="0" shapeOffsetX="0" shapeDraw="0" shapeSVGFile="" shapeSizeY="0" shapeOffsetUnit="Point" shapeBlendMode="0" shapeRotationType="0" shapeBorderColor="128,128,128,255,rgb:0.50196078431372548,0.50196078431372548,0.50196078431372548,1" shapeOffsetY="0" shapeSizeUnit="Point" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeFillColor="255,255,255,255,rgb:1,1,1,1" shapeRotation="0" shapeSizeType="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeOpacity="1">
              <symbol alpha="1" frame_rate="10" type="marker" force_rhr="0" clip_to_extent="1" is_animated="0" name="markerSymbol">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleMarker" id="" enabled="1">
                  <Option type="Map">
                    <Option value="0" type="QString" name="angle"/>
                    <Option value="square" type="QString" name="cap_style"/>
                    <Option value="141,90,153,255,rgb:0.55294117647058827,0.35294117647058826,0.59999999999999998,1" type="QString" name="color"/>
                    <Option value="1" type="QString" name="horizontal_anchor_point"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="circle" type="QString" name="name"/>
                    <Option value="0,0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="MM" type="QString" name="offset_unit"/>
                    <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="outline_color"/>
                    <Option value="solid" type="QString" name="outline_style"/>
                    <Option value="0" type="QString" name="outline_width"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="outline_width_map_unit_scale"/>
                    <Option value="MM" type="QString" name="outline_width_unit"/>
                    <Option value="diameter" type="QString" name="scale_method"/>
                    <Option value="2" type="QString" name="size"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="size_map_unit_scale"/>
                    <Option value="MM" type="QString" name="size_unit"/>
                    <Option value="1" type="QString" name="vertical_anchor_point"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
              <symbol alpha="1" frame_rate="10" type="fill" force_rhr="0" clip_to_extent="1" is_animated="0" name="fillSymbol">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleFill" id="" enabled="1">
                  <Option type="Map">
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/>
                    <Option value="255,255,255,255,rgb:1,1,1,1" type="QString" name="color"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="0,0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="MM" type="QString" name="offset_unit"/>
                    <Option value="128,128,128,255,rgb:0.50196078431372548,0.50196078431372548,0.50196078431372548,1" type="QString" name="outline_color"/>
                    <Option value="no" type="QString" name="outline_style"/>
                    <Option value="0" type="QString" name="outline_width"/>
                    <Option value="Point" type="QString" name="outline_width_unit"/>
                    <Option value="solid" type="QString" name="style"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowDraw="0" shadowUnder="0" shadowRadiusUnit="MM" shadowOpacity="0.69999999999999996" shadowOffsetAngle="135" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetGlobal="1" shadowScale="100" shadowOffsetUnit="MM" shadowRadius="1.5" shadowColor="0,0,0,255,rgb:0,0,0,1" shadowOffsetDist="1" shadowBlendMode="6" shadowRadiusAlphaOnly="0"/>
            <dd_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format multilineAlign="0" leftDirectionSymbol="&lt;" autoWrapLength="0" placeDirectionSymbol="0" reverseDirectionSymbol="0" plussign="0" addDirectionSymbol="0" wrapChar="" decimals="3" formatNumbers="0" rightDirectionSymbol=">" useMaxLineLengthForAutoWrap="1"/>
          <placement maximumDistanceMapUnitScale="3x:0,0,0,0,0,0" overrunDistanceUnit="MM" fitInPolygonOnly="0" offsetType="0" rotationAngle="0" priority="5" geometryGeneratorType="PointGeometry" polygonPlacementFlags="2" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" xOffset="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" placementFlags="9" centroidWhole="0" distUnits="Point" lineAnchorClipping="0" lineAnchorTextPoint="FollowPlacement" offsetUnits="MM" placement="2" yOffset="0" centroidInside="0" repeatDistance="100" distMapUnitScale="3x:0,0,0,0,0,0" maximumDistance="0" quadOffset="4" layerType="LineGeometry" maximumDistanceUnit="MM" preserveRotation="1" rotationUnit="AngleDegrees" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" lineAnchorType="0" dist="-4" overlapHandling="PreventOverlap" lineAnchorPercent="0.5" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" overrunDistance="0" maxCurvedCharAngleOut="-25" prioritization="PreferCloser" geometryGenerator="" repeatDistanceUnits="Point" maxCurvedCharAngleIn="25" allowDegraded="0" geometryGeneratorEnabled="0"/>
          <rendering mergeLines="0" fontLimitPixelSize="0" fontMinPixelSize="3" labelPerPart="0" obstacleFactor="1" limitNumLabels="0" scaleMin="0" zIndex="0" fontMaxPixelSize="10000" upsidedownLabels="0" minFeatureSize="0" scaleMax="0" obstacle="1" scaleVisibility="0" unplacedVisibility="0" obstacleType="1" maxNumLabels="2000" drawLabels="1"/>
          <dd_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option value="pole_of_inaccessibility" type="QString" name="anchorPoint"/>
              <Option value="0" type="int" name="blendMode"/>
              <Option type="Map" name="ddProperties">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
              <Option value="false" type="bool" name="drawToAllParts"/>
              <Option value="0" type="QString" name="enabled"/>
              <Option value="point_on_exterior" type="QString" name="labelAnchorPoint"/>
              <Option value="&lt;symbol alpha=&quot;1&quot; frame_rate=&quot;10&quot; type=&quot;line&quot; force_rhr=&quot;0&quot; clip_to_extent=&quot;1&quot; is_animated=&quot;0&quot; name=&quot;symbol&quot;>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; type=&quot;QString&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; type=&quot;QString&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;layer locked=&quot;0&quot; pass=&quot;0&quot; class=&quot;SimpleLine&quot; id=&quot;{bdec80e5-7b98-428d-8f73-2f9193e43c18}&quot; enabled=&quot;1&quot;>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;align_dash_pattern&quot;/>&lt;Option value=&quot;square&quot; type=&quot;QString&quot; name=&quot;capstyle&quot;/>&lt;Option value=&quot;5;2&quot; type=&quot;QString&quot; name=&quot;customdash&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;customdash_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;customdash_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;draw_inside_polygon&quot;/>&lt;Option value=&quot;bevel&quot; type=&quot;QString&quot; name=&quot;joinstyle&quot;/>&lt;Option value=&quot;60,60,60,255,rgb:0.23529411764705882,0.23529411764705882,0.23529411764705882,1&quot; type=&quot;QString&quot; name=&quot;line_color&quot;/>&lt;Option value=&quot;solid&quot; type=&quot;QString&quot; name=&quot;line_style&quot;/>&lt;Option value=&quot;0.3&quot; type=&quot;QString&quot; name=&quot;line_width&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;line_width_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;offset&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;offset_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;offset_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;ring_filter&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;trim_distance_end&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;trim_distance_end_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;trim_distance_end_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;trim_distance_start&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;trim_distance_start_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;trim_distance_start_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;use_custom_dash&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;width_map_unit_scale&quot;/>&lt;/Option>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; type=&quot;QString&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; type=&quot;QString&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>" type="QString" name="lineSymbol"/>
              <Option value="0" type="double" name="minLength"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="minLengthMapUnitScale"/>
              <Option value="MM" type="QString" name="minLengthUnit"/>
              <Option value="0" type="double" name="offsetFromAnchor"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="offsetFromAnchorMapUnitScale"/>
              <Option value="MM" type="QString" name="offsetFromAnchorUnit"/>
              <Option value="0" type="double" name="offsetFromLabel"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="offsetFromLabelMapUnitScale"/>
              <Option value="MM" type="QString" name="offsetFromLabelUnit"/>
            </Option>
          </callout>
        </settings>
      </rule>
      <rule key="{097db97a-8b3b-4dfc-8f0f-5cd5c918ddfb}" filter="ELSE">
        <settings calloutType="simple">
          <text-style fontLetterSpacing="0" tabStopDistance="80" multilineHeightUnit="Percentage" fieldName="array_to_string(&quot;short_names&quot;, '/')" useSubstitutions="0" textOrientation="horizontal" capitalization="0" textOpacity="1" tabStopDistanceUnit="Point" multilineHeight="1" forcedItalic="0" tabStopDistanceMapUnitScale="3x:0,0,0,0,0,0" namedStyle="Bold" previewBkgrdColor="255,255,255,255,rgb:1,1,1,1" fontSizeUnit="Point" fontKerning="1" blendMode="0" fontWeight="75" legendString="Aa" textColor="50,50,50,255,rgb:0.19607843137254902,0.19607843137254902,0.19607843137254902,1" fontItalic="0" allowHtml="0" fontWordSpacing="0" fontStrikeout="0" fontFamily="Arial" fontUnderline="0" fontSize="10" forcedBold="0" fontSizeMapUnitScale="3x:0,0,0,0,0,0" isExpression="1">
            <families/>
            <text-buffer bufferJoinStyle="128" bufferDraw="0" bufferBlendMode="0" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferColor="250,250,250,255,rgb:0.98039215686274506,0.98039215686274506,0.98039215686274506,1" bufferSize="1" bufferSizeUnits="MM" bufferOpacity="1" bufferNoFill="1"/>
            <text-mask maskedSymbolLayers="" maskOpacity="1" maskSizeUnits="MM" maskJoinStyle="128" maskSize="1.5" maskType="0" maskEnabled="0" maskSize2="1.5" maskSizeMapUnitScale="3x:0,0,0,0,0,0"/>
            <background shapeBorderWidth="1" shapeBorderWidthUnit="Point" shapeType="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeJoinStyle="64" shapeSizeX="2" shapeRadiiUnit="Point" shapeRadiiY="4" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiX="4" shapeOffsetX="0" shapeDraw="0" shapeSVGFile="" shapeSizeY="2" shapeOffsetUnit="Point" shapeBlendMode="0" shapeRotationType="0" shapeBorderColor="111,168,218,255,rgb:0.43529411764705883,0.6588235294117647,0.85490196078431369,1" shapeOffsetY="-1.5" shapeSizeUnit="Point" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeFillColor="255,255,255,255,rgb:1,1,1,1" shapeRotation="0" shapeSizeType="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeOpacity="1">
              <symbol alpha="1" frame_rate="10" type="marker" force_rhr="0" clip_to_extent="1" is_animated="0" name="markerSymbol">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleMarker" id="" enabled="1">
                  <Option type="Map">
                    <Option value="0" type="QString" name="angle"/>
                    <Option value="square" type="QString" name="cap_style"/>
                    <Option value="145,82,45,255,rgb:0.56862745098039214,0.32156862745098042,0.17647058823529413,1" type="QString" name="color"/>
                    <Option value="1" type="QString" name="horizontal_anchor_point"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="circle" type="QString" name="name"/>
                    <Option value="0,0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="MM" type="QString" name="offset_unit"/>
                    <Option value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" type="QString" name="outline_color"/>
                    <Option value="solid" type="QString" name="outline_style"/>
                    <Option value="0" type="QString" name="outline_width"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="outline_width_map_unit_scale"/>
                    <Option value="MM" type="QString" name="outline_width_unit"/>
                    <Option value="diameter" type="QString" name="scale_method"/>
                    <Option value="2" type="QString" name="size"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="size_map_unit_scale"/>
                    <Option value="MM" type="QString" name="size_unit"/>
                    <Option value="1" type="QString" name="vertical_anchor_point"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
              <symbol alpha="1" frame_rate="10" type="fill" force_rhr="0" clip_to_extent="1" is_animated="0" name="fillSymbol">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" pass="0" class="SimpleFill" id="" enabled="1">
                  <Option type="Map">
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/>
                    <Option value="255,255,255,255,rgb:1,1,1,1" type="QString" name="color"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="0,0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="MM" type="QString" name="offset_unit"/>
                    <Option value="111,168,218,255,rgb:0.43529411764705883,0.6588235294117647,0.85490196078431369,1" type="QString" name="outline_color"/>
                    <Option value="solid" type="QString" name="outline_style"/>
                    <Option value="1" type="QString" name="outline_width"/>
                    <Option value="Point" type="QString" name="outline_width_unit"/>
                    <Option value="solid" type="QString" name="style"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option name="properties"/>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowDraw="0" shadowUnder="0" shadowRadiusUnit="MM" shadowOpacity="0.69999999999999996" shadowOffsetAngle="135" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetGlobal="1" shadowScale="100" shadowOffsetUnit="MM" shadowRadius="1.5" shadowColor="0,0,0,255,rgb:0,0,0,1" shadowOffsetDist="1" shadowBlendMode="6" shadowRadiusAlphaOnly="0"/>
            <dd_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format multilineAlign="0" leftDirectionSymbol="&lt;" autoWrapLength="0" placeDirectionSymbol="0" reverseDirectionSymbol="0" plussign="0" addDirectionSymbol="0" wrapChar="" decimals="3" formatNumbers="0" rightDirectionSymbol=">" useMaxLineLengthForAutoWrap="1"/>
          <placement maximumDistanceMapUnitScale="3x:0,0,0,0,0,0" overrunDistanceUnit="MM" fitInPolygonOnly="0" offsetType="0" rotationAngle="0" priority="5" geometryGeneratorType="PointGeometry" polygonPlacementFlags="2" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" xOffset="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" placementFlags="10" centroidWhole="0" distUnits="Point" lineAnchorClipping="0" lineAnchorTextPoint="FollowPlacement" offsetUnits="MM" placement="2" yOffset="0" centroidInside="0" repeatDistance="0" distMapUnitScale="3x:0,0,0,0,0,0" maximumDistance="0" quadOffset="4" layerType="LineGeometry" maximumDistanceUnit="MM" preserveRotation="1" rotationUnit="AngleDegrees" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" lineAnchorType="0" dist="5" overlapHandling="PreventOverlap" lineAnchorPercent="0.5" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" overrunDistance="0" maxCurvedCharAngleOut="-25" prioritization="PreferCloser" geometryGenerator="" repeatDistanceUnits="MM" maxCurvedCharAngleIn="25" allowDegraded="0" geometryGeneratorEnabled="0"/>
          <rendering mergeLines="0" fontLimitPixelSize="0" fontMinPixelSize="3" labelPerPart="0" obstacleFactor="1" limitNumLabels="0" scaleMin="0" zIndex="0" fontMaxPixelSize="10000" upsidedownLabels="0" minFeatureSize="0" scaleMax="0" obstacle="1" scaleVisibility="0" unplacedVisibility="0" obstacleType="1" maxNumLabels="2000" drawLabels="1"/>
          <dd_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option value="pole_of_inaccessibility" type="QString" name="anchorPoint"/>
              <Option value="0" type="int" name="blendMode"/>
              <Option type="Map" name="ddProperties">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
              <Option value="false" type="bool" name="drawToAllParts"/>
              <Option value="0" type="QString" name="enabled"/>
              <Option value="point_on_exterior" type="QString" name="labelAnchorPoint"/>
              <Option value="&lt;symbol alpha=&quot;1&quot; frame_rate=&quot;10&quot; type=&quot;line&quot; force_rhr=&quot;0&quot; clip_to_extent=&quot;1&quot; is_animated=&quot;0&quot; name=&quot;symbol&quot;>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; type=&quot;QString&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; type=&quot;QString&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;layer locked=&quot;0&quot; pass=&quot;0&quot; class=&quot;SimpleLine&quot; id=&quot;{82bfd6fa-1730-455e-ab3f-125fb38a4d05}&quot; enabled=&quot;1&quot;>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;align_dash_pattern&quot;/>&lt;Option value=&quot;square&quot; type=&quot;QString&quot; name=&quot;capstyle&quot;/>&lt;Option value=&quot;5;2&quot; type=&quot;QString&quot; name=&quot;customdash&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;customdash_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;customdash_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;draw_inside_polygon&quot;/>&lt;Option value=&quot;bevel&quot; type=&quot;QString&quot; name=&quot;joinstyle&quot;/>&lt;Option value=&quot;60,60,60,255,rgb:0.23529411764705882,0.23529411764705882,0.23529411764705882,1&quot; type=&quot;QString&quot; name=&quot;line_color&quot;/>&lt;Option value=&quot;solid&quot; type=&quot;QString&quot; name=&quot;line_style&quot;/>&lt;Option value=&quot;0.3&quot; type=&quot;QString&quot; name=&quot;line_width&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;line_width_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;offset&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;offset_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;offset_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;ring_filter&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;trim_distance_end&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;trim_distance_end_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;trim_distance_end_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;trim_distance_start&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;trim_distance_start_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;trim_distance_start_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;use_custom_dash&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;width_map_unit_scale&quot;/>&lt;/Option>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; type=&quot;QString&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; type=&quot;QString&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>" type="QString" name="lineSymbol"/>
              <Option value="0" type="double" name="minLength"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="minLengthMapUnitScale"/>
              <Option value="MM" type="QString" name="minLengthUnit"/>
              <Option value="0" type="double" name="offsetFromAnchor"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="offsetFromAnchorMapUnitScale"/>
              <Option value="MM" type="QString" name="offsetFromAnchorUnit"/>
              <Option value="0" type="double" name="offsetFromLabel"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="offsetFromLabelMapUnitScale"/>
              <Option value="MM" type="QString" name="offsetFromLabelUnit"/>
            </Option>
          </callout>
        </settings>
      </rule>
    </rules>
  </labeling>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerGeometryType>1</layerGeometryType>
</qgis>
