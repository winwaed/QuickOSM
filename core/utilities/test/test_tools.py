"""
/***************************************************************************
 QuickOSM
 A QGIS plugin
 OSM Overpass API frontend
                             -------------------
        begin                : 2014-06-11
        copyright            : (C) 2014 by 3Liz
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


from qgis.testing import unittest

from QuickOSM.core.utilities.tools import best_translation_file


# noinspection PyTypeChecker
class TestTools(unittest.TestCase):

    def test_translation_file(self):
        """Test to find the best translation file."""
        self.assertEqual(best_translation_file('fr'), 'fr')
        self.assertEqual(best_translation_file('pt_PT'), 'fr_BR')
        self.assertEqual(best_translation_file('pt_BR'), 'pt_BR')
        self.assertEqual(best_translation_file('es'), 'es')


if __name__ == '__main__':
    suite = unittest.makeSuite(TestTools)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
