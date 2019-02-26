# -*- coding: utf-8 -*-
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
from json import load
from os.path import dirname, abspath, join, isfile, isdir

from QuickOSM.core.process import process_quick_query
from QuickOSM.core.exceptions import (
    QuickOsmException,
    OutPutGeomTypesException,
    DirectoryOutPutException,
    OsmObjectsException)
from QuickOSM.core.query_factory import QueryFactory
from QuickOSM.core.utilities.tools import tr
from QuickOSM.core.utilities.utilities_qgis import display_message_bar
from QuickOSM.definitions.osm import QueryType, OsmType, LayerType
from QuickOSM.ui.QuickOSMWidget import QuickOSMWidget
from QuickOSM.ui.quick_query import Ui_ui_quick_query
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QApplication, QCompleter, \
    QDialogButtonBox
from qgis.core import Qgis
from qgis.utils import iface


class QuickQueryWidget(QuickOSMWidget, Ui_ui_quick_query):
    # noinspection PyUnresolvedReferences
    def __init__(self, parent=None):
        """
        QuickQueryWidget constructor
        """
        QuickOSMWidget.__init__(self, parent)
        self.setupUi(self)
        self.init()

        # Setup UI

        # Query type
        self.cb_query_type.addItem(tr('In'), 'in')
        self.cb_query_type.addItem(tr('Around'), 'around')
        self.cb_query_type.addItem(tr('Canvas Extent'), 'canvas')
        self.cb_query_type.addItem(tr('Layer Extent'), 'layer')
        self.cb_query_type.addItem(tr('Not Spatial'), 'attributes')

        # self.cb_query_type.setItemIcon(0, QIcon(resources_path('in.svg')))
        # self.cb_query_type.setItemIcon(1, QIcon(resources_path('around.svg')))
        # self.cb_query_type.setItemIcon(2, QIcon(resources_path('map_canvas.svg')))
        # self.cb_query_type.setItemIcon(3, QIcon(resources_path('extent.svg')))
        # self.cb_query_type.setItemIcon(4, QIcon(resources_path('mIconTableLayer.svg')))

        self.cb_query_type.currentIndexChanged.connect(self.query_type_updated)

        self.label_progress.setText("")
        self.lineEdit_filePrefix.setDisabled(True)
        # self.activate_extent_layer()

        # connect
        self.pushButton_runQuery.clicked.connect(self.run_query)
        self.pushButton_showQuery.clicked.connect(self.show_query)
        self.comboBox_key.editTextChanged.connect(self.key_edited)
        self.pushButton_mapFeatures.clicked.connect(self.open_map_features)
        self.buttonBox.button(QDialogButtonBox.Reset).clicked.connect(
            self.reset_form)

        # Setup auto completion
        map_features_json_file = join(
            dirname(dirname(abspath(__file__))), 'mapFeatures.json')

        if isfile(map_features_json_file):
            with open(map_features_json_file) as f:
                self.osmKeys = load(f)
                keys = list(self.osmKeys.keys())
                keys.append('')  # All keys request #118
                keys.sort()
                keys_completer = QCompleter(keys)
                self.comboBox_key.addItems(keys)
                self.comboBox_key.setCompleter(keys_completer)
                self.comboBox_key.completer().setCompletionMode(
                    QCompleter.PopupCompletion)
                self.comboBox_key.lineEdit().setPlaceholderText(tr('Query on all keys'))

        self.comboBox_value.lineEdit().setPlaceholderText(tr('Query on all values'))
        self.key_edited()

        self.query_type_updated()
        self.init_nominatim_autofill()

    def reset_form(self):
        self.comboBox_key.setCurrentIndex(0)
        self.comboBox_value.setCurrentIndex(0)
        self.lineEdit_nominatim.setText("")
        # self.radioButton_place.setChecked(True)
        self.spinBox_distance_point.setValue(1000)
        # self.comboBox_in_around.setCurrentIndex(0)
        self.comboBox_outputs.selectAllOptions()
        self.comboBox_osm_objects.selectAllOptions()
        self.spinBox_timeout.setValue(25)
        self.output_directory.lineEdit().setText('')
        self.lineEdit_filePrefix.setText("")

    def key_edited(self):
        """
        Disable show and run buttons if the key is empty
        and add values to the combobox
        """
        self.comboBox_value.clear()
        self.comboBox_value.setCompleter(None)

        try:
            current_values = (
                self.osmKeys[self.comboBox_key.currentText()])
        except KeyError:
            return
        except AttributeError:
            return

        if len(current_values) == 0:
            current_values.insert(0, '')

        if len(current_values) > 1 and current_values[0] != "":
            current_values.insert(0, '')

        values_completer = QCompleter(current_values)
        self.comboBox_value.setCompleter(values_completer)
        self.comboBox_value.addItems(current_values)

    def run_query(self):
        """
        Process for running the query
        """

        # Block the button and save the initial text
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.output_directory.setDisabled(True)
        self.pushButton_showQuery.setDisabled(True)
        self.start_process()
        QApplication.processEvents()

        # Get all values
        key = self.comboBox_key.currentText()
        value = self.comboBox_value.currentText()
        nominatim = self.nominatim_value()
        timeout = self.spinBox_timeout.value()
        output_directory = self.output_directory.filePath()
        prefix_file = self.lineEdit_filePrefix.text()

        query_type = self.cb_query_type.currentData()
        is_around = query_type == 'around'
        distance = self.spinBox_distance_point.value()

        # Which geometry at the end ?
        output_geometry_types = self.comboBox_outputs.checkedItems()
        output_geometry_types = [LayerType(i) for i in output_geometry_types]

        # Which osm objects ?
        osm_objects = self.comboBox_osm_objects.checkedItems()
        osm_objects = [OsmType(i) for i in osm_objects]

        try:
            # Test values
            if not osm_objects:
                raise OsmObjectsException

            if not output_geometry_types:
                raise OutPutGeomTypesException

            # If bbox, we must set None to nominatim, we can't have both
            bbox = None
            if query_type in ['layer', 'canvas']:
                nominatim = None
                bbox = self.get_bounding_box()

            if nominatim == '':
                nominatim = None

            if output_directory and not isdir(output_directory):
                raise DirectoryOutPutException

            num_layers = process_quick_query(
                dialog=self,
                key=key,
                value=value,
                nominatim=nominatim,
                is_around=is_around,
                distance=distance,
                bbox=bbox,
                osm_objects=osm_objects,
                timeout=timeout,
                output_directory=output_directory,
                prefix_file=prefix_file,
                output_geometry_types=output_geometry_types)

            # We can test numLayers to see if there are some results
            if num_layers:
                self.label_progress.setText(
                    tr('Successful query'))

                display_message_bar(
                    tr('Successful query'),
                    level=Qgis.Success,
                    duration=5)
            else:
                self.label_progress.setText(tr('No result'))

                display_message_bar(
                    tr('Successful query, but no result.'),
                    level=Qgis.Warning,
                    duration=7)

        except QuickOsmException as e:
            self.display_geo_algorithm_exception(e)
        except Exception as e:  # pylint: disable=broad-except
            self.display_exception(e)

        finally:
            # Resetting the button
            self.output_directory.setDisabled(False)
            self.pushButton_showQuery.setDisabled(False)
            QApplication.restoreOverrideCursor()
            self.end_process()
            QApplication.processEvents()

    def show_query(self):
        """
        Show the query in the main window
        """

        # We have to find the widget in the stacked widget of the main window
        query_widget = None
        index_quick_query_widget = None
        for i in range(iface.QuickOSM_mainWindowDialog.stackedWidget.count()):
            widget = iface.QuickOSM_mainWindowDialog.stackedWidget.widget(i)
            if widget.__class__.__name__ == "QueryWidget":
                query_widget = iface.QuickOSM_mainWindowDialog.stackedWidget.\
                    widget(i)
                index_quick_query_widget = i
                break

        # Get all values
        key = self.comboBox_key.currentText()
        value = self.comboBox_value.currentText()
        nominatim = self.lineEdit_nominatim.text()
        timeout = self.spinBox_timeout.value()
        output_directory = self.output_directory.filePath()
        prefix_file = self.lineEdit_filePrefix.text()
        query_type = self.cb_query_type.currentData()
        is_around = query_type == 'around'
        distance = self.spinBox_distance_point.value()

        # If bbox, we must set None to nominatim, we can't have both
        bbox = None
        if query_type in ['layer', 'canvas']:
            nominatim = None
            bbox = True
        elif query_type in ['attributes']:
            nominatim = None

        if nominatim == '':
            nominatim = None

        # Which osm objects ?
        osm_objects = self.comboBox_osm_objects.checkedItems()
        osm_objects = [OsmType(item) for item in osm_objects]

        # Which geometry at the end ?
        query_widget.comboBox_outputs.deselectAllOptions()
        outputs = self.comboBox_outputs.checkedItems()
        for output in outputs:
            index = query_widget.comboBox_outputs.findData(output)
            query_widget.comboBox_outputs.setItemCheckState(index, Qt.Checked)

        # What kind of extent query
        # query_widget.radioButton_extentLayer.setChecked(
        #     self.radioButton_extentLayer.isChecked())
        # query_widget.radioButton_extentMapCanvas.setChecked(
        #     self.radioButton_extentMapCanvas.isChecked())

        # Transfer the combobox from QuickQuery to Query
        # if self.comboBox_extentLayer.count():
        #     query_widget.radioButton_extentLayer.setCheckable(True)

        # Transfer the output
        query_widget.output_directory.setFilePath(output_directory)
        if prefix_file:
            query_widget.lineEdit_filePrefix.setText(prefix_file)
            query_widget.lineEdit_filePrefix.setEnabled(True)

        # TODO
        # Move this logic UP
        # Copy/paste in quick_query_dialog.py
        if is_around and nominatim:
            query_type = QueryType.AroundArea
        elif not is_around and nominatim:
            query_type = QueryType.InArea
        elif bbox:
            query_type = QueryType.BBox
        else:
            query_type = QueryType.NotSpatial
        # End todo

        # Make the query
        query_factory = QueryFactory(
            query_type=query_type,
            key=key,
            value=value,
            area=nominatim,
            around_distance=distance,
            osm_objects=osm_objects,
            timeout=timeout
        )
        query = query_factory.make()
        query_widget.textEdit_query.setPlainText(query)
        iface.QuickOSM_mainWindowDialog.listWidget.setCurrentRow(
            index_quick_query_widget)
        iface.QuickOSM_mainWindowDialog.exec_()
