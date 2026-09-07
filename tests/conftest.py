"""Session bootstrap and shared fixtures for the plugin tests.

The suite runs in two places.

**Normal run** (``pytest tests``): QGIS starts headless through ``qgis.testing.start_app()``
and a ``FakeQgisInterface`` (see ``tests/fake_iface.py``) is installed as
``qgis.utils.iface`` in ``pytest_configure``, before pytest collects the test modules,
because the plugin binds ``qgis.utils.iface`` at import time. Tests get that one fake
through the ``iface`` fixture and rely on ``reset()`` between tests; it is never swapped.

**Inside the real QGIS application** (``ci/qgis_pytest_runner.py`` under ``qgis --code``):
the application and the real ``QgisAppInterface`` already exist, so nothing is started or
faked and the ``iface`` fixture hands out the real interface.

Markers pick the tests that fit the current mode:

* ``real_qgis``  - only inside the QGIS application (skipped in a normal run).
* ``fake_iface`` - only with the fake interface (skipped inside the application).

Do not install pytest-qgis: it starts a second ``QgsApplication``.

Generic fixtures: ``qgis_app``, ``iface``, ``messages``, ``canvas``, ``new_project``.
Plugin fixtures: ``plugin_factory``, ``plugin``.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Callable, Iterator

import pytest
import qgis.utils
from qgis.PyQt.QtCore import QT_VERSION, QCoreApplication

if TYPE_CHECKING:
    from qgis.core import QgsApplication, QgsProject
    from qgis.gui import QgisInterface, QgsMapCanvas

    from arho_feature_template.plugin import Plugin
    from tests.fake_iface import MessageRecorder

# QGIS sets qgis.utils.iface only inside the running application. Read it before anything
# else can assign it, so the mode is settled for the whole session.
RUNNING_INSIDE_QGIS_APP = qgis.utils.iface is not None

if not RUNNING_INSIDE_QGIS_APP:
    # Both must be decided before the first Qt window and before pytest-qt picks a backend.
    # The QGIS 3 Python ships PyQt5 and PyQt6 side by side; pytest-qt would guess PyQt6.
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    os.environ.setdefault("PYTEST_QT_API", "pyqt6" if QT_VERSION >= 0x060000 else "pyqt5")

_FAKE_IFACE_KEY = pytest.StashKey["object"]()


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "real_qgis: only runs inside the real QGIS application")
    config.addinivalue_line("markers", "fake_iface: needs the FakeQgisInterface, not the real one")

    if RUNNING_INSIDE_QGIS_APP:
        return

    if config.pluginmanager.has_plugin("pytest_qgis"):
        msg = (
            "pytest-qgis is installed. It starts its own QgsApplication and clashes with "
            "this conftest. Run `pip uninstall pytest-qgis` (or `pytest -p no:pytest_qgis`)."
        )
        raise pytest.UsageError(msg)

    from qgis.core import QgsApplication

    if QgsApplication.instance() is not None:
        msg = "A QApplication exists before tests/conftest.py could start QGIS."
        raise pytest.UsageError(msg)

    # QGIS 4 start_app() sets these; QGIS 3 does not. QgsSettings needs them.
    QCoreApplication.setOrganizationName("QGIS")
    QCoreApplication.setOrganizationDomain("qgis.org")
    QCoreApplication.setApplicationName("QGIS-TEST")

    from qgis.testing import start_app

    # start_app() points QGIS_CUSTOM_CONFIG_PATH at a fresh temp profile (QGIS 3 and 4)
    # and removes it at exit, so plugin settings and logs never touch the user profile.
    start_app()

    from tests.fake_iface import FakeQgisInterface

    qgis.utils.iface = FakeQgisInterface()
    config.stash[_FAKE_IFACE_KEY] = qgis.utils.iface


def pytest_unconfigure(config: pytest.Config) -> None:
    fake = config.stash.get(_FAKE_IFACE_KEY, None)
    if fake is not None:
        # Delete the widgets while QgsApplication is still alive; exitQgis() runs at exit.
        fake.shutdown()
        qgis.utils.iface = None


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Skip whatever does not fit the interface this session has."""
    if RUNNING_INSIDE_QGIS_APP:
        skip = pytest.mark.skip(reason="needs the fake interface; this runs inside QGIS")
        marker = "fake_iface"
    else:
        skip = pytest.mark.skip(reason="needs the real QGIS application; run ci/qgis_pytest_runner.py")
        marker = "real_qgis"
    for item in items:
        if item.get_closest_marker(marker) is not None:
            item.add_marker(skip)


