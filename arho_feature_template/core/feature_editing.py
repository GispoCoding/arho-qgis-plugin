from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, cast

from qgis.core import QgsProject

from arho_feature_template.project.layers.plan_layers import (
    AdditionalInformationLayer,
    DocumentLayer,
    LegalEffectAssociationLayer,
    PlanLayer,
    PlanMatterLayer,
    PlanPropositionLayer,
    PlanRegulationLayer,
    PlanThemeAssociationLayer,
    RegulationGroupAssociationLayer,
    RegulationGroupLayer,
    TypeOfVerbalRegulationAssociationLayer,
    get_plan_feature_layer_class_by_model,
)
from arho_feature_template.qgis_plugin_tools.tools.messages import MsgBar
from arho_feature_template.utils.misc_utils import (
    get_active_plan_matter_id,
    status_message,
    use_wait_cursor,
)
from arho_feature_template.utils.timing import timed_function

if TYPE_CHECKING:
    from qgis.core import QgsFeature, QgsVectorLayer

    from arho_feature_template.core.models import (
        AdditionalInformation,
        Document,
        Plan,
        PlanMatter,
        PlanObject,
        Proposition,
        Regulation,
        RegulationGroup,
        StoredPlan,
        StoredPlanObject,
        StoredProposition,
        StoredRegulation,
        StoredRegulationGroup,
    )
    from arho_feature_template.project.layers import AbstractLayer

logger = logging.getLogger(__name__)

created_object_models: dict[str, PlanObject] = {}

# Runs when the edit buffer is committed, so that the saved models mirror the database.
# A failed commit drops the callbacks: nothing was written, so the models stay as they were.
_after_commit: list[Callable[[], None]] = []

# The layers whose rows the active plan regulation group library and the regulation groups
# dock show. A save that leaves them all untouched does not need a library refresh.
regulation_group_layers = (
    RegulationGroupLayer,
    RegulationGroupAssociationLayer,
    PlanRegulationLayer,
    PlanPropositionLayer,
    AdditionalInformationLayer,
    PlanThemeAssociationLayer,
    TypeOfVerbalRegulationAssociationLayer,
)


def regulation_group_layers_modified() -> bool:
    """Whether the pending edit buffer changes any regulation group data. Ask before the commit."""
    modified = [
        layer_class.name for layer_class in regulation_group_layers if layer_class.get_from_project().isModified()
    ]
    logger.debug("Regulation group layers with pending changes: %s", modified)
    return bool(modified)


@dataclass(frozen=True)
class PlanObjectSaveResult:
    id_: str
    regulation_groups_changed: bool
    """The commit wrote regulation group data, so the active plan group library is stale."""


def _set_id_after_commit(model: AdditionalInformation | Document, id_: str) -> None:
    """A new leaf model gets the id of its row once the row exists."""

    def apply() -> None:
        if model.id_ is None:
            model.id_ = id_

    _after_commit.append(apply)


def _sync_after_commit(model: Plan | PlanObject | RegulationGroup | Regulation | Proposition, id_: str) -> None:
    """Once committed, the model has the id of its row and its children are the stored ones.

    Children register before their parent (they are saved first), so the parent's snapshot
    sees the ids the new children got.
    """

    def apply() -> None:
        if model.id_ is None:
            model.id_ = id_
        model.refresh_stored()

    _after_commit.append(apply)


def _stored(
    model: Plan | PlanObject | RegulationGroup | Regulation | Proposition,
) -> StoredPlan | StoredPlanObject | StoredRegulationGroup | StoredRegulation | StoredProposition:
    """The database snapshot of a model that has a row.

    Only the readers (and a commit) set the snapshot. A model with an id but no snapshot was
    built some other way, and saving it could leave orphan rows or insert duplicate links.
    """
    if model.stored is None:
        msg = f"{type(model).__name__} {model.id_} has an id but no stored snapshot"
        raise ValueError(msg)
    return model.stored


