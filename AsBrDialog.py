# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AsBrDialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AsBrOverlap(object):
    def setupUi(self, AsBrOverlap):
        AsBrOverlap.setObjectName("AsBrOverlap")
        AsBrOverlap.resize(181, 117)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AsBrOverlap.sizePolicy().hasHeightForWidth())
        AsBrOverlap.setSizePolicy(sizePolicy)
        self.verticalLayoutWidget = QtWidgets.QWidget(AsBrOverlap)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 20, 161, 80))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.YesClick = QtWidgets.QPushButton(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.YesClick.sizePolicy().hasHeightForWidth())
        self.YesClick.setSizePolicy(sizePolicy)
        self.YesClick.setObjectName("YesClick")
        self.horizontalLayout.addWidget(self.YesClick)
        self.NoClick = QtWidgets.QPushButton(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.NoClick.sizePolicy().hasHeightForWidth())
        self.NoClick.setSizePolicy(sizePolicy)
        self.NoClick.setObjectName("NoClick")
        self.horizontalLayout.addWidget(self.NoClick)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(AsBrOverlap)
        QtCore.QMetaObject.connectSlotsByName(AsBrOverlap)

    def retranslateUi(self, AsBrOverlap):
        _translate = QtCore.QCoreApplication.translate
        AsBrOverlap.setWindowTitle(_translate("AsBrOverlap", "Dialog"))
        self.label.setText(_translate("AsBrOverlap", "Overlap As-Br Peaks"))
        self.YesClick.setText(_translate("AsBrOverlap", "Yes"))
        self.NoClick.setText(_translate("AsBrOverlap", "No"))

