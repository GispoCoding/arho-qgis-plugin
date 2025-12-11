from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256

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
from arho_feature_template.project.layers.plan_layers import (
    LandUseAreaLayer,
    LineLayer,
    OtherAreaLayer,
    PlanObjectLayer,
    PointLayer,
)
from arho_feature_template.utils.misc_utils import deserialize_localized_text, iface, symbol_fingerprint


@dataclass(frozen=True)
class RegulationPrintElement:
    """Represents a unique printable regulation entry."""

    symbol: QgsSymbol
    letter_code: str
    heading: str
    text: str

    @classmethod
    def from_feat_and_symbol(cls, feat: QgsFeature, symbol: QgsSymbol) -> RegulationPrintElement:
        letter_code = PlanObjectLayer.feature_letter_codes_as_text(feat) or ""

        heading = feat.attribute("name")
        heading = deserialize_localized_text(heading) if heading else "[PUUTTUVA OTSIKKO]"

        # NOTE: This could be done elsewhere or refactored into a method
        text: str = ""
        regulation_values = feat.attribute("regulation_values")
        if regulation_values:
            # NOTE: There can be only one verbal regulation value in a regulation group?
            verbal_regulations = regulation_values.get("sanallinenMaarays")
            if verbal_regulations:
                text = deserialize_localized_text(verbal_regulations["text_value"]) or ""

        return cls(symbol, letter_code, heading, text)

    def data_hash(self) -> str:
        combined = {
            "symbol": json.loads(symbol_fingerprint(self.symbol)),
            "letter_code": self.letter_code or "",
            "heading": self.heading or "",
            "text": self.text or "",
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
    def new_regulations_print_layout(cls, name: str = "Tulosteen määräysosa") -> QgsPrintLayout:
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
        cls.add_regulation_print_elements(layout)

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
    def add_regulation_print_elements(cls, layout: QgsPrintLayout):
        x_coord: float = cls.COL_1_START_X
        y_coord: float = cls.START_Y

        print_element_hashes: set[str] = set()

        def move_y_coordinate(y: float, item: QgsLayoutItem) -> float:
            return float(y + max(item.sizeWithUnits().height(), cls.ELEMENT_MIN_HEIGHT) + cls.SPACE_BETWEEN_ELEMENTS)

        ordered_plan_object_layers = [LandUseAreaLayer, OtherAreaLayer, LineLayer, PointLayer]
        for i, layer in enumerate(ordered_plan_object_layers):
            # Change column, set coordinates
            if i == 2 and cls.COLUMNS == 2:  # noqa: PLR2004
                y_coord = cls.START_Y
                x_coord = cls.COL_2_START_X

            heading_label = cls.add_object_type_heading(layer.name, layout, (x_coord, y_coord))
            y_coord = move_y_coordinate(y_coord, heading_label)

            for feat, symbol in PlanObjectIconRenderer.get_symbols_for_layer_features(layer.get_from_project()):
                if symbol is None:
                    # What to do if no symbol was found?
                    continue

                # Symbol must be cloned, otherwise QGIS crashes later when deferencing ref dropped by renderer
                cloned_symbol = symbol.clone()

                element = RegulationPrintElement.from_feat_and_symbol(feat, cloned_symbol)

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
