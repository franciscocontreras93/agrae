from osgeo import gdal, gdal_array, osr
from qgis import processing
from qgis.core import *

import numpy as np
import jenkspy
import tempfile
import time


class agraeVerisAlgorithm():

    def __init__(self, verisFile, bar, segmento='memory:Segmentos'):

        self.verisFile = verisFile
        self.bar = bar
        self.f = QgsProcessingFeedback()
        self.f.progressChanged.connect(self.progress_changed)
        self.out = segmento


        pass

    def jenks(self, values: list, n_class=3):
        ''' TABLE STRUCTURE = [MIN-MAX-VALUE] '''
        try:
            if n_class == 2:
                j = jenkspy.jenks_breaks(values, nb_class=n_class)
                table = [j[0], j[1], 1, j[1], j[2], 2]
                return table, j
            if n_class == 3:
                j = jenkspy.jenks_breaks(values, nb_class=n_class)
                table = [j[0], j[1], 1, j[1], j[2], 2, j[2], j[3], 3]
                return table, j
        except ValueError as err:
            print(
                f'Number of class have to be an integer greater than 2\nand smaller than the number of values to use, {type(err)}')
    #        print(f'Unexpected {err}, {type(err)}')
            return(None)

    def progress_changed(self, progress):
        #print(progress)
        self.bar.setValue(progress)

    def processVerisData(self, n_clases):
        path = self.verisFile
        process = {}
        output = {}
        uri = f'file:///{path}?type=csv&delimiter=%5Ct&useHeader=No&maxFields=10000&detectTypes=yes&xField=field_1&yField=field_2&crs=EPSG:4326&spatialIndex=yes&subsetIndex=no&watchFile=no'
        verisData = QgsVectorLayer(uri, 'Veris DAT', 'delimitedtext')
        alg_params = {
            'INPUT': verisData,
            'EXPRESSION': 'field_3 > 0.01',
            'OUTPUT': 'TEMPORARY_OUTPUT'
        }
        process['filter'] = processing.run(
            "native:extractbyexpression", alg_params,feedback=self.f)
        output['filter'] = process['filter']['OUTPUT']
        alg_params = {
            'INPUT': output['filter'],
            'Z_FIELD': 'field_3',
            'POWER': 2,
            'SMOOTHING': 8,
            'RADIUS': 50,
            'MAX_POINTS': 32,
            'MIN_POINTS': 8,
            'NODATA': 0,
            'OPTIONS': '',
            'EXTRA': '',
            'DATA_TYPE': 5,
            'OUTPUT': f'{tempfile.gettempdir()}\idw.tif'}
        process['idw'] = processing.run(
            "gdal:gridinversedistancenearestneighbor", alg_params,feedback=self.f)
        output['idw'] = QgsRasterLayer(process['idw']['OUTPUT'], 'idw')
        dataset = gdal.Open(output['idw'].source())
        band = dataset.GetRasterBand(1)
        nodata = band.GetNoDataValue()
        array = dataset.ReadAsArray()
        new_array = array
        nan_array = array
        nan_array[array == nodata] = np.nan
        array = np.unique(nan_array)
        table, j = self.jenks(array, n_clases)
        alg_params = {'INPUT_RASTER': output['idw'],
                      'RASTER_BAND': 1,
                      'TABLE': table,
                      'NO_DATA': -9999,
                      'RANGE_BOUNDARIES': 0,
                      'NODATA_FOR_MISSING': False,
                      'DATA_TYPE': 5,
                      'OUTPUT': f'{tempfile.gettempdir()}\idw_reclass.tif'}
        process['reclass'] = processing.run(
            "native:reclassifybytable", alg_params,feedback=self.f)
        output['reclass'] = QgsRasterLayer(
            process['reclass']['OUTPUT'], 'idw Reclasificado')

        alg_params = {
            'INPUT': output['reclass'],
            'BAND': 1,
            'FIELD': 'segmento',
            'EIGHT_CONNECTEDNESS': False,
            'EXTRA': '',
            'OUTPUT': f'TEMPORARY_OUTPUT'
        }
        process['polygonize'] = processing.run("gdal:polygonize", alg_params,feedback=self.f)
        output['polygonize'] = process['polygonize']['OUTPUT']

        alg_params = {
            'INPUT': output['polygonize'],
            'OUTPUT': 'TEMPORARY_OUTPUT'}
        process['fixgeometries'] = processing.run(
            "native:fixgeometries", alg_params,feedback=self.f)
        output['fixgeometries'] = process['fixgeometries']['OUTPUT']

        alg_params = {
            'INPUT': output['fixgeometries'],
            'FIELD': ['segmento'],
            'OUTPUT': 'TEMPORARY_OUTPUT'}
        process['dissolve'] = processing.run("native:dissolve", alg_params,feedback=self.f)
        output['dissolve'] = process['dissolve']['OUTPUT']

        alg_params = {
            'INPUT': output['dissolve'],
            'OUTPUT': 'TEMPORARY_OUTPUT'
        }
        process['multiparttosingleparts'] = processing.run(
            "native:multiparttosingleparts", alg_params,feedback=self.f)
        output['multiparttosingleparts'] = process['multiparttosingleparts']['OUTPUT']
    #    values = [f[0] for f in lyr.getFeatures()]
    #    values = list(set(values))
    #    print(values)
        alg_params = {
            'INPUT': output['multiparttosingleparts'],
            'EXPRESSION': '$area < 1000',
            'METHOD': 0}
        process['selectbyexpression'] = processing.run(
            "qgis:selectbyexpression", alg_params,feedback=self.f)
        alg_params = {
            'INPUT': output['multiparttosingleparts'],
            'MODE': 0,
            'OUTPUT': 'TEMPORARY_OUTPUT'
        }
        process['eliminateselectedpolygons'] = processing.run(
            "qgis:eliminateselectedpolygons", alg_params,feedback=self.f)
        output['eliminateselectedpolygons'] = process['eliminateselectedpolygons']['OUTPUT']

        alg_params = {
            'INPUT': output['eliminateselectedpolygons'],
            'FIELD': ['segmento'],
            'OUTPUT': 'TEMPORARY_OUTPUT'}
        process['dissolve2'] = processing.run("native:dissolve", alg_params,feedback=self.f)
        output['dissolve2'] = process['dissolve2']['OUTPUT']
        alg_params = {
            'INPUT': output['dissolve2'],
            'INPUT_RASTER': output['idw'],
            'RASTER_BAND': 1,
            'COLUMN_PREFIX': 'ceap',
            'STATISTICS': [3],
            'OUTPUT': 'TEMPORARY_OUTPUT'
        }
        process['zonalstatisticsfb'] = processing.run(
            "native:zonalstatisticsfb", alg_params,feedback=self.f)
        output['zonalstatisticsfb'] = process['zonalstatisticsfb']['OUTPUT']
        alg_params = {
            'INPUT': output['zonalstatisticsfb'],
            'FIELDS_MAPPING': [{'expression': '\"segmento\"',
                                'length': 0,
                                'name': 'segmento',
                                'precision': 0,
                                'type': 2},
                               {'expression': '\"ceapmedian\"',
                                'length': 0,
                                'name': 'ceap',
                                'precision': 0,
                                'type': 6}],
            'OUTPUT': 'TEMPORARY_OUTPUT'
        }
        process['refactorfields'] = processing.run(
            "native:refactorfields", alg_params,feedback=self.f)
        output['refactorfields'] = process['refactorfields']['OUTPUT']
        


        alg_params = {
            'INPUT': verisData,
            'EXPRESSION': 'field_1 = minimum(field_1) or field_1 = maximum(field_1) or field_2 = minimum(field_2) or field_2 = maximum(field_2)',
            'OUTPUT': 'TEMPORARY_OUTPUT'
        }
        
        process['vertex'] = processing.run(
            "native:extractbyexpression", alg_params, feedback=self.f)
        output['vertex'] = process['vertex']['OUTPUT']

        

        alg_params = {'INPUT': output['vertex'],
                      'FIELD_NAME': 'order', 
                      'FIELD_TYPE': 1, 
                      'FIELD_LENGTH': 0, 
                      'FIELD_PRECISION': 0, 
                      'FORMULA': 'case\r\nwhen field_2 = maximum(field_2) then 0\r\nwhen field_1= maximum(field_1) then 1\r\nwhen field_2 = minimum(field_2) then 2\r\nwhen field_1 = minimum(field_1) then 3\r\nend', 
                      'OUTPUT': 'TEMPORARY_OUTPUT'}

        process['orderVertex'] = processing.run("native:fieldcalculator", alg_params, feedback=self.f )
        output['orderVertex'] = process['orderVertex']['OUTPUT']

        
        
        alg_params = {'INPUT': output['orderVertex'],
         'CLOSE_PATH': True, 
         'ORDER_FIELD': 'order', 
         'GROUP_FIELD': '', 
         'DATE_FORMAT': '', 
         'OUTPUT': 'TEMPORARY_OUTPUT'}
        process['pointstopath'] = processing.run("qgis:pointstopath", alg_params, feedback=self.f)
        output['pointstopath'] = process['pointstopath']['OUTPUT']
        
        
        alg_params = {
            'INPUT': output['pointstopath'], 
            'OUTPUT': 'TEMPORARY_OUTPUT'}
        process['linestopolygons'] = processing.run("qgis:linestopolygons",  alg_params, feedback=self.f)
        output['linestopolygons'] = process['linestopolygons']['OUTPUT']
        
        
        alg_params = {
            'INPUT': output['linestopolygons'], 
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:3857'), 
            'OPERATION': '+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84', 
            'OUTPUT': 'TEMPORARY_OUTPUT'}
        process['reprojectlayer'] = processing.run("native:reprojectlayer", alg_params, feedback=self.f)
        output['reprojectlayer'] = process['reprojectlayer']['OUTPUT']
        

        alg_params = {
            'INPUT': output['reprojectlayer'],
            'DISTANCE': 3, 
            'SEGMENTS': 5, 
            'END_CAP_STYLE': 1, 
            'JOIN_STYLE': 1, 
            'MITER_LIMIT': 2, 
            'DISSOLVE': False, 
            'OUTPUT': 'TEMPORARY_OUTPUT'}
        process['buffer'] = processing.run("native:buffer", alg_params, feedback=self.f )
        output['buffer'] = process['buffer']['OUTPUT']
        
        alg_params = {
            'INPUT': output['buffer'], 
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:4326'), 
            'OPERATION': '+proj=pipeline +step +inv +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84 +step +proj=unitconvert +xy_in=rad +xy_out=deg', 
            'OUTPUT': 'TEMPORARY_OUTPUT'}
        process['reprojectlayer2']=  processing.run("native:reprojectlayer", alg_params, feedback=self.f)
        output['reprojectlayer2'] = process['reprojectlayer2']['OUTPUT']
        
        alg_params = {
            'INPUT': output['refactorfields'],
            'OVERLAY': output['reprojectlayer2'], 
            'OUTPUT': self.out}
        process['clip'] = processing.run("native:clip", alg_params, feedback=self.f)
        output['clip'] = process['clip']['OUTPUT']
        





    #    print(j)
        if self.out != 'memory:Segmentos':
            lyr = QgsVectorLayer(self.out, 'Segmentos', 'ogr')
        else:
            lyr = output['clip']

        # print(output['vertex'])
        QgsProject.instance().addMapLayer(lyr)


# path = r'C:/Users/FRANCISCO/Downloads/VSEC_ARY05.DAT'

# alg = agraeAlgorithm(path)
# alg.processVerisData(3)
