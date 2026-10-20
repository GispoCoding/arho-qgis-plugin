"""Workaround for qgis/QGIS#65323: json and jsonb values are lost in a multi-feature insert.

The PostgreSQL provider loses the values when one insert batch holds two or more features whose
values differ: it binds a map as an empty string and the column ends up NULL. A single feature, or
equal values, go into the SQL as a literal and work. Fixed on master by qgis/QGIS#66478 (QGIS 4.2)
and in the 3.44 LTR point release 3.44.16.

The only entry point is `commit_changes`. On a QGIS with the bug it takes the json values out of the
new features of every multi-feature insert, commits the inserts, then writes the values back as updates and commits again.

To drop this workaround, once the plugin requires QGIS 3.44.16 or newer:
- delete this file and `tests/test_json_insert_workaround.py`
- in `feature_editing.commit_edit_buffer` call `project.commitChanges(stopEditing=stop_editing)` again
- in `PlanObjectsDock`, use `created_object_models.pop(feat_id)` without a default again
- delete `FailingProject.mapLayers` in `tests/test_save_diff.py`
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, cast

from qgis.core import (
    Qgis,
    QgsExpression,
    QgsFeatureRequest,
    QgsFields,
    QgsProject,
    QgsUnsetAttributeValue,
    QgsVariantUtils,
    QgsVectorLayer,
)

logger = logging.getLogger(__name__)

# 3.44.16 is the first fixed 3.x release, 4.2 the first fixed 4.x release
IS_NEEDED = not (34416 <= Qgis.QGIS_VERSION_INT < 40000 or Qgis.QGIS_VERSION_INT >= 40200)  # noqa: PLR2004
JSON_FIELD_TYPE_NAMES = ("json", "jsonb")


@dataclass(frozen=True)
class DeferredJsonValue:
    """A json value taken out of a new feature before the insert, written back after it."""

    layer: QgsVectorLayer
    id_: str
    """Value of the `id` column of the new feature, the key after the commit gives it a new fid."""
    field_index: int
    value: Any


def commit_changes(project: QgsProject, stop_editing: bool) -> tuple[bool, list[str]]:  # noqa: FBT001
    """Like `project.commitChanges(stopEditing=...)`, but keeps the json values of multi-feature inserts."""
    deferred = defer_json_values(project) if IS_NEEDED else []
    result, errors = project.commitChanges(stopEditing=stop_editing and not deferred)
    if result and deferred:
        # The rows exist now; a second commit writes the json values with the safe update path
        restored = apply_deferred_json_values(deferred)
        result, second_errors = project.commitChanges(stopEditing=stop_editing)
        errors = [*errors, *second_errors]
        result = result and restored
    return result, errors


def _is_unset(value: Any) -> bool:
    return QgsVariantUtils.isNull(value) or isinstance(value, QgsUnsetAttributeValue)


def _json_field_indexes(fields: QgsFields) -> list[int]:
    return [
        idx
        for idx in range(fields.count())
        if fields.fieldOrigin(idx) == QgsFields.FieldOrigin.OriginProvider
        and fields[idx].typeName().lower() in JSON_FIELD_TYPE_NAMES
    ]


def defer_json_values(project: QgsProject) -> list[DeferredJsonValue]:
    """Strip every json value from the new features of the inserts that hold two or more features.

    Each set value is replaced by the column default, so the batch takes the safe literal path.
    The values are returned for `apply_deferred_json_values` to write back once the rows exist.
    """
    deferred: list[DeferredJsonValue] = []
    for layer in project.mapLayers().values():
        if not isinstance(layer, QgsVectorLayer) or not layer.isEditable():
            continue
        edit_buffer = layer.editBuffer()
        added = edit_buffer.addedFeatures() if edit_buffer else {}
        fields = layer.fields()
        if len(added) < 2 or fields.indexOf("id") < 0:  # noqa: PLR2004
            continue
        provider = layer.dataProvider()
        layer.beginEditCommand("Json-arvojen siirto")
        for idx in _json_field_indexes(fields):
            clause = provider.defaultValueClause(fields.fieldOriginIndex(idx)) if provider else ""
            placeholder = QgsUnsetAttributeValue(clause) if clause else None
            for fid, feature in added.items():
                if _is_unset(feature[idx]):
                    continue
                deferred.append(DeferredJsonValue(layer, cast(str, feature["id"]), idx, feature[idx]))
                layer.changeAttributeValue(fid, idx, placeholder)
        layer.endEditCommand()
    logger.debug("Deferred json values count=%s", len(deferred))
    return deferred


def apply_deferred_json_values(deferred: list[DeferredJsonValue]) -> bool:
    """Put the deferred json values back on the committed rows. Needs a second commit."""
    by_layer: dict[str, dict[str, dict[int, Any]]] = defaultdict(lambda: defaultdict(dict))
    layers: dict[str, QgsVectorLayer] = {}
    for item in deferred:
        layers[item.layer.id()] = item.layer
        by_layer[item.layer.id()][item.id_][item.field_index] = item.value

    result = True
    for layer_id, values_by_id in by_layer.items():
        layer = layers[layer_id]
        ids = ", ".join(QgsExpression.quotedValue(id_) for id_ in values_by_id)
        request = QgsFeatureRequest().setFilterExpression(f'"id" IN ({ids})')
        request.setFlags(Qgis.FeatureRequestFlag.NoGeometry)
        found: set[str] = set()
        layer.beginEditCommand("Json-arvojen palautus")
        for feature in layer.getFeatures(request):
            id_ = cast(str, feature["id"])
            found.add(id_)
            for idx, value in values_by_id[id_].items():
                if not layer.changeAttributeValue(feature.id(), idx, value):
                    result = False
        layer.endEditCommand()
        missing = set(values_by_id) - found
        if missing:
            logger.error("Deferred json values lost, rows not found layer=%s ids=%s", layer.name(), sorted(missing))
            result = False
        logger.debug("Restored deferred json values layer=%s rows=%s", layer.name(), len(found))
    return result
