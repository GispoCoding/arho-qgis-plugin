"""Module for importing valid plans from the Ryhti WFS service.

The Ryhti WFS service publishes valid plans as open data. The importer
queries the plan layers with the bounding box of a municipality or an
administrative region geometry and creates a plan matter and a plan for
each returned feature. Plan documents attached to the features are not
imported.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import date
from typing import TYPE_CHECKING, Any, Literal

from geoalchemy2.shape import from_shape, to_shape
from owslib.wfs import WebFeatureService
from pydantic import BaseModel, model_validator
from shapely.geometry import shape as shapely_shape
from sqlalchemy import or_, select

from database import codes, models
from database.base import PROJECT_SRID
from database.codes import get_code
from ryhti_client.deserializer import Deserializer

if TYPE_CHECKING:
    from sqlalchemy.orm import Session, sessionmaker

LOGGER = logging.getLogger(__name__)

WFS_PLAN_TYPENAMES = (
    "ryhti_plan:pub_valid_ld_plan_ix_gs",
    "ryhti_plan:pub_valid_lm_plan_ix_gs",
)
WFS_PAGE_SIZE = 1000
# The plan layers are published in EPSG:3067, the same as PROJECT_SRID.
WFS_BBOX_CRS = "urn:ogc:def:crs:EPSG::3067"

LANGUAGE_CODES = ("fin", "swe", "smn", "sms", "sme", "eng")

type Bbox = tuple[float, float, float, float]
type ImportOutcome = Literal["imported", "skipped_existing", "skipped_no_organisation"]


class AreaNotFoundError(Exception):
    def __init__(self, area_code: str) -> None:
        self.area_code = area_code
        super().__init__(f"Area '{area_code}' does not exist.")


class AreaGeometryMissingError(Exception):
    def __init__(self, area_code: str) -> None:
        self.area_code = area_code
        super().__init__(
            f"Area '{area_code}' has no geometry. Run mml_loader to load "
            "municipality and region geometries first."
        )


class ImportWfsPlansData(BaseModel):
    municipality_code: str | None = None
    region_code: str | None = None

    @model_validator(mode="after")
    def check_exactly_one_area(self) -> ImportWfsPlansData:
        if self.municipality_code is None and self.region_code is None:
            raise ValueError("Either municipality_code or region_code is required.")
        if self.municipality_code is not None and self.region_code is not None:
            raise ValueError(
                "Only one of municipality_code and region_code is allowed."
            )
        return self


def _language_dict(properties: dict[str, Any], prefix: str) -> dict[str, str]:
    """Collect e.g. name_fin/name_swe/... properties into a language dict."""
    return {
        lang: text
        for lang in LANGUAGE_CODES
        if (text := properties.get(f"{prefix}_{lang}"))
    }


def _json_string_list(value: str | None) -> list[str]:
    """Parse a JSON-encoded list property such as '["140"]', dropping nulls."""
    if not value:
        return []
    return [str(item) for item in json.loads(value) if item is not None]


def _parse_wfs_date(value: str | None) -> date | None:
    """Parse a WFS date property such as '1983-02-02Z'."""
    if not value:
        return None
    return date.fromisoformat(value.removesuffix("Z"))


class WfsPlanFeature(BaseModel):
    """One plan feature parsed from a ryhti_plan WFS layer."""

    id: str
    plan_key: str
    permanent_plan_identifier: str | None
    producer_plan_identifier: str | None
    plan_type: str
    plan_life_cycle_status: str
    digital_origin: str
    administrative_area_identifiers: list[str]
    case_identifiers: list[str]
    record_numbers: list[str]
    name: dict[str, str]
    description: dict[str, str] | None
    approval_date: date | None
    period_of_validity_begin: date | None
    period_of_validity_end: date | None
    geometry: dict[str, Any]

    @classmethod
    def from_geojson_feature(cls, feature: dict[str, Any]) -> WfsPlanFeature:
        properties = feature["properties"]
        name = _language_dict(properties, "name")
        if not name:
            # Plan and plan matter names may not be empty in the database.
            fallback = (
                properties.get("permanent_plan_identifier")
                or properties.get("producer_plan_identifier")
                or properties["plan_key"]
            )
            name = {"fin": str(fallback)}
        return cls(
            id=properties["id"],
            plan_key=properties["plan_key"],
            permanent_plan_identifier=properties.get("permanent_plan_identifier"),
            producer_plan_identifier=properties.get("producer_plan_identifier"),
            plan_type=properties.get("plan_type") or "",
            plan_life_cycle_status=properties.get("plan_life_cycle_status") or "",
            digital_origin=properties.get("digital_origin") or "",
            administrative_area_identifiers=_json_string_list(
                properties.get("administrative_area_identifiers")
            ),
            case_identifiers=_json_string_list(properties.get("case_identifiers")),
            record_numbers=_json_string_list(properties.get("record_numbers")),
            name=name,
            description=_language_dict(properties, "description") or None,
            approval_date=_parse_wfs_date(properties.get("approval_date")),
            period_of_validity_begin=_parse_wfs_date(
                properties.get("period_of_validity_begin")
            ),
            period_of_validity_end=_parse_wfs_date(
                properties.get("period_of_validity_end")
            ),
            geometry=feature["geometry"],
        )


class WfsPlanClient:
    """Fetches plan features from the Ryhti WFS service with OWSLib."""

    def __init__(self, url: str) -> None:
        self.url = url

    def get_plan_features(self, bbox: Bbox) -> list[WfsPlanFeature]:
        """Fetch all plan features intersecting the bounding box."""
        # Constructing the service does a GetCapabilities request, so only do
        # it when features are actually fetched.
        wfs = WebFeatureService(url=self.url, version="2.0.0")
        features: list[WfsPlanFeature] = []
        for typename in WFS_PLAN_TYPENAMES:
            features.extend(self._get_layer_features(wfs, typename, bbox))
        return features

    def _get_layer_features(
        self, wfs: Any, typename: str, bbox: Bbox
    ) -> list[WfsPlanFeature]:
        features: list[WfsPlanFeature] = []
        start_index = 0
        while True:
            response = wfs.getfeature(
                typename=[typename],
                bbox=(*bbox, WFS_BBOX_CRS),
                outputFormat="application/json",
                startindex=start_index,
                maxfeatures=WFS_PAGE_SIZE,
            )
            page = json.load(response)
            page_features = page["features"]
            features.extend(
                WfsPlanFeature.from_geojson_feature(feature)
                for feature in page_features
            )
            LOGGER.info(
                "Fetched %s of %s features from %s.",
                len(features),
                page.get("numberMatched", "unknown"),
                typename,
            )
            if len(page_features) < WFS_PAGE_SIZE:
                return features
            start_index += len(page_features)


@dataclass
class WfsImportResult:
    total_features: int = 0
    imported: int = 0
    skipped_existing: int = 0
    skipped_no_organisation: int = 0
    filtered_out: int = 0
    failed: int = 0

    def to_details(self) -> dict[str, Any]:
        return asdict(self)


class WfsPlanImporter:
    """Imports WFS plan features as plan matters and plans."""

    def __init__(
        self, session_factory: sessionmaker[Session], wfs_client: WfsPlanClient
    ) -> None:
        self.session_factory = session_factory
        self.wfs_client = wfs_client

    def import_plans(
        self, data: ImportWfsPlansData, overwrite: bool = False
    ) -> WfsImportResult:
        """Import all plans of a municipality or an administrative region.

        Queries the WFS with the bounding box of the area geometry. Since the
        bounding box also covers parts of the neighboring areas, features are
        further filtered by their administrative area identifiers.
        """
        result = WfsImportResult()

        with self.session_factory() as session:
            area = self._get_area(session, data)
            allowed_area_codes = self._get_allowed_area_codes(session, data)
            bbox: Bbox = to_shape(area.geom).bounds

        features = self.wfs_client.get_plan_features(bbox)
        result.total_features = len(features)

        with self.session_factory(autoflush=False, expire_on_commit=False) as session:
            deserializer = Deserializer(session)
            organisation_cache: dict[str, models.Organisation | None] = {}
            for feature in features:
                if not allowed_area_codes & set(
                    feature.administrative_area_identifiers
                ):
                    result.filtered_out += 1
                    continue
                try:
                    outcome = self._import_feature(
                        session, deserializer, organisation_cache, feature, overwrite
                    )
                    session.commit()
                except Exception:
                    LOGGER.exception("Failed to import plan %s.", feature.plan_key)
                    session.rollback()
                    result.failed += 1
                    continue
                if outcome == "imported":
                    result.imported += 1
                elif outcome == "skipped_existing":
                    result.skipped_existing += 1
                elif outcome == "skipped_no_organisation":
                    result.skipped_no_organisation += 1

        LOGGER.info("WFS plan import done: %s", result.to_details())
        return result

    def _get_area(
        self, session: Session, data: ImportWfsPlansData
    ) -> codes.Municipality | codes.AdministrativeRegion:
        area: codes.Municipality | codes.AdministrativeRegion | None
        if data.municipality_code is not None:
            area_code = data.municipality_code
            area = get_code(session, codes.Municipality, area_code)
        elif data.region_code is not None:
            area_code = data.region_code
            area = get_code(session, codes.AdministrativeRegion, area_code)
        else:
            # ImportWfsPlansData validation guarantees one of the codes is set.
            raise ValueError("Either municipality_code or region_code is required.")

        if area is None:
            raise AreaNotFoundError(area_code)
        if area.geom is None:
            raise AreaGeometryMissingError(area_code)
        return area

    def _get_allowed_area_codes(
        self, session: Session, data: ImportWfsPlansData
    ) -> set[str]:
        """Return the administrative area identifiers accepted for the import.

        A feature listing only its region code is not visible to a
        municipality-scoped import.
        """
        if data.municipality_code is not None:
            return {data.municipality_code}
        if data.region_code is None:
            # ImportWfsPlansData validation guarantees one of the codes is set.
            raise ValueError("Either municipality_code or region_code is required.")
        # There is no foreign key between the code tables, so the
        # municipalities of the region are resolved spatially.
        municipality_codes = session.scalars(
            select(codes.Municipality.value)
            .join(
                codes.AdministrativeRegion,
                codes.AdministrativeRegion.geom.ST_Contains(
                    codes.Municipality.geom.ST_PointOnSurface()
                ),
            )
            .where(codes.AdministrativeRegion.value == data.region_code)
        ).all()
        return {data.region_code, *municipality_codes}

    def _import_feature(
        self,
        session: Session,
        deserializer: Deserializer,
        organisation_cache: dict[str, models.Organisation | None],
        feature: WfsPlanFeature,
        overwrite: bool,
    ) -> ImportOutcome:
        existing_plan = session.get(models.Plan, feature.plan_key)
        existing_plan_matter = session.get(models.PlanMatter, feature.id)
        if (existing_plan is not None or existing_plan_matter is not None) and (
            not overwrite
        ):
            return "skipped_existing"
        if existing_plan is not None:
            # The existing plan may hang off a different plan matter than the
            # one this feature would create. Delete whichever matter is left
            # without plans, so re-imports do not leave orphan plan matters.
            old_plan_matter = existing_plan.plan_matter
            session.delete(existing_plan)
            session.flush()
            if old_plan_matter is not None and not old_plan_matter.plans:
                session.delete(old_plan_matter)
                session.flush()
        # Re-fetch: the plan matter may just have been deleted above.
        existing_plan_matter = session.get(models.PlanMatter, feature.id)

        organisation = self._get_organisation(session, organisation_cache, feature)
        if organisation is None:
            return "skipped_no_organisation"

        plan_type_id = deserializer.get_code_id_from_uri(feature.plan_type)
        if plan_type_id is None:
            raise ValueError(f"Unknown plan type: '{feature.plan_type}'")
        lifecycle_status_id = deserializer.get_code_id_from_uri(
            feature.plan_life_cycle_status
        )
        if lifecycle_status_id is None:
            raise ValueError(
                f"Unknown lifecycle status: '{feature.plan_life_cycle_status}'"
            )
        digital_origin_id = deserializer.get_code_id_from_uri(feature.digital_origin)
        if digital_origin_id is None:
            raise ValueError(f"Unknown digital origin: '{feature.digital_origin}'")

        multi_geom = deserializer.convert_to_multi_geom(shapely_shape(feature.geometry))
        plan = models.Plan(
            id=feature.plan_key,
            name=feature.name,
            description=feature.description,
            approval_date=feature.approval_date,
            geom=from_shape(multi_geom, srid=PROJECT_SRID),
            lifecycle_status_id=lifecycle_status_id,
            period_of_validity_start=feature.period_of_validity_begin,
            period_of_validity_end=feature.period_of_validity_end,
        )
        if existing_plan_matter is not None:
            # The plan matter survived the overwrite because it still has
            # other plans. Attach the re-imported plan to it.
            plan_matter = existing_plan_matter
        else:
            plan_matter = models.PlanMatter(
                id=feature.id,
                name=feature.name,
                description=feature.description,
                permanent_plan_identifier=feature.permanent_plan_identifier,
                producers_plan_identifier=feature.producer_plan_identifier,
                case_identifier=self._first_value(
                    feature, "case_identifiers", feature.case_identifiers
                ),
                record_number=self._first_value(
                    feature, "record_numbers", feature.record_numbers
                ),
                digital_origin_id=digital_origin_id,
                plan_type_id=plan_type_id,
                organisation_id=organisation.id,
            )
        plan_matter.plans.append(plan)
        session.add(plan_matter)
        return "imported"

    def _get_organisation(
        self,
        session: Session,
        organisation_cache: dict[str, models.Organisation | None],
        feature: WfsPlanFeature,
    ) -> models.Organisation | None:
        identifier = self._first_value(
            feature,
            "administrative_area_identifiers",
            feature.administrative_area_identifiers,
        )
        if identifier is None:
            LOGGER.warning(
                "Plan %s has no administrative area identifiers, skipping.",
                feature.plan_key,
            )
            return None

        if identifier in organisation_cache:
            return organisation_cache[identifier]

        organisations = (
            session.scalars(
                select(models.Organisation)
                .outerjoin(models.Organisation.municipality)
                .join(models.Organisation.administrative_region)
                .where(
                    or_(
                        codes.Municipality.value == identifier,
                        codes.AdministrativeRegion.value == identifier,
                    )
                )
            )
            .unique()
            .all()
        )
        if not organisations:
            LOGGER.warning(
                "No organisation found for administrative area '%s'.", identifier
            )
            organisation = None
        elif len(organisations) == 1:
            organisation = organisations[0]
        else:
            LOGGER.warning(
                "Multiple organisations found for administrative area '%s', "
                "using the first one.",
                identifier,
            )
            organisation = organisations[0]

        organisation_cache[identifier] = organisation
        return organisation

    def _first_value(
        self, feature: WfsPlanFeature, field_name: str, values: list[str]
    ) -> str | None:
        if not values:
            return None
        if len(values) > 1:
            LOGGER.warning(
                "Plan %s has multiple %s %s, using the first one.",
                feature.plan_key,
                field_name,
                values,
            )
        return values[0]
