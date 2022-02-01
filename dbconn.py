import psycopg2

class DbConnection:
    def connection(dbname,dbuser,dbpass,dbhost,dbport='5432'):   
        try:
            conn = psycopg2.connect(f"dbname={dbname} user={dbuser} host={dbhost} password={dbpass} port={dbport}")
            # print('Conexión exitosa')
            return conn
        except:
            # print('Error de Conexión')
            pass
  
