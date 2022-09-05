import os
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QIcon
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import * 
from qgis.core import * 
from qgis.utils import iface
from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal
from psycopg2 import errors
from .processing import *



from .utils import AgraeUtils, AgraeToolset

agraeExpDialog, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui/dialogs/exp_dialog.ui'))
_agraeSegmentoDialog, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui/dialogs/parcela_dialog.ui'))
_agraeParametrosDialog, _ =  uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui/dialogs/params_dialog.ui'))
agraeCultivoDialog, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui/dialogs/cultivo_dialog.ui'))
agraePersonaDialog, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui/dialogs/personas_dialog.ui'))
agraeAgricultorDialog, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui/dialogs/agricultor_dialog.ui'))
agraeCeapDialog, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui/dialogs/ceap_dialog.ui'))


class expFindDialog(QtWidgets.QDialog, agraeExpDialog):
    closingPlugin = pyqtSignal()
    getIdExp = pyqtSignal(int)
    expName = pyqtSignal(str)

    def __init__(self, parent=None):
        """Constructor."""
        super(expFindDialog, self).__init__(parent)
        self.utils = AgraeUtils()
        self.conn = self.utils.Conn()

        # print(lista)

        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://doc.qt.io/qt-5/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.UIcomponents()

    def selectIdExp(self,r=None):
        # if r != None: 
        #     row = r.row()

        row = self.tableWidget.currentRow()
        
        idExp = int(self.tableWidget.item(row, 0).text())
        _expName = str(self.tableWidget.item(row,1).text())

        self.getIdExp.emit(idExp)
        self.expName.emit(_expName)
        self.close()

    def UIcomponents(self):

        data = self.dataAuto()
        lista = [e[0] for e in data]
        completer = QCompleter(lista)
        completer.setCaseSensitivity(False)

        icons_path = self.utils.iconsPath()
        self.setWindowTitle('Administracón y Busqueda de Explotaciones')

        self.lineEdit.setClearButtonEnabled(True)
        line_buscar_action = self.lineEdit.addAction(
            QIcon(icons_path['search_icon_path']), self.lineEdit.TrailingPosition)
        line_buscar_action.triggered.connect(self.buscar)

        self.tableWidget.setColumnHidden(0, True)
        # self.tableWidget.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.tableWidget.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.tableWidget.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.tableWidget.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)

        self.pushButton.clicked.connect(self.selectIdExp)
        self.pushButton.setIconSize(QtCore.QSize(20, 20))
        self.pushButton.setIcon(QIcon(icons_path['share']))

        self.tabWidget.setCurrentIndex(0)
        self.tabWidget.setTabIcon(0, QIcon(icons_path['search_icon_path']))
        self.tabWidget.setTabIcon(1, QIcon(icons_path['pen-to-square']))

        

        #* ACTIONS
        self.pushButton_2.clicked.connect(self.crear)

        self.lineEdit.setCompleter(completer)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)

        self.tableWidget.doubleClicked.connect(self.selectIdExp)

        

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    def data(self, filtro=None):
        if filtro == None:
            cursor = self.conn.cursor()
            sql = '''select e.idexplotacion, e.nombre, e.direccion, count(a.idagricultor) agricultores from explotacion e
            left join agricultor a on a.idexplotacion = e.idexplotacion
            group by e.idexplotacion, e.nombre, e.direccion
            order by e.idexplotacion '''
            cursor.execute(sql)
            data = cursor.fetchall()
        else:
            cursor = self.conn.cursor()
            sql = f'''select e.idexplotacion,e.nombre,e.direccion , count(a.idagricultor) agricultores from explotacion e 
            left join agricultor a on a.idexplotacion = e.idexplotacion 
            group by e.idexplotacion,e.nombre,e.direccion 
            where nombre ilike '%{filtro}%' or direccion ilike '%{filtro}%' order by e.idexplotacion '''
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
        self.loadData(filtro)
        pass

    def crear(self):
        cursor = self.conn.cursor()
        nombre = self.lineEdit_2.text()
        direccion = self.lineEdit_3.text()
        if nombre != '' and direccion != '':
            try:
                sql = f''' insert into explotacion(nombre,direccion)
                values('{nombre}','{direccion}') '''
                cursor.execute(sql)
                self.conn.commit()
                QMessageBox.about(self, "aGrae GIS:", "Se creo correctamente")
            except Exception as ex:
                print(ex)
                QMessageBox.about(self, "Error:", "Error revisa la consola")
                self.conn.rollback()
        else:
            QMessageBox.about(
                self, "Error:", "Debes rellenar todos los campos")



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
        self.setWindowIcon(QIcon(icons_path['cultivo-icon']))
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
        self.lineEdit.textChanged.connect(self.buscar)
        self.tableWidget.setColumnHidden(0, True)
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

