from __future__ import annotations

import enum
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, fields
from typing import TYPE_CHECKING, cast

from arho_feature_template.project.layers.code_layers import (
    AdditionalInformationTypeLayer,
    PlanRegulationTypeLayer,
    UndergroundTypeLayer,
    VerbalRegulationType,
)
from arho_feature_template.utils.misc_utils import null_to_none

if TYPE_CHECKING:
    from datetime import datetime

    from qgis.core import QgsGeometry
    from qgis.PyQt.QtCore import QDate


logger = logging.getLogger(__name__)


class AttributeValueDataType(str, enum.Enum):
    LOCALIZED_TEXT = "LocalizedText"
    TEXT = "Text"
    NUMERIC = "Numeric"
    NUMERIC_RANGE = "NumericRange"
    POSITIVE_NUMERIC = "PositiveNumeric"
    POSITIVE_NUMERIC_RANGE = "PositiveNumericRange"
    DECIMAL = "Decimal"
    DECIMAL_RANGE = "DecimalRange"
    POSITIVE_DECIMAL = "PositiveDecimal"
    POSITIVE_DECIMAL_RANGE = "PositiveDecimalRange"
    CODE = "Code"
    IDENTIFIER = "Identifier"
    SPOT_ELEVATION = "SpotElevation"
    TIME_PERIOD = "TimePeriod"
    TIME_PERIOD_DATE_ONLY = "TimePeriodDateOnly"


class TemplateSyntaxError(Exception):
    def __init__(self, template_cls: str, message: str):
        super().__init__(f"Invalid template syntax for {template_cls}: {message}")


@dataclass
class Library(ABC):
    """Describes a (template) library."""

    class LibraryType(str, enum.Enum):
        DEFAULT = "default"
        CUSTOM = "custom"
        ACTIVE_PLAN = "active_plan"

    name: str = ""
    file_path: str | None = None
    version: int | None = None
    description: str | None = None
    status: bool = True
    library_type: Library.LibraryType = LibraryType.CUSTOM

    @classmethod
    @abstractmethod
    def from_template_dict(cls, data: dict, library_type: Library.LibraryType, file_path: str | None = None) -> Library:
        pass

    @abstractmethod
    def into_template_dict(self) -> dict:
        pass


@dataclass
class PlanFeatureLibrary(Library):
    """A collection of plan features."""

    plan_features: list[PlanFeature] = field(default_factory=list, compare=False)

    @classmethod
    def from_template_dict(
        cls, data: dict, library_type: Library.LibraryType, file_path: str | None = None
    ) -> PlanFeatureLibrary:
        if data == {}:
            return PlanFeatureLibrary(file_path=file_path, status=False)

        try:
            return PlanFeatureLibrary(
                name=data.get("name", ""),
                file_path=file_path,
                version=data.get("version"),
                description=data.get("description"),
                status=True,
                library_type=library_type,  # NOTE: All PlanFeatureLibraries are CUSTOM now
                plan_features=[
                    PlanFeature.from_template_dict(plan_feature_data) for plan_feature_data in data["plan_features"]
                ]
                if data.get("plan_features")
                else [],
            )
        except KeyError as e:
            raise TemplateSyntaxError(str(cls), str(e)) from e

    def into_template_dict(self) -> dict:
        return {
            "name": self.name,
            "file_path": self.file_path,
            "version": self.version,
            "description": self.description,
            "plan_features": [plan_feature.into_template_dict() for plan_feature in self.plan_features],
        }


