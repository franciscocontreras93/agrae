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
        
        self.editStatus = False

        self.initialRowCount = 0
        self.removeIds = []
        # self.loadTextura()
        self.loadData(i=None)
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
        self.tableWidget_4.setColumnHidden(0, True)
        self.tableWidget_5.setColumnHidden(0, True)
        # self.loadTextura()

        self.an_edit_textura_btn.setIcon(QIcon(icons_path['pen-to-square']))
        self.an_edit_textura_btn.setIconSize(QtCore.QSize(20, 20))
        self.an_edit_textura_btn.setToolTip('Editar Valores')
        self.an_edit_textura_btn.clicked.connect( lambda: self.editionMode(self.tableWidget_1, self.an_save_textura_btn))
        self.an_save_textura_btn.setIcon(QIcon(icons_path['save']))
        self.an_save_textura_btn.setIconSize(QtCore.QSize(20, 20))
        self.an_save_textura_btn.setToolTip('Guardar Valores')
        self.an_save_textura_btn.clicked.connect(lambda: self.saveData(0))

        self.an_edit_ph.setIcon(QIcon(icons_path['pen-to-square']))
        self.an_edit_ph.setIconSize(QtCore.QSize(20, 20))
        self.an_edit_ph.setToolTip('Editar Valores')
        self.an_edit_ph.clicked.connect(lambda: self.editionMode(self.tableWidget_2, self.an_save_ph))
        self.an_save_ph.setIcon(QIcon(icons_path['save']))
        self.an_save_ph.setIconSize(QtCore.QSize(20, 20))
        self.an_save_ph.setToolTip('Guardar Valores')
        self.an_save_ph.clicked.connect(self.savePh)

        self.an_edit_ce.setIcon(QIcon(icons_path['pen-to-square']))
        self.an_edit_ce.setIconSize(QtCore.QSize(20, 20))
        self.an_edit_ce.setToolTip('Editar Valores')
        self.an_edit_ce.clicked.connect(lambda: self.editionMode(self.tableWidget_3, self.an_save_ce))
        # self.an_edit_ce.clicked.connect(self.editCE)
        self.an_save_ce.setIcon(QIcon(icons_path['save']))
        self.an_save_ce.setIconSize(QtCore.QSize(20, 20))
        self.an_save_ce.setToolTip('Guardar Valores')
        self.an_save_ce.clicked.connect(self.saveCE)

        self.tableWidget_2.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.tableWidget_3.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.tableWidget_3.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.tableWidget_3.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        self.tableWidget_3.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)

        self.tableWidget_4.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tableWidget_5.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        # self.tableWidget_4.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)

        self.an_edit_carbon.setIcon(QIcon(icons_path['pen-to-square']))
        self.an_edit_carbon.setIconSize(QtCore.QSize(20, 20))
        self.an_edit_carbon.setToolTip('Editar Valores')
        self.an_edit_carbon.clicked.connect(lambda: self.editionMode(self.tableWidget_4, self.an_save_carbon,self.an_add_carbon,self.an_remove_carbon))
        
        self.an_save_carbon.setIcon(QIcon(icons_path['save']))
        self.an_save_carbon.setIconSize(QtCore.QSize(20, 20))
        self.an_save_carbon.setToolTip('Guardar Valores')
        self.an_save_carbon.clicked.connect(lambda: self.saveData(3))
        
        self.an_add_carbon.setIcon(QIcon(icons_path['add_plus']))
        self.an_add_carbon.setIconSize(QtCore.QSize(20, 20))
        self.an_add_carbon.setToolTip('Añadir Registro')
        self.an_add_carbon.clicked.connect(lambda: self.addNewDataRow(self.tableWidget_4))
        
        self.an_remove_carbon.setIcon(QIcon(icons_path['drop_rel']))
        self.an_remove_carbon.setIconSize(QtCore.QSize(20, 20))
        self.an_remove_carbon.setToolTip('Añadir Registro')
        self.an_remove_carbon.clicked.connect(lambda: self.selectDeleteDataRow(self.tableWidget_4))


        
        
        pass
    

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

    def saveData(self,i):
        if i == 0:
            confirm = QMessageBox.question(
                self, 'aGrae GIS', f"Seguro quiere Actualizar Los valores de textura?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if confirm == QMessageBox.Yes:
                try:
                    for r in range(self.tableWidget_1.rowCount()):
                        id = self.tableWidget_1.item(r, 0).text()
                        categoria = self.tableWidget_1.item(r, 1).text()
                        grupo = self.tableWidget_1.item(r, 2).text()
                        arena_i = self.tableWidget_1.item(r, 3).text()
                        arena_s = self.tableWidget_1.item(r, 4).text()
                        limo_i = self.tableWidget_1.item(r, 5).text()
                        limo_s = self.tableWidget_1.item(r, 6).text()
                        arcilla_i = self.tableWidget_1.item(r, 7).text()
                        arcilla_s = self.tableWidget_1.item(r, 8).text()
                        ceap_i = self.tableWidget_1.item(r, 9).text()
                        ceap_s = self.tableWidget_1.item(r, 10).text()
                        cra = self.tableWidget_1.item(r, 11).text()
                        hsg = self.tableWidget_1.item(r, 12).text()
                        grupo_label = self.tableWidget_1.item(r, 13).text()
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
                    self.editionMode(self.tableWidget_1, self.an_save_textura_btn)
                    self.utils.msgBar(
                        'Parametros de Textura Actualizados Correctamente', 3, 5)

                except Exception as ex:
                    print(ex)
                    QMessageBox.about(self, 'aGrae GIS', 'Ocurrio un Error')

        elif i == 1:
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
                    self.editionMode(self.tableWidget_2,
                                     self.an_save_ph)

                    self.utils.msgBar(
                        'Parametros de pH Actualizados Correctamente', 3, 5)

                except Exception as ex:
                    print(ex)
                    QMessageBox.about(self, 'aGrae GIS', 'Ocurrio un Error')

        elif i == 2:
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
                    self.editionMode(self.tableWidget_3,
                                     self.an_save_ce)

                    self.utils.msgBar(
                        'Parametros de Conductividad Electrica Actualizados Correctamente', 3, 5)

                except Exception as ex:
                    print(ex)
                    QMessageBox.about(self, 'aGrae GIS', 'Ocurrio un Error')
        elif i == 3:
            confirm = QMessageBox.question(
                self, 'aGrae GIS', f"Seguro quiere Actualizar Los valores de Carbonatos?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if confirm == QMessageBox.Yes:
                try:
                    for r in range(self.initialRowCount):
                        id = self.tableWidget_4.item(r, 0).text()
                        tipo = self.tableWidget_4.item(r, 1).text()
                        li = self.tableWidget_4.item(r, 2).text()
                        ls = self.tableWidget_4.item(r, 3).text()
                        sql = f"""update analisis.carbonatos set 
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
                                print('Carbonato: {} actualizado correctamente'.format(id))
                            except Exception as ex:
                                print(ex)
                    if self.tableWidget_4.rowCount() > self.initialRowCount:
                        for r in range(self.initialRowCount, self.tableWidget_4.rowCount()):
                            if self.tableWidget_4.item(r, 1) != None and self.tableWidget_4.item(r, 2) != None and self.tableWidget_4.item(r, 3) != None:
                                tipo = self.tableWidget_4.item(r, 1).text()
                                li = self.tableWidget_4.item(r, 2).text()
                                ls = self.tableWidget_4.item(r, 3).text()
                                sql = f"""insert into analisis.carbonatos(tipo,limite_inferior,limite_superior) 
                                values('{tipo}',{li},{ls})"""
                                with self.conn:
                                    try:
                                        cursor = self.conn.cursor()
                                        cursor.execute(sql)
                                        self.conn.commit()
                                        # print(
                                        #     'Carbonato: {} actualizado correctamente'.format(id))
                                    except Exception as ex:
                                        print('error ingresando')
                                        print(ex)
                    if len(self.removeIds) > 0: 
                        for r in self.removeIds:
                            confirm = QMessageBox.question(
                                self, 'aGrae GIS', f"Desea Borrar los datos de la fila {r}?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                            if confirm == QMessageBox.Yes:
                                sql = f"""delete from analisis.carbonatos                                 
                                    where id = {int(r)}"""
                                with self.conn: 
                                    cursor = self.conn.cursor() 
                                    try: 
                                        cursor.execute(sql)
                                        self.conn.commit()
                                        self.tableWidget_4.removeRow(r.row())
                                    except Exception as ex:
                                        print(ex)
                                        self.conn.rollback()                                    
                            else: 
                                pass
                    self.loadData(i)
                    self.editionMode(self.tableWidget_4, self.an_save_carbon,self.an_add_carbon, self.an_remove_carbon)

                    self.utils.msgBar(
                        'Parametros de Carbonatos Actualizados Correctamente', 3, 5)

                except Exception as ex:
                    print(ex)
                    QMessageBox.about(self, 'aGrae GIS', 'Ocurrio un Error')


            
    def loadData(self,i):

        if i == None:
            # print(i)
            sql = 'select * from analisis.textura order by idtextura '
            self.tools.populateTable(sql, self.tableWidget_1)

        if i == 1:
            # print(i)
            sql = 'select * from analisis.ph order by id '
            self.tools.populateTable(sql, self.tableWidget_2)
            
        elif i == 2:
            # print(i)
            sql = 'select * from analisis.conductividad_electrica order by idce '
            self.tools.populateTable(sql, self.tableWidget_3)


        elif i == 3:
            # print(i)
            sql = 'select * from analisis.carbonatos order by id '
            self.tools.populateTable(sql,self.tableWidget_4)
        elif i == 4:
            # print(i)
            sql = 'select * from analisis.caliza_activa  order by id '
            self.tools.populateTable(sql,self.tableWidget_5)

    def editionMode(self,table,b1,b2,b3): 
        if self.editStatus == False:
            table.setEditTriggers(QAbstractItemView.AllEditTriggers)
            self.editStatus = True
            self.initialRowCount = table.rowCount()
            b1.setEnabled(True)
            b2.setEnabled(True)
            b3.setEnabled(True)
        
        else:
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.editStatus = False
            self.initialRowCount = 0
            b1.setEnabled(False)
            b2.setEnabled(False)
            b3.setEnabled(False)

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
        
    def addNewDataRow(self,table): 
        delegate = ColorDelegateGreen(table)

        table.insertRow(table.rowCount())
        rowCount = table.rowCount()
        
        table.setItem(rowCount-1,0, QTableWidgetItem(str(rowCount)))
        rowCount = table.rowCount()-1
        table.setItemDelegateForRow(rowCount, delegate)

    def selectDeleteDataRow(self,table): 
        delegate = ColorDelegateRed(table)
        if table.rowCount() > 0:
            idx = table.selectionModel().selectedRows()
            if len(idx) == 1: 
                for r in sorted(idx):
                    id = int(table.item(r.row(),0).text())
                    row = r.row()
                    table.setItemDelegateForRow(row, delegate)
                    if id not in self.removeIds: 
                        self.removeIds.append(int(id))
                    # table.removeRow(r.row())
                #     print(int(table.item(r.row(), 0).text()))

                # print(self.removeIds)
                    

            else: 
                print('Debe seleccionar una fila')
            


        pass
    


class ColorDelegateRed(QtWidgets.QStyledItemDelegate):

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.backgroundBrush = QtGui.QColor("red")
class ColorDelegateGreen(QtWidgets.QStyledItemDelegate):

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        
        option.backgroundBrush = QtGui.QColor(170,240,170)
