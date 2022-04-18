import os
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator, QIcon
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import * 
from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal

from .utils import AgraeUtils,AgraeToolset

agraeSegmentoDialog, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui/dialogs/parcela_dialog.ui'))

agraeParametrosDialog, _ =  uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui/dialogs/params_dialog.ui'))

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
        

class agraeParametrosDialog(QtWidgets.QDialog, agraeParametrosDialog): 
    closingPlugin = pyqtSignal()
    
    def __init__(self, parent=None):
        super(agraeParametrosDialog, self).__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__),'ui/dialogs/params_dialog.ui'),self)

        self.tools = AgraeToolset()
        self.utils = AgraeUtils()
        self.conn = self.utils.Conn()

        self.editTexturaStatus = False
        self.editPhStatus = False
        self.editCEStatus = False

        self.loadTextura()

        self.UIComponents()

    def closeEvent(self, event): 
        self.closingPlugin.emit()
        event.accept()

    def UIComponents(self):
        icons_path = self.utils.iconsPath()
        
        self.tabWidget_1.setCurrentIndex(0)
        self.tabWidget_1.currentChanged.connect(self.loadData)

        self.tableWidget_1.setColumnHidden(0, True)
        self.tableWidget_2.setColumnHidden(0, True)
        self.tableWidget_3.setColumnHidden(0, True)
        self.loadTextura()

        self.an_edit_textura_btn.setIcon(QIcon(icons_path['pen-to-square']))
        self.an_edit_textura_btn.setIconSize(QtCore.QSize(20, 20))
        self.an_edit_textura_btn.setToolTip('Editar Valores')
        self.an_edit_textura_btn.clicked.connect(self.editTextura)
        self.an_save_textura_btn.setIcon(QIcon(icons_path['save']))
        self.an_save_textura_btn.setIconSize(QtCore.QSize(20, 20))
        self.an_save_textura_btn.setToolTip('Guardar Valores')
        self.an_save_textura_btn.clicked.connect(self.saveTextura)

        self.an_edit_ph.setIcon(QIcon(icons_path['pen-to-square']))
        self.an_edit_ph.setIconSize(QtCore.QSize(20, 20))
        self.an_edit_ph.setToolTip('Editar Valores')
        self.an_edit_ph.clicked.connect(self.editPh)
        self.an_save_ph.setIcon(QIcon(icons_path['save']))
        self.an_save_ph.setIconSize(QtCore.QSize(20, 20))
        self.an_save_ph.setToolTip('Guardar Valores')
        self.an_save_ph.clicked.connect(self.savePh)

        self.an_edit_ce.setIcon(QIcon(icons_path['pen-to-square']))
        self.an_edit_ce.setIconSize(QtCore.QSize(20, 20))
        self.an_edit_ce.setToolTip('Editar Valores')
        self.an_edit_ce.clicked.connect(self.editCE)
        self.an_save_ce.setIcon(QIcon(icons_path['save']))
        self.an_save_ce.setIconSize(QtCore.QSize(20, 20))
        self.an_save_ce.setToolTip('Guardar Valores')
        self.an_save_ce.clicked.connect(self.saveCE)

        self.tableWidget_3.setColumnWidth(1, 178)
        self.tableWidget_3.setColumnWidth(2, 71)
        self.tableWidget_3.setColumnWidth(3, 71)
        self.tableWidget_3.setColumnWidth(4, 391)



        
        
        pass
    
    
    def loadTextura(self): 
        sql = 'select * from analisis.textura order by idtextura '
        with self.conn: 
            cursor = self.conn.cursor() 
            cursor.execute(sql)
            data = cursor.fetchall() 
            a = len(data)
            b = len(data[0])
            i = 1
            j = 1                      
            self.tableWidget_1.setRowCount(a)
            self.tableWidget_1.setColumnCount(b)
            for j in range(a):
                for i in range(b):
                    item = QTableWidgetItem(str(data[j][i]))
                    self.tableWidget_1.setItem(j, i, item)

    def editTextura(self):
        if self.editTexturaStatus == False:
            self.tableWidget_1.setEditTriggers(QAbstractItemView.AllEditTriggers)
            self.editTexturaStatus = True
            self.an_save_textura_btn.setEnabled(True)
        else: 
            self.tableWidget_1.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.editTexturaStatus = False
            self.an_save_textura_btn.setEnabled(False)
    
    def saveTextura(self):
        confirm = QMessageBox.question(
            self, 'aGrae GIS', f"Seguro quiere Actualizar Los valores de textura?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try: 
                for r in range(self.tableWidget_1.rowCount()): 
                    id =  self.tableWidget_1.item(r,0).text()
                    categoria =  self.tableWidget_1.item(r,1).text()
                    grupo =  self.tableWidget_1.item(r,2).text()
                    arena_i =  self.tableWidget_1.item(r,3).text()
                    arena_s =  self.tableWidget_1.item(r,4).text()
                    limo_i =  self.tableWidget_1.item(r,5).text()
                    limo_s =  self.tableWidget_1.item(r,6).text()
                    arcilla_i =  self.tableWidget_1.item(r,7).text()
                    arcilla_s =  self.tableWidget_1.item(r,8).text()
                    ceap_i =  self.tableWidget_1.item(r,9).text()
                    ceap_s =  self.tableWidget_1.item(r,10).text()
                    cra =  self.tableWidget_1.item(r,11).text()
                    hsg =  self.tableWidget_1.item(r,12).text()
                    grupo_label =  self.tableWidget_1.item(r,13).text()
                    sql = f"""update analisis.textura set 
                            categoria = '{categoria}',
                            grupo = {grupo},
                            arena_i = {arena_i},
                            arena_s = {arena_s},
                            limo_i = {limo_i},
                            limo_s = {limo_s},
                            arcilla_i = {arcilla_i},
                            arcilla_s = {arcilla_s},
                            ceap_i = {ceap_i}, 
                            ceap_s = {ceap_s},
                            cra_cod = {cra},
                            hsg = '{hsg}',
                            grupo_label = '{grupo_label}'
                            where idtextura = {id}
                            """
                    with self.conn:
                        try:
                            cursor = self.conn.cursor() 
                            cursor.execute(sql)
                            self.conn.commit()
                            print('textura: {} actualizada correctamente'.format(id))
                        except Exception as ex:
                            print(ex) 
                self.editTextura()
                self.utils.msgBar('Parametros de Textura Actualizados Correctamente', 3, 5)
            
            except Exception as ex: 
                print(ex)
                QMessageBox.about(self, 'aGrae GIS','Ocurrio un Error')
            
            
    def loadData(self,i):
        if i == 1:
            sql = 'select * from analisis.ph order by id '
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute(sql)
                data = cursor.fetchall()
                a = len(data)
                b = len(data[0])
                i = 1
                j = 1
                self.tableWidget_2.setRowCount(a)
                self.tableWidget_2.setColumnCount(b)
                for j in range(a):
                    for i in range(b):
                        item = QTableWidgetItem(str(data[j][i]))
                        self.tableWidget_2.setItem(j, i, item)
        elif i == 2:
            sql = 'select * from analisis.conductividad_electrica order by idce '
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute(sql)
                data = cursor.fetchall()
                a = len(data)
                b = len(data[0])
                i = 1
                j = 1
                self.tableWidget_3.setRowCount(a)
                self.tableWidget_3.setColumnCount(b)
                for j in range(a):
                    for i in range(b):
                        item = QTableWidgetItem(str(data[j][i]))
                        self.tableWidget_3.setItem(j, i, item)


    def editPh(self):
        if self.editPhStatus == False:
            self.tableWidget_2.setEditTriggers(
                QAbstractItemView.AllEditTriggers)
            self.editPhStatus = True
            self.an_save_ph.setEnabled(True)
        else:
            self.tableWidget_2.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.editPhStatus = False
            self.an_save_ph.setEnabled(False)


    def savePh(self):
        confirm = QMessageBox.question(
            self, 'aGrae GIS', f"Seguro quiere Actualizar Los valores de pH?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                for r in range(self.tableWidget_2.rowCount()):
                    id = self.tableWidget_2.item(r, 0).text()
                    tipo = self.tableWidget_2.item(r, 1).text()
                    li = self.tableWidget_2.item(r, 2).text()
                    ls = self.tableWidget_2.item(r, 3).text()
                    
                    sql = f"""update analisis.ph set 
                            tipo = '{tipo}',
                            limite_inferior = {li},
                            limite_superior = {ls}
                            where id = {id}
                            """
                    with self.conn:
                        try:
                            cursor = self.conn.cursor()
                            cursor.execute(sql)
                            self.conn.commit()
                            print('ph: {} actualizado correctamente'.format(id))
                        except Exception as ex:
                            print(ex)
                self.editPh()

                self.utils.msgBar(
                    'Parametros de pH Actualizados Correctamente', 3, 5)

            except Exception as ex:
                print(ex)
                QMessageBox.about(self, 'aGrae GIS', 'Ocurrio un Error')

    def loadCE(self, i):
        if i == 1:
            sql = 'select * from analisis.conductividad_electrica order by idce '
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute(sql)
                data = cursor.fetchall()
                a = len(data)
                b = len(data[0])
                i = 1
                j = 1
                self.tableWidget_3.setRowCount(a)
                self.tableWidget_3.setColumnCount(b)
                for j in range(a):
                    for i in range(b):
                        item = QTableWidgetItem(str(data[j][i]))
                        self.tableWidget_3.setItem(j, i, item)

    def editCE(self):
        if self.editCEStatus == False:
            self.tableWidget_3.setEditTriggers(
                QAbstractItemView.AllEditTriggers)
            self.editCEStatus = True
            self.an_save_ce.setEnabled(True)
        else:
            self.tableWidget_3.setEditTriggers(
                QAbstractItemView.NoEditTriggers)
            self.editCEStatus = False
            self.an_save_ce.setEnabled(False)

    def saveCE(self):
        confirm = QMessageBox.question(
            self, 'aGrae GIS', f"Seguro quiere Actualizar Los valores de CE?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                for r in range(self.tableWidget_3.rowCount()):
                    id = self.tableWidget_3.item(r, 0).text()
                    tipo = self.tableWidget_3.item(r, 1).text()
                    li = self.tableWidget_3.item(r, 2).text()
                    ls = self.tableWidget_3.item(r, 3).text()
                    influencia = self.tableWidget_3.item(r, 4).text()

                    sql = f"""update analisis.conductividad_electrica set 
                            tipo = '{tipo}',
                            limite_i = {li},
                            limite_s = {ls},
                            influencia = '{influencia}'
                            where idce = {id}
                            """
                    with self.conn:
                        try:
                            cursor = self.conn.cursor()
                            cursor.execute(sql)
                            self.conn.commit()
                            print('CE: {} actualizado correctamente'.format(id))
                        except Exception as ex:
                            print(ex)
                self.editPh()

                self.utils.msgBar(
                    'Parametros de Conductividad Electrica Actualizados Correctamente', 3, 5)

            except Exception as ex:
                print(ex)
                QMessageBox.about(self, 'aGrae GIS', 'Ocurrio un Error')
