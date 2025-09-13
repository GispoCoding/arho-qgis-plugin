import json
from collections.abc import Iterator
from copy import deepcopy

import psycopg
import pytest

from database import codes
from lambdas.koodistot_loader.koodistot_loader import KoodistotLoader, get_code_list_url

lifecycle_status_response = {
    "meta": {"code": 200, "from": 0, "resultCount": 2, "totalResults": 2},
    "results": [
        {
            "id": "476c165b-373d-46fb-b81d-e1d8fbd198bd",
            "codeValue": "02",
            "uri": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/02",
            "url": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/kaavaelinkaari/codes/02",
            "status": "VALID",
            "order": 2,
            "hierarchyLevel": 1,
            "created": "2023-03-28T13:48:49.519Z",
            "modified": "2023-11-29T14:12:44.634Z",
            "statusModified": "2023-03-28T13:48:49.519Z",
            "prefLabel": {
                "en": "Pending",
                "fi": "Vireilletullut",
                "sv": "Blivit anhängigt",
            },
            "description": {
                "en": "The plan has become pending through public notice or its status as pending has been announced in connection with a planning review.",
                "fi": "Kaava on kuulutettu vireille tai vireille tulosta on ilmoitettu kaavoituskatsauksen yhteydessä.",
                "sv": "Planen har kungjorts anhängig eller anhängiggörandet har meddelats i samband med planläggningsöversikten.",
            },
            "codeScheme": {
                "uri": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari",
                "url": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/kaavaelinkaari",
            },
            "membersUrl": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/kaavaelinkaari/codes/02/members/",
        },
        {
            "id": "5c3c5719-2c09-43f2-b0fb-1d6b36812419",
            "codeValue": "03",
            "uri": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
            "url": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/kaavaelinkaari/codes/03",
            "status": "VALID",
            "order": 3,
            "hierarchyLevel": 1,
            "created": "2023-03-28T13:48:49.526Z",
            "modified": "2023-11-29T14:12:44.644Z",
            "statusModified": "2023-03-28T13:48:49.526Z",
            "prefLabel": {"en": "Preparation", "fi": "Valmistelu", "sv": "Beredning"},
            "description": {
                "en": "A phase of plan preparation, during which the participation and assessment scheme are drawn up and interested parties are given the opportunity to express their opinion on the preparation material of the plan.",
                "fi": "Kaavan laatimisen vaihe, jossa laaditaan osallistumis- ja arviointisuunnitelma ja osallisille annetaan mahdollisuus esittää mielipiteensä kaavan valmisteluaineistosta.",
                "sv": "Skede av utarbetandet av en plan där en plan för deltagande och bedömning utarbetas och parterna ges möjlighet att uttrycka sina åsikter om beredningsmaterialet rörande planen.",
            },
            "codeScheme": {
                "uri": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari",
                "url": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/kaavaelinkaari",
            },
            "membersUrl": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/kaavaelinkaari/codes/03/members/",
        },
    ],
}

additional_lifecycle_status = {
    "id": "9d0f3cf3-9653-4eea-8289-cc09b9ffa6e5",
    "codeValue": "04",
    "uri": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/04",
    "url": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/kaavaelinkaari/codes/04",
    "status": "VALID",
    "order": 4,
    "hierarchyLevel": 1,
    "created": "2023-03-28T13:48:49.532Z",
    "modified": "2023-11-29T14:12:44.653Z",
    "statusModified": "2023-03-28T13:48:49.532Z",
    "prefLabel": {"en": "Plan proposal", "fi": "Kaavaehdotus", "sv": "Planförslag"},
    "description": {
        "en": "A phase of plan preparation, during which the plan proposal is presented to the public, people can submit written complaints and opinions are requested.",
        "fi": "Kaavan laatimisen vaihe, jonka aikana kaavaehdotus asetetaan julkisesti nähtäville ja siitä voi tehdä kirjallisen muistutuksen ja siitä pyydetään lausuntoja.",
        "sv": "Skede av utarbetandet av en plan under vilken planförslaget läggs fram offentligt och skriftliga anmärkningar kan inlämnas samt utlåtanden begärs om det.",
    },
    "codeScheme": {
        "uri": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari",
        "url": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/kaavaelinkaari",
    },
    "membersUrl": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/kaavaelinkaari/codes/04/members/",
}

changed_lifecycle_status_response = deepcopy(lifecycle_status_response)
changed_lifecycle_status_response["results"].append(  # type:ignore
    additional_lifecycle_status
)
changed_lifecycle_status_response["meta"]["resultCount"] += 1  # type:ignore
changed_lifecycle_status_response["meta"]["totalResults"] += 1  # type:ignore

