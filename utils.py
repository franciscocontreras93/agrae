import os, sys, re
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QRegExp, QDate, Qt, QObject, QThread, QAbstractTableModel
from PyQt5.QtGui import QGuiApplication
from qgis.PyQt.QtCore import QSettings
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

from qgis.gui import QgsMessageBar
from qgis.utils import iface
from qgis.core import *

from psycopg2 import OperationalError, InterfaceError, errors, extras,connect

import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

from .dbconn import DbConnection

class AgraeUtils():
    
    def __init__(self):
        self.iface = iface
        self.s = QSettings('agrae','dbConnection')
        self.dns = {
            'dbname': self.s.value('dbname'),
            'user': self.s.value('dbuser'),
            'password': self.s.value('dbpass'),
            'host': self.s.value('dbhost'),
            'port': self.s.value('dbport')
        }
        self.conn = DbConnection.connection(self.dns['dbname'], self.dns['user'], self.dns['password'], self.dns['host'], self.dns['port'])

        pass

    def ConnParams(self):
        dns = self.dns
        return dns

    def Conn(self):
        conn = self.conn = DbConnection.connection(
            self.dns['dbname'], self.dns['user'], self.dns['password'], self.dns['host'], self.dns['port'])
        return conn

    def loadGeomLayers(self):
        # dns = self.ConnParams()
        # conn = DbConnection.connection(dns['dbname'], dns['user'], dns['password'], dns['host'])
        with self.conn as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(''' select table_name from information_schema.columns where column_name = 'geometria' ''')
                results = cursor.fetchall()
                layerList = [i[0] for i in results]
                # print(layerList)
                return layerList
            except:
                print('error')
            finally:
                conn.close()
            
        pass
    def loadLayers(self):
        with self.conn as conn: 
            try:
                cursor = conn.cursor()
                cursor.execute(
                    ''' select table_name from information_schema.tables where table_schema = 'public' order by table_name ''')
                results = cursor.fetchall()
                layerList = [i[0] for i in results]
                # print(layerList)
                return layerList
            except:
                print('error')
            finally:
                conn.close()
            
        pass

        dbuser = self.configDialog.user.text()

    def saveConfig(self,dbhost, dbname, dbuser, dbpass, dbport=5432):
        self.settings = QSettings('agrae', 'dbConnection')
        dbhost = dbhost
        dbname = dbname
        dbport = dbport
        dbuser = dbuser
        dbpass = dbpass
        try:
            self.settings.setValue('dbhost', dbhost)
            self.settings.setValue('dbname', dbname)
            self.settings.setValue('dbport', dbport)
            self.settings.setValue('dbuser', dbuser)
            self.settings.setValue('dbpass', dbpass)
        
        except: 
            print('ERROR')

    def dbTestConnection(self,dbname,dbuser,dbpass,dbhost,dbport):     
        conn = DbConnection.connection(dbname, dbuser, dbpass, dbhost, dbport)
        conn.close()

    def styleSheet(self):
        style = '''QTabBar::tab:selected {background : green ; color : white ; border-color : white }
                   QTabBar::tab {padding : 4px ; margin : 2px ;  border-radius : 2px  ; border: 1px solid #000 ; heigth: 15px }
                   '''
        return style

    def actualizarQueryLote(idlote, idexp=None, idcult=None, nombre=None, dateSiembra=None, dateCosecha=None, dateFertFondo=None, fondoFormula=None, fondoPrecio=None, fondoCalculado=None, fondoAjustado=None, fondoAplicado=None, dateFertCob1=None, cob1Formula=None, cob1Precio=None, cob1Calculado=None, cob1Ajustado=None, cob1Aplicado=None, dateFertCob2=None, cob2Formula=None, cob2Precio=None, cob2Calculado=None, cob2Ajustado=None, cob2Aplicado=None, dateFertCob3=None, cob3Formula=None, cob3Precio=None, cob3Calculado=None, cob3Ajustado=None, cob3Aplicado=None):
        sql = f'''update lote set  idexplotacion = '{idexp}', idcultivo = '{idcult}', nombre = '{nombre}',fechasiembra = '{dateSiembra}',fechacosecha = '{dateCosecha}',fechafertilizacionfondo = '{dateFertFondo}',    fertilizantefondoformula = '{fondoFormula}',fertilizantefondoprecio = {fondoPrecio}, fertilizantefondocalculado = {fondoCalculado},fertilizantefondoajustado = {fondoAjustado},  fertilizantefondoaplicado = {fondoAplicado},fechafertilizacioncbo1 = '{dateFertCob1}', fertilizantecob1formula ='{cob1Formula}',fertilizantecob1precio = {cob1Precio}, fertilizantecob1calculado = {cob1Calculado},fertilizantecob1ajustado = {cob1Ajustado}, fertilizantecob1aplicado = {cob1Aplicado},fechafertilizacioncbo2 = '{dateFertCob2}', fertilizantecob2formula = '{cob2Formula}', fertilizantecob2precio = {cob2Precio},  fertilizantecob2calculado = {cob2Calculado}, fertilizantecob2ajustado = {cob2Ajustado}, fertilizantecob2aplicado ={cob2Aplicado},fechafertilizacioncbo3 = '{dateFertCob3}', fertilizantecob3formula = '{cob3Formula}',fertilizantecob3precio = {cob3Precio}, fertilizantecob3calculado = {cob3Calculado},fertilizantecob3ajustado = {cob3Ajustado}, fertilizantecob3aplicado = {cob3Aplicado} where idlote = {idlote} '''

        return sql 

    def segmentosQueryTable(self, param=''):
        if param != '': 
            sql = f''' select sg.id,sg.idlotecampania,sg.lote,sg.regimen,sg.segmento,sg.cod_control,sg.fechasiembra,sg.cultivo,sg.cod_muestra from segmentos sg 
            where sg.cod_control ilike '%{param}%'
            or sg.cod_muestra ilike '%{param}%' 
            '''
            return sql
        else: 
            sql = f''' select sg.idsegmento,sg.idlotecampania,sg.lote,sg.regimen,sg.segmento,sg.cod_control,sg.fechasiembra,sg.cultivo,sg.cod_muestra from segmentos sg 
            '''
            return sql
    def sqlLoteParcela(self,idlote, nombre, fecha): 
        sql = f'''select l.idlote, l.nombre , lc.fechasiembra, lc.fechacosecha, c.nombre, st_multi(st_union(p.geometria)) geometria from loteparcela lp
        left join parcela p on lp.idparcela = p.idparcela 
        left join lote l on lp.idlote = l.idlote 
        left join campania lc on lc.idlote = l.idlote 
        left join cultivo c on c.idcultivo = lc.idcultivo 
        where l.idlote = {idlote} and l.nombre ilike '%{nombre}%' and  lc.fechacosecha = '{fecha}' 
        group by l.idlote , lc.fechasiembra , lc.fechacosecha, c.nombre
        order by lc.fechasiembra desc '''
        return sql

    def iconsPath(self):
        icons_path = {
            'agrae_icon': os.path.join(os.path.dirname(__file__), r'ui\icons\icon.svg'),
            'search_icon_path': os.path.join(os.path.dirname(__file__), r'ui\icons\search.svg'),
            'search_lotes': os.path.join(os.path.dirname(__file__), r'ui\icons\search-lotes.svg'),
            'search_parcela': os.path.join(os.path.dirname(__file__), r'ui\icons\search-parcela.svg'),
            'add_group_layers': os.path.join(os.path.dirname(__file__), r'ui\icons\paperclip-solid.svg'),
            'reload_data': os.path.join(os.path.dirname(__file__), r'ui\icons\reload.svg'),
            'link': os.path.join(os.path.dirname(__file__), r'ui\icons\link-solid.svg'),
            'link-slash': os.path.join(os.path.dirname(__file__), r'ui\icons\link-slash-solid.svg'),
            'add_plus': os.path.join(os.path.dirname(__file__), r'ui\icons\plus-solid.svg'),
            'create_rel': os.path.join(os.path.dirname(__file__), r'ui\icons\object-join.svg'),
            'drop_rel': os.path.join(os.path.dirname(__file__), r'ui\icons\minus-solid.svg'),
            'load_data': os.path.join(os.path.dirname(__file__), r'ui\icons\list-check-solid.svg'),
            'layer_upload': os.path.join(os.path.dirname(__file__), r'ui\icons\layer-upload-tool.svg'),
            'layer_edit': os.path.join(os.path.dirname(__file__), r'ui\icons\layer-edit.svg'),
            'add_layer_to_map': os.path.join(os.path.dirname(__file__), r'ui\icons\layer-add-o.svg'),
            'filter_objects': os.path.join(os.path.dirname(__file__), r'ui\icons\filter-solid.svg'),
            'menu': os.path.join(os.path.dirname(__file__), r'ui\icons\ellipsis-solid.svg'),
            'save': os.path.join(os.path.dirname(__file__), r'ui\icons\floppy-disk-solid.svg'),
            'share': os.path.join(os.path.dirname(__file__), r'ui\icons\share-solid.svg'),
            'pen-to-square': os.path.join(os.path.dirname(__file__), r'ui\icons\pen-to-square-solid.svg'),
            'import': os.path.join(os.path.dirname(__file__), r'ui\icons\file-import-solid.svg'),
            'export-csv': os.path.join(os.path.dirname(__file__), r'ui\icons\file-export-solid.svg'),
            'upload-to-db': os.path.join(os.path.dirname(__file__), r'ui\icons\upload-db.svg'),
            'chart': os.path.join(os.path.dirname(__file__), r'ui\icons\chart-bar-solid.svg'),
            'settings': os.path.join(os.path.dirname(__file__), r'ui\icons\gear-solid.svg'),
            'lgnd1': os.path.join(os.path.dirname(__file__), r'ui\img\lgnd1.svg'),
            'p1': os.path.join(os.path.dirname(__file__), r'ui\img\p1.svg'),
        }

        return icons_path

    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(
            self, "QFileDialog.getSaveFileName()", "", "Todos los Archivos (*);;Archivos separados por coma (*.csv)", options=options)
        if fileName:
            return fileName
        else:
            return False

    def msgBar(self,text:str,level:int,duration:int): 
        self.iface.messageBar().pushMessage('aGraes GIS', '{}'.format(text), level=level, duration=duration)

