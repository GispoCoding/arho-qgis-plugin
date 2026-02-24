from __future__ import annotations

import enum
import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, cast

import yaml

from arho_feature_template.exceptions import ConfigSyntaxError, LayerNameNotFoundError
from arho_feature_template.project.layers import AbstractLayer
from arho_feature_template.qgis_plugin_tools.tools.resources import resources_path

if TYPE_CHECKING:
    from qgis.core import QgsFeature

    from arho_feature_template.core.models import AttributeValue


logger = logging.getLogger(__name__)


class PlanType(str, enum.Enum):
    REGIONAL = "regional"
    GENERAL = "general"
    TOWN = "town"


class AbstractCodeLayer(AbstractLayer):
    _cache: ClassVar[dict[str, dict[str, Any]]] = {}
    _attributes_to_leave_out_from_cache: ClassVar[list[str]] = ["created_at", "modified_at"]
    _field_names: ClassVar[list[str]] = []
    category_only_codes: ClassVar[list[str]] = []
    URI: ClassVar[str | None] = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._cache = {}
        cls._field_names = []

    @classmethod
    def build_cache(cls):
        """
        Builds a cache dictionary for the whole layer to reduce DB access.

        Iterates features of the layer and stores found attributes to `_cache` class var dictionary (keys are
        code feature IDs, values are dictionaries where keys are attribute names and values are attribute values).

        The built cache dictionary can be accessed with method `get_attribute_dict`.
        """
        cls._field_names = cls.get_from_project().fields().names()
        for feat in cls.get_from_project().getFeatures():
            cls._cache_feature(feat)

    @classmethod
    def _cache_feature(cls, feat: QgsFeature):
        if len(cls._field_names) == 0:
            cls._field_names = cls.get_from_project().fields().names()

        attribute_dict = {}
        for attribute in cls._field_names:
            if attribute in cls._attributes_to_leave_out_from_cache:
                continue
            # NOTE: 'feat.attribute(attribute)' returns None if attribute is not found
            attribute_value_to_cache = feat[attribute]
            attribute_dict[attribute] = attribute_value_to_cache

        id_ = feat["id"]
        if cls._cache.get(id_):
            logger.info("Resaving feature (ID %s) to cache for layer %s", id_, cls.name)
        cls._cache[id_] = attribute_dict

    @classmethod
    def get_attribute_dict(cls) -> dict[str, dict[str, Any]]:
        """
        Returns a dictionary of features where key is ID and value is a dictionary of attributes (name, value).

        If cache does not exist yet, will build it first and return it then.
        """
        # NOTE: If we build cache partially, we might return only part of features
        if not cls.cache_exists():
            cls.build_cache()

        return cls._cache

    @classmethod
    def cache_exists(cls) -> bool:
        return bool(cls._cache)

    @classmethod
    def get_id_by_attribute(cls, attribute: str, attribute_value: str) -> str | None:
        """Tries to retrieve ID by attribute from cache, accesses DB if attribute not cachced."""
        for _id, attribute_data in cls._cache.items():
            if attribute_data[attribute] == attribute_value:
                return _id

        return super().get_id_by_attribute(attribute, attribute_value)

    @classmethod
    def get_attribute_by_id(cls, target_attribute: str, id_: str) -> Any | None:
        """Tries to retrieve attribute by ID from cache, accesses DB if attribute not cachced."""
        attribute_value = cls._cache.get(id_, {}).get(target_attribute, "not_found")
        # Attribute value could be None and we don't want to access DB in that without a need
        if attribute_value != "not_found":
            return attribute_value

        return super().get_attribute_by_id(target_attribute, id_)

    @classmethod
    def get_attributes_by_id(cls, id_: str) -> dict[str, Any]:
        """Will cache the queried feature as a side effect if not already present in cached."""
        attributes = cls._cache.get(id_, {})
        if attributes:
            return attributes

        feat = cls.get_feature_by_id(id_)
        if not feat:
            return {}
        cls._cache_feature(feat)
        return cls._cache[id_]

    @classmethod
    def get_name_by_id(cls, id_: str) -> dict[str, str] | None:
        """Returns the name value of a feature

        Name fields in the database are always localized dictionaries."""
        return cls.get_attribute_by_id("name", id_)

    @classmethod
    def get_attribute_value_by_another_attribute_value(
        cls, target_attribute: str, filter_attribute: str, filter_value: str
    ) -> Any | None:
        for attribute_data in cls._cache.values():
            if attribute_data[filter_attribute] == filter_value:
                return attribute_data[target_attribute]

        return super().get_attribute_value_by_another_attribute_value(target_attribute, filter_attribute, filter_value)


