# -*- coding: utf-8 -*-
"""
/***************************************************************************
 aGrae GIS
                                 A QGIS plugin
 Conjunto de herramientas

                              -------------------
        begin                : 2021-12-03
        git sha              : $Format:%H$
        copyright            : (C) 2021 by  aGrae Solutions, S.L.
        email                : info@agrae.es
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt5.QtWidgets import QMessageBox
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt, QVariant, QDate
from qgis.PyQt.QtGui import QIcon, QColor, QFont 
from qgis.PyQt.QtWidgets import QAction, QTableWidgetItem, QComboBox
from qgis.core import *
import pip
import random
import math

from qgis import processing
# Initialize Qt resources from file resources.py
from .resources import *
from .dbconn import DbConnection
from .utils import AgraeUtils, AgraeToolset

# Import the code for the DockWidget
from .agrae_dockwidget import (
    agraeDockWidget, 
    agraeConfigWidget, 
    agraeMainWidget, 
    loteFindDialog, 
    loteFilterDialog, 
    parcelaFindDialog,  
    expFindDialog)

from .agrae_dosificacion import agraeDosificacion


from .agrae_dialogs import ceapPrevDialog, verifyGeometryDialog, gestionDatosDialog, appliedLayerDialog
import os.path
from PIL import Image
from qgis.core import QgsDataSourceUri

try:
    import psycopg2
    import psycopg2.extras
except: 
    pip.main(['install','psycopg2'])
    import psycopg2
    import psycopg2.extras

try: 
    import numpy as np
except:
    pip.main(['install', 'numpy'])
    import numpy as np
try:
    import matplotlib as mpl
    import matplotlib.pyplot as plt
except:
    pip.main(['install', 'matplotlib'])
    import matplotlib as mpl
    import matplotlib.pyplot as plt

    


class agrae:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.utils = AgraeUtils()
        self.tools = AgraeToolset()

        self.icons_path = self.utils.iconsPath()

        self.conn = self.utils.Conn()
        self.dbset = QSettings('agrae','dbConnection')

        self.nameLayerComposer = None
        self.sqlParcela = None

        self.sinceDateStatus = False



        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'agrae_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&aGrae GIS')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'aGrae GIS')
        self.toolbar.setObjectName(u'aGrae GIS')
        
        
        self.queryCapaLotes = ''

        #print "** INITIALIZING agrae"

        self.pluginIsActive = False
        self.dockwidget = None
        self.configDialog = None
        self.mainWindowDialog = None
        self.loteFindDialog = None
        self.loteFilterDialog = None
        self.parcelaFilterDialog = None
        self.analiticaDialog = None
        self.datosDialog = None
        self.verisDataDialog = None
        self.verifyGeomDialog = None
        self.appliedDataDialog = None
        self.dosisDialog = None

        self.dataSuelo = None
        self.dataExtracciones = None

        self.idlotecampania =  None
        self.lote =  None
        self.parcela =  None
        self.prod = None
        self.cultivo =  None

        


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('agrae', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = self.icons_path['agrae_icon']
        self.add_action(
            icon_path,
            text=self.tr(u'aGrae GIS'),
            callback=self.runMain,
            parent=self.iface.mainWindow())
        search_icon_path = self.icons_path['search_lotes']
        self.add_action(
            search_icon_path,
            text=self.tr(u'Panel Lotes'),
            status_tip=self.tr(u'Filtrar Lotes'),
            callback=self.filtrarLotes,
            parent=self.iface.mainWindow())
        search_icon_path = self.icons_path['search_parcela']
        self.add_action(
            search_icon_path,
            text=self.tr(u'Filtrar Parcelas'),
            status_tip=self.tr(u'Filtrar Parcelas'),
            callback=self.filtrarParcelas,
            parent=self.iface.mainWindow())
        recintos_icon_path = self.icons_path['layer_upload']
        self.add_action(
            recintos_icon_path,
            text=self.tr(u'Cargar Recintos'),
            status_tip=self.tr(u'Cargar Recintos'),
            callback=self.uploadRecintos,
            parent=self.iface.mainWindow())
        rel_icon_path = self.icons_path['create_rel']
        self.add_action(
            rel_icon_path,
            text=self.tr(u'Crear Relacion'),
            status_tip=self.tr(u'Crear Relacion'),
            callback=self.relLote,
            parent=self.iface.mainWindow())
        user_icon_path = self.icons_path['users']
        self.add_action(
            user_icon_path,
            text=self.tr(u'Gestion Datos de Trabajo'),
            status_tip=self.tr(u'Gestionar Datos de Trabajo'),
            callback=self.runDatos,
            parent=self.iface.mainWindow())
        veris_icon_path = self.icons_path['ceap']
        self.add_action(
            veris_icon_path,
            text=self.tr(u'Veris DATA'),
            status_tip=self.tr(u'Preprocesamiento datos Veris'),
            callback=self.runVeris,
            parent=self.iface.mainWindow())
        icon = self.icons_path['check']
        self.add_action(
            icon,
            text=self.tr(u'Chequear Geometrias'),
            status_tip=self.tr(u'Preprocesamiento datos Veris'),
            callback=self.runVerifyGeometry,
            parent=self.iface.mainWindow())
        icon = self.plugin_dir + "/ui/icons/grilla.png"
        self.add_action(
            icon,
            text=self.tr(u'Chequear Geometrias'),
            status_tip=self.tr(u'Preprocesamiento datos Veris'),
            callback=self.runApplied,
            parent=self.iface.mainWindow())
        icon = self.plugin_dir + "/ui/icons/fertilizante.png"
        self.add_action(
            icon,
            text=self.tr(u'Chequear Geometrias'),
            status_tip=self.tr(u'Preprocesamiento datos Veris'),
            callback=self.runDosis ,
            parent=self.iface.mainWindow())

       
        self.add_action(
            '',
            text=self.tr(u'Ajustes'),
            add_to_toolbar=False,
            callback=self.runConfig,
            parent=self.iface.mainWindow())
        self.toolbar.addSeparator()



        

        

    #--------------------------------------------------------------------------
    def onClosePluginConfig(self):
        # disconnects
        self.configDialog.closingPlugin2.disconnect(self.onClosePluginConfig)
        self.pluginIsActive = False
    
    def onClosePluginMain(self):

        # disconnects
        self.mainWindowDialog.closingPlugin.disconnect(
            self.onClosePluginMain)
        self.pluginIsActive = False
        self.mainWindowDialog.tableWidget_3.setRowCount(0)
        self.mainWindowDialog.an_lbl_file.setText('')


    def onCloseLoteDialog(self):
        self.loteFindDialog.closingPlugin.disconnect(self.onCloseLoteDialog)
        self.pluginIsActive = False
        # self.loteFindDialog.btn_cargar_lote.setEnabled(True)

    def onCloseLoteFilterDialog(self):
        self.loteFilterDialog.closingPlugin.disconnect(self.onCloseLoteFilterDialog)
        self.pluginIsActive = False

    def onCloseParcelaFilterDialog(self):
        self.parcelaFilterDialog.closingPlugin.disconnect(
            self.onCloseParcelaFilterDialog)
        self.pluginIsActive = False

    def onCloseAnaliticaDialog(self): 
        # disconnects 
        self.analiticaDialog.closingPlugin.disconnect(self.onCloseAnaliticaDialog)
        self.pluginIsActive = False
        self.dataSuelo = None
        self.dataExtracciones = None
        self.idlotecampania = None
        self.lote = None
        self.parcela = None
        self.prod = None
        self.cultivo = None
        pass

    def onCloseDatosDialog(self): 
        self.datosDialog.closingPlugin.disconnect(self.onCloseDatosDialog)
        self.pluginIsActive = False
        pass
    

    
    def onCloseVerifyGeomDialog(self): 
        self.verifyGeomDialog.closingPlugin.disconnect(self.onCloseVerifyGeomDialog)
        # self.verifyGeomDialog.combo_layers.clear()
        self.verifyGeomDialog.close()

        self.pluginIsActive = False
        pass

    def onCloseAppliedDialog(self):
        self.appliedDataDialog.closingPlugin.disconnect(self.onCloseAppliedDialog)
        self.pluginIsActive = False
    def onCloseDosisDialog(self):
        self.dosisDialog.closingPlugin.disconnect(self.onCloseDosisDialog)
        self.pluginIsActive = False

    def onCloseCeapDialog(self): 
        self.verisDataDialog.closingPlugin.disconnect(self.onCloseCeapDialog)
        self.pluginIsActive = False
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD agrae"

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&aGrae GIS'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #--------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""
        def listLayer():
            if self.dockwidget.geom_check.isChecked():
                self.dockwidget.layers_combo.clear()
                self.dockwidget.combo_load_layers.clear()
                layerList = self.utils.loadGeomLayers()
                for i in layerList:
                    self.dockwidget.layers_combo.addItem(i.upper())
                    self.dockwidget.combo_load_layers.addItem(i.upper())
                    
            else: 
                self.dockwidget.layers_combo.clear()
                self.dockwidget.combo_load_layers.clear()
                layerList = self.utils.loadLayers()
                for i in layerList:
                    self.dockwidget.layers_combo.addItem(i.upper())
                    self.dockwidget.combo_load_layers.addItem(i.upper())

        def addLayerToMap(layerName):
            idx = 0
            if idx < 1:
                tablename = str(self.dockwidget.layers_combo.currentText()).lower()
                dns = self.utils.ConnParams()
                try: 
                    uri = QgsDataSourceUri()
                    uri.setConnection(dns['host'],dns['port'],dns['dbname'],dns['user'],dns['password'])
                    uri.setDataSource('public',tablename,'geometria')
                    layer = QgsVectorLayer(uri.uri(), tablename, 'postgres')
                    if layer.isValid():
                        QgsProject.instance().addMapLayer(layer)
                        print(f"Capa añadida correctamente {idx}")
                        idx += 1
                    else: 
                        uri.setDataSource('public', tablename, None)
                        layer = QgsVectorLayer(uri.uri(False), tablename, 'postgres')
                        QgsProject.instance().addMapLayer(layer)
                        idx += 1
                        print("La capa es invalida")
                except:
                    print('Ocurrio un error!')

        def loadFeatureToDB():
            with self.conn as conn:
                try:
                    cur = conn.cursor()
                    layer = self.iface.activeLayer()
                    # print(layer.name())
                    feat = layer.selectedFeatures()
                    ls = feat[0].geometry().asWkt()
                    srid = layer.crs().authid()[5:]
                    # print(ls)
                    sql = f''' INSERT INTO {self.dockwidget.combo_load_layers.currentText().lower()}(geometria) VALUES(st_multi(st_transform(st_geomfromtext('{ls}',{srid}),4326)))'''
                    cur.execute(sql)
                    conn.commit()
                    # print('agregado correctamente')
                    self.iface.messageBar().pushMessage(
                        'aGraes GIS', 'Registro creado Correctamente', level=3, duration=3)
                except:
                    self.iface.messageBar().pushMessage(
                        'aGraes GIS | ERROR: ', 'No se pudo almacenar el registro', level=1, duration=3)
                
        def createReticule():
            with self.conn as conn:
                try: 
                    cur = conn.cursor()
                    layer = self.iface.activeLayer() 
                    field_names = [field.name() for field in layer.fields()]
                    selFeature = layer.selectedFeatures()
                    for e in selFeature: 
                        idfeat = e[1]
                        sourceInfo = layer.publicSource().replace('=', ':')
                        sourceInfo = sourceInfo.replace('"public".', '')
                        source = sourceInfo.split(' ')
                        table = source[6][6:]
                        sql = f'''insert into reticulabase(geometria) 
                                (SELECT (ST_Dump(makegrid(geometria, 85))).geom from {table}
                                where {field_names[1]} = {idfeat}) '''
                        cur.execute(sql)
                        conn.commit()
                        self.iface.messageBar().pushMessage(
                            'aGraes GIS', 'Registro creado Correctamente', level=3, duration=3)

                except:
                    self.iface.messageBar().pushMessage(
                        'aGraes GIS | ERROR: ', 'No se pudo almacenar el registro', level=1, duration=3)
               
        def Intersection():
            try: 
                instance = QgsProject.instance()
                inputLayer = instance.mapLayersByName(self.dockwidget.inputLay.currentText())[0]
                superLayer = instance.mapLayersByName(self.dockwidget.superLay.currentText())[0]
                params = {
                    'INPUT': inputLayer.name(),
                    'OVERLAY': superLayer.name(),
                    #'INPUT_FIELDS':'amb',
                    #'OVERLAY_FIELDS':'segm',
                    'OUTPUT': 'memory:SIG'
                }
                intersect = processing.run('native:intersection', params)
                #result = processing.runAndLoadResults('native:intersection',params)
                layer = intersect['OUTPUT']
                #resultLayer.setName('intersect')
                print(layer)
                ufField = QgsField('UF', QVariant.Int)
                layer.dataProvider().addAttributes([ufField])
                layer.updateFields()
                exp = QgsExpression('"amb" + "segm"')
                context = QgsExpressionContext()
                scope = QgsExpressionContextScope()
                context.appendScope(scope)
                layer.startEditing()
                for f in layer.getFeatures():
                    scope.setFeature(f)
                    f['UF'] = exp.evaluate(context)
                    layer.updateFeature(f)
                layer.commitChanges()
                csvFileName = self.dockwidget.lineEdit.text()
                if len(csvFileName) > 0:
                    uri = f'''file:///{csvFileName}?delimiter=;'''
                    csv = QgsVectorLayer(uri, 'csv', 'delimitedtext')
                    if csv.isValid():
                        print('ok')
                        instance.addMapLayer(csv)
                        info = QgsVectorLayerJoinInfo()
                        info.setJoinFieldName('CONTROL')
                        info.setTargetFieldName('CONTROL')
                        info.setPrefix('')
                        info.setJoinLayerId(csv.id())
                        info.setUsingMemoryCache(True)
                        info.setJoinLayer(csv)
                        layer.addJoin(info)

                instance.addMapLayer(layer)
                self.iface.messageBar().pushMessage(
                    'aGraes GIS', 'Geoproceso Exitoso', level=3, duration=3)
            except Exception as ERROR:
                self.iface.messageBar().pushMessage(
                    f'aGraes GIS | {ERROR}: ', 'No se pudo Ejecutar el Geoproceso', level=1, duration=3)
            

        if not self.pluginIsActive:
            self.pluginIsActive = True

            #print "** STARTING agrae"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = agraeDockWidget()
            
            self.dockwidget.list_btn.clicked.connect(listLayer)
            self.dockwidget.load_1_btn.clicked.connect(addLayerToMap)
            self.dockwidget.create_reticule.clicked.connect(createReticule)
            self.dockwidget.label_6.setText(self.dbset.value('dbhost'))
            for lyr in QgsProject.instance().mapLayers().values():
                if lyr.isValid():
                    self.dockwidget.inputLay.addItem(lyr.name())
                    self.dockwidget.superLay.addItem(lyr.name())
            
                
            
            self.dockwidget.load_feat_btn.clicked.connect(loadFeatureToDB)
            self.dockwidget.interButton.clicked.connect(Intersection)

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
            self.dockwidget.show()

    def runConfig(self): 
        
        def saveConn(): 

            try: 
                self.utils.saveConfig(
                    self.configDialog.host.text(), self.configDialog.dbname.text(), self.configDialog.user.text(), self.configDialog.password.text(), self.configDialog.port.text())
                self.iface.messageBar().pushMessage('aGraes GIS',
                                                    'Ajustes aplicados correctamente, Reinicia el programa', level=3, duration=3)
            except: 
                self.iface.messageBar().pushMessage(
                    'aGraes GIS', 'No se pudieron aplicar los cambios', level=1, duration=3)
        def dbTestConn():
                try: 
                    self.utils.dbTestConnection(
                        self.configDialog.dbname.text(), self.configDialog.user.text(), self.configDialog.password.text(), self.configDialog.host.text(), self.configDialog.port.text())
                    self.iface.messageBar().pushMessage('aGraes GIS', 'Conexion a base de Datos Exitosa', level=3, duration=3)
                except:           
                    self.iface.messageBar().pushMessage(
                        'aGraes GIS', 'Conexion a base de Datos Fallida', level=1, duration=3)
        def getPanelsDirectory(line):
            try: 
                filename = self.utils.saveDirectory()
                line.setText(filename)
            except Exception as ex:
                print(ex)
                pass
        def saveSettings(): 
            paneles_path = self.configDialog.panel_path.text()
            uf_path = self.configDialog.uf_path.text()
            reporte_path = self.configDialog.reporte_path.text()
            
            self.utils.settingPath('paneles_path',paneles_path)
            self.utils.settingPath('ufs_path',uf_path)
            self.utils.settingPath('reporte_path',reporte_path)
            self.configDialog.pushButton_2.setEnabled(False)
                  
        def readSettings(): 
            s = QSettings('agrae', 'dbConnection')

            self.configDialog.panel_path.setText(str(s.value('paneles_path')))
            self.configDialog.uf_path.setText(str(s.value('ufs_path')))
            self.configDialog.reporte_path.setText(str(s.value('reporte_path')))
            self.configDialog.host.setText(str(s.value('dbhost')))
            self.configDialog.dbname.setText(str(s.value('dbname')))
            self.configDialog.user.setText(str(s.value('dbuser')))
            self.configDialog.password.setText(str(s.value('dbpass')))
            self.configDialog.port.setText(str(s.value('dbport')))


        if not self.pluginIsActive:
            self.pluginIsActive = True
        
            if self.configDialog == None:
                self.configDialog = agraeConfigWidget()
                # self.configDialog.closingPlugin2.connect(self.onClosePluginConfig)
                
                readSettings()
                self.configDialog.test_btn.clicked.connect(dbTestConn)
                self.configDialog.pushButton.clicked.connect(saveConn)
                self.configDialog.pushButton_2.clicked.connect(saveSettings)
                self.configDialog.pushButton_3.clicked.connect(lambda: getPanelsDirectory(self.configDialog.panel_path))
                self.configDialog.pushButton_4.clicked.connect(lambda: getPanelsDirectory(self.configDialog.uf_path))
                self.configDialog.pushButton_5.clicked.connect(lambda: getPanelsDirectory(self.configDialog.reporte_path))
            
            self.configDialog.closingPlugin2.connect(self.onClosePluginConfig)
            self.configDialog.show()


        pass

    def runMain(self):
            
        def printMap():
            mainColor = QColor(233, 219, 0)
            layers = self.iface.mapCanvas().layers()
            layoutName = None
            for l in layers:
                if 'SEGMENTOS' in l.name():
                    layoutName = QgsProject.instance(
                    ).mapLayersByName(l.name())[0].name()
                    # print(lyr)
            barPlot()
            #! LAYOUTMANAGER INSTANCIA
            manager = QgsProject.instance().layoutManager() 
            manager_list = manager.printLayouts() 

            for l in manager_list:
                if l.name() == layoutName[10:]:
                    manager.removeLayout(l)
            
            #? print(lyrs) 
            layout = QgsPrintLayout(QgsProject.instance())
            layout.initializeDefaults() 
            layout.setName(layoutName[10:])
            
            pc = layout.pageCollection()
            pc.pages()[0].setPageSize('A4', QgsLayoutItemPage.Portrait)
            
            manager.addLayout(layout)
            lyrsDict = QgsProject().instance().mapLayers()
            lyrs = [lyrsDict[lyr] for lyr in lyrsDict]       
            ms = QgsMapSettings()            
            ms.setLayers(lyrs)
            lyr = QgsProject.instance().mapLayersByName(layoutName)[0]
            # lyr.setCrs(QgsCoordinateReferenceSystem(25830))
            extent = lyr.extent()
            lyrScale = self.iface.mapCanvas().scale()
            scale = math.ceil((lyrScale / 200)) * 200
            print(scale)
            #? extent.scale(1.0)
            #? ms.setExtent(extent)


            #! MAP TITLE 
            title = QgsLayoutItemLabel(layout)
            title.setText('06 - Unidades Fertilizantes')
            title.setFont(QFont('Arial',20,QFont.Bold))
            # title.setFontColor(QColor(255,255,255))
            # title.adjustSizeToText()
            title.setBackgroundEnabled(True)
            title.setBackgroundColor(mainColor)
            title.setFrameEnabled(True)
            title.setFrameStrokeColor(mainColor)
            title.setFrameStrokeWidth(QgsLayoutMeasurement(2,QgsUnitTypes.LayoutMillimeters))
            title.attemptMove(QgsLayoutPoint(10, 10,QgsUnitTypes.LayoutMillimeters))
            title.attemptResize(QgsLayoutSize(140, 10, QgsUnitTypes.LayoutMillimeters))



            #! MAP ITEM
            map = QgsLayoutItemMap(layout)
            # map.setCrs(QgsCoordinateReferenceSystem(25830))
            map.setRect(20,20,20,20)
            # map.setExtent(extent)
            map.zoomToExtent(self.iface.mapCanvas().extent())
            map.setScale(math.floor(scale*10))
            map.setFrameEnabled(True)
            map.setFrameStrokeColor(mainColor)
            map.setFrameStrokeWidth(QgsLayoutMeasurement(2,QgsUnitTypes.LayoutMillimeters))
            map.attemptMove(QgsLayoutPoint(10, 20,QgsUnitTypes.LayoutMillimeters))
            map.attemptResize(QgsLayoutSize(140, 135,QgsUnitTypes.LayoutMillimeters))          
            
            #! BARPLOT
            barplot = QgsLayoutItemPicture(layout)
            barplot.setMode(QgsLayoutItemPicture.FormatRaster)
            barplot.setPicturePath(
                r"C:\Users\FRANCISCO\Documents\agrae\Paneles\panel-{}.png".format(layoutName[10:]))
            barplot.setResizeMode(QgsLayoutItemPicture.ZoomResizeFrame)
            #? barplot.setRect(20, 20, 20, 20)
            #? dim_barplot = [640, 480]
            barplot.attemptMove(QgsLayoutPoint(10, 170, QgsUnitTypes.LayoutMillimeters))
            barplot.attemptResize(QgsLayoutSize(100, 75, QgsUnitTypes.LayoutMillimeters))
            
            #! ADD ITEMS TO LAYOUT 
            layout.addLayoutItem(title)
            layout.addLayoutItem(map)
            layout.addLayoutItem(barplot)

            pass            

        def barPlot():
            # lyr = self.iface.activeLayer()
            layers = self.iface.mapCanvas().layers()

            for l in layers:
                if 'SEGMENTOS' in l.name():
                    lyr = QgsProject.instance().mapLayersByName(l.name())[0]
                    # print(lyr)
            lyrName = lyr.name()
            segmentos = [f['segmento'] for f in lyr.getFeatures()]
            nitrogeno = [f['n_tipo'] for f in lyr.getFeatures()]
            fosforo = [f['p_tipo'] for f in lyr.getFeatures()]
            potasio = [f['k_tipo'] for f in lyr.getFeatures()]
            carbonato = [f['carb_tipo'] for f in lyr.getFeatures()]
            n_values = {segmentos[i]: nitrogeno[i] for i in range(len(segmentos))}
            p_values = {segmentos[i]: fosforo[i] for i in range(len(segmentos))}
            k_values = {segmentos[i]: potasio[i] for i in range(len(segmentos))}
            carb_values = {segmentos[i]: carbonato[i] for i in range(len(segmentos))}

            suelo_1 = [n_values[1], p_values[1], k_values[1], carb_values[1]]
            suelo_2 = [n_values[2], p_values[2], k_values[2], carb_values[2]]
            suelo_3 = [n_values[3], p_values[3], k_values[3], carb_values[3]]

            fig, (ax1,ax2,ax3) = plt.subplots(1,3)
            categorias = ('Nitrogeno', 'Fosforo', 'Potasio', 'Carbonatos')
            y_pos = np.arange(len(categorias))
            def valores(suelo): 
                values = []
                colors = []
                for i in suelo:
                    if i == 'Muy Alto':
                        colors.append('#7702E5')
                        values.append(5)
                    elif i == 'Alto':
                        colors.append('#0293E5')
                        values.append(4)
                    elif i == 'Normal':
                        colors.append('#06E502')
                        values.append(3)
                    elif i == 'Bajo':
                        colors.append('#FF9633')
                        values.append(2)
                    elif i == 'Muy Bajo':
                        colors.append('#FF3333')
                        values.append(1)
                    else:
                        values.append(0)
                return values,colors
            
            values_1,colors_1 = valores(suelo_1)
            values_2,colors_2 = valores(suelo_2)
            values_3,colors_3 = valores(suelo_3)


            g = ax1.barh(y_pos, values_3, align='center', color=colors_3)
            ax1.barh(y_pos, values_3, align='center', color=colors_3)
            
            ax1.spines['top'].set_visible(False)
            ax1.spines['right'].set_visible(False)
            ax1.spines['bottom'].set_visible(False)
            ax1.spines['left'].set_visible(False)

            ax1.set_xticks([])
            # ax1.set_title('{}'.format('Suelo 3'))
            ax1.set_yticks(y_pos)
            ax1.axes.get_yaxis().set_visible(False)
            ax1.invert_yaxis()  # labels read top-to-bottom
            # ax1.bar_label(g, label_type="center")

            ax2.barh(y_pos, values_2, align='center', color=colors_2)

            ax2.spines['top'].set_visible(False)
            ax2.spines['right'].set_visible(False)
            ax2.spines['bottom'].set_visible(False)
            ax2.spines['left'].set_visible(False)

            ax2.set_xticks([])
            ax2.axes.get_yaxis().set_visible(False)
            # ax2.set_title('{}'.format('Suelo 2'))
            ax2.set_yticks(y_pos)
            ax2.set_xticklabels([], color='w')
            ax2.invert_yaxis()  # labels read top-to-bottom

            ax3.barh(y_pos, values_1, align='center', color=colors_1)

            ax3.spines['top'].set_visible(False)
            ax3.spines['right'].set_visible(False)
            ax3.spines['bottom'].set_visible(False)
            ax3.spines['left'].set_visible(False)

            ax3.set_xticks([])
            ax3.axes.get_yaxis().set_visible(False)
            # ax3.set_title('{}'.format('Suelo 1'))
            ax3.set_yticks(y_pos)

            ax3.invert_yaxis()  # labels read top-to-bottom
            plt.xlim([0, 5])

            plt.savefig(r'C:\Users\FRANCISCO\Documents\agrae\Paneles\graficos\demo.png', dpi=200, transparent=True)
            # plt.show()

            img = Image.open(r'C:\Users\FRANCISCO\Documents\agrae\Paneles\graficos\demo.png')


            #img = img.resize((100,100))
            base = Image.open(os.path.join(os.path.dirname(__file__), r'ui\img\base.png'))
            base = base.resize((1280, 960))
            panel = Image.new('RGB', (1280, 960), color='white')
            panel.paste(base, (0, 0))
            panel.paste(img, (100, 20), mask=img)
            #panel.show()
            panel.save(r'C:\Users\FRANCISCO\Documents\agrae\Paneles\panel-{}.png'.format(lyrName[10:]))

            width, height = img.size




        if not self.pluginIsActive:
            self.pluginIsActive = True

            if self.mainWindowDialog == None:
                icons_path = {
                    'search_icon_path': os.path.join(os.path.dirname(__file__), r'ui\icons\search.svg'),
                    'add_layer_to_map': os.path.join(os.path.dirname(__file__), r'ui\icons\layer-add-o.svg')
                }

                
                self.mainWindowDialog = agraeMainWidget()

                

                
                # self.mainWindowDialog.btn_lote_update.setEnabled(False)
                # self.mainWindowDialog.pushButton_2.clicked.connect(printMap)
                
            self.mainWindowDialog.closingPlugin.connect(self.onClosePluginMain)
            self.mainWindowDialog.show()
        pass
    
    def relLote(self): 
        # print('testing')
        if not self.pluginIsActive:
            self.pluginIsActive = True

            if self.loteFindDialog == None:

                self.loteFindDialog = loteFindDialog()
                self.loteFindDialog.setWindowTitle('Agrupar Parcelas')
                # self.loteFindDialog.btn_cargar_lote.setEnabled(False)
                self.loteFindDialog.loadData()
                self.iface.actionSelect().trigger()



            self.loteFindDialog.closingPlugin.connect(self.onCloseLoteDialog)
            self.loteFindDialog.show()

    def uploadRecintos(self):
        # print('Cargar Recintos a BD')
        self.tools.crearParcela()

    def filtrarLotes(self): 
        if not self.pluginIsActive:
            self.pluginIsActive = True

            if self.loteFilterDialog == None:

                self.loteFilterDialog = loteFilterDialog()

            self.loteFilterDialog.closingPlugin.connect(
                self.onCloseLoteFilterDialog)
            self.loteFilterDialog.show()
    
    def filtrarParcelas(self):
        if not self.pluginIsActive:
            self.pluginIsActive = True

            if self.parcelaFilterDialog == None:
                self.parcelaFilterDialog = parcelaFindDialog()

            self.parcelaFilterDialog.closingPlugin.connect(
                self.onCloseParcelaFilterDialog)
            self.parcelaFilterDialog.show()

    

    def runDatos(self): 
        if not self.pluginIsActive:
            self.pluginIsActive = True

            if self.datosDialog == None:
                self.datosDialog = gestionDatosDialog()
                # self.configDialog.closingPlugin2.connect(self.onClosePluginConfig)

                # self.datosDialog.test_btn.clicked.connect(dbTestConn)
                # self.datosDialog.pushButton.clicked.connect(saveConn)

            self.datosDialog.closingPlugin.connect(self.onCloseDatosDialog)
            self.datosDialog.show()

    def runVerifyGeometry(self): 

        if not self.pluginIsActive:
            self.pluginIsActive = True

            if self.verifyGeomDialog == None:
                self.verifyGeomDialog = verifyGeometryDialog()
                # self.verifyGeomDialog.getMapLayers()
            self.verifyGeomDialog.closingPlugin.connect(self.onCloseVerifyGeomDialog)
            self.verifyGeomDialog.show()

    def runVeris(self):
        if not self.pluginIsActive:
            self.pluginIsActive = True

            if self.verisDataDialog == None:
                self.verisDataDialog = ceapPrevDialog()
                # self.configDialog.closingPlugin2.connect(self.onClosePluginConfig)

                # self.datosDialog.test_btn.clicked.connect(dbTestConn)
                # self.datosDialog.pushButton.clicked.connect(saveConn)

            self.verisDataDialog.closingPlugin.connect(
                self.onCloseCeapDialog)
            self.verisDataDialog.show()


    def runApplied(self):
        if not self.pluginIsActive:
            self.pluginIsActive = True

            if self.appliedDataDialog == None: 
                self.appliedDataDialog = appliedLayerDialog()

            
            self.appliedDataDialog.closingPlugin.connect(self.onCloseAppliedDialog)
            self.appliedDataDialog.show()

        # lyr = self.iface.activeLayer() 
        # feat = [f for f in lyr.getSelectedFeatures()]
        # ids = set([str(f[1]) for f in feat])
        # values = '( ' + ', '.join(ids) + ' )'
        # # print(values)

        # sql = '''insert into public.reticulabase (geometria,idlotecampania)
        #     with grid as (
        #     select (st_squaregrid(10, st_transform(geometria,25830))).* 
        #     from public.lotes 
        #     where idlotecampania in {}
        #     ) 
        #     select st_transform(g.geom,4326) as geometria, l.idlotecampania from grid g
        #     join public.lotes l on st_intersects(l.geometria , st_transform(g.geom,4326)) ;'''.format(values)
        
        # print(sql)

        # with self.utils.conn().cursor() as cursor:


            
        

        # self.tools.crearRindes()
            
        pass

    def runDosis(self):
        if not self.pluginIsActive:
            self.pluginIsActive = True

            if self.dosisDialog == None: 
                self.dosisDialog = agraeDosificacion()

            
            self.dosisDialog.closingPlugin.connect(self.onCloseDosisDialog)
            self.dosisDialog.show()