def _ids(
    models: list[RegulationGroup] | list[Regulation] | list[Proposition] | list[AdditionalInformation] | list[Document],
) -> frozenset[str]:
    return frozenset(model.id_ for model in models if model.id_ is not None)


def _delete_removed_rows(
    layer_class: type[AbstractLayer], removed_ids: frozenset[str], delete_text: str, error_text: str
) -> None:
    """Delete the child rows the edited model no longer has. One query, only when something was removed."""
    if not removed_ids:
        return
    layer = layer_class.get_from_project()
    if not layer.isEditable():
        QgsProject.instance().startEditing(layer)
    for feature in layer_class.get_features_by_attribute_value("id", removed_ids):
        if not delete_in_edit_buffer(feature, layer, delete_text):
            MsgBar.error("", error_text)


def _delete_removed_associations(
    layer_class: type[AbstractLayer],
    parent: dict[str, str],
    child_attribute: str,
    removed_ids: frozenset[str],
    delete_text: str,
    error_text: str,
) -> None:
    """Delete the link rows of `parent` whose child the edited model no longer has. One query, only when needed."""
    if not removed_ids:
        return
    layer = layer_class.get_from_project()
    if not layer.isEditable():
        QgsProject.instance().startEditing(layer)
    for feature in layer_class.get_features_by_attribute_values({**parent, child_attribute: removed_ids}):
        if not delete_in_edit_buffer(feature, layer, delete_text):
            MsgBar.error("", error_text)


def _delete_removed_regulation_group_associations(
    feature_id: str, layer_name: str, removed_group_ids: frozenset[str]
) -> None:
    _delete_removed_associations(
        RegulationGroupAssociationLayer,
        {RegulationGroupAssociationLayer.layer_name_to_attribute_map[layer_name]: feature_id},
        "plan_regulation_group_id",
        removed_group_ids,
        "Kaavamääräysryhmän assosiaation poisto",
        "Kaavamääräysryhmän assosiaation poistaminen epäonnistui.",
    )


def feature_id(feature: QgsFeature) -> str:
    """Get the id field value from the feature. Use the internal feature id as a fallback if the id field is not found."""
    try:
        return cast(str, feature["id"])
    except KeyError:
        return str(feature.id())


@timed_function("add_to_edit_buffer")
def add_to_edit_buffer(feature: QgsFeature, layer: QgsVectorLayer, id_: str | None, edit_text: str = "") -> bool:
    action = "add" if id_ is None else "update"
    logger.debug(
        "Edit buffer action=%s layer=%s feature_id=%s command=%s",
        action,
        layer.name(),
        feature_id(feature),
        edit_text,
    )
    layer.beginEditCommand(edit_text)

    result = layer.addFeature(feature) if id_ is None else layer.updateFeature(feature)

    layer.endEditCommand()
    logger.debug("Edit buffer result=%s", result)
    return result


@timed_function("delete_in_edit_buffer")
def delete_in_edit_buffer(feature: QgsFeature, layer: QgsVectorLayer, delete_text: str = "") -> bool:
    logger.debug(
        "Edit buffer action=delete layer=%s feature_id=%s command=%s",
        layer.name(),
        feature_id(feature),
        delete_text,
    )
    layer.beginEditCommand(delete_text)

    result = layer.deleteFeature(feature.id())

    layer.endEditCommand()
    logger.debug("Edit buffer result=%s", result)
    return result


@timed_function("commit_edit_buffer")
def commit_edit_buffer(stop_editing: bool) -> bool:  # noqa: FBT001
    project = QgsProject.instance()
    result, commit_errors = project.commitChanges(stopEditing=stop_editing)
    try:
        if result:
            logger.debug("Committed succesfully. Details=%s", commit_errors)
            for apply in _after_commit:
                apply()
        else:
            logger.error("Failed to commit transaction. Details=%s", commit_errors)
    finally:
        _after_commit.clear()
    if any("VIRHE" in error for error in commit_errors):
        logger.error("Commit errors: %s", commit_errors)

    return result


