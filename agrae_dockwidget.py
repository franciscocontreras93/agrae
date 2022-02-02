# -*- coding: utf-8 -*-
"""
/***************************************************************************
 agraeDockWidget
                                 A QGIS plugin
 Conjunto de herramientas
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2021-12-03
        git sha              : $Format:%H$
        copyright            : (C) 2021 by  aGrae Solutions, S.L.
        email                : info@agrae.es
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


import os
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QAbstractTableModel
from PyQt5.QtWidgets import *
from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal, QSettings
from .utils import AgraeUtils



agraeSidePanel, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/agrae_dockwidget_base.ui'))
agraeConfigPanel, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/config_ui.ui'))
agraeMainPanel, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/agrae_main.ui'))

agraeParcelaDialog, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/dialogs/parcela_dialog.ui'))
agraeLoteDialog, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/dialogs/lote_dialog.ui'))
agraeExpDialog, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/dialogs/exp_dialog.ui'))
agraeCultivoDialog, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/dialogs/cultivo_dialog.ui'))


class agraeDockWidget(QtWidgets.QDockWidget, agraeSidePanel):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(agraeDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://doc.qt.io/qt-5/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.pushButton.clicked.connect(self.select_input_file)

    def select_input_file(self):
        filename = QFileDialog.getOpenFileName(None,'Seleccionar archivo')
        # print(filename[0])
        self.lineEdit.setText(filename[0])
        print(len(self.lineEdit.text()))

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()


class agraeConfigWidget(QtWidgets.QDialog, agraeConfigPanel):

    closingPlugin2 = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(agraeConfigWidget, self).__init__(parent)

        self.s = QSettings('agrae','dbhost')
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://doc.qt.io/qt-5/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
    

    def closeEvent(self, event):
        self.closingPlugin2.emit()
        event.accept()


class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])



class parcelaFindDialog(QtWidgets.QDialog, agraeParcelaDialog):

    closingPlugin = pyqtSignal()
    actualizar = pyqtSignal(list)
    actualizarRel = pyqtSignal(str)
    

    def __init__(self, parent=None):
        """Constructor."""
        super(parcelaFindDialog, self).__init__(parent)

        self.utils = AgraeUtils()
        self.conn = self.utils.Conn()

        # TODO FILTER TABLE 

        
        
        data = self.dataAuto()
        lista = [e[0] for e in data]
        completer = QCompleter(lista)
        completer.setCaseSensitivity(False)

        # self.s = QSettings('agrae', 'dbhost')
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://doc.qt.io/qt-5/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.btn_buscar.clicked.connect(self.buscar)
        self.lineEdit.setCompleter(completer)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.pushButton.clicked.connect(self.cargarParcela)
        self.pushButton_2.clicked.connect(self.insertarIdRelacion)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    def data(self, filtro=None):
        if filtro == None:
            cursor = self.conn.cursor()
            sql = '''select p.idparcela,p.nombre, (case when lp.parcela = 1 then 'Si' else 'No' end) relacion, l.nombre lote_relacion,p.provincia, p.municipio , p.agregado , p.zona , p.poligono , p.parcela , p.recinto from parcela p left join (select lp.idparcela, count(*) as parcela from loteparcela as lp group by lp.idparcela) as lp  on lp.idparcela = p.idparcela left join loteparcela lp2 on lp2.idparcela  = p.idparcela left join lote l on lp2.idlote = l.idlote order by idparcela  '''
            cursor.execute(sql)
            data = cursor.fetchall()
        else:
            cursor = self.conn.cursor()
            sql = f"select p.idparcela,p.nombre, (case when lp.parcela = 1 then 'Si' else 'No' end) relacion, l.nombre lote_relacion,p.provincia, p.municipio , p.agregado , p.zona , p.poligono , p.parcela , p.recinto from parcela p left join (select lp.idparcela, count(*) as parcela from loteparcela as lp group by lp.idparcela) as lp  on lp.idparcela = p.idparcela left join loteparcela lp2 on lp2.idparcela  = p.idparcela left join lote l on lp2.idlote = l.idlote where p.nombre ilike '%{filtro}%' or p.provincia ilike '%{filtro}%' or  p.municipio ilike '%{filtro}%' or p.agregado ilike '%{filtro}%' or p.zona ilike '%{filtro}%' or p.poligono ilike '%{filtro}%' or p.parcela ilike '%{filtro}%' or p.recinto ilike '%{filtro}%' order by p.idparcela "
            cursor.execute(sql)
            data = cursor.fetchall()
        if len(data) >= 1:
            return data
        elif len(data) == 0:
            data = [0, 0]
            return data

    def dataAuto(self):
        cursor = self.conn.cursor()
        sql = "select distinct unnest(array[nombre, provincia, municipio, agregado, zona, poligono, parcela, recinto]) from parcela"


        cursor.execute(sql)
        data = cursor.fetchall()
        return data

    def populate(self,data):
        try:
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
                    
        except:
            QMessageBox.about(self, "Error:", "No Existen Registros")
            print('error')

    def loadData(self,param=None):
        
        
             
        if param == None:  
            data = self.data()
            # print(data[0][1])
            self.populate(data)
        else:
            data = self.data(param)
            # print(data[0][1])
            self.populate(data)
        pass
    
    def buscar(self):
        filtro = self.lineEdit.text()
        self.loadData(filtro)

        pass

    def cargarParcela(self):
        # value = self.tableWidget.item(0, 1).text()
        # print(str(value))
        try:
            row = self.tableWidget.currentRow()
            # column = self.tableWidget.currentColumn()
            param = self.tableWidget.item(row, 0).text()
            sqlQuery = f"""select * from parcela where idparcela = {param} """

            conn = self.conn
            cursor = conn.cursor()
            cursor.execute(sqlQuery)
            data = cursor.fetchone()
            dataLista = list(data)
            self.actualizar.emit(dataLista)
            self.close()
          
        except Exception as ex:
            QMessageBox.about(self,'aGrae GIS', 'Debe Seleccionar una parcela para agregar') 

        pass
    
    def insertarIdRelacion(self):
        try:
            row = self.tableWidget.currentRow()
            idRel = self.tableWidget.item(row, 0).text()
            self.actualizarRel.emit(idRel)
            self.close()
        except Exception as ex:
            QMessageBox.about(self,'aGrae GIS', 'Debe Seleccionar una parcela para agregar a la relacion')     
           
class loteFindDialog(QtWidgets.QDialog, agraeLoteDialog):

    closingPlugin = pyqtSignal()
    actualizar = pyqtSignal(list)
    actualizarRel = pyqtSignal(str)
    

    def __init__(self, parent=None):
        """Constructor."""
        super(loteFindDialog, self).__init__(parent)

        self.utils = AgraeUtils()
        self.conn = self.utils.Conn()
        
        data = self.data()
        lista = [e[1] for e in data]
        completer = QCompleter(lista)
        completer.setCaseSensitivity(False)

        # self.s = QSettings('agrae', 'dbhost')
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://doc.qt.io/qt-5/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.btn_buscar.clicked.connect(self.buscar)
        self.lineEdit.setCompleter(completer)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.btn_cargar_lote.clicked.connect(self.cargarLote)
        self.pushButton_2.clicked.connect(self.insertarIdRelacion)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    def data(self, filtro=None):
        if filtro == None:
            cursor = self.conn.cursor()
            sql = "select l.idlote ,l.nombre, coalesce(lp.parcelas,0) from lote l left join (select lp.idlote, count(*) as parcelas from loteparcela as lp group by lp.idlote) as lp on lp.idlote = l.idlote order by l.idlote"
            cursor.execute(sql)
            data = cursor.fetchall()
        else:
            cursor = self.conn.cursor()
            sql = f"select l.idlote ,l.nombre, coalesce(lp.parcelas,0) from lote l left join (select lp.idlote, count(*) as parcelas from loteparcela as lp group by lp.idlote) as lp on lp.idlote = l.idlote where l.nombre ilike '%{filtro}%' order by l.idlote "
            cursor.execute(sql)
            data = cursor.fetchall()
        if len(data) >= 1:
            return data
        elif len(data) == 0:
            data = [0, 0]
            return data

    def populate(self,data):
        try:
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
        except:
            QMessageBox.about(self, "Error:", "No Existen Registros")
            print('error')

    def loadData(self,param=None):
        
        
             
        if param == None:  
            data = self.data()
            # print(data[0][1])
            self.populate(data)
        else:
            data = self.data(param)
            # print(data[0][1])
            self.populate(data)
        pass
    
    def buscar(self):
        filtro = self.lineEdit.text()
        self.loadData(filtro)

        pass

    def cargarLote(self):
        # value = self.tableWidget.item(0, 1).text()
        # print(str(value))
        try:
            row = self.tableWidget.currentRow()
            # column = self.tableWidget.currentColumn()
            param = self.tableWidget.item(row, 0).text()
            sqlQuery = f"""select * from lote where idlote = {param} """

            conn = self.conn
            cursor = conn.cursor()
            cursor.execute(sqlQuery)
            data = cursor.fetchone()
            dataLista = list(data)
            self.actualizar.emit(dataLista)
            self.close()
            
        except:
            QMessageBox.about(self, 'aGrae GIS',
                              'Debe Seleccionar un lote de la Lista')
            pass
       
    def insertarIdRelacion(self):
        try:
            row = self.tableWidget.currentRow()
            column = self.tableWidget.currentColumn()
            idRel = self.tableWidget.item(row, 0).text()
            self.actualizarRel.emit(idRel)
            self.close()
        except Exception as ex:
            QMessageBox.about(self, 'aGrae GIS',
                              'Debe Seleccionar un lote de la Lista para agregar a la relacion')
                  
class expFindDialog(QtWidgets.QDialog, agraeExpDialog):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(expFindDialog, self).__init__(parent)

        self.utils = AgraeUtils()
        self.conn = self.utils.Conn()

        data = self.dataAuto()
        lista = [e[0] for e in data]
        # print(lista)
        completer = QCompleter(lista)
        completer.setCaseSensitivity(False)

        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://doc.qt.io/qt-5/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect

        self.setupUi(self)
        self.btn_buscar.clicked.connect(self.buscar)
        self.lineEdit.setCompleter(completer)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    def data(self, filtro=None):
        if filtro == None:
            cursor = self.conn.cursor()
            sql = "select idexplotacion,nombre, direccion from explotacion order by idexplotacion"
            cursor.execute(sql)
            data = cursor.fetchall()
        else:
            cursor = self.conn.cursor()
            sql = f"select idexplotacion,nombre, direccion from explotacion where nombre ilike '%{filtro}%' or direccion ilike '%{filtro}%' order by idexplotacion "
            cursor.execute(sql)
            data = cursor.fetchall()
        if len(data) >= 1:
            return data
        elif len(data) == 0:
            data = [0, 0]
            return data

    def dataAuto(self):
        cursor = self.conn.cursor()
        sql = "select nombre from explotacion union select direccion from explotacion"
        cursor.execute(sql)
        data = cursor.fetchall()
        return data


    def populate(self, data):
        try:
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
        except:
            QMessageBox.about(self, "Error:", "No Existen Registros")
            print('error')

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
        self.loadData(filtro)

        pass

class cultivoFindDialog(QtWidgets.QDialog, agraeCultivoDialog):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(cultivoFindDialog, self).__init__(parent)

        self.utils = AgraeUtils()
        self.conn = self.utils.Conn()

        data = self.dataAuto()
        lista = [e[0] for e in data]
        # print(lista)
        completer = QCompleter(lista)
        completer.setCaseSensitivity(False)

        self.setupUi(self)
        self.btn_buscar.clicked.connect(self.buscar)
        self.lineEdit.setCompleter(completer)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    def data(self, filtro=None):
        if filtro == None:
            cursor = self.conn.cursor()
            sql = "select idcultivo,nombre from cultivo order by idcultivo"
            cursor.execute(sql)
            data = cursor.fetchall()
        else:
            cursor = self.conn.cursor()
            sql = f"select idcultivo,nombre from cultivo where nombre ilike '%{filtro}%' order by idcultivo"
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
        except:
            QMessageBox.about(self, "Error:", "No Existen Registros")
            print('error')

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
        self.loadData(filtro)

        pass

class agraeMainWidget(QtWidgets.QMainWindow, agraeMainPanel):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(agraeMainWidget, self).__init__(parent)   

        self.utils = AgraeUtils()
        self.conn = self.utils.Conn()
        self.style = self.utils.styleSheet()

        data = self.dataAuto()
        lista = [e[0] for e in data]
        # print(lista)
        completer = QCompleter(lista)
        completer.setCaseSensitivity(False)

        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://doc.qt.io/qt-5/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        
        self.setupUi(self)

        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.setColumnHidden(5, True)
        self.btn_par_update.clicked.connect(self.actualizarParcela)
        self.btn_buscar_parcela.clicked.connect(self.parcelaDialog)
        self.btn_buscar_parcela_2.clicked.connect(self.parcelaDialog)
        self.btn_buscar_lote.clicked.connect(self.loteDialog)
        self.btn_buscar_lote_2.clicked.connect(self.loteDialog)
        self.btn_buscar_exp.clicked.connect(self.expDialog)
        self.btn_buscar_cult.clicked.connect(self.cultivoDialog)
        self.btn_rel_create.clicked.connect(self.crearRelacionLoteParcela)
        # self.btn_lote_update.clicked.connect(self.actualizarLote)
        
        self.setStyleSheet(self.style)
        self.line_buscar.setCompleter(completer)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    def dataAuto(self): 
        cursor = self.conn.cursor()
        sql = '''select distinct nombre from lote 
                union
                select distinct nombre from parcela
                union 
                select distinct nombre from cultivo
                order by nombre'''
        cursor.execute(sql)
        data = cursor.fetchall()
        return data

    def actualizarParcela(self):
        idParcela = self.lbl_id_parcela.text()
        name = self.ln_par_nombre.text()
        prov = self.ln_par_provincia.text()
        mcpo = self.ln_par_mcpo.text()
        aggregate = self.ln_par_agg.text()
        zone = self.ln_par_zona.text()
        poly = self.ln_par_poly.text()
        allotment = self.ln_par_parcela.text()
        inclosure = self.ln_par_recinto.text()

        confirm = QMessageBox.question(
               self, 'aGrae GIS', f"Seguro quiere Actualizar la parcela:\n--- ID: {idParcela}\n--- Nombre: {name.upper()}?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if confirm == QMessageBox.Yes:
            with self.conn as conn:
                try:
                    sql = f'''update parcela set nombre = '{name}', provincia = '{prov}', municipio = '{mcpo}', agregado = '{aggregate}', zona = '{zone}', poligono = '{poly}', parcela = '{allotment}', recinto = '{inclosure}' where idparcela = '{idParcela}' '''
                    cursor = conn.cursor()
                    cursor.execute(sql)
                    conn.commit()
                    QMessageBox.about(self, f"aGrae GIS:",
                                        f"Parcela *-- {name} --* Se modifico Correctamente.")
                    self.btn_par_update.setEnabled(False)

                except Exception as ex:
                    QMessageBox.about(self, f"Error:",
                                        f"{ex} \nHa ocurrido un Error por favor, verifique los datos o contacese con soporte tecnico")

        else:
            pass

            # print(name,prov,mcpo,aggregate,zone,poly,allotment,inclosure)

            pass
            
            #todo
    def actualizarLote(self):
        idlote = self.lbl_id_lote.text()
        nombre = self.line_lote_nombre.text()
        idexp = self.line_lote_idexp.text()
        idcult = self.line_lote_idcultivo.text()
        dateSiembra = self.lote_dateSiembra.date()
        dateCosecha = self.lote_dateCosecha.date()
        dateFondo = self.date_fondo.date()
        fondoFormula = self.line_fondo_formula.text()
        fondoPrecio = self.line_fondo_precio.text()
        fondoCalculado = self.line_fondo_calculado.text()
        fondoAjustado = self.line_fondo_ajustado.text()
        fondoAplicado = self.line_fondo_Aplicado.text()
        dateCob1 = self.date_cob.date()
        cob1Formula = self.line_cob_formula.text()
        cob1Precio = self.line_cob_precio.text()
        cob1Calculado = self.line_cob_calculado.text()
        cob1Ajustado = self.line_cob_ajustado.text()
        cob1Aplicado = self.line_cob_Aplicado.text()
        dateCob2 = self.date_cob_2.date()
        cob2Formula = self.line_cob_formula_2.text()
        cob2Precio = self.line_cob_precio_2.text()
        cob2Calculado = self.line_cob_calculado_2.text()
        cob2Ajustado = self.line_cob_ajustado_2.text()
        cob2Aplicado = self.line_cob_Aplicado_2.text()
        dateCob3 = self.date_cob_3.date()
        cob3Formula = self.line_cob_formula_3.text()
        cob3Precio = self.line_cob_precio_3.text()
        cob3Calculado = self.line_cob_calculado_3.text()
        cob3Ajustado = self.line_cob_ajustado_3.text()
        cob3Aplicado = self.line_cob_Aplicado_3.text()


        sql = self.utils.actualizarQueryLote(idlote,idcult,nombre,dateSiembra,dateCosecha,dateFondo,fondoFormula,fondoPrecio,fondoCalculado,fondoAjustado,fondoAplicado,dateCob1,cob1Formula,cob1Precio,cob1Calculado,cob1Ajustado,cob1Aplicado,dateCob2,cob2Formula,cob2Precio,cob2Calculado,cob2Ajustado,cob2Aplicado,dateCob2,cob2Formula,cob2Precio,cob2Calculado,cob2Ajustado,cob2Aplicado,dateCob3,cob3Formula,cob3Precio,cob3Calculado,cob3Ajustado,cob3Aplicado)

        print(sql)

        pass

    def populateParcela(self,data):
        dataStr = [str(e) for e in data]
        try:
            self.lbl_id_parcela.setText(dataStr[1])
            self.ln_par_nombre.setText(dataStr[2])
            self.ln_par_provincia.setText(dataStr[3])
            self.ln_par_mcpo.setText(dataStr[4])
            self.ln_par_agg.setText(dataStr[5])
            self.ln_par_zona.setText(dataStr[6])
            self.ln_par_poly.setText(dataStr[7])
            self.ln_par_parcela.setText(dataStr[8])
            self.ln_par_recinto.setText(dataStr[9])

            self.btn_par_update.setEnabled(True)
        except:
            pass
    def populateLote(self, data):
        # print(data)
        self.resetStyleLabels()
        data2 = []
        style = "font-weight: bold ; color : red"
        for e in data:
            if e == None:
                data2.append(e)
            else:
                data2.append(str(e))

        try:
            self.lbl_id_lote.setText(data2[0])
            self.line_lote_idexp.setText(data2[1])
            self.line_lote_idcultivo.setText(data2[2])
            self.line_lote_nombre.setText(data2[3])
            try:
                self.lote_dateSiembra.setDate(data[4])
            except:
                self.label_5.setStyleSheet(style)
                pass
            try:
                self.lote_dateCosecha.setDate(data[5])
            except:
                self.label_6.setStyleSheet(style)
                pass
            try:
                self.lote_dateFondo.setDate(data[6])
            except:
                self.label_13.setStyleSheet(style)
                pass
            self.line_fondo_formula.setText(data2[7])
            self.line_fondo_precio.setText(data2[8])
            self.line_fondo_calculado.setText(data2[9])
            self.line_fondo_ajustado.setText(data2[10])
            self.line_fondo_aplicado.setText(data2[11])
            try:
                self.date_cob.setDate(data[12])
            except:
                self.label_15.setStyleSheet(style)
                pass
            self.line_cob_formula.setText(data2[13])
            self.line_cob_precio.setText(data2[14])
            self.line_cob_calculado.setText(data2[15])
            self.line_cob_ajustado.setText(data2[16])
            self.line_cob_aplicado.setText(data2[17])
            try:
                self.date_cob_2.setDate(data[18])
            except:
                self.label_20.setStyleSheet(style)
                pass
            self.line_cob_formula_2.setText(data2[19])
            self.line_cob_precio_2.setText(data2[20])
            self.line_cob_calculado_2.setText(data2[21])
            self.line_cob_ajustado_2.setText(data2[22])
            self.line_cob_aplicado_2.setText(data2[23])
            try:
                self.date_cob_3.setDate(data[24])
            except:
                self.label_26.setStyleSheet(style)
                pass
            self.line_cob_formula_3.setText(data2[25])
            self.line_cob_precio_3.setText(data2[26])
            self.line_cob_calculado_3.setText(data2[27])
            self.line_cob_ajustado_3.setText(data2[28])
            self.line_cob_aplicado_3.setText(data2[29])
            self.btn_lote_update.setEnabled(True)

        except Exception as ex:
            print(ex)
            pass

    def populateRelPar(self,idPar):
        self.ln_rel_parcela.setText(idPar)
    def populateRelLote(self,idLote):
        self.ln_rel_lote.setText(idLote)
    
        
    def parcelaDialog(self):
        
        dialog = parcelaFindDialog()
        dialog.loadData()
        dialog.actualizar.connect(self.populateParcela)
        dialog.actualizarRel.connect(self.populateRelPar)
        dialog.exec_()
    
    def loteDialog(self):
        
        dialog = loteFindDialog()
        dialog.loadData()
        dialog.actualizar.connect(self.populateLote)
        dialog.actualizarRel.connect(self.populateRelLote)
        dialog.exec_()
    
    def expDialog(self):

        dialog = expFindDialog()
        dialog.loadData()
        dialog.exec_()
    def cultivoDialog(self):

        dialog = cultivoFindDialog()
        dialog.loadData()
        dialog.exec_()

    def crearRelacionLoteParcela(self):
        idParcela = int(self.ln_rel_parcela.text())
        idLote = int(self.ln_rel_lote.text())
        
        sql = f''' insert into loteparcela(idparcela,idlote) 
                values({idParcela},{idLote}) '''
        cursor = self.conn.cursor()
        cursor.execute(sql)
        QMessageBox.about(self, 'aGrae GIS','Se creo la Relacion')
        self.conn.commit()            
        
            # QMessageBox.about(self, 'aGrae GIS',
            #                   'No se pudo crear la Relacion')

    
    def resetStyleLabels(self):
        style = 'font-weight: normal ; color : black'
        self.label_5.setStyleSheet(style)
        self.label_6.setStyleSheet(style)
        self.label_13.setStyleSheet(style)
        self.label_15.setStyleSheet(style)
        self.label_20.setStyleSheet(style)
        self.label_26.setStyleSheet(style)




