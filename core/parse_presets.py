"""
/***************************************************************************
 QuickOSM
 A QGIS plugin
 OSM Overpass API frontend
                             -------------------
        begin                : 2019-06-23
        copyright            : (C) 2019 by 3Liz
        email                : info at 3liz dot com
        contributor          : Etienne Trimaille
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.PyQt.QtCore import QFile
from qgis.PyQt.QtXml import QDomDocument

from QuickOSM.core.utilities.tools import resources_path

PRESET_PATH = resources_path('presets', 'default_presets.xml')


class PresetsParser:

    def __init__(self):
        self.file = QFile(PRESET_PATH)
        self.doc = QDomDocument()
        self.doc.setContent(self.file)

    def keys(self):
        print(self.doc.toString())