@dataclass
class RegulationGroupLibrary(Library):
    """A collection of plan regulation groups."""

    regulation_groups: list[RegulationGroup] = field(default_factory=list, compare=False)

    @classmethod
    def from_template_dict(
        cls, data: dict, library_type: Library.LibraryType, file_path: str | None = None
    ) -> RegulationGroupLibrary:
        """Returns whether initialization from data was succesfull and the created RegulationGroupLibrary."""
        if data == {}:
            return RegulationGroupLibrary(library_type=library_type, file_path=file_path, status=False)
        try:
            return RegulationGroupLibrary(
                name=data.get("name", ""),
                file_path=file_path,
                version=data.get("version"),
                description=data.get("description"),
                library_type=library_type,
                status=True,
                regulation_groups=[
                    RegulationGroup.from_template_dict(group_data) for group_data in data["plan_regulation_groups"]
                ]
                if data.get("plan_regulation_groups")
                else [],
            )
        except KeyError as e:
            raise TemplateSyntaxError(str(cls), str(e)) from e

    def into_template_dict(self) -> dict:
        return {
            "name": self.name,
            "file_path": self.file_path,
            "version": self.version,
            "description": self.description,
            "plan_regulation_groups": [group.into_template_dict() for group in self.regulation_groups],
        }

    def get_letter_codes(self) -> set[str]:
        """Returns set of non-empty short names (letter codes) of regulation groups part of the library."""
        return {group.letter_code for group in self.regulation_groups if group.letter_code}


class PlanBaseModel:
    def __post_init__(self):
        # Set all found NULLs to None
        for _field in fields(self):
            value = getattr(self, _field.name)
            setattr(self, _field.name, null_to_none(value))


@dataclass
class AttributeValue(PlanBaseModel):
    value_data_type: AttributeValueDataType | None = None

    numeric_value: int | float | None = None
    numeric_range_min: int | float | None = None
    numeric_range_max: int | float | None = None

    unit: str | None = None

    text_value: str | None = None
    text_syntax: str | None = None

    code_list: str | None = None
    code_value: str | None = None
    code_title: str | None = None

    height_reference_point: str | None = None

    @staticmethod
    def from_template_dict(data: dict, default_value: AttributeValue | None = None) -> AttributeValue:
        if "value_data_type" in data:
            value_data_type = AttributeValueDataType(data["value_data_type"])
        elif default_value and default_value.value_data_type:
            value_data_type = default_value.value_data_type
        else:
            value_data_type = None

        return AttributeValue(
            value_data_type=value_data_type,
            numeric_value=data.get("numeric_value"),
            numeric_range_min=data.get("numeric_range_min"),
            numeric_range_max=data.get("numeric_range_max"),
            unit=data.get("unit", default_value.unit if default_value else None),
            text_value=data.get("text_value"),
            text_syntax=data.get("text_syntax"),
            code_list=data.get("code_list"),
            code_value=data.get("code_value"),
            code_title=data.get("code_title"),
            height_reference_point=data.get("height_reference_point"),
        )

    def into_template_dict(self) -> dict:
        return {
            "value_data_type": self.value_data_type.value if self.value_data_type else None,
            "numeric_value": self.numeric_value,
            "numeric_range_min": self.numeric_range_min,
            "numeric_range_max": self.numeric_range_max,
            "unit": self.unit,
            "text_value": self.text_value,
            "text_syntax": self.text_syntax,
            "code_list": self.code_list,
            "code_value": self.code_value,
            "code_title": self.code_title,
            "height_reference_point": self.height_reference_point,
        }


@dataclass
class AdditionalInformation(PlanBaseModel):
    additional_information_type_id: str
    value: AttributeValue | None = None
    plan_regulation_id: str | None = None
    modified: bool = field(compare=False, default=True)
    id_: str | None = None

    @staticmethod
    def from_template_dict(data: dict) -> AdditionalInformation:
        return AdditionalInformation(
            additional_information_type_id=cast(str, AdditionalInformationTypeLayer.get_id_by_type(data["type"])),
            value=AttributeValue.from_template_dict(data),  # TODO: check default value is OK
        )

    def into_template_dict(self) -> dict:
        return {
            "type": AdditionalInformationTypeLayer.get_type_by_id(self.additional_information_type_id),
            **(self.value.into_template_dict() if self.value else {}),
        }