@timed_function("delete_feature")
def delete_feature(feature: QgsFeature, layer: QgsVectorLayer, delete_text: str = "") -> bool:
    logger.debug("Deleting feature from layer=%s feature_id=%s", layer.name(), feature_id(feature))
    delete_in_edit_buffer(feature, layer, delete_text)
    result = commit_edit_buffer(stop_editing=False)

    return result


@use_wait_cursor
@status_message("Tallennetaan kaava-asiaa ...")
@timed_function("save_plan_matter")
def save_plan_matter(plan_matter: PlanMatter) -> str | None:
    plan_matter_id = plan_matter.id_
    editing = plan_matter_id is not None
    logger.info("Saving plan matter id=%s editing=%s modified=%s", plan_matter_id, editing, plan_matter.modified)
    if plan_matter.id_ is None or plan_matter.modified:
        layer = PlanMatterLayer.get_from_project()
        feature = PlanMatterLayer.feature_from_model(plan_matter)
        if not layer.isEditable():
            logger.debug("Layer %s not editable, starting edit session", layer.name())
            QgsProject.instance().startEditing(layer)

        if not add_to_edit_buffer(
            feature=feature,
            layer=layer,
            id_=plan_matter_id,
            edit_text="Kaava-asian muokkaus" if editing else "Kaava-asian luominen",
        ):
            MsgBar.error("", "Kaava-asian tallentaminen epäonnistui")
            return None
        plan_matter_id = cast(str, feature["id"])

        result = commit_edit_buffer(stop_editing=False)
        if not result:
            return None
    else:
        logger.debug("Skipping plan matter save, no changes detected for id=%s", plan_matter_id)

    return plan_matter_id


@use_wait_cursor
@status_message("Tallennetaan kaavasuunnitelmaa ...")
@timed_function("save_plan")
def save_plan(plan: Plan) -> str | None:
    plan_id = plan.id_
    if not plan.plan_matter_id:
        plan.plan_matter_id = get_active_plan_matter_id()
    logger.info(
        "Saving plan id=%s modified=%s general_regs=%s legal_effects=%s documents=%s",
        plan_id,
        plan.modified,
        len(plan.general_regulations),
        len(plan.legal_effect_ids),
        len(plan.documents),
    )
    editing = plan_id is not None
    if plan_id is None or plan.modified:
        layer = PlanLayer.get_from_project()
        feature = PlanLayer.feature_from_model(plan)
        if not layer.isEditable():
            logger.debug("Layer %s not editable, starting edit session", layer.name())
            QgsProject.instance().startEditing(layer)

        if not add_to_edit_buffer(
            feature=feature,
            layer=layer,
            id_=plan_id,
            edit_text="Kaavasuunnitelman muokkaus" if editing else "Kaavasuunnitelman luominen",
        ):
            MsgBar.error("", "Kaavasuunnitelman tallentaminen epäonnistui.")
            return None
        plan_id = cast(str, feature["id"])
    else:
        logger.debug("Skipping plan feature update, no direct plan changes for id=%s", plan_id)

    stored_group_ids: frozenset[str] = frozenset()
    stored_legal_effect_ids: frozenset[str] = frozenset()
    if editing:
        stored = cast("StoredPlan", _stored(plan))
        stored_group_ids = stored.general_regulation_group_ids
        stored_legal_effect_ids = stored.legal_effect_ids

        _delete_removed_regulation_group_associations(
            plan_id, PlanLayer.name, stored_group_ids - _ids(plan.general_regulations)
        )
        _delete_removed_associations(
            LegalEffectAssociationLayer,
            {"plan_id": plan_id},
            "legal_effects_of_master_plan_id",
            stored_legal_effect_ids - frozenset(plan.legal_effect_ids),
            "Oikeusvaikutuksen assosiaation poisto",
            "Oikeusvaikutuksen assosiaation poistaminen epäonnistui.",
        )
        _delete_removed_rows(
            DocumentLayer,
            stored.document_ids - _ids(plan.documents),
            "Asiakirjan poisto",
            "Asiakirjan poistaminen epäonnistui.",
        )

    # Save general regulations
    for regulation_group in plan.general_regulations:
        group_id = add_regulation_group_to_edit_buffer(regulation_group, plan_id)
        if group_id is None:
            continue  # Skip association saving if saving regulation group failed
        if group_id not in stored_group_ids:
            add_regulation_group_association_to_edit_buffer(group_id, PlanLayer.name, plan_id)

    # Save legal effect associations
    for legal_effect_id in plan.legal_effect_ids:
        if legal_effect_id not in stored_legal_effect_ids:
            add_legal_effect_association_to_edit_buffer(plan_id, legal_effect_id)

    # Save documents
    for document in plan.documents:
        document.plan_id = plan_id
        add_document_to_edit_buffer(document)

    _sync_after_commit(plan, plan_id)
    result = commit_edit_buffer(stop_editing=False)
    if not result:
        return None

    return plan_id


