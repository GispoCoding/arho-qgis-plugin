from __future__ import annotations

from typing import TYPE_CHECKING, cast

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
from arho_feature_template.utils.misc_utils import (
    get_active_plan_matter_id,
    iface,
    status_message,
    use_wait_cursor,
)

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
    )

created_object_models: dict[str, PlanObject] = {}


def add_to_edit_buffer(feature: QgsFeature, layer: QgsVectorLayer, id_: str | None, edit_text: str = "") -> bool:
    layer.beginEditCommand(edit_text)

    result = layer.addFeature(feature) if id_ is None else layer.updateFeature(feature)

    layer.endEditCommand()
    return result


def delete_in_edit_buffer(feature: QgsFeature, layer: QgsVectorLayer, delete_text: str = "") -> bool:
    layer.beginEditCommand(delete_text)

    result = layer.deleteFeature(feature.id())

    layer.endEditCommand()
    return result


def delete_feature(feature: QgsFeature, layer: QgsVectorLayer, delete_text: str = "") -> bool:
    delete_in_edit_buffer(feature, layer, delete_text)
    result, _ = QgsProject.instance().commitChanges(stopEditing=False)

    return result


@use_wait_cursor
@status_message("Tallennetaan kaava-asiaa ...")
def save_plan_matter(plan_matter: PlanMatter) -> str | None:
    plan_matter_id = plan_matter.id_
    editing = plan_matter_id is not None
    if plan_matter.id_ is None or plan_matter.modified:
        layer = PlanMatterLayer.get_from_project()
        feature = PlanMatterLayer.feature_from_model(plan_matter)
        if not layer.isEditable():
            QgsProject.instance().startEditing(layer)

        if not add_to_edit_buffer(
            feature=feature,
            layer=layer,
            id_=plan_matter_id,
            edit_text="Kaava-asian muokkaus" if editing else "Kaava-asian luominen",
        ):
            iface.messageBar().pushCritical("", "Kaava-asian tallentaminen epäonnistui")
            return None
        plan_matter_id = cast(str, feature["id"])

        result, _ = QgsProject.instance().commitChanges(stopEditing=False)
        if not result:
            return None

    return plan_matter_id


@use_wait_cursor
@status_message("Tallennetaan kaavasuunnitelmaa ...")
def save_plan(plan: Plan) -> str | None:
    plan_id = plan.id_
    if not plan.plan_matter_id:
        plan.plan_matter_id = get_active_plan_matter_id()
    editing = plan_id is not None
    if plan_id is None or plan.modified:
        layer = PlanLayer.get_from_project()
        feature = PlanLayer.feature_from_model(plan)
        if not layer.isEditable():
            QgsProject.instance().startEditing(layer)

        if not add_to_edit_buffer(
            feature=feature,
            layer=layer,
            id_=plan_id,
            edit_text="Kaavasuunnitelman muokkaus" if editing else "Kaavasuunnitelman luominen",
        ):
            iface.messageBar().pushCritical("", "Kaavasuunnitelman tallentaminen epäonnistui.")
            return None
        plan_id = cast(str, feature["id"])

    if editing:
        # Check for deleted general regulations
        for association in RegulationGroupAssociationLayer.get_dangling_associations(
            plan.general_regulations, plan_id, PlanLayer.name
        ):
            if not delete_in_edit_buffer(
                association,
                RegulationGroupAssociationLayer.get_from_project(),
                "Kaavamääräysryhmän assosiaation poisto",
            ):
                iface.messageBar().pushCritical("", "Kaavamääräysryhmän assosiaation poistaminen epäonnistui.")

        # Check for deleted legal effects
        for association in LegalEffectAssociationLayer.get_dangling_associations(plan_id, plan.legal_effect_ids):
            if not delete_in_edit_buffer(
                association, LegalEffectAssociationLayer.get_from_project(), "Oikeusvaikutuksen assosiaation poisto"
            ):
                iface.messageBar().pushCritical("", "Oikeusvaikutuksen assosiaation poistaminen epäonnistui.")

        # Check for documents to be deleted
        doc_layer = DocumentLayer.get_from_project()
        for doc_feature in DocumentLayer.get_documents_to_delete(plan.documents, plan_id):
            if not delete_in_edit_buffer(doc_feature, doc_layer, "Asiakirjan poisto"):
                iface.messageBar().pushCritical("", "Asiakirjan poistaminen epäonnistui.")

    # Save general regulations
    if plan.general_regulations:
        for regulation_group in plan.general_regulations:
            group_id = add_regulation_group_to_edit_buffer(regulation_group, plan_id)
            if group_id is None:
                continue  # Skip association saving if saving regulation group failed
            add_regulation_group_association_to_edit_buffer(group_id, PlanLayer.name, plan_id)

    # Save legal effect associations
    for legal_effect_id in plan.legal_effect_ids:
        add_legal_effect_association_to_edit_buffer(plan_id, legal_effect_id)

    # Save documents
    for document in plan.documents:
        document.plan_id = plan_id
        add_document_to_edit_buffer(document)

    result, _ = QgsProject.instance().commitChanges(stopEditing=False)
    if not result:
        return None

    return plan_id


