import json
import logging
from datetime import date
from pathlib import Path
from typing import Any

import pytest
from geoalchemy2.shape import from_shape, to_shape
from requests_mock import Mocker
from shapely.geometry import MultiPolygon, box
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from database import codes, models
from database.base import PROJECT_SRID
from ryhti_client.wfs_importer import (
    AreaGeometryMissingError,
    AreaNotFoundError,
    Bbox,
    ImportWfsPlansData,
    WfsPlanClient,
    WfsPlanFeature,
    WfsPlanImporter,
)

MOCK_WFS_URL = "http://mock.wfs.url/wfs"

PLAN_TYPE_URI = "http://uri.suomi.fi/codelist/rytj/RY_Kaavalaji/code/11"
LIFECYCLE_URI = "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/13"
DIGITAL_ORIGIN_URI = "http://uri.suomi.fi/codelist/rytj/RY_DigitaalinenAlkupera/code/04"

PLAN_MATTER_ID_1 = "8f4645a3-6cd0-4e90-b503-5fa7c3366251"
PLAN_KEY_1 = "e4fd71e7-522a-41e3-9356-058fdaf8d298"
PLAN_MATTER_ID_2 = "d81862d3-1c43-4b02-8a3b-c8892ee2d7ff"
PLAN_KEY_2 = "6493b731-e942-4c42-a6f5-4a11e10cbe33"
PLAN_MATTER_ID_3 = "76639ce9-4e5c-4611-a2ae-a087f1a17ae2"
PLAN_KEY_3 = "40a54a87-c363-4a37-91bb-2f5f71fe7a53"

# EPSG:3067 coordinates: the municipality is inside the region, and the plan
# geometry is inside the municipality.
REGION_GEOM = MultiPolygon([box(380000, 6670000, 400000, 6690000)])
MUNICIPALITY_GEOM = MultiPolygon([box(381000, 6671000, 389000, 6679000)])
PLAN_GEOMETRY = {
    "type": "Polygon",
    "coordinates": [
        [
            [382000, 6672000],
            [383000, 6672000],
            [383000, 6673000],
            [382000, 6673000],
            [382000, 6672000],
        ]
    ],
}


def make_raw_feature(
    plan_matter_id: str = PLAN_MATTER_ID_1,
    plan_key: str = PLAN_KEY_1,
    **property_overrides: Any,
) -> dict[str, Any]:
    """Build a GeoJSON feature with the properties of the ryhti_plan layers."""
    properties: dict[str, Any] = {
        "id": plan_matter_id,
        "plan_key": plan_key,
        "permanent_plan_identifier": "AK-000081",
        "producer_plan_identifier": "AK 170",
        "plan_type": PLAN_TYPE_URI,
        "plan_type_name_fin": "Asemakaava",
        "original_administrative_area_identifiers": '["577"]',
        "administrative_area_identifiers": '["577"]',
        "name_fin": "Asemakaava AK 170",
        "name_swe": None,
        "name_eng": None,
        "description_fin": "Geometrian lähde: kunta.",
        "description_swe": None,
        "case_identifiers": '["case-1"]',
        "record_numbers": '["record-1"]',
        "time_of_initiation": "1900-01-01Z",
        "digital_origin": DIGITAL_ORIGIN_URI,
        "date_of_validity": None,
        "approval_date": "1983-02-02Z",
        "plan_life_cycle_status": LIFECYCLE_URI,
        "period_of_validity_begin": "1990-01-01Z",
        "period_of_validity_end": None,
        "documents": "[]",
    }
    properties.update(property_overrides)
    return {
        "type": "Feature",
        "id": f"pub_valid_ld_plan_ix_gs.{plan_matter_id}",
        "geometry": PLAN_GEOMETRY,
        "geometry_name": "geographical_area",
        "properties": properties,
    }


def make_feature(
    plan_matter_id: str = PLAN_MATTER_ID_1,
    plan_key: str = PLAN_KEY_1,
    **property_overrides: Any,
) -> WfsPlanFeature:
    return WfsPlanFeature.from_geojson_feature(
        make_raw_feature(plan_matter_id, plan_key, **property_overrides)
    )


class StubWfsClient(WfsPlanClient):
    """WFS client stub that returns canned features without HTTP requests."""

    def __init__(self, features: list[WfsPlanFeature]) -> None:
        super().__init__(MOCK_WFS_URL)
        self.features = features
        self.bboxes: list[Bbox] = []

    def get_plan_features(self, bbox: Bbox) -> list[WfsPlanFeature]:
        self.bboxes.append(bbox)
        return list(self.features)


