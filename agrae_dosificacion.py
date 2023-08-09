import os
import sys
from qgis.PyQt import uic
from qgis.PyQt.QtXml import QDomDocument

from qgis.core import *
from qgis.gui import QgsFieldComboBox
from qgis.utils import iface

from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor
from .utils import AgraeToolset, AgraeUtils


agraeDosificacionDialog, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui/dialogs/dosificacion.ui'))
class agraeDosificacion(QDialog,agraeDosificacionDialog):
    closingPlugin = pyqtSignal()
    def __init__(self,parent=None) -> None:
        super(agraeDosificacion,self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('Dosificacion')
        self.utils = AgraeUtils()
        self.tools = AgraeToolset()
        self.excludedProviders = ['DB2', 'EE', 'OAPIF', 'WFS', 'arcgisfeatureserver', 'arcgismapserver', 'ept', 'gdal', 'grass', 'grassraster', 'hana', 'mdal', 'mesh_memory', 'mssql','oracle', 'postgresraster',  'virtualraster', 'wcs', 'wms']
        self.clasificationMethods = [
            'Cuantil',
            'Escala Logaritmica',
            'Desviacion Standard',
            'Intervalo Igual',
            'Pretty Breaks',
            'Jenks']
        self.plugin_dir = os.path.dirname(__file__)
        self.root = QgsProject.instance().layerTreeRoot()

        

        self.basemaps = {
            'Esri Satelite' : {
                'url': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/%7Bz%7D/%7By%7D/%7Bx%7D',
                'options': 'crs=EPSG:3857&format&type=xyz&url=https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/%7Bz%7D/%7By%7D/%7Bx%7D&zmax=20&zmin=0'
            },
            'Google Satelite' : {
                'url': 'https://mt1.google.com/vt/lyrs=s&x=%7Bx%7D&y=%7By%7D&z=%7Bz%7D',
                'options': 'type=xyz&zmin=0&zmax=20&url=https://mt1.google.com/vt/lyrs%3Ds%26x%3D{x}%26y%3D{y}%26z%3D{z}'
            }

        }

        self.render = None
       

        
        self.UIComponents()
        # print(self.excludedLayers)
    

    def closeEvent(self,event):
        self.closingPlugin.emit()

        event.accept()

        

    def UIComponents(self):
        combosLayers = [self.combo_atlas_layer,self.combo_prees_layer,self.combo_apl_layer]
        combosFields = [self.combo_prees_field,self.combo_apl_field]

        for e in combosLayers:
            e.setExcludedProviders(self.excludedProviders)
        for e in combosFields:
            e.setFilters(QgsFieldProxyModel.Numeric)

        # names = [e for e in self.basemaps]
        # print(names)
        for e in self.basemaps:
            self.combo_basemap.addItem(e)
        for e in self.clasificationMethods:
            self.combo_methods.addItem(e)
            

        
        # self.spin_clases.setValue(5)

        


        self.combo_atlas_layer.layerChanged.connect(lambda l, c=self.combo_atlas_field: self.updateFields(l,c))
        self.combo_prees_layer.layerChanged.connect(lambda l, c=self.combo_prees_field: self.updateFields(l,c))
        self.combo_apl_layer.layerChanged.connect(lambda l, c=self.combo_apl_field: self.updateFields(l,c))

        self.pushButton.clicked.connect(lambda: self.generarAtlas_DEV(
            self.combo_atlas_layer.currentLayer(),
            self.combo_atlas_field.currentField(),
            self.combo_prees_layer.currentLayer(),
            self.combo_prees_field.currentField(),
            self.combo_apl_layer.currentLayer(),
            self.combo_apl_field.currentField())
            )
        
        self.combo_basemap.currentIndexChanged.connect(self.test)
        


    def updateFields(self,l,combo_field:QgsFieldComboBox):
        combo_field.setLayer(l)


    def test(self):
        
        lyr = self.getBaseMap(self.combo_basemap.currentText())

        print(lyr)

    
        pass

    def generarAtlas_DEV(self,
                     layer_atlas:QgsVectorLayer,
                     field_atlas:QgsField, 
                     preescription_layer:QgsVectorLayer,
                     preescription_field:QgsField,
                     applied_layer:QgsVectorLayer,
                     applied_field:QgsField):

        method = self.combo_methods.currentText()
        
        self.render = renderDosification(method)

        lyr_atlas = layer_atlas
        self.render.runSimple(lyr_atlas)
        atlas_field_name = field_atlas
        idx = lyr_atlas.fields().indexOf(atlas_field_name)
        values = lyr_atlas.uniqueValues(idx)
        iterator = iter(values)
        id = next(iterator)

        project = QgsProject.instance()
        manager = project.layoutManager()
        layout = QgsPrintLayout(project)
        layoutName = "Preescripcion"
        layouts_list = manager.printLayouts()



        for layout in layouts_list:
            if layout.name() == layoutName:
                manager.removeLayout(layout)
                
        layout = QgsPrintLayout(project)
        layout.initializeDefaults()                 #create default map canvas
        layout.setName(layoutName)
        manager.addLayout(layout)

        atlas = layout.atlas()
        atlas.setCoverageLayer(lyr_atlas)
        atlas.setPageNameExpression(atlas_field_name)

        pc = layout.pageCollection()
        pc.page(0).setPageSize('A4', QgsLayoutItemPage.Orientation.Portrait)

        tmpfile = self.plugin_dir + '/tools/templates/dosis.qpt'
        with open(tmpfile) as f:
            template_content = f.read()
            
        doc = QDomDocument()
        doc.setContent(template_content)
        items, ok = layout.loadFromTemplate(doc, QgsReadWriteContext(), False)
        
        basemap = self.tools.getBaseMap(self.combo_basemap.currentText(),self.basemaps)

        

        # selected_node: QgsLayerTreeLayer = iface.layerTreeView().currentNode()

        # # print(len(selected_node.children()))

        # selected_node.insertLayer(-1,basemap)

        QgsProject.instance().addMapLayer(basemap,False)
        
        

        map_dosis = layout.itemById('map_dosis')
        map_dosis_settings = QgsMapSettings()
        map_dosis_settings.setLayers([preescription_layer,lyr_atlas,basemap])
        map_dosis.setLayers([preescription_layer,lyr_atlas,basemap])
        map_dosis.attemptResize(QgsLayoutSize(130, 130, QgsUnitTypes.LayoutMillimeters))
        
        map_aplicado = layout.itemById('map_aplicado')
        map_aplicado_settings = QgsMapSettings()
        map_aplicado_settings.setLayers([applied_layer,lyr_atlas,basemap])
        map_aplicado.setLayers([applied_layer,lyr_atlas,basemap])
        map_aplicado.attemptResize(QgsLayoutSize(130, 130, QgsUnitTypes.LayoutMillimeters))
        map_aplicado.setAtlasDriven(True)

        # print(map_dosis.layers())
        # print(map_aplicado.layers())

        map_legend =  layout.itemById('map_legend')
        # print(map_legend)
        legend_model = map_legend.model() 
        legend_root = legend_model.rootGroup()

        for e in [preescription_layer,applied_layer]:
            legend_root.addLayer(e)

        # print(atlas.coverageLayer().getFeature(atlas.currentFeatureNumber())['NOMBRE'])

        atlas.refreshCurrentFeature()
        atlas.updateFeatures()
        atlas.seekTo(0)
        atlas.setEnabled(True)
        # atlas.setFilenameExpression(atlas.coverageLayer().getFeature(atlas.currentFeatureNumber())['lote'])
        
        
            
        atlas.featureChanged.connect(lambda: self.moveCanvas(
            atlas,
            map_dosis,
            atlas_field_name,
            preescription_layer,
            preescription_field,
            applied_layer,
            applied_field))
        iface.openLayoutDesigner(layout)


    def moveCanvas(self,
                   atlas:QgsLayoutAtlas,
                   map:QgsLayoutItemMap,
                   field_cod:QgsField,
                   preescription_layer:QgsVectorLayer,
                   preescription_field:QgsField,
                   applied_layer:QgsVectorLayer,
                   applied_field:QgsField):
            
            feature = atlas.coverageLayer().getFeature(atlas.currentFeatureNumber())
            cod = feature[field_cod]
            dosis_lyr = preescription_layer
            dosis_lyr.setSubsetString('''"{}" = '{}' '''.format(field_cod,cod))
            aplicado_lyr = applied_layer
            aplicado_lyr.setSubsetString('''"{}" = '{}' '''.format(field_cod,cod))

            lbl_prees = self.combo_lbl_prees.currentText()
            lbl_applied = self.combo_lbl_applied.currentText()

            prees_classes = self.spin_clases_prees.value()
            applied_classes = self.spin_clases_applied.value()
            method = self.combo_methods.currentText()
            
            self.render.runGraduated(dosis_lyr,preescription_field,prees_classes,lbl_prees)
            self.render.runGraduated(aplicado_lyr,applied_field,applied_classes,lbl_applied)
            
            extent = map.extent()
            iface.mapCanvas().setExtent(extent)
    

    def getBaseMap(self,name:str) -> QgsRasterLayer:
        basemap = self.basemaps[name]
        url = basemap['url']
        options = basemap['options']
        urlWithParams = 'url={}&{}'.format(url,options)
        return QgsRasterLayer(urlWithParams,name,'wms')


class renderDosification():
    def __init__(self,method):
        
        self.clasificationMethods = {
            'Cuantil' : QgsClassificationQuantile(),
            'Escala Logaritmica': QgsClassificationLogarithmic(),
            'Desviacion Standard': QgsClassificationStandardDeviation(),
            'Intervalo Igual':QgsClassificationEqualInterval(),
            'Pretty Breaks': QgsClassificationJenks(),
            'Jenks':QgsClassificationJenks()
        }

        self.method = self.clasificationMethods[method]

        self.rampName = 'Viridis'


    def runGraduated(self,lyr,field:str,numClass,label):
        # classificationMethod = self.method
        classificationMethod = QgsClassificationQuantile()
        # print(classificationMethod.classes(lyr,field,numClass)) #! ESTA FUNCION RETORNA LOS BREAKS DEL METODO DE CLASIFICACION ESTUDIAR UTILIDAD
        formatLabel = QgsRendererRangeLabelFormat()
        formatLabel.setFormat("%1 - %2 {}".format(label))
        formatLabel.setPrecision(0)
        formatLabel.setTrimTrailingZeroes(True)

        default_style = QgsStyle().defaultStyle()
        color_ramp = default_style.colorRamp(self.rampName)

        renderer = QgsGraduatedSymbolRenderer()
        renderer.setClassAttribute(field)
        renderer.setClassificationMethod(classificationMethod)
        renderer.setLabelFormat(formatLabel)
        renderer.updateClasses(lyr, numClass)
        renderer.updateColorRamp(color_ramp)

        lyr.setRenderer(renderer)
        lyr.triggerRepaint()

    def runSimple(self,lyr:QgsVectorLayer):
        renderer = lyr.renderer()
        symbol = renderer.symbol()
        symbol = symbol[0]
        symbol.setColor(QColor('transparent'))
        symbol.setStrokeColor(QColor('red'))
        symbol.setStrokeWidth(0.25)

        lyr.triggerRepaint()
        iface.layerTreeView().refreshLayerSymbology( lyr.id() )




    


# app = QApplication(sys.argv)

# window = agraeDosificacion()
# window.show()

# app.exec()




    
