from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QMenu, QMessageBox, QPushButton

from arho_feature_template.core.models import PlanObject
from arho_feature_template.core.template_manager import TemplateManager
from arho_feature_template.gui.components.regulation_groups_view import RegulationGroupsView
from arho_feature_template.project.layers.code_layers import (
    UndergroundTypeLayer,
)
from arho_feature_template.utils.localization_utils import get_localized_text
from arho_feature_template.utils.misc_utils import date_as_str

if TYPE_CHECKING:
    from qgis.PyQt.QtWidgets import QLineEdit

    from arho_feature_template.core.models import PlanFeatureLibrary, RegulationGroupLibrary
    from arho_feature_template.gui.components.code_combobox import CodeComboBox
    from arho_feature_template.gui.components.value_input_widgets import (
        LocalizedMultilineTextInputWidget,
        LocalizedSinglelineTextInputWidget,
    )

ui_path = resources.files(__package__) / "plan_feature_form.ui"
FormClass, _ = uic.loadUiType(ui_path)


class PlanObjectForm(QDialog, FormClass):  # type: ignore
    """Parent class for feature forms for adding and modifying feature attribute data."""

    def __init__(
        self,
        plan_feature: PlanObject,
        form_title: str,
        regulation_group_libraries: list[RegulationGroupLibrary],
        plan_feature_libraries: list[PlanFeatureLibrary] | None = None,
        active_plan_regulation_groups_library: RegulationGroupLibrary | None = None,
        template_form: bool = False,  # noqa: FBT001, FBT002
    ):
        super().__init__()
        self.setupUi(self)

        # TYPES
        self.feature_name: LocalizedSinglelineTextInputWidget
        self.feature_description: LocalizedMultilineTextInputWidget
        self.feature_type_of_underground: CodeComboBox
        self.validity_start_date: QLineEdit

        self.save_to_library_button: QPushButton
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

        # If editing, show previously saved value, otherwise show 'Maanpäällinen'
        type_of_underground_id = plan_feature.type_of_underground_id
        if type_of_underground_id:
            type_of_underground = get_localized_text(
                UndergroundTypeLayer.get_attribute_by_id("name", type_of_underground_id)
            )
            self.feature_type_of_underground.setCurrentText(type_of_underground)
        else:
            self.feature_type_of_underground.setCurrentIndex(1)  # Maanpäällinen

        # Initialize attributes from template
        self.plan_feature = plan_feature

        self.feature_name.set_value(plan_feature.name)
        self.feature_description.set_value(plan_feature.description)
        for regulation_group in plan_feature.regulation_groups:
            self.regulation_groups_view.add_plan_regulation_group(regulation_group)
        self.validity_start_date.setText(date_as_str(plan_feature.period_of_validity_start))

        self.plan_feature_libraries = plan_feature_libraries
        self._init_save_to_library_button()

        self.button_box.accepted.connect(self._on_ok_clicked)

    def _init_save_to_library_button(self) -> None:
        if self.plan_feature_libraries:
            self.plan_object_menu = QMenu()
            plan_object_libraries = self.plan_feature_libraries
            if not plan_object_libraries:
                self.save_to_library_button.setEnabled(False)
            else:
                for library in plan_object_libraries:
                    self.plan_object_menu.addAction(
                        library.name,
                        lambda library=library: TemplateManager.save_plan_object_to_library(self.into_model(), library),
                    )
                self.save_to_library_button.setMenu(self.plan_object_menu)

    def _check_feature_name(self) -> bool:
        """Feature must have a name if we are saving a plan feature template."""
        # TODO: Find a better way to detect if we are saving a plan feature template
        if self.template_form and not self.feature_name.get_value():
            msg = "Kaavakohdepohjalla täytyy olla nimi."
            QMessageBox.critical(self, "Virhe", msg)
            return False
        return True

    def into_model(self) -> PlanObject:
        model = PlanObject(
            name=self.feature_name.get_value(),
            type_of_underground_id=self.feature_type_of_underground.value(),
            description=self.feature_description.get_value(),
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