@pytest.fixture
def session_factory(
    dba_connection_string: str, hame_database_migrated: str | None
) -> sessionmaker[Session]:
    engine = create_engine(dba_connection_string)
    return sessionmaker(bind=engine)


@pytest.fixture
def municipality_with_geom(
    session: Session, municipality_instance: codes.Municipality
) -> codes.Municipality:
    municipality_instance.geom = from_shape(MUNICIPALITY_GEOM, srid=PROJECT_SRID)
    session.commit()
    return municipality_instance


@pytest.fixture
def region_with_geom(
    session: Session, administrative_region_instance: codes.AdministrativeRegion
) -> codes.AdministrativeRegion:
    administrative_region_instance.geom = from_shape(REGION_GEOM, srid=PROJECT_SRID)
    session.commit()
    return administrative_region_instance


@pytest.fixture
def municipality_organisation(
    temp_session_feature,
    municipality_instance: codes.Municipality,
    administrative_region_instance: codes.AdministrativeRegion,
) -> models.Organisation:
    instance = models.Organisation(
        business_id="mun-org",
        municipality=municipality_instance,
        administrative_region=administrative_region_instance,
    )
    return temp_session_feature(instance)


def test_import_wfs_plans_data_requires_exactly_one_area() -> None:
    with pytest.raises(ValueError):
        ImportWfsPlansData.model_validate({})
    with pytest.raises(ValueError):
        ImportWfsPlansData.model_validate(
            {"municipality_code": "577", "region_code": "01"}
        )


def test_wfs_plan_feature_parsing() -> None:
    feature = make_feature()
    assert feature.id == PLAN_MATTER_ID_1
    assert feature.plan_key == PLAN_KEY_1
    assert feature.permanent_plan_identifier == "AK-000081"
    assert feature.producer_plan_identifier == "AK 170"
    assert feature.administrative_area_identifiers == ["577"]
    assert feature.case_identifiers == ["case-1"]
    assert feature.record_numbers == ["record-1"]
    assert feature.name == {"fin": "Asemakaava AK 170"}
    assert feature.description == {"fin": "Geometrian lähde: kunta."}
    assert feature.digital_origin == DIGITAL_ORIGIN_URI
    assert feature.approval_date == date(1983, 2, 2)
    assert feature.period_of_validity_begin == date(1990, 1, 1)
    assert feature.period_of_validity_end is None
    assert feature.geometry == PLAN_GEOMETRY


def test_wfs_plan_feature_name_fallback() -> None:
    feature = make_feature(name_fin=None, description_fin=None)
    assert feature.name == {"fin": "AK-000081"}
    assert feature.description is None


def test_import_plans_for_municipality(
    session: Session,
    session_factory: sessionmaker[Session],
    plan_type_instance: codes.PlanType,
    valid_status_instance: codes.LifeCycleStatus,
    digital_origin_instance: codes.DigitalOrigin,
    municipality_with_geom: codes.Municipality,
    municipality_organisation: models.Organisation,
):
    wfs_client = StubWfsClient([make_feature()])
    importer = WfsPlanImporter(session_factory, wfs_client)

    result = importer.import_plans(ImportWfsPlansData(municipality_code="577"))

    assert result.total_features == 1
    assert result.imported == 1
    assert result.failed == 0
    assert wfs_client.bboxes == [to_shape(municipality_with_geom.geom).bounds]

    plan_matter = session.get(models.PlanMatter, PLAN_MATTER_ID_1)
    assert plan_matter is not None
    assert plan_matter.name == {"fin": "Asemakaava AK 170"}
    assert plan_matter.description == {"fin": "Geometrian lähde: kunta."}
    assert plan_matter.permanent_plan_identifier == "AK-000081"
    assert plan_matter.producers_plan_identifier == "AK 170"
    assert plan_matter.case_identifier == "case-1"
    assert plan_matter.record_number == "record-1"
    assert plan_matter.plan_type.value == "11"
    assert plan_matter.digital_origin.value == "04"
    assert plan_matter.organisation_id == municipality_organisation.id

    plan = session.get(models.Plan, PLAN_KEY_1)
    assert plan is not None
    assert plan.plan_matter_id == PLAN_MATTER_ID_1
    assert plan.name == {"fin": "Asemakaava AK 170"}
    assert plan.description == {"fin": "Geometrian lähde: kunta."}
    assert plan.lifecycle_status.value == "13"
    assert plan.approval_date == date(1983, 2, 2)
    assert plan.period_of_validity_start == date(1990, 1, 1)
    assert plan.period_of_validity_end is None
    assert plan.locked is True
    geom = to_shape(plan.geom)
    assert geom.geom_type == "MultiPolygon"
    assert geom.bounds == (382000.0, 6672000.0, 383000.0, 6673000.0)


