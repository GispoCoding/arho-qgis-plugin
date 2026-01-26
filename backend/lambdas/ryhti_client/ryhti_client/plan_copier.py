from typing import Any, TypeVar
from uuid import uuid4

from sqlalchemy.orm import class_mapper

from database import codes, models

MODEL = TypeVar("MODEL", bound=models.Base)
PLAN_OBJECT_MODEL = TypeVar("PLAN_OBJECT_MODEL", bound=models.PlanObjectBase)


class PlanCopier:
    def __init__(
        self,
        plan: models.Plan,
        lifecycle_status: codes.LifeCycleStatus,
        plan_name: dict[str, str],
    ) -> None:
        self.plan = plan
        self.lifecycle_status = lifecycle_status
        self.plan_name = plan_name

        # Mapping original regulation group ID → duplicated regulation group
        self.regulation_group_mapping: dict[str, models.PlanRegulationGroup] = {}

    @classmethod
    def clone_model(cls, obj: MODEL, **overrides: Any) -> MODEL:
        """Clone a SQLAlchemy model instance with the same column data and overrides."""
        model_class = type(obj)
        mapper = class_mapper(model_class)
        data = {
            c.key: getattr(obj, c.key) for c in mapper.columns if c.key not in overrides
        }
        data.update(overrides)
        return model_class(**data)

    def copy_plan(self) -> models.Plan:
        self.duplicate_plan = self.clone_model(
            self.plan,
            id=uuid4(),
            lifecycle_status=self.lifecycle_status,
            name=self.plan_name,
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
                lifecycle_status=self.lifecycle_status,
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
                lifecycle_status=self.lifecycle_status,
            )
            duplicate_proposition.plan_themes = proposition.plan_themes

    def copy_plan_objects(
        self, plan_objects: list[PLAN_OBJECT_MODEL]
    ) -> list[PLAN_OBJECT_MODEL]:
        duplicate_plan_objects = []
        for plan_object in plan_objects:
            duplicate_plan_object = self.clone_model(
                plan_object,
                id=uuid4(),
                plan=self.duplicate_plan,
                lifecycle_status=self.lifecycle_status,
            )
            duplicate_regulation_groups = [
                self.regulation_group_mapping[original_regulation_group.id]
                for original_regulation_group in plan_object.plan_regulation_groups
            ]
            duplicate_plan_object.plan_regulation_groups = duplicate_regulation_groups
            duplicate_plan_objects.append(duplicate_plan_object)

        return duplicate_plan_objects
