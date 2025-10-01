from __future__ import annotations

from typing import TYPE_CHECKING, cast

from arho_feature_template.project.layers.plan_layers import (
    AdditionalInformationLayer,
    DocumentLayer,
    LegalEffectAssociationLayer,
    LifeCycleLayer,
    PlanLayer,
    PlanPropositionLayer,
    PlanRegulationLayer,
    PlanThemeAssociationLayer,
    RegulationGroupAssociationLayer,
    RegulationGroupLayer,
    TypeOfVerbalRegulationAssociationLayer,
    get_plan_feature_layer_class_by_model,
)
from arho_feature_template.utils.misc_utils import (
    iface,
    use_wait_cursor,
)

if TYPE_CHECKING:
    from qgis.core import QgsFeature, QgsVectorLayer

    from arho_feature_template.core.models import (
        AdditionalInformation,
        Document,
        LifeCycle,
        Plan,
        PlanFeature,
        Proposition,
        Regulation,
        RegulationGroup,
    )


def save_feature(feature: QgsFeature, layer: QgsVectorLayer, id_: str | None, edit_text: str = "") -> bool:
    if not layer.isEditable():
        layer.startEditing()
    layer.beginEditCommand(edit_text)

    if id_ is None:
        layer.addFeature(feature)
    else:
        layer.updateFeature(feature)

    layer.endEditCommand()
    return layer.commitChanges(stopEditing=False)


def delete_feature(feature: QgsFeature, layer: QgsVectorLayer, delete_text: str = "") -> bool:
    if not layer.isEditable():
        layer.startEditing()
    layer.beginEditCommand(delete_text)

    layer.deleteFeature(feature.id())

    layer.endEditCommand()
    return layer.commitChanges(stopEditing=False)


@use_wait_cursor
def save_plan(plan: Plan) -> str | None:
    plan_id = plan.id_
    editing = plan_id is not None
    if plan_id is None or plan.modified:
        feature = PlanLayer.feature_from_model(plan)
        if not save_feature(
            feature=feature,
            layer=PlanLayer.get_from_project(),
            id_=plan_id,
            edit_text="Kaavan muokkaus" if editing else "Kaavan luominen",
        ):
            iface.messageBar().pushCritical("", "Kaavan tallentaminen epäonnistui")
            return None
        plan_id = cast(str, feature["id"])

    if editing:
        # Check for deleted general regulations
        for association in RegulationGroupAssociationLayer.get_dangling_associations(
            plan.general_regulations, plan_id, PlanLayer.name
        ):
            if not delete_feature(
                association,
                RegulationGroupAssociationLayer.get_from_project(),
                "Kaavamääräysryhmän assosiaation poisto",
            ):
                iface.messageBar().pushCritical("", "Kaavamääräysryhmän assosiaation poistaminen epäonnistui.")

        # Check for deleted legal effects
        for association in LegalEffectAssociationLayer.get_dangling_associations(plan_id, plan.legal_effect_ids):
            if not delete_feature(
                association, LegalEffectAssociationLayer.get_from_project(), "Oikeusvaikutuksen assosiaation poisto"
            ):
                iface.messageBar().pushCritical("", "Oikeusvaikutuksen assosiaation poistaminen epäonnistui.")

        # Check for documents to be deleted
        doc_layer = DocumentLayer.get_from_project()
        for doc_feature in DocumentLayer.get_documents_to_delete(plan.documents, plan_id):
            if not delete_feature(doc_feature, doc_layer, "Asiakirjan poisto"):
                iface.messageBar().pushCritical("", "Asiakirjan poistaminen epäonnistui.")

    # Save general regulations
    if plan.general_regulations:
        for regulation_group in plan.general_regulations:
            group_id = save_regulation_group(regulation_group, plan_id)
            if group_id is None:
                continue  # Skip association saving if saving regulation group failed
            save_regulation_group_association(group_id, PlanLayer.name, plan_id)

    # Save legal effect associations
    for legal_effect_id in plan.legal_effect_ids:
        save_legal_effect_association(plan_id, legal_effect_id)

    # Save documents
    for document in plan.documents:
        document.plan_id = plan_id
        save_document(document)

    # Save lifecycles
    for lifecycle in plan.lifecycles:
        lifecycle.plan_id = plan_id
        save_lifecycle(lifecycle)

    return plan_id