@use_wait_cursor
@status_message("Tallennetaan kaavakohdetta ...")
@timed_function("save_plan_object")
def save_plan_object(plan_object: PlanObject, plan_id: str | None = None) -> PlanObjectSaveResult | None:
    logger.info("Saving plan object %s:%s", plan_object.layer_name, plan_object.id_)
    object_id = add_plan_object_to_edit_buffer(plan_object, enable_editing=True, plan_id=plan_id)
    if object_id is None:
        logger.warning("Plan object edit-buffer save failed for layer=%s", plan_object.layer_name)
        return None

    regulation_groups_changed = regulation_group_layers_modified()
    result = commit_edit_buffer(stop_editing=False)
    if result is not True:
        return None

    return PlanObjectSaveResult(object_id, regulation_groups_changed)


@use_wait_cursor
@timed_function("add_plan_object_to_edit_buffer")
def add_plan_object_to_edit_buffer(
    plan_object: PlanObject,
    enable_editing: bool = True,  # noqa: FBT001, FBT002
    plan_id: str | None = None,
) -> str | None:
    """Add plan objact object to edit buffer as part of action where multiple plan objects are saved at once.

    When `enable_editing` is False, we don't check for deleted, modified or new regulations groups. It is
    assumed that all regulations groups of plan object to be added exist already and that the plan object
    is new.
    """
    layer_class = get_plan_feature_layer_class_by_model(plan_object)
    layer_name = cast(str, plan_object.layer_name)
    logger.debug(
        "Adding plan object to edit buffer layer=%s id=%s modified=%s enable_editing=%s",
        layer_name,
        plan_object.id_,
        plan_object.modified,
        enable_editing,
    )

    object_id = plan_object.id_
    editing = object_id is not None
    if object_id is None or plan_object.modified:
        feature = layer_class.feature_from_model(plan_object, plan_id)
        layer = layer_class.get_from_project()
        if not layer.isEditable():
            logger.debug("Layer %s not editable, starting edit session", layer.name())
            QgsProject.instance().startEditing(layer)

        if not add_to_edit_buffer(
            feature=feature,
            layer=layer,
            id_=object_id,
            edit_text="Kaavakohteen muokkaus" if editing else "Kaavakohteen lisäys",
        ):
            MsgBar.error("", "Kaavakohteen tallentaminen epäonnistui.")
            return None
        object_id = cast(str, feature["id"])
        # Add id to model so that up-to-date model can be sent to plan objects table
        plan_object.id_ = object_id
        logger.debug("Plan object buffered layer=%s object_id=%s", layer_name, object_id)
    else:
        logger.debug("Skipping plan object feature update, no direct changes for id=%s", object_id)

    stored_group_ids: frozenset[str] = frozenset()
    if editing:
        stored_group_ids = cast("StoredPlanObject", _stored(plan_object)).regulation_group_ids
    if enable_editing and editing:
        _delete_removed_regulation_group_associations(
            object_id, layer_name, stored_group_ids - _ids(plan_object.regulation_groups)
        )

    # Save regulation groups
    for group in plan_object.regulation_groups:
        if enable_editing:
            group_id = add_regulation_group_to_edit_buffer(group)
            if group_id is None:
                continue  # Skip association saving if saving regulation group failed
        else:
            group_id = group.id_
        if group_id not in stored_group_ids:
            add_regulation_group_association_to_edit_buffer(group_id, layer_name, object_id)

    _sync_after_commit(plan_object, object_id)
    created_object_models[object_id] = plan_object
    logger.debug("Stored created_object_models entry id=%s", object_id)

    return object_id