@use_wait_cursor
@status_message("Tallennetaan kaavakohdetta ...")
def save_plan_object(plan_object: PlanObject, plan_id: str | None = None) -> str | None:
    object_id = add_plan_object_to_edit_buffer(plan_object, enable_editing=True, plan_id=plan_id)
    result, _ = QgsProject.instance().commitChanges(stopEditing=False)
    if not result:
        return None

    return object_id


@use_wait_cursor
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

    object_id = plan_object.id_
    editing = object_id is not None
    feature = layer_class.feature_from_model(plan_object, plan_id)
    if object_id is None or plan_object.modified:
        layer = layer_class.get_from_project()
        if not layer.isEditable():
            QgsProject.instance().startEditing(layer)

        if not add_to_edit_buffer(
            feature=feature,
            layer=layer,
            id_=object_id,
            edit_text="Kaavakohteen muokkaus" if editing else "Kaavakohteen lisäys",
        ):
            iface.messageBar().pushCritical("", "Kaavakohteen tallentaminen epäonnistui.")
            return None
        object_id = cast(str, feature["id"])
        # Add id to model so that up-to-date model can be sent to plan objects table
        plan_object.id_ = object_id

    if enable_editing and editing:
        # Check for deleted regulation groups
        for association in RegulationGroupAssociationLayer.get_dangling_associations(
            plan_object.regulation_groups, object_id, layer_name
        ):
            if not delete_in_edit_buffer(
                association,
                RegulationGroupAssociationLayer.get_from_project(),
                "Kaavamääräysryhmän assosiaation poisto",
            ):
                iface.messageBar().pushCritical("", "Kaavamääräysryhmän assosiaation poistaminen epäonnistui.")

    # Save regulation groups
    for group in plan_object.regulation_groups:
        if enable_editing:
            group_id = add_regulation_group_to_edit_buffer(group)
            if group_id is None:
                continue  # Skip association saving if saving regulation group failed
        else:
            group_id = group.id_
        add_regulation_group_association_to_edit_buffer(group_id, layer_name, object_id)

    created_object_models[feature["id"]] = plan_object

    return object_id


@use_wait_cursor
def save_regulation_group(regulation_group: RegulationGroup, plan_id: str | None = None) -> str | None:
    group_id = add_regulation_group_to_edit_buffer(regulation_group, plan_id)
    result, _ = QgsProject.instance().commitChanges(stopEditing=False)
    if not result:
        return None

    return group_id