def test_import_plans_for_region(
    session: Session,
    session_factory: sessionmaker[Session],
    plan_type_instance: codes.PlanType,
    valid_status_instance: codes.LifeCycleStatus,
    digital_origin_instance: codes.DigitalOrigin,
    region_with_geom: codes.AdministrativeRegion,
    municipality_with_geom: codes.Municipality,
    organisation_instance: models.Organisation,
    municipality_organisation: models.Organisation,
):
    features = [
        # In a municipality of the region.
        make_feature(PLAN_MATTER_ID_1, PLAN_KEY_1),
        # In a neighboring municipality that the bounding box also covers.
        make_feature(
            PLAN_MATTER_ID_2, PLAN_KEY_2, administrative_area_identifiers='["999"]'
        ),
        # A regional plan listing the region code itself.
        make_feature(
            PLAN_MATTER_ID_3, PLAN_KEY_3, administrative_area_identifiers='["01"]'
        ),
    ]
    importer = WfsPlanImporter(session_factory, StubWfsClient(features))

    result = importer.import_plans(ImportWfsPlansData(region_code="01"))

    assert result.total_features == 3
    assert result.imported == 2
    assert result.filtered_out == 1
    assert session.get(models.Plan, PLAN_KEY_1) is not None
    assert session.get(models.Plan, PLAN_KEY_2) is None
    plan_3 = session.get(models.Plan, PLAN_KEY_3)
    assert plan_3 is not None
    assert plan_3.plan_matter.organisation_id == organisation_instance.id


def test_import_skips_feature_without_organisation(
    session: Session,
    session_factory: sessionmaker[Session],
    plan_type_instance: codes.PlanType,
    valid_status_instance: codes.LifeCycleStatus,
    digital_origin_instance: codes.DigitalOrigin,
    municipality_with_geom: codes.Municipality,
    caplog: pytest.LogCaptureFixture,
):
    importer = WfsPlanImporter(session_factory, StubWfsClient([make_feature()]))

    with caplog.at_level(logging.WARNING):
        result = importer.import_plans(ImportWfsPlansData(municipality_code="577"))

    assert result.imported == 0
    assert result.skipped_no_organisation == 1
    assert "No organisation found for administrative area '577'." in caplog.text
    assert session.get(models.Plan, PLAN_KEY_1) is None
    assert session.get(models.PlanMatter, PLAN_MATTER_ID_1) is None


def test_import_existing_plan_skipped_and_overwritten(
    session: Session,
    session_factory: sessionmaker[Session],
    plan_type_instance: codes.PlanType,
    valid_status_instance: codes.LifeCycleStatus,
    digital_origin_instance: codes.DigitalOrigin,
    municipality_with_geom: codes.Municipality,
    municipality_organisation: models.Organisation,
):
    importer = WfsPlanImporter(session_factory, StubWfsClient([make_feature()]))
    data = ImportWfsPlansData(municipality_code="577")

    first_result = importer.import_plans(data)
    assert first_result.imported == 1

    second_result = importer.import_plans(data)
    assert second_result.imported == 0
    assert second_result.skipped_existing == 1

    original_created = session.scalars(
        select(models.Plan.created_at).where(models.Plan.id == PLAN_KEY_1)
    ).one()
    overwrite_result = importer.import_plans(data, overwrite=True)
    assert overwrite_result.imported == 1
    overwritten_created = session.scalars(
        select(models.Plan.created_at).where(models.Plan.id == PLAN_KEY_1)
    ).one()
    assert original_created is not None
    assert overwritten_created is not None
    assert original_created < overwritten_created

    # The overwrite must not leave orphan plan matters behind.
    plan_matter_ids = session.scalars(select(models.PlanMatter.id)).all()
    assert plan_matter_ids == [PLAN_MATTER_ID_1]