@use_wait_cursor
@timed_function("save_regulation_group")
def save_regulation_group(regulation_group: RegulationGroup, plan_id: str | None = None) -> str | None:
    logger.info("Saving regulation group id=%s modified=%s", regulation_group.id_, regulation_group.modified)
    group_id = add_regulation_group_to_edit_buffer(regulation_group, plan_id)
    result = commit_edit_buffer(stop_editing=False)
    if not result:
        return None

    return group_id


@use_wait_cursor
@timed_function("add_regulation_group_to_edit_buffer")
def add_regulation_group_to_edit_buffer(regulation_group: RegulationGroup, plan_id: str | None = None) -> str | None:
    group_id = regulation_group.id_
    editing = group_id is not None
    logger.debug(
        "Adding regulation group to edit buffer id=%s editing=%s modified=%s regulations=%s propositions=%s",
        group_id,
        editing,
        regulation_group.modified,
        len(regulation_group.regulations),
        len(regulation_group.propositions),
    )
    if group_id is None or regulation_group.modified:
        layer = RegulationGroupLayer.get_from_project()
        feature = RegulationGroupLayer.feature_from_model(regulation_group, plan_id)
        if not layer.isEditable():
            logger.debug("Layer %s not editable, starting edit session", layer.name())
            QgsProject.instance().startEditing(layer)

        if not add_to_edit_buffer(
            feature=feature,
            layer=layer,
            id_=group_id,
            edit_text="Kaavamääräysryhmän muokkaus" if editing else "Kaavamääräysryhmän lisäys",
        ):
            MsgBar.error("", "Kaavamääräysryhmän tallentaminen epäonnistui.")
            return None
        group_id = cast(str, feature["id"])
        logger.debug("Regulation group buffered id=%s", group_id)
    else:
        logger.debug("Skipping regulation group feature update, no direct changes for id=%s", group_id)

    if editing:
        stored = cast("StoredRegulationGroup", _stored(regulation_group))
        _delete_removed_rows(
            PlanRegulationLayer,
            stored.regulation_ids - _ids(regulation_group.regulations),
            "Kaavamääräyksen poisto",
            "Kaavamääräyksen poistaminen epäonnistui.",
        )
        _delete_removed_rows(
            PlanPropositionLayer,
            stored.proposition_ids - _ids(regulation_group.propositions),
            "Kaavasuosituksen poisto",
            "Kaavasuosituksen poistaminen epäonnistui.",
        )

    # Save regulations
    for regulation in regulation_group.regulations:
        regulation.regulation_group_id = group_id  # Updating regulation group ID
        add_regulation_to_edit_buffer(regulation)

    # Save propositions
    for proposition in regulation_group.propositions:
        proposition.regulation_group_id = group_id  # Updating regulation group ID
        add_proposition_to_edit_buffer(proposition)

    _sync_after_commit(regulation_group, group_id)
    return group_id


