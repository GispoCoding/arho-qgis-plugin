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
    "legaleffectoflocalmasterplans": "Yleiskaavan oikeusvaikutus",
    "letteridentifier": "Kirjaintunnus",
    "planmatter": "Kaava-asia",
    "planmatterphases": "Kaava-asian vaiheet",
    "plandecision": "Kaava-asian päätös",
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

        self.parent_items: dict[str, ValidationItem] = {}

        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(["", "Viesti"])

        self.root = self.invisibleRootItem()
        self.root.appendRow([ValidationItem("Virheet"), ValidationItem("")])
        self.root.appendRow([ValidationItem("Varoitukset"), ValidationItem("")])

    def clear(self):
        self.item(self.ERROR_INDEX, 0).removeRows(0, self.item(self.ERROR_INDEX, 0).rowCount())
        self.item(self.WARNING_INDEX, 0).removeRows(0, self.item(self.WARNING_INDEX, 0).rowCount())
        self._parent_items = {}

    def _add_item(
        self,
        root_index: int,
        error: str,
        object_path: str,
        message: str,
        feature_id: str,
        layer_features: dict,
    ) -> None:
        current_parent = cast(ValidationItem, self.item(root_index, 0))
        # Remove square brackets so the string is splittable by '.'
        object_path = re.sub(r"\[(\d+)\]", r".\1", object_path).lower()
        path_parts = []
        parts = object_path.split(".")
        feature_name = None
        if object_path not in ("planobjects", "planregulationgroups"):
            for part in parts:
                # Ignore following attributes to reduce layer complexity in tree
                if part in ("type", "value", "number", "geometrydata"):  # TODO: Add more if encountered
                    continue

                if part == "planobjects":
                    if not feature_id:
                        feature_name = None
                    else:
                        feature, _ = layer_features[feature_id]
                        feature_name = deserialize_localized_text(feature["name"])

                elif part == "planregulationgroups":
                    if not feature_id:
                        feature_name = None
                    else:
                        feature, layer = layer_features[feature_id]
                        if layer == AdditionalInformationLayer:
                            plan_regulation_id = AdditionalInformationLayer.get_attribute_by_id(
                                target_attribute="plan_regulation_id", id_=feature_id
                            )
                            if plan_regulation_id:
                                regulation_feature = PlanRegulationLayer.get_feature_by_id(plan_regulation_id)
                                if regulation_feature:
                                    regulation_group_id = regulation_feature["plan_regulation_group_id"]
                        elif layer in (PlanRegulationLayer, PlanPropositionLayer):
                            regulation_group_id = feature["plan_regulation_group_id"]
                        elif layer == RegulationGroupLayer:
                            regulation_group_id = feature_id

                        if regulation_group_id:
                            feature, _ = layer_features[regulation_group_id]
                            feature_name = deserialize_localized_text(feature["name"])
                        else:
                            feature_name = None

                elif part == "planregulations":
                    if "additionalinformations" in parts and feature_id is not None and feature_id in layer_features:
                        feature, _ = layer_features[feature_id]
                        feature_name = deserialize_localized_text(feature["name"])
                    else:
                        feature_name = None

                elif part == "planrecommendations":
                    feature_name = None

                path_parts.append(part)
                path = ".".join(path_parts)
                if path not in self._parent_items:
                    # If part is digit, replace it with name or ID
                    if part.isdigit():
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
                        new_item = ValidationItem(category_map.get(part, part))
                    current_parent.appendRow([new_item, ValidationItem("")])
                    self._parent_items[path] = new_item
                current_parent = self._parent_items[path]

        else:  # If object_path is simply "planobjects" or "planregulationgroups", plan has no plan features or regulation groups, respectively. Then, validation error has no feature_id.
            new_item = ValidationItem(category_map.get(object_path, object_path))
            current_parent.appendRow([new_item, ValidationItem("")])

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
        current_parent.appendRow([ValidationItem(""), message_item])

    def add_error(self, error: str, object_path: str, message: str, feature_id: str, feature_names: dict) -> None:
        self._add_item(self.ERROR_INDEX, error, object_path, message, feature_id, feature_names)

    def add_warning(self, error: str, object_path: str, message: str, feature_id: str, feature_names: dict) -> None:
        self._add_item(self.WARNING_INDEX, error, object_path, message, feature_id, feature_names)


class ValidationTreeView(QTreeView):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.model = ValidationModel()
        self.setModel(self.model)

    def clear_errors(self) -> None:
        self.model.clear()

    def add_error(self, error: str, object_path: str, message: str, feature_id: str, feature_names: dict) -> None:
        self.model.add_error(error, object_path, message, feature_id, feature_names)

    def add_warning(self, error: str, object_path: str, message: str, feature_id: str, feature_names: dict) -> None:
        self.model.add_warning(error, object_path, message, feature_id, feature_names)
