# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Users\FRANCISCO\AppData\Roaming\QGIS\QGIS3\profiles\agrae\python\plugins\agrae\ui\config_ui.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(327, 240)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QtCore.QSize(327, 240))
        Dialog.setMaximumSize(QtCore.QSize(327, 240))
        self.gridLayoutWidget = QtWidgets.QWidget(Dialog)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 10, 311, 221))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(5, 5, 5, 5)
        self.gridLayout.setObjectName("gridLayout")
        self.test_btn = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.test_btn.setObjectName("test_btn")
        self.gridLayout.addWidget(self.test_btn, 5, 0, 1, 1)
        self.host = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.host.setObjectName("host")
        self.gridLayout.addWidget(self.host, 0, 1, 1, 1)
        self.password = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.password.setObjectName("password")
        self.gridLayout.addWidget(self.password, 3, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.dbname = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.dbname.setObjectName("dbname")
        self.gridLayout.addWidget(self.dbname, 1, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.user = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.user.setObjectName("user")
        self.gridLayout.addWidget(self.user, 2, 1, 1, 1)
        self.port = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.port.setObjectName("port")
        self.gridLayout.addWidget(self.port, 4, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.pushButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 5, 1, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.host, self.dbname)
        Dialog.setTabOrder(self.dbname, self.user)
        Dialog.setTabOrder(self.user, self.password)
        Dialog.setTabOrder(self.password, self.port)
        Dialog.setTabOrder(self.port, self.test_btn)
        Dialog.setTabOrder(self.test_btn, self.pushButton)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "aGrae GIS "))
        self.test_btn.setText(_translate("Dialog", "Probar Conexion"))
        self.label_3.setText(_translate("Dialog", "Usuario:"))
        self.label_2.setText(_translate("Dialog", "Base de Datos:"))
        self.label_5.setText(_translate("Dialog", "Puerto:"))
        self.label_4.setText(_translate("Dialog", "Contraseña:"))
        self.label.setText(_translate("Dialog", "Host:"))
        self.pushButton.setText(_translate("Dialog", "Guardar Ajustes"))