# --------------------------------------------------------------------- generic


@pytest.fixture(scope="session")
def qgis_app() -> QgsApplication:
    from qgis.core import QgsApplication

    app = QgsApplication.instance()
    assert app is not None
    return app


@pytest.fixture(scope="session")
def iface(qgis_app: QgsApplication) -> QgisInterface:  # noqa: ARG001 (dependency only)
    """The fake interface, or the real one when running inside the QGIS application."""
    return qgis.utils.iface


@pytest.fixture(scope="session")
def _message_recorder(iface: QgisInterface) -> MessageRecorder:
    """One recorder on the message bar. The fake brings its own; the real one gets a new one."""
    from tests.fake_iface import MessageRecorder

    recorder = getattr(iface, "messages", None)
    return recorder if recorder is not None else MessageRecorder(iface.messageBar())


@pytest.fixture
def messages(_message_recorder: MessageRecorder) -> Iterator[MessageRecorder]:
    """Message bar recorder, empty at test start."""
    _message_recorder.clear()
    yield _message_recorder
    _message_recorder.clear()


@pytest.fixture
def canvas(iface: QgisInterface) -> QgsMapCanvas:
    return iface.mapCanvas()


@pytest.fixture
def new_project(iface: QgisInterface) -> Iterator[QgsProject]:
    """Empty ``QgsProject`` and a reset iface, cleaned again after the test."""
    from qgis.core import QgsProject

    QgsProject.instance().clear()
    _reset_iface(iface)
    yield QgsProject.instance()
    QgsProject.instance().clear()
    _reset_iface(iface)


def _reset_iface(iface: QgisInterface) -> None:
    """Undo what a plugin registered. The real interface has nothing like this."""
    reset = getattr(iface, "reset", None)
    if reset is not None:
        reset()


# --------------------------------------------------------- plugin specific


@pytest.fixture
def plugin_factory(
    iface: QgisInterface,
    new_project: QgsProject,  # noqa: ARG001 (dependency only: empty project first)
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[Callable[[], Plugin]]:
    """Builds ``Plugin()`` + ``initGui()``; unloads every built plugin at teardown."""
    monkeypatch.setenv("PGTZ", "Europe/Helsinki")  # tests that want the warning delenv it

    import arho_feature_template
    from arho_feature_template.plugin import Plugin
    from arho_feature_template.qgis_plugin_tools.tools.custom_logging import teardown_logger

    show_exception_before = qgis.utils.showException
    created: list[Plugin] = []
    started: list[Plugin] = []

    def make() -> Plugin:
        plugin = Plugin()
        created.append(plugin)
        plugin.initGui()
        started.append(plugin)
        return plugin

    yield make

    for plugin in started:
        if plugin.toolbar is not None:  # unload() sets toolbar = None
            plugin.unload()
    if len(started) < len(created):
        # initGui() raised, so unload() cannot run. Close the log file it opened, or the
        # temp profile cannot be removed at exit on Windows.
        teardown_logger(arho_feature_template.__name__)
    qgis.utils.showException = show_exception_before
    _reset_iface(iface)


@pytest.fixture
def plugin(plugin_factory: Callable[[], Plugin]) -> Plugin:
    return plugin_factory()