def delete_regulation_group(regulation_group: RegulationGroup, plan_id: str | None = None) -> bool:
    if regulation_group.id_ is None:
        MsgBar.error("", "Kaavamääräysryhmän poistaminen epäonnistui (ei IDtä).")
        return False

    feature = RegulationGroupLayer.feature_from_model(regulation_group, plan_id)
    layer = RegulationGroupLayer.get_from_project()
    if not layer.isEditable():
        QgsProject.instance().startEditing(layer)

    if not delete_in_edit_buffer(feature, layer, "Kaavamääräysryhmän poisto"):
        MsgBar.error("", "Kaavamääräysryhmän poistaminen epäonnistui.")
        return False

    return True


@timed_function("save_regulation_group_association")
def save_regulation_group_association(regulation_group_id: str, layer_name: str, feature_id: str) -> bool:
    add_regulation_group_association_to_edit_buffer(regulation_group_id, layer_name, feature_id)
    result = commit_edit_buffer(stop_editing=False)
    return result


@timed_function("add_regulation_group_association_to_edit_buffer")
def add_regulation_group_association_to_edit_buffer(regulation_group_id: str, layer_name: str, feature_id: str) -> bool:
    """Add the association. The caller knows from the parent's `stored` snapshot that it is not in the database yet."""
    feature = RegulationGroupAssociationLayer.feature_from(regulation_group_id, layer_name, feature_id)
    layer = RegulationGroupAssociationLayer.get_from_project()
    if not layer.isEditable():
        QgsProject.instance().startEditing(layer)

    if not add_to_edit_buffer(
        feature=feature, layer=layer, id_=None, edit_text="Kaavamääräysryhmän assosiaation lisäys"
    ):
        MsgBar.error("", "Kaavamääräysryhmän assosiaation tallentaminen epäonnistui.")
        return False

    return True


@timed_function("add_regulation_to_edit_buffer")
def add_regulation_to_edit_buffer(regulation: Regulation) -> str | None:
    reg_id = regulation.id_
    editing = reg_id is not None
    if reg_id is None or regulation.modified:
        layer = PlanRegulationLayer.get_from_project()
        regulation_feature = PlanRegulationLayer.feature_from_model(regulation)
        if not layer.isEditable():
            QgsProject.instance().startEditing(layer)

        if not add_to_edit_buffer(
            feature=regulation_feature,
            layer=layer,
            id_=reg_id,
            edit_text="Kaavamääräyksen muokkaus" if editing else "Kaavamääräyksen lisäys",
        ):
            MsgBar.error("", "Kaavamääräyksen tallentaminen epäonnistui.")
            return None
        reg_id = cast(str, regulation_feature["id"])

    stored_type_ids: frozenset[str] = frozenset()
    stored_theme_ids: frozenset[str] = frozenset()
    if editing:
        stored = cast("StoredRegulation", _stored(regulation))
        stored_type_ids = stored.verbal_regulation_type_ids
        stored_theme_ids = stored.theme_ids

        _delete_removed_rows(
            AdditionalInformationLayer,
            stored.additional_information_ids - _ids(regulation.additional_information),
            "Lisätiedon poisto",
            "Lisätiedon poistaminen epäonnistui.",
        )
        _delete_removed_associations(
            TypeOfVerbalRegulationAssociationLayer,
            {"plan_regulation_id": reg_id},
            "type_of_verbal_plan_regulation_id",
            stored_type_ids - frozenset(regulation.verbal_regulation_type_ids),
            "Sanallisen kaavamääräyksen lajin assosiaation poisto",
            "Sanallisen kaavamääräyksen lajin assosiaation poistaminen epäonnistui.",
        )
        _delete_removed_associations(
            PlanThemeAssociationLayer,
            {"plan_regulation_id": reg_id},
            "plan_theme_id",
            stored_theme_ids - frozenset(regulation.theme_ids),
            "Kaavoitusteeman assosiaation poisto",
            "Kaavoitusteeman assosiaation poistaminen epäonnistui.",
        )

    for additional_information in regulation.additional_information:
        additional_information.plan_regulation_id = reg_id
        add_additional_information_to_edit_buffer(additional_information)

    for verbal_regulation_type_id in regulation.verbal_regulation_type_ids:
        if verbal_regulation_type_id not in stored_type_ids:
            add_type_of_verbal_regulation_association_to_edit_buffer(reg_id, verbal_regulation_type_id)

    for plan_theme_id in regulation.theme_ids:
        if plan_theme_id not in stored_theme_ids:
            add_plan_theme_association_to_edit_buffer(plan_theme_id=plan_theme_id, regulation_id=reg_id)

    _sync_after_commit(regulation, reg_id)
    return reg_id


