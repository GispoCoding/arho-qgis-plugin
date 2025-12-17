<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.40.3-Bratislava" labelsEnabled="1" styleCategories="Symbology|Labeling">
  <renderer-v2 symbollevels="0" referencescale="-1" type="RuleRenderer" enableorderby="0" forceraster="0">
    <rules key="{178e2009-9047-4176-9ebc-9cb596008dd4}">
      <rule filter="array_sort(map_akeys(&quot;type_regulations&quot;)) = array('tie')&#xd;&#xa;AND&#xd;&#xa;array_length(map_akeys(map_get(&quot;type_regulations&quot;, 'tie'))) = 0" label="Nykyinen tie" symbol="0" key="{67098b2b-c7b1-4727-bd83-4d2a5febcd08}"/>
      <rule filter="map_akeys(&quot;type_regulations&quot;) = array('moottoriTaiMoottoriliikenneTie')" label="Moottori- tai moottoriliikennetie" symbol="1" key="{71233534-3647-4254-ab4e-2187e3ab0742}"/>
      <rule filter="map_akeys(&quot;type_regulations&quot;) = array('kaksiajoratainenTieTaiKatu')&#xa;" label="Kaksiajoratainen tie tai katu" symbol="2" key="{903c9f98-cd42-4ffd-83d5-a079d3fcc05b}"/>
      <rule filter="array_sort(map_akeys(&quot;type_regulations&quot;)) = array('kantatie', 'valtatie')" label="Valtatie tai kantatie" symbol="3" key="{6101e3f2-3657-494a-ba45-850bbbc7fd1a}"/>
      <rule filter="array_sort(map_akeys(&quot;type_regulations&quot;)) = array('valtatie')&#xd;&#xa;AND array_length(map_akeys(map_get(&quot;type_regulations&quot;, 'valtatie'))) = 0" label="Valtatie" symbol="4" key="{7fd7f716-8a76-48fb-a7f9-c76001237174}"/>
      <rule filter="map_akeys(&quot;type_regulations&quot;) = array('kantatie')" label="Kantatie" symbol="5" key="{d0c7fc7b-9ff1-49cf-aab4-75aada06ccaf}"/>
      <rule filter="array_sort(map_akeys(&quot;type_regulations&quot;)) = array('paakatu', 'seututie')" label="Seututie tai pääkatu" symbol="6" key="{44525622-070c-4471-a3a7-46f008ba8620}"/>
      <rule filter="map_akeys(&quot;type_regulations&quot;) = array('seututie')" label="Seututie" symbol="7" key="{6a34abbc-f383-4161-a5af-abe469946ddc}"/>
      <rule filter="map_akeys(&quot;type_regulations&quot;) = array('paakatu')" label="Pääkatu" symbol="8" key="{792a7b80-beaf-4c1d-a197-5203a90c62c1}"/>
      <rule filter="map_akeys(&quot;type_regulations&quot;) = array('yhdystie')" label="Yhdystie" symbol="9" key="{7b22538e-f2b4-4311-ba19-8bcb222a154a}"/>
      <rule filter="array_sort(map_akeys(&quot;type_regulations&quot;)) = array('raideliikenteenAlue')&#xd;&#xa;AND array_length(map_akeys(map_get(&quot;type_regulations&quot;, 'raideliikenteenAlue'))) = 0" label="Rautatie" symbol="10" key="{a98bce27-0290-4dfb-858f-073cc2c872c4}"/>
      <rule filter="map_akeys(&quot;type_regulations&quot;) = array('paarata')" label="Päärata" symbol="11" key="{8f4efa89-4f16-4b9e-959c-3c678ce4eb9a}"/>
      <rule filter="map_akeys(&quot;type_regulations&quot;) = array('yhdysrata')" label="Yhdysrata" symbol="12" key="{e036841f-7968-4755-bbaf-2eccc1895778}"/>
      <rule filter="map_akeys(&quot;type_regulations&quot;) = array('sivurata')" label="Sivurata" symbol="13" key="{b78e78f6-b84a-46df-98e1-95f765d962b0}"/>
      <rule filter="map_akeys(&quot;type_regulations&quot;) = array('kaupunkirata')" label="Kaupunkirata" symbol="14" key="{0603add6-11ca-428e-a0d4-fbef5c3ee594}"/>
      <rule filter="map_akeys(&quot;type_regulations&quot;) = array('liikennetunneli')" label="Liikennetunneli" symbol="15" key="{37891b3d-4865-41ad-82fa-aa03f5727092}"/>
      <rule filter="map_akeys(&quot;type_regulations&quot;) = array('moottorikelkkailureitti')" label="Moottorikelkkailureitti" symbol="16" key="{30a4ce73-39f2-4b3d-94e5-77d9ce2bb7fb}"/>
      <rule filter="map_akeys(&quot;type_regulations&quot;) = array('laivavayla')" label="Laivaväylä" symbol="17" key="{44e49c43-0c54-4c38-9e16-1d5c5f43a5c2}"/>
      <rule filter="map_akeys(&quot;type_regulations&quot;) = array('venevayla')" label="Veneväylä" symbol="18" key="{620ed046-20ad-41cc-a218-22ec1828c84b}"/>
      <rule filter="map_akeys(&quot;type_regulations&quot;) = array('lossiTaiLauttaYhteys')" label="Lossi- tai lauttayhteys" symbol="19" key="{f60df711-5cc6-4c66-93d5-75524ce4a506}"/>
      <rule filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'tie')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'tie')), 'olemassaOleva')" label="Nykyinen tie - olemassa oleva" symbol="20" key="{5e62f549-e28d-400b-98be-6cce6338161e}"/>
      <rule filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'tie')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'tie')), 'uusi')" label="Uusi tie" symbol="21" key="{5eb48288-6088-4741-a782-c8332c4ac895}"/>
      <rule filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'tie')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'tie')), 'merkittavastiParannettava')" label="Uusi tie" symbol="22" key="{43fc452b-c793-40d4-a03b-5d4cccba7a1d}"/>
      <rule filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'valtatie')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'valtatie')), 'olemassaOleva')" label="Valtatie - olemassa oleva" symbol="23" key="{ff18458f-6403-4ed1-8477-c3341ad5b4c2}"/>
      <rule filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'valtatie')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'valtatie')), 'uusi')" label="Uusi valtatie" symbol="24" key="{89ab51ca-9860-4610-a4bb-4696907e941e}"/>
      <rule filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'valtatie')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'valtatie')), 'merkittavastiParannettava')" label="Merkittävästi parannettava valtatie" symbol="25" key="{29b8e7aa-0354-4d55-a108-0e66af591a3c}"/>
      <rule filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'tie')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'tie')), 'yhteystarve')" label="Tieliikenteen yhteystarve" symbol="26" key="{23054690-65d4-45e7-a5c6-42843ee054ea}"/>
      <rule filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'valtatie')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'valtatie')), 'yhteystarve')" label="Valtatien yhteystarve" symbol="27" key="{6251c84e-c449-487c-81c7-ed638d6a2cd9}"/>
      <rule filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'valtatie')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'valtatie')), 'ohjeellinenSijainti')" label="Ohjeellinen valtatie" symbol="28" key="{f7d6210b-b460-467d-b9ff-dbbdc8ba9da2}"/>
      <rule filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'valtatie')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'valtatie')), 'vaihtoehtoinen')" label="Vaihtoehtoinen valtatie" symbol="29" key="{38105b36-b91a-4a72-8e13-c3f620ff5421}"/>
      <rule filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'raideliikenteenAlue')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'raideliikenteenAlue')), 'yhteystarve')" label="Raideliikenteen yhteystarve" symbol="30" key="{1f55ab69-7e60-4a63-94cc-1b83d6b6458b}"/>
      <rule filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'joukkoliikenteenAlue')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'joukkoliikenteenAlue')), 'kehitettava')" label="Joukkoliikenteen kehittämiskäytävä" symbol="31" key="{84e0192a-04c2-4529-8cbc-f434616051cf}"/>
      <rule filter="array_contains(map_akeys(&quot;type_regulations&quot;), 'jalankulkualue')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'jalankulkualue')), 'yhteystarve')&#xa;AND&#xa;array_contains(map_akeys(&quot;type_regulations&quot;), 'pyorailyalue')&#xa;AND&#xa;array_contains(map_akeys(map_get(&quot;type_regulations&quot;, 'pyorailyalue')), 'yhteystarve')" label="Jalankulun ja pyöräilyn yhteystarve" symbol="32" key="{65e1875c-e1b4-4dfe-acf0-947c78eff78f}"/>
      <rule filter="map_akeys(&quot;type_regulations&quot;) = array('jalankulkualue')&#xa;AND&#xa;map_akeys(map_get(&quot;type_regulations&quot;, 'jalankulkualue')) = array('yhteystarve')" label="Jalankulun yhteystarve" symbol="33" key="{31db06af-f599-457a-b7ce-06b8433cc5ca}"/>
      <rule filter="map_akeys(&quot;type_regulations&quot;) = array('pyorailyalue')&#xa;AND&#xa;map_akeys(map_get(&quot;type_regulations&quot;, 'pyorailyalue')) = array('yhteystarve')" label="Pyöräilyn yhteystarve" symbol="34" key="{be570d05-afb3-42d8-ac59-3a5ed1c1600c}"/>
      <rule filter="array_sort(map_akeys(&quot;type_regulations&quot;)) = array('viheryhteys')&#xd;&#xa;AND array_length(map_akeys(map_get(&quot;type_regulations&quot;, 'viheryhteys'))) = 0" label="Viheryhteys" symbol="35" key="{fa229435-2ad4-4b8f-a334-b3effc7a53c0}"/>
      <rule filter="map_akeys(&quot;type_regulations&quot;) = array('viheryhteys')&#xa;AND&#xa;map_akeys(map_get(&quot;type_regulations&quot;, 'viheryhteys')) = array('yhteystarve')" label="Viheryhteystarve" symbol="36" key="{6077dce3-b7c5-46e2-a096-dc76c43fca4c}"/>
      <rule filter="array_sort(map_akeys(&quot;type_regulations&quot;)) = array('sahkolinja')&#xd;&#xa;AND array_length(map_akeys(map_get(&quot;type_regulations&quot;, 'sahkolinja'))) = 0" label="Sähkölinja" symbol="37" key="{874ed9d8-89f9-4c73-a4f8-373cd066112d}"/>
      <rule filter="array_sort(map_akeys(&quot;type_regulations&quot;)) = array('vesijohtoTaiViemari')&#xd;&#xa;AND array_length(map_akeys(map_get(&quot;type_regulations&quot;, 'vesijohtoTaiViemari'))) = 0" label="Vesijohto tai viemäri" symbol="38" key="{6644aed6-61f7-46f7-94f6-b154c7186dc2}"/>
      <rule filter="array_sort(map_akeys(&quot;type_regulations&quot;)) = array('kaasulinja')&#xd;&#xa;AND array_length(map_akeys(map_get(&quot;type_regulations&quot;, 'kaasulinja'))) = 0" label="Kaasulinja" symbol="39" key="{6274e6f7-0236-49a2-a434-97fe984faebb}"/>
      <rule filter="map_akeys(&quot;type_regulations&quot;) = array('sahkolinja')&#xa;AND&#xa;map_akeys(map_get(&quot;type_regulations&quot;, 'sahkolinja')) = array('uusi')" label="Uusi sähkölinja" symbol="40" key="{202bbd74-afd1-4045-bb53-5ab5f90b0cfa}"/>
      <rule filter="map_akeys(&quot;type_regulations&quot;) = array('vesijohtoTaiViemari')&#xa;AND&#xa;map_akeys(map_get(&quot;type_regulations&quot;, 'vesijohtoTaiViemari')) = array('uusi')" label="Uusi vesijohto tai viemäri" symbol="41" key="{b0f66703-7f3c-4fff-a9ea-9f62faeb1d0f}"/>
      <rule filter="map_akeys(&quot;type_regulations&quot;) = array('kaasulinja')&#xa;AND&#xa;map_akeys(map_get(&quot;type_regulations&quot;, 'kaasulinja')) = array('uusi')" label="Uusi kaasulinja" symbol="42" key="{f8275de9-3676-4d13-8562-85c9f444baef}"/>
      <rule filter="map_akeys(&quot;type_regulations&quot;) = array('sahkolinja')&#xa;AND&#xa;map_akeys(map_get(&quot;type_regulations&quot;, 'sahkolinja')) = array('yhteystarve')" label="Sähkölinjan yhteystarve" symbol="43" key="{3f0060c1-1911-4c66-b36e-bdcdff2f7e9d}"/>
      <rule filter="map_akeys(&quot;type_regulations&quot;) = array('vesijohtoTaiViemari')&#xa;AND&#xa;map_akeys(map_get(&quot;type_regulations&quot;, 'vesijohtoTaiViemari')) = array('yhteystarve')" label="Vesijohdon tai viemärin yhteystarve" symbol="44" key="{21f000d1-7099-4e51-9685-39e73e6aaed6}"/>
      <rule filter="map_akeys(&quot;type_regulations&quot;) = array('kaasulinja')&#xa;AND&#xa;map_akeys(map_get(&quot;type_regulations&quot;, 'kaasulinja')) = array('yhteystarve')" label="Kaasulinjan yhteystarve" symbol="45" key="{2bca7222-658a-472a-b5ef-7923b0e9bc53}"/>
      <rule filter="array_sort(map_akeys(&quot;type_regulations&quot;)) = array('historiallinenKohde')&#xd;&#xa;AND array_length(map_akeys(map_get(&quot;type_regulations&quot;, 'historiallinenKohde'))) = 0&#xd;&#xa;" label="Historiallinen tie" symbol="46" key="{0236b4c3-7fc6-4478-acbd-dec99c141f86}"/>
      <rule filter="array_sort(map_akeys(&quot;type_regulations&quot;)) = array('ulkoiluTaiVirkistysReitti')&#xd;&#xa;AND&#xd;&#xa;array_length(map_akeys(map_get(&quot;type_regulations&quot;, 'ulkoiluTaiVirkistysReitti'))) = 0" label="Ulkoilu- tai virkistysreitti" symbol="47" key="{41f233b8-d959-4cce-a00e-fbe5d40910a8}"/>
      <rule filter="map_akeys(&quot;type_regulations&quot;) = array('ulkoiluTaiVirkistysReitti')&#xa;AND&#xa;map_akeys(map_get(&quot;type_regulations&quot;, 'ulkoiluTaiVirkistysReitti')) = array('uusi')" label="Uusi ulkoilu- tai virkistysreitti" symbol="48" key="{d5652e83-42d2-4615-a2ad-53b855bb3182}"/>
      <rule filter="map_akeys(&quot;type_regulations&quot;) = array('ulkoiluTaiVirkistysReitti')&#xa;AND&#xa;map_akeys(map_get(&quot;type_regulations&quot;, 'ulkoiluTaiVirkistysReitti')) = array('yhteystarve')" label="Ulkoilu- tai virkistysreitin yhteystarve" symbol="49" key="{c62c9297-0f9a-46cf-9e48-9e77385b9e7a}"/>
      <rule filter="map_exist(&#xd;&#xa;  &quot;type_regulations&quot;,&#xd;&#xa;  'valtakunnallisestiMerkittavaRakennettuKulttuuriymparisto'&#xd;&#xa;)&#xd;&#xa;AND map_exist(&#xd;&#xa;  &quot;type_regulations&quot;['valtakunnallisestiMerkittavaRakennettuKulttuuriymparisto'],&#xd;&#xa;  'valtakunnallinen'&#xd;&#xa;)" label="Valtakunnallisesti merkittävä rakennettu kulttuuriympäristö" symbol="50" key="{f163734d-0d48-4b8a-8ad1-91a8d908de7a}"/>
      <rule filter="map_exist(&#xd;&#xa;  &quot;type_regulations&quot;,&#xd;&#xa;  'natura2000VerkostonAlue'&#xd;&#xa;)&#xd;&#xa;AND map_exist(&#xd;&#xa;  &quot;type_regulations&quot;['natura2000VerkostonAlue'],&#xd;&#xa;  'osaAlue'&#xd;&#xa;)" label="Natura 2000 -verkostoon kuuluva alue" symbol="51" key="{4d0bd845-1b4c-4785-a671-21d154a1f647}"/>
      <rule filter="map_exist(&#xd;&#xa;  &quot;type_regulations&quot;,&#xd;&#xa;  'luonnonMonimuotoisuudenKannaltaErityisenTarkeaAlue'&#xd;&#xa;)&#xd;&#xa;AND map_exist(&#xd;&#xa;  &quot;type_regulations&quot;['luonnonMonimuotoisuudenKannaltaErityisenTarkeaAlue'],&#xd;&#xa;  'osaAlue'&#xd;&#xa;)" label="Luonnon &#xa;monimuotoisuuden kannalta erityisen tärkeä alue" symbol="52" key="{2f802cb9-1fcf-41ca-a746-185b562f22d5}"/>
      <rule filter="map_akeys(&quot;type_regulations&quot;) = array('yhdyskuntarakenteenLaajenemissuunta')" label="Yhdyskuntarakenteen laajenemissuunta" symbol="53" key="{1c73678f-9182-4917-91ac-d3be82a21409}"/>
      <rule filter="map_akeys(&quot;type_regulations&quot;) = array('liikennealue')&#xa;AND&#xa;map_akeys(map_get(&quot;type_regulations&quot;, 'liikennealue')) = array('yhteystarve')" label="Liikenteen yhteystarve" symbol="54" key="{46e91e2d-23d2-4412-b4a2-f7fbaeab1f4a}"/>
      <rule filter="map_akeys(&quot;type_regulations&quot;) = array('vesialue')" label="Joki tai muu avouoma" symbol="55" key="{4f8ad91e-b296-4cfe-a919-249ce0983787}"/>
      <rule filter="ELSE" symbol="56" key="{ba8c8769-847c-4e70-8e9a-beeece6ff861}"/>
    </rules>
    <symbols>
      <symbol force_rhr="0" is_animated="0" name="0" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{8ad0c838-9845-4e87-88d7-4222d703f5c4}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="0,0,0,255,rgb:0,0,0,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="7"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="1" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{25c4fb42-15ec-424f-997d-3fbfcd0d24da}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="2"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="-2.5"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="Point"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer pass="0" enabled="1" locked="0" id="{61e84333-9081-418c-9840-8a0bedf23d3d}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="2"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="2.5"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="Point"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer pass="0" enabled="1" locked="0" id="{713ea345-8053-41b3-bd94-bfab2ee2b903}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="1"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="Point"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="10" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{e8e74edc-9f4c-4872-952a-71dc3d78f6ae}" class="HashLine">
          <Option type="Map">
            <Option name="average_angle_length" type="QString" value="4"/>
            <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="average_angle_unit" type="QString" value="MM"/>
            <Option name="hash_angle" type="QString" value="0"/>
            <Option name="hash_length" type="QString" value="3"/>
            <Option name="hash_length_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="hash_length_unit" type="QString" value="MM"/>
            <Option name="interval" type="QString" value="5"/>
            <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="interval_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_along_line" type="QString" value="0"/>
            <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_along_line_unit" type="QString" value="MM"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="place_on_every_part" type="bool" value="true"/>
            <Option name="placements" type="QString" value="Interval|LastVertex|FirstVertex"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="rotate" type="QString" value="1"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@10@0" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{8ece23c8-3575-4aab-82ae-f29f412552e6}" class="SimpleLine">
              <Option type="Map">
                <Option name="align_dash_pattern" type="QString" value="0"/>
                <Option name="capstyle" type="QString" value="square"/>
                <Option name="customdash" type="QString" value="5;2"/>
                <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="customdash_unit" type="QString" value="Point"/>
                <Option name="dash_pattern_offset" type="QString" value="0"/>
                <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="dash_pattern_offset_unit" type="QString" value="Point"/>
                <Option name="draw_inside_polygon" type="QString" value="0"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="line_color" type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1"/>
                <Option name="line_style" type="QString" value="solid"/>
                <Option name="line_width" type="QString" value="1.5"/>
                <Option name="line_width_unit" type="QString" value="Point"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="trim_distance_end" type="QString" value="0"/>
                <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_end_unit" type="QString" value="Point"/>
                <Option name="trim_distance_start" type="QString" value="0"/>
                <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_start_unit" type="QString" value="Point"/>
                <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                <Option name="use_custom_dash" type="QString" value="0"/>
                <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer pass="0" enabled="1" locked="0" id="{583d8817-83d0-4417-a21c-bc8a0f5962c3}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="2"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="11" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{e8e74edc-9f4c-4872-952a-71dc3d78f6ae}" class="HashLine">
          <Option type="Map">
            <Option name="average_angle_length" type="QString" value="4"/>
            <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="average_angle_unit" type="QString" value="MM"/>
            <Option name="hash_angle" type="QString" value="0"/>
            <Option name="hash_length" type="QString" value="3"/>
            <Option name="hash_length_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="hash_length_unit" type="QString" value="MM"/>
            <Option name="interval" type="QString" value="5"/>
            <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="interval_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_along_line" type="QString" value="0"/>
            <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_along_line_unit" type="QString" value="MM"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="place_on_every_part" type="bool" value="true"/>
            <Option name="placements" type="QString" value="Interval|LastVertex|FirstVertex"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="rotate" type="QString" value="1"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@11@0" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{8ece23c8-3575-4aab-82ae-f29f412552e6}" class="SimpleLine">
              <Option type="Map">
                <Option name="align_dash_pattern" type="QString" value="0"/>
                <Option name="capstyle" type="QString" value="square"/>
                <Option name="customdash" type="QString" value="5;2"/>
                <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="customdash_unit" type="QString" value="Point"/>
                <Option name="dash_pattern_offset" type="QString" value="0"/>
                <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="dash_pattern_offset_unit" type="QString" value="Point"/>
                <Option name="draw_inside_polygon" type="QString" value="0"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="line_color" type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1"/>
                <Option name="line_style" type="QString" value="solid"/>
                <Option name="line_width" type="QString" value="1.5"/>
                <Option name="line_width_unit" type="QString" value="Point"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="trim_distance_end" type="QString" value="0"/>
                <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_end_unit" type="QString" value="Point"/>
                <Option name="trim_distance_start" type="QString" value="0"/>
                <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_start_unit" type="QString" value="Point"/>
                <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                <Option name="use_custom_dash" type="QString" value="0"/>
                <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer pass="0" enabled="1" locked="0" id="{583d8817-83d0-4417-a21c-bc8a0f5962c3}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="2"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="12" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{e8e74edc-9f4c-4872-952a-71dc3d78f6ae}" class="HashLine">
          <Option type="Map">
            <Option name="average_angle_length" type="QString" value="4"/>
            <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="average_angle_unit" type="QString" value="MM"/>
            <Option name="hash_angle" type="QString" value="0"/>
            <Option name="hash_length" type="QString" value="3"/>
            <Option name="hash_length_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="hash_length_unit" type="QString" value="MM"/>
            <Option name="interval" type="QString" value="5"/>
            <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="interval_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_along_line" type="QString" value="0"/>
            <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_along_line_unit" type="QString" value="MM"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="place_on_every_part" type="bool" value="true"/>
            <Option name="placements" type="QString" value="Interval|LastVertex|FirstVertex"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="rotate" type="QString" value="1"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@12@0" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{8ece23c8-3575-4aab-82ae-f29f412552e6}" class="SimpleLine">
              <Option type="Map">
                <Option name="align_dash_pattern" type="QString" value="0"/>
                <Option name="capstyle" type="QString" value="square"/>
                <Option name="customdash" type="QString" value="5;2"/>
                <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="customdash_unit" type="QString" value="Point"/>
                <Option name="dash_pattern_offset" type="QString" value="0"/>
                <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="dash_pattern_offset_unit" type="QString" value="Point"/>
                <Option name="draw_inside_polygon" type="QString" value="0"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="line_color" type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1"/>
                <Option name="line_style" type="QString" value="solid"/>
                <Option name="line_width" type="QString" value="1.5"/>
                <Option name="line_width_unit" type="QString" value="Point"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="trim_distance_end" type="QString" value="0"/>
                <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_end_unit" type="QString" value="Point"/>
                <Option name="trim_distance_start" type="QString" value="0"/>
                <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_start_unit" type="QString" value="Point"/>
                <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                <Option name="use_custom_dash" type="QString" value="0"/>
                <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer pass="0" enabled="1" locked="0" id="{583d8817-83d0-4417-a21c-bc8a0f5962c3}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="2"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="13" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{e8e74edc-9f4c-4872-952a-71dc3d78f6ae}" class="HashLine">
          <Option type="Map">
            <Option name="average_angle_length" type="QString" value="4"/>
            <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="average_angle_unit" type="QString" value="MM"/>
            <Option name="hash_angle" type="QString" value="0"/>
            <Option name="hash_length" type="QString" value="3"/>
            <Option name="hash_length_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="hash_length_unit" type="QString" value="MM"/>
            <Option name="interval" type="QString" value="5"/>
            <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="interval_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_along_line" type="QString" value="0"/>
            <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_along_line_unit" type="QString" value="MM"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="place_on_every_part" type="bool" value="true"/>
            <Option name="placements" type="QString" value="Interval|LastVertex|FirstVertex"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="rotate" type="QString" value="1"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@13@0" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{8ece23c8-3575-4aab-82ae-f29f412552e6}" class="SimpleLine">
              <Option type="Map">
                <Option name="align_dash_pattern" type="QString" value="0"/>
                <Option name="capstyle" type="QString" value="square"/>
                <Option name="customdash" type="QString" value="5;2"/>
                <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="customdash_unit" type="QString" value="Point"/>
                <Option name="dash_pattern_offset" type="QString" value="0"/>
                <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="dash_pattern_offset_unit" type="QString" value="Point"/>
                <Option name="draw_inside_polygon" type="QString" value="0"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="line_color" type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1"/>
                <Option name="line_style" type="QString" value="solid"/>
                <Option name="line_width" type="QString" value="1.5"/>
                <Option name="line_width_unit" type="QString" value="Point"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="trim_distance_end" type="QString" value="0"/>
                <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_end_unit" type="QString" value="Point"/>
                <Option name="trim_distance_start" type="QString" value="0"/>
                <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_start_unit" type="QString" value="Point"/>
                <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                <Option name="use_custom_dash" type="QString" value="0"/>
                <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer pass="0" enabled="1" locked="0" id="{583d8817-83d0-4417-a21c-bc8a0f5962c3}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="2"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="14" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{e8e74edc-9f4c-4872-952a-71dc3d78f6ae}" class="HashLine">
          <Option type="Map">
            <Option name="average_angle_length" type="QString" value="4"/>
            <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="average_angle_unit" type="QString" value="MM"/>
            <Option name="hash_angle" type="QString" value="0"/>
            <Option name="hash_length" type="QString" value="3"/>
            <Option name="hash_length_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="hash_length_unit" type="QString" value="MM"/>
            <Option name="interval" type="QString" value="5"/>
            <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="interval_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_along_line" type="QString" value="0"/>
            <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_along_line_unit" type="QString" value="MM"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="place_on_every_part" type="bool" value="true"/>
            <Option name="placements" type="QString" value="Interval|LastVertex|FirstVertex"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="rotate" type="QString" value="1"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@14@0" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{8ece23c8-3575-4aab-82ae-f29f412552e6}" class="SimpleLine">
              <Option type="Map">
                <Option name="align_dash_pattern" type="QString" value="0"/>
                <Option name="capstyle" type="QString" value="square"/>
                <Option name="customdash" type="QString" value="5;2"/>
                <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="customdash_unit" type="QString" value="Point"/>
                <Option name="dash_pattern_offset" type="QString" value="0"/>
                <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="dash_pattern_offset_unit" type="QString" value="Point"/>
                <Option name="draw_inside_polygon" type="QString" value="0"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="line_color" type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1"/>
                <Option name="line_style" type="QString" value="solid"/>
                <Option name="line_width" type="QString" value="1.5"/>
                <Option name="line_width_unit" type="QString" value="Point"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="trim_distance_end" type="QString" value="0"/>
                <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_end_unit" type="QString" value="Point"/>
                <Option name="trim_distance_start" type="QString" value="0"/>
                <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_start_unit" type="QString" value="Point"/>
                <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                <Option name="use_custom_dash" type="QString" value="0"/>
                <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer pass="0" enabled="1" locked="0" id="{583d8817-83d0-4417-a21c-bc8a0f5962c3}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="2"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="15" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{5c39f1f5-4b0b-4be7-a2b6-13b41c7167d5}" class="HashLine">
          <Option type="Map">
            <Option name="average_angle_length" type="QString" value="4"/>
            <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="average_angle_unit" type="QString" value="MM"/>
            <Option name="hash_angle" type="QString" value="90"/>
            <Option name="hash_length" type="QString" value="3"/>
            <Option name="hash_length_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="hash_length_unit" type="QString" value="MM"/>
            <Option name="interval" type="QString" value="15"/>
            <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="interval_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="1.9"/>
            <Option name="offset_along_line" type="QString" value="0"/>
            <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_along_line_unit" type="QString" value="MM"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="place_on_every_part" type="bool" value="true"/>
            <Option name="placements" type="QString" value="Interval"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="rotate" type="QString" value="1"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@15@0" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{8d9ec6c7-5d58-40dc-bb74-01bf746b0802}" class="SimpleLine">
              <Option type="Map">
                <Option name="align_dash_pattern" type="QString" value="0"/>
                <Option name="capstyle" type="QString" value="square"/>
                <Option name="customdash" type="QString" value="5;2"/>
                <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="customdash_unit" type="QString" value="Point"/>
                <Option name="dash_pattern_offset" type="QString" value="0"/>
                <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="dash_pattern_offset_unit" type="QString" value="Point"/>
                <Option name="draw_inside_polygon" type="QString" value="0"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="line_color" type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1"/>
                <Option name="line_style" type="QString" value="solid"/>
                <Option name="line_width" type="QString" value="2"/>
                <Option name="line_width_unit" type="QString" value="Point"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="trim_distance_end" type="QString" value="0"/>
                <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_end_unit" type="QString" value="Point"/>
                <Option name="trim_distance_start" type="QString" value="0"/>
                <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_start_unit" type="QString" value="Point"/>
                <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                <Option name="use_custom_dash" type="QString" value="0"/>
                <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer pass="0" enabled="1" locked="0" id="{751c1e16-d2fe-467e-af1e-d3f52fffc4bb}" class="HashLine">
          <Option type="Map">
            <Option name="average_angle_length" type="QString" value="4"/>
            <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="average_angle_unit" type="QString" value="MM"/>
            <Option name="hash_angle" type="QString" value="90"/>
            <Option name="hash_length" type="QString" value="3"/>
            <Option name="hash_length_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="hash_length_unit" type="QString" value="MM"/>
            <Option name="interval" type="QString" value="15"/>
            <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="interval_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="-1.9"/>
            <Option name="offset_along_line" type="QString" value="0"/>
            <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_along_line_unit" type="QString" value="MM"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="place_on_every_part" type="bool" value="true"/>
            <Option name="placements" type="QString" value="Interval"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="rotate" type="QString" value="1"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@15@1" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{25a29b12-86f5-45d4-808b-451b0058b8c7}" class="SimpleLine">
              <Option type="Map">
                <Option name="align_dash_pattern" type="QString" value="0"/>
                <Option name="capstyle" type="QString" value="square"/>
                <Option name="customdash" type="QString" value="5;2"/>
                <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="customdash_unit" type="QString" value="Point"/>
                <Option name="dash_pattern_offset" type="QString" value="0"/>
                <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="dash_pattern_offset_unit" type="QString" value="Point"/>
                <Option name="draw_inside_polygon" type="QString" value="0"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="line_color" type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1"/>
                <Option name="line_style" type="QString" value="solid"/>
                <Option name="line_width" type="QString" value="2"/>
                <Option name="line_width_unit" type="QString" value="Point"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="trim_distance_end" type="QString" value="0"/>
                <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_end_unit" type="QString" value="Point"/>
                <Option name="trim_distance_start" type="QString" value="0"/>
                <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_start_unit" type="QString" value="Point"/>
                <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                <Option name="use_custom_dash" type="QString" value="0"/>
                <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="16" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{8f2a7c15-775f-49ec-bb29-8a6c014f884a}" class="HashLine">
          <Option type="Map">
            <Option name="average_angle_length" type="QString" value="4"/>
            <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="average_angle_unit" type="QString" value="MM"/>
            <Option name="hash_angle" type="QString" value="90"/>
            <Option name="hash_length" type="QString" value="5"/>
            <Option name="hash_length_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="hash_length_unit" type="QString" value="Point"/>
            <Option name="interval" type="QString" value="10"/>
            <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="interval_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="-3"/>
            <Option name="offset_along_line" type="QString" value="3"/>
            <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_along_line_unit" type="QString" value="Point"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="Point"/>
            <Option name="place_on_every_part" type="bool" value="true"/>
            <Option name="placements" type="QString" value="Interval"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="rotate" type="QString" value="1"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@16@0" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{0c095a22-8dd9-4e65-9784-4bc178f6ce8e}" class="SimpleLine">
              <Option type="Map">
                <Option name="align_dash_pattern" type="QString" value="0"/>
                <Option name="capstyle" type="QString" value="square"/>
                <Option name="customdash" type="QString" value="5;2"/>
                <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="customdash_unit" type="QString" value="MM"/>
                <Option name="dash_pattern_offset" type="QString" value="0"/>
                <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
                <Option name="draw_inside_polygon" type="QString" value="0"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="line_color" type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1"/>
                <Option name="line_style" type="QString" value="solid"/>
                <Option name="line_width" type="QString" value="1"/>
                <Option name="line_width_unit" type="QString" value="Point"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="MM"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="trim_distance_end" type="QString" value="0"/>
                <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_end_unit" type="QString" value="MM"/>
                <Option name="trim_distance_start" type="QString" value="0"/>
                <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_start_unit" type="QString" value="MM"/>
                <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                <Option name="use_custom_dash" type="QString" value="0"/>
                <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer pass="0" enabled="1" locked="0" id="{dd88cfd4-0cde-43d0-b51b-602719f8af27}" class="HashLine">
          <Option type="Map">
            <Option name="average_angle_length" type="QString" value="4"/>
            <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="average_angle_unit" type="QString" value="MM"/>
            <Option name="hash_angle" type="QString" value="90"/>
            <Option name="hash_length" type="QString" value="5"/>
            <Option name="hash_length_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="hash_length_unit" type="QString" value="Point"/>
            <Option name="interval" type="QString" value="10"/>
            <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="interval_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="3"/>
            <Option name="offset_along_line" type="QString" value="3"/>
            <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_along_line_unit" type="QString" value="Point"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="Point"/>
            <Option name="place_on_every_part" type="bool" value="true"/>
            <Option name="placements" type="QString" value="Interval"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="rotate" type="QString" value="1"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@16@1" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{8d1da158-9c47-4089-ae61-34550acf3a95}" class="SimpleLine">
              <Option type="Map">
                <Option name="align_dash_pattern" type="QString" value="0"/>
                <Option name="capstyle" type="QString" value="square"/>
                <Option name="customdash" type="QString" value="5;2"/>
                <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="customdash_unit" type="QString" value="Point"/>
                <Option name="dash_pattern_offset" type="QString" value="0"/>
                <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="dash_pattern_offset_unit" type="QString" value="Point"/>
                <Option name="draw_inside_polygon" type="QString" value="0"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="line_color" type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1"/>
                <Option name="line_style" type="QString" value="solid"/>
                <Option name="line_width" type="QString" value="1"/>
                <Option name="line_width_unit" type="QString" value="Point"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="trim_distance_end" type="QString" value="0"/>
                <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_end_unit" type="QString" value="Point"/>
                <Option name="trim_distance_start" type="QString" value="0"/>
                <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_start_unit" type="QString" value="Point"/>
                <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                <Option name="use_custom_dash" type="QString" value="0"/>
                <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer pass="0" enabled="1" locked="0" id="{c7fcb617-7ccd-4853-9b09-e7ede2a2b5e8}" class="HashLine">
          <Option type="Map">
            <Option name="average_angle_length" type="QString" value="4"/>
            <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="average_angle_unit" type="QString" value="MM"/>
            <Option name="hash_angle" type="QString" value="0"/>
            <Option name="hash_length" type="QString" value="5"/>
            <Option name="hash_length_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="hash_length_unit" type="QString" value="Point"/>
            <Option name="interval" type="QString" value="10"/>
            <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="interval_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_along_line" type="QString" value="0"/>
            <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_along_line_unit" type="QString" value="MM"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="place_on_every_part" type="bool" value="true"/>
            <Option name="placements" type="QString" value="Interval"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="rotate" type="QString" value="1"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@16@2" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{ff95c9f2-daff-4264-b75f-490a7caeb416}" class="SimpleLine">
              <Option type="Map">
                <Option name="align_dash_pattern" type="QString" value="0"/>
                <Option name="capstyle" type="QString" value="square"/>
                <Option name="customdash" type="QString" value="5;2"/>
                <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="customdash_unit" type="QString" value="Point"/>
                <Option name="dash_pattern_offset" type="QString" value="0"/>
                <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="dash_pattern_offset_unit" type="QString" value="Point"/>
                <Option name="draw_inside_polygon" type="QString" value="0"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="line_color" type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1"/>
                <Option name="line_style" type="QString" value="solid"/>
                <Option name="line_width" type="QString" value="1"/>
                <Option name="line_width_unit" type="QString" value="Point"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="trim_distance_end" type="QString" value="0"/>
                <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_end_unit" type="QString" value="Point"/>
                <Option name="trim_distance_start" type="QString" value="0"/>
                <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_start_unit" type="QString" value="Point"/>
                <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                <Option name="use_custom_dash" type="QString" value="0"/>
                <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="17" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{8f748a90-fa04-4d9f-a1b7-35450d03ace7}" class="MarkerLine">
          <Option type="Map">
            <Option name="average_angle_length" type="QString" value="4"/>
            <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="average_angle_unit" type="QString" value="MM"/>
            <Option name="interval" type="QString" value="13"/>
            <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="interval_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_along_line" type="QString" value="0"/>
            <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_along_line_unit" type="QString" value="MM"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="place_on_every_part" type="bool" value="true"/>
            <Option name="placements" type="QString" value="Interval"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="rotate" type="QString" value="1"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@17@0" type="marker" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{dc1bd9e5-d02e-4e8f-bfbc-f5f542fbcc7f}" class="SimpleMarker">
              <Option type="Map">
                <Option name="angle" type="QString" value="0"/>
                <Option name="cap_style" type="QString" value="square"/>
                <Option name="color" type="QString" value="0,0,0,255,rgb:0,0,0,1"/>
                <Option name="horizontal_anchor_point" type="QString" value="1"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="name" type="QString" value="circle"/>
                <Option name="offset" type="QString" value="0,0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="outline_color" type="QString" value="0,0,0,255,rgb:0,0,0,1"/>
                <Option name="outline_style" type="QString" value="solid"/>
                <Option name="outline_width" type="QString" value="0"/>
                <Option name="outline_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="outline_width_unit" type="QString" value="Point"/>
                <Option name="scale_method" type="QString" value="diameter"/>
                <Option name="size" type="QString" value="6"/>
                <Option name="size_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="size_unit" type="QString" value="Point"/>
                <Option name="vertical_anchor_point" type="QString" value="1"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer pass="0" enabled="1" locked="0" id="{2abfdf4f-4a9a-45e5-9bbe-e4aa29c087c5}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="0,0,0,255,rgb:0,0,0,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="1"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="18" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{8f748a90-fa04-4d9f-a1b7-35450d03ace7}" class="MarkerLine">
          <Option type="Map">
            <Option name="average_angle_length" type="QString" value="4"/>
            <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="average_angle_unit" type="QString" value="MM"/>
            <Option name="interval" type="QString" value="15"/>
            <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="interval_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_along_line" type="QString" value="0"/>
            <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_along_line_unit" type="QString" value="MM"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="place_on_every_part" type="bool" value="true"/>
            <Option name="placements" type="QString" value="Interval"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="rotate" type="QString" value="1"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@18@0" type="marker" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{dc1bd9e5-d02e-4e8f-bfbc-f5f542fbcc7f}" class="SimpleMarker">
              <Option type="Map">
                <Option name="angle" type="QString" value="0"/>
                <Option name="cap_style" type="QString" value="square"/>
                <Option name="color" type="QString" value="255,255,255,255,rgb:1,1,1,1"/>
                <Option name="horizontal_anchor_point" type="QString" value="1"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="name" type="QString" value="circle"/>
                <Option name="offset" type="QString" value="0,0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="outline_color" type="QString" value="0,0,0,255,rgb:0,0,0,1"/>
                <Option name="outline_style" type="QString" value="solid"/>
                <Option name="outline_width" type="QString" value="1"/>
                <Option name="outline_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="outline_width_unit" type="QString" value="Point"/>
                <Option name="scale_method" type="QString" value="diameter"/>
                <Option name="size" type="QString" value="6"/>
                <Option name="size_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="size_unit" type="QString" value="Point"/>
                <Option name="vertical_anchor_point" type="QString" value="1"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer pass="0" enabled="1" locked="0" id="{0d357d8a-d521-453e-92ba-f5b974037921}" class="HashLine">
          <Option type="Map">
            <Option name="average_angle_length" type="QString" value="4"/>
            <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="average_angle_unit" type="QString" value="MM"/>
            <Option name="hash_angle" type="QString" value="90"/>
            <Option name="hash_length" type="QString" value="8"/>
            <Option name="hash_length_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="hash_length_unit" type="QString" value="Point"/>
            <Option name="interval" type="QString" value="15"/>
            <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="interval_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_along_line" type="QString" value="7"/>
            <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_along_line_unit" type="QString" value="Point"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="place_on_every_part" type="bool" value="true"/>
            <Option name="placements" type="QString" value="Interval"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="rotate" type="QString" value="1"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@18@1" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{a75de32d-2071-4543-896a-cd329adc0907}" class="SimpleLine">
              <Option type="Map">
                <Option name="align_dash_pattern" type="QString" value="0"/>
                <Option name="capstyle" type="QString" value="square"/>
                <Option name="customdash" type="QString" value="5;2"/>
                <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="customdash_unit" type="QString" value="Point"/>
                <Option name="dash_pattern_offset" type="QString" value="0"/>
                <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="dash_pattern_offset_unit" type="QString" value="Point"/>
                <Option name="draw_inside_polygon" type="QString" value="0"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="line_color" type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1"/>
                <Option name="line_style" type="QString" value="solid"/>
                <Option name="line_width" type="QString" value="1"/>
                <Option name="line_width_unit" type="QString" value="Point"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="trim_distance_end" type="QString" value="0"/>
                <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_end_unit" type="QString" value="Point"/>
                <Option name="trim_distance_start" type="QString" value="0"/>
                <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_start_unit" type="QString" value="Point"/>
                <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                <Option name="use_custom_dash" type="QString" value="0"/>
                <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="19" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{8f748a90-fa04-4d9f-a1b7-35450d03ace7}" class="MarkerLine">
          <Option type="Map">
            <Option name="average_angle_length" type="QString" value="4"/>
            <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="average_angle_unit" type="QString" value="MM"/>
            <Option name="interval" type="QString" value="13"/>
            <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="interval_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_along_line" type="QString" value="0"/>
            <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_along_line_unit" type="QString" value="MM"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="place_on_every_part" type="bool" value="true"/>
            <Option name="placements" type="QString" value="Interval"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="rotate" type="QString" value="1"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@19@0" type="marker" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{dc1bd9e5-d02e-4e8f-bfbc-f5f542fbcc7f}" class="SimpleMarker">
              <Option type="Map">
                <Option name="angle" type="QString" value="0"/>
                <Option name="cap_style" type="QString" value="square"/>
                <Option name="color" type="QString" value="0,0,0,255,rgb:0,0,0,1"/>
                <Option name="horizontal_anchor_point" type="QString" value="1"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="name" type="QString" value="circle"/>
                <Option name="offset" type="QString" value="0,0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="outline_color" type="QString" value="0,0,0,255,rgb:0,0,0,1"/>
                <Option name="outline_style" type="QString" value="solid"/>
                <Option name="outline_width" type="QString" value="0"/>
                <Option name="outline_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="outline_width_unit" type="QString" value="Point"/>
                <Option name="scale_method" type="QString" value="diameter"/>
                <Option name="size" type="QString" value="6"/>
                <Option name="size_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="size_unit" type="QString" value="Point"/>
                <Option name="vertical_anchor_point" type="QString" value="1"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer pass="0" enabled="1" locked="0" id="{2abfdf4f-4a9a-45e5-9bbe-e4aa29c087c5}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="0,0,0,255,rgb:0,0,0,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="1"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="2" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{68b416ff-0f22-4a27-95a1-c4546fc5f21f}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="0,0,0,255,rgb:0,0,0,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="3"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="3"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="Point"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer pass="0" enabled="1" locked="0" id="{7f1e5810-df05-4546-aa14-23b5373f1844}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="0,0,0,255,rgb:0,0,0,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="3"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="-3"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="Point"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="20" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{8ad0c838-9845-4e87-88d7-4222d703f5c4}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="Point"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="Point"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="0,0,0,255,rgb:0,0,0,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="7"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="Point"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="Point"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="Point"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="21" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{8ad0c838-9845-4e87-88d7-4222d703f5c4}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="Point"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="Point"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="7"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="Point"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="Point"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="Point"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="22" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{8ad0c838-9845-4e87-88d7-4222d703f5c4}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="Point"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="Point"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="7"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="Point"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="Point"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="Point"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer pass="0" enabled="1" locked="0" id="{358cf78f-0827-4563-90a2-287dcc41d797}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="0,0,0,255,rgb:0,0,0,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="2.25"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="23" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{8ad0c838-9845-4e87-88d7-4222d703f5c4}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="Point"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="Point"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="0,0,0,255,rgb:0,0,0,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="7"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="Point"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="Point"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="Point"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="24" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{8ad0c838-9845-4e87-88d7-4222d703f5c4}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="Point"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="Point"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="7"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="Point"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="Point"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="Point"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="25" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{8ad0c838-9845-4e87-88d7-4222d703f5c4}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="Point"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="Point"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="7"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="Point"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="Point"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="Point"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer pass="0" enabled="1" locked="0" id="{358cf78f-0827-4563-90a2-287dcc41d797}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="0,0,0,255,rgb:0,0,0,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="2.25"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="26" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{91533b6d-d7a6-450e-8706-eac1f6a25d34}" class="ArrowLine">
          <Option type="Map">
            <Option name="arrow_start_width" type="QString" value="1"/>
            <Option name="arrow_start_width_unit" type="QString" value="MM"/>
            <Option name="arrow_start_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="arrow_type" type="QString" value="0"/>
            <Option name="arrow_width" type="QString" value="0"/>
            <Option name="arrow_width_unit" type="QString" value="Point"/>
            <Option name="arrow_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_length" type="QString" value="10"/>
            <Option name="head_length_unit" type="QString" value="Point"/>
            <Option name="head_length_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_thickness" type="QString" value="10"/>
            <Option name="head_thickness_unit" type="QString" value="Point"/>
            <Option name="head_thickness_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_type" type="QString" value="2"/>
            <Option name="is_curved" type="QString" value="1"/>
            <Option name="is_repeated" type="QString" value="1"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_unit" type="QString" value="Point"/>
            <Option name="offset_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="ring_filter" type="QString" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@26@0" type="fill" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{4ca734c4-5a47-4d49-a06a-7509f417212d}" class="SimpleFill">
              <Option type="Map">
                <Option name="border_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="offset" type="QString" value="0,0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="outline_color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
                <Option name="outline_style" type="QString" value="no"/>
                <Option name="outline_width" type="QString" value="0"/>
                <Option name="outline_width_unit" type="QString" value="Point"/>
                <Option name="style" type="QString" value="solid"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer pass="0" enabled="1" locked="0" id="{622dfad4-c787-40f2-b02a-3acdfb1e35b4}" class="GeometryGenerator">
          <Option type="Map">
            <Option name="SymbolType" type="QString" value="Line"/>
            <Option name="geometryModifier" type="QString" value="CASE&#xa;    WHEN length($geometry) > ( (5 + 2) * 2 ) THEN&#xa;        line_substring(&#xa;            $geometry,&#xa;            (5 + 2),&#xa;            length($geometry) - (5 + 2)&#xa;        )&#xa;    ELSE&#xa;        $geometry&#xa;END&#xa;"/>
            <Option name="units" type="QString" value="Point"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@26@1" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{410325a0-e6d3-4692-8772-82224a61351d}" class="HashLine">
              <Option type="Map">
                <Option name="average_angle_length" type="QString" value="4"/>
                <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="average_angle_unit" type="QString" value="Point"/>
                <Option name="hash_angle" type="QString" value="90"/>
                <Option name="hash_length" type="QString" value="1"/>
                <Option name="hash_length_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="hash_length_unit" type="QString" value="Point"/>
                <Option name="interval" type="QString" value="12"/>
                <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="interval_unit" type="QString" value="Point"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_along_line" type="QString" value="0"/>
                <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_along_line_unit" type="QString" value="Point"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="place_on_every_part" type="bool" value="true"/>
                <Option name="placements" type="QString" value="Interval"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="rotate" type="QString" value="1"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
              <symbol force_rhr="0" is_animated="0" name="@@26@1@0" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" type="QString" value=""/>
                    <Option name="properties"/>
                    <Option name="type" type="QString" value="collection"/>
                  </Option>
                </data_defined_properties>
                <layer pass="0" enabled="1" locked="0" id="{98bf797c-2285-4ed3-97b8-1716b341c8c4}" class="SimpleLine">
                  <Option type="Map">
                    <Option name="align_dash_pattern" type="QString" value="0"/>
                    <Option name="capstyle" type="QString" value="square"/>
                    <Option name="customdash" type="QString" value="5;2"/>
                    <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="customdash_unit" type="QString" value="Point"/>
                    <Option name="dash_pattern_offset" type="QString" value="0"/>
                    <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="dash_pattern_offset_unit" type="QString" value="Point"/>
                    <Option name="draw_inside_polygon" type="QString" value="0"/>
                    <Option name="joinstyle" type="QString" value="bevel"/>
                    <Option name="line_color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
                    <Option name="line_style" type="QString" value="solid"/>
                    <Option name="line_width" type="QString" value="7"/>
                    <Option name="line_width_unit" type="QString" value="Point"/>
                    <Option name="offset" type="QString" value="0"/>
                    <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="offset_unit" type="QString" value="Point"/>
                    <Option name="ring_filter" type="QString" value="0"/>
                    <Option name="trim_distance_end" type="QString" value="0"/>
                    <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="trim_distance_end_unit" type="QString" value="Point"/>
                    <Option name="trim_distance_start" type="QString" value="0"/>
                    <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="trim_distance_start_unit" type="QString" value="Point"/>
                    <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                    <Option name="use_custom_dash" type="QString" value="0"/>
                    <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="27" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{91533b6d-d7a6-450e-8706-eac1f6a25d34}" class="ArrowLine">
          <Option type="Map">
            <Option name="arrow_start_width" type="QString" value="1"/>
            <Option name="arrow_start_width_unit" type="QString" value="MM"/>
            <Option name="arrow_start_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="arrow_type" type="QString" value="0"/>
            <Option name="arrow_width" type="QString" value="0"/>
            <Option name="arrow_width_unit" type="QString" value="Point"/>
            <Option name="arrow_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_length" type="QString" value="10"/>
            <Option name="head_length_unit" type="QString" value="Point"/>
            <Option name="head_length_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_thickness" type="QString" value="10"/>
            <Option name="head_thickness_unit" type="QString" value="Point"/>
            <Option name="head_thickness_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_type" type="QString" value="2"/>
            <Option name="is_curved" type="QString" value="1"/>
            <Option name="is_repeated" type="QString" value="1"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_unit" type="QString" value="Point"/>
            <Option name="offset_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="ring_filter" type="QString" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@27@0" type="fill" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{4ca734c4-5a47-4d49-a06a-7509f417212d}" class="SimpleFill">
              <Option type="Map">
                <Option name="border_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="offset" type="QString" value="0,0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="outline_color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
                <Option name="outline_style" type="QString" value="no"/>
                <Option name="outline_width" type="QString" value="0"/>
                <Option name="outline_width_unit" type="QString" value="Point"/>
                <Option name="style" type="QString" value="solid"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer pass="0" enabled="1" locked="0" id="{622dfad4-c787-40f2-b02a-3acdfb1e35b4}" class="GeometryGenerator">
          <Option type="Map">
            <Option name="SymbolType" type="QString" value="Line"/>
            <Option name="geometryModifier" type="QString" value="CASE&#xa;    WHEN length($geometry) > ( (5 + 2) * 2 ) THEN&#xa;        line_substring(&#xa;            $geometry,&#xa;            (5 + 2),&#xa;            length($geometry) - (5 + 2)&#xa;        )&#xa;    ELSE&#xa;        $geometry&#xa;END&#xa;"/>
            <Option name="units" type="QString" value="Point"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@27@1" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{410325a0-e6d3-4692-8772-82224a61351d}" class="HashLine">
              <Option type="Map">
                <Option name="average_angle_length" type="QString" value="4"/>
                <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="average_angle_unit" type="QString" value="Point"/>
                <Option name="hash_angle" type="QString" value="90"/>
                <Option name="hash_length" type="QString" value="1"/>
                <Option name="hash_length_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="hash_length_unit" type="QString" value="Point"/>
                <Option name="interval" type="QString" value="12"/>
                <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="interval_unit" type="QString" value="Point"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_along_line" type="QString" value="0"/>
                <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_along_line_unit" type="QString" value="Point"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="place_on_every_part" type="bool" value="true"/>
                <Option name="placements" type="QString" value="Interval"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="rotate" type="QString" value="1"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
              <symbol force_rhr="0" is_animated="0" name="@@27@1@0" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" type="QString" value=""/>
                    <Option name="properties"/>
                    <Option name="type" type="QString" value="collection"/>
                  </Option>
                </data_defined_properties>
                <layer pass="0" enabled="1" locked="0" id="{98bf797c-2285-4ed3-97b8-1716b341c8c4}" class="SimpleLine">
                  <Option type="Map">
                    <Option name="align_dash_pattern" type="QString" value="0"/>
                    <Option name="capstyle" type="QString" value="square"/>
                    <Option name="customdash" type="QString" value="5;2"/>
                    <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="customdash_unit" type="QString" value="Point"/>
                    <Option name="dash_pattern_offset" type="QString" value="0"/>
                    <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="dash_pattern_offset_unit" type="QString" value="Point"/>
                    <Option name="draw_inside_polygon" type="QString" value="0"/>
                    <Option name="joinstyle" type="QString" value="bevel"/>
                    <Option name="line_color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
                    <Option name="line_style" type="QString" value="solid"/>
                    <Option name="line_width" type="QString" value="7"/>
                    <Option name="line_width_unit" type="QString" value="Point"/>
                    <Option name="offset" type="QString" value="0"/>
                    <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="offset_unit" type="QString" value="Point"/>
                    <Option name="ring_filter" type="QString" value="0"/>
                    <Option name="trim_distance_end" type="QString" value="0"/>
                    <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="trim_distance_end_unit" type="QString" value="Point"/>
                    <Option name="trim_distance_start" type="QString" value="0"/>
                    <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="trim_distance_start_unit" type="QString" value="Point"/>
                    <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                    <Option name="use_custom_dash" type="QString" value="0"/>
                    <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="28" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{622dfad4-c787-40f2-b02a-3acdfb1e35b4}" class="GeometryGenerator">
          <Option type="Map">
            <Option name="SymbolType" type="QString" value="Line"/>
            <Option name="geometryModifier" type="QString" value="CASE&#xa;    WHEN length($geometry) > ( (5 + 2) * 2 ) THEN&#xa;        line_substring(&#xa;            $geometry,&#xa;            (5 + 2),&#xa;            length($geometry) - (5 + 2)&#xa;        )&#xa;    ELSE&#xa;        $geometry&#xa;END&#xa;"/>
            <Option name="units" type="QString" value="Point"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@28@0" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{410325a0-e6d3-4692-8772-82224a61351d}" class="HashLine">
              <Option type="Map">
                <Option name="average_angle_length" type="QString" value="4"/>
                <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="average_angle_unit" type="QString" value="Point"/>
                <Option name="hash_angle" type="QString" value="90"/>
                <Option name="hash_length" type="QString" value="3"/>
                <Option name="hash_length_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="hash_length_unit" type="QString" value="Point"/>
                <Option name="interval" type="QString" value="15"/>
                <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="interval_unit" type="QString" value="Point"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_along_line" type="QString" value="0"/>
                <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_along_line_unit" type="QString" value="Point"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="place_on_every_part" type="bool" value="true"/>
                <Option name="placements" type="QString" value="Interval"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="rotate" type="QString" value="1"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
              <symbol force_rhr="0" is_animated="0" name="@@28@0@0" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" type="QString" value=""/>
                    <Option name="properties"/>
                    <Option name="type" type="QString" value="collection"/>
                  </Option>
                </data_defined_properties>
                <layer pass="0" enabled="1" locked="0" id="{98bf797c-2285-4ed3-97b8-1716b341c8c4}" class="SimpleLine">
                  <Option type="Map">
                    <Option name="align_dash_pattern" type="QString" value="0"/>
                    <Option name="capstyle" type="QString" value="square"/>
                    <Option name="customdash" type="QString" value="5;2"/>
                    <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="customdash_unit" type="QString" value="Point"/>
                    <Option name="dash_pattern_offset" type="QString" value="0"/>
                    <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="dash_pattern_offset_unit" type="QString" value="Point"/>
                    <Option name="draw_inside_polygon" type="QString" value="0"/>
                    <Option name="joinstyle" type="QString" value="bevel"/>
                    <Option name="line_color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
                    <Option name="line_style" type="QString" value="solid"/>
                    <Option name="line_width" type="QString" value="7"/>
                    <Option name="line_width_unit" type="QString" value="Point"/>
                    <Option name="offset" type="QString" value="0"/>
                    <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="offset_unit" type="QString" value="Point"/>
                    <Option name="ring_filter" type="QString" value="0"/>
                    <Option name="trim_distance_end" type="QString" value="0"/>
                    <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="trim_distance_end_unit" type="QString" value="Point"/>
                    <Option name="trim_distance_start" type="QString" value="0"/>
                    <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="trim_distance_start_unit" type="QString" value="Point"/>
                    <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                    <Option name="use_custom_dash" type="QString" value="0"/>
                    <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="29" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{622dfad4-c787-40f2-b02a-3acdfb1e35b4}" class="GeometryGenerator">
          <Option type="Map">
            <Option name="SymbolType" type="QString" value="Line"/>
            <Option name="geometryModifier" type="QString" value="CASE&#xa;    WHEN length($geometry) > ( (5 + 2) * 2 ) THEN&#xa;        line_substring(&#xa;            $geometry,&#xa;            (5 + 2),&#xa;            length($geometry) - (5 + 2)&#xa;        )&#xa;    ELSE&#xa;        $geometry&#xa;END&#xa;"/>
            <Option name="units" type="QString" value="Point"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@29@0" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{410325a0-e6d3-4692-8772-82224a61351d}" class="HashLine">
              <Option type="Map">
                <Option name="average_angle_length" type="QString" value="4"/>
                <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="average_angle_unit" type="QString" value="Point"/>
                <Option name="hash_angle" type="QString" value="90"/>
                <Option name="hash_length" type="QString" value="0.5"/>
                <Option name="hash_length_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="hash_length_unit" type="QString" value="Point"/>
                <Option name="interval" type="QString" value="12"/>
                <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="interval_unit" type="QString" value="Point"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_along_line" type="QString" value="0"/>
                <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_along_line_unit" type="QString" value="Point"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="place_on_every_part" type="bool" value="true"/>
                <Option name="placements" type="QString" value="Interval"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="rotate" type="QString" value="1"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
              <symbol force_rhr="0" is_animated="0" name="@@29@0@0" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" type="QString" value=""/>
                    <Option name="properties"/>
                    <Option name="type" type="QString" value="collection"/>
                  </Option>
                </data_defined_properties>
                <layer pass="0" enabled="1" locked="0" id="{98bf797c-2285-4ed3-97b8-1716b341c8c4}" class="SimpleLine">
                  <Option type="Map">
                    <Option name="align_dash_pattern" type="QString" value="0"/>
                    <Option name="capstyle" type="QString" value="square"/>
                    <Option name="customdash" type="QString" value="5;2"/>
                    <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="customdash_unit" type="QString" value="Point"/>
                    <Option name="dash_pattern_offset" type="QString" value="0"/>
                    <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="dash_pattern_offset_unit" type="QString" value="Point"/>
                    <Option name="draw_inside_polygon" type="QString" value="0"/>
                    <Option name="joinstyle" type="QString" value="bevel"/>
                    <Option name="line_color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
                    <Option name="line_style" type="QString" value="solid"/>
                    <Option name="line_width" type="QString" value="7"/>
                    <Option name="line_width_unit" type="QString" value="Point"/>
                    <Option name="offset" type="QString" value="0"/>
                    <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="offset_unit" type="QString" value="Point"/>
                    <Option name="ring_filter" type="QString" value="0"/>
                    <Option name="trim_distance_end" type="QString" value="0"/>
                    <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="trim_distance_end_unit" type="QString" value="Point"/>
                    <Option name="trim_distance_start" type="QString" value="0"/>
                    <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="trim_distance_start_unit" type="QString" value="Point"/>
                    <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                    <Option name="use_custom_dash" type="QString" value="0"/>
                    <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="3" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{c1fbaa3b-6edf-46d1-be03-12db49ccc062}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="0,0,0,255,rgb:0,0,0,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="7"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="30" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{583d8817-83d0-4417-a21c-bc8a0f5962c3}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="1"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="2"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="Point"/>
            <Option name="trim_distance_start" type="QString" value="2"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="Point"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer pass="0" enabled="1" locked="0" id="{61921724-1c3f-41d4-b76c-2b6311851808}" class="ArrowLine">
          <Option type="Map">
            <Option name="arrow_start_width" type="QString" value="1"/>
            <Option name="arrow_start_width_unit" type="QString" value="MM"/>
            <Option name="arrow_start_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="arrow_type" type="QString" value="0"/>
            <Option name="arrow_width" type="QString" value="1"/>
            <Option name="arrow_width_unit" type="QString" value="Point"/>
            <Option name="arrow_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_length" type="QString" value="10"/>
            <Option name="head_length_unit" type="QString" value="Point"/>
            <Option name="head_length_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_thickness" type="QString" value="10"/>
            <Option name="head_thickness_unit" type="QString" value="Point"/>
            <Option name="head_thickness_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_type" type="QString" value="2"/>
            <Option name="is_curved" type="QString" value="1"/>
            <Option name="is_repeated" type="QString" value="1"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="offset_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="ring_filter" type="QString" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@30@1" type="fill" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{453c2540-89fc-4a30-af74-a6ecefb378f9}" class="SimpleFill">
              <Option type="Map">
                <Option name="border_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="offset" type="QString" value="0,0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="MM"/>
                <Option name="outline_color" type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1"/>
                <Option name="outline_style" type="QString" value="no"/>
                <Option name="outline_width" type="QString" value="0"/>
                <Option name="outline_width_unit" type="QString" value="Point"/>
                <Option name="style" type="QString" value="solid"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer pass="0" enabled="1" locked="0" id="{be35e3da-0861-4706-908f-d2ac57c7331b}" class="GeometryGenerator">
          <Option type="Map">
            <Option name="SymbolType" type="QString" value="Line"/>
            <Option name="geometryModifier" type="QString" value="@geometry"/>
            <Option name="units" type="QString" value="MapUnit"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@30@2" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{df7b1142-8c98-4ffe-9245-df391b5cc6ac}" class="HashLine">
              <Option type="Map">
                <Option name="average_angle_length" type="QString" value="4"/>
                <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="average_angle_unit" type="QString" value="MM"/>
                <Option name="hash_angle" type="QString" value="0"/>
                <Option name="hash_length" type="QString" value="3"/>
                <Option name="hash_length_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="hash_length_unit" type="QString" value="MM"/>
                <Option name="interval" type="QString" value="4"/>
                <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="interval_unit" type="QString" value="Point"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_along_line" type="QString" value="0"/>
                <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_along_line_unit" type="QString" value="MM"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="MM"/>
                <Option name="place_on_every_part" type="bool" value="true"/>
                <Option name="placements" type="QString" value="Interval|LastVertex|FirstVertex"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="rotate" type="QString" value="1"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
              <symbol force_rhr="0" is_animated="0" name="@@30@2@0" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" type="QString" value=""/>
                    <Option name="properties"/>
                    <Option name="type" type="QString" value="collection"/>
                  </Option>
                </data_defined_properties>
                <layer pass="0" enabled="1" locked="0" id="{8ece23c8-3575-4aab-82ae-f29f412552e6}" class="SimpleLine">
                  <Option type="Map">
                    <Option name="align_dash_pattern" type="QString" value="0"/>
                    <Option name="capstyle" type="QString" value="square"/>
                    <Option name="customdash" type="QString" value="5;2"/>
                    <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="customdash_unit" type="QString" value="Point"/>
                    <Option name="dash_pattern_offset" type="QString" value="0"/>
                    <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="dash_pattern_offset_unit" type="QString" value="Point"/>
                    <Option name="draw_inside_polygon" type="QString" value="0"/>
                    <Option name="joinstyle" type="QString" value="bevel"/>
                    <Option name="line_color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
                    <Option name="line_style" type="QString" value="solid"/>
                    <Option name="line_width" type="QString" value="1"/>
                    <Option name="line_width_unit" type="QString" value="Point"/>
                    <Option name="offset" type="QString" value="0"/>
                    <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="offset_unit" type="QString" value="Point"/>
                    <Option name="ring_filter" type="QString" value="0"/>
                    <Option name="trim_distance_end" type="QString" value="0"/>
                    <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="trim_distance_end_unit" type="QString" value="Point"/>
                    <Option name="trim_distance_start" type="QString" value="0"/>
                    <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="trim_distance_start_unit" type="QString" value="Point"/>
                    <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                    <Option name="use_custom_dash" type="QString" value="0"/>
                    <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="31" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{91533b6d-d7a6-450e-8706-eac1f6a25d34}" class="ArrowLine">
          <Option type="Map">
            <Option name="arrow_start_width" type="QString" value="1"/>
            <Option name="arrow_start_width_unit" type="QString" value="MM"/>
            <Option name="arrow_start_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="arrow_type" type="QString" value="0"/>
            <Option name="arrow_width" type="QString" value="0"/>
            <Option name="arrow_width_unit" type="QString" value="Point"/>
            <Option name="arrow_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_length" type="QString" value="10"/>
            <Option name="head_length_unit" type="QString" value="Point"/>
            <Option name="head_length_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_thickness" type="QString" value="10"/>
            <Option name="head_thickness_unit" type="QString" value="Point"/>
            <Option name="head_thickness_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_type" type="QString" value="2"/>
            <Option name="is_curved" type="QString" value="1"/>
            <Option name="is_repeated" type="QString" value="1"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_unit" type="QString" value="Point"/>
            <Option name="offset_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="ring_filter" type="QString" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@31@0" type="fill" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{4ca734c4-5a47-4d49-a06a-7509f417212d}" class="SimpleFill">
              <Option type="Map">
                <Option name="border_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="color" type="QString" value="0,0,0,255,rgb:0,0,0,1"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="offset" type="QString" value="0,0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="outline_color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
                <Option name="outline_style" type="QString" value="no"/>
                <Option name="outline_width" type="QString" value="0"/>
                <Option name="outline_width_unit" type="QString" value="Point"/>
                <Option name="style" type="QString" value="solid"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer pass="0" enabled="1" locked="0" id="{622dfad4-c787-40f2-b02a-3acdfb1e35b4}" class="GeometryGenerator">
          <Option type="Map">
            <Option name="SymbolType" type="QString" value="Line"/>
            <Option name="geometryModifier" type="QString" value="CASE&#xa;    WHEN length($geometry) > ( (5 + 2) * 2 ) THEN&#xa;        line_substring(&#xa;            $geometry,&#xa;            (5 + 2),&#xa;            length($geometry) - (5 + 2)&#xa;        )&#xa;    ELSE&#xa;        $geometry&#xa;END&#xa;"/>
            <Option name="units" type="QString" value="Point"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@31@1" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{410325a0-e6d3-4692-8772-82224a61351d}" class="HashLine">
              <Option type="Map">
                <Option name="average_angle_length" type="QString" value="4"/>
                <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="average_angle_unit" type="QString" value="Point"/>
                <Option name="hash_angle" type="QString" value="90"/>
                <Option name="hash_length" type="QString" value="1"/>
                <Option name="hash_length_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="hash_length_unit" type="QString" value="Point"/>
                <Option name="interval" type="QString" value="12"/>
                <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="interval_unit" type="QString" value="Point"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_along_line" type="QString" value="0"/>
                <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_along_line_unit" type="QString" value="Point"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="place_on_every_part" type="bool" value="true"/>
                <Option name="placements" type="QString" value="Interval"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="rotate" type="QString" value="1"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
              <symbol force_rhr="0" is_animated="0" name="@@31@1@0" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" type="QString" value=""/>
                    <Option name="properties"/>
                    <Option name="type" type="QString" value="collection"/>
                  </Option>
                </data_defined_properties>
                <layer pass="0" enabled="1" locked="0" id="{98bf797c-2285-4ed3-97b8-1716b341c8c4}" class="SimpleLine">
                  <Option type="Map">
                    <Option name="align_dash_pattern" type="QString" value="0"/>
                    <Option name="capstyle" type="QString" value="square"/>
                    <Option name="customdash" type="QString" value="5;2"/>
                    <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="customdash_unit" type="QString" value="Point"/>
                    <Option name="dash_pattern_offset" type="QString" value="0"/>
                    <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="dash_pattern_offset_unit" type="QString" value="Point"/>
                    <Option name="draw_inside_polygon" type="QString" value="0"/>
                    <Option name="joinstyle" type="QString" value="bevel"/>
                    <Option name="line_color" type="QString" value="0,0,0,255,rgb:0,0,0,1"/>
                    <Option name="line_style" type="QString" value="solid"/>
                    <Option name="line_width" type="QString" value="7"/>
                    <Option name="line_width_unit" type="QString" value="Point"/>
                    <Option name="offset" type="QString" value="0"/>
                    <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="offset_unit" type="QString" value="Point"/>
                    <Option name="ring_filter" type="QString" value="0"/>
                    <Option name="trim_distance_end" type="QString" value="0"/>
                    <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="trim_distance_end_unit" type="QString" value="Point"/>
                    <Option name="trim_distance_start" type="QString" value="0"/>
                    <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="trim_distance_start_unit" type="QString" value="Point"/>
                    <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                    <Option name="use_custom_dash" type="QString" value="0"/>
                    <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="32" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{91533b6d-d7a6-450e-8706-eac1f6a25d34}" class="ArrowLine">
          <Option type="Map">
            <Option name="arrow_start_width" type="QString" value="1"/>
            <Option name="arrow_start_width_unit" type="QString" value="MM"/>
            <Option name="arrow_start_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="arrow_type" type="QString" value="0"/>
            <Option name="arrow_width" type="QString" value="0"/>
            <Option name="arrow_width_unit" type="QString" value="Point"/>
            <Option name="arrow_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_length" type="QString" value="10"/>
            <Option name="head_length_unit" type="QString" value="Point"/>
            <Option name="head_length_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_thickness" type="QString" value="10"/>
            <Option name="head_thickness_unit" type="QString" value="Point"/>
            <Option name="head_thickness_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_type" type="QString" value="2"/>
            <Option name="is_curved" type="QString" value="1"/>
            <Option name="is_repeated" type="QString" value="1"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_unit" type="QString" value="Point"/>
            <Option name="offset_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="ring_filter" type="QString" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@32@0" type="fill" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{4ca734c4-5a47-4d49-a06a-7509f417212d}" class="SimpleFill">
              <Option type="Map">
                <Option name="border_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="offset" type="QString" value="0,0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="outline_color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
                <Option name="outline_style" type="QString" value="no"/>
                <Option name="outline_width" type="QString" value="0"/>
                <Option name="outline_width_unit" type="QString" value="Point"/>
                <Option name="style" type="QString" value="solid"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer pass="0" enabled="1" locked="0" id="{622dfad4-c787-40f2-b02a-3acdfb1e35b4}" class="GeometryGenerator">
          <Option type="Map">
            <Option name="SymbolType" type="QString" value="Line"/>
            <Option name="geometryModifier" type="QString" value="CASE&#xa;    WHEN length($geometry) > ( (5 + 2) * 2 ) THEN&#xa;        line_substring(&#xa;            $geometry,&#xa;            (5 + 2),&#xa;            length($geometry) - (5 + 2)&#xa;        )&#xa;    ELSE&#xa;        $geometry&#xa;END&#xa;"/>
            <Option name="units" type="QString" value="Point"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@32@1" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{410325a0-e6d3-4692-8772-82224a61351d}" class="HashLine">
              <Option type="Map">
                <Option name="average_angle_length" type="QString" value="4"/>
                <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="average_angle_unit" type="QString" value="Point"/>
                <Option name="hash_angle" type="QString" value="90"/>
                <Option name="hash_length" type="QString" value="1"/>
                <Option name="hash_length_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="hash_length_unit" type="QString" value="Point"/>
                <Option name="interval" type="QString" value="12"/>
                <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="interval_unit" type="QString" value="Point"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_along_line" type="QString" value="0"/>
                <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_along_line_unit" type="QString" value="Point"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="place_on_every_part" type="bool" value="true"/>
                <Option name="placements" type="QString" value="Interval"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="rotate" type="QString" value="1"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
              <symbol force_rhr="0" is_animated="0" name="@@32@1@0" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" type="QString" value=""/>
                    <Option name="properties"/>
                    <Option name="type" type="QString" value="collection"/>
                  </Option>
                </data_defined_properties>
                <layer pass="0" enabled="1" locked="0" id="{98bf797c-2285-4ed3-97b8-1716b341c8c4}" class="SimpleLine">
                  <Option type="Map">
                    <Option name="align_dash_pattern" type="QString" value="0"/>
                    <Option name="capstyle" type="QString" value="square"/>
                    <Option name="customdash" type="QString" value="5;2"/>
                    <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="customdash_unit" type="QString" value="Point"/>
                    <Option name="dash_pattern_offset" type="QString" value="0"/>
                    <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="dash_pattern_offset_unit" type="QString" value="Point"/>
                    <Option name="draw_inside_polygon" type="QString" value="0"/>
                    <Option name="joinstyle" type="QString" value="bevel"/>
                    <Option name="line_color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
                    <Option name="line_style" type="QString" value="solid"/>
                    <Option name="line_width" type="QString" value="7"/>
                    <Option name="line_width_unit" type="QString" value="Point"/>
                    <Option name="offset" type="QString" value="0"/>
                    <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="offset_unit" type="QString" value="Point"/>
                    <Option name="ring_filter" type="QString" value="0"/>
                    <Option name="trim_distance_end" type="QString" value="0"/>
                    <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="trim_distance_end_unit" type="QString" value="Point"/>
                    <Option name="trim_distance_start" type="QString" value="0"/>
                    <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="trim_distance_start_unit" type="QString" value="Point"/>
                    <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                    <Option name="use_custom_dash" type="QString" value="0"/>
                    <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="33" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{91533b6d-d7a6-450e-8706-eac1f6a25d34}" class="ArrowLine">
          <Option type="Map">
            <Option name="arrow_start_width" type="QString" value="1"/>
            <Option name="arrow_start_width_unit" type="QString" value="MM"/>
            <Option name="arrow_start_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="arrow_type" type="QString" value="0"/>
            <Option name="arrow_width" type="QString" value="0"/>
            <Option name="arrow_width_unit" type="QString" value="Point"/>
            <Option name="arrow_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_length" type="QString" value="10"/>
            <Option name="head_length_unit" type="QString" value="Point"/>
            <Option name="head_length_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_thickness" type="QString" value="10"/>
            <Option name="head_thickness_unit" type="QString" value="Point"/>
            <Option name="head_thickness_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_type" type="QString" value="2"/>
            <Option name="is_curved" type="QString" value="1"/>
            <Option name="is_repeated" type="QString" value="1"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_unit" type="QString" value="Point"/>
            <Option name="offset_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="ring_filter" type="QString" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@33@0" type="fill" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{4ca734c4-5a47-4d49-a06a-7509f417212d}" class="SimpleFill">
              <Option type="Map">
                <Option name="border_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="offset" type="QString" value="0,0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="outline_color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
                <Option name="outline_style" type="QString" value="no"/>
                <Option name="outline_width" type="QString" value="0"/>
                <Option name="outline_width_unit" type="QString" value="Point"/>
                <Option name="style" type="QString" value="solid"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer pass="0" enabled="1" locked="0" id="{622dfad4-c787-40f2-b02a-3acdfb1e35b4}" class="GeometryGenerator">
          <Option type="Map">
            <Option name="SymbolType" type="QString" value="Line"/>
            <Option name="geometryModifier" type="QString" value="CASE&#xa;    WHEN length($geometry) > ( (5 + 2) * 2 ) THEN&#xa;        line_substring(&#xa;            $geometry,&#xa;            (5 + 2),&#xa;            length($geometry) - (5 + 2)&#xa;        )&#xa;    ELSE&#xa;        $geometry&#xa;END&#xa;"/>
            <Option name="units" type="QString" value="Point"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@33@1" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{410325a0-e6d3-4692-8772-82224a61351d}" class="HashLine">
              <Option type="Map">
                <Option name="average_angle_length" type="QString" value="4"/>
                <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="average_angle_unit" type="QString" value="Point"/>
                <Option name="hash_angle" type="QString" value="90"/>
                <Option name="hash_length" type="QString" value="1"/>
                <Option name="hash_length_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="hash_length_unit" type="QString" value="Point"/>
                <Option name="interval" type="QString" value="12"/>
                <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="interval_unit" type="QString" value="Point"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_along_line" type="QString" value="0"/>
                <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_along_line_unit" type="QString" value="Point"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="place_on_every_part" type="bool" value="true"/>
                <Option name="placements" type="QString" value="Interval"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="rotate" type="QString" value="1"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
              <symbol force_rhr="0" is_animated="0" name="@@33@1@0" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" type="QString" value=""/>
                    <Option name="properties"/>
                    <Option name="type" type="QString" value="collection"/>
                  </Option>
                </data_defined_properties>
                <layer pass="0" enabled="1" locked="0" id="{98bf797c-2285-4ed3-97b8-1716b341c8c4}" class="SimpleLine">
                  <Option type="Map">
                    <Option name="align_dash_pattern" type="QString" value="0"/>
                    <Option name="capstyle" type="QString" value="square"/>
                    <Option name="customdash" type="QString" value="5;2"/>
                    <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="customdash_unit" type="QString" value="Point"/>
                    <Option name="dash_pattern_offset" type="QString" value="0"/>
                    <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="dash_pattern_offset_unit" type="QString" value="Point"/>
                    <Option name="draw_inside_polygon" type="QString" value="0"/>
                    <Option name="joinstyle" type="QString" value="bevel"/>
                    <Option name="line_color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
                    <Option name="line_style" type="QString" value="solid"/>
                    <Option name="line_width" type="QString" value="7"/>
                    <Option name="line_width_unit" type="QString" value="Point"/>
                    <Option name="offset" type="QString" value="0"/>
                    <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="offset_unit" type="QString" value="Point"/>
                    <Option name="ring_filter" type="QString" value="0"/>
                    <Option name="trim_distance_end" type="QString" value="0"/>
                    <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="trim_distance_end_unit" type="QString" value="Point"/>
                    <Option name="trim_distance_start" type="QString" value="0"/>
                    <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="trim_distance_start_unit" type="QString" value="Point"/>
                    <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                    <Option name="use_custom_dash" type="QString" value="0"/>
                    <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="34" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{91533b6d-d7a6-450e-8706-eac1f6a25d34}" class="ArrowLine">
          <Option type="Map">
            <Option name="arrow_start_width" type="QString" value="1"/>
            <Option name="arrow_start_width_unit" type="QString" value="MM"/>
            <Option name="arrow_start_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="arrow_type" type="QString" value="0"/>
            <Option name="arrow_width" type="QString" value="0"/>
            <Option name="arrow_width_unit" type="QString" value="Point"/>
            <Option name="arrow_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_length" type="QString" value="10"/>
            <Option name="head_length_unit" type="QString" value="Point"/>
            <Option name="head_length_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_thickness" type="QString" value="10"/>
            <Option name="head_thickness_unit" type="QString" value="Point"/>
            <Option name="head_thickness_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_type" type="QString" value="2"/>
            <Option name="is_curved" type="QString" value="1"/>
            <Option name="is_repeated" type="QString" value="1"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_unit" type="QString" value="Point"/>
            <Option name="offset_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="ring_filter" type="QString" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@34@0" type="fill" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{4ca734c4-5a47-4d49-a06a-7509f417212d}" class="SimpleFill">
              <Option type="Map">
                <Option name="border_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="offset" type="QString" value="0,0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="outline_color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
                <Option name="outline_style" type="QString" value="no"/>
                <Option name="outline_width" type="QString" value="0"/>
                <Option name="outline_width_unit" type="QString" value="Point"/>
                <Option name="style" type="QString" value="solid"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer pass="0" enabled="1" locked="0" id="{622dfad4-c787-40f2-b02a-3acdfb1e35b4}" class="GeometryGenerator">
          <Option type="Map">
            <Option name="SymbolType" type="QString" value="Line"/>
            <Option name="geometryModifier" type="QString" value="CASE&#xa;    WHEN length($geometry) > ( (5 + 2) * 2 ) THEN&#xa;        line_substring(&#xa;            $geometry,&#xa;            (5 + 2),&#xa;            length($geometry) - (5 + 2)&#xa;        )&#xa;    ELSE&#xa;        $geometry&#xa;END&#xa;"/>
            <Option name="units" type="QString" value="Point"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@34@1" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{410325a0-e6d3-4692-8772-82224a61351d}" class="HashLine">
              <Option type="Map">
                <Option name="average_angle_length" type="QString" value="4"/>
                <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="average_angle_unit" type="QString" value="Point"/>
                <Option name="hash_angle" type="QString" value="90"/>
                <Option name="hash_length" type="QString" value="1"/>
                <Option name="hash_length_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="hash_length_unit" type="QString" value="Point"/>
                <Option name="interval" type="QString" value="12"/>
                <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="interval_unit" type="QString" value="Point"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_along_line" type="QString" value="0"/>
                <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_along_line_unit" type="QString" value="Point"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="place_on_every_part" type="bool" value="true"/>
                <Option name="placements" type="QString" value="Interval"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="rotate" type="QString" value="1"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
              <symbol force_rhr="0" is_animated="0" name="@@34@1@0" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" type="QString" value=""/>
                    <Option name="properties"/>
                    <Option name="type" type="QString" value="collection"/>
                  </Option>
                </data_defined_properties>
                <layer pass="0" enabled="1" locked="0" id="{98bf797c-2285-4ed3-97b8-1716b341c8c4}" class="SimpleLine">
                  <Option type="Map">
                    <Option name="align_dash_pattern" type="QString" value="0"/>
                    <Option name="capstyle" type="QString" value="square"/>
                    <Option name="customdash" type="QString" value="5;2"/>
                    <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="customdash_unit" type="QString" value="Point"/>
                    <Option name="dash_pattern_offset" type="QString" value="0"/>
                    <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="dash_pattern_offset_unit" type="QString" value="Point"/>
                    <Option name="draw_inside_polygon" type="QString" value="0"/>
                    <Option name="joinstyle" type="QString" value="bevel"/>
                    <Option name="line_color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
                    <Option name="line_style" type="QString" value="solid"/>
                    <Option name="line_width" type="QString" value="7"/>
                    <Option name="line_width_unit" type="QString" value="Point"/>
                    <Option name="offset" type="QString" value="0"/>
                    <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="offset_unit" type="QString" value="Point"/>
                    <Option name="ring_filter" type="QString" value="0"/>
                    <Option name="trim_distance_end" type="QString" value="0"/>
                    <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="trim_distance_end_unit" type="QString" value="Point"/>
                    <Option name="trim_distance_start" type="QString" value="0"/>
                    <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="trim_distance_start_unit" type="QString" value="Point"/>
                    <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                    <Option name="use_custom_dash" type="QString" value="0"/>
                    <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="35" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{93c298c0-123a-4d08-9582-9e409d858110}" class="ArrowLine">
          <Option type="Map">
            <Option name="arrow_start_width" type="QString" value="1"/>
            <Option name="arrow_start_width_unit" type="QString" value="MM"/>
            <Option name="arrow_start_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="arrow_type" type="QString" value="0"/>
            <Option name="arrow_width" type="QString" value="7"/>
            <Option name="arrow_width_unit" type="QString" value="Point"/>
            <Option name="arrow_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_length" type="QString" value="10"/>
            <Option name="head_length_unit" type="QString" value="Point"/>
            <Option name="head_length_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_thickness" type="QString" value="10"/>
            <Option name="head_thickness_unit" type="QString" value="Point"/>
            <Option name="head_thickness_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_type" type="QString" value="2"/>
            <Option name="is_curved" type="QString" value="1"/>
            <Option name="is_repeated" type="QString" value="1"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="offset_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="ring_filter" type="QString" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@35@0" type="fill" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{1c9e73ae-d42d-4bae-a385-2d99a32d32f9}" class="SimpleFill">
              <Option type="Map">
                <Option name="border_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="color" type="QString" value="25,104,64,255,rgb:0.09803921568627451,0.40784313725490196,0.25098039215686274,1"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="offset" type="QString" value="0,0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="MM"/>
                <Option name="outline_color" type="QString" value="213,180,60,255,rgb:0.83529411764705885,0.70588235294117652,0.23529411764705882,1"/>
                <Option name="outline_style" type="QString" value="no"/>
                <Option name="outline_width" type="QString" value="0"/>
                <Option name="outline_width_unit" type="QString" value="MM"/>
                <Option name="style" type="QString" value="solid"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="36" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{91533b6d-d7a6-450e-8706-eac1f6a25d34}" class="ArrowLine">
          <Option type="Map">
            <Option name="arrow_start_width" type="QString" value="1"/>
            <Option name="arrow_start_width_unit" type="QString" value="MM"/>
            <Option name="arrow_start_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="arrow_type" type="QString" value="0"/>
            <Option name="arrow_width" type="QString" value="0"/>
            <Option name="arrow_width_unit" type="QString" value="Point"/>
            <Option name="arrow_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_length" type="QString" value="10"/>
            <Option name="head_length_unit" type="QString" value="Point"/>
            <Option name="head_length_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_thickness" type="QString" value="10"/>
            <Option name="head_thickness_unit" type="QString" value="Point"/>
            <Option name="head_thickness_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_type" type="QString" value="2"/>
            <Option name="is_curved" type="QString" value="1"/>
            <Option name="is_repeated" type="QString" value="1"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_unit" type="QString" value="Point"/>
            <Option name="offset_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="ring_filter" type="QString" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@36@0" type="fill" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{4ca734c4-5a47-4d49-a06a-7509f417212d}" class="SimpleFill">
              <Option type="Map">
                <Option name="border_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="color" type="QString" value="25,104,64,255,rgb:0.09803921568627451,0.40784313725490196,0.25098039215686274,1"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="offset" type="QString" value="0,0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="outline_color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
                <Option name="outline_style" type="QString" value="no"/>
                <Option name="outline_width" type="QString" value="0"/>
                <Option name="outline_width_unit" type="QString" value="Point"/>
                <Option name="style" type="QString" value="solid"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer pass="0" enabled="1" locked="0" id="{622dfad4-c787-40f2-b02a-3acdfb1e35b4}" class="GeometryGenerator">
          <Option type="Map">
            <Option name="SymbolType" type="QString" value="Line"/>
            <Option name="geometryModifier" type="QString" value="CASE&#xa;    WHEN length($geometry) > ( (5 + 2) * 2 ) THEN&#xa;        line_substring(&#xa;            $geometry,&#xa;            (5 + 2),&#xa;            length($geometry) - (5 + 2)&#xa;        )&#xa;    ELSE&#xa;        $geometry&#xa;END&#xa;"/>
            <Option name="units" type="QString" value="Point"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@36@1" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{410325a0-e6d3-4692-8772-82224a61351d}" class="HashLine">
              <Option type="Map">
                <Option name="average_angle_length" type="QString" value="4"/>
                <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="average_angle_unit" type="QString" value="Point"/>
                <Option name="hash_angle" type="QString" value="90"/>
                <Option name="hash_length" type="QString" value="1"/>
                <Option name="hash_length_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="hash_length_unit" type="QString" value="Point"/>
                <Option name="interval" type="QString" value="12"/>
                <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="interval_unit" type="QString" value="Point"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_along_line" type="QString" value="0"/>
                <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_along_line_unit" type="QString" value="Point"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="place_on_every_part" type="bool" value="true"/>
                <Option name="placements" type="QString" value="Interval"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="rotate" type="QString" value="1"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
              <symbol force_rhr="0" is_animated="0" name="@@36@1@0" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" type="QString" value=""/>
                    <Option name="properties"/>
                    <Option name="type" type="QString" value="collection"/>
                  </Option>
                </data_defined_properties>
                <layer pass="0" enabled="1" locked="0" id="{98bf797c-2285-4ed3-97b8-1716b341c8c4}" class="SimpleLine">
                  <Option type="Map">
                    <Option name="align_dash_pattern" type="QString" value="0"/>
                    <Option name="capstyle" type="QString" value="square"/>
                    <Option name="customdash" type="QString" value="5;2"/>
                    <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="customdash_unit" type="QString" value="Point"/>
                    <Option name="dash_pattern_offset" type="QString" value="0"/>
                    <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="dash_pattern_offset_unit" type="QString" value="Point"/>
                    <Option name="draw_inside_polygon" type="QString" value="0"/>
                    <Option name="joinstyle" type="QString" value="bevel"/>
                    <Option name="line_color" type="QString" value="25,104,64,255,rgb:0.09803921568627451,0.40784313725490196,0.25098039215686274,1"/>
                    <Option name="line_style" type="QString" value="solid"/>
                    <Option name="line_width" type="QString" value="7"/>
                    <Option name="line_width_unit" type="QString" value="Point"/>
                    <Option name="offset" type="QString" value="0"/>
                    <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="offset_unit" type="QString" value="Point"/>
                    <Option name="ring_filter" type="QString" value="0"/>
                    <Option name="trim_distance_end" type="QString" value="0"/>
                    <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="trim_distance_end_unit" type="QString" value="Point"/>
                    <Option name="trim_distance_start" type="QString" value="0"/>
                    <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="trim_distance_start_unit" type="QString" value="Point"/>
                    <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                    <Option name="use_custom_dash" type="QString" value="0"/>
                    <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="37" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{a1f5798e-b1ac-4301-a01c-4d2d9586ad2f}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="0,0,0,255,rgb:0,0,0,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="1"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="38" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{a1f5798e-b1ac-4301-a01c-4d2d9586ad2f}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="0,0,0,255,rgb:0,0,0,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="1"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="39" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{a1f5798e-b1ac-4301-a01c-4d2d9586ad2f}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="0,0,0,255,rgb:0,0,0,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="1"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="4" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{c1fbaa3b-6edf-46d1-be03-12db49ccc062}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="0,0,0,255,rgb:0,0,0,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="7"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="40" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{a1f5798e-b1ac-4301-a01c-4d2d9586ad2f}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="229,31,45,255,rgb:0.89803921568627454,0.12156862745098039,0.17647058823529413,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="1"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="41" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{a1f5798e-b1ac-4301-a01c-4d2d9586ad2f}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="229,31,45,255,rgb:0.89803921568627454,0.12156862745098039,0.17647058823529413,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="1"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="42" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{a1f5798e-b1ac-4301-a01c-4d2d9586ad2f}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="229,31,45,255,rgb:0.89803921568627454,0.12156862745098039,0.17647058823529413,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="1"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="43" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{91533b6d-d7a6-450e-8706-eac1f6a25d34}" class="ArrowLine">
          <Option type="Map">
            <Option name="arrow_start_width" type="QString" value="1"/>
            <Option name="arrow_start_width_unit" type="QString" value="MM"/>
            <Option name="arrow_start_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="arrow_type" type="QString" value="0"/>
            <Option name="arrow_width" type="QString" value="0"/>
            <Option name="arrow_width_unit" type="QString" value="Point"/>
            <Option name="arrow_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_length" type="QString" value="10"/>
            <Option name="head_length_unit" type="QString" value="Point"/>
            <Option name="head_length_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_thickness" type="QString" value="4"/>
            <Option name="head_thickness_unit" type="QString" value="Point"/>
            <Option name="head_thickness_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_type" type="QString" value="2"/>
            <Option name="is_curved" type="QString" value="1"/>
            <Option name="is_repeated" type="QString" value="1"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_unit" type="QString" value="Point"/>
            <Option name="offset_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="ring_filter" type="QString" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@43@0" type="fill" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{4ca734c4-5a47-4d49-a06a-7509f417212d}" class="SimpleFill">
              <Option type="Map">
                <Option name="border_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="offset" type="QString" value="0,0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="outline_color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
                <Option name="outline_style" type="QString" value="no"/>
                <Option name="outline_width" type="QString" value="0"/>
                <Option name="outline_width_unit" type="QString" value="Point"/>
                <Option name="style" type="QString" value="solid"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer pass="0" enabled="1" locked="0" id="{622dfad4-c787-40f2-b02a-3acdfb1e35b4}" class="GeometryGenerator">
          <Option type="Map">
            <Option name="SymbolType" type="QString" value="Line"/>
            <Option name="geometryModifier" type="QString" value="CASE&#xa;    WHEN length($geometry) > ( (5 + 2) * 2 ) THEN&#xa;        line_substring(&#xa;            $geometry,&#xa;            (5 + 2),&#xa;            length($geometry) - (5 + 2)&#xa;        )&#xa;    ELSE&#xa;        $geometry&#xa;END&#xa;"/>
            <Option name="units" type="QString" value="Point"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@43@1" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{410325a0-e6d3-4692-8772-82224a61351d}" class="HashLine">
              <Option type="Map">
                <Option name="average_angle_length" type="QString" value="4"/>
                <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="average_angle_unit" type="QString" value="Point"/>
                <Option name="hash_angle" type="QString" value="90"/>
                <Option name="hash_length" type="QString" value="1"/>
                <Option name="hash_length_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="hash_length_unit" type="QString" value="Point"/>
                <Option name="interval" type="QString" value="4"/>
                <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="interval_unit" type="QString" value="Point"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_along_line" type="QString" value="0"/>
                <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_along_line_unit" type="QString" value="Point"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="place_on_every_part" type="bool" value="true"/>
                <Option name="placements" type="QString" value="Interval"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="rotate" type="QString" value="1"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
              <symbol force_rhr="0" is_animated="0" name="@@43@1@0" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" type="QString" value=""/>
                    <Option name="properties"/>
                    <Option name="type" type="QString" value="collection"/>
                  </Option>
                </data_defined_properties>
                <layer pass="0" enabled="1" locked="0" id="{98bf797c-2285-4ed3-97b8-1716b341c8c4}" class="SimpleLine">
                  <Option type="Map">
                    <Option name="align_dash_pattern" type="QString" value="0"/>
                    <Option name="capstyle" type="QString" value="square"/>
                    <Option name="customdash" type="QString" value="5;2"/>
                    <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="customdash_unit" type="QString" value="Point"/>
                    <Option name="dash_pattern_offset" type="QString" value="0"/>
                    <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="dash_pattern_offset_unit" type="QString" value="Point"/>
                    <Option name="draw_inside_polygon" type="QString" value="0"/>
                    <Option name="joinstyle" type="QString" value="bevel"/>
                    <Option name="line_color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
                    <Option name="line_style" type="QString" value="solid"/>
                    <Option name="line_width" type="QString" value="1"/>
                    <Option name="line_width_unit" type="QString" value="Point"/>
                    <Option name="offset" type="QString" value="0"/>
                    <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="offset_unit" type="QString" value="Point"/>
                    <Option name="ring_filter" type="QString" value="0"/>
                    <Option name="trim_distance_end" type="QString" value="0"/>
                    <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="trim_distance_end_unit" type="QString" value="Point"/>
                    <Option name="trim_distance_start" type="QString" value="0"/>
                    <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="trim_distance_start_unit" type="QString" value="Point"/>
                    <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                    <Option name="use_custom_dash" type="QString" value="0"/>
                    <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="44" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{91533b6d-d7a6-450e-8706-eac1f6a25d34}" class="ArrowLine">
          <Option type="Map">
            <Option name="arrow_start_width" type="QString" value="1"/>
            <Option name="arrow_start_width_unit" type="QString" value="MM"/>
            <Option name="arrow_start_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="arrow_type" type="QString" value="0"/>
            <Option name="arrow_width" type="QString" value="0"/>
            <Option name="arrow_width_unit" type="QString" value="Point"/>
            <Option name="arrow_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_length" type="QString" value="10"/>
            <Option name="head_length_unit" type="QString" value="Point"/>
            <Option name="head_length_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_thickness" type="QString" value="4"/>
            <Option name="head_thickness_unit" type="QString" value="Point"/>
            <Option name="head_thickness_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_type" type="QString" value="2"/>
            <Option name="is_curved" type="QString" value="1"/>
            <Option name="is_repeated" type="QString" value="1"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_unit" type="QString" value="Point"/>
            <Option name="offset_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="ring_filter" type="QString" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@44@0" type="fill" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{4ca734c4-5a47-4d49-a06a-7509f417212d}" class="SimpleFill">
              <Option type="Map">
                <Option name="border_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="offset" type="QString" value="0,0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="outline_color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
                <Option name="outline_style" type="QString" value="no"/>
                <Option name="outline_width" type="QString" value="0"/>
                <Option name="outline_width_unit" type="QString" value="Point"/>
                <Option name="style" type="QString" value="solid"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer pass="0" enabled="1" locked="0" id="{622dfad4-c787-40f2-b02a-3acdfb1e35b4}" class="GeometryGenerator">
          <Option type="Map">
            <Option name="SymbolType" type="QString" value="Line"/>
            <Option name="geometryModifier" type="QString" value="CASE&#xa;    WHEN length($geometry) > ( (5 + 2) * 2 ) THEN&#xa;        line_substring(&#xa;            $geometry,&#xa;            (5 + 2),&#xa;            length($geometry) - (5 + 2)&#xa;        )&#xa;    ELSE&#xa;        $geometry&#xa;END&#xa;"/>
            <Option name="units" type="QString" value="Point"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@44@1" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{410325a0-e6d3-4692-8772-82224a61351d}" class="HashLine">
              <Option type="Map">
                <Option name="average_angle_length" type="QString" value="4"/>
                <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="average_angle_unit" type="QString" value="Point"/>
                <Option name="hash_angle" type="QString" value="90"/>
                <Option name="hash_length" type="QString" value="1"/>
                <Option name="hash_length_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="hash_length_unit" type="QString" value="Point"/>
                <Option name="interval" type="QString" value="4"/>
                <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="interval_unit" type="QString" value="Point"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_along_line" type="QString" value="0"/>
                <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_along_line_unit" type="QString" value="Point"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="place_on_every_part" type="bool" value="true"/>
                <Option name="placements" type="QString" value="Interval"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="rotate" type="QString" value="1"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
              <symbol force_rhr="0" is_animated="0" name="@@44@1@0" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" type="QString" value=""/>
                    <Option name="properties"/>
                    <Option name="type" type="QString" value="collection"/>
                  </Option>
                </data_defined_properties>
                <layer pass="0" enabled="1" locked="0" id="{98bf797c-2285-4ed3-97b8-1716b341c8c4}" class="SimpleLine">
                  <Option type="Map">
                    <Option name="align_dash_pattern" type="QString" value="0"/>
                    <Option name="capstyle" type="QString" value="square"/>
                    <Option name="customdash" type="QString" value="5;2"/>
                    <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="customdash_unit" type="QString" value="Point"/>
                    <Option name="dash_pattern_offset" type="QString" value="0"/>
                    <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="dash_pattern_offset_unit" type="QString" value="Point"/>
                    <Option name="draw_inside_polygon" type="QString" value="0"/>
                    <Option name="joinstyle" type="QString" value="bevel"/>
                    <Option name="line_color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
                    <Option name="line_style" type="QString" value="solid"/>
                    <Option name="line_width" type="QString" value="1"/>
                    <Option name="line_width_unit" type="QString" value="Point"/>
                    <Option name="offset" type="QString" value="0"/>
                    <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="offset_unit" type="QString" value="Point"/>
                    <Option name="ring_filter" type="QString" value="0"/>
                    <Option name="trim_distance_end" type="QString" value="0"/>
                    <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="trim_distance_end_unit" type="QString" value="Point"/>
                    <Option name="trim_distance_start" type="QString" value="0"/>
                    <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="trim_distance_start_unit" type="QString" value="Point"/>
                    <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                    <Option name="use_custom_dash" type="QString" value="0"/>
                    <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="45" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{91533b6d-d7a6-450e-8706-eac1f6a25d34}" class="ArrowLine">
          <Option type="Map">
            <Option name="arrow_start_width" type="QString" value="1"/>
            <Option name="arrow_start_width_unit" type="QString" value="MM"/>
            <Option name="arrow_start_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="arrow_type" type="QString" value="0"/>
            <Option name="arrow_width" type="QString" value="0"/>
            <Option name="arrow_width_unit" type="QString" value="Point"/>
            <Option name="arrow_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_length" type="QString" value="10"/>
            <Option name="head_length_unit" type="QString" value="Point"/>
            <Option name="head_length_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_thickness" type="QString" value="4"/>
            <Option name="head_thickness_unit" type="QString" value="Point"/>
            <Option name="head_thickness_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_type" type="QString" value="2"/>
            <Option name="is_curved" type="QString" value="1"/>
            <Option name="is_repeated" type="QString" value="1"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_unit" type="QString" value="Point"/>
            <Option name="offset_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="ring_filter" type="QString" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@45@0" type="fill" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{4ca734c4-5a47-4d49-a06a-7509f417212d}" class="SimpleFill">
              <Option type="Map">
                <Option name="border_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="offset" type="QString" value="0,0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="outline_color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
                <Option name="outline_style" type="QString" value="no"/>
                <Option name="outline_width" type="QString" value="0"/>
                <Option name="outline_width_unit" type="QString" value="Point"/>
                <Option name="style" type="QString" value="solid"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer pass="0" enabled="1" locked="0" id="{622dfad4-c787-40f2-b02a-3acdfb1e35b4}" class="GeometryGenerator">
          <Option type="Map">
            <Option name="SymbolType" type="QString" value="Line"/>
            <Option name="geometryModifier" type="QString" value="CASE&#xa;    WHEN length($geometry) > ( (5 + 2) * 2 ) THEN&#xa;        line_substring(&#xa;            $geometry,&#xa;            (5 + 2),&#xa;            length($geometry) - (5 + 2)&#xa;        )&#xa;    ELSE&#xa;        $geometry&#xa;END&#xa;"/>
            <Option name="units" type="QString" value="Point"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@45@1" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{410325a0-e6d3-4692-8772-82224a61351d}" class="HashLine">
              <Option type="Map">
                <Option name="average_angle_length" type="QString" value="4"/>
                <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="average_angle_unit" type="QString" value="Point"/>
                <Option name="hash_angle" type="QString" value="90"/>
                <Option name="hash_length" type="QString" value="1"/>
                <Option name="hash_length_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="hash_length_unit" type="QString" value="Point"/>
                <Option name="interval" type="QString" value="4"/>
                <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="interval_unit" type="QString" value="Point"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_along_line" type="QString" value="0"/>
                <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_along_line_unit" type="QString" value="Point"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="place_on_every_part" type="bool" value="true"/>
                <Option name="placements" type="QString" value="Interval"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="rotate" type="QString" value="1"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
              <symbol force_rhr="0" is_animated="0" name="@@45@1@0" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" type="QString" value=""/>
                    <Option name="properties"/>
                    <Option name="type" type="QString" value="collection"/>
                  </Option>
                </data_defined_properties>
                <layer pass="0" enabled="1" locked="0" id="{98bf797c-2285-4ed3-97b8-1716b341c8c4}" class="SimpleLine">
                  <Option type="Map">
                    <Option name="align_dash_pattern" type="QString" value="0"/>
                    <Option name="capstyle" type="QString" value="square"/>
                    <Option name="customdash" type="QString" value="5;2"/>
                    <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="customdash_unit" type="QString" value="Point"/>
                    <Option name="dash_pattern_offset" type="QString" value="0"/>
                    <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="dash_pattern_offset_unit" type="QString" value="Point"/>
                    <Option name="draw_inside_polygon" type="QString" value="0"/>
                    <Option name="joinstyle" type="QString" value="bevel"/>
                    <Option name="line_color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
                    <Option name="line_style" type="QString" value="solid"/>
                    <Option name="line_width" type="QString" value="1"/>
                    <Option name="line_width_unit" type="QString" value="Point"/>
                    <Option name="offset" type="QString" value="0"/>
                    <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="offset_unit" type="QString" value="Point"/>
                    <Option name="ring_filter" type="QString" value="0"/>
                    <Option name="trim_distance_end" type="QString" value="0"/>
                    <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="trim_distance_end_unit" type="QString" value="Point"/>
                    <Option name="trim_distance_start" type="QString" value="0"/>
                    <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="trim_distance_start_unit" type="QString" value="Point"/>
                    <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                    <Option name="use_custom_dash" type="QString" value="0"/>
                    <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="46" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{8ad0c838-9845-4e87-88d7-4222d703f5c4}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="124,217,204,255,rgb:0.48627450980392156,0.85098039215686272,0.80000000000000004,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="7"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="47" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{be582606-510c-4a5f-a69e-01bfa27474ff}" class="MarkerLine">
          <Option type="Map">
            <Option name="average_angle_length" type="QString" value="4"/>
            <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="average_angle_unit" type="QString" value="MM"/>
            <Option name="interval" type="QString" value="3"/>
            <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="interval_unit" type="QString" value="MM"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_along_line" type="QString" value="0"/>
            <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_along_line_unit" type="QString" value="MM"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="place_on_every_part" type="bool" value="true"/>
            <Option name="placements" type="QString" value="Interval"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="rotate" type="QString" value="1"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@47@0" type="marker" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{ae6c71f4-836a-4a67-8e8a-ce20728f47e2}" class="SimpleMarker">
              <Option type="Map">
                <Option name="angle" type="QString" value="0"/>
                <Option name="cap_style" type="QString" value="square"/>
                <Option name="color" type="QString" value="255,255,255,255,rgb:1,1,1,1"/>
                <Option name="horizontal_anchor_point" type="QString" value="1"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="name" type="QString" value="circle"/>
                <Option name="offset" type="QString" value="0,0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="MM"/>
                <Option name="outline_color" type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1"/>
                <Option name="outline_style" type="QString" value="solid"/>
                <Option name="outline_width" type="QString" value="0.5"/>
                <Option name="outline_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="outline_width_unit" type="QString" value="Point"/>
                <Option name="scale_method" type="QString" value="diameter"/>
                <Option name="size" type="QString" value="2"/>
                <Option name="size_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="size_unit" type="QString" value="MM"/>
                <Option name="vertical_anchor_point" type="QString" value="1"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="48" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{be582606-510c-4a5f-a69e-01bfa27474ff}" class="MarkerLine">
          <Option type="Map">
            <Option name="average_angle_length" type="QString" value="4"/>
            <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="average_angle_unit" type="QString" value="MM"/>
            <Option name="interval" type="QString" value="3"/>
            <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="interval_unit" type="QString" value="MM"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_along_line" type="QString" value="0"/>
            <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_along_line_unit" type="QString" value="MM"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="place_on_every_part" type="bool" value="true"/>
            <Option name="placements" type="QString" value="Interval"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="rotate" type="QString" value="1"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@48@0" type="marker" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{ae6c71f4-836a-4a67-8e8a-ce20728f47e2}" class="SimpleMarker">
              <Option type="Map">
                <Option name="angle" type="QString" value="0"/>
                <Option name="cap_style" type="QString" value="square"/>
                <Option name="color" type="QString" value="255,255,255,255,rgb:1,1,1,1"/>
                <Option name="horizontal_anchor_point" type="QString" value="1"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="name" type="QString" value="circle"/>
                <Option name="offset" type="QString" value="0,0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="MM"/>
                <Option name="outline_color" type="QString" value="229,31,45,255,rgb:0.89803921568627454,0.12156862745098039,0.17647058823529413,1"/>
                <Option name="outline_style" type="QString" value="solid"/>
                <Option name="outline_width" type="QString" value="0.5"/>
                <Option name="outline_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="outline_width_unit" type="QString" value="Point"/>
                <Option name="scale_method" type="QString" value="diameter"/>
                <Option name="size" type="QString" value="2"/>
                <Option name="size_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="size_unit" type="QString" value="MM"/>
                <Option name="vertical_anchor_point" type="QString" value="1"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="49" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{644c1d0a-ce9b-4e3a-8e27-3930a6b21a8f}" class="GeometryGenerator">
          <Option type="Map">
            <Option name="SymbolType" type="QString" value="Line"/>
            <Option name="geometryModifier" type="QString" value="CASE&#xa;    WHEN length($geometry) > (2) THEN&#xa;        line_substring(&#xa;            $geometry,&#xa;            10,&#xa;            length($geometry) - 8&#xa;        )&#xa;    ELSE&#xa;        $geometry&#xa;END&#xa;"/>
            <Option name="units" type="QString" value="Point"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@49@0" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{2d99c1db-caad-4488-af10-7fe52e51b266}" class="MarkerLine">
              <Option type="Map">
                <Option name="average_angle_length" type="QString" value="4"/>
                <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="average_angle_unit" type="QString" value="MM"/>
                <Option name="interval" type="QString" value="3"/>
                <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="interval_unit" type="QString" value="MM"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_along_line" type="QString" value="0"/>
                <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_along_line_unit" type="QString" value="MM"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="MM"/>
                <Option name="place_on_every_part" type="bool" value="true"/>
                <Option name="placements" type="QString" value="Interval"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="rotate" type="QString" value="1"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
              <symbol force_rhr="0" is_animated="0" name="@@49@0@0" type="marker" frame_rate="10" alpha="1" clip_to_extent="1">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" type="QString" value=""/>
                    <Option name="properties"/>
                    <Option name="type" type="QString" value="collection"/>
                  </Option>
                </data_defined_properties>
                <layer pass="0" enabled="1" locked="0" id="{ae6c71f4-836a-4a67-8e8a-ce20728f47e2}" class="SimpleMarker">
                  <Option type="Map">
                    <Option name="angle" type="QString" value="0"/>
                    <Option name="cap_style" type="QString" value="square"/>
                    <Option name="color" type="QString" value="255,255,255,255,rgb:1,1,1,1"/>
                    <Option name="horizontal_anchor_point" type="QString" value="1"/>
                    <Option name="joinstyle" type="QString" value="bevel"/>
                    <Option name="name" type="QString" value="circle"/>
                    <Option name="offset" type="QString" value="0,0"/>
                    <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="offset_unit" type="QString" value="MM"/>
                    <Option name="outline_color" type="QString" value="229,31,45,255,rgb:0.89803921568627454,0.12156862745098039,0.17647058823529413,1"/>
                    <Option name="outline_style" type="QString" value="solid"/>
                    <Option name="outline_width" type="QString" value="0.5"/>
                    <Option name="outline_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="outline_width_unit" type="QString" value="Point"/>
                    <Option name="scale_method" type="QString" value="diameter"/>
                    <Option name="size" type="QString" value="2"/>
                    <Option name="size_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="size_unit" type="QString" value="MM"/>
                    <Option name="vertical_anchor_point" type="QString" value="1"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
        <layer pass="0" enabled="1" locked="0" id="{9ff3dc2f-4946-4e73-baf9-11d695921d98}" class="ArrowLine">
          <Option type="Map">
            <Option name="arrow_start_width" type="QString" value="1"/>
            <Option name="arrow_start_width_unit" type="QString" value="MM"/>
            <Option name="arrow_start_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="arrow_type" type="QString" value="0"/>
            <Option name="arrow_width" type="QString" value="0"/>
            <Option name="arrow_width_unit" type="QString" value="Point"/>
            <Option name="arrow_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_length" type="QString" value="2"/>
            <Option name="head_length_unit" type="QString" value="MM"/>
            <Option name="head_length_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_thickness" type="QString" value="2"/>
            <Option name="head_thickness_unit" type="QString" value="MM"/>
            <Option name="head_thickness_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_type" type="QString" value="2"/>
            <Option name="is_curved" type="QString" value="1"/>
            <Option name="is_repeated" type="QString" value="1"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="offset_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="ring_filter" type="QString" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@49@1" type="fill" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{d31c8c7c-3653-40b7-9cad-9d01be6cbb48}" class="SimpleFill">
              <Option type="Map">
                <Option name="border_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="color" type="QString" value="229,31,45,255,rgb:0.89803921568627454,0.12156862745098039,0.17647058823529413,1"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="offset" type="QString" value="0,0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="outline_color" type="QString" value="35,35,35,0,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,0"/>
                <Option name="outline_style" type="QString" value="no"/>
                <Option name="outline_width" type="QString" value="0"/>
                <Option name="outline_width_unit" type="QString" value="Point"/>
                <Option name="style" type="QString" value="solid"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="5" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{c1fbaa3b-6edf-46d1-be03-12db49ccc062}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="0,0,0,255,rgb:0,0,0,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="7"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="50" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{f57eba6b-1712-4eb0-a30d-1cef77422d06}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="111,168,218,255,rgb:0.43529411764705883,0.6588235294117647,0.85490196078431369,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="1.25"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="51" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{394de993-20d3-4bd0-9c6c-358039a3eb8d}" class="MarkerLine">
          <Option type="Map">
            <Option name="average_angle_length" type="QString" value="4"/>
            <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="average_angle_unit" type="QString" value="MM"/>
            <Option name="interval" type="QString" value="3"/>
            <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="interval_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_along_line" type="QString" value="0"/>
            <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_along_line_unit" type="QString" value="MM"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="place_on_every_part" type="bool" value="true"/>
            <Option name="placements" type="QString" value="Interval"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="rotate" type="QString" value="1"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@51@0" type="marker" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{022f2612-398f-4d5f-b472-4f659b787a08}" class="SimpleMarker">
              <Option type="Map">
                <Option name="angle" type="QString" value="0"/>
                <Option name="cap_style" type="QString" value="square"/>
                <Option name="color" type="QString" value="255,0,0,255,rgb:1,0,0,1"/>
                <Option name="horizontal_anchor_point" type="QString" value="1"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="name" type="QString" value="circle"/>
                <Option name="offset" type="QString" value="0,0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="outline_color" type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1"/>
                <Option name="outline_style" type="QString" value="solid"/>
                <Option name="outline_width" type="QString" value="0"/>
                <Option name="outline_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="outline_width_unit" type="QString" value="Point"/>
                <Option name="scale_method" type="QString" value="diameter"/>
                <Option name="size" type="QString" value="0.75"/>
                <Option name="size_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="size_unit" type="QString" value="Point"/>
                <Option name="vertical_anchor_point" type="QString" value="1"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="52" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{8ecf55d0-a946-461d-9ae9-6f1c30fc5e62}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="25,104,64,255,rgb:0.09803921568627451,0.40784313725490196,0.25098039215686274,1"/>
            <Option name="line_style" type="QString" value="dash dot"/>
            <Option name="line_width" type="QString" value="1"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="53" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{50275a2d-a0cc-4563-a4bf-a99f2011a7aa}" class="ArrowLine">
          <Option type="Map">
            <Option name="arrow_start_width" type="QString" value="5"/>
            <Option name="arrow_start_width_unit" type="QString" value="Point"/>
            <Option name="arrow_start_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="arrow_type" type="QString" value="0"/>
            <Option name="arrow_width" type="QString" value="5"/>
            <Option name="arrow_width_unit" type="QString" value="Point"/>
            <Option name="arrow_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_length" type="QString" value="15"/>
            <Option name="head_length_unit" type="QString" value="Point"/>
            <Option name="head_length_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_thickness" type="QString" value="7.5"/>
            <Option name="head_thickness_unit" type="QString" value="Point"/>
            <Option name="head_thickness_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_type" type="QString" value="0"/>
            <Option name="is_curved" type="QString" value="1"/>
            <Option name="is_repeated" type="QString" value="1"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="offset_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="ring_filter" type="QString" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@53@0" type="fill" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{48d25de5-881f-4d77-8eae-c4fa9a833d07}" class="SimpleFill">
              <Option type="Map">
                <Option name="border_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="color" type="QString" value="0,0,0,255,rgb:0,0,0,1"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="offset" type="QString" value="0,0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="MM"/>
                <Option name="outline_color" type="QString" value="231,113,72,0,rgb:0.90588235294117647,0.44313725490196076,0.28235294117647058,0"/>
                <Option name="outline_style" type="QString" value="no"/>
                <Option name="outline_width" type="QString" value="0.26"/>
                <Option name="outline_width_unit" type="QString" value="MM"/>
                <Option name="style" type="QString" value="solid"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="54" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{91533b6d-d7a6-450e-8706-eac1f6a25d34}" class="ArrowLine">
          <Option type="Map">
            <Option name="arrow_start_width" type="QString" value="1"/>
            <Option name="arrow_start_width_unit" type="QString" value="MM"/>
            <Option name="arrow_start_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="arrow_type" type="QString" value="0"/>
            <Option name="arrow_width" type="QString" value="0"/>
            <Option name="arrow_width_unit" type="QString" value="Point"/>
            <Option name="arrow_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_length" type="QString" value="10"/>
            <Option name="head_length_unit" type="QString" value="Point"/>
            <Option name="head_length_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_thickness" type="QString" value="10"/>
            <Option name="head_thickness_unit" type="QString" value="Point"/>
            <Option name="head_thickness_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_type" type="QString" value="2"/>
            <Option name="is_curved" type="QString" value="1"/>
            <Option name="is_repeated" type="QString" value="1"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_unit" type="QString" value="Point"/>
            <Option name="offset_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="ring_filter" type="QString" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@54@0" type="fill" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{4ca734c4-5a47-4d49-a06a-7509f417212d}" class="SimpleFill">
              <Option type="Map">
                <Option name="border_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="color" type="QString" value="0,0,0,255,rgb:0,0,0,1"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="offset" type="QString" value="0,0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="outline_color" type="QString" value="230,45,43,255,rgb:0.90196078431372551,0.17647058823529413,0.16862745098039217,1"/>
                <Option name="outline_style" type="QString" value="no"/>
                <Option name="outline_width" type="QString" value="0"/>
                <Option name="outline_width_unit" type="QString" value="Point"/>
                <Option name="style" type="QString" value="solid"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer pass="0" enabled="1" locked="0" id="{622dfad4-c787-40f2-b02a-3acdfb1e35b4}" class="GeometryGenerator">
          <Option type="Map">
            <Option name="SymbolType" type="QString" value="Line"/>
            <Option name="geometryModifier" type="QString" value="CASE&#xa;    WHEN length($geometry) > ( (5 + 2) * 2 ) THEN&#xa;        line_substring(&#xa;            $geometry,&#xa;            (5 + 2),&#xa;            length($geometry) - (5 + 2)&#xa;        )&#xa;    ELSE&#xa;        $geometry&#xa;END&#xa;"/>
            <Option name="units" type="QString" value="Point"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@54@1" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{410325a0-e6d3-4692-8772-82224a61351d}" class="HashLine">
              <Option type="Map">
                <Option name="average_angle_length" type="QString" value="4"/>
                <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="average_angle_unit" type="QString" value="Point"/>
                <Option name="hash_angle" type="QString" value="90"/>
                <Option name="hash_length" type="QString" value="1"/>
                <Option name="hash_length_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="hash_length_unit" type="QString" value="Point"/>
                <Option name="interval" type="QString" value="12"/>
                <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="interval_unit" type="QString" value="Point"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_along_line" type="QString" value="0"/>
                <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_along_line_unit" type="QString" value="Point"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="Point"/>
                <Option name="place_on_every_part" type="bool" value="true"/>
                <Option name="placements" type="QString" value="Interval"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="rotate" type="QString" value="1"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
              <symbol force_rhr="0" is_animated="0" name="@@54@1@0" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" type="QString" value=""/>
                    <Option name="properties"/>
                    <Option name="type" type="QString" value="collection"/>
                  </Option>
                </data_defined_properties>
                <layer pass="0" enabled="1" locked="0" id="{98bf797c-2285-4ed3-97b8-1716b341c8c4}" class="SimpleLine">
                  <Option type="Map">
                    <Option name="align_dash_pattern" type="QString" value="0"/>
                    <Option name="capstyle" type="QString" value="square"/>
                    <Option name="customdash" type="QString" value="5;2"/>
                    <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="customdash_unit" type="QString" value="Point"/>
                    <Option name="dash_pattern_offset" type="QString" value="0"/>
                    <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="dash_pattern_offset_unit" type="QString" value="Point"/>
                    <Option name="draw_inside_polygon" type="QString" value="0"/>
                    <Option name="joinstyle" type="QString" value="bevel"/>
                    <Option name="line_color" type="QString" value="0,0,0,255,rgb:0,0,0,1"/>
                    <Option name="line_style" type="QString" value="solid"/>
                    <Option name="line_width" type="QString" value="7"/>
                    <Option name="line_width_unit" type="QString" value="Point"/>
                    <Option name="offset" type="QString" value="0"/>
                    <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="offset_unit" type="QString" value="Point"/>
                    <Option name="ring_filter" type="QString" value="0"/>
                    <Option name="trim_distance_end" type="QString" value="0"/>
                    <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="trim_distance_end_unit" type="QString" value="Point"/>
                    <Option name="trim_distance_start" type="QString" value="0"/>
                    <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="trim_distance_start_unit" type="QString" value="Point"/>
                    <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                    <Option name="use_custom_dash" type="QString" value="0"/>
                    <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="55" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{e5ff37ef-d0d9-44c3-94e7-a4765b94a4bd}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="Point"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="Point"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="193,221,245,255,rgb:0.75686274509803919,0.8666666666666667,0.96078431372549022,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="3"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="Point"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="Point"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="Point"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="56" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{bff5a665-c20a-4b9c-8fe9-d41b7e19539f}" class="HashLine">
          <Option type="Map">
            <Option name="average_angle_length" type="QString" value="4"/>
            <Option name="average_angle_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="average_angle_unit" type="QString" value="MM"/>
            <Option name="hash_angle" type="QString" value="45"/>
            <Option name="hash_length" type="QString" value="1"/>
            <Option name="hash_length_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="hash_length_unit" type="QString" value="MM"/>
            <Option name="interval" type="QString" value="2"/>
            <Option name="interval_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="interval_unit" type="QString" value="MM"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_along_line" type="QString" value="0"/>
            <Option name="offset_along_line_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_along_line_unit" type="QString" value="MM"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="place_on_every_part" type="bool" value="true"/>
            <Option name="placements" type="QString" value="Interval"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="rotate" type="QString" value="1"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" is_animated="0" name="@56@0" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer pass="0" enabled="1" locked="0" id="{5ddeaaf4-9263-4cf3-bf10-9622178b4a1f}" class="SimpleLine">
              <Option type="Map">
                <Option name="align_dash_pattern" type="QString" value="0"/>
                <Option name="capstyle" type="QString" value="square"/>
                <Option name="customdash" type="QString" value="5;2"/>
                <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="customdash_unit" type="QString" value="MM"/>
                <Option name="dash_pattern_offset" type="QString" value="0"/>
                <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
                <Option name="draw_inside_polygon" type="QString" value="0"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="line_color" type="QString" value="221,35,35,255,rgb:0.8666666666666667,0.13725490196078433,0.13725490196078433,1"/>
                <Option name="line_style" type="QString" value="solid"/>
                <Option name="line_width" type="QString" value="0.26"/>
                <Option name="line_width_unit" type="QString" value="MM"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="MM"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="trim_distance_end" type="QString" value="0"/>
                <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_end_unit" type="QString" value="MM"/>
                <Option name="trim_distance_start" type="QString" value="0"/>
                <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_start_unit" type="QString" value="MM"/>
                <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                <Option name="use_custom_dash" type="QString" value="0"/>
                <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="6" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{c1fbaa3b-6edf-46d1-be03-12db49ccc062}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="0,0,0,255,rgb:0,0,0,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="5"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="7" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{c1fbaa3b-6edf-46d1-be03-12db49ccc062}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="0,0,0,255,rgb:0,0,0,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="5"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="8" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{c1fbaa3b-6edf-46d1-be03-12db49ccc062}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="0,0,0,255,rgb:0,0,0,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="5"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" is_animated="0" name="9" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{c1fbaa3b-6edf-46d1-be03-12db49ccc062}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="0,0,0,255,rgb:0,0,0,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="3"/>
            <Option name="line_width_unit" type="QString" value="Point"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
    <data-defined-properties>
      <Option type="Map">
        <Option name="name" type="QString" value=""/>
        <Option name="properties"/>
        <Option name="type" type="QString" value="collection"/>
      </Option>
    </data-defined-properties>
  </renderer-v2>
  <selection mode="Default">
    <selectionColor invalid="1"/>
    <selectionSymbol>
      <symbol force_rhr="0" is_animated="0" name="" type="line" frame_rate="10" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" locked="0" id="{caf62504-e233-4f5d-a577-bd90a633f492}" class="SimpleLine">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="0.26"/>
            <Option name="line_width_unit" type="QString" value="MM"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </selectionSymbol>
  </selection>
  <labeling type="rule-based">
    <rules key="{5d144b12-c8d3-4d13-be54-d7bb80977e63}">
      <rule filter="map_akeys(&quot;type_regulations&quot;) = array('liikennetunneli')" description="Liikennetunneli" key="{2d53abb2-3658-4066-95c3-459241171715}">
        <settings calloutType="simple">
          <text-style tabStopDistanceMapUnitScale="3x:0,0,0,0,0,0" multilineHeightUnit="Percentage" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontLetterSpacing="0" capitalization="0" fontSizeUnit="Point" textColor="50,50,50,255,rgb:0.19607843137254902,0.19607843137254902,0.19607843137254902,1" textOrientation="horizontal" fontKerning="1" textOpacity="1" previewBkgrdColor="255,255,255,255,rgb:1,1,1,1" namedStyle="Bold" fontUnderline="0" fontWeight="75" fontFamily="Arial" forcedItalic="0" fontItalic="0" isExpression="1" useSubstitutions="0" legendString="Aa" fontSize="10" fieldName="array_to_string(&quot;short_names&quot;, '/')" fontStrikeout="0" multilineHeight="1" tabStopDistance="80" fontWordSpacing="0" tabStopDistanceUnit="Point" forcedBold="0" blendMode="0" allowHtml="0">
            <families/>
            <text-buffer bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferNoFill="1" bufferColor="250,250,250,255,rgb:0.98039215686274506,0.98039215686274506,0.98039215686274506,1" bufferSizeUnits="MM" bufferJoinStyle="128" bufferDraw="0" bufferSize="1" bufferOpacity="1" bufferBlendMode="0"/>
            <text-mask maskedSymbolLayers="" maskSizeUnits="MM" maskOpacity="1" maskSize="1.5" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskJoinStyle="128" maskSize2="1.5" maskEnabled="0" maskType="0"/>
            <background shapeSizeUnit="Point" shapeOffsetX="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeDraw="0" shapeFillColor="255,255,255,255,rgb:1,1,1,1" shapeType="0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeSVGFile="" shapeBorderColor="128,128,128,255,rgb:0.50196078431372548,0.50196078431372548,0.50196078431372548,1" shapeBorderWidth="0" shapeBorderWidthUnit="Point" shapeOpacity="1" shapeRadiiX="0" shapeBlendMode="0" shapeSizeType="0" shapeRadiiY="0" shapeRotationType="0" shapeOffsetUnit="Point" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeJoinStyle="64" shapeSizeY="0" shapeRotation="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeSizeX="0" shapeRadiiUnit="Point" shapeOffsetY="0">
              <symbol force_rhr="0" is_animated="0" name="markerSymbol" type="marker" frame_rate="10" alpha="1" clip_to_extent="1">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" type="QString" value=""/>
                    <Option name="properties"/>
                    <Option name="type" type="QString" value="collection"/>
                  </Option>
                </data_defined_properties>
                <layer pass="0" enabled="1" locked="0" id="" class="SimpleMarker">
                  <Option type="Map">
                    <Option name="angle" type="QString" value="0"/>
                    <Option name="cap_style" type="QString" value="square"/>
                    <Option name="color" type="QString" value="141,90,153,255,rgb:0.55294117647058827,0.35294117647058826,0.59999999999999998,1"/>
                    <Option name="horizontal_anchor_point" type="QString" value="1"/>
                    <Option name="joinstyle" type="QString" value="bevel"/>
                    <Option name="name" type="QString" value="circle"/>
                    <Option name="offset" type="QString" value="0,0"/>
                    <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="offset_unit" type="QString" value="MM"/>
                    <Option name="outline_color" type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1"/>
                    <Option name="outline_style" type="QString" value="solid"/>
                    <Option name="outline_width" type="QString" value="0"/>
                    <Option name="outline_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="outline_width_unit" type="QString" value="MM"/>
                    <Option name="scale_method" type="QString" value="diameter"/>
                    <Option name="size" type="QString" value="2"/>
                    <Option name="size_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="size_unit" type="QString" value="MM"/>
                    <Option name="vertical_anchor_point" type="QString" value="1"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
              <symbol force_rhr="0" is_animated="0" name="fillSymbol" type="fill" frame_rate="10" alpha="1" clip_to_extent="1">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" type="QString" value=""/>
                    <Option name="properties"/>
                    <Option name="type" type="QString" value="collection"/>
                  </Option>
                </data_defined_properties>
                <layer pass="0" enabled="1" locked="0" id="" class="SimpleFill">
                  <Option type="Map">
                    <Option name="border_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="color" type="QString" value="255,255,255,255,rgb:1,1,1,1"/>
                    <Option name="joinstyle" type="QString" value="bevel"/>
                    <Option name="offset" type="QString" value="0,0"/>
                    <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="offset_unit" type="QString" value="MM"/>
                    <Option name="outline_color" type="QString" value="128,128,128,255,rgb:0.50196078431372548,0.50196078431372548,0.50196078431372548,1"/>
                    <Option name="outline_style" type="QString" value="no"/>
                    <Option name="outline_width" type="QString" value="0"/>
                    <Option name="outline_width_unit" type="QString" value="Point"/>
                    <Option name="style" type="QString" value="solid"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowOpacity="0.69999999999999996" shadowColor="0,0,0,255,rgb:0,0,0,1" shadowDraw="0" shadowUnder="0" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowBlendMode="6" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowScale="100" shadowOffsetUnit="MM" shadowOffsetGlobal="1" shadowOffsetDist="1" shadowRadiusUnit="MM" shadowRadius="1.5" shadowOffsetAngle="135" shadowRadiusAlphaOnly="0"/>
            <dd_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format autoWrapLength="0" reverseDirectionSymbol="0" plussign="0" formatNumbers="0" decimals="3" leftDirectionSymbol="&lt;" placeDirectionSymbol="0" useMaxLineLengthForAutoWrap="1" multilineAlign="0" rightDirectionSymbol=">" wrapChar="" addDirectionSymbol="0"/>
          <placement polygonPlacementFlags="2" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" lineAnchorType="0" distMapUnitScale="3x:0,0,0,0,0,0" maximumDistanceUnit="MM" quadOffset="4" overlapHandling="PreventOverlap" priority="5" lineAnchorClipping="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" distUnits="Point" layerType="LineGeometry" xOffset="0" prioritization="PreferCloser" allowDegraded="0" maxCurvedCharAngleOut="-25" offsetType="0" offsetUnits="MM" geometryGenerator="" rotationUnit="AngleDegrees" overrunDistance="0" lineAnchorTextPoint="FollowPlacement" lineAnchorPercent="0.5" repeatDistanceUnits="MM" placement="2" dist="-6" overrunDistanceUnit="MM" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" maxCurvedCharAngleIn="25" maximumDistance="0" geometryGeneratorType="PointGeometry" placementFlags="10" rotationAngle="0" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" geometryGeneratorEnabled="0" maximumDistanceMapUnitScale="3x:0,0,0,0,0,0" preserveRotation="1" centroidInside="0" yOffset="0" centroidWhole="0" repeatDistance="0" fitInPolygonOnly="0"/>
          <rendering labelPerPart="0" scaleVisibility="0" unplacedVisibility="0" scaleMax="0" obstacleFactor="1" fontMaxPixelSize="10000" zIndex="0" fontMinPixelSize="3" upsidedownLabels="0" obstacle="1" fontLimitPixelSize="0" drawLabels="1" limitNumLabels="0" scaleMin="0" mergeLines="0" maxNumLabels="2000" obstacleType="1" minFeatureSize="0"/>
          <dd_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option name="anchorPoint" type="QString" value="pole_of_inaccessibility"/>
              <Option name="blendMode" type="int" value="0"/>
              <Option name="ddProperties" type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
              <Option name="drawToAllParts" type="bool" value="false"/>
              <Option name="enabled" type="QString" value="0"/>
              <Option name="labelAnchorPoint" type="QString" value="point_on_exterior"/>
              <Option name="lineSymbol" type="QString" value="&lt;symbol force_rhr=&quot;0&quot; is_animated=&quot;0&quot; name=&quot;symbol&quot; type=&quot;line&quot; frame_rate=&quot;10&quot; alpha=&quot;1&quot; clip_to_extent=&quot;1&quot;>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; type=&quot;QString&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; type=&quot;QString&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;layer pass=&quot;0&quot; enabled=&quot;1&quot; locked=&quot;0&quot; id=&quot;{bdec80e5-7b98-428d-8f73-2f9193e43c18}&quot; class=&quot;SimpleLine&quot;>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;align_dash_pattern&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;capstyle&quot; type=&quot;QString&quot; value=&quot;square&quot;/>&lt;Option name=&quot;customdash&quot; type=&quot;QString&quot; value=&quot;5;2&quot;/>&lt;Option name=&quot;customdash_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;customdash_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;dash_pattern_offset&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;dash_pattern_offset_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;dash_pattern_offset_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;draw_inside_polygon&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;joinstyle&quot; type=&quot;QString&quot; value=&quot;bevel&quot;/>&lt;Option name=&quot;line_color&quot; type=&quot;QString&quot; value=&quot;60,60,60,255,rgb:0.23529411764705882,0.23529411764705882,0.23529411764705882,1&quot;/>&lt;Option name=&quot;line_style&quot; type=&quot;QString&quot; value=&quot;solid&quot;/>&lt;Option name=&quot;line_width&quot; type=&quot;QString&quot; value=&quot;0.3&quot;/>&lt;Option name=&quot;line_width_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;offset&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;offset_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;offset_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;ring_filter&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;trim_distance_end&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;trim_distance_end_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;trim_distance_end_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;trim_distance_start&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;trim_distance_start_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;trim_distance_start_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;tweak_dash_pattern_on_corners&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;use_custom_dash&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;width_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;/Option>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; type=&quot;QString&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; type=&quot;QString&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>"/>
              <Option name="minLength" type="double" value="0"/>
              <Option name="minLengthMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="minLengthUnit" type="QString" value="MM"/>
              <Option name="offsetFromAnchor" type="double" value="0"/>
              <Option name="offsetFromAnchorMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="offsetFromAnchorUnit" type="QString" value="MM"/>
              <Option name="offsetFromLabel" type="double" value="0"/>
              <Option name="offsetFromLabelMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="offsetFromLabelUnit" type="QString" value="MM"/>
            </Option>
          </callout>
        </settings>
      </rule>
      <rule filter="(&#xd;&#xa;array_sort(map_akeys(&quot;type_regulations&quot;)) = array('sahkolinja')&#xd;&#xa;AND array_length(map_akeys(map_get(&quot;type_regulations&quot;, 'sahkolinja'))) = 0&#xd;&#xa;)&#xd;&#xa;OR&#xd;&#xa;(&#xd;&#xa;array_sort(map_akeys(&quot;type_regulations&quot;)) = array('vesijohtoTaiViemari')&#xd;&#xa;AND array_length(map_akeys(map_get(&quot;type_regulations&quot;, 'vesijohtoTaiViemari'))) = 0&#xd;&#xa;)&#xd;&#xa;OR&#xd;&#xa;(&#xd;&#xa;array_sort(map_akeys(&quot;type_regulations&quot;)) = array('kaasulinja')&#xd;&#xa;AND array_length(map_akeys(map_get(&quot;type_regulations&quot;, 'kaasulinja'))) = 0&#xd;&#xa;)" description="Sähkölinja, vesijohto, kaasulinja" key="{bab19937-103f-457b-a391-9fb87aa05c10}">
        <settings calloutType="simple">
          <text-style tabStopDistanceMapUnitScale="3x:0,0,0,0,0,0" multilineHeightUnit="Percentage" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontLetterSpacing="0" capitalization="0" fontSizeUnit="Point" textColor="50,50,50,255,rgb:0.19607843137254902,0.19607843137254902,0.19607843137254902,1" textOrientation="horizontal" fontKerning="1" textOpacity="1" previewBkgrdColor="255,255,255,255,rgb:1,1,1,1" namedStyle="Bold" fontUnderline="0" fontWeight="75" fontFamily="Arial" forcedItalic="0" fontItalic="0" isExpression="1" useSubstitutions="0" legendString="Aa" fontSize="10" fieldName="array_to_string(&quot;short_names&quot;, '/')" fontStrikeout="0" multilineHeight="1" tabStopDistance="80" fontWordSpacing="0" tabStopDistanceUnit="Point" forcedBold="0" blendMode="0" allowHtml="0">
            <families/>
            <text-buffer bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferNoFill="1" bufferColor="250,250,250,255,rgb:0.98039215686274506,0.98039215686274506,0.98039215686274506,1" bufferSizeUnits="MM" bufferJoinStyle="128" bufferDraw="0" bufferSize="1" bufferOpacity="1" bufferBlendMode="0"/>
            <text-mask maskedSymbolLayers="" maskSizeUnits="MM" maskOpacity="1" maskSize="1.5" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskJoinStyle="128" maskSize2="1.5" maskEnabled="0" maskType="0"/>
            <background shapeSizeUnit="Point" shapeOffsetX="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeDraw="1" shapeFillColor="255,255,255,255,rgb:1,1,1,1" shapeType="3" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeSVGFile="" shapeBorderColor="0,0,0,255,rgb:0,0,0,1" shapeBorderWidth="0.75" shapeBorderWidthUnit="Point" shapeOpacity="1" shapeRadiiX="0" shapeBlendMode="0" shapeSizeType="0" shapeRadiiY="0" shapeRotationType="0" shapeOffsetUnit="Point" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeJoinStyle="64" shapeSizeY="0" shapeRotation="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeSizeX="0" shapeRadiiUnit="Point" shapeOffsetY="0">
              <symbol force_rhr="0" is_animated="0" name="markerSymbol" type="marker" frame_rate="10" alpha="1" clip_to_extent="1">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" type="QString" value=""/>
                    <Option name="properties"/>
                    <Option name="type" type="QString" value="collection"/>
                  </Option>
                </data_defined_properties>
                <layer pass="0" enabled="1" locked="0" id="" class="SimpleMarker">
                  <Option type="Map">
                    <Option name="angle" type="QString" value="0"/>
                    <Option name="cap_style" type="QString" value="square"/>
                    <Option name="color" type="QString" value="183,72,75,255,rgb:0.71764705882352942,0.28235294117647058,0.29411764705882354,1"/>
                    <Option name="horizontal_anchor_point" type="QString" value="1"/>
                    <Option name="joinstyle" type="QString" value="bevel"/>
                    <Option name="name" type="QString" value="circle"/>
                    <Option name="offset" type="QString" value="0,0"/>
                    <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="offset_unit" type="QString" value="MM"/>
                    <Option name="outline_color" type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1"/>
                    <Option name="outline_style" type="QString" value="solid"/>
                    <Option name="outline_width" type="QString" value="0"/>
                    <Option name="outline_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="outline_width_unit" type="QString" value="MM"/>
                    <Option name="scale_method" type="QString" value="diameter"/>
                    <Option name="size" type="QString" value="2"/>
                    <Option name="size_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="size_unit" type="QString" value="MM"/>
                    <Option name="vertical_anchor_point" type="QString" value="1"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
              <symbol force_rhr="0" is_animated="0" name="fillSymbol" type="fill" frame_rate="10" alpha="1" clip_to_extent="1">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" type="QString" value=""/>
                    <Option name="properties"/>
                    <Option name="type" type="QString" value="collection"/>
                  </Option>
                </data_defined_properties>
                <layer pass="0" enabled="1" locked="0" id="" class="SimpleFill">
                  <Option type="Map">
                    <Option name="border_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="color" type="QString" value="255,255,255,255,rgb:1,1,1,1"/>
                    <Option name="joinstyle" type="QString" value="bevel"/>
                    <Option name="offset" type="QString" value="0,0"/>
                    <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="offset_unit" type="QString" value="MM"/>
                    <Option name="outline_color" type="QString" value="0,0,0,255,rgb:0,0,0,1"/>
                    <Option name="outline_style" type="QString" value="solid"/>
                    <Option name="outline_width" type="QString" value="0.75"/>
                    <Option name="outline_width_unit" type="QString" value="Point"/>
                    <Option name="style" type="QString" value="solid"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowOpacity="0.69999999999999996" shadowColor="0,0,0,255,rgb:0,0,0,1" shadowDraw="0" shadowUnder="0" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowBlendMode="6" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowScale="100" shadowOffsetUnit="MM" shadowOffsetGlobal="1" shadowOffsetDist="1" shadowRadiusUnit="MM" shadowRadius="1.5" shadowOffsetAngle="135" shadowRadiusAlphaOnly="0"/>
            <dd_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format autoWrapLength="0" reverseDirectionSymbol="0" plussign="0" formatNumbers="0" decimals="3" leftDirectionSymbol="&lt;" placeDirectionSymbol="0" useMaxLineLengthForAutoWrap="1" multilineAlign="0" rightDirectionSymbol=">" wrapChar="" addDirectionSymbol="0"/>
          <placement polygonPlacementFlags="2" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" lineAnchorType="0" distMapUnitScale="3x:0,0,0,0,0,0" maximumDistanceUnit="MM" quadOffset="4" overlapHandling="PreventOverlap" priority="5" lineAnchorClipping="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" distUnits="Point" layerType="LineGeometry" xOffset="0" prioritization="PreferCloser" allowDegraded="0" maxCurvedCharAngleOut="-25" offsetType="0" offsetUnits="MM" geometryGenerator="" rotationUnit="AngleDegrees" overrunDistance="0" lineAnchorTextPoint="FollowPlacement" lineAnchorPercent="0.5" repeatDistanceUnits="MM" placement="2" dist="-5" overrunDistanceUnit="MM" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" maxCurvedCharAngleIn="25" maximumDistance="0" geometryGeneratorType="PointGeometry" placementFlags="9" rotationAngle="0" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" geometryGeneratorEnabled="0" maximumDistanceMapUnitScale="3x:0,0,0,0,0,0" preserveRotation="1" centroidInside="0" yOffset="0" centroidWhole="0" repeatDistance="0" fitInPolygonOnly="0"/>
          <rendering labelPerPart="0" scaleVisibility="0" unplacedVisibility="0" scaleMax="0" obstacleFactor="1" fontMaxPixelSize="10000" zIndex="0" fontMinPixelSize="3" upsidedownLabels="0" obstacle="1" fontLimitPixelSize="0" drawLabels="1" limitNumLabels="0" scaleMin="0" mergeLines="0" maxNumLabels="2000" obstacleType="1" minFeatureSize="0"/>
          <dd_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option name="anchorPoint" type="QString" value="pole_of_inaccessibility"/>
              <Option name="blendMode" type="int" value="0"/>
              <Option name="ddProperties" type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
              <Option name="drawToAllParts" type="bool" value="false"/>
              <Option name="enabled" type="QString" value="0"/>
              <Option name="labelAnchorPoint" type="QString" value="point_on_exterior"/>
              <Option name="lineSymbol" type="QString" value="&lt;symbol force_rhr=&quot;0&quot; is_animated=&quot;0&quot; name=&quot;symbol&quot; type=&quot;line&quot; frame_rate=&quot;10&quot; alpha=&quot;1&quot; clip_to_extent=&quot;1&quot;>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; type=&quot;QString&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; type=&quot;QString&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;layer pass=&quot;0&quot; enabled=&quot;1&quot; locked=&quot;0&quot; id=&quot;{f3cd6cb4-4d36-49b5-8197-c1483c454a14}&quot; class=&quot;SimpleLine&quot;>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;align_dash_pattern&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;capstyle&quot; type=&quot;QString&quot; value=&quot;square&quot;/>&lt;Option name=&quot;customdash&quot; type=&quot;QString&quot; value=&quot;5;2&quot;/>&lt;Option name=&quot;customdash_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;customdash_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;dash_pattern_offset&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;dash_pattern_offset_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;dash_pattern_offset_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;draw_inside_polygon&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;joinstyle&quot; type=&quot;QString&quot; value=&quot;bevel&quot;/>&lt;Option name=&quot;line_color&quot; type=&quot;QString&quot; value=&quot;60,60,60,255,rgb:0.23529411764705882,0.23529411764705882,0.23529411764705882,1&quot;/>&lt;Option name=&quot;line_style&quot; type=&quot;QString&quot; value=&quot;solid&quot;/>&lt;Option name=&quot;line_width&quot; type=&quot;QString&quot; value=&quot;0.3&quot;/>&lt;Option name=&quot;line_width_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;offset&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;offset_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;offset_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;ring_filter&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;trim_distance_end&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;trim_distance_end_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;trim_distance_end_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;trim_distance_start&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;trim_distance_start_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;trim_distance_start_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;tweak_dash_pattern_on_corners&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;use_custom_dash&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;width_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;/Option>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; type=&quot;QString&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; type=&quot;QString&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>"/>
              <Option name="minLength" type="double" value="0"/>
              <Option name="minLengthMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="minLengthUnit" type="QString" value="MM"/>
              <Option name="offsetFromAnchor" type="double" value="0"/>
              <Option name="offsetFromAnchorMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="offsetFromAnchorUnit" type="QString" value="MM"/>
              <Option name="offsetFromLabel" type="double" value="0"/>
              <Option name="offsetFromLabelMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="offsetFromLabelUnit" type="QString" value="MM"/>
            </Option>
          </callout>
        </settings>
      </rule>
      <rule filter="(&#xa;    map_akeys(&quot;type_regulations&quot;) = array('sahkolinja')&#xa;    AND&#xa;    (&#xa;        map_akeys(map_get(&quot;type_regulations&quot;, 'sahkolinja')) = array('uusi')&#xa;        OR&#xa;        map_akeys(map_get(&quot;type_regulations&quot;, 'sahkolinja')) = array('yhteystarve')&#xa;    )&#xa;)&#xa;OR&#xa;(&#xa;    map_akeys(&quot;type_regulations&quot;) = array('vesijohtoTaiViemari')&#xa;    AND&#xa;&#x9;(&#xa;&#x9;&#x9;map_akeys(map_get(&quot;type_regulations&quot;, 'vesijohtoTaiViemari')) = array('uusi')&#xa;&#x9;&#x9;OR&#xa;&#x9;&#x9;map_akeys(map_get(&quot;type_regulations&quot;, 'vesijohtoTaiViemari')) = array('yhteystarve')&#xa;&#x9;)&#xa;)&#xa;OR&#xa;(&#xa;    map_akeys(&quot;type_regulations&quot;) = array('kaasulinja')&#xa;    AND&#xa;&#x9;(&#xa;&#x9;&#x9;map_akeys(map_get(&quot;type_regulations&quot;, 'kaasulinja')) = array('uusi')&#xa;&#x9;&#x9;OR&#xa;&#x9;&#x9;map_akeys(map_get(&quot;type_regulations&quot;, 'kaasulinja')) = array('yhteystarve')&#xa;&#x9;)&#xa;)" description="Uusi/yhteystarve sähkölinja, kaasulinja tai vesijohto" key="{2c57c1bc-2fd9-405e-b67d-958c06634f66}">
        <settings calloutType="simple">
          <text-style tabStopDistanceMapUnitScale="3x:0,0,0,0,0,0" multilineHeightUnit="Percentage" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontLetterSpacing="0" capitalization="0" fontSizeUnit="Point" textColor="229,31,45,255,rgb:0.89803921568627454,0.12156862745098039,0.17647058823529413,1" textOrientation="horizontal" fontKerning="1" textOpacity="1" previewBkgrdColor="255,255,255,255,rgb:1,1,1,1" namedStyle="Bold" fontUnderline="0" fontWeight="75" fontFamily="Arial" forcedItalic="0" fontItalic="0" isExpression="1" useSubstitutions="0" legendString="Aa" fontSize="10" fieldName="array_to_string(&quot;short_names&quot;, '/')" fontStrikeout="0" multilineHeight="1" tabStopDistance="80" fontWordSpacing="0" tabStopDistanceUnit="Point" forcedBold="0" blendMode="0" allowHtml="0">
            <families/>
            <text-buffer bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferNoFill="1" bufferColor="250,250,250,255,rgb:0.98039215686274506,0.98039215686274506,0.98039215686274506,1" bufferSizeUnits="MM" bufferJoinStyle="128" bufferDraw="0" bufferSize="1" bufferOpacity="1" bufferBlendMode="0"/>
            <text-mask maskedSymbolLayers="" maskSizeUnits="MM" maskOpacity="1" maskSize="1.5" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskJoinStyle="128" maskSize2="1.5" maskEnabled="0" maskType="0"/>
            <background shapeSizeUnit="Point" shapeOffsetX="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeDraw="1" shapeFillColor="255,255,255,255,rgb:1,1,1,1" shapeType="3" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeSVGFile="" shapeBorderColor="229,31,45,255,rgb:0.89803921568627454,0.12156862745098039,0.17647058823529413,1" shapeBorderWidth="0.75" shapeBorderWidthUnit="Point" shapeOpacity="1" shapeRadiiX="0" shapeBlendMode="0" shapeSizeType="0" shapeRadiiY="0" shapeRotationType="0" shapeOffsetUnit="Point" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeJoinStyle="64" shapeSizeY="0" shapeRotation="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeSizeX="0" shapeRadiiUnit="Point" shapeOffsetY="0">
              <symbol force_rhr="0" is_animated="0" name="markerSymbol" type="marker" frame_rate="10" alpha="1" clip_to_extent="1">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" type="QString" value=""/>
                    <Option name="properties"/>
                    <Option name="type" type="QString" value="collection"/>
                  </Option>
                </data_defined_properties>
                <layer pass="0" enabled="1" locked="0" id="" class="SimpleMarker">
                  <Option type="Map">
                    <Option name="angle" type="QString" value="0"/>
                    <Option name="cap_style" type="QString" value="square"/>
                    <Option name="color" type="QString" value="255,158,23,255,rgb:1,0.61960784313725492,0.09019607843137255,1"/>
                    <Option name="horizontal_anchor_point" type="QString" value="1"/>
                    <Option name="joinstyle" type="QString" value="bevel"/>
                    <Option name="name" type="QString" value="circle"/>
                    <Option name="offset" type="QString" value="0,0"/>
                    <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="offset_unit" type="QString" value="MM"/>
                    <Option name="outline_color" type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1"/>
                    <Option name="outline_style" type="QString" value="solid"/>
                    <Option name="outline_width" type="QString" value="0"/>
                    <Option name="outline_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="outline_width_unit" type="QString" value="MM"/>
                    <Option name="scale_method" type="QString" value="diameter"/>
                    <Option name="size" type="QString" value="2"/>
                    <Option name="size_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="size_unit" type="QString" value="MM"/>
                    <Option name="vertical_anchor_point" type="QString" value="1"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
              <symbol force_rhr="0" is_animated="0" name="fillSymbol" type="fill" frame_rate="10" alpha="1" clip_to_extent="1">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" type="QString" value=""/>
                    <Option name="properties"/>
                    <Option name="type" type="QString" value="collection"/>
                  </Option>
                </data_defined_properties>
                <layer pass="0" enabled="1" locked="0" id="" class="SimpleFill">
                  <Option type="Map">
                    <Option name="border_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="color" type="QString" value="255,255,255,255,rgb:1,1,1,1"/>
                    <Option name="joinstyle" type="QString" value="bevel"/>
                    <Option name="offset" type="QString" value="0,0"/>
                    <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="offset_unit" type="QString" value="MM"/>
                    <Option name="outline_color" type="QString" value="229,31,45,255,rgb:0.89803921568627454,0.12156862745098039,0.17647058823529413,1"/>
                    <Option name="outline_style" type="QString" value="solid"/>
                    <Option name="outline_width" type="QString" value="0.75"/>
                    <Option name="outline_width_unit" type="QString" value="Point"/>
                    <Option name="style" type="QString" value="solid"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowOpacity="0.69999999999999996" shadowColor="0,0,0,255,rgb:0,0,0,1" shadowDraw="0" shadowUnder="0" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowBlendMode="6" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowScale="100" shadowOffsetUnit="MM" shadowOffsetGlobal="1" shadowOffsetDist="1" shadowRadiusUnit="MM" shadowRadius="1.5" shadowOffsetAngle="135" shadowRadiusAlphaOnly="0"/>
            <dd_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format autoWrapLength="0" reverseDirectionSymbol="0" plussign="0" formatNumbers="0" decimals="3" leftDirectionSymbol="&lt;" placeDirectionSymbol="0" useMaxLineLengthForAutoWrap="1" multilineAlign="0" rightDirectionSymbol=">" wrapChar="" addDirectionSymbol="0"/>
          <placement polygonPlacementFlags="2" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" lineAnchorType="0" distMapUnitScale="3x:0,0,0,0,0,0" maximumDistanceUnit="MM" quadOffset="4" overlapHandling="PreventOverlap" priority="5" lineAnchorClipping="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" distUnits="MM" layerType="LineGeometry" xOffset="0" prioritization="PreferCloser" allowDegraded="0" maxCurvedCharAngleOut="-25" offsetType="0" offsetUnits="MM" geometryGenerator="" rotationUnit="AngleDegrees" overrunDistance="0" lineAnchorTextPoint="FollowPlacement" lineAnchorPercent="0.5" repeatDistanceUnits="MM" placement="2" dist="0" overrunDistanceUnit="MM" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" maxCurvedCharAngleIn="25" maximumDistance="0" geometryGeneratorType="PointGeometry" placementFlags="9" rotationAngle="0" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" geometryGeneratorEnabled="0" maximumDistanceMapUnitScale="3x:0,0,0,0,0,0" preserveRotation="1" centroidInside="0" yOffset="0" centroidWhole="0" repeatDistance="0" fitInPolygonOnly="0"/>
          <rendering labelPerPart="0" scaleVisibility="0" unplacedVisibility="0" scaleMax="0" obstacleFactor="1" fontMaxPixelSize="10000" zIndex="0" fontMinPixelSize="3" upsidedownLabels="0" obstacle="1" fontLimitPixelSize="0" drawLabels="1" limitNumLabels="0" scaleMin="0" mergeLines="0" maxNumLabels="2000" obstacleType="1" minFeatureSize="0"/>
          <dd_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option name="anchorPoint" type="QString" value="pole_of_inaccessibility"/>
              <Option name="blendMode" type="int" value="0"/>
              <Option name="ddProperties" type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
              <Option name="drawToAllParts" type="bool" value="false"/>
              <Option name="enabled" type="QString" value="0"/>
              <Option name="labelAnchorPoint" type="QString" value="point_on_exterior"/>
              <Option name="lineSymbol" type="QString" value="&lt;symbol force_rhr=&quot;0&quot; is_animated=&quot;0&quot; name=&quot;symbol&quot; type=&quot;line&quot; frame_rate=&quot;10&quot; alpha=&quot;1&quot; clip_to_extent=&quot;1&quot;>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; type=&quot;QString&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; type=&quot;QString&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;layer pass=&quot;0&quot; enabled=&quot;1&quot; locked=&quot;0&quot; id=&quot;{e0161c43-c9d4-4862-8f31-0efb003d8405}&quot; class=&quot;SimpleLine&quot;>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;align_dash_pattern&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;capstyle&quot; type=&quot;QString&quot; value=&quot;square&quot;/>&lt;Option name=&quot;customdash&quot; type=&quot;QString&quot; value=&quot;5;2&quot;/>&lt;Option name=&quot;customdash_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;customdash_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;dash_pattern_offset&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;dash_pattern_offset_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;dash_pattern_offset_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;draw_inside_polygon&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;joinstyle&quot; type=&quot;QString&quot; value=&quot;bevel&quot;/>&lt;Option name=&quot;line_color&quot; type=&quot;QString&quot; value=&quot;60,60,60,255,rgb:0.23529411764705882,0.23529411764705882,0.23529411764705882,1&quot;/>&lt;Option name=&quot;line_style&quot; type=&quot;QString&quot; value=&quot;solid&quot;/>&lt;Option name=&quot;line_width&quot; type=&quot;QString&quot; value=&quot;0.3&quot;/>&lt;Option name=&quot;line_width_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;offset&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;offset_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;offset_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;ring_filter&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;trim_distance_end&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;trim_distance_end_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;trim_distance_end_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;trim_distance_start&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;trim_distance_start_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;trim_distance_start_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;tweak_dash_pattern_on_corners&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;use_custom_dash&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;width_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;/Option>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; type=&quot;QString&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; type=&quot;QString&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>"/>
              <Option name="minLength" type="double" value="0"/>
              <Option name="minLengthMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="minLengthUnit" type="QString" value="MM"/>
              <Option name="offsetFromAnchor" type="double" value="0"/>
              <Option name="offsetFromAnchorMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="offsetFromAnchorUnit" type="QString" value="MM"/>
              <Option name="offsetFromLabel" type="double" value="0"/>
              <Option name="offsetFromLabelMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="offsetFromLabelUnit" type="QString" value="MM"/>
            </Option>
          </callout>
        </settings>
      </rule>
      <rule filter="map_exist(&#xd;&#xa;  &quot;type_regulations&quot;,&#xd;&#xa;  'valtakunnallisestiMerkittavaRakennettuKulttuuriymparisto'&#xd;&#xa;)&#xd;&#xa;AND map_exist(&#xd;&#xa;  &quot;type_regulations&quot;['valtakunnallisestiMerkittavaRakennettuKulttuuriymparisto'],&#xd;&#xa;  'valtakunnallinen'&#xd;&#xa;)" description="Valtakunnallisesti merkittävä rakennettu kulttuuriympäristö" key="{520c22df-71ba-41fd-98cd-b7ba7237c290}">
        <settings calloutType="simple">
          <text-style tabStopDistanceMapUnitScale="3x:0,0,0,0,0,0" multilineHeightUnit="Percentage" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontLetterSpacing="0" capitalization="0" fontSizeUnit="Point" textColor="50,50,50,255,rgb:0.19607843137254902,0.19607843137254902,0.19607843137254902,1" textOrientation="horizontal" fontKerning="1" textOpacity="1" previewBkgrdColor="255,255,255,255,rgb:1,1,1,1" namedStyle="Bold" fontUnderline="0" fontWeight="75" fontFamily="Arial" forcedItalic="0" fontItalic="0" isExpression="1" useSubstitutions="0" legendString="Aa" fontSize="10" fieldName="array_to_string(&quot;short_names&quot;, '/')" fontStrikeout="0" multilineHeight="1" tabStopDistance="80" fontWordSpacing="0" tabStopDistanceUnit="Point" forcedBold="0" blendMode="0" allowHtml="0">
            <families/>
            <text-buffer bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferNoFill="1" bufferColor="124,217,204,255,rgb:0.48627450980392156,0.85098039215686272,0.80000000000000004,1" bufferSizeUnits="Point" bufferJoinStyle="128" bufferDraw="0" bufferSize="10" bufferOpacity="1" bufferBlendMode="0"/>
            <text-mask maskedSymbolLayers="" maskSizeUnits="Point" maskOpacity="1" maskSize="15" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskJoinStyle="128" maskSize2="15" maskEnabled="0" maskType="0"/>
            <background shapeSizeUnit="Point" shapeOffsetX="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeDraw="1" shapeFillColor="255,255,255,255,rgb:1,1,1,1" shapeType="2" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeSVGFile="" shapeBorderColor="111,168,218,255,rgb:0.43529411764705883,0.6588235294117647,0.85490196078431369,1" shapeBorderWidth="1" shapeBorderWidthUnit="Point" shapeOpacity="1" shapeRadiiX="0" shapeBlendMode="0" shapeSizeType="0" shapeRadiiY="0" shapeRotationType="0" shapeOffsetUnit="Point" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeJoinStyle="64" shapeSizeY="0" shapeRotation="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeSizeX="2" shapeRadiiUnit="Point" shapeOffsetY="-1.5">
              <symbol force_rhr="0" is_animated="0" name="markerSymbol" type="marker" frame_rate="10" alpha="1" clip_to_extent="1">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" type="QString" value=""/>
                    <Option name="properties"/>
                    <Option name="type" type="QString" value="collection"/>
                  </Option>
                </data_defined_properties>
                <layer pass="0" enabled="1" locked="0" id="" class="SimpleMarker">
                  <Option type="Map">
                    <Option name="angle" type="QString" value="0"/>
                    <Option name="cap_style" type="QString" value="square"/>
                    <Option name="color" type="QString" value="133,182,111,255,rgb:0.52156862745098043,0.71372549019607845,0.43529411764705883,1"/>
                    <Option name="horizontal_anchor_point" type="QString" value="1"/>
                    <Option name="joinstyle" type="QString" value="bevel"/>
                    <Option name="name" type="QString" value="circle"/>
                    <Option name="offset" type="QString" value="0,0"/>
                    <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="offset_unit" type="QString" value="MM"/>
                    <Option name="outline_color" type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1"/>
                    <Option name="outline_style" type="QString" value="solid"/>
                    <Option name="outline_width" type="QString" value="0"/>
                    <Option name="outline_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="outline_width_unit" type="QString" value="MM"/>
                    <Option name="scale_method" type="QString" value="diameter"/>
                    <Option name="size" type="QString" value="2"/>
                    <Option name="size_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="size_unit" type="QString" value="MM"/>
                    <Option name="vertical_anchor_point" type="QString" value="1"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
              <symbol force_rhr="0" is_animated="0" name="fillSymbol" type="fill" frame_rate="10" alpha="1" clip_to_extent="1">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" type="QString" value=""/>
                    <Option name="properties"/>
                    <Option name="type" type="QString" value="collection"/>
                  </Option>
                </data_defined_properties>
                <layer pass="0" enabled="1" locked="0" id="" class="SimpleFill">
                  <Option type="Map">
                    <Option name="border_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="color" type="QString" value="255,255,255,255,rgb:1,1,1,1"/>
                    <Option name="joinstyle" type="QString" value="bevel"/>
                    <Option name="offset" type="QString" value="0,0"/>
                    <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="offset_unit" type="QString" value="MM"/>
                    <Option name="outline_color" type="QString" value="111,168,218,255,rgb:0.43529411764705883,0.6588235294117647,0.85490196078431369,1"/>
                    <Option name="outline_style" type="QString" value="solid"/>
                    <Option name="outline_width" type="QString" value="1"/>
                    <Option name="outline_width_unit" type="QString" value="Point"/>
                    <Option name="style" type="QString" value="solid"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowOpacity="0.69999999999999996" shadowColor="0,0,0,255,rgb:0,0,0,1" shadowDraw="0" shadowUnder="0" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowBlendMode="6" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowScale="100" shadowOffsetUnit="MM" shadowOffsetGlobal="1" shadowOffsetDist="1" shadowRadiusUnit="MM" shadowRadius="1.5" shadowOffsetAngle="135" shadowRadiusAlphaOnly="0"/>
            <dd_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format autoWrapLength="0" reverseDirectionSymbol="0" plussign="0" formatNumbers="0" decimals="3" leftDirectionSymbol="&lt;" placeDirectionSymbol="0" useMaxLineLengthForAutoWrap="1" multilineAlign="0" rightDirectionSymbol=">" wrapChar="" addDirectionSymbol="0"/>
          <placement polygonPlacementFlags="2" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" lineAnchorType="0" distMapUnitScale="3x:0,0,0,0,0,0" maximumDistanceUnit="MM" quadOffset="4" overlapHandling="PreventOverlap" priority="5" lineAnchorClipping="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" distUnits="Point" layerType="LineGeometry" xOffset="0" prioritization="PreferCloser" allowDegraded="0" maxCurvedCharAngleOut="-25" offsetType="0" offsetUnits="MM" geometryGenerator="" rotationUnit="AngleDegrees" overrunDistance="0" lineAnchorTextPoint="FollowPlacement" lineAnchorPercent="0.5" repeatDistanceUnits="MM" placement="2" dist="2" overrunDistanceUnit="MM" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" maxCurvedCharAngleIn="25" maximumDistance="0" geometryGeneratorType="PointGeometry" placementFlags="10" rotationAngle="0" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" geometryGeneratorEnabled="0" maximumDistanceMapUnitScale="3x:0,0,0,0,0,0" preserveRotation="1" centroidInside="0" yOffset="0" centroidWhole="0" repeatDistance="0" fitInPolygonOnly="0"/>
          <rendering labelPerPart="0" scaleVisibility="0" unplacedVisibility="0" scaleMax="0" obstacleFactor="1" fontMaxPixelSize="10000" zIndex="0" fontMinPixelSize="3" upsidedownLabels="0" obstacle="1" fontLimitPixelSize="0" drawLabels="1" limitNumLabels="0" scaleMin="0" mergeLines="0" maxNumLabels="2000" obstacleType="1" minFeatureSize="0"/>
          <dd_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option name="anchorPoint" type="QString" value="pole_of_inaccessibility"/>
              <Option name="blendMode" type="int" value="0"/>
              <Option name="ddProperties" type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
              <Option name="drawToAllParts" type="bool" value="false"/>
              <Option name="enabled" type="QString" value="0"/>
              <Option name="labelAnchorPoint" type="QString" value="point_on_exterior"/>
              <Option name="lineSymbol" type="QString" value="&lt;symbol force_rhr=&quot;0&quot; is_animated=&quot;0&quot; name=&quot;symbol&quot; type=&quot;line&quot; frame_rate=&quot;10&quot; alpha=&quot;1&quot; clip_to_extent=&quot;1&quot;>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; type=&quot;QString&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; type=&quot;QString&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;layer pass=&quot;0&quot; enabled=&quot;1&quot; locked=&quot;0&quot; id=&quot;{bbd4a37a-a256-427c-9ba4-a5e720e7120b}&quot; class=&quot;SimpleLine&quot;>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;align_dash_pattern&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;capstyle&quot; type=&quot;QString&quot; value=&quot;square&quot;/>&lt;Option name=&quot;customdash&quot; type=&quot;QString&quot; value=&quot;5;2&quot;/>&lt;Option name=&quot;customdash_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;customdash_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;dash_pattern_offset&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;dash_pattern_offset_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;dash_pattern_offset_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;draw_inside_polygon&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;joinstyle&quot; type=&quot;QString&quot; value=&quot;bevel&quot;/>&lt;Option name=&quot;line_color&quot; type=&quot;QString&quot; value=&quot;60,60,60,255,rgb:0.23529411764705882,0.23529411764705882,0.23529411764705882,1&quot;/>&lt;Option name=&quot;line_style&quot; type=&quot;QString&quot; value=&quot;solid&quot;/>&lt;Option name=&quot;line_width&quot; type=&quot;QString&quot; value=&quot;0.3&quot;/>&lt;Option name=&quot;line_width_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;offset&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;offset_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;offset_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;ring_filter&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;trim_distance_end&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;trim_distance_end_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;trim_distance_end_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;trim_distance_start&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;trim_distance_start_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;trim_distance_start_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;tweak_dash_pattern_on_corners&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;use_custom_dash&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;width_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;/Option>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; type=&quot;QString&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; type=&quot;QString&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>"/>
              <Option name="minLength" type="double" value="0"/>
              <Option name="minLengthMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="minLengthUnit" type="QString" value="MM"/>
              <Option name="offsetFromAnchor" type="double" value="0"/>
              <Option name="offsetFromAnchorMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="offsetFromAnchorUnit" type="QString" value="MM"/>
              <Option name="offsetFromLabel" type="double" value="0"/>
              <Option name="offsetFromLabelMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="offsetFromLabelUnit" type="QString" value="MM"/>
            </Option>
          </callout>
        </settings>
      </rule>
      <rule filter="map_exist(&#xd;&#xa;  &quot;type_regulations&quot;,&#xd;&#xa;  'natura2000VerkostonAlue'&#xd;&#xa;)&#xd;&#xa;AND map_exist(&#xd;&#xa;  &quot;type_regulations&quot;['natura2000VerkostonAlue'],&#xd;&#xa;  'osaAlue'&#xd;&#xa;)" description="Natura 2000" key="{aa85bdd1-c569-4e2b-8966-6fe4ea05a991}">
        <settings calloutType="simple">
          <text-style tabStopDistanceMapUnitScale="3x:0,0,0,0,0,0" multilineHeightUnit="Percentage" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontLetterSpacing="0" capitalization="0" fontSizeUnit="Point" textColor="150,150,150,255,rgb:0.58823529411764708,0.58823529411764708,0.58823529411764708,1" textOrientation="horizontal" fontKerning="1" textOpacity="1" previewBkgrdColor="255,255,255,255,rgb:1,1,1,1" namedStyle="Bold" fontUnderline="0" fontWeight="75" fontFamily="Arial" forcedItalic="0" fontItalic="0" isExpression="1" useSubstitutions="0" legendString="Aa" fontSize="10" fieldName="array_to_string(&quot;short_names&quot;, '/')" fontStrikeout="0" multilineHeight="1" tabStopDistance="80" fontWordSpacing="0" tabStopDistanceUnit="Point" forcedBold="0" blendMode="0" allowHtml="0">
            <families/>
            <text-buffer bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferNoFill="1" bufferColor="250,250,250,255,rgb:0.98039215686274506,0.98039215686274506,0.98039215686274506,1" bufferSizeUnits="MM" bufferJoinStyle="128" bufferDraw="0" bufferSize="1" bufferOpacity="1" bufferBlendMode="0"/>
            <text-mask maskedSymbolLayers="" maskSizeUnits="MM" maskOpacity="1" maskSize="1.5" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskJoinStyle="128" maskSize2="1.5" maskEnabled="0" maskType="0"/>
            <background shapeSizeUnit="Point" shapeOffsetX="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeDraw="1" shapeFillColor="255,255,255,255,rgb:1,1,1,1" shapeType="2" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeSVGFile="" shapeBorderColor="128,128,128,131,rgb:0.50196078431372548,0.50196078431372548,0.50196078431372548,0.51372549019607838" shapeBorderWidth="1" shapeBorderWidthUnit="Point" shapeOpacity="1" shapeRadiiX="0" shapeBlendMode="0" shapeSizeType="0" shapeRadiiY="0" shapeRotationType="0" shapeOffsetUnit="Point" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeJoinStyle="64" shapeSizeY="0" shapeRotation="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeSizeX="2" shapeRadiiUnit="Point" shapeOffsetY="-1.5">
              <symbol force_rhr="0" is_animated="0" name="markerSymbol" type="marker" frame_rate="10" alpha="1" clip_to_extent="1">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" type="QString" value=""/>
                    <Option name="properties"/>
                    <Option name="type" type="QString" value="collection"/>
                  </Option>
                </data_defined_properties>
                <layer pass="0" enabled="1" locked="0" id="" class="SimpleMarker">
                  <Option type="Map">
                    <Option name="angle" type="QString" value="0"/>
                    <Option name="cap_style" type="QString" value="square"/>
                    <Option name="color" type="QString" value="229,182,54,255,rgb:0.89803921568627454,0.71372549019607845,0.21176470588235294,1"/>
                    <Option name="horizontal_anchor_point" type="QString" value="1"/>
                    <Option name="joinstyle" type="QString" value="bevel"/>
                    <Option name="name" type="QString" value="circle"/>
                    <Option name="offset" type="QString" value="0,0"/>
                    <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="offset_unit" type="QString" value="MM"/>
                    <Option name="outline_color" type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1"/>
                    <Option name="outline_style" type="QString" value="solid"/>
                    <Option name="outline_width" type="QString" value="0"/>
                    <Option name="outline_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="outline_width_unit" type="QString" value="MM"/>
                    <Option name="scale_method" type="QString" value="diameter"/>
                    <Option name="size" type="QString" value="2"/>
                    <Option name="size_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="size_unit" type="QString" value="MM"/>
                    <Option name="vertical_anchor_point" type="QString" value="1"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
              <symbol force_rhr="0" is_animated="0" name="fillSymbol" type="fill" frame_rate="10" alpha="1" clip_to_extent="1">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" type="QString" value=""/>
                    <Option name="properties"/>
                    <Option name="type" type="QString" value="collection"/>
                  </Option>
                </data_defined_properties>
                <layer pass="0" enabled="1" locked="0" id="" class="SimpleFill">
                  <Option type="Map">
                    <Option name="border_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="color" type="QString" value="255,255,255,255,rgb:1,1,1,1"/>
                    <Option name="joinstyle" type="QString" value="bevel"/>
                    <Option name="offset" type="QString" value="0,0"/>
                    <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="offset_unit" type="QString" value="MM"/>
                    <Option name="outline_color" type="QString" value="128,128,128,131,rgb:0.50196078431372548,0.50196078431372548,0.50196078431372548,0.51372549019607838"/>
                    <Option name="outline_style" type="QString" value="solid"/>
                    <Option name="outline_width" type="QString" value="1"/>
                    <Option name="outline_width_unit" type="QString" value="Point"/>
                    <Option name="style" type="QString" value="solid"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowOpacity="0.69999999999999996" shadowColor="0,0,0,255,rgb:0,0,0,1" shadowDraw="0" shadowUnder="0" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowBlendMode="6" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowScale="100" shadowOffsetUnit="MM" shadowOffsetGlobal="1" shadowOffsetDist="1" shadowRadiusUnit="MM" shadowRadius="1.5" shadowOffsetAngle="135" shadowRadiusAlphaOnly="0"/>
            <dd_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format autoWrapLength="0" reverseDirectionSymbol="0" plussign="0" formatNumbers="0" decimals="3" leftDirectionSymbol="&lt;" placeDirectionSymbol="0" useMaxLineLengthForAutoWrap="1" multilineAlign="0" rightDirectionSymbol=">" wrapChar="" addDirectionSymbol="0"/>
          <placement polygonPlacementFlags="2" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" lineAnchorType="0" distMapUnitScale="3x:0,0,0,0,0,0" maximumDistanceUnit="MM" quadOffset="4" overlapHandling="PreventOverlap" priority="5" lineAnchorClipping="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" distUnits="Point" layerType="LineGeometry" xOffset="0" prioritization="PreferCloser" allowDegraded="0" maxCurvedCharAngleOut="-25" offsetType="0" offsetUnits="MM" geometryGenerator="" rotationUnit="AngleDegrees" overrunDistance="0" lineAnchorTextPoint="FollowPlacement" lineAnchorPercent="0.5" repeatDistanceUnits="MM" placement="2" dist="2" overrunDistanceUnit="MM" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" maxCurvedCharAngleIn="25" maximumDistance="0" geometryGeneratorType="PointGeometry" placementFlags="10" rotationAngle="0" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" geometryGeneratorEnabled="0" maximumDistanceMapUnitScale="3x:0,0,0,0,0,0" preserveRotation="1" centroidInside="0" yOffset="0" centroidWhole="0" repeatDistance="0" fitInPolygonOnly="0"/>
          <rendering labelPerPart="0" scaleVisibility="0" unplacedVisibility="0" scaleMax="0" obstacleFactor="1" fontMaxPixelSize="10000" zIndex="0" fontMinPixelSize="3" upsidedownLabels="0" obstacle="1" fontLimitPixelSize="0" drawLabels="1" limitNumLabels="0" scaleMin="0" mergeLines="0" maxNumLabels="2000" obstacleType="1" minFeatureSize="0"/>
          <dd_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option name="anchorPoint" type="QString" value="pole_of_inaccessibility"/>
              <Option name="blendMode" type="int" value="0"/>
              <Option name="ddProperties" type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
              <Option name="drawToAllParts" type="bool" value="false"/>
              <Option name="enabled" type="QString" value="0"/>
              <Option name="labelAnchorPoint" type="QString" value="point_on_exterior"/>
              <Option name="lineSymbol" type="QString" value="&lt;symbol force_rhr=&quot;0&quot; is_animated=&quot;0&quot; name=&quot;symbol&quot; type=&quot;line&quot; frame_rate=&quot;10&quot; alpha=&quot;1&quot; clip_to_extent=&quot;1&quot;>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; type=&quot;QString&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; type=&quot;QString&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;layer pass=&quot;0&quot; enabled=&quot;1&quot; locked=&quot;0&quot; id=&quot;{8c8c7e34-545b-4859-bd2a-5b1daf4a1d9f}&quot; class=&quot;SimpleLine&quot;>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;align_dash_pattern&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;capstyle&quot; type=&quot;QString&quot; value=&quot;square&quot;/>&lt;Option name=&quot;customdash&quot; type=&quot;QString&quot; value=&quot;5;2&quot;/>&lt;Option name=&quot;customdash_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;customdash_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;dash_pattern_offset&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;dash_pattern_offset_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;dash_pattern_offset_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;draw_inside_polygon&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;joinstyle&quot; type=&quot;QString&quot; value=&quot;bevel&quot;/>&lt;Option name=&quot;line_color&quot; type=&quot;QString&quot; value=&quot;60,60,60,255,rgb:0.23529411764705882,0.23529411764705882,0.23529411764705882,1&quot;/>&lt;Option name=&quot;line_style&quot; type=&quot;QString&quot; value=&quot;solid&quot;/>&lt;Option name=&quot;line_width&quot; type=&quot;QString&quot; value=&quot;0.3&quot;/>&lt;Option name=&quot;line_width_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;offset&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;offset_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;offset_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;ring_filter&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;trim_distance_end&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;trim_distance_end_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;trim_distance_end_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;trim_distance_start&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;trim_distance_start_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;trim_distance_start_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;tweak_dash_pattern_on_corners&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;use_custom_dash&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;width_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;/Option>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; type=&quot;QString&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; type=&quot;QString&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>"/>
              <Option name="minLength" type="double" value="0"/>
              <Option name="minLengthMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="minLengthUnit" type="QString" value="MM"/>
              <Option name="offsetFromAnchor" type="double" value="0"/>
              <Option name="offsetFromAnchorMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="offsetFromAnchorUnit" type="QString" value="MM"/>
              <Option name="offsetFromLabel" type="double" value="0"/>
              <Option name="offsetFromLabelMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="offsetFromLabelUnit" type="QString" value="MM"/>
            </Option>
          </callout>
        </settings>
      </rule>
      <rule filter="map_exist(&#xd;&#xa;  &quot;type_regulations&quot;,&#xd;&#xa;  'luonnonMonimuotoisuudenKannaltaErityisenTarkeaAlue'&#xd;&#xa;)&#xd;&#xa;AND map_exist(&#xd;&#xa;  &quot;type_regulations&quot;['luonnonMonimuotoisuudenKannaltaErityisenTarkeaAlue'],&#xd;&#xa;  'osaAlue'&#xd;&#xa;)" description="Luonnon monimuotoisuuden kannalta erityisen tärkeä alue" key="{31e40048-9bbf-4428-b3e7-8ca7703acc4e}">
        <settings calloutType="simple">
          <text-style tabStopDistanceMapUnitScale="3x:0,0,0,0,0,0" multilineHeightUnit="Percentage" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontLetterSpacing="0" capitalization="0" fontSizeUnit="Point" textColor="50,50,50,255,rgb:0.19607843137254902,0.19607843137254902,0.19607843137254902,1" textOrientation="horizontal" fontKerning="1" textOpacity="1" previewBkgrdColor="255,255,255,255,rgb:1,1,1,1" namedStyle="Bold" fontUnderline="0" fontWeight="75" fontFamily="Arial" forcedItalic="0" fontItalic="0" isExpression="1" useSubstitutions="0" legendString="Aa" fontSize="10" fieldName="array_to_string(&quot;short_names&quot;, '/')" fontStrikeout="0" multilineHeight="1" tabStopDistance="80" fontWordSpacing="0" tabStopDistanceUnit="Point" forcedBold="0" blendMode="0" allowHtml="0">
            <families/>
            <text-buffer bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferNoFill="1" bufferColor="250,250,250,255,rgb:0.98039215686274506,0.98039215686274506,0.98039215686274506,1" bufferSizeUnits="MM" bufferJoinStyle="128" bufferDraw="0" bufferSize="1" bufferOpacity="1" bufferBlendMode="0"/>
            <text-mask maskedSymbolLayers="" maskSizeUnits="MM" maskOpacity="1" maskSize="1.5" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskJoinStyle="128" maskSize2="1.5" maskEnabled="0" maskType="0"/>
            <background shapeSizeUnit="Point" shapeOffsetX="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeDraw="1" shapeFillColor="255,255,255,255,rgb:1,1,1,1" shapeType="2" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeSVGFile="" shapeBorderColor="25,104,64,255,rgb:0.09803921568627451,0.40784313725490196,0.25098039215686274,1" shapeBorderWidth="1" shapeBorderWidthUnit="Point" shapeOpacity="1" shapeRadiiX="0" shapeBlendMode="0" shapeSizeType="0" shapeRadiiY="0" shapeRotationType="0" shapeOffsetUnit="Point" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeJoinStyle="64" shapeSizeY="0" shapeRotation="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeSizeX="2" shapeRadiiUnit="Point" shapeOffsetY="-1.5">
              <symbol force_rhr="0" is_animated="0" name="markerSymbol" type="marker" frame_rate="10" alpha="1" clip_to_extent="1">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" type="QString" value=""/>
                    <Option name="properties"/>
                    <Option name="type" type="QString" value="collection"/>
                  </Option>
                </data_defined_properties>
                <layer pass="0" enabled="1" locked="0" id="" class="SimpleMarker">
                  <Option type="Map">
                    <Option name="angle" type="QString" value="0"/>
                    <Option name="cap_style" type="QString" value="square"/>
                    <Option name="color" type="QString" value="183,72,75,255,rgb:0.71764705882352942,0.28235294117647058,0.29411764705882354,1"/>
                    <Option name="horizontal_anchor_point" type="QString" value="1"/>
                    <Option name="joinstyle" type="QString" value="bevel"/>
                    <Option name="name" type="QString" value="circle"/>
                    <Option name="offset" type="QString" value="0,0"/>
                    <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="offset_unit" type="QString" value="MM"/>
                    <Option name="outline_color" type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1"/>
                    <Option name="outline_style" type="QString" value="solid"/>
                    <Option name="outline_width" type="QString" value="0"/>
                    <Option name="outline_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="outline_width_unit" type="QString" value="MM"/>
                    <Option name="scale_method" type="QString" value="diameter"/>
                    <Option name="size" type="QString" value="2"/>
                    <Option name="size_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="size_unit" type="QString" value="MM"/>
                    <Option name="vertical_anchor_point" type="QString" value="1"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
              <symbol force_rhr="0" is_animated="0" name="fillSymbol" type="fill" frame_rate="10" alpha="1" clip_to_extent="1">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" type="QString" value=""/>
                    <Option name="properties"/>
                    <Option name="type" type="QString" value="collection"/>
                  </Option>
                </data_defined_properties>
                <layer pass="0" enabled="1" locked="0" id="" class="SimpleFill">
                  <Option type="Map">
                    <Option name="border_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="color" type="QString" value="255,255,255,255,rgb:1,1,1,1"/>
                    <Option name="joinstyle" type="QString" value="bevel"/>
                    <Option name="offset" type="QString" value="0,0"/>
                    <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="offset_unit" type="QString" value="MM"/>
                    <Option name="outline_color" type="QString" value="25,104,64,255,rgb:0.09803921568627451,0.40784313725490196,0.25098039215686274,1"/>
                    <Option name="outline_style" type="QString" value="solid"/>
                    <Option name="outline_width" type="QString" value="1"/>
                    <Option name="outline_width_unit" type="QString" value="Point"/>
                    <Option name="style" type="QString" value="solid"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowOpacity="0.69999999999999996" shadowColor="0,0,0,255,rgb:0,0,0,1" shadowDraw="0" shadowUnder="0" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowBlendMode="6" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowScale="100" shadowOffsetUnit="MM" shadowOffsetGlobal="1" shadowOffsetDist="1" shadowRadiusUnit="MM" shadowRadius="1.5" shadowOffsetAngle="135" shadowRadiusAlphaOnly="0"/>
            <dd_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format autoWrapLength="0" reverseDirectionSymbol="0" plussign="0" formatNumbers="0" decimals="3" leftDirectionSymbol="&lt;" placeDirectionSymbol="0" useMaxLineLengthForAutoWrap="1" multilineAlign="0" rightDirectionSymbol=">" wrapChar="" addDirectionSymbol="0"/>
          <placement polygonPlacementFlags="2" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" lineAnchorType="0" distMapUnitScale="3x:0,0,0,0,0,0" maximumDistanceUnit="MM" quadOffset="4" overlapHandling="PreventOverlap" priority="5" lineAnchorClipping="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" distUnits="Point" layerType="LineGeometry" xOffset="0" prioritization="PreferCloser" allowDegraded="0" maxCurvedCharAngleOut="-25" offsetType="0" offsetUnits="MM" geometryGenerator="" rotationUnit="AngleDegrees" overrunDistance="0" lineAnchorTextPoint="FollowPlacement" lineAnchorPercent="0.5" repeatDistanceUnits="MM" placement="2" dist="2" overrunDistanceUnit="MM" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" maxCurvedCharAngleIn="25" maximumDistance="0" geometryGeneratorType="PointGeometry" placementFlags="10" rotationAngle="0" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" geometryGeneratorEnabled="0" maximumDistanceMapUnitScale="3x:0,0,0,0,0,0" preserveRotation="1" centroidInside="0" yOffset="0" centroidWhole="0" repeatDistance="0" fitInPolygonOnly="0"/>
          <rendering labelPerPart="0" scaleVisibility="0" unplacedVisibility="0" scaleMax="0" obstacleFactor="1" fontMaxPixelSize="10000" zIndex="0" fontMinPixelSize="3" upsidedownLabels="0" obstacle="1" fontLimitPixelSize="0" drawLabels="1" limitNumLabels="0" scaleMin="0" mergeLines="0" maxNumLabels="2000" obstacleType="1" minFeatureSize="0"/>
          <dd_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option name="anchorPoint" type="QString" value="pole_of_inaccessibility"/>
              <Option name="blendMode" type="int" value="0"/>
              <Option name="ddProperties" type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
              <Option name="drawToAllParts" type="bool" value="false"/>
              <Option name="enabled" type="QString" value="0"/>
              <Option name="labelAnchorPoint" type="QString" value="point_on_exterior"/>
              <Option name="lineSymbol" type="QString" value="&lt;symbol force_rhr=&quot;0&quot; is_animated=&quot;0&quot; name=&quot;symbol&quot; type=&quot;line&quot; frame_rate=&quot;10&quot; alpha=&quot;1&quot; clip_to_extent=&quot;1&quot;>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; type=&quot;QString&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; type=&quot;QString&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;layer pass=&quot;0&quot; enabled=&quot;1&quot; locked=&quot;0&quot; id=&quot;{8a8a75b0-c2d8-4e2e-ab30-7d1be84a0206}&quot; class=&quot;SimpleLine&quot;>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;align_dash_pattern&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;capstyle&quot; type=&quot;QString&quot; value=&quot;square&quot;/>&lt;Option name=&quot;customdash&quot; type=&quot;QString&quot; value=&quot;5;2&quot;/>&lt;Option name=&quot;customdash_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;customdash_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;dash_pattern_offset&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;dash_pattern_offset_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;dash_pattern_offset_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;draw_inside_polygon&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;joinstyle&quot; type=&quot;QString&quot; value=&quot;bevel&quot;/>&lt;Option name=&quot;line_color&quot; type=&quot;QString&quot; value=&quot;60,60,60,255,rgb:0.23529411764705882,0.23529411764705882,0.23529411764705882,1&quot;/>&lt;Option name=&quot;line_style&quot; type=&quot;QString&quot; value=&quot;solid&quot;/>&lt;Option name=&quot;line_width&quot; type=&quot;QString&quot; value=&quot;0.3&quot;/>&lt;Option name=&quot;line_width_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;offset&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;offset_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;offset_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;ring_filter&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;trim_distance_end&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;trim_distance_end_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;trim_distance_end_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;trim_distance_start&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;trim_distance_start_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;trim_distance_start_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;tweak_dash_pattern_on_corners&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;use_custom_dash&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;width_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;/Option>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; type=&quot;QString&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; type=&quot;QString&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>"/>
              <Option name="minLength" type="double" value="0"/>
              <Option name="minLengthMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="minLengthUnit" type="QString" value="MM"/>
              <Option name="offsetFromAnchor" type="double" value="0"/>
              <Option name="offsetFromAnchorMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="offsetFromAnchorUnit" type="QString" value="MM"/>
              <Option name="offsetFromLabel" type="double" value="0"/>
              <Option name="offsetFromLabelMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="offsetFromLabelUnit" type="QString" value="MM"/>
            </Option>
          </callout>
        </settings>
      </rule>
      <rule filter="ELSE" key="{ffe2dc24-bf11-448f-9fb4-e1e07d696c6e}">
        <settings calloutType="simple">
          <text-style tabStopDistanceMapUnitScale="3x:0,0,0,0,0,0" multilineHeightUnit="Percentage" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontLetterSpacing="0" capitalization="0" fontSizeUnit="Point" textColor="50,50,50,255,rgb:0.19607843137254902,0.19607843137254902,0.19607843137254902,1" textOrientation="horizontal" fontKerning="1" textOpacity="1" previewBkgrdColor="255,255,255,255,rgb:1,1,1,1" namedStyle="Bold" fontUnderline="0" fontWeight="75" fontFamily="Arial" forcedItalic="0" fontItalic="0" isExpression="1" useSubstitutions="0" legendString="Aa" fontSize="10" fieldName="array_to_string(&quot;short_names&quot;, '/')" fontStrikeout="0" multilineHeight="1" tabStopDistance="80" fontWordSpacing="0" tabStopDistanceUnit="Point" forcedBold="0" blendMode="0" allowHtml="0">
            <families/>
            <text-buffer bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferNoFill="1" bufferColor="250,250,250,255,rgb:0.98039215686274506,0.98039215686274506,0.98039215686274506,1" bufferSizeUnits="MM" bufferJoinStyle="128" bufferDraw="0" bufferSize="1" bufferOpacity="1" bufferBlendMode="0"/>
            <text-mask maskedSymbolLayers="" maskSizeUnits="MM" maskOpacity="1" maskSize="1.5" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskJoinStyle="128" maskSize2="1.5" maskEnabled="0" maskType="0"/>
            <background shapeSizeUnit="Point" shapeOffsetX="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeDraw="0" shapeFillColor="255,255,255,255,rgb:1,1,1,1" shapeType="0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeSVGFile="" shapeBorderColor="111,168,218,255,rgb:0.43529411764705883,0.6588235294117647,0.85490196078431369,1" shapeBorderWidth="1" shapeBorderWidthUnit="Point" shapeOpacity="1" shapeRadiiX="4" shapeBlendMode="0" shapeSizeType="0" shapeRadiiY="4" shapeRotationType="0" shapeOffsetUnit="Point" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeJoinStyle="64" shapeSizeY="2" shapeRotation="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeSizeX="2" shapeRadiiUnit="Point" shapeOffsetY="-1.5">
              <symbol force_rhr="0" is_animated="0" name="markerSymbol" type="marker" frame_rate="10" alpha="1" clip_to_extent="1">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" type="QString" value=""/>
                    <Option name="properties"/>
                    <Option name="type" type="QString" value="collection"/>
                  </Option>
                </data_defined_properties>
                <layer pass="0" enabled="1" locked="0" id="" class="SimpleMarker">
                  <Option type="Map">
                    <Option name="angle" type="QString" value="0"/>
                    <Option name="cap_style" type="QString" value="square"/>
                    <Option name="color" type="QString" value="145,82,45,255,rgb:0.56862745098039214,0.32156862745098042,0.17647058823529413,1"/>
                    <Option name="horizontal_anchor_point" type="QString" value="1"/>
                    <Option name="joinstyle" type="QString" value="bevel"/>
                    <Option name="name" type="QString" value="circle"/>
                    <Option name="offset" type="QString" value="0,0"/>
                    <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="offset_unit" type="QString" value="MM"/>
                    <Option name="outline_color" type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1"/>
                    <Option name="outline_style" type="QString" value="solid"/>
                    <Option name="outline_width" type="QString" value="0"/>
                    <Option name="outline_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="outline_width_unit" type="QString" value="MM"/>
                    <Option name="scale_method" type="QString" value="diameter"/>
                    <Option name="size" type="QString" value="2"/>
                    <Option name="size_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="size_unit" type="QString" value="MM"/>
                    <Option name="vertical_anchor_point" type="QString" value="1"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
              <symbol force_rhr="0" is_animated="0" name="fillSymbol" type="fill" frame_rate="10" alpha="1" clip_to_extent="1">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" type="QString" value=""/>
                    <Option name="properties"/>
                    <Option name="type" type="QString" value="collection"/>
                  </Option>
                </data_defined_properties>
                <layer pass="0" enabled="1" locked="0" id="" class="SimpleFill">
                  <Option type="Map">
                    <Option name="border_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="color" type="QString" value="255,255,255,255,rgb:1,1,1,1"/>
                    <Option name="joinstyle" type="QString" value="bevel"/>
                    <Option name="offset" type="QString" value="0,0"/>
                    <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                    <Option name="offset_unit" type="QString" value="MM"/>
                    <Option name="outline_color" type="QString" value="111,168,218,255,rgb:0.43529411764705883,0.6588235294117647,0.85490196078431369,1"/>
                    <Option name="outline_style" type="QString" value="solid"/>
                    <Option name="outline_width" type="QString" value="1"/>
                    <Option name="outline_width_unit" type="QString" value="Point"/>
                    <Option name="style" type="QString" value="solid"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowOpacity="0.69999999999999996" shadowColor="0,0,0,255,rgb:0,0,0,1" shadowDraw="0" shadowUnder="0" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowBlendMode="6" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowScale="100" shadowOffsetUnit="MM" shadowOffsetGlobal="1" shadowOffsetDist="1" shadowRadiusUnit="MM" shadowRadius="1.5" shadowOffsetAngle="135" shadowRadiusAlphaOnly="0"/>
            <dd_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format autoWrapLength="0" reverseDirectionSymbol="0" plussign="0" formatNumbers="0" decimals="3" leftDirectionSymbol="&lt;" placeDirectionSymbol="0" useMaxLineLengthForAutoWrap="1" multilineAlign="0" rightDirectionSymbol=">" wrapChar="" addDirectionSymbol="0"/>
          <placement polygonPlacementFlags="2" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" lineAnchorType="0" distMapUnitScale="3x:0,0,0,0,0,0" maximumDistanceUnit="MM" quadOffset="4" overlapHandling="PreventOverlap" priority="5" lineAnchorClipping="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" distUnits="Point" layerType="LineGeometry" xOffset="0" prioritization="PreferCloser" allowDegraded="0" maxCurvedCharAngleOut="-25" offsetType="0" offsetUnits="MM" geometryGenerator="" rotationUnit="AngleDegrees" overrunDistance="0" lineAnchorTextPoint="FollowPlacement" lineAnchorPercent="0.5" repeatDistanceUnits="MM" placement="2" dist="5" overrunDistanceUnit="MM" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" maxCurvedCharAngleIn="25" maximumDistance="0" geometryGeneratorType="PointGeometry" placementFlags="10" rotationAngle="0" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" geometryGeneratorEnabled="0" maximumDistanceMapUnitScale="3x:0,0,0,0,0,0" preserveRotation="1" centroidInside="0" yOffset="0" centroidWhole="0" repeatDistance="0" fitInPolygonOnly="0"/>
          <rendering labelPerPart="0" scaleVisibility="0" unplacedVisibility="0" scaleMax="0" obstacleFactor="1" fontMaxPixelSize="10000" zIndex="0" fontMinPixelSize="3" upsidedownLabels="0" obstacle="1" fontLimitPixelSize="0" drawLabels="1" limitNumLabels="0" scaleMin="0" mergeLines="0" maxNumLabels="2000" obstacleType="1" minFeatureSize="0"/>
          <dd_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option name="anchorPoint" type="QString" value="pole_of_inaccessibility"/>
              <Option name="blendMode" type="int" value="0"/>
              <Option name="ddProperties" type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
              <Option name="drawToAllParts" type="bool" value="false"/>
              <Option name="enabled" type="QString" value="0"/>
              <Option name="labelAnchorPoint" type="QString" value="point_on_exterior"/>
              <Option name="lineSymbol" type="QString" value="&lt;symbol force_rhr=&quot;0&quot; is_animated=&quot;0&quot; name=&quot;symbol&quot; type=&quot;line&quot; frame_rate=&quot;10&quot; alpha=&quot;1&quot; clip_to_extent=&quot;1&quot;>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; type=&quot;QString&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; type=&quot;QString&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;layer pass=&quot;0&quot; enabled=&quot;1&quot; locked=&quot;0&quot; id=&quot;{82bfd6fa-1730-455e-ab3f-125fb38a4d05}&quot; class=&quot;SimpleLine&quot;>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;align_dash_pattern&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;capstyle&quot; type=&quot;QString&quot; value=&quot;square&quot;/>&lt;Option name=&quot;customdash&quot; type=&quot;QString&quot; value=&quot;5;2&quot;/>&lt;Option name=&quot;customdash_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;customdash_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;dash_pattern_offset&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;dash_pattern_offset_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;dash_pattern_offset_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;draw_inside_polygon&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;joinstyle&quot; type=&quot;QString&quot; value=&quot;bevel&quot;/>&lt;Option name=&quot;line_color&quot; type=&quot;QString&quot; value=&quot;60,60,60,255,rgb:0.23529411764705882,0.23529411764705882,0.23529411764705882,1&quot;/>&lt;Option name=&quot;line_style&quot; type=&quot;QString&quot; value=&quot;solid&quot;/>&lt;Option name=&quot;line_width&quot; type=&quot;QString&quot; value=&quot;0.3&quot;/>&lt;Option name=&quot;line_width_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;offset&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;offset_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;offset_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;ring_filter&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;trim_distance_end&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;trim_distance_end_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;trim_distance_end_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;trim_distance_start&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;trim_distance_start_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option name=&quot;trim_distance_start_unit&quot; type=&quot;QString&quot; value=&quot;MM&quot;/>&lt;Option name=&quot;tweak_dash_pattern_on_corners&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;use_custom_dash&quot; type=&quot;QString&quot; value=&quot;0&quot;/>&lt;Option name=&quot;width_map_unit_scale&quot; type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;/Option>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; type=&quot;QString&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; type=&quot;QString&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>"/>
              <Option name="minLength" type="double" value="0"/>
              <Option name="minLengthMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="minLengthUnit" type="QString" value="MM"/>
              <Option name="offsetFromAnchor" type="double" value="0"/>
              <Option name="offsetFromAnchorMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="offsetFromAnchorUnit" type="QString" value="MM"/>
              <Option name="offsetFromLabel" type="double" value="0"/>
              <Option name="offsetFromLabelMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="offsetFromLabelUnit" type="QString" value="MM"/>
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
