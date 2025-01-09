from importlib import resources
from typing import TYPE_CHECKING

from qgis.gui import QgsDockWidget
from qgis.PyQt import uic

from arho_feature_template.gui.components.new_feature_grid_widget import NewFeatureGridWidget

if TYPE_CHECKING:
    from qgis.gui import QgsFilterLineEdit
    from qgis.PyQt.QtWidgets import QComboBox, QLabel, QTreeView

ui_path = resources.files(__package__) / "template_dock.ui"
DockClass, _ = uic.loadUiType(ui_path)


class TemplateLibraryDock(QgsDockWidget, DockClass):  # type: ignore
    library_selection: "QComboBox"
    search_box: "QgsFilterLineEdit"
    # template_list: "QListView"
    template_list: "QTreeView"
    txt_tip: "QLabel"

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.new_feature_grid = NewFeatureGridWidget()
        self.dockWidgetContents.layout().insertWidget(1, self.new_feature_grid)

        self.search_box.setShowSearchIcon(True)

        # Update template tree when search text changes
        self.search_box.valueChanged.connect(self.on_template_search_text_changed)

    def on_template_search_text_changed(self, search_text: str) -> None:
        search_text = search_text.lower()
        template_model = self.template_list.model()

        for row in range(template_model.rowCount()):
            group_item = template_model.item(row)
            group_visible = False

            for child_row in range(group_item.rowCount()):
                child_item = group_item.child(child_row)

                if child_item.hasChildren():
                    subgroup_visible = False

                    for template_row in range(child_item.rowCount()):
                        template_item = child_item.child(template_row)
                        matches = search_text in template_item.text().lower()
                        template_item.setEnabled(matches)

                        if matches:
                            subgroup_visible = True

                    child_item.setEnabled(subgroup_visible)
                    group_visible = group_visible or subgroup_visible

                    index = template_model.indexFromItem(child_item)
                    self.template_list.setExpanded(index, subgroup_visible)

                else:
                    template_item = child_item
                    matches = search_text in template_item.text().lower()
                    template_item.setEnabled(matches)

                    if matches:
                        group_visible = True

            group_item.setEnabled(group_visible)

            index = template_model.indexFromItem(group_item)
            self.template_list.setExpanded(index, group_visible)