class agraeSegmentoDialog(QtWidgets.QDialog, _agraeSegmentoDialog):

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
        

class agraeParametrosDialog(QtWidgets.QDialog, _agraeParametrosDialog): 
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
        self.tableWidget_10.setColumnHidden(0, True) 
        self.tableWidget_11.setColumnHidden(0, True) 
        self.tableWidget_12.setColumnHidden(0, True) 

        self.setButtonActions(self.an_edit_textura_btn, self.an_save_textura_btn, self.an_add_textura, self.an_remove_textura, self.tableWidget_1, 0)
        self.setButtonActions(self.an_edit_ph, self.an_save_ph, self.an_add_ph, self.an_remove_ph, self.tableWidget_2, 1,2,3)
        self.setButtonActions(self.an_edit_ce, self.an_save_ce, self.an_add_ce, self.an_remove_ce, self.tableWidget_3, 2,2,3)
        self.setButtonActions(self.an_edit_carbon, self.an_save_carbon, self.an_add_carbon, self.an_remove_carbon, self.tableWidget_4, 3,2,3)
        self.setButtonActions(self.an_edit_ca, self.an_save_ca, self.an_add_ca, self.an_remove_ca, self.tableWidget_5, 4,2,3)
        self.setButtonActions(self.an_edit_cic, self.an_save_cic, self.an_add_cic, self.an_remove_cic, self.tableWidget_6, 5,2,3)
        self.setButtonActions(self.an_edit_calcio, self.an_save_calcio, self.an_add_calcio, self.an_remove_calcio, self.tableWidget_7,6,4,5)
        self.setButtonActions(self.an_edit_magnesio, self.an_save_magnesio, self.an_add_magnesio, self.an_remove_magnesio, self.tableWidget_8,7,4,5)
        
        
        self.setButtonActions(self.an_edit_potasio, self.an_save_potasio, self.an_add_potasio, self.an_remove_potasio, self.tableWidget_9,8,7,8)
       
       
        self.setButtonActions(self.an_edit_sodio, self.an_save_sodio, self.an_add_sodio, self.an_remove_sodio, self.tableWidget_10,9,3,4)
        self.setButtonActions(self.an_edit_nitrogeno, self.an_save_nitrogeno, self.an_add_nitrogeno, self.an_remove_nitrogeno, self.tableWidget_11,10,2,3)
        self.setButtonActions(self.an_edit_fosforo, self.an_save_fosforo, self.an_add_fosforo, self.an_remove_fosforo, self.tableWidget_12,11,5,6)

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


        self.tableWidget_9.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.tableWidget_9.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.tableWidget_9.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        self.tableWidget_9.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        self.tableWidget_9.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.Stretch)
        self.tableWidget_9.horizontalHeader().setSectionResizeMode(6, QtWidgets.QHeaderView.Stretch)
        self.tableWidget_9.horizontalHeader().setSectionResizeMode(7, QtWidgets.QHeaderView.Stretch)
        self.tableWidget_9.horizontalHeader().setSectionResizeMode(8, QtWidgets.QHeaderView.Stretch)
        self.tableWidget_9.horizontalHeader().setSectionResizeMode(9, QtWidgets.QHeaderView.Stretch)
        
        self.tableWidget_10.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.tableWidget_10.horizontalHeader().setSectionResizeMode(
            2, QtWidgets.QHeaderView.Stretch)
        self.tableWidget_10.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        self.tableWidget_10.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        self.tableWidget_10.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        


        
        self.arenoso_radio.clicked.connect(lambda: self.check_suelo(6,1))
        self.franco_radio.clicked.connect(lambda: self.check_suelo(6,2))
        self.arcilloso_radio.clicked.connect(lambda: self.check_suelo(6,3))
        
        self.arenoso_radio_2.clicked.connect(lambda: self.check_suelo(7,1))
        self.franco_radio_2.clicked.connect(lambda: self.check_suelo(7,2))
        self.arcilloso_radio_2.clicked.connect(lambda: self.check_suelo(7,3))

        self.arenoso_radio_3.clicked.connect(lambda: self.check_suelo(8,1,r1=self.regadio_radio,r2=self.semi_radio,r3=self.secano_radio,regimen=True))
        self.franco_radio_3.clicked.connect(lambda: self.check_suelo(8,2,r1=self.regadio_radio,r2=self.semi_radio,r3=self.secano_radio,regimen=True))
        self.arcilloso_radio_3.clicked.connect(lambda: self.check_suelo(8, 3, r1=self.regadio_radio, r2=self.semi_radio, r3=self.secano_radio, regimen=True))        
        self.regadio_radio.clicked.connect(lambda: self.check_regimen(8,1,s1=self.arenoso_radio_3,s2=self.franco_radio_3,s3=self.arcilloso_radio_3))
        self.semi_radio.clicked.connect(lambda: self.check_regimen(8,2,s1=self.arenoso_radio_3,s2=self.franco_radio_3,s3=self.arcilloso_radio_3))
        self.secano_radio.clicked.connect(lambda: self.check_regimen(8,3,s1=self.arenoso_radio_3,s2=self.franco_radio_3,s3=self.arcilloso_radio_3))

        self.arenoso_radio_4.clicked.connect(lambda: self.check_suelo(9, 1))
        self.franco_radio_4.clicked.connect(lambda: self.check_suelo(9, 2))
        self.arcilloso_radio_4.clicked.connect(lambda: self.check_suelo(9, 3))


        self.metodo1_radio.clicked.connect(lambda: self.check_metodo(11,1,r1=self.regadio_radio_2,r2=self.semi_radio_2,r3=self.secano_radio_2,s1=self.arenoso_radio_5,s2=self.franco_radio_5,s3=self.arcilloso_radio_5))
        self.metodo2_radio.clicked.connect(lambda: self.check_metodo(11,2,r1=self.regadio_radio_2,r2=self.semi_radio_2,r3=self.secano_radio_2,s1=self.arenoso_radio_5,s2=self.franco_radio_5,s3=self.arcilloso_radio_5))




        self.regadio_radio_2.clicked.connect(lambda: self.check_regimen(8,1,s1=self.arenoso_radio_5,s2=self.franco_radio_5,s3=self.arcilloso_radio_5,metodo=True))
        self.semi_radio_2.clicked.connect(lambda: self.check_regimen(8,2,s1=self.arenoso_radio_5,s2=self.franco_radio_5,s3=self.arcilloso_radio_5,metodo=True))
        self.secano_radio_2.clicked.connect(lambda: self.check_regimen(
            8, 3, s1=self.arenoso_radio_5, s2=self.franco_radio_5, s3=self.arcilloso_radio_5, metodo=True))
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
                self, 'aGrae GIS', f"Seguro quiere Actualizar Los valores de Calcio?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
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
                        'Parametros de Calcio Actualizados Correctamente', 3, 5)

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
                        suelo = self.tableWidget_9.item(r, 3).text()
                        nivel = self.tableWidget_9.item(r, 5).text()
                        tipo = self.tableWidget_9.item(r, 6).text()
                        li = self.tableWidget_9.item(r, 7).text()
                        ls = self.tableWidget_9.item(r, 8).text()
                        incremento = self.tableWidget_9.item(r, 9).text()
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
                                suelo = self.tableWidget_9.item(r, 3).text()
                                nivel = self.tableWidget_9.item(r, 5).text()
                                tipo = self.tableWidget_9.item(r, 6).text()
                                li = self.tableWidget_9.item(r, 7).text()
                                ls = self.tableWidget_9.item(r, 8).text()
                                incremento = self.tableWidget_9.item(r, 9).text()
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
    
        elif i == 11:
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
                            if self.tableWidget_11.item(r, 1) != None:
                                tipo = self.tableWidget_11.item(r, 1).text()
                                li = self.tableWidget_11.item(r, 2).text()
                                ls = self.tableWidget_11.item(r, 3).text()
                                incremento = self.tableWidget_11.item(
                                    r, 4).text()
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

            
    def loadData(self,i,suelo=1,regimen=1,metodo=1):
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
            sql = 'select distinct ca.id,ca.suelo, t.grupo_label tipo_suelo,ca.tipo ,ca.limite_inferior , ca.limite_superior , ca.incremento from analisis.calcio ca left join analisis.textura t on t.grupo = ca.suelo where ca.suelo = {} order by ca.suelo, ca.limite_inferior  '.format(suelo)
            self.tools.populateTable(sql, self.tableWidget_7)
                
            
        elif i == 7:
            # print(i)           
            sql = 'select distinct m.id,m.suelo, t.grupo_label tipo_suelo,m.tipo ,m.limite_inferior , m.limite_superior , m.incremento from analisis.magnesio m left join analisis.textura t on t.grupo = m.suelo where m.suelo = {} order by m.suelo, m.limite_inferior '.format(suelo)
            self.tools.populateTable(sql,self.tableWidget_8)

        elif i == 8:
            # print(i)            
            sql = 'select distinct k.id,k.regimen,r.nombre, k.suelo,t.grupo_label tipo_suelo, k.nivel,k.tipo, k.limite_inferior, k.limite_superior,k.incremento from analisis.potasio k left join analisis.textura t on t.grupo = k.suelo left join analisis.regimen r on r.id  = k.regimen  where k.suelo = {} and k.regimen = {} order by k.regimen, k.suelo, k.limite_inferior'.format(suelo,regimen)
            self.tools.populateTable(sql,self.tableWidget_9)
        elif i == 9:
            # print(i)        
            sql = 'select * from analisis.sodio where suelo = {} order by id'.format(suelo)
            self.tools.populateTable(sql,self.tableWidget_10)
        elif i == 10:
            # print(i)
            sql = 'select * from analisis.nitrogeno order by id'
            self.tools.populateTable(sql,self.tableWidget_11)
        elif i == 11:
            if metodo == 1:
                sql = 'select id,metodo,regimen,suelo,tipo,limite_inferior ,limite_inferior ,incremento from analisis.fosforo f where metodo = {} and regimen = {} and suelo = {} order by metodo, regimen, suelo, limite_inferior'.format(metodo,regimen,suelo)
                self.tools.populateTable(sql,self.tableWidget_12)
            # print(i)
            if metodo == 2:             
                try: 
                    sql = 'select id,metodo,regimen,suelo,tipo,limite_inferior ,limite_inferior ,incremento from analisis.fosforo f where metodo = {} and regimen = {} order by metodo, regimen, suelo, limite_inferior'.format(metodo,regimen)
                    self.tools.populateTable(sql,self.tableWidget_12)
                except: 
                    pass

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

    def check_suelo(self,i,s,r1=None,r2=None,r3=None,regimen=False,metodo=False):
        if regimen:
             if r1.isChecked(): 
                 self.loadData(i, suelo=s,regimen=1)
             if r2.isChecked(): 
                 self.loadData(i, suelo=s,regimen=2)
             if r3.isChecked(): 
                 self.loadData(i, suelo=s,regimen=3)

        elif regimen and metodo: 
            if r1.isChecked() and self.metodo1_radio.isChecked():
                 self.loadData(i, suelo=s, regimen=1, metodo = 1)
            if r2.isChecked() and self.metodo1_radio.isChecked():
                self.loadData(i, suelo=s, regimen=2, metodo = 1)
            if r3.isChecked() and self.metodo1_radio.isChecked():
                self.loadData(i, suelo=s, regimen=3, metodo=1)
            
            if r1.isChecked() and self.metodo2_radio.isChecked():
                self.loadData(i, suelo=s, regimen=1, metodo=2)
            if r2.isChecked() and self.metodo2_radio.isChecked():
                self.loadData(i, suelo=s, regimen=2, metodo=2)
            if r3.isChecked() and self.metodo2_radio.isChecked():
                self.loadData(i, suelo=s, regimen=3, metodo=2)
        else:
            self.loadData(i,suelo = s)
            pass
    def check_regimen(self,i,r,s1,s2,s3,metodo=False):
        if metodo==True: 

            if s1.isChecked() and self.metodo1_radio.isChecked(): 
                self.loadData(i,suelo=1,regimen=r,metodo=1)
            if s2.isChecked() and self.metodo1_radio.isChecked():            
                self.loadData(i,suelo=2,regimen=r,metodo=1)
            if s3.isChecked() and self.metodo1_radio.isChecked():
                self.loadData(i, suelo=3, regimen=r, metodo=1)
            if s1.isChecked() and self.metodo2_radio.isChecked():
                self.loadData(i, suelo=1, regimen=r, metodo=2)
            if s2.isChecked() and self.metodo2_radio.isChecked():
                self.loadData(i, suelo=2, regimen=r, metodo=2)
            if s3.isChecked() and self.metodo2_radio.isChecked():
                self.loadData(i, suelo=3, regimen=r, metodo=2)
            pass
        else:
            if s1.isChecked(): 
                self.loadData(i,suelo=1,regimen=r)
            if s2.isChecked():            
                self.loadData(i,suelo=2,regimen=r)
            if s3.isChecked():
                self.loadData(i,suelo=3,regimen=r)
        pass

    def check_metodo(self,i,m,r1,r2,r3,s1,s2,s3): 
        if s1.isChecked() and r1.isChecked(): 
            self.loadData(i,suelo=1,regimen=1,metodo=m)
            pass
        elif s1.isChecked() and r2.isChecked():
            self.loadData(i,suelo=1,regimen=2,metodo=m) 
            pass
        elif s1.isChecked() and r3.isChecked():
            self.loadData(i,suelo=1,regimen=3,metodo=m) 
            pass
        elif s2.isChecked() and r1.isChecked():
            self.loadData(i,suelo=2,regimen=1,metodo=m) 
            pass
        elif s2.isChecked() and r2.isChecked():
            self.loadData(i,suelo=2,regimen=2,metodo=m) 
            pass
        elif s2.isChecked() and r3.isChecked():
            self.loadData(i,suelo=2,regimen=3,metodo=m) 
            pass
        elif s3.isChecked() and r1.isChecked():
            self.loadData(i,suelo=3,regimen=1,metodo=m) 
            pass
        elif s3.isChecked() and r2.isChecked():
            self.loadData(i,suelo=3,regimen=2,metodo=m) 
            pass
        elif s3.isChecked() and r3.isChecked():
            self.loadData(i,suelo=3,regimen=3,metodo=m) 
            pass

