from __future__ import annotations

import logging
from typing import ClassVar

from qgis.core import QgsApplication
from qgis.gui import QgsDoubleSpinBox, QgsSpinBox
from qgis.PyQt.QtCore import QObject, pyqtSignal
from qgis.PyQt.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QWidget,
)

from arho_feature_template.core.models import AttributeValue, AttributeValueDataType, LocalizedText
from arho_feature_template.core.settings_manager import SettingsManager
from arho_feature_template.gui.components.code_combobox import CodeComboBox, HierarchicalCodeComboBox
from arho_feature_template.project.layers.code_layers import (
    LegalEffectsLayer,
    VerbalRegulationType,
    get_code_layer_by_uri,
)

logger = logging.getLogger(__name__)


def initialize_numeric_input_widget(
    widget: QgsSpinBox | QgsDoubleSpinBox,
    default_value: float | None,
    unit: str | None,
    positive: bool,  # noqa: FBT001
):
    if unit:
        widget.setSuffix(f" {unit}")

    if positive:
        widget.setMinimum(0)
    else:
        widget.setMinimum(-999999999)

    if unit == "%":
        widget.setMaximum(100)
    else:
        widget.setMaximum(999999999)

    if default_value:
        widget.setValue(default_value)

    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)


def initialize_text_input_widget(
    widget: QTextEdit | QLineEdit,
    default_value: str | None,
    editable: bool,  # noqa: FBT001
):
    if default_value:
        widget.setText(default_value)

    if not editable:
        widget.setReadOnly(True)


class DecimalInputWidget(QgsDoubleSpinBox):
    changed = pyqtSignal()

    def __init__(
        self,
        default_value: float | None = None,
        unit: str | None = None,
        positive: bool = False,  # noqa: FBT001, FBT002
    ):
        super().__init__()
        self.unit = unit
        initialize_numeric_input_widget(self, default_value, unit, positive)

        self.valueChanged.connect(lambda _: self.changed.emit())

    def get_value(self) -> float:
        return self.value()


class IntegerInputWidget(QgsSpinBox):
    changed = pyqtSignal()

    def __init__(
        self,
        default_value: int | None = None,
        unit: str | None = None,
        positive: bool = False,  # noqa: FBT001, FBT002
    ):
        super().__init__()
        self.unit = unit
        initialize_numeric_input_widget(self, default_value, unit, positive)

        self.valueChanged.connect(lambda _: self.changed.emit())

    def get_value(self) -> int:
        return self.value()


class IntegerRangeInputWidget(QWidget):
    changed = pyqtSignal()

    def __init__(
        self,
        range_min: int | None = None,
        range_max: int | None = None,
        unit: str | None = None,
        positive: bool = False,  # noqa: FBT001, FBT002
    ):
        super().__init__()

        self.min_widget = IntegerInputWidget(range_min, unit, positive)
        self.max_widget = IntegerInputWidget(range_max, unit, positive)
        layout = QHBoxLayout()
        layout.addWidget(self.min_widget)
        layout.addWidget(QLabel("-"))
        layout.addWidget(self.max_widget)
        self.setLayout(layout)

        self.min_widget.changed.connect(lambda: self.changed.emit())
        self.max_widget.changed.connect(lambda: self.changed.emit())

    def get_value(self) -> tuple[int, int]:
        return (self.min_widget.get_value(), self.max_widget.get_value())


class SinglelineTextInputWidget(QLineEdit):
    changed = pyqtSignal()

    def __init__(
        self,
        default_value: str | None = None,
        editable: bool = False,  # noqa: FBT001, FBT002
    ):
        super().__init__()
        initialize_text_input_widget(self, default_value, editable)

        self.textChanged.connect(lambda _: self.changed.emit())

    def get_value(self) -> str | None:
        return self.text() if self.text() else None


class MultilineTextInputWidget(QTextEdit):
    changed = pyqtSignal()

    def __init__(
        self,
        default_value: str | None = None,
        editable: bool = True,  # noqa: FBT001, FBT002
    ):
        super().__init__()
        initialize_text_input_widget(self, default_value, editable)
        self.setMaximumHeight(75)

        self.textChanged.connect(lambda: self.changed.emit())

    def get_value(self) -> str | None:
        text = self.toPlainText()
        return text if text else None


