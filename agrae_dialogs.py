import os
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator, QIcon
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import * 
from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal

from .utils import AgraeUtils, AgraeToolset

agraeSegmentoDialog, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui/dialogs/parcela_dialog.ui'))

agraeParametrosDialog, _ =  uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui/dialogs/params_dialog.ui'))
agraeCultivoDialog, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/dialogs/cultivo_dialog.ui'))


class cultivoFindDialog(QtWidgets.QDialog, agraeCultivoDialog):

    closingPlugin = pyqtSignal()
    getIdCultivo = pyqtSignal(int)

    def __init__(self, parent=None):
        """Constructor."""
        super(cultivoFindDialog, self).__init__(parent)
        self.utils = AgraeUtils()
        self.conn = self.utils.Conn()
        self.setupUi(self)
        self.UIcomponents()
        self.editStatus = False
        self.initialRowCount = None

    def UIcomponents(self):
        icons_path = self.utils.iconsPath()
        data = self.dataAuto()
        lista = [e[0] for e in data]
        # print(lista)
        completer = QCompleter(lista)
        completer.setCaseSensitivity(False)

        self.lineEdit.setClearButtonEnabled(True)
        line_buscar_action = self.lineEdit.addAction(
            QIcon(icons_path['search_icon_path']), self.lineEdit.TrailingPosition)
        line_buscar_action.triggered.connect(self.buscar)


        # self.lineEdit.returnPressed.connect(self.buscar)

        # self.btn_buscar.clicked.connect(self.buscar)
        self.lineEdit.setCompleter(completer)

        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.pushButton.clicked.connect(self.selectIdCultivo)
        self.pushButton.setIconSize(QtCore.QSize(20, 20))
        self.pushButton.setIcon(QIcon(icons_path['share']))

        self.edit_btn.setIcon(QIcon(icons_path['pen-to-square']))
        self.edit_btn.setIconSize(QtCore.QSize(20, 20))
        self.edit_btn.setToolTip('Editar Valores')
        self.edit_btn.clicked.connect(lambda:  self.editionMode(self.tableWidget))
        
        self.save_btn.setIcon(QIcon(icons_path['save']))
        self.save_btn.setIconSize(QtCore.QSize(20, 20))
        self.save_btn.setToolTip('Editar Valores')
        self.save_btn.clicked.connect(lambda:  self.editionMode(self.tableWidget))
        
            
       

    def selectIdCultivo(self):
        row = self.tableWidget.currentRow()
        idCultivo = int(self.tableWidget.item(row, 0).text())
        self.getIdCultivo.emit(idCultivo)
        self.close()

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    def data(self, filtro=None):
        if filtro == None:
            cursor = self.conn.cursor()
            sql = "select  * from cultivo order by idcultivo"
            cursor.execute(sql)
            data = cursor.fetchall()
        else:
            cursor = self.conn.cursor()
            sql = f"select * from cultivo where nombre ilike '%{filtro}%' order by idcultivo"
            cursor.execute(sql)
            data = cursor.fetchall()
        if len(data) >= 1:
            return data
        elif len(data) == 0:
            data = [0, 0]
            return data

    def dataAuto(self):
        cursor = self.conn.cursor()
        sql = "select nombre from cultivo"
        cursor.execute(sql)
        data = cursor.fetchall()
        return data

    def populate(self, data):
        try:
            # print(data)
            a = len(data)
            b = len(data[0])
            i = 1
            j = 1
            self.tableWidget.setRowCount(a)
            self.tableWidget.setColumnCount(b)
            for j in range(a):
                for i in range(b):
                    item = QTableWidgetItem(str(data[j][i]))
                    self.tableWidget.setItem(j, i, item)
            
            self.tableWidget.setColumnHidden(18, True)

        except:
            QMessageBox.about(self, "Error:", "No Existen Registros")
            # print('error')

    def loadData(self, param=None):
        if param == None:
            data = self.data()
            self.populate(data)
        else:
            data = self.data(param)
            self.populate(data)
        pass

    def buscar(self):
        filtro = self.lineEdit.text()
        if filtro != '':
            self.loadData(filtro)
        pass
    
    def editionMode(self, table):
        if self.editStatus == False:
            print('editando')
            table.setEditTriggers(QAbstractItemView.AllEditTriggers)
            # delegateCalcio = self.readOnlyColumn(self.tableWidget_7)
            # self.tableWidget_7.setItemDelegateForColumn(2, delegateCalcio)
            self.editStatus = True
            self.initialRowCount = table.rowCount()
            # self.tableWidget.itemChanged.connect(self.test)
            # b1.setEnabled(True)
            # b2.setEnabled(True)
            # b3.setEnabled(True)

        else:
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.editStatus = False
            self.initialRowCount = 0
            # self.tableWidget.itemChanged.disconnect()
            # b1.setEnabled(False)
            # b2.setEnabled(False)
            # b3.setEnabled(False)

    def saveData(self):         
        confirm = QMessageBox.question(
            self, 'aGrae GIS', f"Seguro quiere Actualizar Los valores de textura?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:           
            for r in range(self.tableWidget.rowCount()):
                id = self.tableWidget.item(r, 0).text()
                categoria = self.tableWidget.item(r, 1).text()
                grupo = self.tableWidget.item(r, 2).text()
                arena_i = self.tableWidget.item(r, 3).text()
                arena_s = self.tableWidget.item(r, 4).text()
                limo_i = self.tableWidget.item(r, 5).text()
                limo_s = self.tableWidget.item(r, 6).text()
                arcilla_i = self.tableWidget.item(r, 7).text()
                arcilla_s = self.tableWidget.item(r, 8).text()
                ceap_i = self.tableWidget.item(r, 9).text()
                ceap_s = self.tableWidget.item(r, 10).text()
                cra = self.tableWidget.item(r, 11).text()
                hsg = self.tableWidget.item(r, 12).text()
                grupo_label = self.tableWidget.item(r, 13).text()
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
                    except Exception as ex:
                        print(ex)

    def test(self,item):
        print('Cambio en Columna {} Fila {}'.format(item.column(),item.row()))
        pass

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
        self.removeRows = []
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
        self.tableWidget_6.setColumnHidden(0, True)     
        self.tableWidget_7.setColumnHidden(0, True) 
        self.tableWidget_8.setColumnHidden(0, True) 
        self.tableWidget_9.setColumnHidden(0, True) 

        self.setButtonActions(self.an_edit_textura_btn, self.an_save_textura_btn, self.an_add_textura, self.an_remove_textura, self.tableWidget_1, 0)
        self.setButtonActions(self.an_edit_ph, self.an_save_ph, self.an_add_ph, self.an_remove_ph, self.tableWidget_2, 1,2,3)
        self.setButtonActions(self.an_edit_ce, self.an_save_ce, self.an_add_ce, self.an_remove_ce, self.tableWidget_3, 2,2,3)
        self.setButtonActions(self.an_edit_carbon, self.an_save_carbon, self.an_add_carbon, self.an_remove_carbon, self.tableWidget_4, 3,2,3)
        self.setButtonActions(self.an_edit_ca, self.an_save_ca, self.an_add_ca, self.an_remove_ca, self.tableWidget_5, 4,2,3)
        self.setButtonActions(self.an_edit_cic, self.an_save_cic, self.an_add_cic, self.an_remove_cic, self.tableWidget_6, 5,2,3)
        self.setButtonActions(self.an_edit_calcio, self.an_save_calcio, self.an_add_calcio, self.an_remove_calcio, self.tableWidget_7,6,4,5)
        self.setButtonActions(self.an_edit_magnesio, self.an_save_magnesio, self.an_add_magnesio, self.an_remove_magnesio, self.tableWidget_8,7,4,5)
        self.setButtonActions(self.an_edit_potasio, self.an_save_potasio, self.an_add_potasio, self.an_remove_potasio, self.tableWidget_9,8,5,6)
        self.setButtonActions(self.an_edit_sodio, self.an_save_sodio, self.an_add_sodio, self.an_remove_sodio, self.tableWidget_10,9,3,4)
        self.setButtonActions(self.an_edit_nitrogeno, self.an_save_nitrogeno, self.an_add_nitrogeno, self.an_remove_nitrogeno, self.tableWidget_11,10,2,3)

        self.tableWidget_2.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.tableWidget_3.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.tableWidget_3.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.tableWidget_3.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        self.tableWidget_3.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)

        self.tableWidget_4.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tableWidget_5.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tableWidget_6.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        # self.tableWidget_4.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)

        self.tableWidget_7.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.tableWidget_7.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.tableWidget_7.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        self.tableWidget_7.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        self.tableWidget_7.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        self.tableWidget_7.horizontalHeader().setSectionResizeMode(6, QtWidgets.QHeaderView.Stretch)
        
        self.tableWidget_8.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.tableWidget_8.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.tableWidget_8.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        self.tableWidget_8.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        self.tableWidget_8.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        self.tableWidget_8.horizontalHeader().setSectionResizeMode(6, QtWidgets.QHeaderView.Stretch)


        self.tableWidget_9.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.tableWidget_9.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.tableWidget_9.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        self.tableWidget_9.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        self.tableWidget_9.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.Stretch)
        self.tableWidget_9.horizontalHeader().setSectionResizeMode(6, QtWidgets.QHeaderView.Stretch)
        


        
        
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
        # TEXTURA
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
                            except Exception as ex:
                                print(ex)
                    if self.tableWidget_1.rowCount() > self.initialRowCount:
                        for r in range(self.initialRowCount, self.tableWidget_1.rowCount()):
                            if self.tableWidget_1.item(r, 1) != None and self.tableWidget_1.item(r, 2) != None and self.tableWidget_1.item(r, 3) != None and self.tableWidget_1.item(r, 4) != None:
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
                                sql = f"""insert into analisis.textura(categoria,grupo,arena_i,arena_s,limo_i,limo_s,arcilla_i,arcilla_s,ceap_i,ceap_s,cra_cod,hsg,grupo_label) 
                                values('{categoria}',{grupo},{arena_i},{arena_s},{limo_i},{limo_s},{arcilla_i},{arcilla_s},{ceap_i},{ceap_s},{cra},'{hsg}','{grupo_label}')"""
                                with self.conn:
                                    try:
                                        cursor = self.conn.cursor()
                                        cursor.execute(sql)
                                        self.conn.commit()
                                        
                                    except Exception as ex:
                                        print('error ingresando')
                                        print(ex)
                                        self.conn.rollback()
                    if len(self.removeIds) > 0:
                        for r in self.removeIds:
                            confirm = QMessageBox.question(
                                self, 'aGrae GIS', f"Desea Borrar los registros?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                            if confirm == QMessageBox.Yes:
                                sql = f"""delete from analisis.textura                                 
                                    where idtextura = {int(r)}"""
                                # print(sql)
                                with self.conn:
                                    cursor = self.conn.cursor()
                                    try:
                                        cursor.execute(sql)
                                        self.conn.commit()
                                        
                                    except Exception as ex:
                                        print(ex)
                                        self.conn.rollback()
                                for row in self.removeRows: 
                                    self.tableWidget_1.removeRow(row)
                            else:
                                pass
                    
                    self.removeIds = []
                    self.removeRows = []
                    self.loadData(i)
                    self.editionMode(self.tableWidget_1,self.an_save_textura_btn,self.an_add_textura,self.an_remove_textura)
                    self.utils.msgBar(
                        'Parametros de Textura Actualizados Correctamente', 3, 5)

                except Exception as ex:
                    print(ex)
                    QMessageBox.about(self, 'aGrae GIS', 'Ocurrio un Error')
        # PH
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
                    if self.tableWidget_2.rowCount() > self.initialRowCount:
                        for r in range(self.initialRowCount, self.tableWidget_2.rowCount()):
                            if self.tableWidget_2.item(r, 1) != None and self.tableWidget_2.item(r, 2) != None and self.tableWidget_2.item(r, 3) != None:
                                tipo = self.tableWidget_2.item(r, 1).text()
                                li = self.tableWidget_2.item(r, 2).text()
                                ls = self.tableWidget_2.item(r, 3).text()
                                sql = f"""insert into analisis.ph(tipo,limite_inferior,limite_superior) 
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
                                        self.conn.rollback()
                    if len(self.removeIds) > 0:
                        # print(self.removeIds)
                        for r in self.removeIds:
                            confirm = QMessageBox.question(
                                self, 'aGrae GIS', f"Desea Borrar los registros?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                            if confirm == QMessageBox.Yes:
                                sql = f"""delete from analisis.ph                                 
                                    where id = {int(r)}"""
                                # print(sql)
                                with self.conn:
                                    cursor = self.conn.cursor()
                                    try:
                                        cursor.execute(sql)
                                        self.conn.commit()
                                    except Exception as ex:
                                        print(ex)
                                        self.conn.rollback()
                                for row in self.removeRows:
                                    self.tableWidget_2.removeRow(row)
                            else:
                                pass
                                
                    self.removeIds = [] 
                    self.removeRows = []
                    self.loadData(i)
                    self.editionMode(self.tableWidget_2,self.an_save_ph,self.an_add_ph,self.an_remove_ph)

                    self.utils.msgBar(
                        'Parametros de pH Actualizados Correctamente', 3, 5)

                except Exception as ex:
                    print(ex)
                    QMessageBox.about(self, 'aGrae GIS', 'Ocurrio un Error')
        # CE
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
                    if self.tableWidget_3.rowCount() > self.initialRowCount:
                        for r in range(self.initialRowCount, self.tableWidget_3.rowCount()):
                            if self.tableWidget_3.item(r, 1) != None and self.tableWidget_3.item(r, 2) != None and self.tableWidget_3.item(r, 3) != None and self.tableWidget_3.item(r, 4) != None:
                                tipo = self.tableWidget_3.item(r, 1).text()
                                li = self.tableWidget_3.item(r, 2).text()
                                ls = self.tableWidget_3.item(r, 3).text()
                                influencia = self.tableWidget_3.item(r, 4).text()
                                sql = f"""insert into analisis.conductividad_electrica(tipo,limite_i,limite_s, influencia) 
                                values('{tipo}',{li},{ls},'{influencia}')"""
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
                                        self.conn.rollback()
                    if len(self.removeIds) > 0:
                        # print(self.removeIds)
                        for r in self.removeIds:
                            confirm = QMessageBox.question(
                                self, 'aGrae GIS', f"Desea Borrar los registros?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                            if confirm == QMessageBox.Yes:
                                sql = f"""delete from analisis.conductividad_electrica                                 
                                    where idce = {int(r)}"""
                                # print(sql)
                                with self.conn:
                                    cursor = self.conn.cursor()
                                    try:
                                        cursor.execute(sql)
                                        self.conn.commit()
                                    except Exception as ex:
                                        print(ex)
                                        self.conn.rollback()
                                for row in self.removeRows:
                                    self.tableWidget_3.removeRow(row)
                            else:
                                pass
                    self.removeIds = [] 
                    self.removeRows = []
                    self.loadData(i)
                    self.editionMode(self.tableWidget_3, self.an_save_ce, self.an_add_ce, self.an_remove_ce)

                    self.utils.msgBar(
                        'Parametros de Conductividad Electrica Actualizados Correctamente', 3, 5)

                except Exception as ex:
                    print(ex)
                    QMessageBox.about(self, 'aGrae GIS', 'Ocurrio un Error')
        # CARBONATOS
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
                                        self.conn.rollback()
                    if len(self.removeIds) > 0: 
                        for r in self.removeIds:
                            confirm = QMessageBox.question(
                                self, 'aGrae GIS', f"Desea Borrar los registros?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                            if confirm == QMessageBox.Yes:
                                sql = f"""delete from analisis.carbonatos                                 
                                    where id = {int(r)}"""
                                with self.conn: 
                                    cursor = self.conn.cursor() 
                                    try: 
                                        cursor.execute(sql)
                                        self.conn.commit()
                                    except Exception as ex:
                                        print(ex)
                                        self.conn.rollback()
                                for row in self.removeRows:
                                    self.tableWidget_4.removeRow(row)
                            else: 
                                pass
                    self.removeIds = []
                    self.removeRows = []
                    self.loadData(i)
                    self.editionMode(self.tableWidget_4, self.an_save_carbon,self.an_add_carbon, self.an_remove_carbon)

                    self.utils.msgBar(
                        'Parametros de Carbonatos Actualizados Correctamente', 3, 5)

                except Exception as ex:
                    print(ex)
                    QMessageBox.about(self, 'aGrae GIS', 'Ocurrio un Error')
        # CALIZA
        elif i == 4: 
            confirm = QMessageBox.question(
                self, 'aGrae GIS', f"Seguro quiere Actualizar Los valores de Carbonatos?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if confirm == QMessageBox.Yes:
                try:
                    for r in range(self.initialRowCount):
                        id = self.tableWidget_5.item(r, 0).text()
                        tipo = self.tableWidget_5.item(r, 1).text()
                        li = self.tableWidget_5.item(r, 2).text()
                        ls = self.tableWidget_5.item(r, 3).text()
                        sql = f"""update analisis.caliza_activa set 
                                tipo = '{tipo}',
                                limite_i = {li},
                                limite_s = {ls}
                                where id = {id}
                                """
                        with self.conn:
                            try:
                                cursor = self.conn.cursor()
                                cursor.execute(sql)
                                self.conn.commit()
                                print(
                                    'Carbonato: {} actualizado correctamente'.format(id))
                            except Exception as ex:
                                print(ex)
                    if self.tableWidget_5.rowCount() > self.initialRowCount:
                        for r in range(self.initialRowCount, self.tableWidget_5.rowCount()):
                            if self.tableWidget_5.item(r, 1) != None and self.tableWidget_5.item(r, 2) != None and self.tableWidget_5.item(r, 3) != None:
                                tipo = self.tableWidget_5.item(r, 1).text()
                                li = self.tableWidget_5.item(r, 2).text()
                                ls = self.tableWidget_5.item(r, 3).text()
                                sql = f"""insert into analisis.caliza_activa(tipo,limite_i,limite_s) 
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
                                        self.conn.rollback()
                    if len(self.removeIds) > 0:
                        for r in self.removeIds:
                            confirm = QMessageBox.question(
                                self, 'aGrae GIS', f"Desea Borrar los registros?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                            if confirm == QMessageBox.Yes:
                                sql = f"""delete from analisis.caliza_activa                                
                                    where id = {int(r)}"""
                                with self.conn:
                                    cursor = self.conn.cursor()
                                    try:
                                        cursor.execute(sql)
                                        self.conn.commit()
                                    except Exception as ex:
                                        print(ex)
                                        self.conn.rollback()
                                for row in self.removeRows:
                                    self.tableWidget_5.removeRow(row)
                            else:
                                pass
                    self.removeIds = []
                    self.removeRows = []
                    self.loadData(i)
                    self.editionMode(self.tableWidget_5, self.an_save_ca,
                                     self.an_add_ca, self.an_remove_ca)

                    self.utils.msgBar(
                        'Parametros de Carbonatos Actualizados Correctamente', 3, 5)

                except Exception as ex:
                    print(ex)
                    QMessageBox.about(self, 'aGrae GIS', 'Ocurrio un Error')
        # CIC
        elif i == 5: 
            confirm = QMessageBox.question(
                self, 'aGrae GIS', f"Seguro quiere Actualizar Los valores de Carbonatos?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if confirm == QMessageBox.Yes:
                try:
                    for r in range(self.initialRowCount):
                        id = self.tableWidget_6.item(r, 0).text()
                        tipo = self.tableWidget_6.item(r, 1).text()
                        li = self.tableWidget_6.item(r, 2).text()
                        ls = self.tableWidget_6.item(r, 3).text()
                        sql = f"""update analisis.cic set 
                                tipo = '{tipo}',
                                limite_i = {li},
                                limite_s = {ls}
                                where id = {id}
                                """
                        with self.conn:
                            try:
                                cursor = self.conn.cursor()
                                cursor.execute(sql)
                                self.conn.commit()
                                print(
                                    'Carbonato: {} actualizado correctamente'.format(id))
                            except Exception as ex:
                                print(ex)
                    if self.tableWidget_6.rowCount() > self.initialRowCount:
                        for r in range(self.initialRowCount, self.tableWidget_6.rowCount()):
                            if self.tableWidget_6.item(r, 1) != None and self.tableWidget_6.item(r, 2) != None and self.tableWidget_6.item(r, 3) != None:
                                tipo = self.tableWidget_6.item(r, 1).text()
                                li = self.tableWidget_6.item(r, 2).text()
                                ls = self.tableWidget_6.item(r, 3).text()
                                sql = f"""insert into analisis.cic(tipo,limite_i,limite_s) 
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
                                        self.conn.rollback()
                    if len(self.removeIds) > 0:
                        for r in self.removeIds:
                            confirm = QMessageBox.question(
                                self, 'aGrae GIS', f"Desea Borrar los registros?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                            if confirm == QMessageBox.Yes:
                                sql = f"""delete from analisis.cic                                
                                    where id = {int(r)}"""
                                with self.conn:
                                    cursor = self.conn.cursor()
                                    try:
                                        cursor.execute(sql)
                                        self.conn.commit()
                                    except Exception as ex:
                                        print(ex)
                                        self.conn.rollback()
                                for row in self.removeRows:
                                    self.tableWidget_6.removeRow(row)
                            else:
                                pass
                    self.removeIds = []
                    self.removeRows = []
                    self.loadData(i)
                    self.editionMode(self.tableWidget_6, self.an_save_cic,
                                     self.an_add_cic, self.an_remove_cic)

                    self.utils.msgBar(
                        'Parametros de Carbonatos Actualizados Correctamente', 3, 5)

                except Exception as ex:
                    print(ex)
                    QMessageBox.about(self, 'aGrae GIS', 'Ocurrio un Error')
        # CALCIO
        elif i == 6: 
            confirm = QMessageBox.question(
                self, 'aGrae GIS', f"Seguro quiere Actualizar Los valores de Carbonatos?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if confirm == QMessageBox.Yes:
                try:
                    for r in range(self.initialRowCount):
                        id = self.tableWidget_7.item(r, 0).text()
                        suelo = self.tableWidget_7.item(r, 1).text()
                        tipo = self.tableWidget_7.item(r, 3).text()
                        li = self.tableWidget_7.item(r, 4).text()
                        ls = self.tableWidget_7.item(r, 5).text()
                        incremento = self.tableWidget_7.item(r,6).text()
                        if incremento == 'None':
                            incremento = 0
                        sql = f"""update analisis.calcio set
                                suelo = {suelo}, 
                                tipo = '{tipo}',
                                limite_inferior = {li},
                                limite_superior = {ls},
                                incremento = {incremento}
                                where id = {id}
                                """
                        with self.conn:
                            try:
                                cursor = self.conn.cursor()
                                cursor.execute(sql)
                                self.conn.commit()
                            except Exception as ex:
                                print(ex)
                    if self.tableWidget_7.rowCount() > self.initialRowCount:
                        for r in range(self.initialRowCount, self.tableWidget_7.rowCount()):
                            if self.tableWidget_7.item(r, 1) != None and self.tableWidget_7.item(r, 2) != None and self.tableWidget_7.item(r, 3) != None:
                                suelo = self.tableWidget_7.item(r, 1).text()
                                tipo = self.tableWidget_7.item(r, 3).text()
                                li = self.tableWidget_7.item(r, 4).text()
                                ls = self.tableWidget_7.item(r, 5).text()
                                incremento = self.tableWidget_7.item(r,6).text()
                                sql = f"""insert into analisis.calcio(suelo,tipo,limite_inferior,limite_superior,incremento) 
                                values({suelo},'{tipo}',{li},{ls},{incremento})"""
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
                                        self.conn.rollback()
                    if len(self.removeIds) > 0:
                        for r in self.removeIds:
                            confirm = QMessageBox.question(
                                self, 'aGrae GIS', f"Desea Borrar los registros?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                            if confirm == QMessageBox.Yes:
                                sql = f"""delete from analisis.calcio                                
                                    where id = {int(r)}"""
                                with self.conn:
                                    cursor = self.conn.cursor()
                                    try:
                                        cursor.execute(sql)
                                        self.conn.commit()
                                    except Exception as ex:
                                        print(ex)
                                        self.conn.rollback()
                                for row in self.removeRows:
                                    self.tableWidget_7.removeRow(row)
                            else:
                                pass
                    self.removeIds = []
                    self.removeRows = []
                    self.loadData(i)
                    self.editionMode(self.tableWidget_7, self.an_save_calcio,
                                     self.an_add_calcio, self.an_remove_calcio)

                    self.utils.msgBar(
                        'Parametros de Carbonatos Actualizados Correctamente', 3, 5)

                except Exception as ex:
                    print(ex)
                    QMessageBox.about(self, 'aGrae GIS', 'Ocurrio un Error')
        # MAGNESIO
        elif i == 7: 
            confirm = QMessageBox.question(
                self, 'aGrae GIS', f"Seguro quiere Actualizar Los valores de Magnesio?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if confirm == QMessageBox.Yes:
                try:
                    for r in range(self.initialRowCount):
                        id = self.tableWidget_8.item(r, 0).text()
                        suelo = self.tableWidget_8.item(r, 1).text()
                        tipo = self.tableWidget_8.item(r, 3).text()
                        li = self.tableWidget_8.item(r, 4).text()
                        ls = self.tableWidget_8.item(r, 5).text()
                        incremento = self.tableWidget_8.item(r,6).text()
                        if incremento == 'None':
                            incremento = 0
                        sql = f"""update analisis.magnesio set
                                suelo = {suelo}, 
                                tipo = '{tipo}',
                                limite_inferior = {li},
                                limite_superior = {ls},
                                incremento = {incremento}
                                where id = {id}
                                """
                        with self.conn:
                            try:
                                cursor = self.conn.cursor()
                                cursor.execute(sql)
                                self.conn.commit()
                            except Exception as ex:
                                print(ex)
                    if self.tableWidget_8.rowCount() > self.initialRowCount:
                        for r in range(self.initialRowCount, self.tableWidget_8.rowCount()):
                            if self.tableWidget_8.item(r, 1) != None and self.tableWidget_8.item(r, 2) != None and self.tableWidget_8.item(r, 3) != None:
                                suelo = self.tableWidget_8.item(r, 1).text()
                                tipo = self.tableWidget_8.item(r, 3).text()
                                li = self.tableWidget_8.item(r, 4).text()
                                ls = self.tableWidget_8.item(r, 5).text()
                                incremento = self.tableWidget_8.item(r,6).text()
                                sql = f"""insert into analisis.magnesio(suelo,tipo,limite_inferior,limite_superior,incremento) 
                                values({suelo},'{tipo}',{li},{ls},{incremento})"""
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
                                        self.conn.rollback()
                    if len(self.removeIds) > 0:
                        for r in self.removeIds:
                            confirm = QMessageBox.question(
                                self, 'aGrae GIS', f"Desea Borrar los registros?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                            if confirm == QMessageBox.Yes:
                                sql = f"""delete from analisis.magnesio                                
                                    where id = {int(r)}"""
                                with self.conn:
                                    cursor = self.conn.cursor()
                                    try:
                                        cursor.execute(sql)
                                        self.conn.commit()
                                    except Exception as ex:
                                        print(ex)
                                        self.conn.rollback()
                                for row in self.removeRows:
                                    self.tableWidget_8.removeRow(row)
                            else:
                                pass
                    self.removeIds = []
                    self.removeRows = []
                    self.loadData(i)
                    self.editionMode(self.tableWidget_8, self.an_save_magnesio,
                                     self.an_add_magnesio, self.an_remove_magnesio)

                    self.utils.msgBar(
                        'Parametros de Carbonatos Actualizados Correctamente', 3, 5)

                except Exception as ex:
                    print(ex)
                    QMessageBox.about(self, 'aGrae GIS', 'Ocurrio un Error')
        # POTASIO
        elif i == 8:
            confirm = QMessageBox.question(
                self, 'aGrae GIS', f"Seguro quiere Actualizar Los valores de Magnesio?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if confirm == QMessageBox.Yes:
                try:
                    for r in range(self.initialRowCount):
                        id = self.tableWidget_9.item(r, 0).text()
                        regimen = self.tableWidget_9.item(r, 1).text()
                        suelo = self.tableWidget_9.item(r, 2).text()
                        nivel = self.tableWidget_9.item(r, 3).text()
                        tipo = self.tableWidget_9.item(r, 4).text()
                        li = self.tableWidget_9.item(r, 5).text()
                        ls = self.tableWidget_9.item(r, 6).text()
                        incremento = self.tableWidget_9.item(r, 7).text()
                        if incremento == 'None':
                            incremento = 0
                        sql = f"""update analisis.potasio set
                                regimen = {regimen},
                                suelo = {suelo}, 
                                nivel = {nivel}, 
                                tipo = '{tipo}',
                                limite_inferior = {li},
                                limite_superior = {ls},
                                incremento = {incremento}
                                where id = {id}
                                """
                        with self.conn:
                            try:
                                cursor = self.conn.cursor()
                                cursor.execute(sql)
                                self.conn.commit()
                            except Exception as ex:
                                print(ex)
                    if self.tableWidget_9.rowCount() > self.initialRowCount:
                        for r in range(self.initialRowCount, self.tableWidget_9.rowCount()):
                            if self.tableWidget_9.item(r, 1) != None and self.tableWidget_9.item(r, 2) != None and self.tableWidget_9.item(r, 3) != None:
                                regimen = self.tableWidget_9.item(r, 1).text()
                                suelo = self.tableWidget_9.item(r, 2).text()
                                nivel = self.tableWidget_9.item(r, 3).text()
                                tipo = self.tableWidget_9.item(r, 4).text()
                                li = self.tableWidget_9.item(r, 5).text()
                                ls = self.tableWidget_9.item(r, 6).text()
                                incremento = self.tableWidget_9.item(r, 7).text()
                                sql = f"""insert into analisis.potasio(regimen,suelo,nivel,tipo,limite_inferior,limite_superior,incremento) 
                                values({regimen},{suelo},{nivel},'{tipo}',{li},{ls},{incremento})"""
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
                                        self.conn.rollback()
                    if len(self.removeIds) > 0:
                        for r in self.removeIds:
                            confirm = QMessageBox.question(
                                self, 'aGrae GIS', f"Desea Borrar los registros?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                            if confirm == QMessageBox.Yes:
                                sql = f"""delete from analisis.potasio                                
                                    where id = {int(r)}"""
                                with self.conn:
                                    cursor = self.conn.cursor()
                                    try:
                                        cursor.execute(sql)
                                        self.conn.commit()
                                    except Exception as ex:
                                        print(ex)
                                        self.conn.rollback()
                                for row in self.removeRows:
                                    self.tableWidget_9.removeRow(row)
                            else:
                                pass
                    self.removeIds = []
                    self.removeRows = []
                    self.loadData(i)
                    self.editionMode(self.tableWidget_9, self.an_save_potasio,
                                     self.an_add_potasio, self.an_remove_potasio)

                    self.utils.msgBar(
                        'Parametros de Carbonatos Actualizados Correctamente', 3, 5)

                except Exception as ex:
                    print(ex)
                    QMessageBox.about(self, 'aGrae GIS', 'Ocurrio un Error')

        # SODIO
        elif i == 9:
            confirm = QMessageBox.question(
                self, 'aGrae GIS', f"Seguro quiere Actualizar Los valores de Magnesio?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if confirm == QMessageBox.Yes:
                try:
                    for r in range(self.initialRowCount):
                        id = self.tableWidget_10.item(r, 0).text()
                        suelo = self.tableWidget_10.item(r, 1).text()
                        tipo = self.tableWidget_10.item(r, 2).text()
                        li = self.tableWidget_10.item(r, 3).text()
                        ls = self.tableWidget_10.item(r, 4).text()
                        incremento = self.tableWidget_10.item(r, 5).text()
                        if incremento == 'None':
                            incremento = 0
                        sql = f"""update analisis.sodio set
                                suelo = {suelo}, 
                                tipo = '{tipo}',
                                limite_inferior = {li},
                                limite_superior = {ls},
                                incremento = {incremento}
                                where id = {id}
                                """
                        with self.conn:
                            try:
                                cursor = self.conn.cursor()
                                cursor.execute(sql)
                                self.conn.commit()
                            except Exception as ex:
                                print(ex)
                    if self.tableWidget_10.rowCount() > self.initialRowCount:
                        for r in range(self.initialRowCount, self.tableWidget_10.rowCount()):
                            if self.tableWidget_10.item(r, 1) != None and self.tableWidget_10.item(r, 2) != None and self.tableWidget_10.item(r, 3) != None:
                                suelo = self.tableWidget_10.item(r, 1).text()
                                tipo = self.tableWidget_10.item(r, 2).text()
                                li = self.tableWidget_10.item(r, 3).text()
                                ls = self.tableWidget_10.item(r, 4).text()
                                incremento = self.tableWidget_10.item(
                                    r, 5).text()
                                sql = f"""insert into analisis.sodio(suelo,tipo,limite_inferior,limite_superior,incremento) 
                                values({suelo},'{tipo}',{li},{ls},{incremento})"""
                                with self.conn:
                                    try:
                                        cursor = self.conn.cursor()
                                        cursor.execute(sql)
                                        self.conn.commit()
                                    except Exception as ex:
                                        print('error ingresando')
                                        print(ex)
                                        self.conn.rollback()
                    if len(self.removeIds) > 0:
                        for r in self.removeIds:
                            confirm = QMessageBox.question(
                                self, 'aGrae GIS', f"Desea Borrar los registros?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                            if confirm == QMessageBox.Yes:
                                sql = f"""delete from analisis.sodio                                
                                    where id = {int(r)}"""
                                with self.conn:
                                    cursor = self.conn.cursor()
                                    try:
                                        cursor.execute(sql)
                                        self.conn.commit()
                                    except Exception as ex:
                                        print(ex)
                                        self.conn.rollback()
                                for row in self.removeRows:
                                    self.tableWidget_10.removeRow(row)
                            else:
                                pass
                    self.removeIds = []
                    self.removeRows = []
                    self.loadData(i)
                    self.editionMode(
                        self.tableWidget_10, self.an_save_sodio, self.an_add_sodio, self.an_remove_sodio)
                except:
                    pass
        # NITROGENO
        elif i == 10:
            confirm = QMessageBox.question(
                self, 'aGrae GIS', f"Seguro quiere Actualizar Los valores de Magnesio?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if confirm == QMessageBox.Yes:
                try:
                    for r in range(self.initialRowCount):
                        id = self.tableWidget_11.item(r, 0).text()
                        tipo = self.tableWidget_11.item(r, 1).text()
                        li = self.tableWidget_11.item(r, 2).text()
                        ls = self.tableWidget_11.item(r, 3).text()
                        incremento = self.tableWidget_11.item(r, 4).text()
                        if incremento == 'None':
                            incremento = 0
                        sql = f"""update analisis.nitrogeno set
                                tipo = '{tipo}',
                                limite_inferior = {li},
                                limite_superior = {ls},
                                incremento = {incremento}
                                where id = {id}
                                """
                        with self.conn:
                            try:
                                cursor = self.conn.cursor()
                                cursor.execute(sql)
                                self.conn.commit()
                            except Exception as ex:
                                print(ex)
                    if self.tableWidget_11.rowCount() > self.initialRowCount:
                        for r in range(self.initialRowCount, self.tableWidget_11.rowCount()):
                            if self.tableWidget_11.item(r, 1) != None :
                                tipo = self.tableWidget_11.item(r, 1).text()
                                li = self.tableWidget_11.item(r, 2).text()
                                ls = self.tableWidget_11.item(r, 3).text()
                                incremento = self.tableWidget_11.item(r, 4).text()
                                sql = f"""insert into analisis.nitrogeno(tipo,limite_inferior,limite_superior,incremento) 
                                values('{tipo}',{li},{ls},{incremento})"""
                                with self.conn:
                                    try:
                                        cursor = self.conn.cursor()
                                        cursor.execute(sql)
                                        self.conn.commit()
                                    except Exception as ex:
                                        print('error ingresando')
                                        print(ex)
                                        self.conn.rollback()
                            else: 
                                print('Algo falla')
                    if len(self.removeIds) > 0:
                        for r in self.removeIds:
                            confirm = QMessageBox.question(
                                self, 'aGrae GIS', f"Desea Borrar los registros?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                            if confirm == QMessageBox.Yes:
                                sql = f"""delete from analisis.nitrogeno                                
                                    where id = {int(r)}"""
                                with self.conn:
                                    cursor = self.conn.cursor()
                                    try:
                                        cursor.execute(sql)
                                        self.conn.commit()
                                    except Exception as ex:
                                        print(ex)
                                        self.conn.rollback()
                                for row in self.removeRows:
                                    self.tableWidget_11.removeRow(row)
                            else:
                                pass
                    self.removeIds = []
                    self.removeRows = []
                    self.loadData(i)
                    self.editionMode(
                        self.tableWidget_11, self.an_save_nitrogeno, self.an_add_nitrogeno, self.an_remove_nitrogeno)
                except:
                    pass
    
    def setButtonActions(self,btn_edit,btn_save,btn_add,btn_remove,table,i,c=None,v=None):
        icons_path = self.utils.iconsPath()
        btn_edit.setIcon(QIcon(icons_path['pen-to-square']))
        btn_edit.setIconSize(QtCore.QSize(20, 20))
        btn_edit.setToolTip('Editar Valores')
        btn_edit.clicked.connect(lambda:  self.editionMode(table, btn_save, btn_add, btn_remove))
        btn_save.setIcon(QIcon(icons_path['save']))
        btn_save.setIconSize(QtCore.QSize(20, 20))
        btn_save.setToolTip('Guardar Valores')
        btn_save.clicked.connect(lambda: self.saveData(i))
        btn_add.setIcon(QIcon(icons_path['add_plus']))
        btn_add.setIconSize(QtCore.QSize(20, 20))
        btn_add.setToolTip('Añadir Registro')
        btn_add.clicked.connect(lambda: self.addNewDataRow(table,c,v))
        btn_remove.setIcon(QIcon(icons_path['drop_rel']))
        btn_remove.setIconSize(QtCore.QSize(20, 20))
        btn_remove.setToolTip('Eliminar Registro')
        btn_remove.clicked.connect(
            lambda: self.selectDeleteDataRow(table))

            
    def loadData(self,i):
        self.editStatus = False
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
        elif i == 5:
            # print(i)
            sql = 'select * from analisis.cic  order by id '
            self.tools.populateTable(sql,self.tableWidget_6)
        elif i == 6:
            # print(i)
            sql = 'select distinct ca.id,ca.suelo, t.grupo_label tipo_suelo,ca.tipo ,ca.limite_inferior , ca.limite_superior , ca.incremento from analisis.calcio ca left join analisis.textura t on t.grupo = ca.suelo order by ca.suelo  '
            self.tools.populateTable(sql,self.tableWidget_7)
        elif i == 7:
            # print(i)
            sql = 'select distinct m.id,m.suelo, t.grupo_label tipo_suelo,m.tipo ,m.limite_inferior , m.limite_superior , m.incremento from analisis.magnesio m left join analisis.textura t on t.grupo = m.suelo order by m.suelo '
            self.tools.populateTable(sql,self.tableWidget_8)
        elif i == 8:
            # print(i)
            sql = 'select * from analisis.potasio order by id'
            self.tools.populateTable(sql,self.tableWidget_9)
        elif i == 9:
            # print(i)
            sql = 'select * from analisis.sodio order by id'
            self.tools.populateTable(sql,self.tableWidget_10)
        elif i == 10:
            # print(i)
            sql = 'select * from analisis.nitrogeno order by id'
            self.tools.populateTable(sql,self.tableWidget_11)

    def editionMode(self,table,b1,b2,b3): 
        if self.editStatus == False:
            table.setEditTriggers(QAbstractItemView.AllEditTriggers)
            # delegateCalcio = self.readOnlyColumn(self.tableWidget_7)
            # self.tableWidget_7.setItemDelegateForColumn(2, delegateCalcio)
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

    
    def addNewDataRow(self,table,c=None,v=None): 
        # print('TEST ADD')
        delegate = ColorDelegateGreen(table)

        table.insertRow(table.rowCount())
        rowCount = table.rowCount()
        
        table.setItem(rowCount-1,0, QTableWidgetItem(str(int(table.item(rowCount-2,0).text())+1)))
        if c != None and v != None:
            if table.item(rowCount-2, v) != None:
                table.setItem(rowCount-1,c, QTableWidgetItem(str(table.item(rowCount-2,v).text())))
            else: 
                pass
        rowCount = table.rowCount()-1
        table.setItemDelegateForRow(rowCount, delegate)

    def selectDeleteDataRow(self,table): 
        # print('TEST REMOVE')
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
                        self.removeRows.append(int(r.row()))
                    # table.removeRow(r.row())
                #     print(int(table.item(r.row(), 0).text()))

                # print(self.removeIds)
                    

            else: 
                print('Debe seleccionar una fila')
            


        pass
    
    def readOnlyColumn(self,table): 
        delegate = ReadOnlyDelegate(table)
        return delegate

class ColorDelegateRed(QtWidgets.QStyledItemDelegate):

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.backgroundBrush = QtGui.QColor("red")
class ColorDelegateGreen(QtWidgets.QStyledItemDelegate):

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        
        option.backgroundBrush = QtGui.QColor(170,240,170)
class ReadOnlyDelegate(QtWidgets.QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        return
