from __future__ import annotations

import enum
import json
import logging
import textwrap
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field, fields
from hashlib import sha256
from typing import TYPE_CHECKING, TypeAlias, cast

from arho_feature_template.project.layers.code_layers import (
    AdditionalInformationTypeLayer,
    PlanRegulationTypeLayer,
    UndergroundTypeLayer,
    VerbalRegulationType,
)
from arho_feature_template.utils.localization_utils import (
    get_localized_text,
    localized_text_as_str,
    read_localized_field_backward_compatible,
)
from arho_feature_template.utils.misc_utils import null_to_none

if TYPE_CHECKING:
    from datetime import date

    from qgis.core import QgsGeometry


# Type alias for localized text fields for models
LocalizedText: TypeAlias = dict[str, str]


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

    plan_features: list[PlanObject] = field(default_factory=list, compare=False)

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
                    PlanObject.from_template_dict(plan_feature_data) for plan_feature_data in data["plan_features"]
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

    def into_hash_map(self) -> defaultdict[int, list]:
        plan_object_hash_map: defaultdict[int, list] = defaultdict(list)
        for plan_object in self.plan_features:
            plan_object_hash_map[plan_object.data_hash()].append(plan_object)
        return plan_object_hash_map


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

    def into_hash_map(self) -> defaultdict[int, list]:
        regulation_group_hash_map: defaultdict[int, list] = defaultdict(list)
        for group in self.regulation_groups:
            regulation_group_hash_map[group.data_hash()].append(group)
        return regulation_group_hash_map

    def get_letter_codes(self) -> set[str]:
        """Returns set of non-empty short names (letter codes) of regulation groups part of the library."""
        return {group.letter_code for group in self.regulation_groups if group.letter_code}


@dataclass
class PlanBaseModel:
    def __post_init__(self):
        # Set all found NULLs to None
        for _field in fields(self):
            value = getattr(self, _field.name)
            setattr(self, _field.name, null_to_none(value))

    def data_hash(self) -> int:
        hash_components = []
        for _field in fields(self):
            # Hash fields unless they are marked with compare=False and don't have hash=True in metadata
            if not _field.compare and not _field.metadata.get("hash", False):
                continue

            value = getattr(self, _field.name)
            # Convert lists into frozensets, consider if list has PlanBaseModels
            if isinstance(value, list):
                if len(value) > 0 and isinstance(value[0], PlanBaseModel):
                    # value = tuple(sorted(element.data_hash() for element in value))
                    value = frozenset(element.data_hash() for element in value)
                else:
                    # value = tuple(sorted(element for element in value))
                    value = frozenset(value)

            elif isinstance(value, dict):
                value = sha256(json.dumps(value, sort_keys=True).encode("utf-8")).hexdigest()

            # Call data_hash recursively
            elif isinstance(value, PlanBaseModel):
                value = value.data_hash()

            hash_components.append(value)

        return hash(tuple(hash_components))


@dataclass
class AttributeValue(PlanBaseModel):
    value_data_type: AttributeValueDataType | None = None

    numeric_value: int | float | None = None
    numeric_range_min: int | float | None = None
    numeric_range_max: int | float | None = None

    unit: str | None = None

    text_value: LocalizedText | None = None
    text_syntax: str | None = None

    code_list: str | None = None
    code_value: str | None = None
    code_title: str | None = None

    height_reference_point: str | None = None

    def __post_init__(self):
        super().__post_init__()

        for _field in fields(self):
            value = getattr(self, _field.name)
            # Convert empty strings and such to None, otherwise hash comparisons fail
            if not value:
                setattr(self, _field.name, None)

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
    plan_regulation_id: str | None = field(compare=False, default=None)  # Should be ok that this field is not compared
    modified: bool = field(compare=False, default=True)
    id_: str | None = field(compare=False, default=None)

    def __post_init__(self):
        super().__post_init__()

        # Replace empty AttributeValue with None to stay consistent for hashing
        if self.value == AttributeValue():
            self.value = None

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
    additional_information: list[AdditionalInformation] = field(
        default_factory=list, compare=False, metadata={"hash": True}
    )
    regulation_number: int | None = None
    files: list[str] = field(default_factory=list, compare=False)  # hash?
    theme_ids: list[str] = field(default_factory=list, compare=False, metadata={"hash": True})
    subject_identifiers: list[str] = field(default_factory=list)
    verbal_regulation_type_ids: list[str] = field(default_factory=list)
    regulation_group_id: str | None = field(compare=False, default=None)  # Should be ok that this field is not compared
    lifecycle_status_id: str | None = None
    period_of_validity_start: date | None = None
    period_of_validity_end: date | None = None
    modified: bool = field(compare=False, default=True)
    id_: str | None = field(compare=False, default=None)

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

    def is_verbal_regulation(self) -> bool:
        reg_type = PlanRegulationTypeLayer.get_type_by_id(self.regulation_type_id)
        return reg_type in PlanRegulationTypeLayer.verbal_regulation_types