class personaDialog(QtWidgets.QDialog,agraePersonaDialog): 
    closingPlugin = pyqtSignal()
    dniSignal = pyqtSignal(str)
    def __init__(self,parent=None):
        super(personaDialog, self).__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__),'ui/dialogs/personas_dialog.ui'),self)
        self.tools = AgraeToolset()
        self.utils = AgraeUtils()
        self.conn = self.utils.Conn()
        self.buscarPersona()

        self.UIComponents()

    
    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    def doubleClick(self,e): 
        row = e.row() 
        dni = str(self.tableWidget.item(row,1).text())
        # print(dni)
        self.dniSignal.emit(dni)

        self.close()

    def UIComponents(self):
        #* UI 
        icons_path = self.utils.iconsPath()
        self.setWindowIcon(QIcon(icons_path['users']))
        self.tabWidget.setCurrentIndex(0)
        self.pushButton.setIconSize(QtCore.QSize(20, 20))
        self.pushButton.setIcon(QIcon(icons_path['share']))
        self.pushButton_2.setIconSize(QtCore.QSize(20, 20))
        self.pushButton_2.setIcon(QIcon(icons_path['user-check']))
        self.tabWidget.setTabIcon(0, QIcon(icons_path['search_icon_path']))
        self.tabWidget.setTabIcon(1, QIcon(icons_path['pen-to-square']))




        # self.date_cultivo.setDate(QDate.currentDate())
        #* ACTIONS
        line_buscar_action = self.lineEdit.addAction(
            QIcon(icons_path['search_icon_path']), self.lineEdit.TrailingPosition)
        line_buscar_action.triggered.connect(self.buscar)
        self.lineEdit.textChanged.connect(self.buscarPersona)

        self.pushButton_2.clicked.connect(self.crearPersona)


        #* SIGNALS
        self.tableWidget.doubleClicked.connect(self.doubleClick)
    
    def buscar(self):
        filtro = self.lineEdit.text()
        # print(filtro)
        self.buscarPersona(filtro)
    def buscarPersona(self,param:str=None): 
        if param == None or len(self.lineEdit.text()) == 0:
            sql = ''' select * from persona p   '''
            try:
                self.tools.populateTable(sql, self.tableWidget)
            except IndexError as ie:
                pass
            except Exception as ex:
                print(ex)
        else:
            sql = ''' select * from persona p where p.dni = '{}' or p.nombre ilike '%{}%' or p.direccion ilike '%{}%' '''.format(param, param, param)
            try:
                # print(param)
                self.tools.populateTable(sql, self.tableWidget)
            except IndexError as ie:
                pass
            except Exception as ex:
                print(ex)

    def crearPersona(self): 
        with self.conn.cursor() as cursor: 
            try: 
                DNI = self.ln_dni.text()
                NOMBRE = self.ln_nombre.text()
                APELLIDO = self.ln_apellido.text()
                DIRECCION = self.ln_direccion.text()
                TELEFONO = self.ln_telefono.text()
                EMAIL = self.ln_email.text()
                sql = ''' insert into persona(dni,nombre,apellidos,direccion,telefono,email) 
                values('{}','{}','{}','{}','{}','{}') '''.format(DNI.upper(),NOMBRE.upper(),APELLIDO.upper(),DIRECCION.upper(),TELEFONO.upper(),EMAIL)
                
                cursor.execute(sql)
                self.conn.commit()
                QMessageBox.about(self, "", "Datos Guardados Correctamente")
                # print(sql)
                self.buscarPersona()
                self.tabWidget.setCurrentIndex(0)
                self.ln_dni.clear()
                self.ln_nombre.clear()
                self.ln_apellido.clear()
                self.ln_direccion.clear()
                self.ln_telefono.clear()
                self.ln_email.clear()
                

            except Exception as ex: 
                print(ex)
    
