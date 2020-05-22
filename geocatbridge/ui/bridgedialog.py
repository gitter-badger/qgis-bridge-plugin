import os

from qgis.PyQt import uic
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QFrame, QListWidget
from qgis.PyQt.QtCore import QSize, QSettings

from .publishwidget import PublishWidget
from .serverconnectionswidget import ServerConnectionsWidget
from .geocatwidget import GeoCatWidget

FIRSTTIME_SETTING = "geocatbridge/FirstTimeRun"

def iconPath(icon):
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons", icon)

WIDGET, BASE = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'bridgedialog.ui'))

class BridgeDialog(BASE, WIDGET):

    def __init__(self, parent=None):
        super(BridgeDialog, self).__init__(parent)
        self.setupUi(self)
        self.publishWidget = PublishWidget(self)
        self.serversWidget = ServerConnectionsWidget()
        self.geocatWidget = GeoCatWidget()
        self.stackedWidget.addWidget(self.publishWidget)
        self.stackedWidget.addWidget(self.serversWidget)
        self.stackedWidget.addWidget(self.geocatWidget)
        self.listWidget.setMinimumSize(QSize(100, 200))
        self.listWidget.setMaximumSize(QSize(153, 16777215))
        self.listWidget.setStyleSheet("QListWidget{\n"
            "    background-color: rgb(69, 69, 69, 220);\n"
            "    outline: 0;\n"
            "}\n"
            "QListWidget::item {\n"
            "    color: white;\n"
            "    padding: 3px;\n"
            "}\n"
            "QListWidget::item::selected {\n"
            "    color: black;\n"
            "    background-color:palette(Window);\n"
            "    padding-right: 0px;\n"
            "}")
        self.listWidget.setFrameShape(QFrame.Box)
        self.listWidget.setLineWidth(0)
        self.listWidget.setIconSize(QSize(32, 32))
        self.listWidget.setUniformItemSizes(True)
        self.item = []
        for i in range(3):
            item = self.listWidget.item(i)
            item.setIcon(QIcon(iconPath('preview.png')))
        self.listWidget.currentRowChanged.connect(self.sectionChanged)
        if self.isFirstTime():
            self.currentIdx = 2
            self.listWidget.setCurrentRow(2) 
        else:
            self.currentIdx = 0
            self.listWidget.setCurrentRow(0)

    def isFirstTime(self):        
        if QSettings().contains(FIRSTTIME_SETTING):
            return False
        else:
            QSettings().setValue(FIRSTTIME_SETTING, False)
            return True

    def sectionChanged(self):
        if self.currentIdx  == 1:
            if not self.serversWidget.canClose():
                self.listWidget.blockSignals(True)
                self.listWidget.item(1).setSelected(True)
                self.listWidget.setCurrentRow(1)
                self.listWidget.blockSignals(False)
                return
        idx = self.listWidget.currentRow()                
        self.setCurrentPanel(idx)

    def setCurrentPanel(self, idx):
        self.currentIdx = idx
        if idx == 0:
            self.stackedWidget.setCurrentWidget(self.publishWidget)
            self.publishWidget.updateServers()
        elif idx == 1:
            self.stackedWidget.setCurrentWidget(self.serversWidget)
            self.serversWidget.populateServers()
        elif idx == 2:
            self.stackedWidget.setCurrentWidget(self.geocatWidget)

    def closeEvent(self, evt):
        self.publishWidget.storeMetadata()
        if self.serversWidget.canClose():
            evt.accept()
        else:
            evt.ignore()