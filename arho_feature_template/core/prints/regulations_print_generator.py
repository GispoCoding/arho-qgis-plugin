from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256
from typing import TYPE_CHECKING

from qgis.core import (
    QgsFeature,
    QgsLayoutItem,
    QgsLayoutItemLabel,
    QgsLayoutItemPage,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsPrintLayout,
    QgsProject,
    QgsSymbol,
)
from qgis.PyQt.QtWidgets import QMessageBox

from arho_feature_template.core.plan_object_icons import PlanObjectIconRenderer
from arho_feature_template.core.prints.layout_items import LayoutItemFactory
from arho_feature_template.core.settings_manager import SettingsManager
from arho_feature_template.project.layers.plan_layers import (
    LandUseAreaLayer,
    LineLayer,
    OtherAreaLayer,
    PlanObjectLayer,
    PointLayer,
)
from arho_feature_template.utils.localization_utils import deserialize_localized_text
from arho_feature_template.utils.misc_utils import iface, symbol_fingerprint

if TYPE_CHECKING:
    from arho_feature_template.core.models import PlanObject, RegulationGroupLibrary


@dataclass(frozen=True)
class RegulationPrintElement:
    """Represents a unique printable regulation entry."""

    symbol: QgsSymbol
    letter_code: str
    heading: str  # As localized text
    regulation_texts: list[str]  # As localized texts

    @classmethod
    def create(
        cls,
        feat: QgsFeature,
        plan_object: PlanObject,
        symbol: QgsSymbol,
        language: str,  # TODO: multiple languages
    ) -> RegulationPrintElement:
        # Get element letter code (can be empty)
        letter_code = PlanObjectLayer.feature_letter_codes_as_text(feat) or ""

        # Determine element heading (can be empty) and regulation texts (can be empty)
        heading = ""  # "[PUUTTUVA OTSIKKO]"
        found_headings: list[str] = []
        regulation_texts: list[str] = []
        for group in plan_object.regulation_groups:
            if group.heading:
                localized_heading = deserialize_localized_text(group.heading, language)
                if not localized_heading:
                    continue
                found_headings.append(localized_heading)
                # Use heading of primary use group if it exists
                if group.is_primary_use_group():
                    heading = localized_heading

            # Save all found verbal regulation texts
            regulation_texts.extend(
                text
                for text in (
                    deserialize_localized_text(regulation.value.text_value, language)
                    for regulation in group.regulations
                    if regulation.is_verbal_regulation() and regulation.value and regulation.value.text_value
                )
                if text  # Filter Nones that may come from deserialize_localized_text
            )

        # Otherwise, use heading of first group with a heading defined if one exists
        if heading == "" and len(found_headings) > 0:
            heading = found_headings[0]

        return cls(symbol, letter_code, heading, regulation_texts)

    def data_hash(self) -> str:
        combined = {
            "symbol": json.loads(symbol_fingerprint(self.symbol)),
            "letter_code": self.letter_code or "",
            "heading": self.heading or "",
            "regulation_texts": tuple(sorted(self.regulation_texts)),
        }
        key_str = json.dumps(combined, sort_keys=True)
        return sha256(key_str.encode("utf-8")).hexdigest()