class agricultorDialog(QtWidgets.QDialog,agraeAgricultorDialog): 
    closingPlugin = pyqtSignal()
    def __init__(self,parent=None): 
        super(agricultorDialog,self).__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__),'ui/dialogs/agricultor_dialog.ui'),self)
        self.tools = AgraeToolset()
        self.utils = AgraeUtils()
        self.conn = self.utils.Conn()
        self.buscarAgricultor()
        self.UIComponents()
    
    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
    
    def UIComponents(self): 
        icons_path = self.utils.iconsPath()
        self.setWindowIcon(QIcon(icons_path['farmer-color']))
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget.setTabEnabled(2,False)
        self.date_cultivo.setDate(QDate.currentDate())
        line_buscar_action = self.lineEdit.addAction(
            QIcon(icons_path['search_icon_path']), self.lineEdit.TrailingPosition)
        line_buscar_action.triggered.connect(self.buscar)

        self.lineEdit.textChanged.connect(self.buscarAgricultor)
        line_dni_action = self.ln_dni.addAction(QIcon(icons_path['search_icon_path']), self.ln_dni.TrailingPosition)
        line_dni_action.triggered.connect(self.personasDialog)
        line_exp_action = self.ln_exp.addAction(QIcon(icons_path['search_icon_path']), self.ln_exp.TrailingPosition)
        line_exp_action.triggered.connect(self.expDialog)
        line_cultivo_action = self.ln_cultivo.addAction(QIcon(icons_path['search_icon_path']), self.ln_cultivo.TrailingPosition)
        line_cultivo_action.triggered.connect(self.cultivoDialog)

        self.pushButton_3.setIconSize(QtCore.QSize(20, 20))
        self.pushButton_3.setIcon(QIcon(icons_path['user-check']))
        self.pushButton_3.clicked.connect(self.saveAgricultor)
        self.pushButton_4.setIconSize(QtCore.QSize(20, 20))
        self.pushButton_4.setIcon(QIcon(icons_path['user-check']))
        self.pushButton_4.clicked.connect(self.saveCultivoAgricultor)
        self.tableWidget.doubleClicked.connect(self.select)
        self.tabWidget.setTabIcon(0, QIcon(icons_path['search_icon_path']))
        self.tabWidget.setTabIcon(1, QIcon(icons_path['pen-to-square']))
        self.tabWidget.setTabIcon(2, QIcon(icons_path['farmer']))
        pass
    #! METODOS DE AGRICULTOR
    #* DIALOGS
    def personasDialog(self):
        dialog = personaDialog()
        dialog.setModal(True)
        dialog.dniSignal.connect(self.popDni)
        dialog.exec()

    def expDialog(self): 
        dialog = expFindDialog()
        dialog.setModal(True)
        dialog.loadData()
        dialog.getIdExp.connect(self.popExp)
        dialog.expName.connect(self.nameExp)
        dialog.exec_()
    
    def cultivoDialog(self):
        dialog = cultivoFindDialog()
        dialog.setModal(True)
        dialog.loadData()
        dialog.getIdCultivo.connect(self.popIdCultivo)
        dialog.exec()
    
    #* METODOS
    def buscarAgricultor(self,param:str=None): 
        if param == None or len(self.lineEdit.text()) == 0: 
            sql = ''' select a.idagricultor ,p.dni, a.nombre, e.nombre explotacion from agricultor a 
            join explotacion e on a.idexplotacion = e.idexplotacion 
            join persona p on p.idpersona = a.idpersona    '''
            try:
                self.tools.populateTable(sql, self.tableWidget)
            except IndexError as ie: 
                pass
            except Exception as ex:
                print(ex)
        else: 
            sql = ''' select a.idagricultor ,p.dni, a.nombre, e.nombre explotacion from agricultor a 
            join explotacion e on a.idexplotacion = e.idexplotacion 
            join persona p on p.idpersona = a.idpersona  
            where p.dni = '{}' or a.nombre ilike '%{}%' or e.nombre ilike '%{}%' '''.format(param,param,param)
            try: 
                # print(param)
                self.tools.populateTable(sql, self.tableWidget)
            except IndexError as ie: 
                pass
            except Exception as ex: 
                print(ex)


    def buscar(self):
        filtro = self.lineEdit.text()
        print(filtro)
        self.buscarAgricultor(filtro)
    def popDni(self,dni:str):
        # print(dni)
        self.ln_dni.setText(dni)
    def popExp(self,exp):
        id = str(exp)
        self.ln_exp.setText(id)
    def nameExp(self,name:str):
        self.label_7.setText(name)

    def popIdCultivo(self,id):
        self.ln_cultivo.setText(str(id))

    def select(self,e):
        row = e.row()
        id = self.tableWidget.item(row,0).text()
        # dni = self.tableWidget.item(row,1).text()
        dni = self.tableWidget.item(row,1).text()
        nombre = self.tableWidget.item(row,2).text()
        
        self.ln_idagricultor.setText(id)
        self.label_4.setText('{}- DNI: {}'.format(nombre,dni))
        self.tabWidget.setTabEnabled(2,True)
        self.tabWidget.setCurrentIndex(2)

    def saveAgricultor(self):
        idExplotacion = self.ln_exp.text()
        dni = self.ln_dni.text()
        with self.conn.cursor() as cursor: 
            try: 
                sql = ''' insert into agricultor(idpersona,idexplotacion,nombre)
                    select p.idpersona, {}, p.nombre ||' '|| p.apellidos 
                    from persona p
                    where p.dni = '{}' '''.format(idExplotacion,dni) 
                cursor.execute(sql)
                self.conn.commit()
                QMessageBox.about(self, "", "Datos Guardados Correctamente")
                self.ln_exp.clear()
                self.ln_dni.clear()
                self.label_7.clear()
            except errors.lookup('23505'):
                QMessageBox.about(self, "", "El Agricultor ya existe en la explotacion seleccionada")
                self.conn.rollback()
            except Exception as ex: 
                print(ex)
                QMessageBox.about(self, "", "Ocurrio un error")
                self.conn.rollback()

        pass
    
    def saveCultivoAgricultor(self): 
        idAgricultor = self.ln_idagricultor.text() 
        idCultivo = self.ln_cultivo.text() 
        fechaCultivo = self.date_cultivo.date().toString('yyyy.MM.dd')
        undNPKTradicionales = self.ln_npk.text()
        costeFertilizante = self.ln_coste.text() 
        costeNPK = self.ln_costenpk.text()

        with self.conn.cursor() as cursor: 
            try: 
                sql = ''' insert into cultivoagricultor(idagricultor,idcultivo,unidadesnpktradicionales,costefertilizante,costefertilizanteunidades,fechacultivo)
                values({},{},'{}', {},'{}','{}') '''.format(idAgricultor, idCultivo, undNPKTradicionales, costeFertilizante, costeNPK, fechaCultivo)
                cursor.execute(sql)
                self.conn.commit() 
                QMessageBox.about(self, "", "Datos Guardados Correctamente")
                self.ln_idagricultor.clear() 
                self.ln_cultivo.clear() 
                self.ln_npk.clear()
                self.ln_coste.clear() 
                self.ln_costenpk.clear()
                self.date_cultivo.setDate(QDate.currentDate())
                self.tabWidget.setCurrentIndex(0)
                self.tabWidget.setTabEnabled(2,False)
            except Exception as ex:
                print(ex)
                self.conn.rollback()
                QMessageBox.about(self, "", "Ocurrio un Error")

