from __future__ import annotations

import contextlib
import datetime
import logging
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import uuid4

from pydantic import BaseModel
from sqlalchemy.orm import Session, class_mapper
from sqlalchemy.orm.exc import UnmappedColumnError

from database import codes, models

if TYPE_CHECKING:
    from datetime import date

logger = logging.getLogger(__name__)

MODEL = TypeVar("MODEL", bound=models.Base)
PLAN_OBJECT_MODEL = TypeVar("PLAN_OBJECT_MODEL", bound=models.PlanObjectBase)


class PlanCopier:
    def __init__(
        self,
        session: Session,
        plan: models.Plan,
        lifecycle_status: codes.LifeCycleStatus,
        plan_name: dict[str, str],
        partially_valid: bool | None = None,
        approval_date: date | None = None,
        period_of_validity_start: date | None = None,
    ) -> None:
        self.session = session
        self.plan = plan
        self.lifecycle_status = lifecycle_status
        self.plan_name = plan_name
        self.approval_date = approval_date
        self.period_of_validity_start = period_of_validity_start
        self.partially_valid = partially_valid

        self.regulation_lifecycle_status = (
            self.define_regulation_lifecycle_status()
        )  # for duplicated plan objects, regulations and propositions
        logger.debug(
            "regulation lifecycle status: %s",
            self.regulation_lifecycle_status.value
            if self.regulation_lifecycle_status
            else None,
        )

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

    def define_regulation_lifecycle_status(self) -> codes.LifeCycleStatus | None:
        """Defines the lifecycle status for the duplicated plan objects, regulations and
        propositions.

        If the plan is partially valid, the lifecycle status for regional plans must be
        set to "Valid before legal validity of plan" and for other plans to "Valid".
        """
        if self.partially_valid:
            logger.debug("is partially valid")
            if self.plan.plan_matter.plan_type.is_regional_plan():  # maakuntakaava
                logger.debug("is regional plan")
                return codes.get_code(
                    self.session,
                    codes.LifeCycleStatus,
                    codes.LifeCycleStatus.VALID_BEFORE_LEGAL_VALIDITY_VALUE,
                )  # Voimassa ennen kaavan lainvoimaisuutta
            return codes.get_code(
                self.session, codes.LifeCycleStatus, codes.LifeCycleStatus.VALID_VALUE
            )  # Voimassa
        return self.lifecycle_status

    def define_plan_validity_start_date(self) -> date | None:
        return self.period_of_validity_start if not self.partially_valid else None

    def copy_plan(self) -> models.Plan:
        plan_id = uuid4()
        self.duplicate_plan = self.clone_model(
            self.plan,
            id=plan_id,
            name=self.plan_name,
            lifecycle_status=self.lifecycle_status,
            approval_date=self.approval_date,
            period_of_validity_start=self.define_plan_validity_start_date(),
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
                lifecycle_status=self.regulation_lifecycle_status,
                period_of_validity_start=self.period_of_validity_start,
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
                lifecycle_status=self.regulation_lifecycle_status,
                period_of_validity_start=self.period_of_validity_start,
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
                lifecycle_status=self.regulation_lifecycle_status,
                period_of_validity_start=self.period_of_validity_start,
            )
            duplicate_regulation_groups = [
                self.regulation_group_mapping[original_regulation_group.id]
                for original_regulation_group in plan_object.plan_regulation_groups
            ]
            duplicate_plan_object.plan_regulation_groups = duplicate_regulation_groups
            duplicate_plan_objects.append(duplicate_plan_object)

        return duplicate_plan_objects


class CopyPlanData(BaseModel):
    lifecycle_status_id: str
    plan_name: dict[str, str]
    partially_valid: bool | None = None
    approval_date: datetime.date | None = None
    period_of_validity_start: datetime.date | None = None
