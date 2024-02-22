from models import CodeBase, Plan, PlanProposition, PlanRegulation
from sqlalchemy.orm import Mapped, declared_attr, relationship


class LifeCycleStatus(CodeBase):
    """
    Elinkaaren vaihe
    """

    __tablename__ = "lifecycle_status"
    code_list_uri = "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari"

    @classmethod
    @declared_attr
    def plans(cls) -> Mapped[Plan]:
        return relationship(Plan, back_populates="lifecycle_status")

    @classmethod
    @declared_attr
    def plan_regulations(cls) -> Mapped[PlanRegulation]:
        return relationship(PlanRegulation, back_populates="lifecycle_status")

    @classmethod
    @declared_attr
    def plan_propositions(cls) -> Mapped[PlanProposition]:
        return relationship(PlanProposition, back_populates="lifecycle_status")


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

    plan_regulations = relationship(
        "PlanRegulation", back_populates="type_of_plan_regulation"
    )


class TypeOfAdditionalInformationForPlanRegulation(CodeBase):
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


class TypeOfVerbalPlanRegulation(CodeBase):
    """
    Sanallisen määräyksen laji

    Epäselvää milloin tätä käytetään.
    """

    __tablename__ = "type_of_verbal_plan_regulation"
    code_list_uri = (
        "http://uri.suomi.fi/codelist/rytj/RY_Sanallisen_Kaavamaarayksen_Laji"
    )

    plan_regulations = relationship(
        "PlanRegulation", back_populates="type_of_verbal_plan_regulation"
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
    # Asiakirjatyyppi is apparently our own code list. It does not exist in RYTJ.
    code_list_uri = ""