class LocalizedTextInputWidget(QWidget):
    WIDGET_CLS: type[SinglelineTextInputWidget | MultilineTextInputWidget] | None = None

    changed = pyqtSignal()

    TRIM_EMPTY_VALUES: ClassVar[bool] = True
    HIDE_LABEL_WHEN_SHOW_PRIMARY_LANGUAGE_ONLY: ClassVar[bool] = True

    def __init__(self, editable: bool = True):  # noqa: FBT001, FBT002
        super().__init__()

        self.editable = editable
        self.show_primary_language_only = SettingsManager.get_show_only_primary_language()

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        layout = QFormLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # widgets by language code
        self.input_widgets: dict[str, SinglelineTextInputWidget | MultilineTextInputWidget] = {}

        if self.show_primary_language_only:
            self.initialize_for_languages([SettingsManager.get_primary_language()])
        else:
            self.initialize_for_languages(SettingsManager.get_languages())

    def set_editable(self, editable: bool):  # noqa: FBT001
        self.editable = editable
        for widget in self.input_widgets.values():
            widget.setReadOnly(not editable)

    def _add_widget_for_language(self, language_code: str):
        if self.WIDGET_CLS is None:
            raise NotImplementedError

        widget = self.WIDGET_CLS(None, self.editable)  # Initialize input field as empty
        widget.changed.connect(self.changed)

        # TODO: Language rather than language code?
        if self.HIDE_LABEL_WHEN_SHOW_PRIMARY_LANGUAGE_ONLY and self.show_primary_language_only:
            self.layout().addRow("", widget)
            self.layout().setSpacing(0)  # If spacing is not 0, there is a small empty space in place of label
        else:
            self.layout().addRow(language_code, widget)
        self.input_widgets[language_code] = widget

    def initialize_for_languages(self, language_codes: list[str]):
        for language_code in language_codes:
            self._add_widget_for_language(language_code)

    def set_value(
        self,
        values_dict: LocalizedText | None,
        add_missing_widgets: bool = True,  # noqa: FBT001, FBT002
    ):
        if not values_dict:
            return
        for language_code, value in values_dict.items():
            if language_code in self.input_widgets:
                self.input_widgets[language_code].setText(value)
            # Don't add empty fields here, only in initialization phase
            elif not self.show_primary_language_only and add_missing_widgets and value not in ["", None]:
                self._add_widget_for_language(language_code)
                self.input_widgets[language_code].setText(value)
            else:
                # Value exists for a language but widget is not created
                pass

    def set_value_for_language_code(
        self,
        language_code: str,
        value: str,
        add_missing_widgets: bool = True,  # noqa: FBT001, FBT002
    ):
        if language_code not in self.input_widgets:
            if add_missing_widgets:
                self._add_widget_for_language(language_code)
            else:
                return
        self.input_widgets[language_code].setText(value)

    def get_value(self) -> LocalizedText | None:
        result: LocalizedText = {}
        for language_code, widget in self.input_widgets.items():
            value = widget.get_value()
            if self.TRIM_EMPTY_VALUES and value in ["", None]:
                continue

            result[language_code] = value or ""

        return result or None

    def get_value_for_language_code(self, language_code: str) -> str | None:
        widget = self.input_widgets.get(language_code)
        return widget.get_value() if widget else None


class LocalizedSinglelineTextInputWidget(LocalizedTextInputWidget):
    WIDGET_CLS = SinglelineTextInputWidget


class LocalizedMultilineTextInputWidget(LocalizedTextInputWidget):
    WIDGET_CLS = MultilineTextInputWidget


class TypeOfVerbalRegulationWidget(QWidget):
    changed = pyqtSignal()

    def __init__(
        self,
        with_add_btn: bool = False,  # noqa: FBT001, FBT002
        with_del_btn: bool = False,  # noqa: FBT001, FBT002
        parent=None,
    ):
        super().__init__(parent)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.input_widget = HierarchicalCodeComboBox()
        self.input_widget.populate_from_code_layer(VerbalRegulationType)
        layout.addWidget(self.input_widget)

        self.add_btn: QPushButton | None = None
        if with_add_btn:
            self.add_btn = QPushButton()
            self.add_btn.setMaximumWidth(30)
            self.add_btn.setIcon(QgsApplication.getThemeIcon("mActionAdd.svg"))
            layout.addWidget(self.add_btn)

        self.del_btn: QPushButton | None = None
        if with_del_btn:
            self.del_btn = QPushButton()
            self.del_btn.setMaximumWidth(30)
            self.del_btn.setIcon(QgsApplication.getThemeIcon("mActionDeleteSelected.svg"))
            layout.addWidget(self.del_btn)

        self.setLayout(layout)

        self.input_widget.currentIndexChanged.connect(lambda _: self.changed.emit())

    def set_value(self, value: str | None):
        self.input_widget.set_value(value)

    def get_value(self) -> str | None:
        return self.input_widget.value()


class LegalEffectWidget(QWidget):
    changed = pyqtSignal()

    def __init__(
        self,
        with_add_btn: bool = False,  # noqa: FBT001, FBT002
        with_del_btn: bool = False,  # noqa: FBT001, FBT002
        parent=None,
    ):
        super().__init__(parent)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.input_widget = HierarchicalCodeComboBox()
        self.input_widget.populate_from_code_layer(LegalEffectsLayer)
        layout.addWidget(self.input_widget)

        self.add_btn: QPushButton | None = None
        if with_add_btn:
            self.add_btn = QPushButton()
            self.add_btn.setMaximumWidth(30)
            self.add_btn.setIcon(QgsApplication.getThemeIcon("mActionAdd.svg"))
            layout.addWidget(self.add_btn)

        self.del_btn: QPushButton | None = None
        if with_del_btn:
            self.del_btn = QPushButton()
            self.del_btn.setMaximumWidth(30)
            self.del_btn.setIcon(QgsApplication.getThemeIcon("mActionDeleteSelected.svg"))
            layout.addWidget(self.del_btn)

        self.setLayout(layout)

        self.input_widget.currentIndexChanged.connect(lambda _: self.changed.emit())

    def set_value(self, value: str | None):
        self.input_widget.set_value(value)

    def get_value(self) -> str | None:
        return self.input_widget.value()


