from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qgis.PyQt.QtWidgets import QWidget


def remove_widget(widget: QWidget) -> None:
    """Takes `widget` out of its layout and schedules it for deletion.

    `QLayout.removeWidget` does not change the parent, so the widget stays a visible
    child at (0, 0) until the deferred delete runs. `QWidget.setParent(None)` removes it
    from the layout (the layout acts on the `ChildRemoved` event) and hides it.

    The order matters: both `setParent` and `deleteLater` are `/TransferThis/` in the
    bindings, so `setParent(None)` hands ownership to Python and `deleteLater` hands it
    back to C++, which then frees it on the next turn of the event loop.
    """
    widget.setParent(None)
    widget.deleteLater()