@use_wait_cursor
def save_plan_feature(plan_feature: PlanFeature, plan_id: str | None = None) -> str | None:
    layer_class = get_plan_feature_layer_class_by_model(plan_feature)
    layer_name = cast(str, plan_feature.layer_name)

    feat_id = plan_feature.id_
    editing = feat_id is not None
    if feat_id is None or plan_feature.modified:
        feature = layer_class.feature_from_model(plan_feature, plan_id)
        if not save_feature(
            feature=feature,
            layer=layer_class.get_from_project(),
            id_=feat_id,
            edit_text="Kaavakohteen muokkaus" if editing else "Kaavakohteen lisäys",
        ):
            iface.messageBar().pushCritical("", "Kaavakohteen tallentaminen epäonnistui.")
            return None
        feat_id = cast(str, feature["id"])

    if editing:
        # Check for deleted regulation groups
        for association in RegulationGroupAssociationLayer.get_dangling_associations(
            plan_feature.regulation_groups, feat_id, layer_name
        ):
            if not delete_feature(
                association,
                RegulationGroupAssociationLayer.get_from_project(),
                "Kaavamääräysryhmän assosiaation poisto",
            ):
                iface.messageBar().pushCritical("", "Kaavamääräysryhmän assosiaation poistaminen epäonnistui.")

    # Save regulation groups
    for group in plan_feature.regulation_groups:
        group_id = save_regulation_group(group)
        if group_id is None:
            continue  # Skip association saving if saving regulation group failed
        save_regulation_group_association(group_id, layer_name, feat_id)

    return feat_id