class ValueWidgetManager(QObject):
    value_changed = pyqtSignal()

    def __init__(self, value: AttributeValue | None, default_value: AttributeValue):
        super().__init__()

        if value is None:
            value = AttributeValue()
        self.value_data_type = default_value.value_data_type
        self.unit = default_value.unit
        self.default_value = default_value

        self.value_widget: QWidget | None = None

        if self.value_data_type in (AttributeValueDataType.DECIMAL, AttributeValueDataType.POSITIVE_DECIMAL):
            positive = self.value_data_type == AttributeValueDataType.POSITIVE_DECIMAL
            self.value_widget = DecimalInputWidget(
                value.numeric_value or default_value.numeric_value, self.unit, positive
            )

        elif self.value_data_type in (AttributeValueDataType.NUMERIC, AttributeValueDataType.POSITIVE_NUMERIC):
            positive = self.value_data_type == AttributeValueDataType.POSITIVE_NUMERIC
            numeric_value = value.numeric_value or default_value.numeric_value
            self.value_widget = IntegerInputWidget(
                default_value=int(numeric_value) if numeric_value is not None else None,
                unit=self.unit,
                positive=positive,
            )

        elif self.value_data_type in (
            AttributeValueDataType.NUMERIC_RANGE,
            AttributeValueDataType.POSITIVE_NUMERIC_RANGE,
        ):
            positive = self.value_data_type == AttributeValueDataType.POSITIVE_NUMERIC_RANGE

            value_min = value.numeric_range_min or default_value.numeric_range_min
            value_max = value.numeric_range_max or default_value.numeric_range_max
            self.value_widget = IntegerRangeInputWidget(
                int(value_min) if value_min is not None else None,
                int(value_max) if value_max is not None else None,
                self.unit,
                positive,
            )

        elif self.value_data_type == AttributeValueDataType.LOCALIZED_TEXT:
            text_value = value.text_value or default_value.text_value
            self.value_widget = LocalizedMultilineTextInputWidget(editable=True)
            if text_value:
                self.value_widget.set_value(text_value)

        elif self.value_data_type == AttributeValueDataType.CODE:
            self.value_widget = CodeComboBox()
            if not default_value.code_list:
                logger.critical("Code list missing for %s", default_value)
                return

            code_layer = get_code_layer_by_uri(default_value.code_list)
            if code_layer:
                self.value_widget.populate_from_code_layer(code_layer)
                if value.code_value:
                    value_id = code_layer.get_id_by_attribute("value", value.code_value)
                    if value_id:
                        self.value_widget.set_value(value_id)
                    else:
                        logger.critical("Could not find code value %s for value widget", value.code_value)
            else:
                logger.critical("Could not find code layer with name %s for value widget", default_value.code_list)

        else:
            logger.warning("No value input implemented for data type: %s", default_value.value_data_type)

        if self.value_widget:
            self.value_widget.changed.connect(lambda: self.value_changed.emit())

    def into_model(self) -> AttributeValue:
        if self.value_data_type in (
            AttributeValueDataType.DECIMAL,
            AttributeValueDataType.POSITIVE_DECIMAL,
            AttributeValueDataType.NUMERIC,
            AttributeValueDataType.POSITIVE_NUMERIC,
        ):
            return AttributeValue(
                value_data_type=self.value_data_type,
                numeric_value=self.value_widget.get_value() if self.value_widget else None,
                unit=self.unit,
            )

        if self.value_data_type in (
            AttributeValueDataType.NUMERIC_RANGE,
            AttributeValueDataType.POSITIVE_NUMERIC_RANGE,
        ):
            range_min, range_max = self.value_widget.get_value() if self.value_widget else (None, None)
            return AttributeValue(
                value_data_type=self.value_data_type,
                numeric_range_min=range_min,
                numeric_range_max=range_max,
                unit=self.unit,
            )

        if self.value_data_type == AttributeValueDataType.LOCALIZED_TEXT:
            return AttributeValue(
                value_data_type=self.value_data_type,
                text_value=self.value_widget.get_value() if self.value_widget else None,
                text_syntax=None,
            )

        if self.value_data_type == AttributeValueDataType.CODE:
            if self.value_widget:
                code_value = self.value_widget.code_layer.get_attribute_by_id("value", self.value_widget.value())
            else:
                code_value = None
            return AttributeValue(
                value_data_type=self.value_data_type,
                code_list=self.default_value.code_list,
                code_value=code_value,
                code_title=self.default_value.code_title,
            )

        return AttributeValue()
