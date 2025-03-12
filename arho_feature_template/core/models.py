from __future__ import annotations

import enum
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from arho_feature_template.core import libraries
from arho_feature_template.utils.misc_utils import iface

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


@dataclass
class AttributeValue:
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


@dataclass
class AdditionalInformation:
    config: libraries.AdditionalInformationConfig  # includes code and unit among other needed data for saving feature

    id_: str | None = None
    plan_regulation_id: str | None = None
    type_additional_information_id: str | None = None
    value: AttributeValue | None = None

    @staticmethod
    def from_config_data(data: dict) -> AdditionalInformation:
        ai_config = libraries.AdditionalInformationConfigLibrary.get_config_by_code(data["type"])
        return AdditionalInformation(
            config=ai_config,
            value=AttributeValue(
                value_data_type=data.get(
                    "value_data_type",
                    ai_config.default_value.value_data_type if ai_config.default_value is not None else None,
                ),
                numeric_value=data.get("numeric_value"),
                numeric_range_min=data.get("numeric_range_min"),
                numeric_range_max=data.get("numeric_range_max"),
                unit=data.get(
                    "unit",
                    ai_config.default_value.unit if ai_config.default_value is not None else None,
                ),
                text_value=data.get("text_value"),
                text_syntax=data.get("text_syntax"),
                code_list=data.get("code_list"),
                code_value=data.get("code_value"),
                code_title=data.get("code_title"),
                height_reference_point=data.get("height_reference_point"),
            ),
        )


@dataclass
class Regulation:
    config: libraries.RegulationConfig  # includes regulation_code and unit among other needed data for saving feature
    value: AttributeValue | None = None
    additional_information: list[AdditionalInformation] = field(default_factory=list)
    regulation_number: int | None = None
    files: list[str] = field(default_factory=list)
    theme: str | None = None
    topic_tag: str | None = None
    verbal_regulation_type_ids: list[str] = field(default_factory=list)
    regulation_group_id: str | None = None
    id_: str | None = None


@dataclass
class Proposition:
    value: str
    theme_id: str | None = None
    proposition_number: int | None = None
    regulation_group_id: str | None = None
    id_: str | None = None


@dataclass
class RegulationGroup:
    type_code_id: str | None = None
    name: str | None = None
    short_name: str | None = None
    color_code: str | None = None
    group_number: int | None = None
    regulations: list[Regulation] = field(default_factory=list)
    propositions: list[Proposition] = field(default_factory=list)
    id_: str | None = None

    @classmethod
    def from_config_data(cls, data: dict) -> RegulationGroup:
        regulations = []
        for reg_data in data["plan_regulations"]:
            reg_code = reg_data["regulation_code"]
            config = libraries.RegulationLibrary.get_regulation_by_code(reg_code)
            if config:
                regulations.append(
                    Regulation(
                        config=config,
                        value=reg_data.get("value"),
                        additional_information=[
                            AdditionalInformation.from_config_data(info_data)
                            for info_data in reg_data.get("additional_information", [])
                        ],
                        regulation_number=reg_data.get("regulation_number"),
                        files=reg_data.get("files") if reg_data.get("files") else [],
                        theme=reg_data.get("theme"),
                        topic_tag=reg_data.get("topic_tag"),
                        regulation_group_id=None,
                        id_=None,
                    )
                )
            else:
                iface.messageBar().pushWarning("", f"Could not find plan regulation {reg_code}!")
        return cls(
            type_code_id=data.get("type"),  # NOTE: Might need to convert type code into type code ID here when
            # config file has type codes for regulation groups
            name=data.get("name"),
            short_name=data.get("short_name"),
            color_code=data.get("color_code"),
            group_number=data.get("group_number"),
            regulations=regulations,
            propositions=[],
            id_=None,
        )

    def __str__(self):
        return " - ".join(part for part in (self.short_name, self.name) if part)


@dataclass
class LifeCycle:
    status_id: str | None = None
    id_: str | None = None
    plan_id: str | None = None
    plan_regulation_id: str | None = None
    plan_proposition_id: str | None = None
    starting_at: QDate | None = None
    ending_at: QDate | None = None
    # might not need the following
    land_use_are_id: str | None = None
    other_area_id: str | None = None
    line_id: str | None = None
    land_use_point_id: str | None = None
    other_point_id: str | None = None


@dataclass
class PlanFeature:
    geom: QgsGeometry | None = None  # Need to allow None for feature templates
    type_of_underground_id: str | None = None
    layer_name: str | None = None
    name: str | None = None
    description: str | None = None
    regulation_groups: list[RegulationGroup] = field(default_factory=list)
    plan_id: int | None = None
    id_: str | None = None

    @classmethod
    def from_config_data(cls, data: dict) -> PlanFeature:
        # TODO: Implement
        return cls(**data)

    def __str__(self):
        return self.name if self.name else ""


@dataclass
class Plan:
    name: str | None = None
    description: str | None = None
    plan_type_id: str | None = None
    lifecycle_status_id: str | None = None
    lifecycles: list[LifeCycle] = field(default_factory=list)
    record_number: str | None = None
    matter_management_identifier: str | None = None
    permanent_plan_identifier: str | None = None
    producers_plan_identifier: str | None = None
    organisation_id: str | None = None
    general_regulations: list[RegulationGroup] = field(default_factory=list)
    documents: list[Document] = field(default_factory=list)
    legal_effect_ids: list[str] = field(default_factory=list)
    geom: QgsGeometry | None = None
    id_: str | None = None


@dataclass
class Document:
    name: str | None = None
    url: str | None = None
    type_of_document_id: str | None = None
    decision: bool | None = None
    # permanent_document_identifier: str | None = None
    category_of_publicity_id: str | None = None
    personal_data_content_id: str | None = None
    retention_time_id: str | None = None
    language_id: str | None = None
    document_date: datetime | None = None
    # exported_at: str | None = None
    # exported_file_key:
    confirmation_date: datetime | None = None
    arrival_date: datetime | None = None
    plan_id: int | None = None
    id_: str | None = None