type_of_plan_regulation_response = {
    "meta": {"code": 200, "from": 0, "resultCount": 4, "totalResults": 4},
    "results": [
        {
            "id": "e6f03e18-f292-4068-b6a6-b9e52206accc",
            "codeValue": "asuinpientaloalue",
            "uri": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji/code/asuinpientaloalue",
            "url": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/RY_Kaavamaarayslaji/codes/asuinpientaloalue",
            "status": "DRAFT",
            "order": 299,
            "hierarchyLevel": 2,
            "created": "2023-04-12T07:41:52.734Z",
            "modified": "2023-12-18T10:16:39.342Z",
            "statusModified": "2023-04-12T07:41:52.734Z",
            "prefLabel": {
                "en": "Area of residential houses",
                "fi": "Asuinpientaloalue",
                "sv": "Område för småhus",
            },
            "description": {
                "fi": "Ilmaisee, että kaavakohde kuvaa asuinpientaloille tarkoitetun alueen. Käytetään asemakaavoissa ilmaisemaan, että alueelle voidaan erilaisia pientaloja eli rivitaloja, kytkettyjä pientaloja ja erillisiä pientaloja asumistarkoituksiin. Käytetään yleiskaavoissa ilmaisemaan pientalovaltaista asuntoaluetta. Koodi liittyy lähtökohtaisesti kaavakohteeseen, joka on geometrialtaan alue."
            },
            "codeScheme": {
                "uri": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji",
                "url": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/RY_Kaavamaarayslaji",
            },
            "shortName": "AP",
            "broaderCode": {
                "id": "15934bd8-419b-420b-9b1d-b12608bdf27a",
                "codeValue": "asumisenAlue",
                "uri": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji/code/asumisenAlue",
                "url": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/RY_Kaavamaarayslaji/codes/asumisenAlue",
                "status": "DRAFT",
                "order": 298,
                "hierarchyLevel": 1,
                "created": "2023-04-12T07:41:52.721Z",
                "modified": "2023-12-18T10:16:39.309Z",
                "statusModified": "2023-04-12T07:41:52.721Z",
                "prefLabel": {
                    "en": "Housing area",
                    "fi": "Asumisen alue",
                    "sv": "Område för boende",
                },
                "description": {
                    "fi": "Ilmaisee, että kaavakohde kuvaa asumisen rakennuksille tai asunnoille tarkoitetun alueen. Käytetään asemakaavoissa ilmaisemaan asuinrakennusten alueita, joille voidaan rakentaa eri tyyppisiä asuinrakennuksia. Maakunta- ja yleiskaavoissa käytetään ilmaisemaan asuntoalueita, jolla kerrosalasta pääosa on tarkoitettu asumiseen. Koodi liittyy lähtökohtaisesti kaavakohteeseen, joka on geometrialtaan alue."
                },
                "shortName": "A",
                "membersUrl": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/RY_Kaavamaarayslaji/codes/asumisenAlue/members/",
            },
            "membersUrl": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/RY_Kaavamaarayslaji/codes/asuinpientaloalue/members/",
        },
        {
            "id": "15934bd8-419b-420b-9b1d-b12608bdf27a",
            "codeValue": "asumisenAlue",
            "uri": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji/code/asumisenAlue",
            "url": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/RY_Kaavamaarayslaji/codes/asumisenAlue",
            "status": "DRAFT",
            "order": 298,
            "hierarchyLevel": 1,
            "created": "2023-04-12T07:41:52.721Z",
            "modified": "2023-12-18T10:16:39.309Z",
            "statusModified": "2023-04-12T07:41:52.721Z",
            "prefLabel": {
                "en": "Housing area",
                "fi": "Asumisen alue",
                "sv": "Område för boende",
            },
            "description": {
                "fi": "Ilmaisee, että kaavakohde kuvaa asumisen rakennuksille tai asunnoille tarkoitetun alueen. Käytetään asemakaavoissa ilmaisemaan asuinrakennusten alueita, joille voidaan rakentaa eri tyyppisiä asuinrakennuksia. Maakunta- ja yleiskaavoissa käytetään ilmaisemaan asuntoalueita, jolla kerrosalasta pääosa on tarkoitettu asumiseen. Koodi liittyy lähtökohtaisesti kaavakohteeseen, joka on geometrialtaan alue."
            },
            "codeScheme": {
                "uri": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji",
                "url": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/RY_Kaavamaarayslaji",
            },
            "shortName": "A",
            "membersUrl": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/RY_Kaavamaarayslaji/codes/asumisenAlue/members/",
        },
        {
            "id": "ba9a86d5-6944-4bc4-a86c-87a78c0cdc2a",
            "codeValue": "erillistenAsuinpientalojenAlue",
            "uri": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji/code/erillistenAsuinpientalojenAlue",
            "url": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/RY_Kaavamaarayslaji/codes/erillistenAsuinpientalojenAlue",
            "status": "DRAFT",
            "order": 300,
            "hierarchyLevel": 3,
            "created": "2023-04-12T07:41:52.740Z",
            "modified": "2023-12-18T10:16:39.357Z",
            "statusModified": "2023-04-12T07:41:52.740Z",
            "prefLabel": {
                "en": "Area of detached houses",
                "fi": "Erillisten asuinpientalojen alue",
                "sv": "Område för fristående småhus",
            },
            "description": {
                "fi": "Ilmaisee, että kaavakohde kuvaa erillisille asuinpientaloille tarkoitetun alueen eli alueen, jolle on ja/tai sille voidaan rakentaa yksi- tai kaksiasuntoisia pientaloja (omakotitaloja Rakennusluokituksen 2018 mukainen koodiarvo 0110 tai paritaloja Rakennusluokituksen 2018 mukainen koodiarvo 0111) asumistarkoituksiin. Mikäli halutaan, että kullekin rakennuspaikalle saa rakentaa vain yhden asuinrakennuksen, tulee kaavakohteeseen liittää sanallinen määräys asiasta. Kaavamääräyslaji ei ota kantaa asuntojen omistusmuotoon eli siihen onko kyseessä yhtiömuotoinen erillistalo. Koodi liittyy lähtökohtaisesti kaavakohteeseen, joka on geometrialtaan alue."
            },
            "codeScheme": {
                "uri": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji",
                "url": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/RY_Kaavamaarayslaji",
            },
            "shortName": "AO",
            "broaderCode": {
                "id": "e6f03e18-f292-4068-b6a6-b9e52206accc",
                "codeValue": "asuinpientaloalue",
                "uri": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji/code/asuinpientaloalue",
                "url": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/RY_Kaavamaarayslaji/codes/asuinpientaloalue",
                "status": "DRAFT",
                "order": 299,
                "hierarchyLevel": 2,
                "created": "2023-04-12T07:41:52.734Z",
                "modified": "2023-12-18T10:16:39.342Z",
                "statusModified": "2023-04-12T07:41:52.734Z",
                "prefLabel": {
                    "en": "Area of residential houses",
                    "fi": "Asuinpientaloalue",
                    "sv": "Område för småhus",
                },
                "description": {
                    "fi": "Ilmaisee, että kaavakohde kuvaa asuinpientaloille tarkoitetun alueen. Käytetään asemakaavoissa ilmaisemaan, että alueelle voidaan erilaisia pientaloja eli rivitaloja, kytkettyjä pientaloja ja erillisiä pientaloja asumistarkoituksiin. Käytetään yleiskaavoissa ilmaisemaan pientalovaltaista asuntoaluetta. Koodi liittyy lähtökohtaisesti kaavakohteeseen, joka on geometrialtaan alue."
                },
                "shortName": "AP",
                "membersUrl": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/RY_Kaavamaarayslaji/codes/asuinpientaloalue/members/",
            },
            "membersUrl": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/RY_Kaavamaarayslaji/codes/erillistenAsuinpientalojenAlue/members/",
        },
        {
            "id": "8ced8dae-5a62-410a-ad49-890f623a16bf",
            "codeValue": "rivitalojenJaMuidenKytkettyjenAsuinpientalojenAlue",
            "uri": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji/code/rivitalojenJaMuidenKytkettyjenAsuinpientalojenAlue",
            "url": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/RY_Kaavamaarayslaji/codes/rivitalojenJaMuidenKytkettyjenAsuinpientalojenAlue",
            "status": "DRAFT",
            "order": 301,
            "hierarchyLevel": 3,
            "created": "2023-04-12T07:41:52.747Z",
            "modified": "2023-12-18T10:16:39.371Z",
            "statusModified": "2023-04-12T07:41:52.747Z",
            "prefLabel": {
                "en": "Area of semi-detached and terraced houses",
                "fi": "Rivitalojen ja muiden kytkettyjen asuinpientalojen alue",
                "sv": "Område för radhus och andra kopplade bostadshus",
            },
            "description": {
                "fi": "Ilmaisee, että kaavakohde kuvaa rivitaloille ja muille kytketyille asuinpientaloille tarkoitetun alueen. Kattaa rivitalot (Rakennusluokituksen 2018 mukainen koodiarvo  0112), joita ovat pientalot, joissa on vähintään kolme rinnakkaista asuinhuoneistoa ja joissa eri asuinhuoneistoihin kuuluvia tiloja ei ole päällekkäin. Rivitalot koostuvat kolmesta tai useammasta yhteen rakennetusta asuinhuoneistosta ja muusta asukkaiden käytössä olevasta huonetilasta. Muita kytkettyjä asuinpientaloja ovat esimerkiksi autokatoksin tai varastoin toisiinsa kytketyt asuinpientalot. Koodi liittyy lähtökohtaisesti kaavakohteeseen, joka on geometrialtaan alue."
            },
            "codeScheme": {
                "uri": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji",
                "url": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/RY_Kaavamaarayslaji",
            },
            "shortName": "AR",
            "broaderCode": {
                "id": "e6f03e18-f292-4068-b6a6-b9e52206accc",
                "codeValue": "asuinpientaloalue",
                "uri": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji/code/asuinpientaloalue",
                "url": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/RY_Kaavamaarayslaji/codes/asuinpientaloalue",
                "status": "DRAFT",
                "order": 299,
                "hierarchyLevel": 2,
                "created": "2023-04-12T07:41:52.734Z",
                "modified": "2023-12-18T10:16:39.342Z",
                "statusModified": "2023-04-12T07:41:52.734Z",
                "prefLabel": {
                    "en": "Area of residential houses",
                    "fi": "Asuinpientaloalue",
                    "sv": "Område för småhus",
                },
                "description": {
                    "fi": "Ilmaisee, että kaavakohde kuvaa asuinpientaloille tarkoitetun alueen. Käytetään asemakaavoissa ilmaisemaan, että alueelle voidaan erilaisia pientaloja eli rivitaloja, kytkettyjä pientaloja ja erillisiä pientaloja asumistarkoituksiin. Käytetään yleiskaavoissa ilmaisemaan pientalovaltaista asuntoaluetta. Koodi liittyy lähtökohtaisesti kaavakohteeseen, joka on geometrialtaan alue."
                },
                "shortName": "AP",
                "membersUrl": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/RY_Kaavamaarayslaji/codes/asuinpientaloalue/members/",
            },
            "membersUrl": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/RY_Kaavamaarayslaji/codes/rivitalojenJaMuidenKytkettyjenAsuinpientalojenAlue/members/",
        },
    ],
}

