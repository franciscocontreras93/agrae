from qgis.core import * 
from qgis.utils import iface

class agraeToolset():
    
    def __init__(self): 
        self.iface = iface

    def cargarAmbientes(self):
            # print('test')
            lyr = self.iface.activeLayer()
            srid = lyr.crs().authid()[5:]
            features = lyr.selectedFeatures()
            try:
                with self.conn as conn:
                    cursor = conn.cursor()
                    for f in features:
                        oa = f[1]
                        amb = f[0]
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
                        # print(sql)
                        cursor.execute(sql)
                        conn.commit()
                        QMessageBox.about(
                            self, 'aGrae GIS', 'Ambiente cargado Correctamente \na la base de datos')

            except Exception as ex:
                print(ex)
                pass
