from qgis.PyQt.QtCore import QSettings
from qgis.gui import QgsMessageBar
from .dbconn import DbConnection

class AgraeUtils():
    
    def __init__(self):
        
        self.s = QSettings('agrae','dbConnection')
        self.dns = {
            'host': self.s.value('dbhost'),
            'port': self.s.value('dbport'),
            'dbname': self.s.value('dbname'),
            'user': self.s.value('dbuser'),
            'password': self.s.value('dbpass')
        }
        self.conn = DbConnection.connection(self.dns['dbname'], self.dns['user'], self.dns['password'], self.dns['host'])

        pass

    def ConnParams(self):
        dns = self.dns
        return dns

    def Conn(self):
        conn = self.conn = DbConnection.connection(
            self.dns['dbname'], self.dns['user'], self.dns['password'], self.dns['host'])
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

    def dbTestConnection(self,dbname,dbuser,dbpass,dbhost,dbport=5432):     
        conn = DbConnection.connection(
            dbname, dbuser, dbpass, dbhost, dbport)
        conn.close()


 
  # def loadData():
        #     layer = self.iface.activeLayer()
        #     feature = layer.selectedFeatures()
        #     print(len(feature))
        #     try:
        #         self.addFeatureDialog.line_Nombre.setText(
        #             str(feature[0]['name_parc']))
        #         self.addFeatureDialog.line_Prov.setText(
        #             str(feature[0]['provincia']))
        #         self.addFeatureDialog.line_Mcpo.setText(
        #             str(feature[0]['municipio']))
        #         self.addFeatureDialog.line_Agregado.setText(
        #             str(feature[0]['agregado']))
        #         self.addFeatureDialog.line_Zona.setText(
        #             str(feature[0]['zona']))
        #         self.addFeatureDialog.line_Poly.setText(
        #             str(feature[0]['poligono']))
        #         self.addFeatureDialog.line_Parcela.setText(
        #             str(feature[0]['parcela']))
        #         self.addFeatureDialog.line_Recinto.setText(
        #             str(feature[0]['recinto']))
        #     except Exception as ex:
        #         if len(feature) == 0 or len(feature) >1:
        #             self.iface.messageBar().pushMessage(
        #                 f'aGraes GIS | {ex}: ', 'Debe seleccionar una Parcela', level=1, duration=3)

    #  def loadAllotmentToDB():

        # with self.conn as conn:
        #     try:

        #         cur = conn.cursor()
        #         layer = self.iface.activeLayer()
        #         # print(layer.name())
        #         feat = layer.selectedFeatures()
        #         ls = feat[0].geometry().asWkt()
        #         srid = layer.crs().authid()[5:]

        #         name = self.addFeatureDialog.line_Nombre.text()
        #         prov = self.addFeatureDialog.line_Prov.text()
        #         mcpo = self.addFeatureDialog.line_Mcpo.text()
        #         aggregate = self.addFeatureDialog.line_Agregado.text()
        #         zone = self.addFeatureDialog.line_Zona.text()
        #         poly = self.addFeatureDialog.line_Poly.text()
        #         allotment = self.addFeatureDialog.line_Parcela.text()
        #         inclosure = self.addFeatureDialog.line_Recinto.text()

        #         # print(ls)
        #         sql = f'''
        #         INSERT INTO parcela(nombre,provincia,municipio,agregado,zona,poligono,parcela,recinto,geometria)
        #         VALUES('{name}','{prov}','{mcpo}','{aggregate}','{zone}','{poly}','{allotment}','{inclosure}',st_multi(st_force2d(st_transform(st_geomfromtext('{ls}',{srid}),4326))))'''
        #         cur.execute(sql)
        #         conn.commit()
        #         # print('agregado correctamente')
        #         self.iface.messageBar().pushMessage(
        #             'aGraes GIS', 'Registro creado Correctamente', level=3, duration=3)

        #     except Exception as ex:
        #         print(ex)
        #         self.iface.messageBar().pushMessage(
        #             f'aGraes GIS | {ex}: ', 'No se pudo almacenar el registro', level=1, duration=3)




    

