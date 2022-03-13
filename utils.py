import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication
from qgis.PyQt.QtCore import QSettings

from qgis.gui import QgsMessageBar
from qgis.utils import iface
from qgis.core import *

from psycopg2 import OperationalError, InterfaceError, errors, extras

import pandas as pd

from .dbconn import DbConnection

class AgraeUtils():
    
    def __init__(self):
        
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
            sql = f''' select s.idsegmento, l.idlote , ca.idcampania, l.nombre lote, s.segmento , (l.nombre||'-'||s.segmento) cod_control , 
            ca.fechasiembra, cu.nombre, a.cod_analisis 
            from segmento s 
            left join lote l on s.idlote = l.idlote 
            left join lotecampania lc on lc.idlote = l.idlote 
            left join campania ca on ca.idcampania = lc.idcampania 
            left join cultivo cu on cu.idcultivo = ca.idcultivo 
            left join segmentoanalisis sa on sa.idsegmento = s.idsegmento 
            left join analisis a on a.idanalisis = sa.idanalisis  
            where l.nombre ||'-'||s.segmento ilike '%{param}%'
            or a.cod_analisis ilike '%{param}%' 
            order by ca.idcampania desc '''
            return sql
        else: 
            sql = f''' select s.idsegmento, l.idlote , ca.idcampania, l.nombre lote, s.segmento , (l.nombre||'-'||s.segmento) cod_control , 
            ca.fechasiembra, cu.nombre, a.cod_analisis 
            from segmento s 
            left join lote l on s.idlote = l.idlote 
            left join lotecampania lc on lc.idlote = l.idlote 
            left join campania ca on ca.idcampania = lc.idcampania 
            left join cultivo cu on cu.idcultivo = ca.idcultivo 
            left join segmentoanalisis sa on sa.idsegmento = s.idsegmento 
            left join analisis a on a.idanalisis = sa.idanalisis   '''
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
        }

        return icons_path
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
        try:
            with self.conn as conn:
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
                        print(f'{oa}-{amb}-{ndvimax}-{atlas}')
                        cursor.execute(sql)
                        conn.commit()
                        
                    QMessageBox.about(widget, 'aGrae GIS', 'Ambiente Cargado Correctamente \na la base de datos')
                else:
                    QMessageBox.about(
                        widget, 'aGrae GIS', 'Debe Seleccionar al menos un ambiente')

        except Exception as ex:
            print(ex)
            pass
        
    def crearParcela(self,widget=None):
        count = 0
        _count = 0
        try:
            with self.conn as conn:
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
            print(ex)
            QMessageBox.about(widget, f"aGrae GIS", f"No se pudo almacenar el registro {ex}")
            conn.rollback()

    def renameParcela(self,widget): 
        lyr = QgsProject.instance().mapLayersByName('aGrae Parcelas')[0]
        nombreParcelario = str(widget.lineEdit_2.text())
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
                print('exitoso')
            else:
                pass

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
                print(f"Capa añadida correctamente ")
                widget.pushButton.setEnabled(False)

            else:
                QMessageBox.about(self, "aGrae GIS:",
                                    "La capa no es Valida")

        except Exception as ex:
            print(ex)
            QMessageBox.about(
                widget, f"Error:", f"Debe seleccionar un campo para el Nombre")

    def buscarLotes(self,widget,status):
        nombre = widget.line_buscar.text()
        sinceDate = widget.sinceDate.date().toString('yyyy-MM-dd')
        untilDate = widget.untilDate.date().toString('yyyy-MM-dd')

        sqlQuery = ''
        try: 
            with self.conn as conn:
                if nombre == '' and status == False:
                    sqlQuery = f'''select lc.idlotecampania , l.nombre lote, p.nombre parcela, ca.fechasiembra, ca.fechacosecha , cu.nombre cultivo 
                    from lotecampania lc
                    join loteparcela lp on lp.idlotecampania = lc.idlotecampania 
                    left join lote l on l.idlote = lc.idlote
                    left join parcela p on p.idparcela = lp.idparcela 
                    left join campania ca on ca.idcampania = lc.idcampania 
                    left join cultivo cu on cu.idcultivo = ca.idcultivo 
                    group by lc.idlotecampania , l.nombre , p.nombre , ca.fechasiembra , ca.fechacosecha , cu.nombre
                    order by ca.fechasiembra desc'''
                    widget.btn_add_layer.setEnabled(False)
                    

                elif nombre != '' and status == False:
                    sqlQuery = f"""select lc.idlotecampania , l.nombre lote, p.nombre parcela, ca.fechasiembra, ca.fechacosecha , cu.nombre cultivo 
                    from lotecampania lc
                    join loteparcela lp on lp.idlotecampania = lc.idlotecampania 
                    left join lote l on l.idlote = lc.idlote
                    left join parcela p on p.idparcela = lp.idparcela 
                    left join campania ca on ca.idcampania = lc.idcampania 
                    left join cultivo cu on cu.idcultivo = ca.idcultivo 
                    where l.nombre ilike '%{nombre}%' or p.nombre ilike '%{nombre}%' or cu.nombre ilike '%{nombre}%' 
                    group by lc.idlotecampania , l.nombre , p.nombre , ca.fechasiembra , ca.fechacosecha , cu.nombre
                    order by ca.fechasiembra desc                        
                    """
                    widget.btn_reload.setEnabled(True)

                elif nombre == '' and status == True:
                    sqlQuery = f"""select lc.idlotecampania , l.nombre lote, p.nombre parcela, ca.fechasiembra, ca.fechacosecha , cu.nombre cultivo 
                    from lotecampania lc
                    join loteparcela lp on lp.idlotecampania = lc.idlotecampania 
                    left join lote l on l.idlote = lc.idlote
                    left join parcela p on p.idparcela = lp.idparcela 
                    left join campania ca on ca.idcampania = lc.idcampania 
                    left join cultivo cu on cu.idcultivo = ca.idcultivo 
                    where ca.fechasiembra >= '{sinceDate}' and ca.fechasiembra <= '{untilDate}'
                    group by lc.idlotecampania , l.nombre , p.nombre , ca.fechasiembra , ca.fechacosecha , cu.nombre
                    order by ca.fechasiembra desc"""
                    widget.btn_reload.setEnabled(True)
                elif nombre != '' and status == True:
                    sqlQuery = f"""select lc.idlotecampania , l.nombre lote, p.nombre parcela, ca.fechasiembra, ca.fechacosecha , cu.nombre cultivo 
                    from lotecampania lc
                    join loteparcela lp on lp.idlotecampania = lc.idlotecampania 
                    left join lote l on l.idlote = lc.idlote
                    left join parcela p on p.idparcela = lp.idparcela 
                    left join campania ca on ca.idcampania = lc.idcampania 
                    left join cultivo cu on cu.idcultivo = ca.idcultivo 
                    where ca.fechasiembra >= '{sinceDate}' and ca.fechasiembra <= '{untilDate}'
                    or l.nombre ilike '%{nombre}%' or p.nombre ilike '%{nombre}%' or cu.nombre ilike '%{nombre}%' 
                    group by lc.idlotecampania , l.nombre , p.nombre , ca.fechasiembra , ca.fechacosecha , cu.nombre
                    order by ca.fechasiembra desc"""
                    widget.btn_reload.setEnabled(True)


                cursor = conn.cursor()
                cursor.execute(sqlQuery)
                data = cursor.fetchall()
                if len(data) == 0:
                    QMessageBox.about(
                        widget, "aGrae GIS:", "No existen registros con los parametros de busqueda")
                    widget.tableWidget.setRowCount(0)
                else:
                    widget.btn_add_layer.setEnabled(True)
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
            print(ex)
            QMessageBox.about(widget, "Error:", f"Verifica el Parametro de Consulta (ID o Nombre)") 
    
    
    def cargarLote(self,widget):
        selected = widget.tableWidget.selectionModel().selectedRows()
        dns = self.dns

        if len(selected) == 0: 
            msg = 'Debes seleccionar un lote'
            QMessageBox.about(widget, "aGrae GIS:", f"{msg}")
        elif len(selected) >1: 
            msg = 'Debes seleccionar solo un loteS'
            QMessageBox.about(widget, "aGrae GIS:", f"{msg}")
        else:          
            row = widget.tableWidget.currentRow()
            column = widget.tableWidget.currentColumn()
           
            try:
                idlote = widget.tableWidget.item(row, 0)
                nombreLote = widget.tableWidget.item(row, 1)
                nombreParcela = widget.tableWidget.item(row, 2)
                fecha = widget.tableWidget.item(row, 3)
                sql = sql = f''' select * from lotes
                where idlotecampania = {idlote.text()} and lote ilike '%{nombreLote.text()}%' and parcela ilike'%{nombreParcela.text()}%' and fechasiembra = '{fecha.text()}' '''
                uri = self.retUri(sql, 'geometria', 'idlotecampania')
                
                nombreCapa = f'{nombreLote.text()}-{nombreParcela.text()}-{widget.tableWidget.item(row, 5).text()}'
                layer = self.iface.addVectorLayer(uri.uri(False), nombreCapa, 'postgres')
                    
                if layer is not None and layer.isValid():
                    QgsProject.instance().addMapLayer(layer)
                    self.iface.setActiveLayer(layer)
                    self.iface.zoomToActiveLayer()
                    print(f"Capa añadida correctamente ")
                else:
                    QMessageBox.about(widget, "aGrae GIS:", "Capa invalida.")
            
            except Exception as ex:
                print(ex)
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
        except Exception as ex: 
            print(ex)
            pass


    def lastCode(self): 
        with self.conn as conn: 
            cursor = conn.cursor()
            try: 
                sql = '''select a.cod_analisis  from analisis a 
                        order by a.idanalisis desc limit 1'''
                cursor.execute(sql)
                code = cursor.fetchone()
                if len(code) > 0: 
                    return code[0]
                else: 
                    code = 'NO DATA'
            except Exception as ex:

                print(ex)
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
        fondoAjustado = float(widget.line_fondo_ajustado.text())
        fondoAplicado = float(widget.line_fondo_aplicado.text())
        dateCob1 = widget.date_cob.date().toString('yyyy.MM.dd')
        cob1Formula = widget.line_cob_formula.text()
        cob1Precio = float(widget.line_cob_precio.text())
        cob1Calculado = float(widget.line_cob_calculado.text())
        cob1Ajustado = float(widget.line_cob_ajustado.text())
        cob1Aplicado = float(widget.line_cob_aplicado.text())
        dateCob2 = widget.date_cob_2.date().toString('yyyy.MM.dd')
        cob2Formula = widget.line_cob_formula_2.text()
        cob2Precio = float(widget.line_cob_precio_2.text())
        cob2Calculado = float(widget.line_cob_calculado_2.text())
        cob2Ajustado = float(widget.line_cob_ajustado_2.text())
        cob2Aplicado = float(widget.line_cob_aplicado_2.text())
        dateCob3 = widget.date_cob_3.date().toString('yyyy.MM.dd')
        cob3Formula = widget.line_cob_formula_3.text()
        cob3Precio = float(widget.line_cob_precio_3.text())
        cob3Calculado = float(widget.line_cob_calculado_3.text())
        cob3Ajustado = float(widget.line_cob_ajustado_3.text())
        cob3Aplicado = float(widget.line_cob_aplicado_3.text())
        unidadDesprecio = widget.ln_und_deprecio.text()
      
        sql = f'''
        insert into campania 
        values(nextval('campania_idcampania_seq') ,{idexp}, {idcult},'{dateSiembra}','{dateCosecha}', '{dateFondo}','{fondoFormula}',{fondoPrecio}, {fondoCalculado}, {fondoAjustado},  {fondoAplicado}, '{dateCob1}', '{cob1Formula}', {cob1Precio},  {cob1Calculado}, {cob1Ajustado},  {cob1Aplicado}, '{dateCob2}',  '{cob2Formula}',  {cob2Precio},   {cob2Calculado},  {cob2Ajustado}, {cob2Aplicado}, '{dateCob3}',  '{cob3Formula}', {cob3Precio},  {cob3Calculado}, {cob3Ajustado},  {cob3Aplicado} , '{unidadDesprecio}');
        '''

        sql2 = f'''insert into lotecampania(idlote,idcampania) 
        select ql.idlote, qc.idcampania from (select idlote from lote where nombre = '{lote}') as ql, (select idcampania from campania order by idcampania desc limit 1) as qc; '''
       
        with self.conn as conn:
            try: 
                cursor = conn.cursor()
                cursor.execute(sql)
                conn.commit()
                cursor.execute(sql2)
                conn.commit()
                QMessageBox.about(widget, f"aGrae GIS:",f"Campaña creada y asociada correctamente")
            except InterfaceError as ie: 
                conn = widget.utils.Conn()
                cursor = conn.cursor()
                cursor.execute(sql)
                QMessageBox.about(widget, f"aGrae GIS:", f"Campaña creada correctamente")


            except Exception as e: 
                print(e)
                QMessageBox.about(widget, f"Error: ",f"{e}")         
    
    def crearLote(self,widget):
        nombre = str(widget.line_lote_nombre.text()).upper()
        sql = f""" insert into lote(nombre) values('{nombre}')  """
        with widget.conn as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                print('Lote creado')
                QMessageBox.about(
                    widget, f"aGrae GIS:", f"Lote: {nombre} Creado Correctamente.\nCrear una campaña para continuar.")
            except errors.lookup('23505'):
                # print('El lote ya existe, ingresa otro nombre o modifica el existente')
                QMessageBox.about(
                    widget, f"aGrae GIS:", f"El Lote: {nombre} ya existe.\nIngresa otro Nombre o Modifica el Existente")
                conn.rollback()
                widget.line_lote_nombre.setText('')
                # widget.line_lote_nombre.setEnabled(False)

            except Exception as ex:
                print(ex)
                QMessageBox.about(
                    widget, f"ERROR:", f"Ocurrio un Error")
                conn.rollback()
                widget.line_lote_nombre.setText('')
                # widget.line_lote_nombre.setEnabled(False)
