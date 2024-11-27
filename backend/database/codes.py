from typing import Type

from geoalchemy2 import Geometry
from models import CodeBase
from sqlalchemy import Column
from sqlalchemy.orm import Session, relationship


class LifeCycleStatus(CodeBase):
    """
    Elinkaaren vaihe
    """

    __tablename__ = "lifecycle_status"
    code_list_uri = "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari"

    lifecycle_dates = relationship(
        "LifeCycleDate", back_populates="lifecycle_status", cascade="delete"
    )


class PlanType(CodeBase):
    """
    Kaavalaji
    """

    __tablename__ = "plan_type"
    code_list_uri = "http://uri.suomi.fi/codelist/rytj/RY_Kaavalaji"


class TypeOfPlanRegulation(CodeBase):
    """
    Kaavamääräyslaji
    """

    __tablename__ = "type_of_plan_regulation"
    code_list_uri = "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji"


class TypeOfAdditionalInformation(CodeBase):
    """
    Kaavamääräyksen lisätiedon laji

    HAME-Ryhti-tietomallissa tämän koodiston arvot jaetaan useaan monivalintakenttään,
    joista jokaisesta käyttäjä voi valita yhden koodin.

    Toteutetaan kentät niin, että jokaisessa on filtteri, joka tarkistaa sopivan
    koodistoarvon. Tietokantaan voi tallentaa vain arvon jolla on oikea parent. Ainakin
    osissa kentistä tämä toimii sellaisenaan, koska arvot on RYTJ:ssä ryhmitelty oikein.
    """

    # Let's use a shortish table name, since the long name creates indexes that have
    # names that are too long for PostgreSQL, hooray :D
    __tablename__ = "type_of_additional_information"
    code_list_uri = (
        "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayksen_Lisatiedonlaji"
    )
    local_codes = [
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


class TypeOfVerbalPlanRegulation(CodeBase):
    """
    Sanallisen määräyksen laji

    Epäselvää milloin tätä käytetään.
    """

    __tablename__ = "type_of_verbal_plan_regulation"
    code_list_uri = (
        "http://uri.suomi.fi/codelist/rytj/RY_Sanallisen_Kaavamaarayksen_Laji"
    )


class TypeOfSourceData(CodeBase):
    """
    Lähtöaineiston laji
    """

    __tablename__ = "type_of_source_data"
    code_list_uri = "http://uri.suomi.fi/codelist/rytj/RY_LahtotietoaineistonLaji"


class TypeOfUnderground(CodeBase):
    """
    Maanalaisuuden laji
    """

    __tablename__ = "type_of_underground"
    code_list_uri = "http://uri.suomi.fi/codelist/rytj/RY_MaanalaisuudenLaji"


class TypeOfDocument(CodeBase):
    """
    Asiakirjatyyppi
    """

    __tablename__ = "type_of_document"
    code_list_uri = "http://uri.suomi.fi/codelist/rytj/RY_AsiakirjanLaji_YKAK"


class AdministrativeRegion(CodeBase):
    """
    Maakunta
    """

    __tablename__ = "administrative_region"
    code_list_uri = "http://uri.suomi.fi/codelist/jhs/maakunta_1_20240101"
    geom = Column(Geometry(geometry_type="MULTIPOLYGON", srid=3067), nullable=True)


class TypeOfPlanRegulationGroup(CodeBase):
    """
    Kaavamääräysryhmän tyyppi

    This is our own code list. It does not exist in koodistot.suomi.fi.
    """

    __tablename__ = "type_of_plan_regulation_group"
    code_list_uri = ""
    local_codes = [
        {"value": "generalRegulations", "name": {"fin": "Yleismääräykset"}},
        {"value": "landUseRegulations", "name": {"fin": "Aluevaraus"}},
        {"value": "otherAreaRegulations", "name": {"fin": "Osa-alue"}},
        {"value": "lineRegulations", "name": {"fin": "Viiva"}},
        {"value": "otherPointRegulations", "name": {"fin": "Muu piste"}},
    ]


class PlanTheme(CodeBase):
    """
    Kaavoitusteema
    """

    __tablename__ = "plan_theme"
    code_list_uri = "http://uri.suomi.fi/codelist/rytj/kaavoitusteema"


class CategoryOfPublicity(CodeBase):
    """
    Asiakirjan julkisuusluokka
    """

    __tablename__ = "category_of_publicity"
    code_list_uri = "http://uri.suomi.fi/codelist/rytj/julkisuus"


class TypeOfInteractionEvent(CodeBase):
    """
    Vuorovaikutustapahtuman laji (kaava)
    """

    __tablename__ = "type_of_interaction_event"
    code_list_uri = (
        "http://uri.suomi.fi/codelist/rytj/RY_KaavanVuorovaikutustapahtumanLaji"
    )


class NameOfPlanCaseDecision(CodeBase):
    """
    Kaava-asian päätöksen nimi
    """

    __tablename__ = "name_of_plan_case_decision"
    code_list_uri = "http://uri.suomi.fi/codelist/rytj/kaavpaatnimi"


class TypeOfProcessingEvent(CodeBase):
    """
    Käsittelytapahtuman laji
    """

    __tablename__ = "type_of_processing_event"
    code_list_uri = "http://uri.suomi.fi/codelist/rytj/kaavakastap"


class TypeOfDecisionMaker(CodeBase):
    """
    Päätöksentekijän laji
    """

    __tablename__ = "type_of_decision_maker"
    code_list_uri = "http://uri.suomi.fi/codelist/rytj/PaatoksenTekija"


def get_code(session: Session, code_class: Type[CodeBase], value: str) -> CodeBase:
    """
    Get code object by value.
    """
    return session.query(code_class).filter_by(value=value).first()


def get_code_uri(code_class: Type[CodeBase], value: str) -> str:
    """
    Get code URI by value, without querying the database.
    """
    return code_class(value=value).uri


decisions_by_status = {
    # Some lifecycle statuses require decisions, some don't.
    # Plan decision code depends on lifecycle status:
    # https://ryhti.syke.fi/wp-content/uploads/sites/2/2023/11/Kaavatiedon-validointisaannot-ja-paluuarvot.pdf
    "02": [
        "01",
        "02",
        "03",
    ],  # lifecycle/req-codelist-plandecision-name-codevalue-pending
    "03": [
        "04",
        "05",
        "06",
    ],  # lifecycle/req-codelist-plandecision-name-codevalue-preparation
    "04": ["07", "08"],  # lifecycle/req-codelist-plandecision-name-codevalue-proposal
    "05": ["07", "09"],  # lifecycle/req-codelist-regionalplan-decisionname-lifecycle-05
    "06": [
        "11A"
    ],  # lifecycle/req-codelist-plandecision-name-alternative-codevalues-approved-spatialplan  # noqa
    "08": [
        "12",
        "13",
        "15",
    ],  # lifecycle/req-planmatterdecision-name-subject-appeal-lifecycle
}

processing_events_by_status = {
    # Some lifecycle statuses require processing events, some don't.
    # Processing event code depends on lifecycle status:
    # https://ryhti.syke.fi/wp-content/uploads/sites/2/2023/11/Kaavatiedon-validointisaannot-ja-paluuarvot.pdf
    "02": ["04"],  # lifecycle/req-codelist-handlingeventtype-codevalue-lifecycle
    "03": ["05", "06"],  # lifecycle/req-codelist-handlingeventtype-codevalue-lifecycle
    "04": ["07", "08"],  # lifecycle/req-codelist-plandecision-name-codevalue-proposal
    "05": [
        "08",
        "09",
    ],  # lifecycle/req-codelist-regionalplan-handlingeventtype-lifecycle-05
    "06": [
        "11"
    ],  # lifecycle/req-codelist-regionalplan-handlingevent-approved-spatialplan
    "11": ["13"],  # not allowed in regional plan!
    "13": ["16"],  # lifecycle/req-codelist-handlingeventtype-codevalue-lifecycle
}


interaction_events_by_status = {
    # Some lifecycle statuses require interaction events, some don't
    # Interaction event code depends on lifecycle status:
    # https://ryhti.syke.fi/wp-content/uploads/sites/2/2023/11/Kaavatiedon-validointisaannot-ja-paluuarvot.pdf
    "03": ["01"],  # lifecycle/req-codelist-interactionevent-codevalue-lifecycle
    "04": [
        "01"
    ],  # lifecycle/req-codelist-regionalplan-interactionevent-display-proposal
    "05": [
        "01",
        "02",
    ],  # lifecycle/req-codelist-regionalplan-iteractioneventtype-lifecycle-05
}


decisionmaker_by_status = {
    # TODO: Decisionmaker may depend on lifecycle status.
    str(i).zfill(2): "01"
    for i in range(1, 16)
}