class PlanTypeLayer(AbstractCodeLayer):
    name = "Kaavalaji"
    URI = "http://uri.suomi.fi/codelist/rytj/RY_Kaavalaji"

    category_only_codes: ClassVar[list[str]] = ["1", "2", "3"]  # "Maakuntakaava", "Asemakaava", "Yleiskaava"

    regional_plan_type_first_character = "1"
    general_plan_type_first_character = "2"
    town_plan_type_first_character = "3"

    @classmethod
    def get_plan_type(cls, _id: str | None) -> PlanType | None:
        if _id is None:
            return None
        attribute_value = cls.get_attribute_value_by_another_attribute_value("value", "id", _id)
        if not attribute_value:
            return None

        if attribute_value[0] == cls.regional_plan_type_first_character:
            return PlanType.REGIONAL
        if attribute_value[0] == cls.general_plan_type_first_character:
            return PlanType.GENERAL
        if attribute_value[0] == cls.town_plan_type_first_character:
            return PlanType.TOWN
        return None

    @classmethod
    def is_regional_plan_type(cls, _id: str | None) -> bool:
        return cls.get_plan_type(_id) == PlanType.REGIONAL

    @classmethod
    def is_general_plan_type(cls, _id: str | None) -> bool:
        return cls.get_plan_type(_id) == PlanType.GENERAL

    @classmethod
    def is_town_plan_type(cls, _id: str | None) -> bool:
        return cls.get_plan_type(_id) == PlanType.TOWN


class MunicipalityLayer(AbstractCodeLayer):
    name = "Kunta"


class RegionLayer(AbstractCodeLayer):
    name = "Maakunta"


class LifeCycleStatusLayer(AbstractCodeLayer):
    name = "Elinkaaren tila"
    URI = "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari"

    valid_status_values: ClassVar[list[str]] = ["11", "13"]  # "Voimassa ennen kaavan lainvoimaisuutta", "Voimassa"
    repealed_status_values: ClassVar[list[str]] = ["14"]  # "Kumoutunut"

    @classmethod
    def is_valid_status(cls, _id: str) -> bool:
        return cls.get_attribute_by_id("value", _id) in cls.valid_status_values

    @classmethod
    def is_repealed_status(cls, _id: str) -> bool:
        return cls.get_attribute_by_id("value", _id) in cls.repealed_status_values


class OrganisationLayer(AbstractCodeLayer):
    name = "Toimija"


class UndergroundTypeLayer(AbstractCodeLayer):
    name = "Maanalaisuuden tyyppi"
    URI = "http://uri.suomi.fi/codelist/rytj/RY_MaanalaisuudenLaji"


class PlanThemeLayer(AbstractCodeLayer):
    name = "Kaavoitusteemat"
    URI = "http://uri.suomi.fi/codelist/rytj/kaavoitusteema"


