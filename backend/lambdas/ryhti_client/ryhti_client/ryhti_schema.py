from typing import TypedDict


class Period(TypedDict):
    begin: str
    end: str | None


# Typing for ryhti dicts
class RyhtiPlan(TypedDict, total=False):
    planKey: str
    lifeCycleStatus: str
    scale: int | None
    legalEffectOfLocalMasterPlans: list | None
    geographicalArea: dict
    periodOfValidity: Period | None
    approvalDate: str | None
    planMaps: list
    planAnnexes: list
    otherPlanMaterials: list
    planReport: dict | None
    generalRegulationGroups: list[dict]
    planDescription: str | None
    planObjects: list
    planRegulationGroups: list
    planRegulationGroupRelations: list


class RyhtiPlanDecision(TypedDict, total=False):
    planDecisionKey: str
    name: str
    decisionDate: str
    dateOfDecision: str
    typeOfDecisionMaker: str
    plans: list[RyhtiPlan]


class RyhtiHandlingEvent(TypedDict, total=False):
    handlingEventKey: str
    handlingEventType: str
    eventTime: str
    cancelled: bool


class RyhtiInteractionEvent(TypedDict, total=False):
    interactionEventKey: str
    interactionEventType: str
    eventTime: Period


class RyhtiPlanMatterPhase(TypedDict, total=False):
    planMatterPhaseKey: str
    lifeCycleStatus: str
    geographicalArea: dict
    handlingEvent: RyhtiHandlingEvent | None
    interactionEvents: list[RyhtiInteractionEvent] | None
    planDecision: RyhtiPlanDecision | None


class RyhtiPlanMatter(TypedDict, total=False):
    permanentPlanIdentifier: str | None  # TODO: make mandatory, handle None in the code
    planType: str
    name: dict[str, str]
    timeOfInitiation: str | None
    description: dict[str, str] | None
    producerPlanIdentifier: str | None
    caseIdentifiers: list | None
    recordNumbers: list | None
    administrativeAreaIdentifiers: list
    digitalOrigin: str
    planMatterPhases: list[RyhtiPlanMatterPhase]


class RyhtiAttributeValue(TypedDict, total=False):
    dataType: str
    code: str | None
    codeList: str | None
    title: dict[str, str] | None
    number: int | float | None
    minimumValue: int | float | None
    maximumValue: int | float | None
    unitOfMeasure: str | None
    text: dict[str, str] | None
    syntax: str | None


class RyhtiAdditionalInformation(TypedDict, total=False):
    type: str
    value: RyhtiAttributeValue
