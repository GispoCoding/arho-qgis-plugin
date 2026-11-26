"""`remove_widget` takes a widget out of its layout before deleting it.

`QLayout.removeWidget` leaves the parent alone, so the widget kept painting at (0, 0)
until the deferred delete ran.
"""

from __future__ import annotations

import pytest
from qgis.PyQt import sip
from qgis.PyQt.QtWidgets import QLabel, QVBoxLayout, QWidget

from arho_feature_template.utils.widget_utils import remove_widget

pytestmark = pytest.mark.fake_iface


@pytest.fixture
def parent_with_two_labels() -> tuple[QWidget, QVBoxLayout, QLabel, QLabel]:
    parent = QWidget()
    layout = QVBoxLayout(parent)
    first, second = QLabel("a", parent), QLabel("b", parent)
    layout.addWidget(first)
    layout.addWidget(second)
    return parent, layout, first, second


def test_remove_widget_takes_it_out_of_the_layout(parent_with_two_labels):
    parent, layout, first, second = parent_with_two_labels

    remove_widget(first)

    assert layout.count() == 1
    assert layout.itemAt(0).widget() is second
    assert first.parent() is None
    assert first not in parent.findChildren(QLabel)


def test_remove_widget_deletes_it_on_the_next_turn_of_the_loop(parent_with_two_labels, flush_deferred_deletes):
    _parent, _layout, first, second = parent_with_two_labels

    remove_widget(first)
    assert not sip.isdeleted(first)  # deleteLater only posts an event

    flush_deferred_deletes()

    assert sip.isdeleted(first)
    assert not sip.isdeleted(second)