type_of_additional_information_response = {
    "meta": {"code": 200, "from": 0, "resultCount": 2, "totalResults": 2},
    "results": [
        {
            "id": "94ad30a5-9239-4e69-8aac-907e29384ef1",
            "codeValue": "tyyppi",
            "uri": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayksen_Lisatiedonlaji/code/tyyppi",
            "url": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/RY_Kaavamaarayksen_Lisatiedonlaji/codes/tyyppi",
            "status": "DRAFT",
            "order": 1,
            "hierarchyLevel": 1,
            "created": "2023-04-12T08:43:01.971Z",
            "modified": "2023-11-02T09:22:38.165Z",
            "statusModified": "2023-04-12T08:43:01.971Z",
            "prefLabel": {"en": "Type", "fi": "Tyyppi", "sv": "Typ"},
            "description": {
                "fi": "Koodistoa jäsentävä otsikkotason koodi, jota ei käytetä kaavamääräyksissä. Kaavamääräysten tyypit tulisi luokitella kaavoissa tarkemmin niitä kuvaavalla kaavamääräyksen lisätiedon laji-koodiarvolla."
            },
            "codeScheme": {
                "uri": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayksen_Lisatiedonlaji",
                "url": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/RY_Kaavamaarayksen_Lisatiedonlaji",
            },
            "membersUrl": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/RY_Kaavamaarayksen_Lisatiedonlaji/codes/tyyppi/members/",
        },
        {
            "id": "19f05f06-b18f-4d06-917a-2041204266b1",
            "codeValue": "paakayttotarkoitus",
            "uri": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayksen_Lisatiedonlaji/code/paakayttotarkoitus",
            "url": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/RY_Kaavamaarayksen_Lisatiedonlaji/codes/paakayttotarkoitus",
            "status": "DRAFT",
            "order": 2,
            "hierarchyLevel": 2,
            "created": "2023-04-12T08:43:01.978Z",
            "modified": "2023-11-02T09:22:38.182Z",
            "statusModified": "2023-04-12T08:43:01.978Z",
            "prefLabel": {
                "en": "Principal intended use",
                "fi": "Pääkäyttötarkoitus",
                "sv": "Huvudsakligt användningsändamål",
            },
            "description": {
                "fi": "Ilmaisee, että kaavamääräys liittyy kaavakohteeseen, joka muodostaa aluevarauksen. Kaavamääräyksen tyypiksi voidaan määritellä pääkäyttötarkoitus ainoastaan, mikäli kaavamääräys liittyy kaavakohteeseen, joka on geometrialtaan alue. "
            },
            "codeScheme": {
                "uri": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayksen_Lisatiedonlaji",
                "url": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/RY_Kaavamaarayksen_Lisatiedonlaji",
            },
            "broaderCode": {
                "id": "94ad30a5-9239-4e69-8aac-907e29384ef1",
                "codeValue": "tyyppi",
                "uri": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayksen_Lisatiedonlaji/code/tyyppi",
                "url": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/RY_Kaavamaarayksen_Lisatiedonlaji/codes/tyyppi",
                "status": "DRAFT",
                "order": 1,
                "hierarchyLevel": 1,
                "created": "2023-04-12T08:43:01.971Z",
                "modified": "2023-11-02T09:22:38.165Z",
                "statusModified": "2023-04-12T08:43:01.971Z",
                "prefLabel": {"en": "Type", "fi": "Tyyppi", "sv": "Typ"},
                "description": {
                    "fi": "Koodistoa jäsentävä otsikkotason koodi, jota ei käytetä kaavamääräyksissä. Kaavamääräysten tyypit tulisi luokitella kaavoissa tarkemmin niitä kuvaavalla kaavamääräyksen lisätiedon laji-koodiarvolla."
                },
                "membersUrl": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/RY_Kaavamaarayksen_Lisatiedonlaji/codes/tyyppi/members/",
            },
            "membersUrl": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/RY_Kaavamaarayksen_Lisatiedonlaji/codes/paakayttotarkoitus/members/",
        },
    ],
}

