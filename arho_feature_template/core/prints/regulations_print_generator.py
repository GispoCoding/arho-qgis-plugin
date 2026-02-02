from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from functools import cmp_to_key
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

from arho_feature_template.core.models import LocalizedText
from arho_feature_template.core.plan_object_icons import PlanObjectIconRenderer
from arho_feature_template.core.prints.layout_items import LayoutItemFactory
from arho_feature_template.core.settings_manager import SettingsManager
from arho_feature_template.exceptions import UnexpectedNoneError
from arho_feature_template.gui.dialogs.regulations_print_settings_dialog import RegulationsPrintSettingsDialog
from arho_feature_template.project.layers.plan_layers import (
    LandUseAreaLayer,
    LineLayer,
    OtherAreaLayer,
    PlanObjectLayer,
    PointLayer,
    RegulationGroupLayer,
)
from arho_feature_template.utils.misc_utils import get_active_plan_id, iface, symbol_fingerprint

if TYPE_CHECKING:
    from arho_feature_template.core.models import PlanObject, RegulationGroup, RegulationGroupLibrary


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RegulationPrintElement:
    """Represents a unique printable regulation entry."""

    symbol: QgsSymbol | None
    letter_code: str
    heading: LocalizedText
    regulation_texts: list[LocalizedText]

    @classmethod
    def from_plan_object(cls, feat: QgsFeature, plan_object: PlanObject, symbol: QgsSymbol) -> RegulationPrintElement:
        # Get element letter code (can be empty)
        letter_code = PlanObjectLayer.feature_letter_codes_as_text(feat) or ""

        # Determine element heading (can be empty) and regulation texts (can be empty)
        heading = LocalizedText()
        found_headings: list[LocalizedText] = []
        regulation_texts: list[LocalizedText] = []
        for group in plan_object.regulation_groups:
            if group.heading:
                found_headings.append(group.heading)
                # Use heading of primary use group if it exists
                if group.is_primary_use_group():
                    heading = group.heading

            # Save all found verbal regulation texts
            regulation_texts.extend(
                text
                for text in (
                    regulation.value.text_value
                    for regulation in group.regulations
                    if regulation.is_verbal_regulation() and regulation.value and regulation.value.text_value
                )
                if text  # Filter Nones that may come from get_localized_text
            )

        # Otherwise, use heading of first group with a heading defined if one exists
        if heading == LocalizedText() and len(found_headings) > 0:
            heading = found_headings[0]

        return cls(symbol, letter_code, heading, regulation_texts)

    @classmethod
    def from_general_regulation_group(cls, general_regulation_group: RegulationGroup) -> RegulationPrintElement:
        return cls(
            None,
            "",
            general_regulation_group.heading or LocalizedText(),
            RegulationPrintElement.get_regulation_texts(general_regulation_group),
        )

    @staticmethod
    def get_regulation_texts(group: RegulationGroup) -> list[LocalizedText]:
        regulation_texts: list[LocalizedText] = []
        regulation_texts.extend(
            regulation.value.text_value
            for regulation in group.regulations
            if regulation.is_verbal_regulation() and regulation.value and regulation.value.text_value
        )
        return regulation_texts

    def data_hash(self) -> str:
        # Combine texts with each language into one for hashing
        texts_to_hash = [
            "".join(value for value in localized_text.values()) for localized_text in self.regulation_texts
        ]

        combined = {
            "symbol": json.loads(symbol_fingerprint(self.symbol)),
            "letter_code": self.letter_code or "",
            "heading": self.heading or "",
            "regulation_texts": tuple(sorted(texts_to_hash)),
        }
        key_str = json.dumps(combined, sort_keys=True)
        return sha256(key_str.encode("utf-8")).hexdigest()


