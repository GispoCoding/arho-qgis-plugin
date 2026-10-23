from __future__ import annotations

import re
from textwrap import dedent
from typing import cast

from qgis.PyQt.QtGui import QStandardItem, QStandardItemModel
from qgis.PyQt.QtWidgets import QTreeView

from arho_feature_template.project.layers.plan_layers import RegulationGroupLayer
from arho_feature_template.utils.load_validation_errors import VALIDATION_ERRORS
from arho_feature_template.utils.localization_utils import get_localized_text, languages_in_order

category_map = {
    "plan": "Kaavasuunnitelma",
    "geographicalarea": "Kaavasuunnitelman ulkoraja",
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


def _feature_name(
    layer_features: dict, feature_id: str | None, languages: list[str], layer: type | None = None
) -> str | None:
    """Name of the feature with the id in `layer_features`. With `layer`, only a feature of that layer counts."""
    feature, feature_layer = layer_features.get(feature_id, (None, None))
    if feature is None or (layer is not None and feature_layer is not layer):
        return None
    return get_localized_text(feature["name"], languages=languages)


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
        # Read once per listing, reading the settings for each name is slow
        self._languages = languages_in_order()

        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(["", "Viesti"])

        self.root = self.invisibleRootItem()
        self.root.appendRow([ValidationItem("Virheet"), ValidationItem("")])
        self.root.appendRow([ValidationItem("Varoitukset"), ValidationItem("")])

    def clear(self):
        self.item(self.ERROR_INDEX, 0).removeRows(0, self.item(self.ERROR_INDEX, 0).rowCount())
        self.item(self.WARNING_INDEX, 0).removeRows(0, self.item(self.WARNING_INDEX, 0).rowCount())
        self._parent_items = {}
        self._languages = languages_in_order()

    def _add_item(
        self,
        root_index: int,
        error: str,
        object_path: str,
        message: str,
        feature_id: str | None,
        layer_features: dict,
        regulation_group_ids: dict[str, str],
    ) -> None:
        current_parent = cast(ValidationItem, self.item(root_index, 0))
        # classKey is not always a feature id, e.g. lifecycle errors give the lifecycle status code URI
        if feature_id not in layer_features:
            feature_id = None
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
                    feature_name = _feature_name(layer_features, feature_id, self._languages)

                elif part == "planregulationgroups":
                    # A regulation group is not in regulation_group_ids, its own id is the group id
                    regulation_group_id = regulation_group_ids.get(feature_id, feature_id) if feature_id else None
                    feature_name = _feature_name(
                        layer_features, regulation_group_id, self._languages, RegulationGroupLayer
                    )

                elif part == "planregulations":
                    if "additionalinformations" in parts:
                        feature_name = _feature_name(layer_features, feature_id, self._languages)
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
                        elif feature_id:
                            new_item = ValidationItem(text=feature_id[:6], feature_id=feature_id)
                        else:
                            new_item = ValidationItem(text=f"[{part}]")
                    else:
                        new_item = ValidationItem(category_map.get(part, part))
                    current_parent.appendRow([new_item, ValidationItem("")])
                    self._parent_items[path] = new_item
                current_parent = self._parent_items[path]

        else:  # If object_path is simply "planobjects" or "planregulationgroups", plan has no plan objects or regulation groups, respectively. Then, validation error has no feature_id.
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

    def add_error(
        self,
        error: str,
        object_path: str,
        message: str,
        feature_id: str | None = None,
        layer_features: dict | None = None,
        regulation_group_ids: dict[str, str] | None = None,
    ) -> None:
        self._add_item(
            self.ERROR_INDEX,
            error,
            object_path,
            message,
            feature_id,
            layer_features or {},
            regulation_group_ids or {},
        )

    def add_warning(
        self,
        error: str,
        object_path: str,
        message: str,
        feature_id: str | None = None,
        layer_features: dict | None = None,
        regulation_group_ids: dict[str, str] | None = None,
    ) -> None:
        self._add_item(
            self.WARNING_INDEX,
            error,
            object_path,
            message,
            feature_id,
            layer_features or {},
            regulation_group_ids or {},
        )


class ValidationTreeView(QTreeView):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.model = ValidationModel()
        self.setModel(self.model)

    def clear_errors(self) -> None:
        self.model.clear()

    def add_error(
        self,
        error: str,
        object_path: str,
        message: str,
        feature_id: str | None = None,
        layer_features: dict | None = None,
        regulation_group_ids: dict[str, str] | None = None,
    ) -> None:
        self.model.add_error(error, object_path, message, feature_id, layer_features, regulation_group_ids)

    def add_warning(
        self,
        error: str,
        object_path: str,
        message: str,
        feature_id: str | None = None,
        layer_features: dict | None = None,
        regulation_group_ids: dict[str, str] | None = None,
    ) -> None:
        self.model.add_warning(error, object_path, message, feature_id, layer_features, regulation_group_ids)
