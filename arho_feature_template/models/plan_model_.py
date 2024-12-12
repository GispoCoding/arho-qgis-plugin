from dataclasses import dataclass
from typing import ClassVar

from qgis.PyQt.QtCore import QObject, pyqtSignal


class SignaledDataClass:
    def __setattr__(self, name, value):
        if getattr(self, name, None) != value:
            signal_name = f"{name}_changed"
            if signal_name in self.__class__.__dict__:
                signal = getattr(self, signal_name, None)
        super().__setattr__(name, value)
        if signal:
            signal.emit(value)


@dataclass
class Plan(QObject, SignaledDataClass):
    name_changed: ClassVar = pyqtSignal(str)

    name: str
    description: str
    is_active: bool = True

    def __post_init__(self):
        super().__init__()


if __name__ == "__main__":
    plan = Plan(name="Basic", description="Basic plan")