class AgraeToolset():
    def __init__(self):
        self.iface = iface
        self.s = QSettings('agrae', 'dbConnection')
        self.dns = {
            'dbname': self.s.value('dbname'),
            'user': self.s.value('dbuser'),
            'password': self.s.value('dbpass'),
            'host': self.s.value('dbhost'),
            'port': self.s.value('dbport')
        }
        self.conn = DbConnection.connection(
            self.dns['dbname'], self.dns['user'], self.dns['password'], self.dns['host'], self.dns['port'])
        pass

    def crearAmbientes(self,widget):
        # print('test')
        lyr = self.iface.activeLayer()
        srid = lyr.crs().authid()[5:]
        features = lyr.selectedFeatures()
        print(features)
        
        with self.conn as conn:
            try:
                cursor = conn.cursor()
                if len(features) > 0: 
                    for f in features:
                        # print('test')
                        oa = f[0]
                        amb = f[1]
                        ndvimax = f[2]
                        atlas = f[3]
                        geometria = f.geometry().asWkt()
                        sql = f''' insert into ambiente(obj_amb,ambiente,ndvimax,atlas,geometria)
                                values
                                ({oa},
                                {amb},
                                {ndvimax},
                                '{atlas}',
                                st_multi(st_force2d(st_transform(st_geomfromtext('{geometria}',{srid}),4326))))'''
                        # print(f'{oa}-{amb}-{ndvimax}-{atlas}')
                        cursor.execute(sql)
                        conn.commit()
                        print(f[0])
                        
                    QMessageBox.about(widget, 'aGrae GIS', 'Ambiente Cargado Correctamente \na la base de datos')
                else:
                    QMessageBox.about(
                        widget, 'aGrae GIS', 'Debe Seleccionar al menos un ambiente')

            except Exception as ex:
                # print(ex)
                conn.rollback()
                pass
    def cargarAmbientes(self, widget):
        dns = self.dns
        row = widget.tableWidget_2.currentRow()
        idlotecampania = widget.tableWidget_2.item(row, 1)
        lote = widget.tableWidget_2.item(row, 2)
        exp = f''' "idlotecampania" = {idlotecampania} '''
        uri = QgsDataSourceUri()
        uri.setConnection(dns['host'], dns['port'],
                          dns['dbname'], dns['user'], dns['password'])
        uri.setDataSource('public', 'segmentos', 'geometria', exp, 'id')
        nombreCapa = f'Ambientes Lote {lote}'
        layer = QgsVectorLayer(uri.uri(False), nombreCapa, 'postgres')
        if layer is not None and layer.isValid():
            QgsProject.instance().addMapLayer(layer)
            self.iface.setActiveLayer(layer)
            self.iface.zoomToActiveLayer()

    def crearParcela(self,widget=None):
        count = 0
        _count = 0
        with self.conn as conn:
            try:
                cur = conn.cursor()
                layer = self.iface.activeLayer()
                # print(layer.name())
                features = layer.getFeatures()
                confirm = QMessageBox.question(
                    widget, 'aGrae GIS', f"Se Cargaran {layer.featureCount()} recintos, de la capa {layer.name()} a la Base de Datos.\nProceder con la carga? ", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if confirm == QMessageBox.Yes: 
                    for feat in features: 
                        
                        ls = feat.geometry().asWkt()
                        srid = layer.crs().authid()[5:]
                        name = ''
                        prov = feat[2]
                        mcpo = feat[3]
                        aggregate = feat[4]
                        zone = feat[5]
                        poly = feat[6]
                        allotment = feat[7]
                        inclosure = feat[8]
                        idsigpac = feat[0]

                        sql = f'''INSERT INTO parcela(nombre,provincia,municipio,agregado,zona,poligono,parcela,recinto,geometria,idsigpac) VALUES('{name}',{prov},{mcpo},{aggregate},{zone},{poly},{allotment},{inclosure},st_multi(st_force2d(st_transform(st_geomfromtext('{ls}',{srid}),4326))),'{idsigpac}')'''
                        try:
                            cur.execute(sql)
                            conn.commit()
                            count += 1
                            # print('agregado correctamente')
                        except errors.lookup('23505'):
                            # errors.append(idParcela)
                            _count += 1
                            # print(f'La parcela {feat[0]} ya existe.')
                            # QMessageBox.about(widget, f"aGrae GIS:",f'La parcela: {feat[0]} ya existe.')
                            conn.rollback()

                    QMessageBox.about(widget, f"aGrae GIS:",
                                        f"Se agregaron {count} parcelas correctamente.\nErronas = {_count}")
                else: 
                    pass



            except IndexError as ie:
                QMessageBox.about(widget, f"aGrae GIS {ie}", f"Debe Seleccionar una parcela a cargar.")
                conn.rollback()

            except Exception as ex:
                # print(ex)
                QMessageBox.about(widget, f"aGrae GIS", f"No se pudo almacenar el registro {ex}")
                conn.rollback()
    def renameParcela(self,widget): 
        lyr = QgsProject.instance().mapLayersByName('aGrae Parcelas')[0]
        nombreParcelario = str(widget.lineEdit_2.text())
        with self.conn:
            try: 
                cursor = self.conn.cursor()
                for f in lyr.selectedFeatures():
                    # print(f[1])
                    idParcela = f[1]
                    if nombreParcelario != '':
                        sqlRename = f''' update parcela
                        set nombre = '{nombreParcelario}'
                        where idparcela = {idParcela}'''
                        cursor.execute(sqlRename)
                        self.conn.commit()
                        widget.lineEdit_2.setText('')
                        # print('exitoso')
                    else:
                        self.conn.rollback()

                        pass
            except Exception as ex: 
                print(ex)
            finally:
                conn.close()

        pass
    def cargarParcela(self,widget, id):
        self.sqlParcela = 'select * from parcela'
        idParcela = widget.idParcela
        exp = f'idparcela = {idParcela}'
        sql = self.sqlParcela
        dns = self.dns
        row = widget.tableWidget.currentRow()
        column = widget.tableWidget.currentColumn()
        try: 
            uri = self.retUri(sql, 'geometria', 'idparcela', exp,'parcela')
            nombre = id
            layer = QgsVectorLayer(uri.uri(False), nombre, 'postgres')
            if layer.isValid():
                QgsProject.instance().addMapLayer(layer)
                self.iface.setActiveLayer(layer)
                self.iface.zoomToActiveLayer()
                # print(f"Capa añadida correctamente ")
                # widget.pushButton.setEnabled(False)
            else:
                QMessageBox.about(self, "aGrae GIS:",
                                    "La capa no es Valida")
        except Exception as ex:
            # print(ex)
            QMessageBox.about(
                widget, f"Error:", f"Debe seleccionar un campo para el Nombre")

    def cargarGrupoParcelas(self, widget):
        dns = self.dns
        row = widget.tableWidget.currentRow() 
        nombreParcelario = widget.tableWidget.item(row, 1).text()
        exp = f''' "nombre" ilike '{nombreParcelario}' '''
        uri = QgsDataSourceUri()
        uri.setConnection(dns['host'], dns['port'],
                          dns['dbname'], dns['user'], dns['password'])
        uri.setDataSource('public', 'parcela', 'geometria', exp, 'idparcela')
        layer = QgsVectorLayer(uri.uri(False),nombreParcelario,'postgres')
        QgsProject.instance().addMapLayer(layer)
        self.iface.setActiveLayer(layer)
        self.iface.zoomToActiveLayer()
    def buscarLotes(self,widget,status):
        nombre = widget.line_buscar.text()
        sinceDate = widget.sinceDate.date().toString('yyyy-MM-dd')
        untilDate = widget.untilDate.date().toString('yyyy-MM-dd')

        sqlQuery = ''
         
        with self.conn as conn:
            try:
                if nombre == '' and status == False:
                    sqlQuery = f'''select lc.idlotecampania , l.nombre lote, p.nombre parcela, ca.fechasiembra, ca.fechacosecha , cu.nombre cultivo, ca.prod_esperada, ls.biomasa, ls.residuo , cu.indice_cosecha, cu.contenidocosechac, cu.contenidoresiduoc 
                    from lotecampania lc
                    join loteparcela lp on lp.idlotecampania = lc.idlotecampania
                    join lotes ls on lc.idlotecampania = ls.idlotecampania
                    left join lote l on l.idlote = lc.idlote
                    left join parcela p on p.idparcela = lp.idparcela 
                    left join campania ca on ca.idcampania = lc.idcampania 
                    left join cultivo cu on cu.idcultivo = ca.idcultivo 
                    group by lc.idlotecampania , l.nombre , p.nombre , ca.fechasiembra , ca.fechacosecha , cu.nombre, ca.prod_esperada , ls.biomasa, ls.residuo, cu.indice_cosecha , cu.contenidocosechac, cu.contenidoresiduoc 
                    order by ca.fechasiembra desc'''
                    widget.btn_add_layer.setEnabled(False)
                    try:
                        widget.btn_chart.setEnabled(True)
                    except:
                        pass
                    

                elif nombre != '' and status == False:
                    sqlQuery = f"""select lc.idlotecampania , l.nombre lote, p.nombre parcela, ca.fechasiembra, ca.fechacosecha , cu.nombre cultivo, ca.prod_esperada, ls.biomasa, ls.residuo, cu.indice_cosecha, cu.contenidocosechac, cu.contenidoresiduoc 
                    from lotecampania lc
                    join loteparcela lp on lp.idlotecampania = lc.idlotecampania
                    join lotes ls on lc.idlotecampania = ls.idlotecampania
                    left join lote l on l.idlote = lc.idlote
                    left join parcela p on p.idparcela = lp.idparcela 
                    left join campania ca on ca.idcampania = lc.idcampania 
                    left join cultivo cu on cu.idcultivo = ca.idcultivo 
                    where l.nombre ilike '%{nombre}%' or p.nombre ilike '%{nombre}%' or cu.nombre ilike '%{nombre}%' 
                    group by lc.idlotecampania , l.nombre , p.nombre , ca.fechasiembra , ca.fechacosecha , cu.nombre, ca.prod_esperada , ls.biomasa, ls.residuo, cu.indice_cosecha, cu.contenidocosechac, cu.contenidoresiduoc 
                    order by ca.fechasiembra desc                        
                    """
                    widget.btn_reload.setEnabled(True)
                    try:
                        widget.btn_chart.setEnabled(True)
                    except:
                        pass

                elif nombre == '' and status == True:
                    sqlQuery = f"""select lc.idlotecampania , l.nombre lote, p.nombre parcela, ca.fechasiembra, ca.fechacosecha , cu.nombre cultivo, ca.prod_esperada, ls.biomasa, ls.residuo, cu.indice_cosecha, cu.contenidocosechac, cu.contenidoresiduoc 
                    from lotecampania lc
                    join loteparcela lp on lp.idlotecampania = lc.idlotecampania
                    join lotes ls on lc.idlotecampania = ls.idlotecampania
                    left join lote l on l.idlote = lc.idlote
                    left join parcela p on p.idparcela = lp.idparcela 
                    left join campania ca on ca.idcampania = lc.idcampania 
                    left join cultivo cu on cu.idcultivo = ca.idcultivo 
                    where ca.fechasiembra >= '{sinceDate}' and ca.fechasiembra <= '{untilDate}'
                    group by lc.idlotecampania , l.nombre , p.nombre , ca.fechasiembra , ca.fechacosecha , cu.nombre, ca.prod_esperada , ls.biomasa, ls.residuo, cu.indice_cosecha, cu.contenidocosechac, cu.contenidoresiduoc 
                    order by ca.fechasiembra desc"""
                    widget.btn_reload.setEnabled(True)
                    try:
                        widget.btn_chart.setEnabled(True)
                    except:
                        pass

                elif nombre != '' and status == True:
                    sqlQuery = f"""select lc.idlotecampania , l.nombre lote, p.nombre parcela, ca.fechasiembra, ca.fechacosecha , cu.nombre cultivo, ca.prod_esperada, ls.biomasa, ls.residuo, cu.indice_cosecha, cu.contenidocosechac, cu.contenidoresiduoc 
                    from lotecampania lc
                    join loteparcela lp on lp.idlotecampania = lc.idlotecampania
                    join lotes ls on lc.idlotecampania = ls.idlotecampania
                    left join lote l on l.idlote = lc.idlote
                    left join parcela p on p.idparcela = lp.idparcela 
                    left join campania ca on ca.idcampania = lc.idcampania 
                    left join cultivo cu on cu.idcultivo = ca.idcultivo 
                    where ca.fechasiembra >= '{sinceDate}' and ca.fechasiembra <= '{untilDate}'
                    or l.nombre ilike '%{nombre}%' or p.nombre ilike '%{nombre}%' or cu.nombre ilike '%{nombre}%' 
                    group by lc.idlotecampania , l.nombre , p.nombre , ca.fechasiembra , ca.fechacosecha , cu.nombre, ca.prod_esperada , ls.biomasa, ls.residuo, cu.indice_cosecha, cu.contenidocosechac, cu.contenidoresiduoc 
                    order by ca.fechasiembra desc"""
                    widget.btn_reload.setEnabled(True)
                    try:
                        widget.btn_chart.setEnabled(True)
                    except:
                        pass


                cursor = conn.cursor()
                cursor.execute(sqlQuery)
                data = cursor.fetchall()
                if len(data) == 0:
                    QMessageBox.about(
                        widget, "aGrae GIS:", "No existen registros con los parametros de busqueda")
                    widget.tableWidget.setRowCount(0)
                else:
                    widget.btn_add_layer.setEnabled(True)
                    # widget.btn_add_layer_2.setEnabled(True)
                    widget.sinceDateStatus = False
                    widget.untilDate.setEnabled(False)
                    self.queryCapaLotes = sqlQuery
                    a = len(data)
                    b = len(data[0])
                    i = 1
                    j = 1
                
                
                    widget.tableWidget.setRowCount(a)
                    widget.tableWidget.setColumnCount(b)
                    for j in range(a):
                        for i in range(b):
                            item = QTableWidgetItem(str(data[j][i]))
                            widget.tableWidget.setItem(j,i,item)
                        obj = widget.tableWidget.item(j,1).text()
            except Exception as ex:
                # print(ex)
                print(ex)
                QMessageBox.about(widget, "Error:", f"Verifica el Parametro de Consulta (ID o Nombre)")  
            
    def cargarLote(self,widget):
        selected = widget.tableWidget.selectionModel().selectedRows()
        dns = self.dns

        if len(selected) == 0: 
            msg = 'Debes seleccionar un lote'
            QMessageBox.about(widget, "aGrae GIS:", f"{msg}")
        elif len(selected) >1: 
            msg = 'Debes seleccionar solo un lote'
            QMessageBox.about(widget, "aGrae GIS:", f"{msg}")
        else:          
            row = widget.tableWidget.currentRow()
            column = widget.tableWidget.currentColumn()           
            try:
                idlote = widget.tableWidget.item(row, 0)
                nombreLote = widget.tableWidget.item(row, 1)
                nombreParcela = widget.tableWidget.item(row, 2)
                fecha = widget.tableWidget.item(row, 3)
                exp = f''' "idlotecampania" = {idlote.text()} and "lote" ilike '%{nombreLote.text()}%' and "parcela" ilike'%{nombreParcela.text()}%' and "fechasiembra" = '{fecha.text()}' '''
                uri = QgsDataSourceUri()
                uri.setConnection(dns['host'], dns['port'],
                                  dns['dbname'], dns['user'], dns['password'])
                uri.setDataSource('public', 'lotes', 'geometria', exp, 'id')


                nombreCapa = f'{nombreLote.text()}-{nombreParcela.text()}-{widget.tableWidget.item(row, 5).text()}'
                layer = self.iface.addVectorLayer(uri.uri(False), nombreCapa, 'postgres')
                    
                if layer is not None and layer.isValid():
                    QgsProject.instance().addMapLayer(layer)
                    self.iface.setActiveLayer(layer)
                    self.iface.zoomToActiveLayer()
                    # print(f"Capa añadida correctamente ")
                else:
                    QMessageBox.about(widget, "aGrae GIS:", "Capa invalida.")
            
            except Exception as ex:
                # print(ex)
                QMessageBox.about(widget, f"Error:{ex}", f"Debe seleccionar un campo para el Nombre")
    def dataSegmento(self,table):
        lyr = self.iface.activeLayer()
        features = lyr.getFeatures()
        columns = [fld.name() for fld in lyr.fields()]
        data = ([f[col] for col in columns] for f in features)
        df = pd.DataFrame.from_records(data=data, columns=columns)
        
        
        nRows , nColumns = df.shape
        table.setRowCount(nRows)
        table.setColumnCount(nColumns)
        table.setHorizontalHeaderLabels(columns)
        for r in range(table.rowCount()):
            for c in range(table.columnCount()):
                item = QTableWidgetItem(str(df.iloc[r,c]))
                table.setItem(r,c,item)
    def crearSegmento(self,widget,table):
        lyr = self.iface.activeLayer()
        srid = lyr.crs().authid()[5:]
        features = lyr.getFeatures()

        nRow = table.rowCount() 
        nColumn = table.columnCount()
        try:
            with self.conn as conn:
                try: 
                    cursor = conn.cursor()
                    for row , f in (zip(range(nRow), features)):
                        segm = f[0]               
                        geometria = f.geometry() .asWkt()                                        
                        sql = f""" insert into segmento(segmento,geometria)
                                            values
                                            ({segm},
                                            st_multi(st_force2d(st_transform(st_geomfromtext('{geometria}',{srid}),4326))))"""                   
                        cursor.execute(sql)
                        conn.commit()                            
                        # print(sql)

                    QMessageBox.about(widget, 'aGrae GIS', 'Segmento Cargado Correctamente \na la base de datos')
                finally: 
                    conn.close()
        except Exception as ex: 
            # print(ex)
            pass
    
    def asignarCodigoSegmento(self,widget):
        code = self.lastCode() 
        row = widget.tableWidget_2.currentRow()
        idsegmento = widget.tableWidget_2.item(row, 0).text()
        idlotecampania = widget.tableWidget_2.item(row, 1).text()
        analisis = widget.tableWidget_2.item(row, 7).text()
        print(idsegmento, idlotecampania, analisis)
        cursor = self.conn.cursor()
        sql = f''' insert into segmentoanalisis (idsegmento,idlotecampania,idanalisis)
                select {idsegmento},{idlotecampania} , qan.idanalisis 
                from (select idanalisis from analisis where cod_analisis ilike '%{analisis}%') qan '''
        try:
            cursor.execute(sql)
            self.conn.commit()
            print('relacionado correctamente')
        except errors.lookup('23505'):
            print('Segmento ya pertenece al lote')
            self.conn.rollback()
        except Exception as ex:
            print(ex)
            self.conn.rollback()
        finally: 
            self.conn.close()
            
            
    def cargarSegmentos(self,widget):
        dns = self.dns
        row = widget.tableWidget_2.currentRow()
        idlotecampania = widget.tableWidget_2.item(row,1)
        lote = widget.tableWidget_2.item(row,2)
        cultivo = widget.tableWidget_2.item(row,6)
        exp = f''' "idlotecampania" = {idlotecampania} '''
        uri = QgsDataSourceUri()
        uri.setConnection(dns['host'], dns['port'],
                            dns['dbname'], dns['user'], dns['password'])
        uri.setDataSource('public', 'segmentos', 'geometria', exp, 'id')
        nombreCapa = f'Segmentos Lote {lote}-{cultivo}'
        layer = QgsVectorLayer(uri.uri(False), nombreCapa, 'postgres')
        if layer is not None and layer.isValid():
            QgsProject.instance().addMapLayer(layer)
            self.iface.setActiveLayer(layer)
            self.iface.zoomToActiveLayer()
    

    
    def lastCode(self): 
        with self.conn as conn: 
            cursor = conn.cursor()
            try: 
                sql = ''' select s.codigo from segmentoanalisis s 
                order by s.idsegmentoanalisis desc limit 1'''
                cursor.execute(sql)
                code = cursor.fetchone()
                if len(code) > 0: 
                    return code[0]
                else: 
                    code = 'NO DATA'
            except Exception as ex:

                # print(ex)
                code = 'NO DATA'
                return code
                pass
    def addMapLayer(self, table, nombre, ogr='postgres', geom='geometria',id=None):
        dns = self.dns
        uri = QgsDataSourceUri()
        uri.setConnection(dns['host'], dns['port'],
                          dns['dbname'], dns['user'], dns['password'])
        if id != None:                  
            uri.setDataSource('public',table,geom,'',id)
        else: 
            uri.setDataSource('public',table,geom,'')

        layer = QgsVectorLayer(uri.uri(False), f'{nombre}', f'{ogr}')
        QgsProject.instance().addMapLayer(layer)
    def retUri(self,sql,geom,id, exp=None, table=None):
        dns = self.dns
        uri = QgsDataSourceUri()
        uri.setConnection(dns['host'], dns['port'],
                          dns['dbname'], dns['user'], dns['password'])
        if exp == None and table == None:  
            uri.setDataSource('', f'({sql})',f'{geom}', '', f'{id}')
        else: 
            uri.setDataSource('public', table ,geom ,exp)


        return uri
    def crearCampania(self,widget):
        lote = str(widget.line_lote_nombre.text()).upper()
        idexp = widget.line_lote_idexp.text()
        idcult = widget.line_lote_idcultivo.text()
        dateSiembra = widget.lote_dateSiembra.date().toString('yyyy.MM.dd')
        dateCosecha = widget.lote_dateCosecha.date().toString('yyyy.MM.dd')
        dateFondo = widget.date_fondo.date().toString('yyyy.MM.dd')
        fondoFormula = widget.line_fondo_formula.text()
        fondoPrecio = float(widget.line_fondo_precio.text())
        fondoCalculado = float(widget.line_fondo_calculado.text())
        fondoAjustado = widget.line_fondo_ajustado.text()
        fondoAplicado = float(widget.line_fondo_aplicado.text())
        dateCob1 = widget.date_cob.date().toString('yyyy.MM.dd')
        cob1Formula = widget.line_cob_formula.text()
        cob1Precio = float(widget.line_cob_precio.text())
        cob1Calculado = float(widget.line_cob_calculado.text())
        cob1Ajustado = widget.line_cob_ajustado.text()
        cob1Aplicado = float(widget.line_cob_aplicado.text())
        dateCob2 = widget.date_cob_2.date().toString('yyyy.MM.dd')
        cob2Formula = widget.line_cob_formula_2.text()
        cob2Precio = float(widget.line_cob_precio_2.text())
        cob2Calculado = float(widget.line_cob_calculado_2.text())
        cob2Ajustado = widget.line_cob_ajustado_2.text()
        cob2Aplicado = float(widget.line_cob_aplicado_2.text())
        dateCob3 = widget.date_cob_3.date().toString('yyyy.MM.dd')
        cob3Formula = widget.line_cob_formula_3.text()
        cob3Precio = float(widget.line_cob_precio_3.text())
        cob3Calculado = float(widget.line_cob_calculado_3.text())
        cob3Ajustado = widget.line_cob_ajustado_3.text()
        cob3Aplicado = float(widget.line_cob_aplicado_3.text())
        if widget.ln_und_precio.currentIndex() > 0:
            unidadDesprecio = widget.ln_und_precio.currentText()
        else:
            unidadDesprecio = NULL
        regimen = int(widget.cmb_regimen.currentIndex())
        produccion = float(widget.ln_produccion.text())
      
        sql = f'''
        insert into campania 
        values(nextval('campania_idcampania_seq') ,{idexp}, {idcult},'{dateSiembra}','{dateCosecha}', '{dateFondo}','{fondoFormula}',{fondoPrecio}, {fondoCalculado}, {fondoAjustado},  {fondoAplicado}, '{dateCob1}', '{cob1Formula}', {cob1Precio},  {cob1Calculado}, {cob1Ajustado},  {cob1Aplicado}, '{dateCob2}',  '{cob2Formula}',  {cob2Precio},   {cob2Calculado},  {cob2Ajustado}, {cob2Aplicado}, '{dateCob3}',  '{cob3Formula}', {cob3Precio},  {cob3Calculado}, {cob3Ajustado},  {cob3Aplicado} , '{unidadDesprecio}',{regimen}, {produccion});
        '''

        sql2 = f'''insert into lotecampania(idlote,idcampania) 
        select ql.idlote, qc.idcampania from (select idlote from lote where nombre = '{lote}') as ql, (select idcampania from campania order by idcampania desc limit 1) as qc; '''
       
        conn = connect(dbname=self.dns['dbname'], user=self.dns['user'],
                       password=self.dns['password'], host=self.dns['host'], port=self.dns['port'])
        with conn:
            try: 
                if regimen != 0:
                    cursor = conn.cursor()
                    cursor.execute(sql)
                    conn.commit()
                    cursor.execute(sql2)
                    conn.commit()
                    QMessageBox.about(widget, f"aGrae GIS:",f"Campaña creada y asociada correctamente")
                else: 
                    QMessageBox.about(widget, f"aGrae GIS:",f"Debe seleccionar un Regimen de Cultivo")
            except InterfaceError as ie: 
                conn = widget.utils.Conn()
                cursor = conn.cursor()
                cursor.execute(sql)
                QMessageBox.about(widget, f"aGrae GIS:", f"Campaña creada correctamente")


            except Exception as e: 
                # print(e)
                QMessageBox.about(widget, f"Error: ",f"{e}")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)

               

    def crearLote(self,widget):
        nombre = str(widget.line_lote_nombre.text()).upper()
        sql = f""" insert into lote(nombre) values('{nombre}')  """
        conn = connect(dbname=self.dns['dbname'], user=self.dns['user'],
                       password=self.dns['password'], host=self.dns['host'], port=self.dns['port'])
        with conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                # print('Lote creado')
                QMessageBox.about(
                    widget, f"aGrae GIS:", f"Lote: {nombre} Creado Correctamente.\nCrear una campaña para continuar.")
                conn.commit()
                
            except errors.lookup('23505'):
                # print('El lote ya existe, ingresa otro nombre o modifica el existente')
                QMessageBox.about(
                    widget, f"aGrae GIS:", f"El Lote: {nombre} ya existe.\nIngresa otro Nombre o Modifica el Existente")
                conn.rollback()
                widget.line_lote_nombre.setText('')
                
                # widget.line_lote_nombre.setEnabled(False)

            except Exception as ex:
                # print(ex)
                QMessageBox.about(
                    widget, f"ERROR:", f"Ocurrio un Error")
                conn.rollback()
                widget.line_lote_nombre.setText('')
                
                # widget.line_lote_nombre.setEnabled(False)
            
            finally:
                conn.close()
               
    def cargarAnalitica(self,path, widget): 
        file = path        
        df = pd.read_csv(r"C:\Users\FRANCISCO\Desktop\reporte_16042022.csv",delimiter=';')
        df = df.astype(object).replace(np.nan, None)       
        columns = [c for c in df.columns]
        data = ([f[col] for col in columns] for f in df)
        df = pd.DataFrame.from_records(data=data, columns=columns)

        nRows, nColumns = df.shape
        table.setRowCount(nRows)
        table.setColumnCount(nColumns)
        table.setHorizontalHeaderLabels(columns)
        for r in range(table.rowCount()):
            for c in range(table.columnCount()):
                item = QTableWidgetItem(str(df.iloc[r, c]))
                table.setItem(r, c, item)


    def populateTable(self,sql,widget, action=False):
        
        with self.conn:
                cursor = self.conn.cursor()
                cursor.execute(sql)
                data = cursor.fetchall()
                a = len(data)
                b = len(data[0])
                i = 1
                j = 1
                widget.setRowCount(a)
                widget.setColumnCount(b)
                for j in range(a):
                    for i in range(b):
                        item = QTableWidgetItem(str(data[j][i]))
                        widget.setItem(j, i, item)



    def editionMode(self, variable, table, button): 
        if variable == False:
            table.setEditTriggers(QAbstractItemView.AllEditTriggers)
            variable = True
            button.setEnabled(True)
            print('editando')
        else:
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            variable = False
            button.setEnabled(False)
            print('nada')


