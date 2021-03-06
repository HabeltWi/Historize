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
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.utils import *
from qgis.core import *
from qgis.gui import *
from ui_selectDate import Ui_SelectDate
from sqlexecute import SQLExecute
from dbconn import DBConn


class SelectDateDialog(QDialog, Ui_SelectDate):
    """
    Class responsible for handling the date selection.
    """
    def __init__(self, iface, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.iface = iface
        self.dbconn = DBConn(iface)
        self.cmbDate.clear()
        self.getDates()

    def getDates(self):
        """Get all historized dates from layer"""
        provider = self.iface.activeLayer().dataProvider()
        self.uri = QgsDataSourceURI(provider.dataSourceUri())
        self.conn = self.dbconn.connectToDb(self.uri)
        # self.schema = self.uri.schema()
        self.execute = SQLExecute(self.conn, self.iface.activeLayer())
        self.dateList = self.execute.retrieveHistVersions(self.iface.activeLayer().name(), self.uri.schema())

        if not self.dateList:
            self.records = False
            QMessageBox.warning(self.iface.mainWindow(), self.tr(u"Error"), self.tr(u"No historized versions found!"))
        else:
            for date in self.dateList:
                self.cmbDate.addItem(str(date[0]))
                self.records = True

    @pyqtSignature("")
    def on_buttonBox_accepted(self):
        """
        Run hist_tabs.version() SQL-function
        """
        if self.records:
            self.execute.histTabsVersion(self.uri.schema(), self.iface.activeLayer().name(), self.cmbDate.currentText(), self.uri)

    @pyqtSignature("")
    def on_buttonBox_rejected(self):
        """
        Close Window and DB-Connection
        """
        self.conn.close()
        self.close()
