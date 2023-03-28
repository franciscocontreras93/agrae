from osgeo import gdal
from qgis import processing
from qgis.core import *
from qgis.utils import iface

import numpy as np
import jenkspy
import tempfile


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
                j = jenkspy.jenks_breaks(values, nb_class=n_class) #n_classes for v0.3.1
                table = [j[0], j[1], 1, j[1], j[2], 2]
                return table, j
            if n_class == 3:
                j = jenkspy.jenks_breaks(values, nb_class=n_class) #n_classes for v0.3.1
                table = [j[0], j[1], 1, j[1], j[2], 2, j[2], j[3], 3]
                return table, j
        except ValueError as err:
            print(
                f'Number of class have to be an integer greater than 2\nand smaller than the number of values to use, {type(err)}')
    #        print(f'Unexpected {err}, {type(err)}')
            return(None)

    def quantile(self,values:list, n_class=3) :
        
        if n_class == 3:
            min = np.min(values)
            q1 = np.percentile(values,25)
            q2 = np.percentile(values,50)
            q3 = np.percentile(values,75)
            max = np.max(values)
        print(min,q1,q2,q3,max)
            
        
        pass
    
    def progress_changed(self, progress):
        #print(progress)
        self.bar.setValue(progress)
    def style(self,segmentos,veris): 
        segmentos_layer = segmentos
        field_name = 'segmento'
        field_index = segmentos_layer.fields().indexFromName(field_name)
        unique_values = segmentos_layer.uniqueValues(field_index)
        category_list = []
        for value in unique_values:
            symbol = QgsSymbol.defaultSymbol(segmentos_layer.geometryType())
            category = QgsRendererCategory(value, symbol, str(value))
            category_list.append(category)
        renderer = QgsCategorizedSymbolRenderer(field_name, category_list)
        style = QgsStyle().defaultStyle()
        ramp = style.colorRamp('Spectral')
        renderer.updateColorRamp(ramp)
        segmentos_layer.setRenderer(renderer)
        segmentos_layer.triggerRepaint()

        veris_layer = veris
        veris_layer.renderer().symbol().setSize(2)
        veris_layer.renderer().symbol().symbolLayer(0).setShape(
            QgsSimpleMarkerSymbolLayerBase.Cross)
        veris_layer.triggerRepaint()


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
        # self.quantile(nan_array)
        # return None
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
            'FIELD': '', 
            'TYPE': 3, 
            'OUTPUT': 'TEMPORARY_OUTPUT'}
        process['minimumboundinggeometry'] = processing.run("qgis:minimumboundinggeometry", alg_params, feedback=self.f)
        output['minimumboundinggeometry'] = process['minimumboundinggeometry']['OUTPUT']      
        
        alg_params = {
            'INPUT': output['minimumboundinggeometry'],
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

        processing.run("native:createspatialindex", {'INPUT': output['refactorfields']})
        
        alg_params = {
            'INPUT': output['refactorfields'],
            'OVERLAY': output['reprojectlayer2'], 
            'OUTPUT': self.out}
        process['clip'] = processing.run("native:clip", alg_params, feedback=self.f)
        output['clip'] = process['clip']['OUTPUT']



        

        if self.out != 'memory:Segmentos':
            lyr = QgsVectorLayer(self.out, 'Segmentos', 'ogr')
        else:
            lyr = output['clip']

        # print(output['vertex'])
        QgsProject.instance().addMapLayer(lyr)
        QgsProject.instance().addMapLayer(verisData)
        self.style(lyr,verisData)

        process = {}
        output = {}



class agraeVerifyAlgorithm():
   
    def __init__(self,bar):
        """
        aGrae Algoritmo de Verificacion de Capas: 
            Verifica la integridad de las geometrias de una capa para su inclusion en la Base de Datos

        """      
        self.bar = bar
        self.f = QgsProcessingFeedback()
        self.f.progressChanged.connect(self.progress_changed)

        pass
    def progress_changed(self, progress):
        # print(progress)
        self.bar.setValue(progress)


    def verifySegmento(self,layer,field,grid_size,layer_lotes):
        """_summary_

        Args:
            layer (QgsVectorLayer): _description_
            field (QgsField): _description_
            grid_size (Integer): _description_
            layer_lotes (QgsVectorLayer): _description_

        Returns:
            _type_: _description_
        """      
        # process = {}
        try:
        
            layer_data = layer
            lotes = [f for f in layer_lotes.getFeatures()]
            buffer_lyrs = []
            lotes_lyrs = []
           
            process = {}
            for f in lotes:
                
                nombre = f['lote']
                loteLyr = QgsVectorLayer('Polygon?crs=epsg:4326', f['lote'],"memory")
                provider = loteLyr.dataProvider() 
                provider.addFeature(f)
                lotes_lyrs.append(loteLyr)
                params = {'INPUT':loteLyr,
                'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:3857'),
                'OPERATION':'+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
                'OUTPUT':'TEMPORARY_OUTPUT'}
                reproject_process = processing.run("native:reprojectlayer",params ,feedback=self.f)
                reprojected = reproject_process['OUTPUT']
                params = {
                'INPUT':reprojected,
                'DISTANCE':10,
                'SEGMENTS':5,
                'END_CAP_STYLE':1,
                'JOIN_STYLE':1,
                'MITER_LIMIT':2,
                'DISSOLVE':False,
                'OUTPUT':'TEMPORARY_OUTPUT'}
                buffer_process = processing.run("native:buffer",params,feedback=self.f)
                buffer = buffer_process['OUTPUT']
                buffer.setName(nombre)
                buffer_lyrs.append(buffer)
            #    QgsProject.instance().addMapLayer(buffer)
                
            #print(buffer_lyrs)
            procesadas = []
            for buffer,lote in zip(buffer_lyrs,lotes_lyrs):
                nombre = buffer.name()
                params = {
                    'TYPE':2,
                    'EXTENT':buffer,
                    'HSPACING':grid_size,
                    'VSPACING':grid_size,
                    'HOVERLAY':0,
                    'VOVERLAY':0,
                    'CRS':QgsCoordinateReferenceSystem('EPSG:3857'),
                    'OUTPUT':'TEMPORARY_OUTPUT'}
                process['grid'] = processing.run("native:creategrid",params,feedback=self.f)
                grid = process['grid']['OUTPUT']
                params = {'INPUT':grid,
                        'JOIN':layer_data,
                        'PREDICATE':[0],
                        'JOIN_FIELDS':field,
                        'METHOD':1,
                        'DISCARD_NONMATCHING':True,
                        'PREFIX':'',
                        'OUTPUT':'TEMPORARY_OUTPUT'}
                process['gridjoin']=processing.run("native:joinattributesbylocation",params,feedback=self.f)
                gridJoin = process['gridjoin']['OUTPUT']
                params = {'INPUT':gridJoin,
                        'FIELD':[field],
                        'OUTPUT':'TEMPORARY_OUTPUT'}
                process['gridDisolve'] = processing.run("native:dissolve",params,feedback=self.f)
                gridDisolve = process['gridDisolve']['OUTPUT']
                
                params = {
                    'INPUT': gridDisolve,
                    'OVERLAY': lote, 
                    'OUTPUT': 'TEMPORARY_OUTPUT'}
                
                process['clip'] = processing.run("native:clip", params, feedback=self.f)
                clipped = process['clip']['OUTPUT']
                
                params =  {'INPUT':clipped,'COLUMN':['left','top','right','bottom'],'OUTPUT':'TEMPORARY_OUTPUT'}
                process['removeFields'] = processing.run("qgis:deletecolumn", params,feedback=self.f)
                removeFields = process['removeFields']['OUTPUT']
                removeFields.setName(nombre)
                procesadas.append(removeFields)
                

            params = {
            'LAYERS':procesadas,
            'CRS':QgsCoordinateReferenceSystem('EPSG:25832'),
            'OUTPUT':'TEMPORARY_OUTPUT'}

            unificar  = processing.run("native:mergevectorlayers",params,feedback=self.f )

            
            params =  {'INPUT':unificar['OUTPUT'],'COLUMN':['layer','path'],'OUTPUT':'TEMPORARY_OUTPUT'}
            limpiar_process = processing.run("qgis:deletecolumn", params,feedback=self.f)
            removeFields = limpiar_process['OUTPUT']              
            duplicates = processing.run("native:deleteduplicategeometries", {'INPUT':removeFields,'OUTPUT':'TEMPORARY_OUTPUT'})   
            verificada  = duplicates['OUTPUT']
            verificada = processing.run("native:renametablefield", {'INPUT':verificada,'FIELD':'SEGM','NEW_NAME':'segmento','OUTPUT':'TEMPORARY_OUTPUT'}) 
            verificada = verificada['OUTPUT']
            verificada.setName(f'{layer_data.name()}_Verificada')
            
            return verificada

        except Exception as ex: 
            # QgsMessageLog.logMessage(f'{ex} \nError ejecutando el proceso VerifyLayer', 'aGrae GIS', level=1)
            # QMessageBox.about(self,'aGrae GIS', 'Ocurrio un error, revisa el panel de mensajes de registros')
            print(ex)

    def verifyAmbiente(self,layer,grid_size,layer_lotes):
            """_summary_

            Args:
                layer (QgsVectorLayer): _description_
                grid_size (Integer): _description_
                layer_lotes (QgsVectorLayer): _description_

            Returns:
                _type_: _description_
            """      
            # process = {}
            try:
            
                layer_data = layer
                lotes = [f for f in layer_lotes.getFeatures()]
                buffer_lyrs = []
                lotes_lyrs = []
            
                process = {}
                for f in lotes:
                    
                    nombre = f['lote']
                    loteLyr = QgsVectorLayer('Polygon?crs=epsg:4326', f['lote'],"memory")
                    provider = loteLyr.dataProvider() 
                    provider.addFeature(f)
                    lotes_lyrs.append(loteLyr)
                    params = {'INPUT':loteLyr,
                    'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:3857'),
                    'OPERATION':'+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
                    'OUTPUT':'TEMPORARY_OUTPUT'}
                    reproject_process = processing.run("native:reprojectlayer",params ,feedback=self.f)
                    reprojected = reproject_process['OUTPUT']
                    params = {
                    'INPUT':reprojected,
                    'DISTANCE':10,
                    'SEGMENTS':5,
                    'END_CAP_STYLE':1,
                    'JOIN_STYLE':1,
                    'MITER_LIMIT':2,
                    'DISSOLVE':False,
                    'OUTPUT':'TEMPORARY_OUTPUT'}
                    buffer_process = processing.run("native:buffer",params,feedback=self.f)
                    buffer = buffer_process['OUTPUT']
                    buffer.setName(nombre)
                    buffer_lyrs.append(buffer)
                #    QgsProject.instance().addMapLayer(buffer)
                    
                #print(buffer_lyrs)
                procesadas = []
                for buffer,lote in zip(buffer_lyrs,lotes_lyrs):
                    nombre = buffer.name()
                    params = {
                        'TYPE':2,
                        'EXTENT':buffer,
                        'HSPACING':grid_size,
                        'VSPACING':grid_size,
                        'HOVERLAY':0,
                        'VOVERLAY':0,
                        'CRS':QgsCoordinateReferenceSystem('EPSG:3857'),
                        'OUTPUT':'TEMPORARY_OUTPUT'}
                    process['grid'] = processing.run("native:creategrid",params,feedback=self.f)
                    grid = process['grid']['OUTPUT']
                    params = {'INPUT':grid,
                            'JOIN':layer_data,
                            'PREDICATE':[0],
                            'JOIN_FIELDS':['AMB','NDVIMAX'],
                            'METHOD':1,
                            'DISCARD_NONMATCHING':True,
                            'PREFIX':'',
                            'OUTPUT':'TEMPORARY_OUTPUT'}
                    process['gridjoin']=processing.run("native:joinattributesbylocation",params,feedback=self.f)
                    gridJoin = process['gridjoin']['OUTPUT']
                    params = {'INPUT':gridJoin,
                            'FIELD':['AMB','NDVIMAX'],
                            'OUTPUT':'TEMPORARY_OUTPUT'}
                    process['gridDisolve'] = processing.run("native:dissolve",params,feedback=self.f)
                    gridDisolve = process['gridDisolve']['OUTPUT']
                    
                    params = {
                        'INPUT': gridDisolve,
                        'OVERLAY': lote, 
                        'OUTPUT': 'TEMPORARY_OUTPUT'}
                    
                    process['clip'] = processing.run("native:clip", params, feedback=self.f)
                    clipped = process['clip']['OUTPUT']
                    
                    params =  {'INPUT':clipped,'COLUMN':['left','top','right','bottom'],'OUTPUT':'TEMPORARY_OUTPUT'}
                    process['removeFields'] = processing.run("qgis:deletecolumn", params,feedback=self.f)
                    removeFields = process['removeFields']['OUTPUT']
                    removeFields.setName(nombre)
                    procesadas.append(removeFields)
                    

                params = {
                'LAYERS':procesadas,
                'CRS':QgsCoordinateReferenceSystem('EPSG:25832'),
                'OUTPUT':'TEMPORARY_OUTPUT'}

                unificar  = processing.run("native:mergevectorlayers",params,feedback=self.f )

                params =  {'INPUT':unificar['OUTPUT'],'COLUMN':['layer','path'],'OUTPUT':'TEMPORARY_OUTPUT'}
                limpiar_process = processing.run("qgis:deletecolumn", params,feedback=self.f)
                removeFields = limpiar_process['OUTPUT']
                renameFields = processing.run("native:renametablefield", {'INPUT':removeFields,'FIELD':'AMB','NEW_NAME':'ambiente','OUTPUT':'TEMPORARY_OUTPUT'})   

                duplicates = processing.run("native:deleteduplicategeometries", {'INPUT':renameFields['OUTPUT'],'OUTPUT':'TEMPORARY_OUTPUT'})   
                verificada  = duplicates['OUTPUT']
                verificada.setName(f'{layer_data.name()}_Verificada')
                
                return verificada

            except Exception as ex: 
                # QgsMessageLog.logMessage(f'{ex} \nError ejecutando el proceso VerifyLayer', 'aGrae GIS', level=1)
                # QMessageBox.about(self,'aGrae GIS', 'Ocurrio un error, revisa el panel de mensajes de registros')
                print(ex)