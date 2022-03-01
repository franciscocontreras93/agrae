import os
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import * 
from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal

from .utils import AgraeToolset

agraeSegmentoDialog, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui/dialogs/parcela_dialog.ui'))

class agraeSegmentoDialog(QtWidgets.QDialog, agraeSegmentoDialog):

    closingPlugin = pyqtSignal()

    def __init__(self,parent=None): 
        #* constructor
        super(agraeSegmentoDialog, self).__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'ui/dialogs/segmento_dialog.ui'), self)

        self.tools = AgraeToolset()
        self.lastCode = self.tools.lastCode()       
        self.btn_guardar.clicked.connect(self.export)
        self.lbl_code.setText(self.lastCode)
        
        
        self.populateTable()

        self.show()

    def closeEvent(self,event): 
        self.closingPlugin.emit()
        event.accept()

    def data(self): 
        self.tools.dataSegmento()

    def populateTable(self):
        
        self.tools.dataSegmento(self.tableWidget)


    def export(self):
        table = self.tableWidget
        self.tools.crearSegmento(self, table) 
        