@use_wait_cursor
def add_regulation_group_to_edit_buffer(regulation_group: RegulationGroup, plan_id: str | None = None) -> str | None:
    group_id = regulation_group.id_
    editing = group_id is not None
    if group_id is None or regulation_group.modified:
        layer = RegulationGroupLayer.get_from_project()
        feature = RegulationGroupLayer.feature_from_model(regulation_group, plan_id)
        if not layer.isEditable():
            QgsProject.instance().startEditing(layer)

        if not add_to_edit_buffer(
            feature=feature,
            layer=layer,
            id_=group_id,
            edit_text="Kaavamääräysryhmän muokkaus" if editing else "Kaavamääräysryhmän lisäys",
        ):
            iface.messageBar().pushCritical("", "Kaavamääräysryhmän tallentaminen epäonnistui.")
            return None
        group_id = cast(str, feature["id"])

    if editing:
        # Check for regulations to be deleted
        regulation_layer = PlanRegulationLayer.get_from_project()
        for reg_feature in PlanRegulationLayer.get_regulations_to_delete(regulation_group.regulations, group_id):
            if not delete_in_edit_buffer(reg_feature, regulation_layer, "Kaavamääräyksen poisto"):
                iface.messageBar().pushCritical("", "Kaavamääräyksen poistaminen epäonnistui.")

        # Check for propositions to be deleted
        proposition_layer = PlanPropositionLayer.get_from_project()
        for prop_feature in PlanPropositionLayer.get_propositions_to_delete(regulation_group.propositions, group_id):
            if not delete_in_edit_buffer(prop_feature, proposition_layer, "Kaavasuosituksen poisto"):
                iface.messageBar().pushCritical("", "Kaavasuosituksen poistaminen epäonnistui.")

    # Save regulations
    if regulation_group.regulations:
        for regulation in regulation_group.regulations:
            regulation.regulation_group_id = group_id  # Updating regulation group ID
            add_regulation_to_edit_buffer(regulation)

    # Save propositions
    if regulation_group.propositions:
        for proposition in regulation_group.propositions:
            proposition.regulation_group_id = group_id  # Updating regulation group ID
            add_proposition_to_edit_buffer(proposition)

    return group_id


def delete_regulation_group(regulation_group: RegulationGroup, plan_id: str | None = None) -> bool:
    if regulation_group.id_ is None:
        iface.messageBar().pushCritical("", "Kaavamääräysryhmän poistaminen epäonnistui (ei IDtä).")
        return False

    feature = RegulationGroupLayer.feature_from_model(regulation_group, plan_id)
    layer = RegulationGroupLayer.get_from_project()
    if not layer.isEditable():
        QgsProject.instance().startEditing(layer)

    if not delete_in_edit_buffer(feature, layer, "Kaavamääräysryhmän poisto"):
        iface.messageBar().pushCritical("", "Kaavamääräysryhmän poistaminen epäonnistui.")
        return False

    return True


def save_regulation_group_association(regulation_group_id: str, layer_name: str, feature_id: str) -> bool:
    add_regulation_group_association_to_edit_buffer(regulation_group_id, layer_name, feature_id)
    result, _ = QgsProject.instance().commitChanges(stopEditing=False)
    return result


