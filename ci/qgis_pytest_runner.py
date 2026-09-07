"""Run pytest inside the real QGIS application.

QGIS executes this file with ``qgis --code``, so it runs in the embedded Python of the
running application. ``qgis.utils.iface`` is the real ``QgisAppInterface`` here, and
``tests/conftest.py`` notices that and skips its own QGIS start-up and fake interface.

Usage (inside a ``qgis/qgis`` container, repository mounted at ``/tests_directory``)::

    qgis --nologo --noversioncheck --code ci/qgis_pytest_runner.py

Pass pytest arguments in ``QGIS_PYTEST_ARGS``; the default is the whole ``tests``
directory, where tests that need the fake interface skip themselves::

    QGIS_PYTEST_ARGS="tests/test_smoke_in_qgis.py -x" qgis ... --code ci/qgis_pytest_runner.py

The process exits with the pytest exit code, so no output scraping is needed. This
replaces the ``qgis_testrunner.sh`` / ``qgis_testrunner.py`` pair that ships in the image:
those need ``unittest`` with a ``run_all()`` entry point, they need ``unbuffer`` (missing
from the image), and they decide pass or fail by grepping the output.
"""

from __future__ import annotations

import os
import shlex
import sys

from qgis.utils import iface

if iface is None:
    sys.stderr.write("qgis_pytest_runner.py must be run by QGIS: qgis --code <this file>\n")
    raise SystemExit(2)

from qgis.core import QgsProject, QgsProjectBadLayerHandler


class SilentBadLayerHandler(QgsProjectBadLayerHandler):
    """Keep a broken project from opening a modal dialog that would hang the run."""

    def handleBadLayers(self, layers, dom=None):  # noqa: N802 (Qt override)
        pass


def _pytest_args() -> list[str]:
    args = shlex.split(os.environ.get("QGIS_PYTEST_ARGS", "tests"))
    # Never write .pytest_cache into the mounted repository as root.
    return ["-p", "no:cacheprovider", *args]


def _use_pinned_pytest() -> None:
    """Prefer the pytest that ci/qgis_docker_setup.sh installed over the distro one."""
    deps_dir = os.environ.get("ARHO_TEST_DEPS", "/opt/arho-test-deps")
    if os.path.isdir(deps_dir) and deps_dir not in sys.path:
        sys.path.insert(0, deps_dir)


def run_tests() -> None:
    QgsProject.instance().setBadLayerHandler(SilentBadLayerHandler())
    _use_pinned_pytest()

    import pytest

    sys.stderr.write(f"qgis_pytest_runner: pytest {pytest.__version__} inside QGIS\n")
    sys.stderr.flush()
    exit_code = int(pytest.main(_pytest_args()))

    sys.stdout.flush()
    sys.stderr.flush()
    # QGIS is fully started, so a normal quit would run teardown and could hang or lose
    # the exit code. Leave immediately with the pytest result instead.
    os._exit(exit_code)


# Wait until the plugins are loaded before touching them.
iface.initializationCompleted.connect(run_tests)
