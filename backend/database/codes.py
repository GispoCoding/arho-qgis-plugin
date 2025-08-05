import uuid
from typing import Dict, List, Optional, Type

from geoalchemy2 import Geometry
from sqlalchemy import Column, ForeignKey, Table, Uuid
from sqlalchemy.orm import Mapped, Session, declared_attr, mapped_column, relationship
from sqlalchemy.sql import func

from database.base import Base, VersionedBase, language_str, unique_str

allowed_events = Table(
    "allowed_events",
    Base.metadata,
    Column("id", Uuid, primary_key=True, server_default=func.gen_random_uuid()),
    Column(
        "lifecycle_status_id",
        ForeignKey(
            "codes.lifecycle_status.id",
            name="lifecycle_status_id_fkey",
            ondelete="CASCADE",
        ),
        index=True,
    ),
    Column(
        "name_of_plan_case_decision_id",
        ForeignKey(
            "codes.name_of_plan_case_decision.id",
            name="name_of_plan_case_decision_id_fkey",
            ondelete="CASCADE",
        ),
        index=True,
    ),
    Column(
        "type_of_processing_event_id",
        ForeignKey(
            "codes.type_of_processing_event.id",
            name="type_of_processing_event_id_fkey",
            ondelete="CASCADE",
        ),
        index=True,
    ),
    Column(
        "type_of_interaction_event_id",
        ForeignKey(
            "codes.type_of_interaction_event.id",
            name="type_of_interaction_event_id_fkey",
            ondelete="CASCADE",
        ),
        index=True,
    ),
    schema="codes",
)


class CodeBase(VersionedBase):
    """
    Code tables in Ryhti should refer to national Ryhti code table URIs. They may
    have hierarchical structure.
    """

    __abstract__ = True
    __table_args__ = {"schema": "codes"}
    code_list_uri = ""  # the URI to use for looking for codes online
    local_codes: List[Dict] = []  # local codes to add to the code list

    value: Mapped[unique_str]
    short_name: Mapped[str] = mapped_column(server_default="", index=True)
    name: Mapped[Optional[language_str]]
    description: Mapped[Optional[language_str]]
    # Let's import code status too. This tells our importer if the koodisto is final,
    # or if the code can be deleted and/or moved.
    status: Mapped[str]
    # For now, level can just be imported from RYTJ. Let's assume the level in RYTJ
    # is correct, so we don't have to calculate and recalculate it ourselves.
    level: Mapped[int] = mapped_column(server_default="1", index=True)

    # self-reference in abstract base class:
    # We cannot use @classmethod decorator here. Alembic is buggy and apparently
    # does not recognize declared attributes that are correctly marked as class methods.
    @declared_attr
    def parent_id(cls) -> Mapped[Optional[uuid.UUID]]:  # noqa
        return mapped_column(
            ForeignKey(cls.id, name=f"{cls.__tablename__}_parent_id_fkey"), index=True
        )

    # Oh great. Unlike SQLAlchemy documentation states, @classmethod decorator should
    # absolutely *not* be used. Declared relationships are not correctly set if the
    # decorator is present.
    @declared_attr
    def parent(cls) -> Mapped[Optional[VersionedBase]]:  # noqa
        return relationship(cls, remote_side=[cls.id], backref="children")

    @property
    def uri(self):
        return f"{self.code_list_uri}/code/{self.value}"


class LifeCycleStatus(CodeBase):
    """
    Elinkaaren vaihe
    """

    __tablename__ = "lifecycle_status"
    code_list_uri = "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari"

    lifecycle_dates = relationship(
        "LifeCycleDate",
        back_populates="lifecycle_status",
    )
    allowed_interaction_events: Mapped[List["TypeOfInteractionEvent"]] = relationship(
        secondary="codes.allowed_events", back_populates="allowed_statuses"
    )
    allowed_decisions: Mapped[List["NameOfPlanCaseDecision"]] = relationship(
        secondary="codes.allowed_events",
        back_populates="allowed_statuses",
        overlaps="allowed_interaction_events",
    )
    allowed_processing_events: Mapped[List["TypeOfProcessingEvent"]] = relationship(
        secondary="codes.allowed_events",
        back_populates="allowed_statuses",
        overlaps="allowed_decisions,allowed_interaction_events",
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


class Municipality(CodeBase):
    """
    Kunta
    """

    __tablename__ = "municipality"
    code_list_uri = "http://uri.suomi.fi/codelist/jhs/kunta_1_20240101"
    geom = Column(Geometry(geometry_type="MULTIPOLYGON", srid=3067), nullable=True)


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


class PersonalDataContent(CodeBase):
    """
    Asiakirjan henkilötietosisältö
    """

    __tablename__ = "personal_data_content"
    code_list_uri = "http://uri.suomi.fi/codelist/rytj/henkilotietosisalto"


class RetentionTime(CodeBase):
    """
    Asiakirjan säilytysaika
    """

    __tablename__ = "retention_time"
    code_list_uri = "http://uri.suomi.fi/codelist/rytj/sailytysaika"


class Language(CodeBase):
    """
    Rakennetun ympäristön tietojärjestelmän tukemat kielet
    """

    __tablename__ = "language"
    code_list_uri = "http://uri.suomi.fi/codelist/rytj/ryhtikielet"


class LegalEffectsOfMasterPlan(CodeBase):
    """
    Yleiskaavan oikeusvaikutukset
    """

    __tablename__ = "legal_effects_of_master_plan"
    code_list_uri = "http://uri.suomi.fi/codelist/rytj/oikeusvaik_YK"


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
    "04": [
        "08"
    ],  # lifecycle__req_codelist_plandecision_name_codevalue_changed_proposal_reversed  # noqa
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


class TypeOfInteractionEvent(CodeBase):
    """
    Vuorovaikutustapahtuman laji (kaava)
    """

    __tablename__ = "type_of_interaction_event"
    code_list_uri = (
        "http://uri.suomi.fi/codelist/rytj/RY_KaavanVuorovaikutustapahtumanLaji"
    )
    allowed_status_dict = interaction_events_by_status
    allowed_statuses: Mapped[List["LifeCycleStatus"]] = relationship(
        secondary="codes.allowed_events",
        back_populates="allowed_interaction_events",
        overlaps="allowed_decisions,allowed_processing_events",
    )


class NameOfPlanCaseDecision(CodeBase):
    """
    Kaava-asian päätöksen nimi
    """

    __tablename__ = "name_of_plan_case_decision"
    code_list_uri = "http://uri.suomi.fi/codelist/rytj/kaavpaatnimi"
    allowed_status_dict = decisions_by_status
    allowed_statuses: Mapped[List["LifeCycleStatus"]] = relationship(
        secondary="codes.allowed_events",
        back_populates="allowed_decisions",
        overlaps="allowed_interaction_events,allowed_processing_events,allowed_statuses",  # noqa
    )


class TypeOfProcessingEvent(CodeBase):
    """
    Käsittelytapahtuman laji
    """

    __tablename__ = "type_of_processing_event"
    code_list_uri = "http://uri.suomi.fi/codelist/rytj/kaavakastap"
    allowed_status_dict = processing_events_by_status
    allowed_statuses: Mapped[List["LifeCycleStatus"]] = relationship(
        secondary="codes.allowed_events",
        back_populates="allowed_processing_events",
        overlaps="allowed_interaction_events,allowed_decisions,allowed_statuses",
    )


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


decisionmaker_by_status = {
    # TODO: Decisionmaker may depend on lifecycle status.
    str(i).zfill(2): "01"
    for i in range(1, 16)
}
