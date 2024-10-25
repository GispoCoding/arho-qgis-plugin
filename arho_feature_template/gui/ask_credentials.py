from __future__ import annotations

from importlib import resources

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QLineEdit

# Load the .ui file path using importlib resources
ui_path = resources.files(__package__) / "ask_credentials.ui"

# Use uic.loadUiType to load the UI definition from the .ui file
DbAskCredentialsDialogBase, _ = uic.loadUiType(ui_path)


class DbAskCredentialsDialog(QDialog, DbAskCredentialsDialogBase):  # type: ignore
    def __init__(self, parent: QDialog = None):
        super().__init__(parent)

        # Set up the UI from the loaded .ui file
        self.setupUi(self)

        # The UI elements defined in the .ui file
        self.userLineEdit: QLineEdit = self.findChild(QLineEdit, "userLineEdit")
        self.pwdLineEdit: QLineEdit = self.findChild(QLineEdit, "pwdLineEdit")
        self.buttonBox: QDialogButtonBox = self.findChild(QDialogButtonBox, "buttonBox")

        # Connect the OK and Cancel buttons to their respective functions
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def get_credentials(self) -> tuple[str, str]:
        """
        Returns the entered username and password.
        :return: Tuple (username, password)
        """
        return self.userLineEdit.text(), self.pwdLineEdit.text()
