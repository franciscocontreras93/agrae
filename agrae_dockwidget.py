# -*- coding: utf-8 -*-
"""
/***************************************************************************
 agraeDockWidget
                                 A QGIS plugin
 Conjunto de herramientas
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
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

import os

from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal, QSettings

agraeSidePanel, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/agrae_dockwidget_base.ui'))
agraeConfigPanel, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/config_ui.ui'))
agraeAddFeaturePanel, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/addFeature.ui'))


class agraeDockWidget(QtWidgets.QDockWidget, agraeSidePanel):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(agraeDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://doc.qt.io/qt-5/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()


class agraeConfigWidget(QtWidgets.QDialog, agraeConfigPanel):

    closingPlugin2 = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(agraeConfigWidget, self).__init__(parent)

        self.s = QSettings('agrae','dbhost')
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://doc.qt.io/qt-5/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        

    def closeEvent(self, event):
        self.closingPlugin2.emit()
        event.accept()


class addFeatureWidget(QtWidgets.QDialog, agraeAddFeaturePanel):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(addFeatureWidget, self).__init__(parent)

        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://doc.qt.io/qt-5/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