class AgraeAnalitic(): 
    def __init__(self):
        self.s = QSettings('agrae', 'dbConnection')
        self.dns = {
            'dbname': self.s.value('dbname'),
            'user': self.s.value('dbuser'),
            'password': self.s.value('dbpass'),
            'host': self.s.value('dbhost'),
            'port': self.s.value('dbport')
        }
        self.conn = DbConnection.connection(
            self.dns['dbname'], self.dns['user'], self.dns['password'], self.dns['host'], self.dns['port'])
        pass
    
    def classification(self,table,value,clase,li,ls): 
        sql = 'select * from analisis.{} where {} between {} and {}'.format(table,value,li,ls)
        with self.conn: 
            cursor = self.conn.cursor(cursor_factory=extras.RealDictCursor)
            cursor.execute(sql)
            data = cursor.fetchone()
            
            return data[clase]
       
        
    def phColor(self,l):
        colors = {
            1: 'rgb(250, 55, 13)',
            2: 'rgb(250, 121, 13)',
            3: 'rgb(250, 211, 13)',
            4: 'rgb(125, 250, 13)',
            5: 'rgb(250, 121, 13)',
            6:  'rgb(22, 200, 13)',
            7:  'rgb(13, 186, 200)',
            8:  'rgb(13, 95, 200)',
            9:  'rgb(115, 13, 200)'

        } 
        if l in colors: 
            return colors[l]

    def sumaPonderada(self, x, y):
        """
        x = Value y = Area

        """
        zipedd = zip(x, y)
        p1 = [x * y for (x, y) in zipedd]
        p2 = round(sum(p1)/sum(y))

        # print(p2)
        return p2

