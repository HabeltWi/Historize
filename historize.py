"""
 /***************************************************************************
   QGIS Historize Plugin
  -------------------------------------------------------------------
 Date                 : 09 Mai 2017
 Copyright            : (C) 2017 by William Habelt
 email                : wha@sourcepole.ch

  ***************************************************************************
  *                                                                         *
  *   This program is free software; you can redistribute it and/or modify  *
  *   it under the terms of the GNU General Public License as published by  *
  *   the Free Software Foundation; either version 2 of the License, or     *
  *   (at your option) any later version.                                   *
  *                                                                         *
  ***************************************************************************/
"""
from qgis.core import QgsFeature,  QgsMapLayerRegistry
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from importUpdateDialog import ImportUpdateDialog
from selectDateDialog import SelectDateDialog
from aboutDialog import AboutDialog
from dbconn import DBConn
from sqlexecute import SQLExecute

class Historize:
    """Class documentation goes here"""

    def __init__(self, iface):
        self.iface = iface
        self.dbconn = DBConn(iface)

    def initGui(self):
        self.menu = QMenu()
        self.menu.setTitle("Historize")

        self.lyrMenu = QMenu()
        self.lyrMenu.setTitle("Layer")

        # Create menu actions
        self.actionInit = QAction( u"Initialize Database", self.iface.mainWindow())
        self.actionLyrInit = QAction(u"Initialize Layer", self.iface.mainWindow())
        self.actionLyrUpdate = QAction(u"Update Layer", self.iface.mainWindow())
        self.actionLyrLoad = QAction(u"Load Layer", self.iface.mainWindow())
        self.actionAbout = QAction( u"About", self.iface.mainWindow())

        # Connect menu actions
        self.actionInit.triggered.connect(self.doInit)
        self.actionLyrInit.triggered.connect(self.doLyrInit)
        self.actionLyrUpdate.triggered.connect(self.doLyrUpdate)
        self.actionLyrLoad.triggered.connect(self.doLyrLoad)
        self.actionAbout.triggered.connect(self.doAbout)

        # Add actions to menu
        self.lyrMenu.addActions([self.actionLyrInit,  self.actionLyrUpdate, self.actionLyrLoad])
        self.menu.addAction(self.actionInit)
        self.menu.addMenu(self.lyrMenu)
        self.menu.addAction(self.actionAbout)
        self.menu.insertSeparator(self.actionAbout)
        menuBar = self.iface.mainWindow().menuBar()
        menuBar.addMenu(self.menu)

    def unload(self):
        self.menu.deleteLater()

    def doInit(self):
        """Use Database info from layer and run historisation.sql on it."""
        pass

    def doLyrInit(self):
        """Use Layer info and run init() .sql query"""
        selectedLayer = self.iface.activeLayer()

        if not selectedLayer:
            QMessageBox.warning(self.iface.mainWindow(), "Select Layer", "Please select a layer!")
            return

        provider = selectedLayer.dataProvider()

        if provider.name() != 'postgres':
            QMessageBox.warning(self.iface.mainWindow(), "Invalid Layer", "Layer must be provided by postgres!")
            return

        uri = QgsDataSourceURI(provider.dataSourceUri())
        cur = self.dbconn.connectToDb(uri)

        if cur is False:
            return


        result = QMessageBox.warning(self.iface.mainWindow(), "Initialize Layer", "Are you sure you wish to proceed?", QMessageBox.No | QMessageBox.Yes)
        if result == QMessageBox.Yes:
            # Get SQL vars
            hasGeometry = selectedLayer.hasGeometryType()
            schema = uri.schema()
            table = uri.table()

            self.execute = SQLExecute(cur, selectedLayer)
            self.execute.histTabsInit(hasGeometry, schema, table)
        else:
            return

    def doLyrUpdate(self):
        """Open ImportUpdate dialog"""
        self.updateDialog = ImportUpdateDialog(self.iface)
        self.updateDialog.show()

    def doLyrLoad(self):
        """Open selectDate dialog"""
        self.dateDialog = SelectDateDialog(self.iface)
        self.dateDialog.show()

    def doAbout(self):
        """Show About dialog"""
        self.aboutDialog = AboutDialog()
        self.aboutDialog.show()
