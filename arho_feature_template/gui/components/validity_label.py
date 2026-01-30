from qgis.PyQt.QtCore import QSize, Qt
from qgis.PyQt.QtGui import QIcon, QPixmap, QStandardItem
from qgis.PyQt.QtWidgets import QLabel, QSizePolicy

from arho_feature_template.core.models import PlanBaseModel
from arho_feature_template.project.layers.code_layers import LifeCycleStatusLayer
from arho_feature_template.qgis_plugin_tools.tools.resources import resources_path
from arho_feature_template.utils.misc_utils import date_as_str

VALIDITY_SORT_ROLE = Qt.UserRole


class ValidityLabel(QLabel):
    VALID_MARK = QPixmap(resources_path("icons", "valid_mark2.png"))
    REPEALED_MARK = QPixmap(resources_path("icons", "repealed_mark.png"))

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMaximumSize(23, 23)
        self.setScaledContents(True)

    def set_from_model(self, model: PlanBaseModel) -> None:
        if not hasattr(model, "lifecycle_status_id"):
            self.hide_widget()
            return

        if LifeCycleStatusLayer.is_repealed_status(model.lifecycle_status_id):
            self.setPixmap(self.REPEALED_MARK)

            if model.period_of_validity_start is not None and model.period_of_validity_end is not None:  # type: ignore
                self.setToolTip(
                    "KUMOTTU\n"  # noqa: ISC003
                    + f"Voimassa {date_as_str(model.period_of_validity_start)} - "  # type: ignore
                    + date_as_str(model.period_of_validity_end)  # type: ignore
                )
            elif model.period_of_validity_end is not None:  # type: ignore
                self.setToolTip(f"KUMOTTU\nKumottu alkaen: {date_as_str(model.period_of_validity_end)}")  # type: ignore
            else:
                self.setToolTip("KUMOTTU")

        elif LifeCycleStatusLayer.is_valid_status(model.lifecycle_status_id):
            self.setPixmap(self.VALID_MARK)
            self.setToolTip(f"VOIMASSA\nVoimassa alkaen: {date_as_str(model.period_of_validity_start)}")  # type: ignore

        else:
            self.hide_widget()

    def hide_widget(self):
        self.setToolTip("")
        self.hide()


def validity_item_from_model(model: PlanBaseModel) -> QStandardItem:
    """
    Create a QStandardItem with valid icon, repealed icon or no icon depending on model status.

    Items are meant to be used in PlanObjectDock table.

    Each item has a validity number for sorting stored in `VALIDITY_SORT_ROLE`.
    0 = valid, 1 = repealed, 0 = undefined.
    """
    item = QStandardItem("")
    item.setEditable(False)

    item.setData(QSize(23, 23), Qt.SizeHintRole)

    if not hasattr(model, "lifecycle_status_id"):
        item.setData(2, VALIDITY_SORT_ROLE)
        return item

    if LifeCycleStatusLayer.is_repealed_status(model.lifecycle_status_id):
        item.setData(QIcon(ValidityLabel.REPEALED_MARK), Qt.DecorationRole)

        if model.period_of_validity_start and model.period_of_validity_end:  # type: ignore
            tooltip = (
                "KUMOTTU\n"
                f"Voimassa {date_as_str(model.period_of_validity_start)} - "  # type: ignore
                f"{date_as_str(model.period_of_validity_end)}"  # type: ignore
            )
        elif model.period_of_validity_end:  # type: ignore
            tooltip = f"KUMOTTU\nKumottu alkaen: {date_as_str(model.period_of_validity_end)}"  # type: ignore
        else:
            tooltip = "KUMOTTU"

        item.setData(1, VALIDITY_SORT_ROLE)
        item.setData(tooltip, Qt.ToolTipRole)

    elif LifeCycleStatusLayer.is_valid_status(model.lifecycle_status_id):
        item.setData(QIcon(ValidityLabel.VALID_MARK), Qt.DecorationRole)
        item.setData(f"VOIMASSA\nVoimassa alkaen: {date_as_str(model.period_of_validity_start)}", Qt.ToolTipRole)  # type: ignore
        item.setData(0, VALIDITY_SORT_ROLE)

    return item