name_of_plan_case_decision_response = {
    "meta": {"code": 200, "from": 0, "resultCount": 1, "totalResults": 1},
    "results": [
        {
            "id": "326b10a9-a5b7-4b69-9ee1-5990d8f27474",
            "codeValue": "04",
            "uri": "http://uri.suomi.fi/codelist/rytj/kaavpaatnimi/code/04",
            "url": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/kaavpaatnimi/codes/04",
            "status": "DRAFT",
            "order": 4,
            "hierarchyLevel": 1,
            "created": "2023-03-27T16:16:15.862Z",
            "modified": "2023-11-29T14:26:52.247Z",
            "statusModified": "2023-03-27T16:16:15.862Z",
            "prefLabel": {
                "en": "Presenting the participation and assessment scheme to the public",
                "fi": "Osallistumis- ja arviointisuunnitelman nähtäville asettaminen",
                "sv": "Planen för deltagande och bedömning läggs fram offentligt",
            },
            "description": {
                "en": "Decision to present the plan’s participation and assessment scheme to the public.",
                "fi": "Päätös kaavan osallistumis- ja arviointisuunnitelman nähtäville asettamisesta.",
                "sv": "Beslut om offentligt framläggande av planen för deltagande och bedömning.",
            },
            "codeScheme": {
                "uri": "http://uri.suomi.fi/codelist/rytj/kaavpaatnimi",
                "url": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/kaavpaatnimi",
            },
            "membersUrl": "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes/kaavpaatnimi/codes/04/members/",
        }
    ],
}


