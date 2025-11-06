from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from qgis.core import QgsApplication
from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtGui import QIcon, QPixmap
from qgis.PyQt.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QWidget

from arho_feature_template.core.models import PlanObject, Proposition, Regulation, RegulationGroup
from arho_feature_template.gui.components.plan_proposition_widget import PropositionWidget
from arho_feature_template.gui.components.plan_regulation_widget import RegulationWidget
from arho_feature_template.gui.dialogs.regulation_group_selection_view import RegulationGroupSelectionView
from arho_feature_template.project.layers.code_layers import PlanRegulationGroupTypeLayer
from arho_feature_template.project.layers.plan_layers import RegulationGroupAssociationLayer
from arho_feature_template.qgis_plugin_tools.tools.resources import resources_path
from arho_feature_template.utils.signal_utils import SignalDebouncer

if TYPE_CHECKING:
    from qgis.PyQt.QtWidgets import QFormLayout, QFrame, QLineEdit, QPushButton

ui_path = resources.files(__package__) / "plan_regulation_group_widget.ui"
FormClass, _ = uic.loadUiType(ui_path)


class RegulationGroupWidget(QWidget, FormClass):  # type: ignore
    """A widget representation of a plan regulation group."""

    open_as_form_signal = pyqtSignal(QWidget)
    delete_signal = pyqtSignal(QWidget)
    update_matching_groups = pyqtSignal(QWidget)

    def __init__(self, regulation_group: RegulationGroup, plan_feature: PlanObject | None = None):
        super().__init__()
        self.setupUi(self)

        # TYPES
        self.frame: QFrame
        self.heading: QLineEdit
        self.letter_code: QLineEdit
        self.link_btn: QPushButton
        self.edit_btn: QPushButton
        self.del_btn: QPushButton
        self.regulation_group_details_layout: QFormLayout

        # INIT
        self.frame.setObjectName("frame")  # Set unique name to avoid style cascading
        self.regulation_widgets: list[RegulationWidget] = []
        self.proposition_widgets: list[PropositionWidget] = []
        self.link_label_icon: QLabel | None = None
        self.link_label_text: QLabel | None = None

        self.plan_feature = plan_feature
        if self.plan_feature and self.plan_feature.layer_name:
            self.layer_name = self.plan_feature.layer_name
            regulation_group.type_code_id = PlanRegulationGroupTypeLayer.get_id_by_feature_layer_name(self.layer_name)

        self.matching_groups_in_db: list[RegulationGroup] = []
        self.from_model(regulation_group)

        self.link_btn.clicked.connect(self._on_link_btn_clicked)
        self.edit_btn.setIcon(QIcon(resources_path("icons", "settings.svg")))
        self.edit_btn.clicked.connect(lambda: self.open_as_form_signal.emit(self))
        self.del_btn.setIcon(QgsApplication.getThemeIcon("mActionDeleteSelected.svg"))
        self.del_btn.clicked.connect(lambda: self.delete_signal.emit(self))

        self.group_contents_update_debouncer = SignalDebouncer(delay_ms=300)
        self.group_contents_update_debouncer.triggered.connect(self._on_group_details_changed)
        self.heading.textEdited.connect(lambda _: self.group_contents_update_debouncer.restart_timer())
        self.letter_code.textEdited.connect(lambda _: self.group_contents_update_debouncer.restart_timer())

    def disable_linking(self):
        self.link_btn.hide()

    def setup_linking_to_matching_groups(self, matching_groups: list[RegulationGroup]):
        # This function should only be called if the regulation group is not in DB yet
        if self.regulation_group.id_ is not None:
            return

        self.link_btn.show()
        self.matching_groups_in_db = matching_groups
        nr_of_matching_groups = len(matching_groups)
        if nr_of_matching_groups == 0:
            self.link_btn.setEnabled(False)
            self.link_btn.setText(str(0))
            self.link_btn.setToolTip(
                "Yhdistämistä ei voi suorittaa, tietokannasta ei löydy vastaavia kaavamääräysryhmiä."
            )
        elif nr_of_matching_groups == 1:
            self.link_btn.setEnabled(True)
            self.link_btn.setText("")
            self.link_btn.setMaximumWidth(30)
            self.link_btn.setToolTip("Yhdistä kaavamääräysryhmä tietokannan vastaavaan kaavamääräysryhmään.")
        else:
            self.link_btn.setEnabled(True)
            self.link_btn.setText(f"{nr_of_matching_groups!s}!")
            self.link_btn.setToolTip(
                "Tietokannasta löytyy useita vastaavia kaavamääräysryhmiä, valitse yhdistettävä ryhmä."
            )
            # Determine width based on characters in the button text
            if nr_of_matching_groups < 10:  # noqa: PLR2004
                self.link_btn.setMaximumWidth(45)
            elif nr_of_matching_groups < 100:  # noqa: PLR2004
                self.link_btn.setMaximumWidth(52)
            else:
                self.link_btn.setMaximumWidth(60)

    def from_model(self, regulation_group: RegulationGroup):
        self.regulation_group = regulation_group

        self.heading.setText(regulation_group.heading if regulation_group.heading else "")
        self.letter_code.setText(regulation_group.letter_code if regulation_group.letter_code else "")

        # Remove existing child widgets if reinitializing
        for widget in self.regulation_widgets:
            self.delete_regulation_widget(widget)
        for widget in self.proposition_widgets:
            self.delete_proposition_widget(widget)
        for regulation in regulation_group.regulations:
            self.add_regulation_widget(regulation)
        for proposition in regulation_group.propositions:
            self.add_proposition_widget(proposition)

        # Remove existing indicators if reinitializing
        self.unset_existing_regulation_group_style()

        if regulation_group.id_ and self.plan_feature:
            if self.plan_feature.id_ is None:
                other_linked_features_count = len(
                    list(RegulationGroupAssociationLayer.get_associations_for_regulation_group(regulation_group.id_))
                )
            else:
                other_linked_features_count = len(
                    RegulationGroupAssociationLayer.get_associations_for_regulation_group_exclude_feature(
                        regulation_group.id_, self.plan_feature.id_, self.layer_name
                    )
                )
            self.set_existing_regulation_group_style(other_linked_features_count)

        else:
            self.update_matching_groups.emit(self)

    def add_regulation_widget(self, regulation: Regulation) -> RegulationWidget:
        widget = RegulationWidget(regulation=regulation, parent=self.frame)
        widget.changed.connect(lambda: self.group_contents_update_debouncer.restart_timer())
        widget.delete_signal.connect(self.delete_regulation_widget)
        self.frame.layout().addWidget(widget)
        self.regulation_widgets.append(widget)
        return widget

    def delete_regulation_widget(self, regulation_widget: RegulationWidget):
        self.frame.layout().removeWidget(regulation_widget)
        self.regulation_widgets.remove(regulation_widget)
        regulation_widget.deleteLater()
        self.group_contents_update_debouncer.restart_timer()

    def add_proposition_widget(self, proposition: Proposition) -> PropositionWidget:
        widget = PropositionWidget(proposition=proposition, parent=self.frame)
        widget.changed.connect(lambda: self.group_contents_update_debouncer.restart_timer())
        widget.delete_signal.connect(self.delete_proposition_widget)
        self.frame.layout().addWidget(widget)
        self.proposition_widgets.append(widget)
        return widget

    def delete_proposition_widget(self, proposition_widget: RegulationWidget):
        self.frame.layout().removeWidget(proposition_widget)
        self.proposition_widgets.remove(proposition_widget)
        proposition_widget.deleteLater()
        self.group_contents_update_debouncer.restart_timer()

    def set_existing_regulation_group_style(self, other_linked_features_count: int):
        # Always use blue frame if regulation group is in DB
        self.setStyleSheet("#frame { border: 2px solid #4b8db2; }")

        # Link button should show delink image
        self.link_btn.setIcon(QIcon(resources_path("icons", "delinked_img.png")))
        self.link_btn.setText("")

        # Case group exists in DB but no other plan object uses it
        if other_linked_features_count == 0:
            self.link_btn.setEnabled(False)
            self.link_btn.setToolTip("Ei purettavia linkkejä, kaavamääräysryhmää ei ole annettu muille kaavakohteelle.")
            # Return early, don't add other existing group indicators if not linked to other plan objects
            return

        # Case group exists in DB and N other plan object use it too
        self.link_btn.setEnabled(True)
        self.link_btn.setToolTip("Tee kaavamääräysryhmästä uniikki / pura linkitys muihin kaavakohteisiin.")

        tooltip = (
            "Kaavamääräysryhmä on tallennettu kaavasuunnitelmaan. Ryhmän tietojen muokkaaminen vaikuttaa muihin "
            "kaavakohteisiin, joille ryhmä on lisätty."
        )
        layout = QHBoxLayout()

        self.link_label_icon = QLabel()
        self.link_label_icon.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.link_label_icon.setPixmap(QPixmap(resources_path("icons", "linked_img_small.png")))
        self.link_label_icon.setToolTip(tooltip)
        layout.addWidget(self.link_label_icon)

        self.link_label_text = QLabel()
        self.link_label_text.setObjectName("text_label")  # Set unique name to avoid style cascading
        self.link_label_text.setText(
            f"Kaavamääräysryhmä on käytössä myös {other_linked_features_count} toisella kaavakohteella"
        )
        self.link_label_text.setWordWrap(True)
        self.link_label_text.setStyleSheet("#text_label { color: #4b8db2; }")
        self.link_label_text.setToolTip(tooltip)
        layout.addWidget(self.link_label_text)

        self.frame.layout().insertLayout(1, layout)

    def unset_existing_regulation_group_style(self):
        if self.link_label_icon:
            self.link_label_icon.deleteLater()
            self.link_label_icon = None

        if self.link_label_text:
            self.link_label_text.deleteLater()
            self.link_label_text = None

        self.setStyleSheet("")
        self.link_btn.setIcon(QIcon(resources_path("icons", "linked_img.png")))

    def _on_link_btn_clicked(self):
        # Group with ID, delink
        if self.regulation_group.id_ is not None:
            delinked_group = self.into_model()
            delinked_group.id_ = None
            self.from_model(delinked_group)

        # Group without ID, link with a matching group in DB
        # Only 1 option, immediately perform linking / replacing
        elif len(self.matching_groups_in_db) == 1:
            group = self.matching_groups_in_db[0]
            self.from_model(group)
        # Multiple choices, make user choose which group to use
        elif len(self.matching_groups_in_db) > 1:
            dialog = RegulationGroupSelectionView(self.matching_groups_in_db)
            if dialog.exec():
                self.from_model(dialog.get_selected_group())

    def _on_group_details_changed(self):
        # Only ask for update if group is new / not in DB
        if self.regulation_group.id_ is None:
            self.update_matching_groups.emit(self)

    def into_model(self) -> RegulationGroup:
        model = RegulationGroup(
            type_code_id=self.regulation_group.type_code_id,
            heading=self.heading.text(),
            letter_code=self.letter_code.text(),
            color_code=self.regulation_group.color_code,
            regulations=[widget.into_model() for widget in self.regulation_widgets],
            propositions=[widget.into_model() for widget in self.proposition_widgets],
            modified=self.regulation_group.modified,
            id_=self.regulation_group.id_,
        )
        if not model.modified and model != self.regulation_group:
            model.modified = True

        return model
