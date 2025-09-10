from typing import Dict, List, TypedDict


class Period(TypedDict):
    begin: str
    end: str | None


# Typing for ryhti dicts
class RyhtiPlan(TypedDict, total=False):
    planKey: str
    lifeCycleStatus: str
    scale: int | None
    legalEffectOfLocalMasterPlans: List | None
    geographicalArea: Dict
    periodOfValidity: Period | None
    approvalDate: str | None
    planMaps: List
    planAnnexes: List
    otherPlanMaterials: List
    planReport: Dict | None
    generalRegulationGroups: List[Dict]
    planDescription: str | None
    planObjects: List
    planRegulationGroups: List
    planRegulationGroupRelations: List


class RyhtiPlanDecision(TypedDict, total=False):
    planDecisionKey: str
    name: str
    decisionDate: str
    dateOfDecision: str
    typeOfDecisionMaker: str
    plans: List[RyhtiPlan]


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
    geographicalArea: Dict
    handlingEvent: RyhtiHandlingEvent | None
    interactionEvents: List[RyhtiInteractionEvent] | None
    planDecision: RyhtiPlanDecision | None


class RyhtiPlanMatter(TypedDict, total=False):
    permanentPlanIdentifier: str
    planType: str
    name: dict[str, str]
    timeOfInitiation: str | None
    description: dict[str, str] | None
    producerPlanIdentifier: str | None
    caseIdentifiers: List | None
    recordNumbers: List | None
    administrativeAreaIdentifiers: List
    digitalOrigin: str
    planMatterPhases: List[RyhtiPlanMatterPhase]


class AttributeValue(TypedDict, total=False):
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
