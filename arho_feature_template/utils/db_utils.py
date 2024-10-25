from __future__ import annotations

import logging

from qgis.core import QgsApplication, QgsAuthMethodConfig
from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtWidgets import QDialog, QMessageBox

from arho_feature_template.core.exceptions import AuthConfigException
from arho_feature_template.gui.ask_credentials import DbAskCredentialsDialog
from arho_feature_template.qgis_plugin_tools.tools.custom_logging import bar_msg
from arho_feature_template.qgis_plugin_tools.tools.settings import parse_value

LOGGER = logging.getLogger("LandUsePlugin")

PG_CONNECTIONS = "PostgreSQL/connections"
QGS_SETTINGS_PSYCOPG2_PARAM_MAP = {
    "database": "dbname",
    "host": "host",
    "password": "password",
    "port": "port",
    "username": "user",
    "sslmode": "sslmode",
}
QGS_SETTINGS_SSL_MODE_TO_POSTGRES = {
    "SslDisable": "disable",
    "SslAllow": "allow",
    "SslPrefer": "prefer",
    "SslRequire": "require",
    "SslVerifyCa": "verify-ca",
    "SslVerifyFull": "verify-full",
}


def get_existing_database_connections() -> set:
    """
    Retrieve the list of existing database connections from QGIS settings.

    :return: A set of available PostgreSQL connection names.
    """
    s = QSettings()
    s.beginGroup(PG_CONNECTIONS)
    keys = s.allKeys()
    s.endGroup()

    connections = {key.split("/")[0] for key in keys if "/" in key}
    LOGGER.debug(f"Available database connections: {connections}")  # noqa: G004

    return connections


def get_db_connection_params(con_name) -> dict:
    s = QSettings()
    s.beginGroup(f"{PG_CONNECTIONS}/{con_name}")

    auth_cfg_id = parse_value(s.value("authcfg"))
    username_saved = parse_value(s.value("saveUsername"))
    pwd_saved = parse_value(s.value("savePassword"))
    # sslmode = parse_value(s.value("sslmode"))

    params = {}

    for qgs_key, psyc_key in QGS_SETTINGS_PSYCOPG2_PARAM_MAP.items():
        if psyc_key != "sslmode":
            params[psyc_key] = parse_value(s.value(qgs_key))
        else:
            params[psyc_key] = QGS_SETTINGS_SSL_MODE_TO_POSTGRES[parse_value(s.value(qgs_key))]

    s.endGroup()
    # username or password might have to be asked separately
    if not username_saved:
        params["user"] = None

    if not pwd_saved:
        params["password"] = None

    if auth_cfg_id is not None and auth_cfg_id != "":
        # Auth config is being used to store the username and password
        auth_config = QgsAuthMethodConfig()
        # noinspection PyArgumentList
        QgsApplication.authManager().loadAuthenticationConfig(auth_cfg_id, auth_config, True)

        if auth_config.isValid():
            params["user"] = auth_config.configMap().get("username")
            params["password"] = auth_config.configMap().get("password")
        else:
            msg = "Auth config error occurred while fetching database connection parameters"
            raise AuthConfigException(
                msg,
                bar_msg=bar_msg(f"Check auth config with id: {auth_cfg_id}"),
            )

    return params


def check_credentials(conn_params: dict) -> None:
    """
    Checks whether the username and password are present in the connection parameters.
    If not, prompt the user to enter the credentials via a dialog.

    :param conn_params: Connection parameters (dictionary).
    """
    if not conn_params["user"] or not conn_params["password"]:
        LOGGER.info("No username and/or password found. Asking user for credentials.")

        # Show dialog to ask for user credentials
        ask_credentials_dlg = DbAskCredentialsDialog()
        result = ask_credentials_dlg.exec_()

        if result == QDialog.Accepted:
            conn_params["user"] = ask_credentials_dlg.userLineEdit.text()
            conn_params["password"] = ask_credentials_dlg.pwdLineEdit.text()
        else:
            ask_credentials_dlg.close()
            QMessageBox.warning(None, "Authentication Required", "Cannot connect without username or password.")
            return None