def add_regulation_group_association_to_edit_buffer(regulation_group_id: str, layer_name: str, feature_id: str) -> bool:
    if RegulationGroupAssociationLayer.association_exists(regulation_group_id, layer_name, feature_id):
        return True
    feature = RegulationGroupAssociationLayer.feature_from(regulation_group_id, layer_name, feature_id)
    layer = RegulationGroupAssociationLayer.get_from_project()
    if not layer.isEditable():
        QgsProject.instance().startEditing(layer)

    if not add_to_edit_buffer(
        feature=feature, layer=layer, id_=None, edit_text="Kaavamääräysryhmän assosiaation lisäys"
    ):
        iface.messageBar().pushCritical("", "Kaavamääräysryhmän assosiaation tallentaminen epäonnistui.")
        return False

    return True


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
            iface.messageBar().pushCritical("", "Kaavamääräyksen tallentaminen epäonnistui.")
            return None
        reg_id = cast(str, regulation_feature["id"])

    if editing:
        # Check for additional information to be deleted
        info_layer = AdditionalInformationLayer.get_from_project()
        for info_feature in AdditionalInformationLayer.get_additional_information_to_delete(
            regulation.additional_information, reg_id
        ):
            if not delete_in_edit_buffer(info_feature, info_layer, "Lisätiedon poisto"):
                iface.messageBar().pushCritical("", "Liätiedon poistaminen epäonnistui.")

        # Check for verbal regulation types to be deleted
        for association in TypeOfVerbalRegulationAssociationLayer.get_dangling_associations(
            reg_id, regulation.verbal_regulation_type_ids
        ):
            if not delete_in_edit_buffer(
                association,
                TypeOfVerbalRegulationAssociationLayer.get_from_project(),
                "Sanallisen kaavamääräyksen lajin assosiaation poisto",
            ):
                iface.messageBar().pushCritical(
                    "", "Sanallisen kaavamääräyksen lajin assosiaation poistaminen epäonnistui."
                )

        # Check for plan theme to be deleted
        for association in PlanThemeAssociationLayer.get_dangling_regulation_associations(reg_id, regulation.theme_ids):
            if not delete_in_edit_buffer(
                association, PlanThemeAssociationLayer.get_from_project(), "Kaavoitusteeman assosiaation poisto"
            ):
                iface.messageBar().pushCritical("", "Kaavoitusteeman assosiaation poistaminen epäonnistui.")

    for additional_information in regulation.additional_information:
        additional_information.plan_regulation_id = reg_id
        add_additional_information_to_edit_buffer(additional_information)

    for verbal_regulation_type_id in regulation.verbal_regulation_type_ids:
        add_type_of_verbal_regulation_association_to_edit_buffer(reg_id, verbal_regulation_type_id)

    for plan_theme_id in regulation.theme_ids:
        add_plan_theme_association_to_edit_buffer(plan_theme_id=plan_theme_id, regulation_id=reg_id)

    return reg_id


def add_plan_theme_association_to_edit_buffer(
    plan_theme_id: str, regulation_id: str | None = None, proposition_id: str | None = None
) -> bool:
    if regulation_id is not None and PlanThemeAssociationLayer.regulation_association_exists(
        plan_theme_id=plan_theme_id, plan_regulation_id=regulation_id
    ):
        return True

    if proposition_id is not None and PlanThemeAssociationLayer.proposition_association_exists(
        plan_theme_id=plan_theme_id, plan_proposition_id=proposition_id
    ):
        return True
    feature = PlanThemeAssociationLayer.feature_from(
        plan_theme_id=plan_theme_id, plan_regulation_id=regulation_id, plan_proposition_id=proposition_id
    )
    layer = PlanThemeAssociationLayer.get_from_project()
    if not layer.isEditable():
        QgsProject.instance().startEditing(layer)

    if not add_to_edit_buffer(feature=feature, layer=layer, id_=None, edit_text="Kaavoitusteeman assosiaation lisäys"):
        iface.messageBar().pushCritical("", "Kaavoitusteeman assosiaation tallentaminen epäonnistui.")
        return False

    return True


def add_type_of_verbal_regulation_association_to_edit_buffer(
    regulation_id: str, verbal_regulation_type_id: str
) -> bool:
    if TypeOfVerbalRegulationAssociationLayer.association_exists(regulation_id, verbal_regulation_type_id):
        return True
    feature = TypeOfVerbalRegulationAssociationLayer.feature_from(regulation_id, verbal_regulation_type_id)
    layer = TypeOfVerbalRegulationAssociationLayer.get_from_project()
    if not layer.isEditable():
        QgsProject.instance().startEditing(layer)

    if not add_to_edit_buffer(
        feature=feature, layer=layer, id_=None, edit_text="Sanallisen kaavamääräyksen lajin assosiaation lisäys"
    ):
        iface.messageBar().pushCritical("", "Sanallisen kaavamääräyksen lajin assosiaation tallentaminen epäonnistui.")
        return False

    return True


