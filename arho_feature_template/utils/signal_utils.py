from PyQt5.QtCore import QObject, QTimer, pyqtSignal


class SignalDebouncer(QObject):
    """
    Utility class to debounce/reduce call rate for rapid function calls.

    To use this, connect signals to `restart_timer` and connect the actual
    function that needs to be executed to `triggered`. For example:
    ```
    self.debouncer = SignalDebouncer(delay_ms=250)
    self.line_edit.textEdited.connect(self.debouncer.restart_timer)
    self.debouncer.triggered.connect(self._on_line_edit_contents_changed)
    ```
    """

    triggered = pyqtSignal()

    def __init__(self, delay_ms=250, parent=None):
        super().__init__(parent)

        self.delay_ms = delay_ms
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.triggered)

    def restart_timer(self):
        self._timer.start(self.delay_ms)

    def cancel(self):
        self._timer.stop()

    def is_pending(self):
        return self._timer.isActive()
