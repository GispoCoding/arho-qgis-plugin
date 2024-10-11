from typing import cast

from qgis.gui import QgisInterface
from qgis.utils import iface as qgis_iface

# This is just a workaround to make static typing work
iface = cast(QgisInterface, qgis_iface)
