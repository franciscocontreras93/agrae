from .dbconn import DbConnection

class AgraeUtils:
    def __init__(self):

        pass

    def ConnParams(self):
        dns = {
            'host':'localhost',
            'port': '5432',
            'dbname':'agrae',
            'user': 'postgres',
            'password':'23826405'
                }
        return dns
    def loadGeomLayers(self):
        conn = DbConnection.connection(
            'agrae', 'postgres', '23826405', 'localhost')
        with conn:
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
        conn = DbConnection.connection(
            'agrae', 'postgres', '23826405', 'localhost')
        with conn:
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

    