def add_legal_effect_association_to_edit_buffer(plan_id: str, legal_effect_id: str) -> bool:
    if LegalEffectAssociationLayer.association_exists(plan_id, legal_effect_id):
        return True
    feature = LegalEffectAssociationLayer.feature_from(plan_id, legal_effect_id)
    layer = LegalEffectAssociationLayer.get_from_project()
    if not layer.isEditable():
        QgsProject.instance().startEditing(layer)

    if not add_to_edit_buffer(
        feature=feature, layer=layer, id_=None, edit_text="Oikeusvaikutuksen assosiaation lisäys"
    ):
        iface.messageBar().pushCritical("", "Oikeusvaikutuksen assosiaation tallentaminen epäonnistui.")
        return False

    return True


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
        iface.messageBar().pushCritical("", "Lisätiedon tallentaminen epäonnistui.")
        return None

    return feature["id"]


def delete_additional_information(additional_information: AdditionalInformation) -> bool:
    feature = AdditionalInformationLayer.feature_from_model(additional_information)
    layer = AdditionalInformationLayer.get_from_project()
    if not layer.isEditable():
        QgsProject.instance().startEditing(layer)

    if not delete_in_edit_buffer(feature, layer, "Lisätiedon poisto"):
        iface.messageBar().pushCritical("", "Lisätiedon poistaminen epäonnistui.")
        return False

    return True


def delete_regulation(regulation: Regulation) -> bool:
    feature = PlanRegulationLayer.feature_from_model(regulation)
    layer = PlanRegulationLayer.get_from_project()
    if not layer.isEditable():
        QgsProject.instance().startEditing(layer)

    if not delete_in_edit_buffer(feature, layer, "Kaavamääräyksen poisto"):
        iface.messageBar().pushCritical("", "Lisätiedon poistaminen epäonnistui.")
        return False

    return True


def add_proposition_to_edit_buffer(proposition: Proposition) -> str | None:
    prop_id = proposition.id_
    editing = prop_id is not None
    if proposition.id_ is not None and not proposition.modified:
        return proposition.id_

    feature = PlanPropositionLayer.feature_from_model(proposition)
    layer = PlanPropositionLayer.get_from_project()
    if not layer.isEditable():
        QgsProject.instance().startEditing(layer)

    if not add_to_edit_buffer(
        feature=feature,
        layer=layer,
        id_=prop_id,
        edit_text="Kaavasuosituksen lisäys" if prop_id is None else "Kaavasuosituksen muokkaus",
    ):
        iface.messageBar().pushCritical("", "Kaavasuosituksen tallentaminen epäonnistui.")
        return None
    prop_id = cast(str, feature["id"])

    if editing:
        # Check for plan theme to be deleted
        for association in PlanThemeAssociationLayer.get_dangling_proposition_associations(
            prop_id, proposition.theme_ids
        ):
            if not delete_in_edit_buffer(
                association, PlanThemeAssociationLayer.get_from_project(), "Kaavoitusteeman assosiaation poisto"
            ):
                iface.messageBar().pushCritical("", "Kaavoitusteeman assosiaation poistaminen epäonnistui.")

    for plan_theme_id in proposition.theme_ids:
        add_plan_theme_association_to_edit_buffer(plan_theme_id=plan_theme_id, proposition_id=prop_id)

    return feature["id"]


def delete_proposition(proposition: Proposition) -> bool:
    feature = PlanPropositionLayer.feature_from_model(proposition)
    layer = PlanPropositionLayer.get_from_project()
    if not layer.isEditable():
        QgsProject.instance().startEditing(layer)

    if not delete_in_edit_buffer(feature, layer, "Kaavasuosituksen poisto"):
        iface.messageBar().pushCritical("", "Kaavasuosituksen poistaminen epäonnistui.")
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
        iface.messageBar().pushCritical("", "Asiakirjan tallentaminen epäonnistui.")
        return None

    return feature["id"]
