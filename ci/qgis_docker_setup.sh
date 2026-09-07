#!/bin/bash
# Prepare a qgis/qgis container to run this plugin's tests inside the real QGIS application:
# install the test dependencies, prepare the QGIS profile and enable the plugin.
#
# Replaces the image's /usr/bin/qgis_setup.sh, which hard-codes the QGIS3 profile paths and
# therefore does nothing useful on QGIS 4 (profile dir QGIS4, settings file QGIS4.ini).
#
# Usage (inside the container, repository mounted at /tests_directory):
#   bash /tests_directory/ci/qgis_docker_setup.sh arho_feature_template
set -euo pipefail

PLUGIN_NAME=${1:?plugin package name required}
REPO_DIR=$(cd "$(dirname "$0")/.." && pwd)

# --- test dependencies ------------------------------------------------------------------
# QGIS runs the tests in its own embedded Python, which is the system Python. The image
# ships an older pytest installed by the distro, which pip cannot replace (no RECORD file),
# so install the pinned one into its own directory instead and leave the system untouched.
# ci/qgis_pytest_runner.py puts that directory first on sys.path.
#
# requirements-test.txt is used as a constraints file: it carries environment markers and
# more than one pytest pin, and pip picks the one that fits this interpreter.
TEST_DEPS_DIR=${ARHO_TEST_DEPS:-/opt/arho-test-deps}
echo "Installing pinned pytest into ${TEST_DEPS_DIR}"
python3 -m pip install --quiet --root-user-action=ignore \
    --target "${TEST_DEPS_DIR}" -c "${REPO_DIR}/requirements-test.txt" pytest
PYTHONPATH="${TEST_DEPS_DIR}" python3 -c "import pytest; print('pytest', pytest.__version__)"

# --- QGIS profile -----------------------------------------------------------------------
MAJOR=$(python3 -c "from qgis.core import Qgis; print(Qgis.versionInt() // 10000)")
APP="QGIS${MAJOR}"
BASE="/root/.local/share/QGIS/${APP}"
PROFILE="${BASE}/profiles/default"

mkdir -p "${PROFILE}/QGIS" "${PROFILE}/python/plugins"

# Print Python errors to stdout instead of opening a modal dialog.
if [ -f /usr/bin/qgis_startup.py ]; then
    cp /usr/bin/qgis_startup.py "${BASE}/startup.py"
fi

cat > "${PROFILE}/QGIS/${APP}.ini" <<INI
[PythonPlugins]
${PLUGIN_NAME}=true

[migration]
fileVersion=2
firstRunVersionFlag=30500
settings=true
INI

PLUGIN_DIR="${REPO_DIR}/${PLUGIN_NAME}"
if [ ! -d "${PLUGIN_DIR}" ]; then
    echo "ERROR: ${PLUGIN_DIR} does not exist" >&2
    exit 1
fi
ln -sfn "${PLUGIN_DIR}" "${PROFILE}/python/plugins/${PLUGIN_NAME}"
echo "Profile ${PROFILE} prepared for ${PLUGIN_NAME} (${APP})"
