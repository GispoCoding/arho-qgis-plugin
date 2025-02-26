import os
from typing import Callable

import pytest
from requests_mock.request import _RequestObjectProxy
from sqlalchemy.orm import Session

from database import codes
from lambdas.mml_loader.mml_loader import MMLLoader


@pytest.fixture()
def mock_mml(requests_mock):
    def match_request_body(request: _RequestObjectProxy):
        return request.json() == {
            "id": "hallinnolliset_aluejaot_vektori_koko_suomi",
            "inputs": {
                "fileFormatInput": "GML",
                "dataSetInput": "kuntajako_250k",
                "yearInput": 2023,
            },
        }

    requests_mock.post(
        "https://avoin-paikkatieto.maanmittauslaitos.fi/tiedostopalvelu/ogcproc/v1/processes/hallinnolliset_aluejaot_vektori_koko_suomi/execution?api-key=mock_apikey",
        json={"jobID": "whatever"},
        request_headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        additional_matcher=match_request_body,
        status_code=200,
    )
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "test_mml_loader_geom.zip"
    )
    with open(path, "rb") as zip_file:
        requests_mock.get(
            "https://avoin-paikkatieto.maanmittauslaitos.fi/tiedostopalvelu/dl/v1/whatever/TietoaKuntajaosta_2023_250k.zip",
            body=zip_file,
            headers={
                "Content-Type": "application/zip",
            },
            status_code=200,
        )
        yield


@pytest.fixture()
def loader(
    admin_connection_string: str,
    municipality_instance: codes.Municipality,
    administrative_region_instance: codes.AdministrativeRegion,
) -> MMLLoader:
    return MMLLoader(admin_connection_string, api_key="mock_apikey")


def test_get_geometries(mock_mml: Callable, loader: MMLLoader):
    geoms = loader.get_geometries()
    assert len(geoms) == 2


def test_save_geometries(
    session: Session,
    mock_mml: Callable,
    loader: MMLLoader,
    municipality_instance: codes.Municipality,
    administrative_region_instance: codes.AdministrativeRegion,
):
    geoms = loader.get_geometries()
    msg = loader.save_geometries(geoms)
    assert msg == "2 inserted or updated. 0 deleted."
    session.refresh(municipality_instance)
    session.refresh(administrative_region_instance)
    assert municipality_instance.geom
    assert administrative_region_instance.geom