def test_import_uses_first_of_multiple_identifiers(
    session: Session,
    session_factory: sessionmaker[Session],
    plan_type_instance: codes.PlanType,
    valid_status_instance: codes.LifeCycleStatus,
    digital_origin_instance: codes.DigitalOrigin,
    municipality_with_geom: codes.Municipality,
    municipality_organisation: models.Organisation,
    caplog: pytest.LogCaptureFixture,
):
    features = [make_feature(administrative_area_identifiers='["577", "999"]')]
    importer = WfsPlanImporter(session_factory, StubWfsClient(features))

    with caplog.at_level(logging.WARNING):
        result = importer.import_plans(ImportWfsPlansData(municipality_code="577"))

    assert result.imported == 1
    assert "multiple administrative_area_identifiers" in caplog.text
    plan_matter = session.get(models.PlanMatter, PLAN_MATTER_ID_1)
    assert plan_matter is not None
    assert plan_matter.organisation_id == municipality_organisation.id


def test_import_counts_failed_features(
    session: Session,
    session_factory: sessionmaker[Session],
    plan_type_instance: codes.PlanType,
    valid_status_instance: codes.LifeCycleStatus,
    digital_origin_instance: codes.DigitalOrigin,
    municipality_with_geom: codes.Municipality,
    municipality_organisation: models.Organisation,
):
    unknown_plan_type = "http://uri.suomi.fi/codelist/rytj/RY_Kaavalaji/code/99"
    features = [
        make_feature(PLAN_MATTER_ID_1, PLAN_KEY_1, plan_type=unknown_plan_type),
        make_feature(PLAN_MATTER_ID_2, PLAN_KEY_2),
    ]
    importer = WfsPlanImporter(session_factory, StubWfsClient(features))

    result = importer.import_plans(ImportWfsPlansData(municipality_code="577"))

    assert result.failed == 1
    assert result.imported == 1
    assert session.get(models.Plan, PLAN_KEY_1) is None
    assert session.get(models.Plan, PLAN_KEY_2) is not None


def test_import_unknown_area(session_factory: sessionmaker[Session]):
    importer = WfsPlanImporter(session_factory, StubWfsClient([]))
    with pytest.raises(AreaNotFoundError):
        importer.import_plans(ImportWfsPlansData(municipality_code="000"))


def test_import_area_without_geometry(
    session_factory: sessionmaker[Session], municipality_instance: codes.Municipality
):
    importer = WfsPlanImporter(session_factory, StubWfsClient([]))
    with pytest.raises(AreaGeometryMissingError):
        importer.import_plans(ImportWfsPlansData(municipality_code="577"))


def test_wfs_plan_client_paging(requests_mock: Mocker, monkeypatch: pytest.MonkeyPatch):
    """The client fetches both layers and pages through large results."""
    monkeypatch.setattr("ryhti_client.wfs_importer.WFS_PAGE_SIZE", 2)
    capabilities = (Path(__file__).parent / "wfs_capabilities.xml").read_text(
        encoding="utf-8"
    )
    ld_features = [
        make_raw_feature(PLAN_MATTER_ID_1, PLAN_KEY_1),
        make_raw_feature(PLAN_MATTER_ID_2, PLAN_KEY_2),
        make_raw_feature(PLAN_MATTER_ID_3, PLAN_KEY_3),
    ]

    def wfs_response(request, context) -> str:
        query = request.qs
        if query["request"] == ["getcapabilities"]:
            return capabilities
        assert query["request"] == ["getfeature"]
        assert query["outputformat"] == ["application/json"]
        assert query["bbox"] == ["0,0,10,10,urn:ogc:def:crs:epsg::3067"]
        assert query["count"] == ["2"]
        if query["typenames"] == ["ryhti_plan:pub_valid_ld_plan_ix_gs"]:
            start_index = int(query.get("startindex", ["0"])[0])
            page = ld_features[start_index : start_index + 2]
        elif query["typenames"] == ["ryhti_plan:pub_valid_lm_plan_ix_gs"]:
            page = []
        else:
            pytest.fail(f"Unexpected typenames: {query['typenames']}")
        return json.dumps(
            {
                "type": "FeatureCollection",
                "features": page,
                "numberMatched": len(ld_features),
                "numberReturned": len(page),
            }
        )

    requests_mock.get(MOCK_WFS_URL, text=wfs_response)

    features = WfsPlanClient(MOCK_WFS_URL).get_plan_features((0, 0, 10, 10))

    assert [feature.plan_key for feature in features] == [
        PLAN_KEY_1,
        PLAN_KEY_2,
        PLAN_KEY_3,
    ]