class AdditionalInformationTypeLayer(AbstractCodeLayer):
    name = "Lisätiedonlaji"
    URI = "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayksen_Lisatiedonlaji"

    ADDITIONAL_INFORMATION_CONFIG_PATH = Path(os.path.join(resources_path(), "configs", "additional_information.yaml"))

    category_only_codes: ClassVar[list[str]] = [
        "tyyppi",
        "hairionTorjuntatarve",
        "merkittavyys",
        "eriTahojenTarpeisiinVaraaminen",
        "ymparistomuutoksenLaji",
        "rakentamisenOhjaus",
    ]

    @classmethod
    def build_cache(cls):
        super().build_cache()
        configs = cls.read_additional_information_configs()
        cls.initialize_from_additional_information_config(configs)

    @classmethod
    def read_additional_information_configs(cls) -> dict:
        # NOTE: Should this config be read in another module? Imports now here to avoid circular import
        from arho_feature_template.core.models import AttributeValue, AttributeValueDataType

        with cls.ADDITIONAL_INFORMATION_CONFIG_PATH.open(encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
        try:
            return {
                info_data["code"]: {
                    "default_value": AttributeValue(
                        value_data_type=AttributeValueDataType(info_data["data_type"]),
                        unit=info_data.get("unit"),
                        code_list=info_data.get("code_list"),
                        code_title=info_data.get("code_list"),
                    )
                }
                for info_data in config_data["additional_information"]
            }
        except KeyError as e:
            raise ConfigSyntaxError(str(e)) from e

    @classmethod
    def initialize_from_additional_information_config(cls, information_configs: dict):
        for info_attributes in cls._cache.values():
            additional_data: dict = information_configs.get(info_attributes["value"], {"default_value": None})
            info_attributes |= additional_data  # noqa: PLW2901

    @classmethod
    def get_id_by_type(cls, information_type: str) -> str | None:
        return cls.get_id_by_attribute("value", information_type)

    @classmethod
    def get_type_by_id(cls, id_: str) -> str | None:
        return cls.get_attribute_by_id("value", id_)

    @classmethod
    def get_default_value_by_id(cls, id_: str) -> AttributeValue | None:
        attribute_value = cls._cache.get(id_, {}).get("default_value", "not_found")
        # Attribute value could be None and we don't want to access DB in that without a need
        if attribute_value != "not_found":
            return attribute_value
        return None


class PlanRegulationGroupTypeLayer(AbstractCodeLayer):
    name = "Kaavamääräysryhmän tyyppi"

    # TODO: Use PlanObjectLayer.name constants instead of hardcoding layer names
    # Currently there is a circular import issue if we try to import PlanObjectLayers here
    LAYER_NAME_TO_REGULATION_GROUP_TYPE_MAP: ClassVar[dict[str, str]] = {
        "Kaavasuunnitelma": "generalRegulations",
        "Aluevaraus": "landUseRegulations",
        "Osa-alue": "otherAreaRegulations",
        "Viivat": "lineRegulations",
        "Pisteet": "pointRegulations",
    }

    @classmethod
    def get_id_by_feature_layer_name(cls, layer_name: str) -> str | None:
        regulation_group_type = cls.LAYER_NAME_TO_REGULATION_GROUP_TYPE_MAP.get(layer_name)
        if not regulation_group_type:
            raise LayerNameNotFoundError(layer_name)
        regulation_type_id = cls.get_attribute_value_by_another_attribute_value("id", "value", regulation_group_type)
        if regulation_type_id:
            return cast(str, regulation_type_id)
        return None


class PlanRegulationTypeLayer(AbstractCodeLayer):
    name = "Kaavamääräyslaji"
    URI = "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji"

    PLAN_REGULATIONS_CONFIG_PATH = Path(os.path.join(resources_path(), "configs", "kaavamaaraykset.yaml"))
    # Attributes added from config: 'category_only' and 'default_value'

    verbal_regulation_types: ClassVar[list[str]] = [
        "sanallinenMaarays",
        "rakentamisrajoitusYleiskaava",
        "rakentamisrajoitusMaakuntakaava",
        "maaraAikainenRakentamisrajoitus",
        "toimenpiderajoitus",
        "maaraAikainenKieltoRakennuksenRakentamiseksi",
        "suunnittelumaarays",
        "rakentamismaarays",
        "suojelumaarays",
    ]

    @classmethod
    def build_cache(cls):
        super().build_cache()
        configs = cls.read_regulation_configs()
        cls.initialize_from_regulation_config(configs)

    @classmethod
    def read_regulation_configs(cls) -> dict:
        # NOTE: Should this config be read in another module? Imports now here to avoid circular import
        from arho_feature_template.core.models import AttributeValue, AttributeValueDataType

        with cls.PLAN_REGULATIONS_CONFIG_PATH.open(encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
        try:
            return {
                reg_data["regulation_code"]: {
                    "category_only": reg_data.get("category_only", False),
                    "default_value": AttributeValue(
                        value_data_type=(
                            AttributeValueDataType(reg_data["value_type"]) if "value_type" in reg_data else None
                        ),
                        unit=reg_data["unit"] if "unit" in reg_data else None,
                    ),
                }
                for reg_data in config_data["plan_regulations"]
            }
        except KeyError as e:
            raise ConfigSyntaxError(str(e)) from e

    @classmethod
    def initialize_from_regulation_config(cls, regulation_configs: dict):
        for reg_attributes in cls._cache.values():
            additional_reg_data: dict = regulation_configs.get(
                reg_attributes["value"], {"category_only": False, "default_value": None}
            )
            reg_attributes |= additional_reg_data  # noqa: PLW2901

    @classmethod
    def get_id_by_type(cls, regulation_type: str) -> str | None:
        return cls.get_id_by_attribute("value", regulation_type)

    @classmethod
    def get_type_by_id(cls, id_: str) -> str | None:
        return cls.get_attribute_by_id("value", id_)

    @classmethod
    def get_default_value_by_id(cls, id_: str) -> AttributeValue | None:
        attribute_value = cls._cache.get(id_, {}).get("default_value", "not_found")
        # Attribute value could be None and we don't want to access DB in that without a need
        if attribute_value != "not_found":
            return attribute_value
        return None


class VerbalRegulationType(AbstractCodeLayer):
    name = "Sanallisen määräyksen laji"
    URI = "http://uri.suomi.fi/codelist/rytj/RY_Sanallisen_Kaavamaarayksen_Laji"

    category_only_codes: ClassVar[list[str]] = ["maarayksenTyyppi"]


class CategoryOfPublicityLayer(AbstractCodeLayer):
    name = "Julkisuusluokka"
    URI = "http://uri.suomi.fi/codelist/rytj/julkisuus"

    category_only_codes: ClassVar[list[str]] = []


class TypeOfDocumentLayer(AbstractCodeLayer):
    name = "Asiakirjatyyppi"
    URI = "http://uri.suomi.fi/codelist/rytj/RY_AsiakirjanLaji_YKAK"

    category_only_codes: ClassVar[list[str]] = []


class LanguageLayer(AbstractCodeLayer):
    name = "Kieli"

    category_only_codes: ClassVar[list[str]] = []

    # Map two letter language codes into Ryhti compatible 3 letter codes
    # These are needed when using CodeComboBox with LanguageLayer
    LANGUAGE_CODE_MAP: ClassVar[dict[str, str]] = {"fi": "fin", "sv": "swe", "en": "eng", "se": "sme"}

    @classmethod
    def get_language_code_by_id(cls, id_: str) -> str | None:
        code = cls.get_attribute_by_id("value", id_)
        if code is None:
            return None
        if code in cls.LANGUAGE_CODE_MAP:
            return cls.LANGUAGE_CODE_MAP[code]
        return code

    @classmethod
    def get_id_by_language_code(cls, language_code: str) -> str | None:
        for key, value in cls.LANGUAGE_CODE_MAP.items():
            if value == language_code:
                return cls.get_id_by_attribute("value", key)

        return cls.get_id_by_attribute("value", language_code)


class PersonalDataContentLayer(AbstractCodeLayer):
    name = "Henkilötietosisältö"
    URI = "http://uri.suomi.fi/codelist/rytj/henkilotietosisalto"

    category_only_codes: ClassVar[list[str]] = []


class RetentionTimeLayer(AbstractCodeLayer):
    name = "Säilytysaika"
    URI = "http://uri.suomi.fi/codelist/rytj/sailytysaika"

    category_only_codes: ClassVar[list[str]] = []


class LegalEffectsLayer(AbstractCodeLayer):
    name = "Yleiskaavan oikeusvaikutus"
    URI = "http://uri.suomi.fi/codelist/rytj/oikeusvaik_YK"

    category_only_codes: ClassVar[list[str]] = []


code_layers = AbstractCodeLayer.__subclasses__()


def get_code_layer_by_uri(uri: str) -> type[AbstractCodeLayer] | None:
    for code_layer in code_layers:
        if uri == code_layer.URI:
            return code_layer

    return None
