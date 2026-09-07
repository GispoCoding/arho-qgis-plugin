from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, TypeVar

from qgis.PyQt.QtWidgets import QWidget

if TYPE_CHECKING:
    from typing import Iterator

T = TypeVar("T", bound=QWidget)


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


@contextmanager
def deleted_after_use(dialog: T) -> Iterator[T]:
    """Yields `dialog` and schedules it for deletion when the block ends.

    A dialog parented to the QGIS main window is owned by C++, so letting the Python
    name go out of scope is not enough: without this it stays a child of the window for
    the rest of the session, one more every time it is opened.
    """
    try:
        yield dialog
    finally:
        dialog.deleteLater()