class RegulationsPrintGenerator:
    # Regulation elements columns placing
    ELEMENT_MIN_HEIGHT = 10
    SPACE_BETWEEN_ELEMENTS = 5
    SPACE_AFTER_HEADING = 10

    # State vars
    CURRENT_PAGE_NUMBER: int = 0
    PAGE_HEIGHT: float = 297  # A4
    PAGE_WIDTH: float = 210
    X_COORD: float = 0
    Y_COORD: float = 0

    # SETTINGS
    SETTINGS = None

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

        # Open settings dialog
        dialog = RegulationsPrintSettingsDialog()
        if dialog.exec():
            cls.SETTINGS = dialog.get_settings()
            LayoutItemFactory.SETTINGS = cls.SETTINGS  # Copy settings to factory class
        else:
            # If user clicked Cancel, simply exit
            return

        # Remove old layout if exists after user has selected settings
        if existing:
            manager.removeLayout(existing)
            existing = None

        cls.CURRENT_PAGE_NUMBER = 0
        cls.X_COORD = cls.SETTINGS.x_margins
        cls.Y_COORD = cls.SETTINGS.y_margins

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
        label.attemptMove(QgsLayoutPoint(cls.X_COORD, cls.Y_COORD))
        label.attemptResize(QgsLayoutSize(46, 9.2))
        layout.addLayoutItem(label)

        # Move y cordinate
        cls.Y_COORD = float(cls.Y_COORD + label.sizeWithUnits().height() + cls.SPACE_AFTER_HEADING)

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
        if cls.SETTINGS is None:
            msg = "Print settings not defined!"
            raise UnexpectedNoneError(msg)

        print_element_hashes: set[str] = set()

        # General regulations
        general_regulation_groups = RegulationGroupLayer.get_general_regulation_groups(get_active_plan_id())
        for group in general_regulation_groups:
            element = RegulationPrintElement.from_general_regulation_group(group)
            cls._add_element_to_layout(element, layout)

        # Plan object regulations
        regulation_groups = active_regulation_groups_library.regulation_groups

        for layer in [LandUseAreaLayer, OtherAreaLayer, LineLayer, PointLayer]:
            vector_layer = layer.get_from_project()
            feats = list(vector_layer.getFeatures())
            plan_objects = layer.models_from_features(feats, regulation_groups)

            # Construct symbol ordering dict
            symbol_index_map: dict[str, int] = {}
            failed_count = 0
            for index, symbol_item in enumerate(layer.get_from_project().renderer().legendSymbolItems()):
                symbol = symbol_item.symbol()
                try:
                    symbol_index_map[symbol_fingerprint(symbol_item.symbol())] = index
                except TypeError:
                    failed_count += 1

            if failed_count > 0:
                logger.debug("Failed to get symbol of %s legend symbol items.", str(failed_count))

            # Collection of RegulationPrintElements with symbol index, letter code and heading.
            # Order of the elements is based on them
            elements_collection: list[tuple[RegulationPrintElement, int, str, str]] = []

            symbols_for_feats = PlanObjectIconRenderer.get_symbols_for_layer_features(vector_layer, feats)

            # List elements are in same order so we can zip lists
            for plan_object, (feat, symbol) in zip(plan_objects, symbols_for_feats):
                if symbol is None:
                    # What to do if no symbol was found?
                    continue

                # Symbol must be cloned, otherwise QGIS crashes later when dereferencing ref dropped by renderer
                cloned_symbol = symbol.clone()

                # element = RegulationPrintElement.create(feat, plan_object, cloned_symbol, language)
                element = RegulationPrintElement.from_plan_object(feat, plan_object, cloned_symbol)

                # Check if element exists already. If it does, skip creating a duplicate
                hash_value = element.data_hash()
                if hash_value in print_element_hashes:
                    continue
                print_element_hashes.add(hash_value)

                # Default to large index if symbol is not found in map
                symbol_index = symbol_index_map.get(symbol_fingerprint(symbol), 10000)
                heading_in_primary_language = element.heading.get(SettingsManager.get_primary_language(), "")
                elements_collection.append(
                    (element, symbol_index, element.letter_code.casefold(), heading_in_primary_language.casefold())
                )

            # Sort elements to add them in correct order to layout
            elements_collection.sort(key=cmp_to_key(cls._compare_elements))
            for element, _, _, _ in elements_collection:
                cls._add_element_to_layout(element, layout)

    @classmethod
    def _add_element_to_layout(cls, element: RegulationPrintElement, layout: QgsPrintLayout):
        item = LayoutItemFactory.new_regulation_print_item(element, layout, (cls.X_COORD, cls.Y_COORD))
        if item is None:
            return

        if cls._item_does_not_fit_to_page(item):
            cls.add_page_to_layout(layout)

            # Set Y coord
            page_index = cls.CURRENT_PAGE_NUMBER - 1
            cls.Y_COORD = cls.SETTINGS.y_margins + cls.PAGE_HEIGHT * page_index  # type: ignore

        # Place the new item, X coord should be correct already
        item.attemptMove(QgsLayoutPoint(item.x(), cls.Y_COORD))

        # Move Y coordinate to be ready for next item
        cls.Y_COORD = float(
            cls.Y_COORD + max(item.sizeWithUnits().height(), cls.ELEMENT_MIN_HEIGHT) + cls.SPACE_BETWEEN_ELEMENTS
        )

    @staticmethod
    def _compare_elements(
        a: tuple[RegulationPrintElement, int, str, str], b: tuple[RegulationPrintElement, int, str, str]
    ) -> int:
        """Compare tuples with RegulationPrintElements to sort them."""
        # 1. Compare symbol indices (legend order)
        if a[1] != b[1]:
            return -1 if a[1] < b[1] else 1

        # 2. Compare letter codes if needed
        if a[2] != b[2]:
            return -1 if a[2] < b[2] else 1

        # 2. Compare headings in primary langauge if needed
        if a[3] != b[3]:
            return -1 if a[3] < b[3] else 1

        return 0

    @classmethod
    def _item_does_not_fit_to_page(cls, item: QgsLayoutItem) -> bool:
        item_bottom_y = cls.Y_COORD + item.sizeWithUnits().height()
        return item_bottom_y + cls.SETTINGS.y_margins > cls.PAGE_HEIGHT * cls.CURRENT_PAGE_NUMBER  # type: ignore