def get_url(cls: type[codes.CodeBase]) -> str:
    code_registry, name = cls.code_list_uri.rsplit("/", 2)[-2:None]
    return get_code_list_url("http://mock.url", code_registry, name)


@pytest.fixture
def mock_koodistot(requests_mock) -> None:
    requests_mock.get(
        get_url(codes.LifeCycleStatus), text=json.dumps(lifecycle_status_response)
    )
    requests_mock.get(
        get_url(codes.TypeOfPlanRegulation),
        text=json.dumps(type_of_plan_regulation_response),
    )
    requests_mock.get(get_url(codes.PlanType), text="")
    requests_mock.get(
        get_url(codes.TypeOfAdditionalInformation),
        text=json.dumps(type_of_additional_information_response),
    )
    requests_mock.get(get_url(codes.TypeOfVerbalPlanRegulation), text="")
    requests_mock.get(get_url(codes.TypeOfSourceData), text="")
    requests_mock.get(get_url(codes.TypeOfUnderground), text="")
    requests_mock.get(get_url(codes.TypeOfDocument), text="")
    requests_mock.get(get_url(codes.Municipality), text="")
    requests_mock.get(get_url(codes.AdministrativeRegion), text="")
    requests_mock.get(get_url(codes.PlanTheme), text="")
    requests_mock.get(get_url(codes.CategoryOfPublicity), text="")
    requests_mock.get(get_url(codes.PersonalDataContent), text="")
    requests_mock.get(get_url(codes.RetentionTime), text="")
    requests_mock.get(get_url(codes.Language), text="")
    requests_mock.get(get_url(codes.LegalEffectsOfMasterPlan), text="")
    requests_mock.get(get_url(codes.TypeOfInteractionEvent), text="")
    requests_mock.get(
        get_url(codes.NameOfPlanCaseDecision),
        text=json.dumps(name_of_plan_case_decision_response),
    )
    requests_mock.get(get_url(codes.TypeOfProcessingEvent), text="")
    requests_mock.get(get_url(codes.TypeOfDecisionMaker), text="")


@pytest.fixture
def changed_mock_koodistot(requests_mock, mock_koodistot) -> None:
    # override one response
    requests_mock.get(
        get_url(codes.LifeCycleStatus),
        text=json.dumps(changed_lifecycle_status_response),
    )


@pytest.fixture(scope="module")
def loader(admin_connection_string) -> KoodistotLoader:
    return KoodistotLoader(admin_connection_string, api_url="http://mock.url")


@pytest.fixture
def koodistot_data(mock_koodistot, loader):
    data = loader.get_objects()
    assert len(data) == 21  # this must be changed if new code lists with uri are added
    # data should contain the mock data and be empty for other tables
    print(data[codes.LifeCycleStatus])
    assert len(data[codes.LifeCycleStatus]) == 2
    assert len(data[codes.NameOfPlanCaseDecision]) == 1
    assert len(data[codes.TypeOfPlanRegulation]) == 4
    assert len(data[codes.PlanType]) == 0
    assert len(data[codes.TypeOfAdditionalInformation]) == 2
    # data should also contain the local codes
    assert len(data[codes.TypeOfPlanRegulationGroup]) == 5
    return data


