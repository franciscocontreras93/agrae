import psycopg2
import psycopg2.extras

conn = psycopg2.connect('dbname=agrae user=postgres host=localhost password=23826405')
cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

query = 'select * from public.lotes' 

cursor.execute(query=query)
rc = cursor.rowcount
results = cursor.fetchall()
for r in results: 
    print('ID: {}'.format(r['id']))