@dataclass
class Proposition(PlanBaseModel):
    value: LocalizedText | None
    theme_ids: list[str] = field(default_factory=list, compare=False, metadata={"hash": True})
    proposition_number: int | None = None
    regulation_group_id: str | None = field(compare=False, default=None)
    lifecycle_status_id: str | None = None
    period_of_validity_start: date | None = None
    period_of_validity_end: date | None = None
    modified: bool = field(compare=False, default=True)
    id_: str | None = field(compare=False, default=None)

    def into_template_dict(self) -> dict:
        return {
            "value": self.value,
            # "theme_id": self.theme_id,  # Themes will be changed in a to-be-merged PR
            "proposition_number": self.proposition_number,
        }


@dataclass
class RegulationGroup(PlanBaseModel):
    type_code_id: str | None = None
    heading: LocalizedText | None = None  # Called "regulation_heading" / "kaavamääräyksen otsikko" in UI and data model
    letter_code: str | None = None
    color_code: str | None = None
    group_number: int | None = None
    regulations: list[Regulation] = field(default_factory=list, compare=False, metadata={"hash": True})
    propositions: list[Proposition] = field(default_factory=list, compare=False, metadata={"hash": True})
    modified: bool = field(compare=False, default=True)
    category: str | None = field(compare=False, default=None)
    id_: str | None = field(compare=False, default=None)

    @classmethod
    def from_template_dict(cls, data: dict) -> RegulationGroup:
        return cls(
            # NOTE: Might need to convert type code into type code ID here when
            # config file has type codes for regulation groups
            # type_code_id=data.get("type"),
            heading=read_localized_field_backward_compatible(data.get("heading")),
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

    def is_primary_use_group(self) -> bool:
        primary_use_id = AdditionalInformationTypeLayer.get_id_by_type("paakayttotarkoitus")
        for regulation in self.regulations:
            for ai in regulation.additional_information:
                if ai.additional_information_type_id == primary_use_id:
                    return True
        return False

    def __str__(self):
        return " - ".join(part for part in (self.letter_code, get_localized_text(self.heading)) if part)

    def as_tooltip(self, long: bool = True) -> str:  # noqa: FBT001, FBT002
        """If long format, show regulation names."""
        wrapper = textwrap.TextWrapper(width=70, subsequent_indent="    ")

        def wrap_line(label: str, value: str) -> str:
            text = f"{label}: {value}"
            return "\n".join(wrapper.fill(line) for line in text.splitlines())

        if long:
            names = [
                get_localized_text(PlanRegulationTypeLayer.get_name_by_id(reg.regulation_type_id))
                for reg in self.regulations
            ]
            return (
                f"{wrap_line('Kaavamääräyksen otsikko', get_localized_text(self.heading) or '')}\n"
                f"{wrap_line('Kirjaintunnus', self.letter_code or '')}\n"
                f"{wrap_line('Järjestysnumero', str(self.group_number) if self.group_number else '')}\n"
                # f"{wrap_line('Kategoria', self.category)}\n"
                f"{wrap_line('Kaavamääräykset', ', '.join(name for name in names if name))}\n"
                f"{wrap_line('Suositusten määrä', str(len(self.propositions)))}"
            )
        return (
            f"{wrap_line('Kaavamääräyksen otsikko', get_localized_text(self.heading) or '')}\n"
            f"{wrap_line('Kirjaintunnus', self.letter_code or '')}\n"
            f"{wrap_line('Järjestysnumero', str(self.group_number) if self.group_number else '')}\n"
            # f"{wrap_line('Kategoria', self.category)}\n"
            f"{wrap_line('Kaavamääräysten määrä', str(len(self.regulations)))}\n"
            f"{wrap_line('Suositusten määrä', str(len(self.propositions)))}"
        )


@dataclass
class PlanObject(PlanBaseModel):
    geom: QgsGeometry | None = None  # Need to allow None for feature templates
    type_of_underground_id: str | None = None
    layer_name: str | None = None
    name: LocalizedText | None = None
    description: LocalizedText | None = None
    lifecycle_status_id: str | None = None
    period_of_validity_start: date | None = None
    period_of_validity_end: date | None = None
    regulation_groups: list[RegulationGroup] = field(default_factory=list, compare=False)
    plan_id: int | None = None
    modified: bool = field(compare=False, default=True)
    id_: str | None = field(compare=False, default=None)

    @classmethod
    def from_template_dict(cls, data: dict) -> PlanObject:
        get_underground_id = UndergroundTypeLayer.get_attribute_value_by_another_attribute_value
        return cls(
            geom=None,
            type_of_underground_id=(
                get_underground_id("id", "value", data["type_of_underground"])
                if data.get("type_of_underground")
                else None
            ),
            layer_name=data.get("layer_name"),
            name=read_localized_field_backward_compatible(data.get("name")),
            description=read_localized_field_backward_compatible(data.get("description")),
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

    def __str__(self) -> str:
        return get_localized_text(self.name) or "" if self.name else ""

    def as_tooltip(self, only_primary_language: bool = False) -> str:  # noqa: FBT001, FBT002
        if only_primary_language:
            return (
                f"Nimi: {get_localized_text(self.name)}\n"
                f"Kuvaus: {get_localized_text(self.description)}\n"
                f"Kaavamääräysryhmien määrä: {len(self.regulation_groups)}"
            )
        return (
            f"Nimi: {localized_text_as_str(self.name)}\n"
            f"Kuvaus: {localized_text_as_str(self.description)}\n"
            f"Kaavamääräysryhmien määrä: {len(self.regulation_groups)}"
        )


@dataclass
class Plan(PlanBaseModel):
    name: str | None = None
    description: str | None = None
    scale: int | None = None
    lifecycle_status_id: str | None = None
    general_regulations: list[RegulationGroup] = field(default_factory=list, compare=False)
    documents: list[Document] = field(default_factory=list, compare=False)
    legal_effect_ids: list[str] = field(default_factory=list)
    geom: QgsGeometry | None = None
    plan_matter_id: str | None = None
    approval_date: date | None = None
    period_of_validity_start: date | None = None
    period_of_validity_end: date | None = None
    locked: bool = False
    modified: bool = field(compare=False, default=True)
    id_: str | None = field(compare=False, default=None)


@dataclass
class PlanMatter(PlanBaseModel):
    name: LocalizedText | None = None
    description: LocalizedText | None = None
    plan_type_id: str | None = None
    record_number: str | None = None
    case_identifier: str | None = None
    permanent_plan_identifier: str | None = None
    producers_plan_identifier: str | None = None
    organisation_id: str | None = None
    modified: bool = field(compare=False, default=True)
    id_: str | None = field(compare=False, default=None)


@dataclass(unsafe_hash=True)
class Document(PlanBaseModel):
    name: LocalizedText | None = None
    url: str | None = None
    type_of_document_id: str | None = None
    accessibility: bool = False
    identifier: str | None = None
    category_of_publicity_id: str | None = None
    personal_data_content_id: str | None = None
    retention_time_id: str | None = None
    language_id: str | None = None
    document_date: date | None = None
    # exported_at: str | None = None
    # exported_file_key:
    confirmation_date: date | None = None
    arrival_date: date | None = None
    plan_id: str | None = None
    modified: bool = field(compare=False, default=True)
    id_: str | None = field(compare=False, default=None)