@pytest.fixture
def changed_koodistot_data(changed_mock_koodistot, loader):
    data = loader.get_objects()
    assert len(data) == 21  # this must be changed if new code lists with uri are added
    # data should contain the mock data and be empty for other tables
    print(data[codes.LifeCycleStatus])
    assert len(data[codes.LifeCycleStatus]) == 3
    assert len(data[codes.NameOfPlanCaseDecision]) == 1
    assert len(data[codes.TypeOfPlanRegulation]) == 4
    assert len(data[codes.PlanType]) == 0
    assert len(data[codes.TypeOfAdditionalInformation]) == 2
    # data should also contain the local codes
    assert len(data[codes.TypeOfPlanRegulationGroup]) == 5
    return data


def test_get_vireilletullut(loader, koodistot_data) -> None:
    """Check that remote code is imported"""
    code = loader.get_object(
        codes.LifeCycleStatus, koodistot_data[codes.LifeCycleStatus]["02"]
    )
    assert code["id"]
    assert code["value"] == "02"
    assert "short_name" not in code
    assert code["name"]["fin"] == "Vireilletullut"
    assert (
        code["description"]["fin"]
        == "Kaava on kuulutettu vireille tai vireille tulosta on ilmoitettu kaavoituskatsauksen yhteydessä."
    )
    assert code["status"] == "VALID"
    assert code["level"] == 1
    assert "parent_id" not in code


def test_get_asumisen_alue(loader, koodistot_data) -> None:
    """Check that remote code with children is imported"""
    code = loader.get_object(
        codes.TypeOfPlanRegulation,
        koodistot_data[codes.TypeOfPlanRegulation]["asumisenAlue"],
    )
    assert code["id"] == "15934bd8-419b-420b-9b1d-b12608bdf27a"
    assert code["value"] == "asumisenAlue"
    assert code["short_name"] == "A"
    assert code["name"]["fin"] == "Asumisen alue"
    assert (
        code["description"]["fin"]
        == "Ilmaisee, että kaavakohde kuvaa asumisen rakennuksille tai asunnoille tarkoitetun alueen. Käytetään asemakaavoissa ilmaisemaan asuinrakennusten alueita, joille voidaan rakentaa eri tyyppisiä asuinrakennuksia. Maakunta- ja yleiskaavoissa käytetään ilmaisemaan asuntoalueita, jolla kerrosalasta pääosa on tarkoitettu asumiseen. Koodi liittyy lähtökohtaisesti kaavakohteeseen, joka on geometrialtaan alue."
    )
    assert code["status"] == "DRAFT"
    assert code["level"] == 1
    assert "parent_id" not in code


def test_get_asuinpientaloalue(loader, koodistot_data) -> None:
    """Check that remote code with parent and children is imported"""
    code = loader.get_object(
        codes.TypeOfPlanRegulation,
        koodistot_data[codes.TypeOfPlanRegulation]["asuinpientaloalue"],
    )
    assert code["id"] == "e6f03e18-f292-4068-b6a6-b9e52206accc"
    assert code["value"] == "asuinpientaloalue"
    assert code["short_name"] == "AP"
    assert code["name"]["fin"] == "Asuinpientaloalue"
    assert (
        code["description"]["fin"]
        == "Ilmaisee, että kaavakohde kuvaa asuinpientaloille tarkoitetun alueen. Käytetään asemakaavoissa ilmaisemaan, että alueelle voidaan erilaisia pientaloja eli rivitaloja, kytkettyjä pientaloja ja erillisiä pientaloja asumistarkoituksiin. Käytetään yleiskaavoissa ilmaisemaan pientalovaltaista asuntoaluetta. Koodi liittyy lähtökohtaisesti kaavakohteeseen, joka on geometrialtaan alue."
    )
    assert code["status"] == "DRAFT"
    assert code["level"] == 2
    assert code["parent_id"] == "15934bd8-419b-420b-9b1d-b12608bdf27a"


def test_get_erillisten_asuinpientalojen_alue(loader, koodistot_data) -> None:
    """Check that remote code with parent is imported"""
    code = loader.get_object(
        codes.TypeOfPlanRegulation,
        koodistot_data[codes.TypeOfPlanRegulation]["erillistenAsuinpientalojenAlue"],
    )
    assert code["id"] == "ba9a86d5-6944-4bc4-a86c-87a78c0cdc2a"
    assert code["value"] == "erillistenAsuinpientalojenAlue"
    assert code["short_name"] == "AO"
    assert code["name"]["fin"] == "Erillisten asuinpientalojen alue"
    assert (
        code["description"]["fin"]
        == "Ilmaisee, että kaavakohde kuvaa erillisille asuinpientaloille tarkoitetun alueen eli alueen, jolle on ja/tai sille voidaan rakentaa yksi- tai kaksiasuntoisia pientaloja (omakotitaloja Rakennusluokituksen 2018 mukainen koodiarvo 0110 tai paritaloja Rakennusluokituksen 2018 mukainen koodiarvo 0111) asumistarkoituksiin. Mikäli halutaan, että kullekin rakennuspaikalle saa rakentaa vain yhden asuinrakennuksen, tulee kaavakohteeseen liittää sanallinen määräys asiasta. Kaavamääräyslaji ei ota kantaa asuntojen omistusmuotoon eli siihen onko kyseessä yhtiömuotoinen erillistalo. Koodi liittyy lähtökohtaisesti kaavakohteeseen, joka on geometrialtaan alue."
    )
    assert code["status"] == "DRAFT"
    assert code["level"] == 3
    assert code["parent_id"] == "e6f03e18-f292-4068-b6a6-b9e52206accc"