class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data
        self.colors = {'UF1': '#0be825',
                       'UF2': '#dd3f20',
                       'UF3': '#f5f227',
                       'UF4': '#0e13a9',
                       'UF5': '#f618d5',
                       'UF6': '#d5d5d5',
                       'UF7': '#18d9f6',
                       'UF8': '#8800e2',
                       'UF9': '#fab505'}

    def data(self, index, role):

        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            if value != NULL:
                return str(value)
            else:
                return int(0)
        if role == Qt.BackgroundRole and index.column() == 0:
            value = self._data.iloc[index.row()][0]
            if value in self.colors.keys():
                return QtGui.QColor(self.colors[value])
        

        if role == Qt.FontRole:                     
            return QtGui.QFont("Segoe UI", 9, QtGui.QFont.Bold)
       
       
        if role == Qt.TextAlignmentRole: 
            return Qt.AlignCenter
        
            

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Vertical:
                return str(self._data.index[section])


class PanelRender():
    """
    Class PanelRender:  Renderiza el panel agropecuario con los siguientes parametros. 
    lote(string) = Nombre del Lote.
    parcela(string) = Nombre Parcelario.
    cultivo = Nombre Cultivo
    produccion(int) = Produccion Ponderada
    n,p,k (int) = Valores Resultantes de NPK 

    """

    path = {'base': os.path.join(os.path.dirname(__file__), r'ui\img\base00.png'),
            'base2': os.path.join(os.path.dirname(__file__), r'ui\img\base02.png'),
            'base3': os.path.join(os.path.dirname(__file__), r'ui\img\base03.png'),
            'base4': os.path.join(os.path.dirname(__file__), r'ui\img\base04.png'),
            'plot': os.path.join(os.path.dirname(__file__), r'ui\img\chart.png'),
            'table': os.path.join(os.path.dirname(__file__), r'ui\img\tabla.png'),
            'tf1': os.path.join(os.path.dirname(__file__), r'ui\img\tf1.png'),
            'tf2': os.path.join(os.path.dirname(__file__), r'ui\img\tf2.png'),
            'tf3': os.path.join(os.path.dirname(__file__), r'ui\img\tf3.png'),
            'tf4': os.path.join(os.path.dirname(__file__), r'ui\img\tf4.png'),
            'trigo_esquema': os.path.join(os.path.dirname(__file__), r'ui\img\assets\trigo_esquema.png')}

    _cultivos_path = {
        'TRIGO B': os.path.join(os.path.dirname(__file__), r'ui\img\assets\cereal_esquema.png'),
        'MAIZ G': os.path.join(os.path.dirname(__file__), r'ui\img\assets\maiz_esquema.png'),
                }

    def __init__(self, lote, parcela, cultivo, produccion, area, npk: list, i: int, pesos:list, precios:list,aplicados:list,formulas:list,dataHuellaCarbono,preciosTon:list,moneda):
        
        
        
        self.iface = iface
        self.now = datetime.now()
        self.date = self.now.strftime("%H%M%S%d%m%y")
        self.lote = lote
        self.parcela = parcela
        self.cultivo = cultivo
        self.prod_ponderado = produccion
        self.area = area
        self.n_ponderado = npk[0]
        self.p_ponderado = npk[1]
        self.k_ponderado = npk[2]

        self.i = i
        self._pesos = pesos
        self._pesos_aplicados = aplicados
        self._precios = precios
        self._precios_ton = preciosTon
        self.formulas = formulas
        self.dataHuellaCarbono = dataHuellaCarbono
        self.moneda = moneda
       

        

        self.p1 = None
        self.p2 = None
        self.p3 = None
        self.phc = None

        self.font = ImageFont.truetype("arialbi.ttf", 13)
        self.font2 = ImageFont.truetype("arialbi.ttf", 10)
        self.font3 = ImageFont.truetype("arialbi.ttf", 12)
        self.color = (0, 0, 0)

        pass

    def panelUno(self):
        
        img = Image.open(self.path['base'])
        font = ImageFont.truetype("arialbi.ttf", 13)
        font2 = ImageFont.truetype("arialbi.ttf", 10)
        color = (0, 0, 0)
        d1 = ImageDraw.Draw(img)
        d1.text((328, 434), "{} Kg cosecha/Ha".format(self.prod_ponderado),
                font=font, fill=color)
        d2 = ImageDraw.Draw(img)
        d2.text((630, 434), "{} Ha".format(self.area), font=font, fill=color)
        d3 = ImageDraw.Draw(img)
        d3.text((576, 456), "{} / {} / {}".format(self.n_ponderado, self.p_ponderado, self.k_ponderado),
                font=font, fill=color)
        img2 = Image.open(self.path['plot'])
        img2 = img2.resize((281, 211))
        img.paste(img2, (25, 184), mask=img2)
        img3 = Image.open(self.path['table'])
        img3 = img3.resize((386, 225))
        img.paste(img3, (314, 187), mask=img3)
        
        self.setEsquema(self.cultivo, img)


        d4 = ImageDraw.Draw(img)
        d4.text((44, 225), "N", font=font2, fill=color)
        d4.text((44, 262), "P", font=font2, fill=color)
        d4.text((44, 303), "K", font=font2, fill=color)
        d4.text((28, 340), "Carb.", font=font2, fill=color)
        self.p1 = img

    def setEsquema(self, cultivo, img):
        try:
            if cultivo in self._cultivos_path:
                path = self._cultivos_path[cultivo]
                esquema = Image.open(path)
                esquema = esquema.resize((290, 141))
                img.paste(esquema, (25, 50), mask=esquema)
        except UnboundLocalError:
            print('No existe Grafico')
            pass
    
    def panelHuellaCarbono(self,
                           datos: dict = {
                               'percent': 0,
                               'chc': 0,
                               'biomasa': 0,
                               'cosecha': 0,
                               'residuo': 0,
                               'fertilizacion': 0
                           }):
        font = ImageFont.truetype("arialbi.ttf", 18)
        font2 = ImageFont.truetype("arialbi.ttf", 12)
        img = Image.open(self.path['base4'])
        draw = ImageDraw.Draw(img)
        txt = 'Si hacemos las coseas BIEN, además de\nahorrar Fertilizante, conseguimos un\n{}% de HUELLA DE CARBONO\nrepecto a seguir haciendolas como siempre'.format(
            datos['percent'])
        draw.text((240, 140), txt, font=font, fill=self.color,
                  anchor='mm', align='center', spacing=12)  # ! TEXTO PANEL
        draw.text((620, 100), '{:,} KgCO2eq/ha'.format(datos['chc']), font=font, fill=(110, 178, 83),
                  anchor='mm', align='center', spacing=12)  # ! CAPTURA HUELLA DE CARBONO
        draw.text((680, 135), '{:,} KgCO2eq/ha'.format(datos['biomasa']), font=font2, fill=(0, 0, 0),
                  anchor='mm', align='center', spacing=12)  # ! CAPTURA BIOMASA
        draw.text((680, 160), '{:,} KgCO2eq/ha'.format(datos['cosecha']), font=font2, fill=(0, 0, 0),
                  anchor='mm', align='center', spacing=12)  # ! CAPTURA COSECHA
        draw.text((680, 185), '{:,} KgCO2eq/ha'.format(datos['residuo']), font=font2, fill=(0, 0, 0),
                  anchor='mm', align='center', spacing=12)  # ! CAPTURA RESIDUO
        draw.text((680, 205), '{:,} KgCO2eq/ha'.format(datos['fertilizacion']*(-1)), font=font2, fill=(0, 0, 0),
                  anchor='mm', align='center', spacing=12)  # ! CAPTURA FERTILZIACION VARIABLE
        self.phc = img
        pass


    def panelDos(self, i, pesos,precios):
        def modify(formula):
            # print(formula)
            pa = re.compile('^[0]')
            f = ''

            # formula = list(formula.split('-'))
            for e in formula:

                if re.match(pa, e):
                    e = e[1:]

                f = f + ' {}% -'.format(e)

            return f[:-1]
        font = ImageFont.truetype("arialbi.ttf", 15)
        font2 = ImageFont.truetype("arialbi.ttf", 13)
        font3 = ImageFont.truetype("arialbi.ttf", 22)
        font4 = ImageFont.truetype("arialbi.ttf", 16)
        color = self.color
        formulas = ''

        total_peso = sum(pesos)
        coste_unitario = sum(precios)

        coste_total = round((coste_unitario * self.area),2)

        w = 117
        h = 307

        datos = self.dataHuellaCarbono


        img = Image.open(self.path['base2'])
        draw = ImageDraw.Draw(img)
        if i >= 1:
            tf1 = Image.open(self.path['tf1'])
            tf1 = tf1.resize((w, h))
            img.paste(tf1, (67, 155), mask=tf1)
            f1 = modify(self.formulas[0])
            formulas = formulas + f1 + ' --- '
            draw.text((120,140), '{}'.format(f1), font=font,fill=(0,0,0),anchor='mm') #! FORMULA 1
            draw.text((75, 450), '{} Kg/Ha\n{:,} {}/Ha'.format(pesos[0], precios[0],self.moneda), font=font, fill=color, align='center', spacing=8)
        if i >= 2:
            tf2 = Image.open(self.path['tf2'])
            tf2 = tf2.resize((w, h))
            img.paste(tf2, (232, 155), mask=tf2)
            f2 = modify(self.formulas[1])
            formulas = formulas + f2 + ' --- '
            draw.text((285,140), f2, font=font,fill=color,anchor='mm') #! FORMULA 2
            draw.text((245, 450), '{} Kg/Ha\n{:,} {}/Ha'.format(pesos[1], precios[1], self.moneda), font=font, fill=color, align='center', spacing=8)
        if i >= 3:
            tf3 = Image.open(self.path['tf3'])
            tf3 = tf3.resize((w, h))
            img.paste(tf3, (400, 155), mask=tf3)
            f3 = modify(self.formulas[2])
            formulas = formulas + f3 + ' --- '
            draw.text((455,140), f3, font=font,fill=color,anchor='mm') #! FORMULA 3
            draw.text((410, 450), '{} Kg/Ha\n{:,} {}/Ha'.format(
                pesos[2], precios[2],self.moneda), font=font, fill=color, align='center', spacing=8)
        if i >= 4:
            tf4 = Image.open(self.path['tf4'])
            tf4 = tf4.resize((w, h))
            img.paste(tf4, (566, 155), mask=tf4)
            f4 = modify(self.formulas[3])
            formulas = formulas + f4 + ' --- '
            draw.text((620,140), f4, font=font,fill=color,anchor='mm') #! FORMULA 4
            draw.text((580, 450), '{} Kg/Ha\n{:,}{}/Ha'.format(
                pesos[3], precios[3], self.moneda), font=font, fill=color, align='center', spacing=8)
        
        draw.text((270, 532), '{:,} {}/Ha'.format(coste_unitario,self.moneda), font=font3, fill=color)
        draw.text((270, 584), '{:,} Ha'.format(self.area), font=font3, fill=color)
        draw.text((500, 545), '{} {:,}'.format(self.moneda,coste_total), font=font3, fill=color)


        txt = 'Si hacemos las coseas BIEN, además\nde ahorrar Fertilizante, conseguimos un\n{}% de HUELLA DE CARBONO\nrepecto a seguir haciendolas como\nsiempre'.format(
            datos['percent'])
        draw = ImageDraw.Draw(img)
        draw.text((210, 735), txt,
                  font=font,
                  fill=self.color,
                  anchor='mm',
                  align='center',
                  spacing=10)  # ! TEXTO PANEL
        draw.text((520, 652), '{:,} KgCO2eq/ha'.format(datos['chc']), font=ImageFont.truetype("arialbi.ttf", 22), fill=(110, 178, 83),
                  anchor='mm', align='center', spacing=12)  # ! CAPTURA HUELLA DE CARBONO
        draw.text((590, 687), '{:,} KgCO2eq/ha'.format(datos['biomasa']), font=ImageFont.truetype("arialbi.ttf", 15), fill=(110, 178, 83),
                  anchor='mm', align='center', spacing=12)  # ! CAPTURA BIOMASA
        draw.text((605, 722), '{:,} KgCO2eq/ha'.format(datos['cosecha']), font=ImageFont.truetype("arialbi.ttf", 15), fill=(110, 178, 83),
                  anchor='mm', align='center', spacing=12)  # ! CAPTURA COSECHA
        draw.text((605, 760), '{:,} KgCO2eq/ha'.format(datos['residuo']), font=ImageFont.truetype("arialbi.ttf", 15), fill=(110, 178, 83),
                  anchor='mm', align='center', spacing=12)  # ! CAPTURA RESIDUO
        draw.text((580, 797), '{:,} KgCO2eq/ha'.format(datos['fertilizacion']*(-1)), font=ImageFont.truetype("arialbi.ttf", 15), fill=(226, 59, 59),
                  anchor='mm', align='center', spacing=12)  # ! CAPTURA FERTILZIACION VARIABLE

        nota = 'Se han calculado {} combinaciones de Fertilizantes para ajustar las necesidades del Cultivo.\nDe ellas se ha seleccionado la combinacion mas economica. Los fertilizantes con los que\nse ha analizado han sido: {}\n***Precios Fertilizantes a dia {}. Pueden sufrir Variacion***'.format(
            len(precios), formulas[:-4], datetime.today().strftime("%d/%m/%Y"))

        draw.text((50, 850),
                  nota, font=ImageFont.truetype("arial.ttf", 12), fill=color)

        

        
        self.p2 = img
    
    def panelTres(self):
        def modify(formula):
            # print(formula)
            pa = re.compile('^[0]')
            f = ''
            
            # formula = list(formula.split('-'))
            for e in formula:

                if re.match(pa, e):
                    e = e[1:]

                f = f + ' {}% -'.format(e)

            return f[:-1]

        pesos = self._pesos_aplicados
        precios = self._precios_ton
        x = 150
        y = 105
        font = self.font3
        font2 = ImageFont.truetype("arialbi.ttf", 14)
        color = self.color
        img = Image.open(self.path['base3'])
        draw = ImageDraw.Draw(img)
        total_unitario = 0
        formulas = ''
        datos = self.dataHuellaCarbono

        # print(pesos,precios)
        # for e,x in pesos,precios:
        #     print(e,x)


        if len(pesos) >= 1:
            f1 = self.formulas[0]
            f1 = modify(f1)
            formulas = formulas + f1 + ' --- '
            t1 = round(pesos[0]*self.area)/1000*precios[0]
            # print(t1)
            draw.text((140, y), '{}\n\n{:,}Kg/ha\n{:,}{}/ha\n\n{:,} Kg'.format(f1, pesos[0], round(
                t1/self.area),self.moneda, round(pesos[0]*self.area)), font=font2, fill=color, align='center', spacing=8)
            total_unitario = total_unitario + round(
                t1/self.area)

        if len(pesos) >= 2:
            f2 = self.formulas[1]
            f2 = modify(f2)
            formulas = formulas + f2 + ' --- '
            t2 = round(pesos[1]*self.area)/1000*precios[1]
            # print(t2)
            draw.text(((148*2)+10, y), '{}\n\n{:,}Kg/ha\n{:,}{}/ha\n\n{:,} Kg'.format(f2, pesos[1], round(
                t2/self.area), self.moneda, round(pesos[1]*self.area)), font=font2, fill=color, align='center', spacing=8)
            total_unitario = total_unitario + round(
                t2/self.area)

        if len(pesos) >= 3:
            f3 = self.formulas[2]
            f3 = modify(f3)
            formulas = formulas + f3 + ' --- '
            t3 = round(pesos[2]*self.area)/1000*precios[2]
            # print(t3)
            draw.text(((148*3)+20, y), '{}\n\n{:,}Kg/ha\n{:,}{}/ha\n\n{:,}Kg'.format(f3, pesos[2], round(
                t3/self.area), self.moneda, round(
                pesos[2]*self.area)), font=font2, fill=color, align='center', spacing=8)
            total_unitario = total_unitario + round(
                t3/self.area)

        if len(pesos) > 3:
            f4 = self.formulas[3]
            f4 = modify(f4)
            formulas = formulas + f4 + ' --- '
            t4 = round(pesos[3]*self.area)/1000*precios[3]
            # print(t4)
            draw.text(((148*4)+30, y), '{}\n\n{:,}Kg/ha\n{:,}{}/ha\n\n{:,}Kg'.format(f3, pesos[3], round(
                t4/self.area),self.moneda, round(
                pesos[3]*self.area)), font=font2, fill=color, align='center', spacing=8)
            total_unitario = total_unitario + round(
                t4/self.area)

        draw.text((340, 295),
                  '{:,} {}/ha'.format(total_unitario,self.moneda),
                  font=ImageFont.truetype("arialbi.ttf", 16),
                  fill=color,
                  align='center')
        draw.text((340, 345),
                  '{} Ha'.format(self.area),
                  font=ImageFont.truetype("arialbi.ttf", 16),
                  fill=color,
                  align='center')

        draw.text((600, 335),
                  '{} {:,}'.format(self.moneda,round(total_unitario*self.area)),
                  font=ImageFont.truetype("arialbi.ttf", 24),
                  fill=color)
        


        nota = 'Se han calculado {} combinaciones de Fertilizantes para ajustar las necesidades del Cultivo.\nDe ellas se ha seleccionado la combinacion mas economica. Los fertilizantes con los que\nse ha analizado han sido: {}\n***Precios Fertilizantes a dia {}. Pueden sufrir Variacion***'.format(
            len(precios), formulas[:-4], datetime.today().strftime("%d/%m/%Y"))

        draw.text((50, 630),
                  nota, font=ImageFont.truetype("arial.ttf", 12), fill=color)
        txt = 'Si hacemos las coseas BIEN, además\nde ahorrar Fertilizante, conseguimos un\n{}% de HUELLA DE CARBONO\nrepecto a seguir haciendolas como\nsiempre'.format(
            datos['percent'])
        draw = ImageDraw.Draw(img)
        draw.text((230, 525), txt,
                  font=ImageFont.truetype("arialbi.ttf", 16),
                  fill=self.color,
                  anchor='mm',
                  align='center',
                  spacing=10)  # ! TEXTO PANEL
        draw.text((560, 445), '{:,} KgCO2eq/ha'.format(datos['chc']), font=ImageFont.truetype("arialbi.ttf", 22), fill=(110, 178, 83),
                  anchor='mm', align='center', spacing=12)  # ! CAPTURA HUELLA DE CARBONO
        draw.text((650, 482), '{:,} KgCO2eq/ha'.format(datos['biomasa']), font=ImageFont.truetype("arialbi.ttf", 15), fill=(110, 178, 83),
                  anchor='mm', align='center', spacing=12)  # ! CAPTURA BIOMASA
        draw.text((670, 518), '{:,} KgCO2eq/ha'.format(datos['cosecha']), font=ImageFont.truetype("arialbi.ttf", 15), fill=(110, 178, 83),
                  anchor='mm', align='center', spacing=12)  # ! CAPTURA COSECHA
        draw.text((670, 555), '{:,} KgCO2eq/ha'.format(datos['residuo']), font=ImageFont.truetype("arialbi.ttf", 15), fill=(110, 178, 83),
                  anchor='mm', align='center', spacing=12)  # ! CAPTURA RESIDUO
        draw.text((650, 595), '{:,} KgCO2eq/ha'.format(datos['fertilizacion']*(-1)), font=ImageFont.truetype("arialbi.ttf", 15), fill=(226, 59, 59),
                  anchor='mm', align='center', spacing=12)  # ! CAPTURA FERTILZIACION VARIABLE

        self.p3 = img
        pass


    
    def showPanel(self):
        self.panelUno()
        self.img.show()

    def savePanel(self):
        
        self.panelUno()
        self.panelHuellaCarbono(self.dataHuellaCarbono)
        self.panelDos(self.i,self._pesos,self._precios)
        filename = QFileDialog.getExistingDirectory(
            None, "Seleccionar directorio de Paneles:")
        self.panelTres()
        self.p1.save(f'{filename}\\Panel00{self.lote}.png')
        self.p2.save(f'{filename}\\Panel02{self.lote}.png')
        self.p3.save(f'{filename}\\Panel01{self.lote}.png')
        self.phc.save((f'{filename}\\Panel03{self.lote}.png'))
        # self.p2.show()

        self.iface.messageBar().pushMessage(f'Paneles Exportado Correctamente <a href="{filename}">{filename}</a>', 3, 10)
        



