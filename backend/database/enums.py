import enum


class AttributeValueDataType(enum.StrEnum):
    LOCALIZED_TEXT = "LocalizedText"
    TEXT = "Text"
    NUMERIC = "Numeric"
    NUMERIC_RANGE = "NumericRange"
    POSITIVE_NUMERIC = "PositiveNumeric"
    POSITIVE_NUMERIC_RANGE = "PositiveNumericRange"
    DECIMAL = "Decimal"
    DECIMAL_RANGE = "DecimalRange"
    POSITIVE_DECIMAL = "PositiveDecimal"
    POSITIVE_DECIMAL_RANGE = "PositiveDecimalRange"
    CODE = "Code"
    IDENTIFIER = "Identifier"
    SPOT_ELEVATION = "SpotElevation"
    TIME_PERIOD = "TimePeriod"
    TIME_PERIOD_DATE_ONLY = "TimePeriodDateOnly"


class JobStatus(enum.StrEnum):
    """The states of a ryhti_client job, see jobs.job.

    done means that the action ran, whatever status code it answered. failed
    means that the job crashed, never started or never finished.
    """

    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