def test_get_yleismaaraysryhma(loader, koodistot_data) -> None:
    """Check that local code is imported"""
    code = loader.get_object(
        codes.TypeOfPlanRegulation,
        koodistot_data[codes.TypeOfPlanRegulationGroup][
            codes.TypeOfPlanRegulationGroup.local_codes[0]["value"]
        ],
    )
    assert code["value"] == codes.TypeOfPlanRegulationGroup.local_codes[0]["value"]
    assert "short_name" not in code
    assert (
        code["name"]["fin"]
        == codes.TypeOfPlanRegulationGroup.local_codes[0]["name"]["fin"]
    )
    assert "description" not in code
    assert code["status"] == "LOCAL"
    assert "level" not in code
    assert "parent_id" not in code


@pytest.fixture(scope="module")
def custom_code_loader(admin_connection_string) -> Iterator[KoodistotLoader]:
    """Use monkey patched local codes for testing local custom codes with
    remote children. At the moment, no local custom codes with remote
    children are used in production.
    """
    codes.TypeOfAdditionalInformation.local_codes = [
        {
            "value": "kayttotarkoitus",
            "name": {"fin": "Käyttötarkoitus"},
            "child_values": [
                "paakayttotarkoitus",
                "osaAlue",
                "poisluettavaKayttotarkoitus",
                "yhteystarve",
            ],
        },
        {
            "value": "olemassaolo",
            "name": {"fin": "Olemassaolo"},
            "child_values": [
                "olemassaOleva",
                "sailytettava",
                "uusi",
                "olennaisestiMuuttuva",
            ],
        },
        {
            "value": "kehittaminen",
            "name": {"fin": "Kehittäminen"},
            "child_values": [
                "reservialue",
                "kehitettava",
                "merkittavastiParannettava",
                "eheytettavaTaiTiivistettava",
            ],
        },
    ]
    yield KoodistotLoader(admin_connection_string, api_url="http://mock.url")
    # we have to remove local codes after the test so that they aren't found
    # in other tests that import the codes module
    codes.TypeOfAdditionalInformation.local_codes = []


@pytest.fixture
def custom_koodistot_data(mock_koodistot, custom_code_loader):
    data = custom_code_loader.get_objects()
    assert len(data) == 21  # this must be changed if new code lists with uri are added
    # data should contain the mock data and be empty for other tables
    print(data[codes.LifeCycleStatus])
    assert len(data[codes.LifeCycleStatus]) == 2
    assert len(data[codes.NameOfPlanCaseDecision]) == 1
    assert len(data[codes.TypeOfPlanRegulation]) == 4
    assert len(data[codes.PlanType]) == 0
    # data should also contain the local codes
    assert len(data[codes.TypeOfPlanRegulationGroup]) == 5
    # patched class should have both local and remote codes
    assert len(data[codes.TypeOfAdditionalInformation]) == 5
    return data


@pytest.fixture
def changed_custom_koodistot_data(changed_mock_koodistot, custom_code_loader):
    data = custom_code_loader.get_objects()
    assert len(data) == 21  # this must be changed if new code lists with uri are added
    # data should contain the mock data and be empty for other tables
    print(data[codes.LifeCycleStatus])
    assert len(data[codes.LifeCycleStatus]) == 3
    assert len(data[codes.NameOfPlanCaseDecision]) == 1
    assert len(data[codes.TypeOfPlanRegulation]) == 4
    assert len(data[codes.PlanType]) == 0
    # data should also contain the local codes
    assert len(data[codes.TypeOfPlanRegulationGroup]) == 5
    # patched class should have both local and remote codes
    assert len(data[codes.TypeOfAdditionalInformation]) == 5
    return data


def test_get_custom_kayttotarkoitus(custom_code_loader, custom_koodistot_data) -> None:
    """Check that custom local code with remote children is imported"""
    code = custom_code_loader.get_object(
        codes.TypeOfAdditionalInformation,
        custom_koodistot_data[codes.TypeOfAdditionalInformation][
            codes.TypeOfAdditionalInformation.local_codes[0]["value"]
        ],
    )
    assert code["value"] == codes.TypeOfAdditionalInformation.local_codes[0]["value"]
    assert "short_name" not in code
    assert (
        code["name"]["fin"]
        == codes.TypeOfAdditionalInformation.local_codes[0]["name"]["fin"]
    )
    assert "description" not in code
    assert code["status"] == "LOCAL"
    assert "level" not in code
    assert "parent_id" not in code


