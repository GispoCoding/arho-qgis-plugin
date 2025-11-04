from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QListWidget

ui_path = resources.files(__package__) / "regulation_group_selection_view.ui"
FormClass, _ = uic.loadUiType(ui_path)

if TYPE_CHECKING:
    from arho_feature_template.core.models import RegulationGroup


class RegulationGroupSelectionView(QDialog, FormClass):  # type: ignore
    def __init__(self, regulation_groups: list[RegulationGroup]):
        super().__init__()
        self.setupUi(self)

        # TYPES
        self.regulation_groups_list: QListWidget

        self.regulation_groups = regulation_groups
        for regulation_group in regulation_groups:
            self.regulation_groups_list.addItem(str(regulation_group.id_))
        self.regulation_groups_list.setCurrentRow(0)

    def get_selected_group(self) -> RegulationGroup:
        return self.regulation_groups[self.regulation_groups_list.currentRow()]
