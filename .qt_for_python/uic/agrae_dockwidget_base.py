# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'agrae_dockwidget_base.ui'
##
## Created by: Qt User Interface Compiler version 6.1.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *  # type: ignore
from PySide6.QtGui import *  # type: ignore
from PySide6.QtWidgets import *  # type: ignore


class Ui_agraeDockWidgetBase(object):
    def setupUi(self, agraeDockWidgetBase):
        if not agraeDockWidgetBase.objectName():
            agraeDockWidgetBase.setObjectName(u"agraeDockWidgetBase")
        agraeDockWidgetBase.resize(300, 500)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(agraeDockWidgetBase.sizePolicy().hasHeightForWidth())
        agraeDockWidgetBase.setSizePolicy(sizePolicy)
        agraeDockWidgetBase.setMinimumSize(QSize(300, 163))
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.gridLayout = QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName(u"gridLayout")
        self.toolBox = QToolBox(self.dockWidgetContents)
        self.toolBox.setObjectName(u"toolBox")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.page.setGeometry(QRect(0, 0, 282, 406))
        self.geom_check = QCheckBox(self.page)
        self.geom_check.setObjectName(u"geom_check")
        self.geom_check.setGeometry(QRect(0, 60, 174, 17))
        self.list_btn = QPushButton(self.page)
        self.list_btn.setObjectName(u"list_btn")
        self.list_btn.setGeometry(QRect(180, 29, 89, 23))
        self.layers_combo = QComboBox(self.page)
        self.layers_combo.setObjectName(u"layers_combo")
        self.layers_combo.setGeometry(QRect(0, 30, 174, 20))
        self.load_1_btn = QPushButton(self.page)
        self.load_1_btn.setObjectName(u"load_1_btn")
        self.load_1_btn.setGeometry(QRect(0, 220, 261, 23))
        self.label = QLabel(self.page)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(0, 10, 171, 16))
        self.toolBox.addItem(self.page, u"Cargar Capas")
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.page_2.setGeometry(QRect(0, 0, 282, 406))
        self.toolBox.addItem(self.page_2, u"Page 2")

        self.gridLayout.addWidget(self.toolBox, 0, 0, 1, 1)

        agraeDockWidgetBase.setWidget(self.dockWidgetContents)

        self.retranslateUi(agraeDockWidgetBase)

        self.toolBox.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(agraeDockWidgetBase)
    # setupUi

    def retranslateUi(self, agraeDockWidgetBase):
        agraeDockWidgetBase.setWindowTitle(QCoreApplication.translate("agraeDockWidgetBase", u"aGrae GIS", None))
        self.geom_check.setText(QCoreApplication.translate("agraeDockWidgetBase", u"Listar solo tablas con geometria", None))
        self.list_btn.setText(QCoreApplication.translate("agraeDockWidgetBase", u"Listar", None))
        self.load_1_btn.setText(QCoreApplication.translate("agraeDockWidgetBase", u"Anadir Capa al Mapa", None))
        self.label.setText(QCoreApplication.translate("agraeDockWidgetBase", u"Lista de Tablas", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page), QCoreApplication.translate("agraeDockWidgetBase", u"Cargar Capas", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_2), QCoreApplication.translate("agraeDockWidgetBase", u"Page 2", None))
    # retranslateUi

