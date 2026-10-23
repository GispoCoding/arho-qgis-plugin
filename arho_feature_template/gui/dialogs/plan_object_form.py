from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QMenu, QMessageBox, QPushButton, QWidget

from arho_feature_template.core.models import PlanObject
from arho_feature_template.core.template_manager import TemplateManager
from arho_feature_template.gui.components.regulation_groups_view import RegulationGroupsView
from arho_feature_template.project.layers.code_layers import (
    UndergroundTypeLayer,
)
from arho_feature_template.utils.localization_utils import get_localized_text
from arho_feature_template.utils.misc_utils import date_as_str

if TYPE_CHECKING:
    from qgis.gui import QgsCollapsibleGroupBox
    from qgis.PyQt.QtWidgets import QLabel, QLineEdit

    from arho_feature_template.core.models import PlanObjectLibrary, RegulationGroupLibrary
    from arho_feature_template.gui.components.code_combobox import CodeComboBox
    from arho_feature_template.gui.components.value_input_widgets import (
        LocalizedMultilineTextInputWidget,
        LocalizedSinglelineTextInputWidget,
    )

ui_path = resources.files(__package__) / "plan_object_form.ui"
FormClass, _ = uic.loadUiType(ui_path)

PLAN_LOCKED_MESSAGE = "Kaavasuunnitelma on lukittu, kaavakohdetta ei voi muokata."
VALID_PLAN_OBJECT_READ_ONLY_MESSAGE = "Ajantasakaavan kaavakohdetta ei voi muokata."


class PlanObjectForm(QDialog, FormClass):  # type: ignore
    """Parent class for feature forms for adding and modifying feature attribute data.

    `save_disabled_reason` disables the OK button and shows the reason as its tooltip.
    """

    def __init__(
        self,
        plan_object: PlanObject,
        form_title: str,
        regulation_group_libraries: list[RegulationGroupLibrary],
        plan_object_libraries: list[PlanObjectLibrary] | None = None,
        active_plan_regulation_groups_library: RegulationGroupLibrary | None = None,
        save_disabled_reason: str | None = None,
        template_form: bool = False,  # noqa: FBT001, FBT002
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.setupUi(self)

        # TYPES
        self.plan_object_groupbox: QgsCollapsibleGroupBox
        self.plan_object_name: LocalizedSinglelineTextInputWidget
        self.plan_object_description: LocalizedMultilineTextInputWidget
        self.type_of_underground_selection: CodeComboBox
        self.validity_start_label: QLabel
        self.validity_start_date: QLineEdit
        self.validity_end_label: QLabel
        self.validity_end_date: QLineEdit
        self.save_to_library_button: QPushButton
        self.button_box: QDialogButtonBox

        # INIT
        self.regulation_groups_view = RegulationGroupsView(
            regulation_group_libraries, active_plan_regulation_groups_library, plan_object
        )
        self.layout().insertWidget(1, self.regulation_groups_view)

        self.template_form = template_form
        self.setWindowTitle(form_title)

        self.type_of_underground_selection.populate_from_code_layer(UndergroundTypeLayer)
        self.type_of_underground_selection.remove_item_by_text("NULL")

        # If editing, show previously saved value, otherwise show 'Maanpäällinen'
        type_of_underground_id = plan_object.type_of_underground_id
        if type_of_underground_id:
            type_of_underground = get_localized_text(
                UndergroundTypeLayer.get_attribute_by_id("name", type_of_underground_id)
            )
            self.type_of_underground_selection.setCurrentText(type_of_underground)
        else:
            self.type_of_underground_selection.setCurrentIndex(1)  # Maanpäällinen

        # Initialize attributes from template
        self.plan_object = plan_object

        self.plan_object_name.set_value(plan_object.name)
        self.plan_object_description.set_value(plan_object.description)
        self.regulation_groups_view.add_stored_plan_regulation_groups(plan_object.regulation_groups)

        # Validity start
        if plan_object.period_of_validity_start:
            self.validity_start_date.setText(date_as_str(plan_object.period_of_validity_start))
        else:
            self.plan_object_groupbox.layout().removeRow(self.validity_start_label)

        # Validity end
        if plan_object.period_of_validity_end:
            self.validity_end_date.setText(date_as_str(plan_object.period_of_validity_end))
        else:
            self.plan_object_groupbox.layout().removeRow(self.validity_end_label)

        self.plan_object_libraries = plan_object_libraries
        self._init_save_to_library_button()

        self.button_box.accepted.connect(self._on_ok_clicked)

        if save_disabled_reason is not None:
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setToolTip(save_disabled_reason)

    def _init_save_to_library_button(self) -> None:
        if self.plan_object_libraries:
            self.plan_object_menu = QMenu(self.save_to_library_button)
            plan_object_libraries = self.plan_object_libraries
            if not plan_object_libraries:
                self.save_to_library_button.setEnabled(False)
            else:
                for library in plan_object_libraries:
                    self.plan_object_menu.addAction(
                        library.name,
                        lambda library=library: TemplateManager.save_plan_object_to_library(self.into_model(), library),
                    )
                self.save_to_library_button.setMenu(self.plan_object_menu)

    def _check_plan_object_name(self) -> bool:
        """Feature must have a name if we are saving a plan object template."""
        # TODO: Find a better way to detect if we are saving a plan object template
        if self.template_form and not self.plan_object_name.get_value():
            msg = "Kaavakohdepohjalla täytyy olla nimi."
            QMessageBox.critical(self, "Virhe", msg)
            return False
        return True

    def into_model(self) -> PlanObject:
        model = PlanObject(
            name=self.plan_object_name.get_value(),
            type_of_underground_id=self.type_of_underground_selection.value(),
            description=self.plan_object_description.get_value(),
            lifecycle_status_id=self.plan_object.lifecycle_status_id,
            period_of_validity_start=self.plan_object.period_of_validity_start,
            period_of_validity_end=self.plan_object.period_of_validity_end,
            geom=self.plan_object.geom,
            layer_name=self.plan_object.layer_name,
            regulation_groups=self.regulation_groups_view.into_model(),
            plan_id=self.plan_object.plan_id,
            id_=self.plan_object.id_,
            stored=self.plan_object.stored,
            modified=self.plan_object.modified,
        )
        if not model.modified and model != self.plan_object:
            model.modified = True

        return model

    def _on_ok_clicked(self):
        if (
            self.regulation_groups_view.check_multiple_regulation_groups_with_principal_intended_use_regulations()
            and self._check_plan_object_name()
        ):
            self.model = self.into_model()
            self.accept()