@dataclass
class Regulation(PlanBaseModel):
    regulation_type_id: str
    value: AttributeValue | None = None
    additional_information: list[AdditionalInformation] = field(default_factory=list, compare=False)
    regulation_number: int | None = None
    files: list[str] = field(default_factory=list, compare=False)
    theme_ids: list[str] = field(default_factory=list, compare=False)
    subject_identifiers: list[str] = field(default_factory=list)
    verbal_regulation_type_ids: list[str] = field(default_factory=list)
    regulation_group_id: str | None = None
    modified: bool = field(compare=False, default=True)
    id_: str | None = None

    @classmethod
    def from_template_dict(cls, data: dict) -> Regulation:
        regulation_type_id = PlanRegulationTypeLayer.get_id_by_type(data["regulation_code"])
        if regulation_type_id is None:
            msg = f"Invalid regulation code in config: {data['regulation_code']}"
            raise TemplateSyntaxError(str(cls), msg)

        try:
            return Regulation(
                regulation_type_id=regulation_type_id,
                value=AttributeValue.from_template_dict(data),
                additional_information=[
                    AdditionalInformation.from_template_dict(info) for info in data.get("additional_information", [])
                ],
                regulation_number=data.get("regulation_number"),
                # files=data.get("files") if data.get("files") else [],
                # theme_id=data.get("theme"),
                subject_identifiers=data["subject_identifiers"] if data.get("subject_identifiers") else [],
                verbal_regulation_type_ids=[
                    verbal_type_id
                    for verbal_type_id in (
                        VerbalRegulationType.get_id_by_attribute("value", verbal_type)
                        for verbal_type in data["verbal_regulation_types"]
                    )
                    if verbal_type_id is not None
                ]
                if data.get("verbal_regulation_types") is not None
                else [],
                regulation_group_id=None,
                id_=None,
            )
        except KeyError as e:
            raise TemplateSyntaxError(str(cls), str(e)) from e

    def into_template_dict(self) -> dict:
        return {
            "regulation_code": PlanRegulationTypeLayer.get_type_by_id(self.regulation_type_id),
            **(self.value.into_template_dict() if self.value else {}),
            "additional_information": [info.into_template_dict() for info in self.additional_information],
            "regulation_number": self.regulation_number,
            # "files": self.files,
            # "theme_id": self.theme_id,  # Themes will be changed in a to-be-merged PR
            "subject_identifiers": self.subject_identifiers,
            "verbal_regulation_types": [
                VerbalRegulationType.get_attribute_by_id("value", verbal_type_id)
                for verbal_type_id in self.verbal_regulation_type_ids
            ],
        }


@dataclass
class Proposition(PlanBaseModel):
    value: str | None
    theme_ids: list[str] = field(default_factory=list, compare=False)
    proposition_number: int | None = None
    regulation_group_id: str | None = None
    modified: bool = field(compare=False, default=True)
    id_: str | None = None

    def into_template_dict(self) -> dict:
        return {
            "value": self.value,
            # "theme_id": self.theme_id,  # Themes will be changed in a to-be-merged PR
            "proposition_number": self.proposition_number,
        }


@dataclass
class RegulationGroup(PlanBaseModel):
    type_code_id: str | None = None
    heading: str | None = None  # Called "regulation_heading" / "kaavamääräyksen otsikko" in UI and data model
    letter_code: str | None = None
    color_code: str | None = None
    group_number: int | None = None
    regulations: list[Regulation] = field(default_factory=list, compare=False)
    propositions: list[Proposition] = field(default_factory=list, compare=False)
    modified: bool = field(compare=False, default=True)
    category: str | None = None
    id_: str | None = None

    @classmethod
    def from_template_dict(cls, data: dict) -> RegulationGroup:
        return cls(
            # NOTE: Might need to convert type code into type code ID here when
            # config file has type codes for regulation groups
            # type_code_id=data.get("type"),
            heading=data.get("heading"),
            letter_code=data.get("letter_code"),
            color_code=data.get("color_code"),
            group_number=data.get("group_number"),
            regulations=[Regulation.from_template_dict(reg_data) for reg_data in data.get("plan_regulations", [])],
            propositions=[Proposition(**prop_data) for prop_data in data.get("plan_propositions", [])],
            category=data.get("category", "Muut"),
            id_=None,
        )

    def into_template_dict(self) -> dict:
        return {
            # "type": self.type_code_id,
            "heading": self.heading,
            "letter_code": self.letter_code,
            "color_code": self.color_code,
            "group_number": self.group_number,
            "plan_regulations": [regulation.into_template_dict() for regulation in self.regulations],
            "plan_propositions": [proposition.into_template_dict() for proposition in self.propositions],
            "category": self.category,
        }

    def __str__(self):
        return " - ".join(part for part in (self.letter_code, self.heading) if part)

    def as_tooltip(self) -> str:
        letter_code = self.letter_code if self.letter_code else ""
        return (
            f"Kaavamääräyksen otsikko: {self.heading}\n"
            f"Kirjaintunnus: {letter_code}\n"
            f"Kategoria: {self.category}\n"
            f"Kaavamääräysten määrä: {len(self.regulations)}\n"
            f"Suositusten määrä: {len(self.propositions)}"
        )


