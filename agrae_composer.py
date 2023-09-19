import base64
from io import BytesIO
from PIL import Image
import os
import sys
from qgis.PyQt import uic
from qgis.PyQt.QtXml import QDomDocument

from qgis.core import *
from qgis.gui import QgsFieldComboBox
from qgis.utils import iface

from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, QSettings, QDateTime, QThreadPool
from PyQt5.QtGui import QColor,QFont
from .utils import AgraeToolset, AgraeUtils, AgraeZipper
from .agrae_worker import Worker

agraeComposerDialog, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui/dialogs/composer.ui'))
class agraeComposer(QDialog,agraeComposerDialog):
    closingPlugin = pyqtSignal()
    def __init__(self,parent=None) -> None:
        super(agraeComposer,self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('Generar Reporte de Preescripcion')
        self.threadpool = QThreadPool()
        self.atlas = None
        self.settings = QSettings('agrae','dbConnection')
        self.panels_path = self.settings.value('paneles_path')
        self.reportes_path = self.settings.value('reporte_path')
        self.utils = AgraeUtils()
        self.conn = AgraeUtils().Conn()
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
        self.groups = [ g for g in self.root.children() if isinstance(g, QgsLayerTreeGroup) ] 

        # self.comboBox.addItems(lambda name: for x.name() in self.groups)

        self.basemaps = {
          
            'Esri Satelite' : {
                'url': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/%7Bz%7D/%7By%7D/%7Bx%7D',
                'options': 'crs=EPSG:3857&format&type=xyz&url=https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/%7Bz%7D/%7By%7D/%7Bx%7D&zmax=20&zmin=0'
            },
            'Google Satelite' : {
                'url': 'https://mt1.google.com/vt/lyrs=s&x=%7Bx%7D&y=%7By%7D&z=%7Bz%7D',
                'options': 'type=xyz&zmin=0&zmax=20&url=https://mt1.google.com/vt/lyrs%3Ds%26x%3D{x}%26y%3D{y}%26z%3D{z}'
            },
              'PNOA Ortofoto' : {
                'url': 'contextualWMSLegend=0&crs=EPSG:4326&dpiMode=7&featureCount=10&format=image/png&layers=OI.OrthoimageCoverage&styles' ,
                'options': 'url=https://www.ign.es/wms-inspire/pnoa-ma'
            }

        }

        self.render = None
       

        
        self.UIComponents()
        # print(self.excludedLayers)
    def closeEvent(self,event):
        self.closingPlugin.emit()

        event.accept()
    def populateCombos(self):
        self.combo_grupos.clear()
        self.combo_basemap.clear()
        self.combo_grupos.addItems([g.name() for g in self.groups])
        self.combo_basemap.addItems([k for k in self.basemaps])
    def UIComponents(self):
        self.populateCombos()
        self.pushButton.clicked.connect(lambda: self.layoutGenerator(preview=True))
        self.pushButton_2.clicked.connect(self.ComposerPrintWorker)
    def setLayersToMap(self,mapItems,layers,basemap):
        
        map_1 = mapItems[0]
        map_1_settings = QgsMapSettings()
        map_1_settings.setLayers([layers[1],layers[0],basemap])
        map_1.setLayers([layers[1],layers[0],basemap])
        clippingSettings = QgsLayoutItemMapAtlasClippingSettings(map_1)
        clippingSettings.setEnabled(True)
        clippingSettings.setLayersToClip([layers[1]])
        if len(mapItems) >= 2:
            map_2 = mapItems[1]
            map_2_settings = QgsMapSettings()
            map_2_settings.setLayers([layers[2],layers[0],basemap])
            map_2.setLayers([layers[2],layers[0],basemap])
            clippingSettings = QgsLayoutItemMapAtlasClippingSettings(map_2)
            clippingSettings.setEnabled(True)
            clippingSettings.setLayersToClip([layers[2]])

        pass 
    def setLegendsToLayout(self,legendItem,layers,labels):
        titleFont = QFont('Arial',12,1,False)
        titleFont.setBold(True)
        subGroupFont = QFont('Arial',10,1,False)
        subGroupFont.setBold(True)
        font = QFont('Arial',10,1,False)


        legend =  legendItem
        legend.rstyle(QgsLegendStyle.Title).setFont(titleFont)
        legend.rstyle(QgsLegendStyle.Title).setMargin(QgsLegendStyle.Bottom,3)
        legend.rstyle(QgsLegendStyle.Subgroup).setFont(subGroupFont)
        legend.rstyle(QgsLegendStyle.Subgroup).setMargin(QgsLegendStyle.Bottom,3)
        legend.rstyle(QgsLegendStyle.SymbolLabel).setFont(font)
        legend.rstyle(QgsLegendStyle.SymbolLabel).setMargin(QgsLegendStyle.Left,3)
        # txt_legend.setStyle(QgsLegendStyle.Title,legend_style_title)
        # txt_legend.setStyle(QgsLegendStyle.Subgroup,legend_style_subGroup)
        # txt_legend.setStyle(QgsLegendStyle.SymbolLabel,legend_style)

        legend_model = legend.model() 
        legend_root = legend_model.rootGroup()
        legend_root.clear()

        for l in layers:
            legend_root.addLayer(l)

        # legend_root.addLayer(layers[_CEAP90_TXT])

        for tr,layer,label in zip(legend_root.children(),layers,labels):
            if tr.name() == layer.name():
                tr.setCustomProperty('legend/title-label',label)
                # tr.setCustomProperty('legend/')
        
        # pc.insertPage(QgsLayoutItemPage(),0)
        
        
        
        pass
    def getDistLogo(self,layer) -> Image:
        with self.conn.cursor() as cursor: 
            try:
                sql = "select imagen from public.distribuidor where icono = '{}' ".format(list(set([f['dist_icono'] for f in layer.getFeatures()]))[0])
                cursor.execute(sql)
                data = cursor.fetchone()[0]
                out = open(os.path.join(os.path.dirname(__file__),'ui/img/dist_logo.png'),'wb')
                out.write(data)
                # image = Image.open(BytesIO(data))

                # # print(image)
                # return image
            except TypeError as te:
                QgsMessageLog.logMessage('{}'.format(te), 'aGrae GIS Errors', level=Qgis.Warning)      
            except Exception as ex:
                QgsMessageLog.logMessage('{}'.format(ex), 'aGrae GIS Errors', level=Qgis.Critical)
            finally:
                out.close()
                pass
    def setTextOverElements(self,elements,text):
        for e in elements:
            e.setText(text)
    def layoutGenerator(self,
             preview=False,
             printer=False):
        titleFont = QFont('Arial',12,1,False)
        titleFont.setBold(True)
        subGroupFont = QFont('Arial',10,1,False)
        subGroupFont.setBold(True)
        font = QFont('Arial',10,1,False)

        

        legend_style = QgsLegendStyle()
        legend_style.setFont(font)
        legend_style.setMargin(QgsLegendStyle.Left,3)
        legend_style_title = QgsLegendStyle()
        legend_style_title.setFont(titleFont)
        legend_style.setMargin(QgsLegendStyle.Bottom,10)
        legend_style_subGroup = QgsLegendStyle()
        legend_style_subGroup.setFont(subGroupFont)



        _LOTES_ = 'LOTES'
        _NITROGENO_ = 'NITROGENO'
        _FOSFORO_ = 'FOSFORO'
        _POTASIO_ = 'POTASIO'
        _AMBIENTES_ = 'AMBIENTES PRODUCTIVOS'
        _PH_ = 'PH'
        _CONDUCTIVIDAD_ = 'CONDUCTIVIDAD ELECTRICA'
        _UNIDADES_I_ = 'FERT. VARIABLE INTRAPARCELARIA'
        _UNIDADES_II_ = 'FERT. VARIABLE PARCELARIA'
        _CALCIO_ = 'CALCIO'
        _MAGNESIO_ = 'MAGNESIO'
        _SODIO_ = 'SODIO'
        _AZUFRE_ = 'AZUFRE'
        _CIC_ = 'CIC'
        _HIERRO_ = 'HIERRO'
        _MANGANESO_ = 'MANGANESO'
        _ALUMINIO_ = 'ALUMINIO'
        _BORO_ = 'BORO'
        _CINQ_ = 'CINQ'
        _COBRE_ = 'COBRE'
        _MATERIA_ORGANICA_ = 'MATERIA ORGANICA'
        _REL_CN_ = 'RELACION CN'
        _SEGMENTOS_ = 'SEGMENTOS'
        _CEAP36_TXT = 'CEAP36 TEXTURA'
        _CEAP90_TXT = 'CEAP90 TEXTURA'
        _CEAP36_INF = 'CEAP36 INFILTRACION'
        _CEAP90_INF = 'CEAP90 INFILTRACION'


        basemap = self.tools.getBaseMap(self.combo_basemap.currentText(),self.basemaps)
        QgsProject.instance().addMapLayer(basemap,False)
        grupo = self.root.findGroup(self.combo_grupos.currentText())
        
        layers = {c.name():c.layer() for c in grupo.children()}
        # layers = {c.name():c.layer() for c in self.root.children()}
        self.getDistLogo(layers[_LOTES_])

        
            




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

        self.atlas = layout.atlas()
        self.atlas.setCoverageLayer(layers[_LOTES_])
        self.atlas.setPageNameExpression('lote')
        self.atlas.setFilenameExpression('lote')

        self.atlas.refreshCurrentFeature()
        self.atlas.updateFeatures()
        self.atlas.setEnabled(True)
        self.atlas.seekTo(0)

        feature = self.atlas.coverageLayer().getFeature(self.atlas.currentFeatureNumber()+1)

        pc = layout.pageCollection()
        # pc.page(0).setPageSize('A4', QgsLayoutItemPage.Orientation.Portrait)
        for l in range(0,15):
            pc.addPage(QgsLayoutItemPage(layout=layout))
            pc.page(l).setPageSize('A4', QgsLayoutItemPage.Orientation.Portrait)


        tmpfile = self.plugin_dir + '/tools/templates/prescripcion.qpt'
        with open(tmpfile) as f:
            template_content = f.read()
            
        doc = QDomDocument()
        doc.setContent(template_content)
        items, _ = layout.loadFromTemplate(doc, QgsReadWriteContext(), False)


        logos = [i for i in items if isinstance(i,QgsLayoutItemPicture) and i.id() == 'exp_logo']
        direcciones = [i for i in items if isinstance(i,QgsLayoutItemLabel) and i.id() == 'exp_dir']
        nombres_exp = [i for i in items if isinstance(i,QgsLayoutItemLabel) and i.id() == 'exp_name']
        nombres_lotes = [i for i in items if isinstance(i,QgsLayoutItemLabel) and i.id() == 'lote_nom']
        
        for l in logos:
            l.setPicturePath(os.path.join(os.path.dirname(__file__),'ui/img/dist_logo.png'))


        self.setTextOverElements(nombres_exp,feature.attribute('explotacion'))
        self.setTextOverElements(direcciones,feature.attribute('direccion'))
        


        # dist_logo_item.setPicturePath(os.path.join(os.path.dirname(__file__),'ui/img/dist_logo.png'))

        #* MAPAS
       






        self.setLayersToMap([layout.itemById('ceap36_txt'),layout.itemById('ceap90_txt')],[layers[_LOTES_],layers[_CEAP36_TXT],layers[_CEAP90_TXT]],basemap) #*  PAG 01
        self.setLayersToMap([layout.itemById('ceap36_inf'),layout.itemById('ceap90_inf')],[layers[_LOTES_],layers[_CEAP36_INF],layers[_CEAP90_INF]],basemap) #* PAG 02
        self.setLayersToMap([layout.itemById('map_nitrogeno'),layout.itemById('map_fosforo')],[layers[_LOTES_],layers[_NITROGENO_],layers[_FOSFORO_]],basemap) #* PAG 03
        self.setLayersToMap([layout.itemById('map_potasio'),layout.itemById('map_ambientes')],[layers[_LOTES_],layers[_POTASIO_],layers[_AMBIENTES_]],basemap) #* PAG 04
        self.setLayersToMap([layout.itemById('map_ph'),layout.itemById('map_conductividad')],[layers[_LOTES_],layers[_PH_],layers[_CONDUCTIVIDAD_]],basemap) #* PAG 05
        self.setLayersToMap([layout.itemById('map_06')],[layers[_LOTES_],layers[_UNIDADES_I_]],basemap) #* PAG 06
        self.setLayersToMap([layout.itemById('map_07_01')],[layers[_LOTES_],layers[_UNIDADES_I_]],basemap) #* PAG 07_01
        self.setLayersToMap([layout.itemById('map_07_02')],[layers[_LOTES_],layers[_UNIDADES_II_]],basemap) #* PAG 07_02
        self.setLayersToMap([layout.itemById('map_calcio'),layout.itemById('map_magnesio')],[layers[_LOTES_],layers[_CALCIO_],layers[_MAGNESIO_]],basemap) #* PAG 08
        self.setLayersToMap([layout.itemById('map_sodio'),layout.itemById('map_azufre')],[layers[_LOTES_],layers[_SODIO_],layers[_AZUFRE_]],basemap) #* PAG 09
        self.setLayersToMap([layout.itemById('map_cic'),layout.itemById('map_segmentos')],[layers[_LOTES_],layers[_CIC_],layers[_SEGMENTOS_]],basemap) #* PAG 10
        self.setLayersToMap([layout.itemById('map_hierro'),layout.itemById('map_manganeso')],[layers[_LOTES_],layers[_HIERRO_],layers[_MANGANESO_]],basemap) #* PAG 14
        self.setLayersToMap([layout.itemById('map_aluminio'),layout.itemById('map_boro')],[layers[_LOTES_],layers[_ALUMINIO_],layers[_BORO_]],basemap) #* PAG 15
        self.setLayersToMap([layout.itemById('map_cinq'),layout.itemById('map_cobre')],[layers[_LOTES_],layers[_CINQ_],layers[_COBRE_]],basemap) #* PAG 16
        self.setLayersToMap([layout.itemById('map_materia_organica'),layout.itemById('map_rel_cn')],[layers[_LOTES_],layers[_MATERIA_ORGANICA_],layers[_REL_CN_]],basemap) #* PAG 17
        # self.setLayersToMap([layout.itemById('map_cic')],[layers[_LOTES_],layers[_CIC_]],basemap) #* PAG 10
        
        # print(layers[_UNIDADES_I_])

        
        
        #* LEYENDAS 
        self.setLegendsToLayout(layout.itemById('legend_txt'),[layers[_CEAP90_TXT]],['Texturas'])
        self.setLegendsToLayout(layout.itemById('legend_inf'),[layers[_CEAP90_INF]],['Infiltración [mm/h]'])
        self.setLegendsToLayout(layout.itemById('legend_03'),[layers[_NITROGENO_],layers[_FOSFORO_]],['Nitrogeno','Fosforo'])
        self.setLegendsToLayout(layout.itemById('legend_04'),[layers[_POTASIO_],layers[_AMBIENTES_]],['Potasio','Ambientes Productivos'])
        self.setLegendsToLayout(layout.itemById('legend_05'),[layers[_PH_],layers[_CONDUCTIVIDAD_]],['pH','Conductividad Eléctrica'])
        self.setLegendsToLayout(layout.itemById('legend_06'),[layers[_UNIDADES_I_]],['Unidades Fertilziantes'])
        self.setLegendsToLayout(layout.itemById('legend_07_01'),[layers[_UNIDADES_I_]],['Unidades Fertilziantes'])
        self.setLegendsToLayout(layout.itemById('legend_07_02'),[layers[_UNIDADES_II_]],['UF Unica'])
        self.setLegendsToLayout(layout.itemById('legend_08'),[layers[_CALCIO_],layers[_MAGNESIO_]],['Calcio','Magnesio'])
        self.setLegendsToLayout(layout.itemById('legend_09'),[layers[_SODIO_],layers[_AZUFRE_]],['Sodio','Azufre'])
        self.setLegendsToLayout(layout.itemById('legend_10'),[layers[_CIC_]],['CIC'])
        self.setLegendsToLayout(layout.itemById('legend_14'),[layers[_HIERRO_],layers[_MANGANESO_]],['Hierro','Manganeso'])
        self.setLegendsToLayout(layout.itemById('legend_15'),[layers[_ALUMINIO_],layers[_BORO_]],['Aluminio','Boro'])
        self.setLegendsToLayout(layout.itemById('legend_16'),[layers[_CINQ_],layers[_COBRE_]],['Cinq','Cobre'])
        self.setLegendsToLayout(layout.itemById('legend_17'),[layers[_MATERIA_ORGANICA_],layers[_REL_CN_]],['Materia Organica','Relacion Carbono/Nitrogeno'])


        cic_table = layout.itemById('cic_table')
        table_item = cic_table.multiFrame()
        

       

        self.atlas.featureChanged.connect(lambda: self.moveCanvas(
            layout,
            layout.itemById('ceap36_inf'),
            self.atlas,
            nombres_lotes,
            [layers[k] for k in layers if k != 'LOTES'],
            [layout.itemById('panel_00')],
            table_item,
            # map_ceap36_txt,
            # atlas_field_name,
            # preescription_layer,
            # preescription_field,
            # applied_layer,
            # applied_field
            ))

        if preview:
            iface.openLayoutDesigner(layout)
        
        if printer:
            self.exportAtlasReport()

        

       






        

        pass
    def moveCanvas(self,
                   layout,
                   map:QgsLayoutItemMap,
                   atlas:QgsLayoutAtlas,
                   nombresLotes,
                   layers,
                   panels,
                   table,

                #    map:QgsLayoutItemMap,
                #    field_cod:QgsField,
                #    preescription_layer:QgsVectorLayer,
                #    preescription_field:QgsField,
                #    applied_layer:QgsVectorLayer,
                #    applied_field:QgsField
                   ):
            

            feature = atlas.coverageLayer().getFeature(atlas.currentFeatureNumber()+1)
            nombre_lote = feature.attribute('lote')
            for l in layers:
                l.setSubsetString('''  "lote"= '{}' '''.format(nombre_lote))
                if l.name() == 'CIC':
                    cic_layer = l
            
            for l in layers:
                l.setSubsetString('''  "lote"= '{}' '''.format(nombre_lote))

            # try:
            #   layout.removeLayoutItem(layout.itemById('table_cic'),)
            # except Exception:
            #   print(ex)

            table.setVectorLayer(cic_layer)
            table.setDisplayedFields(['segmento'.upper(),'cic','ca','mg','k','na'])
            c_0 = table.columns()[0]
            c_0.setHeading('Segmento')

            table.refreshAttributes()

        

           
            # table.refreshAttributes()
            # CIC_TABLE_DATA = []
            # for f in cic_layer.getFeatures():
            #     d = [f.attribute('lbl_segmento'),str(round(f.attribute('cic'),2)),str(round(f.attribute('ca'),2)),str(round(f.attribute('mg'),2)),str(round(f.attribute('k'),2)),str(round(f.attribute('na'),2))]
            #     CIC_TABLE_DATA.append(d)
            
            
            # for d in CIC_TABLE_DATA:
            #     table.addRow(d)
            # # cic_table.setContents(CIC_TABLE_DATA[1])
            # # cic_table.setContents(CIC_TABLE_DATA)
            # print(CIC_TABLE_DATA)


            # cic_table.setContents([['hola','mundo','como','te','va','100'],['hola','mundo','como','te','va','100'],['hola','mundo','como','te','va','100']])
            # cic_table.setContents([['hola','mundo','como','te','va','100'],['hola','mundo','como','te','va','100'],['hola','mundo','como','te','va','100']])

          
           
            # print(atlas.currentFeatureNumber(),feature.attribute('lote'))
            self.setTextOverElements(nombresLotes,nombre_lote)

            
            panels[0].setPicturePath(self.panels_path+'/Panel00'+nombre_lote+'.png')


            # cod = feature[field_cod]
            # dosis_lyr = preescription_layer
            # dosis_lyr.setSubsetString('''"{}" = '{}' '''.format(field_cod,cod))
            # aplicado_lyr = applied_layer
            # aplicado_lyr.setSubsetString('''"{}" = '{}' '''.format(field_cod,cod))

            # lbl_prees = self.combo_lbl_prees.currentText()
            # lbl_applied = self.combo_lbl_applied.currentText()

            # prees_classes = self.spin_clases_prees.value()
            # applied_classes = self.spin_clases_applied.value()
            # method = self.combo_methods.currentText()
            
            # self.render.runGraduated(dosis_lyr,preescription_field,prees_classes,lbl_prees)
            # self.render.runGraduated(aplicado_lyr,applied_field,applied_classes,lbl_applied)
            
            extent = map.extent()
            atlas.coverageLayer().getFeature(atlas.currentFeatureNumber()+1)
            iface.mapCanvas().setExtent(extent)   
    def ComposerPrintWorker(self):
        self.tools.UserMessages('Generando archivos de Preescripcion, este proceso puede tardar varios minutos.\nPorfavor espere un momento.')
        # print('worker')
        worker = Worker(lambda: self.layoutGenerator(printer=True))
        # worker.signals.finished.connect(lambda: self.tools.UserMessages('Archivos generados correctamente',level=Qgis.Success))
        worker.signals.finished.connect(lambda: iface.messageBar().pushMessage("aGrae GIS", 'Archivos generados correctamente', level=Qgis.Success))
        self.threadpool.start(worker)
    def exportAtlasReport(self):
        """exportAtlasReport Print layout aGrae
        """        
        directory = list(set([f['explotacion'] for f in self.atlas.coverageLayer().getFeatures()]))[0]
        directory = directory.replace(' ','_')
        path = os.path.join(self.reportes_path,directory+'_' + QDateTime.currentDateTime().toString('yyyyMMddHHmmss'))
        zipper = AgraeZipper()
        try:
            os.makedirs(path)
            self.atlas.beginRender()
            settings = QgsLayoutExporter.PdfExportSettings()
            settings.appendGeoreference = False
            settings.simplifyGeometries = True
            
            exporter = QgsLayoutExporter(self.atlas.layout())
            
            for i in range(0,self.atlas.count()):
                self.atlas.seekTo(i)
                name = self.atlas.currentFilename().replace(' ','_')
                name = name + '_' + QDateTime.currentDateTime().toString('yyyyMMddHHmmss')+".pdf"
                exporter.exportToPdf(path+r'\\'+name,settings)
                # self.tools.UserMessages('Reporte del Lote <b>{}</b> generado correctamente'.format(name), 5, Qgis.Success)
            self.atlas.endRender()
            zipper.zipFiles(path,True)
        except Exception as ex:
            print(ex)



    


# app = QApplication(sys.argv)

# window = agraeComposer()
# window.show()

# app.exec()




    
