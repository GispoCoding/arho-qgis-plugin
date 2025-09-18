from __future__ import annotations

import re
from textwrap import dedent
from typing import cast

from qgis.PyQt.QtGui import QStandardItem, QStandardItemModel
from qgis.PyQt.QtWidgets import QTreeView

from arho_feature_template.project.layers.plan_layers import (
    AdditionalInformationLayer,
    PlanPropositionLayer,
    PlanRegulationLayer,
    RegulationGroupLayer,
)
from arho_feature_template.utils.load_validation_errors import VALIDATION_ERRORS
from arho_feature_template.utils.misc_utils import deserialize_localized_text

category_map = {
    "plan": "Kaava",
    "geographicalarea": "Kaavan ulkoraja",
    "planobjects": "Kaavakohteet",
    "planregulationgroups": "Kaavamääräysryhmät",
    "planregulations": "Kaavamääräykset",
    "planrecommendations": "Kaavasuositukset",
    "lifecyclestatus": "Elinkaaritila",
    "additionalinformations": "Lisätiedot",
}


class ValidationItem(QStandardItem):
    def __init__(self, text: str, feature_id: str | None = None):
        super().__init__(text)
        self.setEditable(False)

        self.feature_id = feature_id


class ValidationModel(QStandardItemModel):
    ERROR_INDEX = 0
    WARNING_INDEX = 1

    def __init__(self) -> None:
        super().__init__()

        self._parent_items: dict[str, ValidationItem] = {}

        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(["", "Attribuutti", "Viesti"])

        self.root = self.invisibleRootItem()
        self.root.appendRow([ValidationItem("Virheet"), ValidationItem(""), ValidationItem("")])
        self.root.appendRow([ValidationItem("Varoitukset"), ValidationItem(""), ValidationItem("")])

    def clear(self):
        self.item(self.ERROR_INDEX, 0).removeRows(0, self.item(self.ERROR_INDEX, 0).rowCount())
        self.item(self.WARNING_INDEX, 0).removeRows(0, self.item(self.WARNING_INDEX, 0).rowCount())
        self._parent_items = {}

    def _add_item(
        self, root_index: int, error: str, instance: str, message: str, feature_id: str, layer_features: dict
    ) -> None:
        feature_name = None
        for features in layer_features.values():
            for feat_id, name, _ in features:
                if feat_id == feature_id:
                    feature_name = name
                    break
            if feature_name:
                feature_name = deserialize_localized_text(name)
                break

        current_parent = cast(ValidationItem, self.item(root_index, 0))
        # Remove square brackets so the string is splittable by '.'
        instance = re.sub(r"\[(\d+)\]", r".\1", instance).lower()
        # print(f"Instance: {instance}")
        path_parts = []
        attribute = ""
        parts = instance.split(".")
        regulation_group_id = None
        for instance_part in parts:
            if instance_part == "planregulations":
                if "additionalinformations" in parts:
                    info_feature = AdditionalInformationLayer.get_feature_by_id(feature_id)
                    if info_feature:
                        feature_id = info_feature["plan_regulation_id"]
                regulation_feature = PlanRegulationLayer.get_feature_by_id(feature_id)
                if regulation_feature:
                    regulation_group_id = regulation_feature["plan_regulation_group_id"]
            elif instance_part == "planrecommendations":
                proposition_feature = PlanPropositionLayer.get_feature_by_id(feature_id)
                if proposition_feature:
                    regulation_group_id = proposition_feature["plan_regulation_group_id"]

            # Get regulation group name
            regulation_group_feature = RegulationGroupLayer.get_feature_by_id(regulation_group_id)
            if regulation_group_feature:
                feature_name = deserialize_localized_text(regulation_group_feature["name"])
            elif instance_part in ["planregulations", "planrecommendations"]:
                feature_name = None  # regulations and propositions do not have names -> use ID

            path_parts.append(instance_part)
            path = ".".join(path_parts)
            if path not in self._parent_items:
                # If instance part is digit, replace it with name or ID
                if instance_part.isdigit():
                    # Show only 20 characters in the first column
                    max_length = 20
                    if feature_name:
                        tooltip_text = feature_name
                        if len(feature_name) > max_length:
                            feature_name = feature_name[:max_length] + "..."
                        new_item = ValidationItem(
                            text=feature_name,
                            feature_id=feature_id,
                        )
                        new_item.setToolTip(tooltip_text)
                    else:
                        new_item = ValidationItem(text=feature_id[:6], feature_id=feature_id)
                else:
                    new_item = ValidationItem(category_map.get(instance_part, instance_part))
                current_parent.appendRow([new_item, ValidationItem(""), ValidationItem("")])
                self._parent_items[path] = new_item
            current_parent = self._parent_items[path]

        current_parent = self._parent_items[instance]
        message_item = ValidationItem(text=message, feature_id=feature_id)

        processed_rule_id = error.replace("__", "/").replace("_", "-")
        try:
            description = VALIDATION_ERRORS[processed_rule_id]
        except KeyError:
            description = ""
        message_tooltip = dedent(
            f"""\
            <p>
                <span style='font-weight:bold'>Virhe:</span><br/>
                {error}
            </p>
            <p>
                <span style='font-weight:bold'>Virheviesti:</span><br/>
                {message}
            </p>
            <p>
                <span style='font-weight:bold'>Kuvaus:</span><br/>
                {description}
            </p>
            """
        )
        message_item.setToolTip(message_tooltip)
        current_parent.appendRow([ValidationItem(""), ValidationItem(attribute), message_item])
        print(f"Current parent: {current_parent}")

    def add_error(self, error: str, instance: str, message: str, feature_id: str, layer_features: dict) -> None:
        self._add_item(self.ERROR_INDEX, error, instance, message, feature_id, layer_features)

    def add_warning(self, error: str, instance: str, message: str, feature_id: str, layer_features: dict) -> None:
        self._add_item(self.WARNING_INDEX, error, instance, message, feature_id, layer_features)


class ValidationTreeView(QTreeView):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.model = ValidationModel()
        self.setModel(self.model)

    def clear_errors(self) -> None:
        self.model.clear()

    def add_error(self, error: str, instance: str, message: str, feature_id: str, layer_features: dict) -> None:
        self.model.add_error(error, instance, message, feature_id, layer_features)

    def add_warning(self, error: str, instance: str, message: str, feature_id: str, layer_features: dict) -> None:
        self.model.add_warning(error, instance, message, feature_id, layer_features)