@dataclass
class LifeCycle(PlanBaseModel):
    status_id: str | None = None
    id_: str | None = None
    # No need to compare `plan_id` since lifecycles can't be reassigned for another plan after creation
    plan_id: str | None = field(compare=False, default=None)
    plan_regulation_id: str | None = None
    plan_proposition_id: str | None = None
    starting_at: QDate | None = None
    ending_at: QDate | None = None
    # might not need the following
    land_use_are_id: str | None = None
    other_area_id: str | None = None
    line_id: str | None = None
    point_id: str | None = None
    modified: bool = field(compare=False, default=True)


@dataclass
class PlanFeature(PlanBaseModel):
    geom: QgsGeometry | None = None  # Need to allow None for feature templates
    type_of_underground_id: str | None = None
    layer_name: str | None = None
    name: str | None = None
    description: str | None = None
    regulation_groups: list[RegulationGroup] = field(default_factory=list, compare=False)
    plan_id: int | None = None
    modified: bool = field(compare=False, default=True)
    id_: str | None = None

    @classmethod
    def from_template_dict(cls, data: dict) -> PlanFeature:
        get_underground_id = UndergroundTypeLayer.get_attribute_value_by_another_attribute_value
        return cls(
            geom=None,
            type_of_underground_id=(
                get_underground_id("id", "value", data["type_of_underground"])
                if data.get("type_of_underground")
                else None
            ),
            layer_name=data.get("layer_name"),
            name=data.get("name"),
            description=data.get("description"),
            regulation_groups=[
                RegulationGroup.from_template_dict(group_data) for group_data in data.get("regulation_groups", [])
            ],
            plan_id=None,
            id_=None,
        )

    def into_template_dict(self) -> dict:
        return {
            # Type of underground should always be defined at this point
            "type_of_underground": UndergroundTypeLayer.get_attribute_by_id(
                "value", cast(str, self.type_of_underground_id)
            ),
            "layer_name": self.layer_name,
            "name": self.name,
            "description": self.description,
            "regulation_groups": [regulation_group.into_template_dict() for regulation_group in self.regulation_groups],
        }

    def __str__(self):
        return self.name if self.name else ""

    def as_tooltip(self) -> str:
        return (
            f"Nimi: {self.name}\n"
            f"Kuvaus: {self.description}\n"
            f"Kaavamääräysryhmien määrä: {len(self.regulation_groups)}"
        )


@dataclass
class Plan(PlanBaseModel):
    name: str | None = None
    description: str | None = None
    scale: int | None = None
    plan_type_id: str | None = None
    lifecycle_status_id: str | None = None
    lifecycles: list[LifeCycle] = field(default_factory=list, compare=False)
    record_number: str | None = None
    matter_management_identifier: str | None = None
    permanent_plan_identifier: str | None = None
    producers_plan_identifier: str | None = None
    organisation_id: str | None = None
    general_regulations: list[RegulationGroup] = field(default_factory=list, compare=False)
    documents: list[Document] = field(default_factory=list, compare=False)
    legal_effect_ids: list[str] = field(default_factory=list)
    geom: QgsGeometry | None = None
    modified: bool = field(compare=False, default=True)
    id_: str | None = None


@dataclass
class Document(PlanBaseModel):
    name: str | None = None
    url: str | None = None
    type_of_document_id: str | None = None
    accessibility: bool = False
    identifier: str | None = None
    category_of_publicity_id: str | None = None
    personal_data_content_id: str | None = None
    retention_time_id: str | None = None
    language_id: str | None = None
    document_date: datetime | None = None
    # exported_at: str | None = None
    # exported_file_key:
    confirmation_date: datetime | None = None
    arrival_date: datetime | None = None
    plan_id: str | None = None
    modified: bool = field(compare=False, default=True)
    id_: str | None = None
