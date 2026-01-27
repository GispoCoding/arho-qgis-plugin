from qgis.PyQt.QtGui import QPixmap
from qgis.PyQt.QtWidgets import QLabel, QSizePolicy

from arho_feature_template.core.models import PlanBaseModel
from arho_feature_template.qgis_plugin_tools.tools.resources import resources_path
from arho_feature_template.utils.misc_utils import date_as_str


class ValidityLabel(QLabel):
    VALID_MARK = QPixmap(resources_path("icons", "valid_mark2.png"))
    REPEALED_MARK = QPixmap(resources_path("icons", "repealed_mark.png"))

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMaximumSize(23, 23)
        self.setScaledContents(True)

    def set_from_model(self, model: PlanBaseModel) -> None:
        if hasattr(model, "period_of_validity_end") and model.period_of_validity_end is not None:
            self.setPixmap(self.REPEALED_MARK)

            if hasattr(model, "period_of_validity_start") and model.period_of_validity_start is not None:
                self.setToolTip(
                    "KUMOTTU\n"  # noqa: ISC003
                    + f"Voimassa {date_as_str(model.period_of_validity_start)} - "
                    + date_as_str(model.period_of_validity_end)
                )
            # Should this ever happen?
            else:
                self.setToolTip(f"KUMOTTU\nKumottu alkaen: {date_as_str(model.period_of_validity_end)}")

        elif hasattr(model, "period_of_validity_start") and model.period_of_validity_start is not None:
            self.setPixmap(self.VALID_MARK)
            self.setToolTip(f"VOIMASSA\nVoimassa alkaen: {date_as_str(model.period_of_validity_start)}")

        else:
            self.setToolTip("")
            self.hide()