class ceapPrevDialog(QtWidgets.QDialog, agraeCeapDialog): 
    closingPlugin = pyqtSignal()
    def __init__(self, parent=None):
        super(ceapPrevDialog, self).__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__),'ui/dialogs/ceap_dialog.ui'),self)
        self.tools = AgraeToolset()
        self.utils = AgraeUtils()
        
        self.conn = self.utils.Conn() 
        
        self.UIComponents()

    def closeEvent(self, event):
        self.closingPlugin.emit()
        self.progressBar.setValue(0)
        event.accept()

    def UIComponents(self):
        icons_path = self.utils.iconsPath()
        self.setWindowIcon(QIcon(icons_path['ceap']))
        
        self.pushButton.clicked.connect(self.openFileDialog)
        self.pushButton_2.clicked.connect(self.saveFileDialog)
        
        self.pushButton_3.clicked.connect(self.saveInDataBase)

        self.btn_run.clicked.connect(self.run)
    
    def run(self):
        # print(self.ln_input.text())
        try: 
            inp = os.path.normpath(self.ln_input.text())
            out = os.path.normpath(self.ln_output.text())
            n_class = self.spinBox.value()
            if len(inp) > 3:
                if len(out) > 3:
                    alg = agraeVerisAlgorithm(inp, self.progressBar, segmento=out)
                else: 
                    alg = agraeVerisAlgorithm(inp, self.progressBar)
                alg.processVerisData(n_class)
            else: 
                pass
        except Exception as ex: 
            print(ex)

        finally: 
            self.progressBar.setValue(100)
            self.pushButton_3.setEnabled(True)
            # lyr = QgsProject.instance().mapLayersByName('Veris DAT')[0]
            # iface.layerTreeView().refreshLayerSymbology(lyr.id())
    

    def saveInDataBase(self): 
        lyr = iface.activeLayer() 
        srid = lyr.crs().authid()[5:]
        for f in lyr.getFeatures(): 
            s = f[0]
            ceap = f[1]
            geom = f.geometry().asWkt()
            try: 
                with self.conn:
                    if 'Segmentos' in lyr.name(): 
                        cursor = self.conn.cursor() 
                        sql = f''' insert into segmentocampo(segmento,ceap,geometria)
                                                values
                                                ({s},{ceap},
                                                st_multi(st_force2d(st_transform(st_geomfromtext('{geom}',{srid}),4326)))) '''
                                                
                        cursor.execute(sql)
                        self.conn.commit() 
                        iface.messageBar().pushMessage(
                            'aGraes GIS', 'Segmentos guardados Correctamente', level=3, duration=3)
                    else: 
                        iface.messageBar().pushMessage(
                            'Error', 'Capa invalida', level=2, duration=3)
            except Exception as ex: 
                print(ex)
                self.conn.rollback()
                                            
            
            

    def openFileDialog(self):
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(
            self, "aGrae GIS", "", "Todos los archivos (*);;Archivos separados por coma (*.csv);;Archivos DAT(*.dat)", options=options)
        if fileName:
            self.ln_input.setText(fileName)
            # return fileName
        else:
            return False
    
    def saveFileDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(
            None, "aGrae GIS", "", "Archivos Shapefile (*.shp)", options=options)
        if fileName:
            self.ln_output.setText(fileName)
            # return fileName
        else:
            return False


    

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


