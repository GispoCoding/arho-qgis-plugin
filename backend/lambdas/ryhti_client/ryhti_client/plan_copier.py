from __future__ import annotations

import contextlib
import datetime
import logging
from typing import TYPE_CHECKING, Any, NotRequired, TypedDict, TypeVar
from uuid import uuid4

from pydantic import BaseModel
from sqlalchemy.orm import Session, class_mapper
from sqlalchemy.orm.exc import UnmappedColumnError

from database import codes, models
from ryhti_client.lifecycles import (
    LifeCycleStatusValue,
    UnderAppealScopeOption,
    is_under_appeal,
)

if TYPE_CHECKING:
    from datetime import date

logger = logging.getLogger(__name__)

MODEL = TypeVar("MODEL", bound=models.Base)
PLAN_OBJECT_MODEL = TypeVar("PLAN_OBJECT_MODEL", bound=models.PlanObjectBase)


class FeatureLifecycleOverride(TypedDict):
    lifecycle_status: NotRequired[codes.LifeCycleStatus]
    period_of_validity_start: NotRequired[date | None]


class PlanCopier:
    def __init__(
        self,
        session: Session,
        plan: models.Plan,
        plan_name: dict[str, str],
        lifecycle_status: codes.LifeCycleStatus | None,
        under_appeal_scope: UnderAppealScopeOption | None = None,
        deep_copy: bool | None = False,
        keep_under_appeal_lifecycle: bool | None = False,
        approval_date: date | None = None,
        period_of_validity_start: date | None = None,
        lock: bool | None = False,
    ) -> None:
        self.session = session
        self.plan = plan
        self.lifecycle_status = lifecycle_status
        self.plan_name = plan_name
        self.approval_date = approval_date
        self.period_of_validity_start = period_of_validity_start
        self.under_appeal_scope = under_appeal_scope
        self.deep_copy = deep_copy
        self.keep_under_appeal_lifecycle = keep_under_appeal_lifecycle
        self.lock = lock

        # Mapping original regulation group ID → duplicated regulation group
        self.regulation_group_mapping: dict[str, models.PlanRegulationGroup] = {}

    @classmethod
    def clone_model(cls, obj: MODEL, **overrides: Any) -> MODEL:
        """Clone a SQLAlchemy model instance with the same column data and overrides.

        Overrides may use relationship attribute names (e.g. plan=new_plan) instead of
        FK column names; the corresponding FK columns are excluded from the copied data
        to avoid conflicts.
        """
        model_class = type(obj)
        mapper = class_mapper(model_class)

        rel_by_key = {rel.key: rel for rel in mapper.relationships}
        fk_attrs_to_skip: set[str] = set()
        for key in overrides:
            if key not in rel_by_key:
                continue
            for col in rel_by_key[key].local_columns:
                with contextlib.suppress(UnmappedColumnError):
                    fk_attrs_to_skip.add(mapper.get_property_by_column(col).key)

        data = {
            column.key: getattr(obj, column.key)
            for column in mapper.columns
            if column.key not in overrides and column.key not in fk_attrs_to_skip
        }
        data.update(overrides)
        return model_class(**data)

    def define_lifecycle_override(
        self, feature: models.RyhtiLifecycleBase
    ) -> FeatureLifecycleOverride:
        """Defines the lifecycle status for the duplicated plan objects, regulations and
        propositions.

        If the plan is partially valid, the lifecycle status for regional plans must be
        set to "Valid before legal validity of plan" and for other plans to "Valid".
        """
        # if the feature is under appeal and it is wanted to keep that way don't change
        # the lifecycle
        if (
            self.keep_under_appeal_lifecycle
            and is_under_appeal(LifeCycleStatusValue(feature.lifecycle_status.value))
        ) or self.deep_copy:
            return {}

        # if the target lifecycle is valid and the features are already valid, don't
        # change the lifecycle status or the period of validity start date for the
        # features
        if (
            self.lifecycle_status
            and LifeCycleStatusValue(self.lifecycle_status.value)
            == LifeCycleStatusValue.VALID
            and LifeCycleStatusValue(feature.lifecycle_status.value)
            == LifeCycleStatusValue.VALID
        ):
            return {}

        lifecycle: codes.LifeCycleStatus | None = None
        if self.lifecycle_status and is_under_appeal(
            LifeCycleStatusValue(self.lifecycle_status.value)
        ):
            lifecycle_value = None
            if self.under_appeal_scope == UnderAppealScopeOption.WHOLE_PLAN:
                # set the same lifecycle for feautes than the plan
                lifecycle = self.lifecycle_status
            elif self.under_appeal_scope == UnderAppealScopeOption.PARTIALLY_VALID:
                logger.debug("is partially valid")
                if self.plan.plan_matter.plan_type.is_regional_plan():  # maakuntakaava
                    logger.debug("is regional plan")
                    # Voimassa ennen kaavan lainvoimaisuutta
                    lifecycle_value = LifeCycleStatusValue.VALID_BEFORE_LEGAL_VALIDITY
                lifecycle_value = LifeCycleStatusValue.VALID  # Voimassa
            elif self.under_appeal_scope == UnderAppealScopeOption.SUBSET_OF_PLAN:
                lifecycle_value = LifeCycleStatusValue.APPORVED  # Hyväksytty kaava

            if lifecycle_value:
                lifecycle = codes.get_code(
                    self.session, codes.LifeCycleStatus, lifecycle_value
                )
        else:
            lifecycle = self.lifecycle_status

        if not lifecycle:
            raise ValueError(
                "Couldn't determine lifecycle status for duplicated features"
            )

        return {
            "lifecycle_status": lifecycle,
            "period_of_validity_start": self.period_of_validity_start,
        }

    def copy_plan(self) -> models.Plan:
        plan_id = uuid4()
        plan_validity_start_date = (
            self.period_of_validity_start
            if self.under_appeal_scope != UnderAppealScopeOption.PARTIALLY_VALID
            else None
        )
        plan_overrides: dict[str, Any] = (
            {
                "lifecycle_status": self.lifecycle_status,
                "approval_date": self.approval_date,
                "period_of_validity_start": plan_validity_start_date,
            }
            if not self.deep_copy
            else {}
        )
        self.duplicate_plan = self.clone_model(
            self.plan,
            id=plan_id,
            name=self.plan_name,
            locked=self.lock,
            **plan_overrides,
        )

        # Documents
        self.duplicate_plan.documents = [
            self.clone_model(document, id=uuid4(), plan=self.duplicate_plan)
            for document in self.plan.documents
        ]

        # Master plan effects
        self.duplicate_plan.legal_effects_of_master_plan = (
            self.plan.legal_effects_of_master_plan
        )

        # Regulation groups and dependencies
        self.copy_regulation_groups()

        # Plan objects
        duplicate_land_use_areas = self.copy_plan_objects(self.plan.land_use_areas)
        self.duplicate_plan.land_use_areas = duplicate_land_use_areas

        duplicate_other_areas = self.copy_plan_objects(self.plan.other_areas)
        self.duplicate_plan.other_areas = duplicate_other_areas

        duplicate_lines = self.copy_plan_objects(self.plan.lines)
        self.duplicate_plan.lines = duplicate_lines

        duplicate_points = self.copy_plan_objects(self.plan.points)
        self.duplicate_plan.points = duplicate_points

        return self.duplicate_plan

    def copy_regulation_groups(self) -> None:
        duplicate_regulation_groups: list[models.PlanRegulationGroup] = []
        duplicate_general_regulation_groups: list[models.PlanRegulationGroup] = []

        for regulation_group in self.plan.regulation_groups:
            duplicate_regulation_group = self.clone_model(
                regulation_group, id=uuid4(), plan=self.duplicate_plan
            )
            self.regulation_group_mapping[regulation_group.id] = (
                duplicate_regulation_group
            )

            # Regulations
            self.copy_regulations(regulation_group, duplicate_regulation_group)

            # Propositions
            self.copy_propositions(regulation_group, duplicate_regulation_group)

            duplicate_regulation_groups.append(duplicate_regulation_group)
            if regulation_group in self.plan.general_plan_regulation_groups:
                duplicate_general_regulation_groups.append(duplicate_regulation_group)

        self.duplicate_plan.regulation_groups = duplicate_regulation_groups
        self.duplicate_plan.general_plan_regulation_groups = (
            duplicate_general_regulation_groups
        )

    def copy_regulations(
        self,
        regulation_group: models.PlanRegulationGroup,
        duplicate_regulation_group: models.PlanRegulationGroup,
    ) -> None:
        for regulation in regulation_group.plan_regulations:
            duplicate_regulation = self.clone_model(
                regulation,
                id=uuid4(),
                plan_regulation_group=duplicate_regulation_group,
                **self.define_lifecycle_override(regulation),
            )

            duplicate_regulation.types_of_verbal_plan_regulations = (
                regulation.types_of_verbal_plan_regulations
            )
            duplicate_regulation.plan_themes = regulation.plan_themes

            for info in regulation.additional_information:
                self.clone_model(info, id=uuid4(), plan_regulation=duplicate_regulation)

    def copy_propositions(
        self,
        regulation_group: models.PlanRegulationGroup,
        duplicate_regulation_group: models.PlanRegulationGroup,
    ) -> None:
        for proposition in regulation_group.plan_propositions:
            duplicate_proposition = self.clone_model(
                proposition,
                id=uuid4(),
                plan_regulation_group=duplicate_regulation_group,
                **self.define_lifecycle_override(proposition),
            )
            duplicate_proposition.plan_themes = proposition.plan_themes

    def copy_plan_objects(
        self, plan_objects: list[PLAN_OBJECT_MODEL]
    ) -> list[PLAN_OBJECT_MODEL]:
        duplicate_plan_objects: list[PLAN_OBJECT_MODEL] = []
        for plan_object in plan_objects:
            duplicate_plan_object = self.clone_model(
                plan_object,
                id=uuid4(),
                plan=self.duplicate_plan,
                **self.define_lifecycle_override(plan_object),
            )
            duplicate_regulation_groups = [
                self.regulation_group_mapping[original_regulation_group.id]
                for original_regulation_group in plan_object.plan_regulation_groups
            ]
            duplicate_plan_object.plan_regulation_groups = duplicate_regulation_groups
            duplicate_plan_objects.append(duplicate_plan_object)

        return duplicate_plan_objects


class CopyPlanData(BaseModel):
    plan_name: dict[str, str]
    lifecycle_status_id: str | None = None
    under_appeal_scope: UnderAppealScopeOption | None = None
    keep_under_appeal_lifecycle: bool = False
    deep_copy: bool | None = False
    approval_date: datetime.date | None = None
    period_of_validity_start: datetime.date | None = None
    lock: bool | None = False
