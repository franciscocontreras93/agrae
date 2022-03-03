from PyQt5.QtWidgets import *
from qgis.PyQt.QtCore import QSettings

from qgis.gui import QgsMessageBar
from qgis.utils import iface
from qgis.core import *

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
            sql = f''' select p.nombre parcela, l.nombre lote , s.cod_control, a.cod_analisis , s.geometria from segmento s
                left join segmentoanalisis sa on s.idsegmento = sa.idsegmento 
                left join analisis a on a.idanalisis = sa.idanalisis 
                left join parcela p on p.idparcela = s.idparcela
                left join lote l on l.idlote = s.idlote 
                where a.cod_analisis ilike '%{param}%' or l.nombre ilike '%{param}%' or s.cod_control ilike '%{param}%' '''
            return sql
        else: 
            sql = f''' select p.nombre parcela, l.nombre lote , s.cod_control, a.cod_analisis , s.geometria from segmento s
                left join segmentoanalisis sa on s.idsegmento = sa.idsegmento 
                left join analisis a on a.idanalisis = sa.idanalisis 
                left join parcela p on p.idparcela = s.idparcela
                left join lote l on l.idlote = s.idlote '''
            return sql
    def sqlLoteParcela(self,idlote): 
        sql = f'''select p.idparcela , l.idlote, l.nombre lote, p.nombre parcela, l.fechasiembra,l.fechacosecha, c.nombre cultivo, p.geometria 
        from parcela p 
        left join loteparcela lp on p.idparcela = lp.idparcela 
        left join lote l on l.idlote = lp.idlote 
        left join cultivo c on c.idcultivo = l.idcultivo 
        where p.idparcela in(lp.idparcela) and l.idlote = {idlote} order by p.nombre '''
        return sql

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
        
    def crearParcela(self,widget):
        try:
            with self.conn as conn:
                cur = conn.cursor()
            layer = self.iface.activeLayer()
            # print(layer.name())
            feat = layer.selectedFeatures()
            ls = feat[0].geometry().asWkt()
            srid = layer.crs().authid()[5:]

            name = str(widget.ln_par_nombre.text())
            prov = int(widget.prov_combo.currentData())
            mcpo = int(widget.mcpo_combo.currentData())
            aggregate = int(widget.ln_par_agg.text())
            zone = int(widget.ln_par_zona.text())
            poly = int(widget.ln_par_poly.text())
            allotment = int(widget.ln_par_parcela.text())
            inclosure = int(widget.ln_par_recinto.text())
            # print(ls)

            sql = f'''INSERT INTO parcela(nombre,provincia,municipio,agregado,zona,poligono,parcela,recinto,geometria) VALUES('{name}',{prov},{mcpo},{aggregate},{zone},{poly},{allotment},{inclosure},st_multi(st_force2d(st_transform(st_geomfromtext('{ls}',{srid}),4326))))'''
            cur.execute(sql)
            conn.commit()
            print('agregado correctamente')
            QMessageBox.about(widget, f"aGrae GIS:",
                                f"Parcela *-- {name} --* Creada Correctamente.\nCrear Relacion Lote Parcelas.")



        except IndexError as ie:
            QMessageBox.about(widget, f"aGrae GIS {ie}", f"Debe Seleccionar una parcela a cargar.")

        except Exception as ex:
            print(ex)
            QMessageBox.about(widget, f"aGrae GIS", f"No se pudo almacenar el registro {ex}")

        finally:
            widget.ln_par_nombre.setText('')
            # widget.ln_par_provincia.setText('')
            # widget.ln_par_mcpo.setText('')
            widget.ln_par_agg.setText('0')
            widget.ln_par_zona.setText('0')
            widget.ln_par_poly.setText('0')
            widget.ln_par_parcela.setText('0')
            widget.ln_par_recinto.setText('0')

    def cargarParcela(self,widget):
        self.sqlParcela = widget.sqlParcela
        sql = self.sqlParcela
        dns = self.dns
        row = widget.tableWidget.currentRow()
        column = widget.tableWidget.currentColumn()
        try:
            uri = QgsDataSourceUri()
            uri.setConnection(dns['host'], dns['port'],
                                dns['dbname'], dns['user'], dns['password'])
            uri.setDataSource('', f'({sql})', 'geometria', '', 'idparcela')
            nombre = widget.ln_par_nombre.text()
            if nombre == None:
                nombre = widget.ln_par_nombre.text()
                layer = self.iface.addVectorLayer(
                    uri.uri(False), nombre, 'postgres')
            else:
                layer = self.iface.addVectorLayer(
                    uri.uri(False), nombre, 'postgres')

            if layer.isValid():
                QgsProject.instance().addMapLayer(layer)
                self.iface.setActiveLayer(layer)
                self.iface.zoomToActiveLayer()
                print(f"Capa añadida correctamente ")
                widget.pushButton.setEnabled(False)

            else:
                # uri.setDataSource('public', tablename, None)
                # layer = QgsVectorLayer(
                #     uri.uri(False), tablename, 'postgres')
                # QgsProject.instance().addMapLayer(layer)
                QMessageBox.about(self, "aGrae GIS:",
                                    "La capa no es Valida")

        except Exception as ex:
            QMessageBox.about(
                widget, f"Error:{ex}", f"Debe seleccionar un campo para el Nombre")




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





