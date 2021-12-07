import psycopg2

class DbConnection:
    def connection(dbname,dbuser,dbpass,dbhost):   
        try:
            conn = psycopg2.connect(f"dbname={dbname} user={dbuser} host={dbhost} password={dbpass}")
            print('Conexión exitosa')
            return conn
        except:
            print('Error de Conexión')
  
