"""Model equality decides whether a form save writes a row. Empty form fields must equal empty database values."""

from __future__ import annotations

from arho_feature_template.core.models import RegulationGroup


def test_an_empty_letter_code_equals_a_missing_one():
    assert RegulationGroup(letter_code="") == RegulationGroup(letter_code=None)
    assert RegulationGroup(letter_code="").letter_code is None


def test_empty_heading_languages_are_dropped():
    assert RegulationGroup(heading={"fin": "Asuinalue", "swe": ""}) == RegulationGroup(heading={"fin": "Asuinalue"})
    assert RegulationGroup(heading={"fin": "", "swe": ""}).heading is None
    assert RegulationGroup(heading={}).heading is None


def test_changed_fields_names_the_differences():
    stored = RegulationGroup(heading={"fin": "A"}, letter_code="A", group_number=1)
    edited = RegulationGroup(heading={"fin": "B"}, letter_code="A", group_number=2)

    assert edited.changed_fields(stored) == ["heading", "group_number"]
    assert stored.changed_fields(stored) == []