@use_wait_cursor
def save_regulation_group(regulation_group: RegulationGroup, plan_id: str | None = None) -> str | None:
    group_id = regulation_group.id_
    editing = group_id is not None
    if group_id is None or regulation_group.modified:
        feature = RegulationGroupLayer.feature_from_model(regulation_group, plan_id)
        if not save_feature(
            feature=feature,
            layer=RegulationGroupLayer.get_from_project(),
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
            if not delete_feature(reg_feature, regulation_layer, "Kaavamääräyksen poisto"):
                iface.messageBar().pushCritical("", "Kaavamääräyksen poistaminen epäonnistui.")

        # Check for propositions to be deleted
        proposition_layer = PlanPropositionLayer.get_from_project()
        for prop_feature in PlanPropositionLayer.get_propositions_to_delete(regulation_group.propositions, group_id):
            if not delete_feature(prop_feature, proposition_layer, "Kaavasuosituksen poisto"):
                iface.messageBar().pushCritical("", "Kaavasuosituksen poistaminen epäonnistui.")

    # Save regulations
    if regulation_group.regulations:
        for regulation in regulation_group.regulations:
            regulation.regulation_group_id = group_id  # Updating regulation group ID
            save_regulation(regulation)

    # Save propositions
    if regulation_group.propositions:
        for proposition in regulation_group.propositions:
            proposition.regulation_group_id = group_id  # Updating regulation group ID
            save_proposition(proposition)

    return group_id


@use_wait_cursor
def delete_regulation_group(regulation_group: RegulationGroup, plan_id: str | None = None) -> bool:
    if regulation_group.id_ is None:
        iface.messageBar().pushCritical("", "Kaavamääräysryhmän poistaminen epäonnistui (ei IDtä).")
        return False

    feature = RegulationGroupLayer.feature_from_model(regulation_group, plan_id)
    layer = RegulationGroupLayer.get_from_project()

    if not delete_feature(feature, layer, "Kaavamääräysryhmän poisto"):
        iface.messageBar().pushCritical("", "Kaavamääräysryhmän poistaminen epäonnistui.")
        return False

    return True


def save_regulation_group_association(regulation_group_id: str, layer_name: str, feature_id: str) -> bool:
    if RegulationGroupAssociationLayer.association_exists(regulation_group_id, layer_name, feature_id):
        return True
    feature = RegulationGroupAssociationLayer.feature_from(regulation_group_id, layer_name, feature_id)
    layer = RegulationGroupAssociationLayer.get_from_project()

    if not save_feature(feature=feature, layer=layer, id_=None, edit_text="Kaavamääräysryhmän assosiaation lisäys"):
        iface.messageBar().pushCritical("", "Kaavamääräysryhmän assosiaation tallentaminen epäonnistui.")
        return False

    return True


def save_regulation(regulation: Regulation) -> str | None:
    reg_id = regulation.id_
    editing = reg_id is not None
    if reg_id is None or regulation.modified:
        regulation_feature = PlanRegulationLayer.feature_from_model(regulation)
        if not save_feature(
            feature=regulation_feature,
            layer=PlanRegulationLayer.get_from_project(),
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
            if not delete_feature(info_feature, info_layer, "Lisätiedon poisto"):
                iface.messageBar().pushCritical("", "Liätiedon poistaminen epäonnistui.")

        # Check for verbal regulation types to be deleted
        for association in TypeOfVerbalRegulationAssociationLayer.get_dangling_associations(
            reg_id, regulation.verbal_regulation_type_ids
        ):
            if not delete_feature(
                association,
                TypeOfVerbalRegulationAssociationLayer.get_from_project(),
                "Sanallisen kaavamääräyksen lajin assosiaation poisto",
            ):
                iface.messageBar().pushCritical(
                    "", "Sanallisen kaavamääräyksen lajin assosiaation poistaminen epäonnistui."
                )

        # Check for plan theme to be deleted
        for association in PlanThemeAssociationLayer.get_dangling_regulation_associations(reg_id, regulation.theme_ids):
            if not delete_feature(
                association, PlanThemeAssociationLayer.get_from_project(), "Kaavoitusteeman assosiaation poisto"
            ):
                iface.messageBar().pushCritical("", "Kaavoitusteeman assosiaation poistaminen epäonnistui.")

    for additional_information in regulation.additional_information:
        additional_information.plan_regulation_id = reg_id
        save_additional_information(additional_information)

    for verbal_regulation_type_id in regulation.verbal_regulation_type_ids:
        save_type_of_verbal_regulation_association(reg_id, verbal_regulation_type_id)

    for plan_theme_id in regulation.theme_ids:
        save_plan_theme_association(plan_theme_id=plan_theme_id, regulation_id=reg_id)

    return reg_id


def save_plan_theme_association(
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

    if not save_feature(feature=feature, layer=layer, id_=None, edit_text="Kaavoitusteeman assosiaation lisäys"):
        iface.messageBar().pushCritical("", "Kaavoitusteeman assosiaation tallentaminen epäonnistui.")
        return False

    return True


def save_type_of_verbal_regulation_association(regulation_id: str, verbal_regulation_type_id: str) -> bool:
    if TypeOfVerbalRegulationAssociationLayer.association_exists(regulation_id, verbal_regulation_type_id):
        return True
    feature = TypeOfVerbalRegulationAssociationLayer.feature_from(regulation_id, verbal_regulation_type_id)
    layer = TypeOfVerbalRegulationAssociationLayer.get_from_project()

    if not save_feature(
        feature=feature, layer=layer, id_=None, edit_text="Sanallisen kaavamääräyksen lajin assosiaation lisäys"
    ):
        iface.messageBar().pushCritical("", "Sanallisen kaavamääräyksen lajin assosiaation tallentaminen epäonnistui.")
        return False

    return True


def save_legal_effect_association(plan_id: str, legal_effect_id: str) -> bool:
    if LegalEffectAssociationLayer.association_exists(plan_id, legal_effect_id):
        return True
    feature = LegalEffectAssociationLayer.feature_from(plan_id, legal_effect_id)
    layer = LegalEffectAssociationLayer.get_from_project()

    if not save_feature(feature=feature, layer=layer, id_=None, edit_text="Oikeusvaikutuksen assosiaation lisäys"):
        iface.messageBar().pushCritical("", "Oikeusvaikutuksen assosiaation tallentaminen epäonnistui.")
        return False

    return True


def save_additional_information(additional_information: AdditionalInformation) -> str | None:
    if additional_information.id_ is not None and not additional_information.modified:
        return additional_information.id_

    feature = AdditionalInformationLayer.feature_from_model(additional_information)
    if not save_feature(
        feature=feature,
        layer=AdditionalInformationLayer.get_from_project(),
        id_=additional_information.id_,
        edit_text="Lisätiedon lisäys" if additional_information.id_ is None else "Lisätiedon muokkaus",
    ):
        iface.messageBar().pushCritical("", "Lisätiedon tallentaminen epäonnistui.")
        return None

    return feature["id"]


def delete_additional_information(additional_information: AdditionalInformation) -> bool:
    feature = AdditionalInformationLayer.feature_from_model(additional_information)
    layer = AdditionalInformationLayer.get_from_project()

    if not delete_feature(feature, layer, "Lisätiedon poisto"):
        iface.messageBar().pushCritical("", "Lisätiedon poistaminen epäonnistui.")
        return False

    return True


def delete_regulation(regulation: Regulation) -> bool:
    feature = PlanRegulationLayer.feature_from_model(regulation)
    layer = PlanRegulationLayer.get_from_project()

    if not delete_feature(feature, layer, "Kaavamääräyksen poisto"):
        iface.messageBar().pushCritical("", "Lisätiedon poistaminen epäonnistui.")
        return False

    return True


def save_proposition(proposition: Proposition) -> str | None:
    prop_id = proposition.id_
    editing = prop_id is not None
    if proposition.id_ is not None and not proposition.modified:
        return proposition.id_

    feature = PlanPropositionLayer.feature_from_model(proposition)
    if not save_feature(
        feature=feature,
        layer=PlanPropositionLayer.get_from_project(),
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
            if not delete_feature(
                association, PlanThemeAssociationLayer.get_from_project(), "Kaavoitusteeman assosiaation poisto"
            ):
                iface.messageBar().pushCritical("", "Kaavoitusteeman assosiaation poistaminen epäonnistui.")

    for plan_theme_id in proposition.theme_ids:
        save_plan_theme_association(plan_theme_id=plan_theme_id, proposition_id=prop_id)

    return feature["id"]


def delete_proposition(proposition: Proposition) -> bool:
    feature = PlanPropositionLayer.feature_from_model(proposition)
    layer = PlanPropositionLayer.get_from_project()

    if not delete_feature(feature, layer, "Kaavasuosituksen poisto"):
        iface.messageBar().pushCritical("", "Kaavasuosituksen poistaminen epäonnistui.")
        return False

    return True


def save_document(document: Document) -> str | None:
    if document.id_ is not None and not document.modified:
        return document.id_

    feature = DocumentLayer.feature_from_model(document)
    if not save_feature(
        feature=feature,
        layer=DocumentLayer.get_from_project(),
        id_=document.id_,
        edit_text="Asiakirjan lisäys" if document.id_ is None else "Asiakirjan muokkaus",
    ):
        iface.messageBar().pushCritical("", "Asiakirjan tallentaminen epäonnistui.")
        return None

    return feature["id"]


def save_lifecycle(lifecycle: LifeCycle) -> str | None:
    if lifecycle.id_ is not None and not lifecycle.modified:
        return lifecycle.id_

    feature = LifeCycleLayer.feature_from_model(lifecycle)
    if not save_feature(
        feature=feature,
        layer=LifeCycleLayer.get_from_project(),
        id_=lifecycle.id_,
        edit_text="Elinkaaren lisäys" if lifecycle.id_ is None else "Elinkaaren muokkaus",
    ):
        iface.messageBar().pushCritical("", "Elinkaaren tallentaminen epäonnistui.")
        return None

    return feature["id"]
