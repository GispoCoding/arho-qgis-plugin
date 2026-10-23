"""Library files carry a `format_version`; older files are upgraded when read."""

from __future__ import annotations

from typing import TYPE_CHECKING

import yaml

from arho_feature_template.core.template_manager import LIBRARY_FORMAT_VERSION, TemplateManager

if TYPE_CHECKING:
    from pathlib import Path

    from tests.fake_iface import MessageRecorder


def _write(path: Path, data: dict) -> Path:
    path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    return path


def _library_errors(messages: MessageRecorder) -> list[tuple[str, str]]:
    """The library errors on the message bar. Inside QGIS the bar also shows unrelated Qt messages."""
    return [message for message in messages.criticals if message[1].startswith("Kirjasto")]


def test_a_format_1_plan_object_library_is_upgraded(tmp_path: Path, messages: MessageRecorder):
    path = _write(
        tmp_path / "old.yaml",
        {"name": "Old", "library_type": "plan_feature", "plan_features": [{"layer_name": "Aluevaraus"}]},
    )

    data = TemplateManager.read_library_config_file(path, "plan_object")

    assert data["library_type"] == "plan_object"
    assert data["plan_objects"] == [{"layer_name": "Aluevaraus"}]
    assert "plan_features" not in data
    assert data["format_version"] == LIBRARY_FORMAT_VERSION
    assert _library_errors(messages) == []


def test_a_format_2_plan_object_library_is_read_as_is(tmp_path: Path, messages: MessageRecorder):
    content = {
        "format_version": 2,
        "name": "New",
        "library_type": "plan_object",
        "plan_objects": [{"layer_name": "Piste"}],
    }
    path = _write(tmp_path / "new.yaml", content)

    assert TemplateManager.read_library_config_file(path, "plan_object") == content
    assert _library_errors(messages) == []


def test_a_regulation_group_library_without_a_format_version_is_read(tmp_path: Path, messages: MessageRecorder):
    path = _write(tmp_path / "groups.yaml", {"name": "Groups", "library_type": "regulation_group"})

    data = TemplateManager.read_library_config_file(path, "regulation_group")

    assert data["library_type"] == "regulation_group"
    assert _library_errors(messages) == []


def test_a_newer_format_is_refused(tmp_path: Path, messages: MessageRecorder):
    path = _write(
        tmp_path / "future.yaml",
        {"format_version": LIBRARY_FORMAT_VERSION + 1, "name": "Future", "library_type": "plan_object"},
    )

    assert TemplateManager.read_library_config_file(path, "plan_object") == {}
    assert len(_library_errors(messages)) == 1


def test_a_written_plan_object_library_has_the_current_format(tmp_path: Path):
    path = tmp_path / "written.yaml"

    TemplateManager.write_plan_object_template_file({"name": "Written", "plan_objects": []}, path)

    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == f"format_version: {LIBRARY_FORMAT_VERSION}"
    assert yaml.safe_load("\n".join(lines))["library_type"] == "plan_object"


def test_a_written_regulation_group_library_has_the_current_format(tmp_path: Path):
    path = tmp_path / "groups.yaml"

    TemplateManager.write_regulation_group_template_file({"name": "Groups"}, path)

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert data["format_version"] == LIBRARY_FORMAT_VERSION
    assert data["library_type"] == "regulation_group"
