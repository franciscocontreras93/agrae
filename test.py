
import pandas as pd
import numpy as np
import psycopg2

conn = psycopg2.connect("dbname=agrae user=postgres password=23826405 host=localhost")
cursor = conn.cursor()

cursor.execute(' select version()')

df = pd.read_csv(r"C:\Users\FRANCISCO\Desktop\reporte_16042022.csv",delimiter=';')
df1 = df.astype(object).replace(np.nan, 'NULL')
columns = [c for c in df.columns]
print(columns)

for index, row in df1.iterrows():
    _SQL = f'''INSERT INTO analisis.analitica (idsegmentoanalisis,ceap,ph,ce,carbon,caliza,ca,mg,k,na,n,p,organi,cox,rel_cn,ca_eq,mg_eq,k_eq,na_eq,cic,ca_f,mg_f,k_f,na_f,al,b,fe,mn,cu,zn,s,mo,arcilla,limo,arena,ni,co,ti,"as",pb,cr) VALUES ({row['id']},{row['ceap']},{row['pH']},{row['CE']},{row['CARBON']},{row['CALIZA']},{row['CA']},{row['MG']},{row['K']},{row['NA']},{row['N']},{row['P']},{row['ORGANI']},{row['COX']},{row['REL_CN']},{row['CA_EQ']},{row['MG_EQ']},{row['K_EQ']},{row['NA_EQ']},{row['CIC']},{row['CA_F']},{row['MG_F']},{row['K_F']},{row['NA_F']},{row['AL']},{row['B']},{row['FE']},{row['MN']},{row['CU']},{row['ZN']},{row['S']},{row['MO']},{row['ARCILLA']},{row['LIMO']},{row['ARENA']},{row['NI']},{row['CO']},{row['TI']},{row['AS']},{row['PB']},{row['CR']}); '''

    print(_SQL)   
    cursor.execute(_SQL)
    conn.commit()
    
        