def test_get_custom_paakayttotarkoitus(
    custom_code_loader, custom_koodistot_data
) -> None:
    """Check that remote code with custom local parent is imported"""
    code = custom_code_loader.get_object(
        codes.TypeOfAdditionalInformation,
        custom_koodistot_data[codes.TypeOfAdditionalInformation]["paakayttotarkoitus"],
    )
    assert code["id"] == "19f05f06-b18f-4d06-917a-2041204266b1"
    assert code["value"] == "paakayttotarkoitus"
    assert "short_name" not in code
    assert code["name"]["fin"] == "Pääkäyttötarkoitus"
    assert (
        code["description"]["fin"]
        == "Ilmaisee, että kaavamääräys liittyy kaavakohteeseen, joka muodostaa aluevarauksen. Kaavamääräyksen tyypiksi voidaan määritellä pääkäyttötarkoitus ainoastaan, mikäli kaavamääräys liittyy kaavakohteeseen, joka on geometrialtaan alue. "
    )
    assert code["status"] == "DRAFT"
    assert code["level"] == 2
    # Code parent is still remote at this stage. We will have to check that parents are reassigned
    # correctly after the loader has finished saving objects.
    assert "parent_id" in code


def check_code_parents(cur) -> None:
    """Check that remote codes are correctly assigned to remote or local parents as desired."""
    # remote code with remote parent
    cur.execute(
        "SELECT parent_id FROM codes.type_of_plan_regulation WHERE value='asuinpientaloalue'"
    )
    asuinpientaloalue_parent_id = cur.fetchone()[0]
    cur.execute(
        "SELECT id FROM codes.type_of_plan_regulation WHERE value='asumisenAlue'"
    )
    asumisenalue_id = cur.fetchone()[0]
    assert asuinpientaloalue_parent_id == asumisenalue_id
    # remote code with local parent
    cur.execute(
        "SELECT parent_id FROM codes.type_of_additional_information WHERE value='paakayttotarkoitus'"
    )
    paakayttotarkoitus_parent_id = cur.fetchone()[0]
    cur.execute(
        "SELECT id FROM codes.type_of_additional_information WHERE value='kayttotarkoitus'"
    )
    kayttotarkoitus_id = cur.fetchone()[0]
    assert paakayttotarkoitus_parent_id == kayttotarkoitus_id


def assert_data_is_imported(main_db_params) -> None:
    conn = psycopg.connect(**main_db_params)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM codes.lifecycle_status")
            assert cur.fetchone()[0] == 2
            cur.execute("SELECT count(*) FROM codes.name_of_plan_case_decision")
            assert cur.fetchone()[0] == 1
            # Relationship between decision and status should also be created
            cur.execute("SELECT count(*) FROM codes.allowed_events")
            assert cur.fetchone()[0] == 1
            cur.execute("SELECT count(*) FROM codes.type_of_plan_regulation")
            assert cur.fetchone()[0] == 4
            cur.execute("SELECT count(*) FROM codes.plan_type")
            assert cur.fetchone()[0] == 0
            cur.execute("SELECT count(*) FROM codes.type_of_plan_regulation_group")
            assert cur.fetchone()[0] == 5
            cur.execute("SELECT count(*) FROM codes.type_of_additional_information")
            assert cur.fetchone()[0] == 5
            check_code_parents(cur)
    finally:
        conn.close()


def assert_changed_data_is_imported(main_db_params) -> None:
    conn = psycopg.connect(**main_db_params)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM codes.lifecycle_status")
            assert cur.fetchone()[0] == 3
            cur.execute("SELECT count(*) FROM codes.name_of_plan_case_decision")
            assert cur.fetchone()[0] == 1
            # Relationship between decision and status should also be created
            cur.execute("SELECT count(*) FROM codes.allowed_events")
            assert cur.fetchone()[0] == 1
            cur.execute("SELECT count(*) FROM codes.type_of_plan_regulation")
            assert cur.fetchone()[0] == 4
            cur.execute("SELECT count(*) FROM codes.plan_type")
            assert cur.fetchone()[0] == 0
            cur.execute("SELECT count(*) FROM codes.type_of_plan_regulation_group")
            assert cur.fetchone()[0] == 5
            cur.execute("SELECT count(*) FROM codes.type_of_additional_information")
            assert cur.fetchone()[0] == 5
            check_code_parents(cur)
    finally:
        conn.close()


def test_save_objects(
    custom_code_loader, custom_koodistot_data, main_db_params
) -> None:
    custom_code_loader.save_objects(custom_koodistot_data)
    assert_data_is_imported(main_db_params)


def test_save_changed_objects(
    changed_custom_koodistot_data, admin_connection_string, main_db_params
) -> None:
    # The database is already populated in the first test. Because
    # connection string (and therefore hame_database_created)
    # has module scope, the database persists between tests.
    assert_data_is_imported(main_db_params)
    # check that a new loader adds one object to the database
    loader = KoodistotLoader(admin_connection_string, api_url="http://mock.url")
    loader.save_objects(changed_custom_koodistot_data)
    assert_changed_data_is_imported(main_db_params)
