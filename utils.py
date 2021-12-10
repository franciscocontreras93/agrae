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

 
            



    

