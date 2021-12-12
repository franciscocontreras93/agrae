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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import *
# Initialize Qt resources from file resources.py
from .resources import *
from .dbconn import DbConnection
from .utils import AgraeUtils

# Import the code for the DockWidget
from .agrae_dockwidget import agraeDockWidget,agraeConfigWidget
import os.path
from qgis.core import QgsDataSourceUri


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

        #print "** INITIALIZING agrae"

        self.pluginIsActive = False
        self.dockwidget = None
        self.configDialog = None

        


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
            callback=self.run,
            parent=self.iface.mainWindow())
        self.add_action(
            '',
            text=self.tr(u'Ajustes'),
            add_to_toolbar=False,
            callback=self.runConfig,
            parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def onClosePlugin(self):

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)


        self.pluginIsActive = False

    def onClosePluginConfig(self):
        # disconnects
        self.configDialog.closingPlugin2.disconnect(self.onClosePluginConfig)
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
                layerList = self.utils.loadGeomLayers()
                for i in layerList:
                    self.dockwidget.layers_combo.addItem(i.upper())
                    
            else: 
                self.dockwidget.layers_combo.clear()
                layerList = self.utils.loadLayers()
                for i in layerList:
                    self.dockwidget.layers_combo.addItem(i.upper())

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
                                (SELECT (ST_Dump(makegrid(geometria, 121))).geom from {table}
                                where {field_names[1]} = {idfeat}) '''
                        cur.execute(sql)
                        conn.commit()
                        self.iface.messageBar().pushMessage(
                            'aGraes GIS', 'Registro creado Correctamente', level=3, duration=3)

                except:
                    self.iface.messageBar().pushMessage(
                        'aGraes GIS | ERROR: ', 'No se pudo almacenar el registro', level=1, duration=3)

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
            for i in self.utils.loadGeomLayers():
                self.dockwidget.combo_load_layers.addItem(i.upper())
            
            self.dockwidget.load_feat_btn.clicked.connect(loadFeatureToDB)



                
            
                        
                

                
                



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
                        self.configDialog.dbname.text(), self.configDialog.user.text(), self.configDialog.password.text(), self.configDialog.host.text())
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
