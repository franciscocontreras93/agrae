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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt, QVariant
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QTableWidgetItem
from qgis.core import *
import pip
import random

from qgis import processing
# Initialize Qt resources from file resources.py
from .resources import *
from .dbconn import DbConnection
from .utils import AgraeUtils

# Import the code for the DockWidget
from .agrae_dockwidget import agraeDockWidget, agraeConfigWidget, agraeMainWidget
import os.path
from qgis.core import QgsDataSourceUri

try:
    import psycopg2
    import psycopg2.extras
except: 
    pip.main('install','psycopg2')
    import psycopg2
    import psycopg2.extras

try: 
    import numpy as np
except:
    pip.main('install', 'numpy')
    import numpy as np
try:
    import matplotlib as mpl
    import matplotlib.pyplot as plt
except:
    pip.main('install', 'matplotlib')
    import matplotlib as mpl
    import matplotlib.pyplot as plt
try: 
    import seaborn as sns
except:
    pip.main('install', 'seaborn')
    import seaborn as sns

    


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
        self.conn = self.utils.Conn()
        self.dbset = QSettings('agrae','dbConnection')

        self.nameLayerComposer = None



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
        self.toolbar = self.iface.addToolBar(u'agrae')
        self.toolbar.setObjectName(u'agrae')
        self.queryCapaLotes = ''

        #print "** INITIALIZING agrae"

        self.pluginIsActive = False
        self.dockwidget = None
        self.configDialog = None
        self.mainWindowDialog = None

        


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

        icon_path = ':/plugins/agrae/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'aGrae GIS'),
            callback=self.runMain,
            parent=self.iface.mainWindow())
        # self.add_action(
        #     '',
        #     text=self.tr(u'Agregar Objeto'),
        #     callback=self.runMain,
        #     parent=self.iface.mainWindow())
        self.add_action(
            '',
            text=self.tr(u'Ajustes'),
            add_to_toolbar=False,
            callback=self.runConfig,
            parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        self.dockwidget.inputLay.clear()
        self.dockwidget.superLay.clear()
        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)


        self.pluginIsActive = False

    def onClosePluginConfig(self):
        # disconnects
        self.configDialog.closingPlugin2.disconnect(self.onClosePluginConfig)
        self.pluginIsActive = False
    
    def onClosePluginMain(self):

        # disconnects
        self.mainWindowDialog.closingPlugin.disconnect(
            self.onClosePluginMain)
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
               



        if not self.pluginIsActive:
            self.pluginIsActive = True
        
            if self.configDialog == None:
                self.configDialog = agraeConfigWidget()
                # self.configDialog.closingPlugin2.connect(self.onClosePluginConfig)
                

                self.configDialog.test_btn.clicked.connect(dbTestConn)
                self.configDialog.pushButton.clicked.connect(saveConn)
            
            self.configDialog.closingPlugin2.connect(self.onClosePluginConfig)
            self.configDialog.show()


        pass


    def runMain(self):
        def loadLayer():
            sql = self.queryCapaLotes
            dns = self.utils.ConnParams()
            row = self.mainWindowDialog.tableWidget.currentRow()
            column = self.mainWindowDialog.tableWidget.currentColumn()
           

            try:
                uri = QgsDataSourceUri()
                uri.setConnection(dns['host'], dns['port'], dns['dbname'], dns['user'], dns['password'])
                uri.setDataSource('', f'({sql})', 'geometria', '', 'idparcela')
                nombre = self.mainWindowDialog.tableWidget.item(row, column)
                if nombre.text() == None:
                    nombre = self.mainWindowDialog.tableWidget.item(0, 1)
                    layer = self.iface.addVectorLayer(uri.uri(False), nombre.text(), 'postgres')
                else: 
                    layer = self.iface.addVectorLayer(uri.uri(False), nombre.text(), 'postgres')
                    
                if layer.isValid():
                    QgsProject.instance().addMapLayer(layer)
                    self.iface.setActiveLayer(layer)
                    self.iface.zoomToActiveLayer()
                    print(f"Capa añadida correctamente ")
                    

                else:
                    # uri.setDataSource('public', tablename, None)
                    # layer = QgsVectorLayer(
                    #     uri.uri(False), tablename, 'postgres')
                    # QgsProject.instance().addMapLayer(layer)
                    QMessageBox.about(self, "aGrae GIS:", "La capa no es Valida")
            
            except Exception as ex:
                QMessageBox.about(self.mainWindowDialog, f"Error:{ex}", f"Debe seleccionar un campo para el Nombre")
        
        def cargarLotesParcelas():
            
            param = self.mainWindowDialog.line_buscar.text()
            sqlQuery = ''
            try: 
                with self.conn as conn:
                    if param == '':
                        sqlQuery = f'''select p.idparcela , l.idlote, l.nombre lote, p.nombre parcela, c.nombre cultivo, p.geometria from parcela p left join loteparcela lp on p.idparcela = lp.idparcela left join lote l on l.idlote = lp.idlote left join cultivo c on c.idcultivo = l.idcultivo where p.idparcela in(lp.idparcela) order by l.idlote'''
                        self.mainWindowDialog.btn_add_layer.setEnabled(False)

                    elif self.mainWindowDialog.radio_id.isChecked() and param != '':
                        sqlQuery = f'''select p.idparcela , l.idlote, l.nombre lote, p.nombre parcela, c.nombre cultivo, p.geometria from parcela p left join loteparcela lp on p.idparcela = lp.idparcela left join lote l on l.idlote = lp.idlote left join cultivo c on c.idcultivo = l.idcultivo  where p.idparcela in(lp.idparcela) and p.idparcela = {param} or l.idlote = {param} order by p.idparcela'''
                        self.mainWindowDialog.btn_add_layer.setEnabled(True)

                        # sqlQuery = f'select * from rel_parcelas_lote where idparcela = {param} or idlote = {param}'
                        
                    elif self.mainWindowDialog.radio_nombre.isChecked() and param != '':
                        sqlQuery = f"""select p.idparcela , l.idlote, l.nombre lote, p.nombre parcela, c.nombre cultivo, p.geometria from parcela p left join loteparcela lp on p.idparcela = lp.idparcela left join lote l on l.idlote = lp.idlote left join cultivo c on c.idcultivo = l.idcultivo  where p.idparcela in(lp.idparcela) and p.nombre ilike '%{param}%' or l.nombre ilike '%{param}%' or c.nombre ilike '%{param}%' order by p.idparcela"""
                        self.mainWindowDialog.btn_add_layer.setEnabled(True)
                    
                    
                    cursor = conn.cursor()
                    cursor.execute(sqlQuery)
                    data = cursor.fetchall()
                    if len(data) == 0:
                        QMessageBox.about(
                            self.mainWindowDialog, "aGrae GIS:", "La Parcela o el Lote que buscas no se encuentra relacionado.\nDebes crear una nueva relacion")
            
                        # self.iface.messageBar().pushMessage(
                        #     "aGrae GIS", "No Existe la relacion de lotes y parcelas.\nDebes crear una nueva relacion", level=1, duration=5)
                    else:
                        # self.mainWindowDialog.btn_add_layer.setEnabled(True)
                        self.queryCapaLotes = sqlQuery
                        a = len(data)
                        b = len(data[0])
                        i = 1
                        j = 1
                        self.mainWindowDialog.tableWidget.setRowCount(a)
                        self.mainWindowDialog.tableWidget.setColumnCount(b)
                        for j in range(a):
                            for i in range(b):
                                item = QTableWidgetItem(str(data[j][i]))
                                self.mainWindowDialog.tableWidget.setItem(j,i,item)
                        # print(data)
                        # funct = loadLayer(sqlQuery)
            
            except Exception as ex: 
                QMessageBox.about(self.mainWindowDialog, "Error:", f"Verifica el Parametro de Consulta (ID o Nombre)")

        def crearParcela():
            try:
                with self.conn as conn:
                    cur = conn.cursor()
                layer = self.iface.activeLayer()
                # print(layer.name())
                feat = layer.selectedFeatures()
                ls = feat[0].geometry().asWkt()
                srid = layer.crs().authid()[5:]

                name = str(self.mainWindowDialog.ln_par_nombre.text())
                prov = str(self.mainWindowDialog.ln_par_provincia.text())
                mcpo = str(self.mainWindowDialog.ln_par_mcpo.text())
                aggregate = str(self.mainWindowDialog.ln_par_agg.text())
                zone = str(self.mainWindowDialog.ln_par_zona.text())
                poly = str(self.mainWindowDialog.ln_par_poly.text())
                allotment = str(self.mainWindowDialog.ln_par_parcela.text())
                inclosure = str(self.mainWindowDialog.ln_par_recinto.text())

                # print(ls)
                sql = f'''INSERT INTO parcela(nombre,provincia,municipio,agregado,zona,poligono,parcela,recinto,geometria) VALUES('{name}','{prov}','{mcpo}','{aggregate}','{zone}','{poly}','{allotment}','{inclosure}',st_multi(st_force2d(st_transform(st_geomfromtext('{ls}',{srid}),4326))))'''
                cur.execute(sql)
                conn.commit()
                # print('agregado correctamente')
                QMessageBox.about(self.mainWindowDialog,f"aGrae GIS:", "Parcela *-- {name} --* Creada Correctamente.\nCrear Relacion Lote Parcelas.")

            except Exception as ex:
                print(ex)
                QMessageBox.about(self.mainWindowDialog, f"aGrae GIS",f"No se pudo almacenar el registro {ex}")

            finally: 
                self.mainWindowDialog.ln_par_nombre.setText('')
                self.mainWindowDialog.ln_par_provincia.setText('')
                self.mainWindowDialog.ln_par_mcpo.setText('')
                self.mainWindowDialog.ln_par_agg.setText('')
                self.mainWindowDialog.ln_par_zona.setText('')
                self.mainWindowDialog.ln_par_poly.setText('')
                self.mainWindowDialog.ln_par_parcela.setText('')
                self.mainWindowDialog.ln_par_recinto.setText('')

        def dataLoteParcela(param='',inicial=False):
            with self.conn as conn:
                if inicial == False:
                    if self.mainWindowDialog.radio_id.isChecked():
                        sqlQuery = f'''select p.idparcela , l.idlote, l.nombre lote, p.nombre parcela, c.nombre cultivo, p.geometria from parcela p left join loteparcela lp on p.idparcela = lp.idparcela left join lote l on l.idlote = lp.idlote left join cultivo c on c.idcultivo = l.idcultivo  where p.idparcela = {param} or l.idlote = {param}'''

                        # sqlQuery = f'select * from rel_parcelas_lote where idparcela = {param} or idlote = {param}'

                    elif self.mainWindowDialog.radio_nombre.isChecked():
                        sqlQuery = f"""select p.idparcela , l.idlote, l.nombre lote, p.nombre parcela, c.nombre cultivo, p.geometria from parcela p left join loteparcela lp on p.idparcela = lp.idparcela left join lote l on l.idlote = lp.idlote left join cultivo c on c.idcultivo = l.idcultivo  where p.nombre ilike '%{param}%' or l.nombre ilike '%{param}%' or c.nombre ilike '%{param}%'"""

                elif inicial == True:                    
                    sqlQuery = f'''select p.idparcela , l.idlote, l.nombre lote, p.nombre parcela, c.nombre cultivo, p.geometria from parcela p left join loteparcela lp on p.idparcela = lp.idparcela left join lote l on l.idlote = lp.idlote left join cultivo c on c.idcultivo = l.idcultivo'''

                cursor = conn.cursor()
                cursor.execute(sqlQuery)
                data = cursor.fetchall()
                if len(data) == 0:
                    QMessageBox.about(
                        self.mainWindowDialog, "aGrae GIS:", "No Existe la relacion de lotes y parcelas.\nDebes crear una nueva relacion")

                else:
                    return data
            
        def printMap():
            import math 
            barPlot()
            #! LAYOUTMANAGER INSTANCIA
            manager = QgsProject.instance().layoutManager() 
            layoutName = self.iface.activeLayer().name()
            manager_list = manager.printLayouts() 

            for l in manager_list:
                if l.name() == layoutName :
                    manager.removeLayout(l)
            
            #print(lyrs)
            


            layout = QgsPrintLayout(QgsProject.instance())
            layout.initializeDefaults() 
            layout.setName(layoutName)
            manager.addLayout(layout)

            lyrsDict = QgsProject().instance().mapLayers()
            lyrs = [lyrsDict[lyr] for lyr in lyrsDict]
            colors = [l.renderer().symbol().color().name() for l in lyrs]
            print(colors)
            # for l in lyrs:
            #     color = 
            #     colors.append(color)
            
            
            ms = QgsMapSettings()
            
            ms.setLayers(lyrs)            
            extent = QgsProject.instance().mapLayersByName(layoutName)[0].extent()
            lyrScale = self.iface.mapCanvas().scale()
            scale = math.ceil((lyrScale / 200)) * 200
            print(scale)
            # extent.scale(1.0)
            # ms.setExtent(extent)
            #! MAP ITEM
            map = QgsLayoutItemMap(layout)
            map.setRect(20,20,20,20)
            map.setExtent(extent)
            map.setScale(math.floor(scale*10))
            # map.setBackgroundColor(QColor(255,255,225,0))
            map.attemptMove(QgsLayoutPoint(5, 5,QgsUnitTypes.LayoutMillimeters))
            map.attemptResize(QgsLayoutSize(180, 180,QgsUnitTypes.LayoutMillimeters))

            #! BARPLOT
            barplot = QgsLayoutItemPicture(layout)
            barplot.setMode(QgsLayoutItemPicture.FormatRaster)
            barplot.setPicturePath(r'C:\Users\FRANCISCO\Desktop\demo.png')
            barplot.setResizeMode(QgsLayoutItemPicture.ZoomResizeFrame)
            # barplot.setRect(20, 20, 20, 20)
            # dim_barplot = [640, 480]
            barplot.attemptMove(QgsLayoutPoint(212, 5, QgsUnitTypes.LayoutMillimeters))
            barplot.attemptResize(QgsLayoutSize(80, 60, QgsUnitTypes.LayoutMillimeters))





            #! ADD ITEMS TO LAYOUT 
            layout.addLayoutItem(map)
            layout.addLayoutItem(barplot)


            pass            

        def barPlot():
            lyrsDict = QgsProject().instance().mapLayers()
            lyrs = [lyrsDict[lyr] for lyr in lyrsDict]
            colors = [l.renderer().symbol().color().name() for l in lyrs]
            # colors = ['#a47158', '#85b66f', '#85006f']
            print(colors)

            sns.set_style('darkgrid')
            conn = psycopg2.connect(
                'host=localhost dbname=agrae user=postgres password=23826405')
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            sql = '''select l.nombre ,sum(st_area(st_transform(p.geometria,25830))/10000) area
                    from parcela p
                    join loteparcela lp on p.idparcela = lp.idparcela 
                    join lote l on l.idlote = lp.idlote
                    group by l.nombre'''
            cursor.execute(sql)
            result = cursor.fetchall()
            nombre = [e[0] for e in result]
            data = [e[1] for e in result]

            print(nombre, data,)


            ypos = np.arange(len(nombre))
            plt.xticks(ypos, nombre)
            plt.ylabel('Area Parcela (Ha)')
            # plt.bar(ypos, data)

            plt.bar(ypos, data, color=colors)

            plt.show()\
# plt.savefig(r'C:\Users\FRANCISCO\Desktop\demo.png')
        if not self.pluginIsActive:
            self.pluginIsActive = True

            if self.mainWindowDialog == None:
                self.mainWindowDialog = agraeMainWidget()
                # cargar = loadLayer(self.queryCapaLotes)
                self.mainWindowDialog.btn_buscar1.clicked.connect(cargarLotesParcelas)
                # self.mainWindowDialog.btn_buscar2.clicked.connect(buscarLote)
                self.mainWindowDialog.btn_add_layer.clicked.connect(loadLayer)
                self.mainWindowDialog.btn_par_create.clicked.connect(crearParcela)
                # self.mainWindowDialog.tableWidget.setColumnHidden(0, True)
                # self.mainWindowDialog.tableWidget.setColumnHidden(5, True)
                # self.mainWindowDialog.loadButton.clicked.connect(loadAllotmentToDB)
                self.mainWindowDialog.btn_lote_update.setEnabled(False)
                self.mainWindowDialog.pushButton_2.clicked.connect(printMap)

            self.mainWindowDialog.closingPlugin.connect(self.onClosePluginMain)

            self.mainWindowDialog.show()
        pass
    
