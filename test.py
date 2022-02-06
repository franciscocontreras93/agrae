import psycopg2.extras
import psycopg2
import random
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
# import warnings
# warnings.filterwarnings(action='once')

sns.set_style('darkgrid')
conn = psycopg2.connect(
    'host=localhost dbname=agrae user=postgres password=23826405')
cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
cursor.execute(
    'select nombre , st_area(st_transform(geometria,25830))/10000  from parcela')
# data = [r[1] for r in cursor.fetchall()]
result = cursor.fetchall()
nombre = [e[0] for e in result]
data = [e[1] for e in result]

print(nombre, data)


# ypos = np.arange(len(nombre))
# plt.xticks(ypos, nombre)
# plt.ylabel('Area Parcela (Ha)')
# plt.bar(ypos, data)

sns.barplot(nombre,data)

plt.show()\
# plt.savefig(r'C:\Users\FRANCISCO\Desktop\demo.png')
