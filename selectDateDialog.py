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
    Class documentation goes here.
    """
    def __init__(self, iface, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.iface = iface
        self.dbconn = DBConn(iface)
        self.cmbDate.clear()
        self.getDates()

    def getDates(self):
        self.selectedLayer = self.iface.activeLayer()

        if not self.selectedLayer:
            QMessageBox.warning(self.iface.mainWindow(), "Select Layer", "Please select a layer!")
            return

        provider = self.selectedLayer.dataProvider()

        if provider.name() != 'postgres':
            QMessageBox.warning(self.iface.mainWindow(), "Invalid Layer", "Layer must be provided by postgres!")
            return

        uri = QgsDataSourceURI(provider.dataSourceUri())
        conn = self.dbconn.connectToDb(uri)
        self.schema = uri.schema()
        self.execute = SQLExecute(conn, self.selectedLayer)
        self.dateList = self.execute.retrieveHistVersions(self.selectedLayer.name(), self.schema)
        if not self.dateList:
            self.records = False
            QMessageBox.warning(self.iface.mainWindow(), "Error", "No historized versions found!")
        else:
            for date in self.dateList:
                self.cmbDate.addItem(str(date[0]))
                self.records = True

    @pyqtSignature("")
    def on_buttonBox_accepted(self):
        """
        Slot documentation goes here.
        """
        if self.records:
            self.execute.histTabsVersion(self.schema, self.selectedLayer.name(), self.cmbDate.currentText())

    @pyqtSignature("")
    def on_buttonBox_rejected(self):
        """
        Slot documentation goes here.
        """
        print "Close"
        self.close()