@timed_function("add_plan_theme_association_to_edit_buffer")
def add_plan_theme_association_to_edit_buffer(
    plan_theme_id: str,
    regulation_id: str | None = None,
    proposition_id: str | None = None,
) -> bool:
    """Add the association. The caller knows from the parent's `stored` snapshot that it is not in the database yet."""
    feature = PlanThemeAssociationLayer.feature_from(
        plan_theme_id=plan_theme_id, plan_regulation_id=regulation_id, plan_proposition_id=proposition_id
    )
    layer = PlanThemeAssociationLayer.get_from_project()
    if not layer.isEditable():
        QgsProject.instance().startEditing(layer)

    if not add_to_edit_buffer(feature=feature, layer=layer, id_=None, edit_text="Kaavoitusteeman assosiaation lisäys"):
        MsgBar.error("", "Kaavoitusteeman assosiaation tallentaminen epäonnistui.")
        return False

    return True


@timed_function("add_type_of_verbal_regulation_association_to_edit_buffer")
def add_type_of_verbal_regulation_association_to_edit_buffer(
    regulation_id: str, verbal_regulation_type_id: str
) -> bool:
    """Add the association. The caller knows from the parent's `stored` snapshot that it is not in the database yet."""
    feature = TypeOfVerbalRegulationAssociationLayer.feature_from(regulation_id, verbal_regulation_type_id)
    layer = TypeOfVerbalRegulationAssociationLayer.get_from_project()
    if not layer.isEditable():
        QgsProject.instance().startEditing(layer)

    if not add_to_edit_buffer(
        feature=feature, layer=layer, id_=None, edit_text="Sanallisen kaavamääräyksen lajin assosiaation lisäys"
    ):
        MsgBar.error("", "Sanallisen kaavamääräyksen lajin assosiaation tallentaminen epäonnistui.")
        return False

    return True


def add_legal_effect_association_to_edit_buffer(plan_id: str, legal_effect_id: str) -> bool:
    """Add the association. The caller knows from the parent's `stored` snapshot that it is not in the database yet."""
    feature = LegalEffectAssociationLayer.feature_from(plan_id, legal_effect_id)
    layer = LegalEffectAssociationLayer.get_from_project()
    if not layer.isEditable():
        QgsProject.instance().startEditing(layer)

    if not add_to_edit_buffer(
        feature=feature, layer=layer, id_=None, edit_text="Oikeusvaikutuksen assosiaation lisäys"
    ):
        MsgBar.error("", "Oikeusvaikutuksen assosiaation tallentaminen epäonnistui.")
        return False

    return True


@timed_function("add_additional_information_to_edit_buffer")
def add_additional_information_to_edit_buffer(additional_information: AdditionalInformation) -> str | None:
    if additional_information.id_ is not None and not additional_information.modified:
        return additional_information.id_

    feature = AdditionalInformationLayer.feature_from_model(additional_information)
    layer = AdditionalInformationLayer.get_from_project()
    if not layer.isEditable():
        QgsProject.instance().startEditing(layer)

    if not add_to_edit_buffer(
        feature=feature,
        layer=layer,
        id_=additional_information.id_,
        edit_text="Lisätiedon lisäys" if additional_information.id_ is None else "Lisätiedon muokkaus",
    ):
        MsgBar.error("", "Lisätiedon tallentaminen epäonnistui.")
        return None

    _set_id_after_commit(additional_information, feature["id"])
    return feature["id"]


