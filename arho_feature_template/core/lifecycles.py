from __future__ import annotations

import enum

from qgis.PyQt.QtGui import QColor, QPixmap

from arho_feature_template.gui.components.text_icon import text_icon
from arho_feature_template.qgis_plugin_tools.tools.resources import resources_path


class LifeCycleStatusValue(enum.StrEnum):
    PLANNING_INITIATIVE = "01"  # Kaavoitusaloite
    PENDING = "02"  # Vireilletullut
    PREPARATION = "03"  # Valmistelu
    PLAN_PROPOSAL = "04"  # Kaavaehdotus
    AMENDED_PLAN_PROPOSAL = "05"  # Muutettu kaavaehdotus
    APPORVED = "06"  # Hyväksytty kaava
    UNDER_RECTIFICATION_REMINDER = "07"  # Oikaisukehotuksen alainen
    UNDER_APPEAL = "08"  # Valituksen alainen
    UNDER_RECTIFICATION_REMINDER_AND_UNDER_APPEAL = "09"  # Oikaisukehotuksen alainen ja valituksen alainen
    PARTIALLY_VALID = "10"  # Osittain voimassa
    VALID_BEFORE_LEGAL_VALIDITY = "11"  # Voimassa ennen kaavan lainvoimaisuutta
    LEGALLY_VALID = "12"  # Lainvoimainen
    VALID = "13"  # Voimassa
    REPEALED = "14"  # Kumoutunut
    LAPSED = "15"  # Rauennut
    REJECTED = "16"  # Hylätty
    SUSPENDED = "17"  # Keskeytetty


LIFECYCLE_PIXMAPS = {
    LifeCycleStatusValue.LEGALLY_VALID: text_icon("✓", QColor(200, 200, 200)),
    LifeCycleStatusValue.VALID: text_icon("✓", QColor(48, 166, 26)),
    LifeCycleStatusValue.VALID_BEFORE_LEGAL_VALIDITY: QPixmap(resources_path("icons", "valid_mark.svg")),
    LifeCycleStatusValue.REPEALED: text_icon("X", QColor(255, 0, 0)),
    LifeCycleStatusValue.UNDER_APPEAL: text_icon("§", QColor(255, 0, 0)),
    LifeCycleStatusValue.UNDER_RECTIFICATION_REMINDER: text_icon("§", QColor(0, 0, 255)),
    LifeCycleStatusValue.UNDER_RECTIFICATION_REMINDER_AND_UNDER_APPEAL: text_icon("§", QColor(140, 0, 190)),
}


def get_allowed_plan_lifecycle_transitions(source_lifecycle: LifeCycleStatusValue) -> list[LifeCycleStatusValue]:
    allowed_transitions: dict[LifeCycleStatusValue, list[LifeCycleStatusValue]] = {
        LifeCycleStatusValue.PENDING: [
            LifeCycleStatusValue.PREPARATION,
            LifeCycleStatusValue.PLAN_PROPOSAL,
            LifeCycleStatusValue.APPORVED,
            LifeCycleStatusValue.SUSPENDED,
        ],
        LifeCycleStatusValue.PREPARATION: [
            LifeCycleStatusValue.PREPARATION,
            LifeCycleStatusValue.PLAN_PROPOSAL,
            LifeCycleStatusValue.APPORVED,
            LifeCycleStatusValue.SUSPENDED,
        ],
        LifeCycleStatusValue.PLAN_PROPOSAL: [
            LifeCycleStatusValue.PREPARATION,
            LifeCycleStatusValue.PLAN_PROPOSAL,
            LifeCycleStatusValue.AMENDED_PLAN_PROPOSAL,
            LifeCycleStatusValue.APPORVED,
            LifeCycleStatusValue.REJECTED,
            LifeCycleStatusValue.SUSPENDED,
        ],
        LifeCycleStatusValue.AMENDED_PLAN_PROPOSAL: [
            LifeCycleStatusValue.PREPARATION,
            LifeCycleStatusValue.AMENDED_PLAN_PROPOSAL,
            LifeCycleStatusValue.APPORVED,
            LifeCycleStatusValue.REJECTED,
            LifeCycleStatusValue.SUSPENDED,
        ],
        LifeCycleStatusValue.APPORVED: [
            LifeCycleStatusValue.LEGALLY_VALID,
            LifeCycleStatusValue.VALID,
            LifeCycleStatusValue.UNDER_RECTIFICATION_REMINDER,
            LifeCycleStatusValue.UNDER_APPEAL,
            LifeCycleStatusValue.UNDER_RECTIFICATION_REMINDER_AND_UNDER_APPEAL,
        ],
        LifeCycleStatusValue.UNDER_RECTIFICATION_REMINDER: [
            LifeCycleStatusValue.PLAN_PROPOSAL,
            LifeCycleStatusValue.APPORVED,
            LifeCycleStatusValue.LAPSED,
        ],
        LifeCycleStatusValue.UNDER_APPEAL: [
            LifeCycleStatusValue.LEGALLY_VALID,
            LifeCycleStatusValue.VALID,
            LifeCycleStatusValue.REPEALED,
        ],
        LifeCycleStatusValue.UNDER_RECTIFICATION_REMINDER_AND_UNDER_APPEAL: [
            LifeCycleStatusValue.UNDER_APPEAL,
            LifeCycleStatusValue.APPORVED,
            LifeCycleStatusValue.LAPSED,
        ],
        LifeCycleStatusValue.LEGALLY_VALID: [
            LifeCycleStatusValue.VALID,
            LifeCycleStatusValue.REPEALED,
        ],
        LifeCycleStatusValue.VALID: [
            LifeCycleStatusValue.REPEALED,
        ],
        LifeCycleStatusValue.REPEALED: [],
        LifeCycleStatusValue.LAPSED: [],
        LifeCycleStatusValue.REJECTED: [],
        LifeCycleStatusValue.SUSPENDED: [],
    }

    return allowed_transitions.get(source_lifecycle, [])
