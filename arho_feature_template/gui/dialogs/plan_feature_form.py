from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLineEdit,
    QMessageBox,
    QTextEdit,
)

from arho_feature_template.core.models import PlanObject
from arho_feature_template.gui.components.regulation_groups_view import RegulationGroupsView
from arho_feature_template.project.layers.code_layers import (
    UndergroundTypeLayer,
)

if TYPE_CHECKING:
    from arho_feature_template.core.models import RegulationGroupLibrary
    from arho_feature_template.gui.components.code_combobox import CodeComboBox

ui_path = resources.files(__package__) / "plan_feature_form.ui"
FormClass, _ = uic.loadUiType(ui_path)


class PlanObjectForm(QDialog, FormClass):  # type: ignore
    """Parent class for feature forms for adding and modifying feature attribute data."""

    def __init__(
        self,
        plan_feature: PlanObject,
        form_title: str,
        regulation_group_libraries: list[RegulationGroupLibrary],
        active_plan_regulation_groups_library: RegulationGroupLibrary | None = None,
        template_form: bool = False,  # noqa: FBT001, FBT002
    ):
        super().__init__()
        self.setupUi(self)

        # TYPES
        self.feature_name: QLineEdit
        self.feature_description: QTextEdit
        self.feature_type_of_underground: CodeComboBox

        self.button_box: QDialogButtonBox

        # INIT
        self.regulation_groups_view = RegulationGroupsView(
            regulation_group_libraries, active_plan_regulation_groups_library, plan_feature
        )
        self.layout().insertWidget(1, self.regulation_groups_view)

        self.template_form = template_form
        self.setWindowTitle(form_title)

        self.feature_type_of_underground.populate_from_code_layer(UndergroundTypeLayer)
        self.feature_type_of_underground.remove_item_by_text("NULL")
        self.feature_type_of_underground.setCurrentIndex(1)  # Set default to Maanpäällinen (index 1)

        # Initialize attributes from template
        self.plan_feature = plan_feature

        if plan_feature.name:
            self.feature_name.setText(plan_feature.name)
        if plan_feature.description:
            self.feature_description.setText(plan_feature.description)
        for regulation_group in plan_feature.regulation_groups:
            self.regulation_groups_view.add_plan_regulation_group(regulation_group)

        self.button_box.accepted.connect(self._on_ok_clicked)

    def _check_feature_name(self) -> bool:
        """Feature must have a name if we are saving a plan feature template."""
        # TODO: Find a better way to detect if we are saving a plan feature template
        if self.template_form and self.feature_name.text() == "":
            msg = "Kaavakohdepohjalla täytyy olla nimi."
            QMessageBox.critical(self, "Virhe", msg)
            return False
        return True

    def into_model(self) -> PlanObject:
        model = PlanObject(
            name=self.feature_name.text() if self.feature_name.text() != "" else None,
            type_of_underground_id=self.feature_type_of_underground.value(),
            description=self.feature_description.toPlainText()
            if self.feature_description.toPlainText() != ""
            else None,
            geom=self.plan_feature.geom,
            layer_name=self.plan_feature.layer_name,
            regulation_groups=self.regulation_groups_view.into_model(),
            plan_id=self.plan_feature.plan_id,
            id_=self.plan_feature.id_,
            modified=self.plan_feature.modified,
        )
        if not model.modified and model != self.plan_feature:
            model.modified = True

        return model

    def _on_ok_clicked(self):
        if (
            self.regulation_groups_view.check_multiple_regulation_groups_with_principal_intended_use_regulations()
            and self._check_feature_name()
        ):
            self.model = self.into_model()
            self.accept()
