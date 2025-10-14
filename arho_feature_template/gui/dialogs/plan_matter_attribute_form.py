from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QLineEdit, QTextEdit

from arho_feature_template.core.models import PlanMatter
from arho_feature_template.project.layers.code_layers import OrganisationLayer, PlanTypeLayer

if TYPE_CHECKING:
    from arho_feature_template.gui.components.code_combobox import CodeComboBox, HierarchicalCodeComboBox


# Load UI
ui_path = resources.files(__package__) / "plan_matter_attribute_form.ui"
FormClass, _ = uic.loadUiType(ui_path)


class PlanMatterAttributeForm(QDialog, FormClass):  # type: ignore
    permanent_identifier_edit: QLineEdit
    name_edit: QLineEdit
    description_edit: QTextEdit
    organisation_combo_box: CodeComboBox
    plan_type_combo_box: HierarchicalCodeComboBox
    record_number_edit: QLineEdit
    producers_id_edit: QLineEdit
    case_id_edit: QLineEdit

    button_box: QDialogButtonBox

    def __init__(self, plan_matter: PlanMatter, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.plan_matter = plan_matter

        # --- Populate comboboxes from code layers ---
        self.organisation_combo_box.populate_from_code_layer(OrganisationLayer)
        self.plan_type_combo_box.populate_from_code_layer(PlanTypeLayer)

        # --- Load model values into form ---
        self._load_model_into_form()

        # --- Hook up events ---
        self.name_edit.textChanged.connect(self._check_required_fields)
        self.organisation_combo_box.currentIndexChanged.connect(self._check_required_fields)
        self.plan_type_combo_box.currentIndexChanged.connect(self._check_required_fields)

        # Disable OK until required fields are valid
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
        self.button_box.accepted.connect(self._on_ok_clicked)

        # Initial validation
        self._check_required_fields()

    def _load_model_into_form(self) -> None:
        """Fill the form fields from the PlanMatter model."""
        self.permanent_identifier_edit.setText(self.plan_matter.permanent_plan_identifier or "")
        self.name_edit.setText(self.plan_matter.name or "")
        self.description_edit.setText(self.plan_matter.description or "")
        self.case_id_edit.setText(self.plan_matter.case_identifier or "")
        self.record_number_edit.setText(self.plan_matter.record_number or "")
        self.producers_id_edit.setText(self.plan_matter.producers_plan_identifier or "")

        self.organisation_combo_box.set_value(self.plan_matter.organisation_id)
        self.plan_type_combo_box.set_value(self.plan_matter.plan_type_id)

    def _check_required_fields(self) -> None:
        ok_button = self.button_box.button(QDialogButtonBox.Ok)
        if (
            self.name_edit.text() != ""
            and self.plan_type_combo_box.value() is not None
            and self.organisation_combo_box.value() is not None
        ):
            ok_button.setEnabled(True)
        else:
            ok_button.setEnabled(False)

    def _on_ok_clicked(self) -> None:
        self.model = self.into_model()
        self.accept()

    def into_model(self) -> PlanMatter:
        """Return an updated PlanMatter model based on the form data."""
        model = PlanMatter(
            id_=self.plan_matter.id_,
            name=self.name_edit.text(),
            description=self.description_edit.toPlainText() or None,
            organisation_id=self.organisation_combo_box.value(),
            plan_type_id=self.plan_type_combo_box.value(),
            permanent_plan_identifier=self.permanent_identifier_edit.text() or None,
            case_identifier=self.case_id_edit.text() or None,
            record_number=self.record_number_edit.text() or None,
            producers_plan_identifier=self.producers_id_edit.text() or None,
            modified=self.plan_matter.modified,
        )

        if not model.modified and model != self.plan_matter:
            model.modified = True

        return model
