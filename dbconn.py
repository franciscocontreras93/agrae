import psycopg2

class DbConnection:
    def connection(dbname,dbuser,dbpass,dbhost,dbport):
        
        try:
            conn = psycopg2.connect(dbname=dbname,user=dbuser,host=dbhost, password=dbpass, port=dbport)
            # !DESCOMENTAR PARA DEBUGGEAR LA CONEXION A LA BD
            # with conn.cursor() as curs:
            #     curs.execute('select version()')
            #     print(curs.fetchone())
            return conn
        except Exception as ex:
             print(ex)

    connection('agrae', 'doadmin', 'hMElJYf5Lq5BjG4r', '137.184.106.142', 25060)


        
    
