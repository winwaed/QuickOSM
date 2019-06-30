
from os.path import exists
from qgis.testing import unittest

from QuickOSM.core.parse_presets import PresetsParser, PRESET_PATH


class TestPresetParser(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_preset_exist(self):
        """Test the path exists."""
        self.assertTrue(exists(PRESET_PATH))

    def test_preset_parsing(self):
        """Test parsing of the preset file."""
        preset = PresetsParser()
        preset.keys()
