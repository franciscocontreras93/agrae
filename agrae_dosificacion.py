import os
import sys
from qgis.PyQt import uic
from qgis.PyQt.QtXml import QDomDocument

from qgis.core import *
from qgis.gui import QgsFieldComboBox
from qgis.utils import iface

from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal


agraeDosificacionDialog, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui/dialogs/dosificacion.ui'))
class agraeDosificacion(QDialog,agraeDosificacionDialog):
    closingPlugin = pyqtSignal()
    def __init__(self,parent=None) -> None:
        super(agraeDosificacion,self).__init__(parent)
        self.setWindowTitle('Dosificacion')
        self.excludedProviders = ['DB2', 'EE', 'OAPIF', 'WFS', 'arcgisfeatureserver', 'arcgismapserver', 'ept', 'gdal', 'grass', 'grassraster', 'hana', 'mdal', 'mesh_memory', 'mssql','oracle', 'postgresraster',  'virtualraster', 'wcs', 'wms']
        
        self.render = renderDosification()

        self.setupUi(self)
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
        
        self.spin_clases.setValue(5)


        self.combo_atlas_layer.layerChanged.connect(lambda l, c=self.combo_atlas_field: self.updateFields(l,c))
        self.combo_prees_layer.layerChanged.connect(lambda l, c=self.combo_prees_field: self.updateFields(l,c))
        self.combo_apl_layer.layerChanged.connect(lambda l, c=self.combo_apl_field: self.updateFields(l,c))

        self.pushButton.clicked.connect(lambda: self.generarAtlas_DEV(
            self.combo_atlas_layer.currentLayer(),
            self.combo_atlas_field.currentField(),
            self.combo_prees_layer.currentLayer(),
            self.combo_prees_field.currentField(),
            self.combo_apl_layer.currentLayer(),
            self.combo_apl_field.currentField(),
            self.spin_clases.value(),
            self.line_label.text())
            )
        


    def updateFields(self,l,combo_field:QgsFieldComboBox):
        combo_field.setLayer(l)


    def generarAtlas(self,
                     layer_atlas:QgsVectorLayer,
                     field_atlas:QgsField, 
                     layer_dosis:QgsVectorLayer,
                     field_dosis:QgsField,
                     layer_aplicado:QgsVectorLayer,
                     field_aplicado:QgsField,
                     numClass:int,
                     label:str):
        
        self.render.run(layer_dosis,field_dosis,numClass,label)

    
        pass

    def generarAtlas_DEV(self,
                     layer_atlas:QgsVectorLayer,
                     field_atlas:QgsField, 
                     preescription_layer:QgsVectorLayer,
                     preescription_field:QgsField,
                     applied_layer:QgsVectorLayer,
                     applied_field:QgsField,
                     numClasses:int,
                     label:str):
        
        

        lyr_atlas = layer_atlas
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

        tmpfile = r'D:/GeoSIG/aGrae/Proyectos/Dosis.qpt'
        with open(tmpfile) as f:
            template_content = f.read()
            
        doc = QDomDocument()
        doc.setContent(template_content)
        items, ok = layout.loadFromTemplate(doc, QgsReadWriteContext(), False)
        map_dosis = layout.itemById('map_dosis')
        map_dosis_settings = QgsMapSettings()
        map_dosis_settings.setLayers([preescription_layer,lyr_atlas])
        map_dosis.setLayers([preescription_layer,lyr_atlas])
        #rect_map = QgsRectangle(map_dosis_settings.fullExtent())
        # rect_map.scale(5000)
        #map_dosis_settings.setExtent(rect_map)
        # map_dosis.zoomToExtent(extent)
        map_dosis.attemptResize(QgsLayoutSize(130, 130, QgsUnitTypes.LayoutMillimeters))
        
        map_aplicado = layout.itemById('map_aplicado')
        map_aplicado_settings = QgsMapSettings()
        map_aplicado_settings.setLayers([applied_layer,lyr_atlas])
        map_aplicado.setLayers([applied_layer,lyr_atlas])
        #rect_map = QgsRectangle(map_aplicado_settings.fullExtent())
        # rect_map.scale(5000)
        #map_aplicado_settings.setExtent(rect_map)
        # map_aplicado.zoomToExtent(extent)
        map_aplicado.attemptResize(QgsLayoutSize(130, 130, QgsUnitTypes.LayoutMillimeters))
        map_aplicado.setAtlasDriven(True)

        print(map_dosis.layers())
        print(map_aplicado.layers())

        atlas.refreshCurrentFeature()
        atlas.updateFeatures()
        atlas.seekTo(0)
        atlas.setEnabled(True)
        atlas.setFilenameExpression(atlas.coverageLayer().getFeature(atlas.currentFeatureNumber())['NOMBRE'])
        
        
            
        atlas.featureChanged.connect(lambda: self.moveCanvas(
            atlas,
            map_dosis,
            atlas_field_name,
            preescription_layer,
            preescription_field,
            applied_layer,
            applied_field,
            numClasses,
            label))
        iface.openLayoutDesigner(layout)


    def moveCanvas(self,
                   atlas:QgsLayoutAtlas,
                   map:QgsLayoutItemMap,
                   field_cod:QgsField,
                   preescription_layer:QgsVectorLayer,
                   preescription_field:QgsField,
                   applied_layer:QgsVectorLayer,
                   applied_field:QgsField,
                   numClasses:int,
                   label:str):
            
            feature = atlas.coverageLayer().getFeature(atlas.currentFeatureNumber())
            cod = feature[field_cod]
            dosis_lyr = preescription_layer
            dosis_lyr.setSubsetString('''"_ATLAS" = '{}' '''.format(cod))
            aplicado_lyr = applied_layer
            aplicado_lyr.setSubsetString('''"_ATLAS" = '{}' '''.format(cod))
            
            self.render.run(dosis_lyr,preescription_field,numClasses,label)
            self.render.run(aplicado_lyr,applied_field,numClasses,label)
            
            extent = map.extent()
            iface.mapCanvas().setExtent(extent)
    




class renderDosification():
    def __init__(self):
        self.rampName = 'Viridis'
    def run(self,lyr,field,numClass,label):
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



    


# app = QApplication(sys.argv)

# window = agraeDosificacion()
# window.show()

# app.exec()




    