class RegulationsPrintGenerator:
    # General settings
    BOTTOM_MARGIN = 10

    # Regulation elements columns placing
    COLUMNS = 1  # 1 or 2 for now
    COL_1_START_X = 20
    COL_2_START_X = 115
    START_Y = 35
    ELEMENT_MIN_HEIGHT = 10
    SPACE_BETWEEN_ELEMENTS = 5

    # State vars
    CURRENT_PAGE_NUMBER = 0
    PAGE_HEIGHT = 297  # A4

    @classmethod
    def new_regulations_print_layout(
        cls, active_regulation_groups_library: RegulationGroupLibrary, name: str = "Tulosteen määräysosa"
    ) -> QgsPrintLayout:
        project = QgsProject.instance()
        manager = project.layoutManager()

        existing = manager.layoutByName(name)
        if existing:
            response = QMessageBox.question(
                None,
                "Tulosteen määräysosan luominen",
                "Tulosteelle on jo luotuna määräysosa. Haluatko ylikirjoittaa vanhan määräysosan?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if response == QMessageBox.No:
                iface.openLayoutDesigner(existing)
                return existing

            manager.removeLayout(existing)
            existing = None

        cls.CURRENT_PAGE_NUMBER = 0

        # Create layout
        layout = QgsPrintLayout(project)
        layout.setName(name)
        manager.addLayout(layout)

        cls.add_page_to_layout(layout)
        cls.add_regulation_print_heading(layout)
        cls.add_regulation_print_elements(layout, active_regulation_groups_library)

        iface.openLayoutDesigner(layout)
        return layout

    @classmethod
    def add_page_to_layout(cls, layout: QgsPrintLayout):
        # Add page
        page = QgsLayoutItemPage(layout)
        layout.pageCollection().addPage(page)

        # Page settings: set orientation to portrait
        newest_page_i = layout.pageCollection().pageCount() - 1
        page = layout.pageCollection().page(newest_page_i)
        page.setPageSize("A4", QgsLayoutItemPage.Orientation.Portrait)
        cls.CURRENT_PAGE_NUMBER += 1
        cls.PAGE_HEIGHT = page.sizeWithUnits().height()

        return page

    @classmethod
    def add_regulation_print_heading(cls, layout: QgsPrintLayout) -> QgsLayoutItemLabel:
        label = QgsLayoutItemLabel(layout)
        label.setMode(QgsLayoutItemLabel.Mode.ModeHtml)
        label.setText("<h1>Määräysosa</h1>")
        label.attemptMove(QgsLayoutPoint(20, 15))
        label.attemptResize(QgsLayoutSize(46, 9.2))
        layout.addLayoutItem(label)

        return label

    @classmethod
    def add_object_type_heading(
        cls, text: str, layout: QgsPrintLayout, coords: tuple[float, float]
    ) -> QgsLayoutItemLabel:
        label = QgsLayoutItemLabel(layout)
        label.setMode(QgsLayoutItemLabel.Mode.ModeHtml)
        label.setText(f"<h2>{text}</h2>")
        label.attemptResize(QgsLayoutSize(46, 9.2))
        label.attemptMove(QgsLayoutPoint(*coords))
        layout.addLayoutItem(label)

        return label

    @classmethod
    def add_regulation_print_elements(
        cls, layout: QgsPrintLayout, active_regulation_groups_library: RegulationGroupLibrary
    ):
        x_coord: float = cls.COL_1_START_X
        y_coord: float = cls.START_Y

        print_element_hashes: set[str] = set()

        language = SettingsManager.get_primary_language()  # TODO: Multiple languages

        def move_y_coordinate(y: float, item: QgsLayoutItem) -> float:
            return float(y + max(item.sizeWithUnits().height(), cls.ELEMENT_MIN_HEIGHT) + cls.SPACE_BETWEEN_ELEMENTS)

        regulation_groups = active_regulation_groups_library.regulation_groups

        ordered_plan_object_layers = [LandUseAreaLayer, OtherAreaLayer, LineLayer, PointLayer]
        for i, layer in enumerate(ordered_plan_object_layers):
            # Change column, set coordinates
            if i == 2 and cls.COLUMNS == 2:  # noqa: PLR2004
                y_coord = cls.START_Y
                x_coord = cls.COL_2_START_X

            heading_label = cls.add_object_type_heading(layer.name, layout, (x_coord, y_coord))
            y_coord = move_y_coordinate(y_coord, heading_label)

            vector_layer = layer.get_from_project()
            feats = list(vector_layer.getFeatures())
            plan_objects = layer.models_from_features(feats, regulation_groups)

            # List elements are in same order so we can zip lists
            for plan_object, (feat, symbol) in zip(
                plan_objects, PlanObjectIconRenderer.get_symbols_for_layer_features(vector_layer, feats)
            ):
                if symbol is None:
                    # What to do if no symbol was found?
                    continue

                # Symbol must be cloned, otherwise QGIS crashes later when dereferencing ref dropped by renderer
                cloned_symbol = symbol.clone()

                element = RegulationPrintElement.create(feat, plan_object, cloned_symbol, language)

                # Check if element exists already. If it does, skip creating a duplicate
                hash_value = element.data_hash()
                if hash_value in print_element_hashes:
                    continue

                item = LayoutItemFactory.new_regulation_print_item(element, layout, (x_coord, y_coord))
                print_element_hashes.add(hash_value)

                if cls._item_does_not_fit_to_page(y_coord, item):
                    cls.add_page_to_layout(layout)

                    # Set Y coord
                    page_index = cls.CURRENT_PAGE_NUMBER - 1
                    y_coord = cls.START_Y + cls.PAGE_HEIGHT * page_index

                # Place the new item, X coord should be correct already
                item.attemptMove(QgsLayoutPoint(item.x(), y_coord))

                # Move Y coordinate to be ready for next item
                y_coord = move_y_coordinate(y_coord, item)

            # Put extra space between plan object types
            y_coord += 5

    @classmethod
    def _item_does_not_fit_to_page(cls, y_coord: float, item: QgsLayoutItem) -> bool:
        item_bottom_y = y_coord + item.sizeWithUnits().height()
        return item_bottom_y + cls.BOTTOM_MARGIN > cls.PAGE_HEIGHT * cls.CURRENT_PAGE_NUMBER
