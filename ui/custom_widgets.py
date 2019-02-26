from qgis.PyQt.QtCore import Qt
from qgis.gui import QgsCheckableComboBox

from QuickOSM.definitions.osm import LayerType, OsmType

"""Different QWidgets which are used in QuickOSM."""


class CheckableOutputsComboBox(QgsCheckableComboBox):
    """Display checkable combobox about outputs."""
    def __init__(self, parent=None):
        QgsCheckableComboBox.__init__(self, parent)

        # noinspection PyTypeChecker
        for i, one_type in enumerate(list(LayerType)):
            self.addItem(one_type.name, one_type.value)
            self.setItemCheckState(i, Qt.Checked)


class CheckableOsmObjectsComboBox(QgsCheckableComboBox):
    """Display checkable combobox about OSM objects."""
    def __init__(self, parent=None):
        QgsCheckableComboBox.__init__(self, parent)

        # noinspection PyTypeChecker
        for i, one_type in enumerate(list(OsmType)):
            self.addItem(one_type.name, one_type.value)
            self.setItemCheckState(i, Qt.Checked)