def delete_additional_information(additional_information: AdditionalInformation) -> bool:
    feature = AdditionalInformationLayer.feature_from_model(additional_information)
    layer = AdditionalInformationLayer.get_from_project()
    if not layer.isEditable():
        QgsProject.instance().startEditing(layer)

    if not delete_in_edit_buffer(feature, layer, "Lisätiedon poisto"):
        MsgBar.error("", "Lisätiedon poistaminen epäonnistui.")
        return False

    return True


def delete_regulation(regulation: Regulation) -> bool:
    feature = PlanRegulationLayer.feature_from_model(regulation)
    layer = PlanRegulationLayer.get_from_project()
    if not layer.isEditable():
        QgsProject.instance().startEditing(layer)

    if not delete_in_edit_buffer(feature, layer, "Kaavamääräyksen poisto"):
        MsgBar.error("", "Lisätiedon poistaminen epäonnistui.")
        return False

    return True


@timed_function("add_proposition_to_edit_buffer")
def add_proposition_to_edit_buffer(proposition: Proposition) -> str | None:
    prop_id = proposition.id_
    editing = prop_id is not None
    if prop_id is None or proposition.modified:
        feature = PlanPropositionLayer.feature_from_model(proposition)
        layer = PlanPropositionLayer.get_from_project()
        if not layer.isEditable():
            QgsProject.instance().startEditing(layer)

        if not add_to_edit_buffer(
            feature=feature,
            layer=layer,
            id_=prop_id,
            edit_text="Kaavasuosituksen muokkaus" if editing else "Kaavasuosituksen lisäys",
        ):
            MsgBar.error("", "Kaavasuosituksen tallentaminen epäonnistui.")
            return None
        prop_id = cast(str, feature["id"])

    stored_theme_ids: frozenset[str] = frozenset()
    if editing:
        stored_theme_ids = cast("StoredProposition", _stored(proposition)).theme_ids
        _delete_removed_associations(
            PlanThemeAssociationLayer,
            {"plan_proposition_id": prop_id},
            "plan_theme_id",
            stored_theme_ids - frozenset(proposition.theme_ids),
            "Kaavoitusteeman assosiaation poisto",
            "Kaavoitusteeman assosiaation poistaminen epäonnistui.",
        )

    for plan_theme_id in proposition.theme_ids:
        if plan_theme_id not in stored_theme_ids:
            add_plan_theme_association_to_edit_buffer(plan_theme_id=plan_theme_id, proposition_id=prop_id)

    _sync_after_commit(proposition, prop_id)
    return prop_id


def delete_proposition(proposition: Proposition) -> bool:
    feature = PlanPropositionLayer.feature_from_model(proposition)
    layer = PlanPropositionLayer.get_from_project()
    if not layer.isEditable():
        QgsProject.instance().startEditing(layer)

    if not delete_in_edit_buffer(feature, layer, "Kaavasuosituksen poisto"):
        MsgBar.error("", "Kaavasuosituksen poistaminen epäonnistui.")
        return False

    return True


def add_document_to_edit_buffer(document: Document) -> str | None:
    if document.id_ is not None and not document.modified:
        return document.id_

    feature = DocumentLayer.feature_from_model(document)
    layer = DocumentLayer.get_from_project()
    if not layer.isEditable():
        QgsProject.instance().startEditing(layer)

    if not add_to_edit_buffer(
        feature=feature,
        layer=layer,
        id_=document.id_,
        edit_text="Asiakirjan lisäys" if document.id_ is None else "Asiakirjan muokkaus",
    ):
        MsgBar.error("", "Asiakirjan tallentaminen epäonnistui.")
        return None

    _set_id_after_commit(document, feature["id"])
    return feature["id"]
