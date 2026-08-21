import enum


# TODO: check that valid status is "13" and approval status is "06" when
# the lifecycle status code list transitions from DRAFT to VALID. Unlike the
# other code lists, these values are numbers that may change, not descriptive
# strings.
class LifeCycleStatusValue(enum.StrEnum):
    PLANNING_INITIATIVE = "01"  # Kaavoitusaloite
    PENDING = "02"  # Vireilletullut
    PREPARATION = "03"  # Valmistelu
    PLAN_PROPOSAL = "04"  # Kaavaehdotus
    AMENDED_PLAN_PROPOSAL = "05"  # Muutettu kaavaehdotus
    APPORVED = "06"  # Hyväksytty kaava
    UNDER_RECTIFICATION_REMINDER = "07"  # Oikaisukehotuksen alainen
    UNDER_APPEAL = "08"  # Valituksen alainen
    UNDER_RECTIFICATION_REMINDER_AND_UNDER_APPEAL = (
        "09"  # Oikaisukehotuksen alainen ja valituksen alainen
    )
    PARTIALLY_VALID = "10"  # Osittain voimassa
    VALID_BEFORE_LEGAL_VALIDITY = "11"  # Voimassa ennen kaavan lainvoimaisuutta
    LEGALLY_VALID = "12"  # Lainvoimainen
    VALID = "13"  # Voimassa
    REPEALED = "14"  # Kumoutunut
    LAPSED = "15"  # Rauennut
    REJECTED = "16"  # Hylätty
    SUSPENDED = "17"  # Keskeytetty


def is_under_appeal(lifecycle_status: LifeCycleStatusValue) -> bool:
    return lifecycle_status in {
        LifeCycleStatusValue.UNDER_APPEAL,
        LifeCycleStatusValue.UNDER_RECTIFICATION_REMINDER,
        LifeCycleStatusValue.UNDER_RECTIFICATION_REMINDER_AND_UNDER_APPEAL,
    }


class UnderAppealScopeOption(enum.Enum):
    SUBSET_OF_PLAN = "subset_of_plan"
    WHOLE_PLAN = "whole_plan"
    PARTIALLY_VALID = "partially_valid"
