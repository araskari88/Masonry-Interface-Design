import sys
from PyQt4.QtGui import *
from PyQt4.QtGui import *
from PyQt4.QtCore import pyqtSlot
import numpy as np
import pandas as pd
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, SIGNAL, QSize, QRect
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import vtk
import os
import re
import readAnalysis_func

colors = vtk.vtkNamedColors()
# define necessary functions

class mainActions():
    def __init__(self):
        super().__init__()
        self.mainSidePanel = QTreeWidget()
        self.mainSidePanel.setSelectionMode(3)

        self.propertySidePanel = QWidget()
        self.toggleFill = "on"
        self.prjName = ''

    def notEmptTxtChng(self, prjName, OKprjNameBtn):
        print(prjName.text())
        if prjName.text() == '':
            OKprjNameBtn.setDisabled(True)
        else:
            OKprjNameBtn.setDisabled(False)

    def newFile(self):
        print("new file")

    def openFile(self):
        global appMode, material, node, wall, element, polygon, analysis, fixConstraint, w2wConstraint, f2wConstraint, restraintActors, totalAnalysis, callCounter, storeElementPatch
        path = QtGui.QFileDialog.getOpenFileName(parent=mWindow, caption="Select existing Tremuri or OpenSees file",
                                                 filter='Tremuri text files (*.txt);;OpenSees TCL files (*.tcl)')

        if path:
            file = QtCore.QFile(path)

            prjNameDialog = QtGui.QDialog()
            prjNameDialogLayout = QGridLayout()
            prjNameTtl = QLabel("Please specify the project name below:")
            prjName = QLineEdit()

            OKprjNameBtn = QPushButton('Apply', widget)
            OKprjNameBtn.setToolTip('Click to Set')
            OKprjNameBtn.clicked.connect(lambda: get_prjName(prjName, mWindow, prjNameDialog))
            OKprjNameBtn.resize(OKprjNameBtn.sizeHint())
            OKprjNameBtn.move(100, 80)
            OKprjNameBtn.setDisabled(True)

            prjName.textChanged.connect(lambda: self.notEmptTxtChng(prjName, OKprjNameBtn))

            prjNameDialogLayout.addWidget(prjNameTtl, 1, 1)
            prjNameDialogLayout.addWidget(prjName, 2, 1)
            prjNameDialogLayout.addWidget(OKprjNameBtn, 3, 1)
            prjNameDialog.setLayout(prjNameDialogLayout)
            prjNameDialog.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowTitleHint | QtCore.Qt.CustomizeWindowHint)
            prjNameDialog.setWindowTitle("Define project name")
            if prjNameDialog.exec_() == QtGui.QDialog.Accepted:
                prjNameDialog.show()

            if file.open(QtCore.QIODevice.ReadOnly):
                editMenu.setDisabled(False)
                defineMenu.setDisabled(False)
                assignMenu.setDisabled(False)
                analysisMenu.setDisabled(False)
                displayMenu.setDisabled(False)
                saveFileMenu.setDisabled(False)
                saveAsFileMenu.setDisabled(False)
                printFileMenu.setDisabled(False)
                exportFileMenu.setDisabled(False)
                stream = QtCore.QTextStream(file)
                text = stream.readAll()
                info = QtCore.QFileInfo(path)
                if info.completeSuffix() == 'txt':
                    appMode = "Tremuri"
                    import drawModelVTK_func
                    #import readAnalysis_func
                    drawModelVTK_func.completeFileLocation3 = path
                    drawModelVTK_func.drMoVTKFunc()
                    structureFrame = QtGui.QFrame()
                    structureLayout = QtGui.QGridLayout()
                    vtkWidget = QVTKRenderWindowInteractor(structureFrame)
                    structureLayout.addWidget(vtkWidget, 1, 1)
                    self.renderer = drawModelVTK_func.renderer
                    vtkWidget.GetRenderWindow().AddRenderer(self.renderer)
                    self.renderer.ResetCamera()
                    iren = vtkWidget.GetRenderWindow().GetInteractor()
                    IsoPos = self.renderer.GetActiveCamera().GetPosition()
                    IsoFocal = self.renderer.GetActiveCamera().GetFocalPoint()
                    IsoNearClip, IsoFarClip = self.renderer.GetActiveCamera().GetClippingRange()
                    structureFrame.setLayout(structureLayout)
                    mWindow.setCentralWidget(structureFrame)
                    iren.Initialize()

                    material = drawModelVTK_func.impMaterial.copy(deep=True)
                    element = drawModelVTK_func.impElement.copy(deep=True)
                    node = drawModelVTK_func.impNode.copy(deep=True)
                    wall = drawModelVTK_func.impWall.copy(deep=True)
                    floor = drawModelVTK_func.impFloor.copy(deep=True)
                    polygon = drawModelVTK_func.impPolygon.copy(deep=True)
                    analysis = drawModelVTK_func.impAnalysis.copy(deep=True)
                    fixConstraint = drawModelVTK_func.impFixConstraint.copy(deep=True)
                    w2wConstraint = drawModelVTK_func.impW2wConstraint.copy(deep=True)
                    f2wConstraint = drawModelVTK_func.impF2wConstraint.copy(deep=True)
                    storeElementPatch = drawModelVTK_func.storeElementPatch.copy(deep=True)
                    restraintActors = drawModelVTK_func.restraintActors.copy(deep=True)
                    self.restraintPlotter(self.renderer)  # Add the restraints to the view

                    maxX = drawModelVTK_func.maxX
                    minX = drawModelVTK_func.minX
                    maxY = drawModelVTK_func.maxY
                    minY = drawModelVTK_func.minY
                    maxZ = drawModelVTK_func.maxZ
                    minZ = drawModelVTK_func.minZ
                    totalAnalysis = analysis['type'].count()

                    # Create the left panel widget for model navigation
                    mainSidePanelLayout = QVBoxLayout()
                    mainSidePanelLayout.setContentsMargins(5, 0, 5, 0)
                    self.mainSidePanel.setFixedWidth(300)
                    self.mainSidePanel.setColumnCount(1)
                    self.mainSidePanel.setHeaderHidden(True)

                    topLevelItems = ["Model", "Analyze", "Constraints/Restraints", "Loads", "Boundary Conditions", "Results"]
                    topLevelItemList = []
                    for tlItem in topLevelItems:
                        topLevelItemList.append(QTreeWidgetItem([tlItem]))
                        self.mainSidePanel.addTopLevelItem(topLevelItemList[-1])

                    ModelTreeItems = ["Nodes", "Elements"]
                    ModelTreeItemList = []
                    for mtItem in ModelTreeItems:
                        ModelTreeItemList.append(QTreeWidgetItem([mtItem]))
                        topLevelItemList[topLevelItems.index("Model")].addChild(ModelTreeItemList[-1])

                    self.nodeIndexList = node.index.to_list()
                    self.nodeIndexList.sort()
                    self.nodeItemList = []
                    nodeGroupItemList = []
                    remainingNodes = len(self.nodeIndexList)
                    remainingNodesList = self.nodeIndexList
                    [self.nodeItemList, nodeGroupItemList] = self.handleTreeItems(remainingNodes, nodeGroupItemList, remainingNodesList, self.nodeItemList, ModelTreeItemList, ModelTreeItems, "Nodes")

                    elementTreeItems = ["Floors", "Piers", "Spandrels", "Beams", "Zero Lengths"]
                    elementTreeItemList = []
                    for elItem in elementTreeItems:
                        elementTreeItemList.append(QTreeWidgetItem([elItem]))
                        ModelTreeItemList[ModelTreeItems.index("Elements")].addChild(elementTreeItemList[-1])  # child of elements

                    beamElementTreeItems = ["Elastic Beams", "Nonlinear Beams"]
                    beamElementTreeItemList = []
                    for beamElItem in beamElementTreeItems:
                        beamElementTreeItemList.append(QTreeWidgetItem([beamElItem]))
                        elementTreeItemList[elementTreeItems.index("Beams")].addChild(beamElementTreeItemList[-1])  # add elastic beam type

                    storeFloorPatch = storeElementPatch[storeElementPatch['Element Type'] == 'FloorShell']
                    self.elementFloorIndexList = storeFloorPatch.index.to_list()
                    self.elementFloorIndexList.sort()
                    self.elementFloorItemList = []
                    elementFloorGroupItemList = []
                    remainingElementFloors = len(self.elementFloorIndexList)
                    remainingElementFloorsList = self.elementFloorIndexList
                    [self.elementFloorItemList, elementFloorGroupItemList] = self.handleTreeItems(remainingElementFloors, elementFloorGroupItemList, remainingElementFloorsList, self.elementFloorItemList, elementTreeItemList, elementTreeItems, "Floors")

                    storePierElementPatch = storeElementPatch[storeElementPatch['Element Type'] == 'Wall - Pier']
                    self.elementPierIndexList = storePierElementPatch.index.to_list()
                    self.elementPierIndexList.sort()
                    self.elementPierItemList = []
                    elementPierGroupItemList = []
                    remainingPiers = len(self.elementPierIndexList)
                    remainingPiersList = self.elementPierIndexList
                    [self.elementPierItemList, elementPierGroupItemList] = self.handleTreeItems(remainingPiers, elementPierGroupItemList, remainingPiersList, self.elementPierItemList, elementTreeItemList, elementTreeItems, "Piers")

                    storeSpandrelElementPatch = storeElementPatch[storeElementPatch['Element Type'] == 'Wall - Spandrel']
                    self.elementSpandrelIndexList = storeSpandrelElementPatch.index.to_list()
                    self.elementSpandrelIndexList.sort()
                    self.elementSpandrelItemList = []
                    elementSpandrelGroupItemList = []
                    remainingSpandrels = len(self.elementSpandrelIndexList)
                    remainingSpandrelsList = self.elementSpandrelIndexList
                    [self.elementSpandrelItemList, elementSpandrelGroupItemList] = self.handleTreeItems(remainingSpandrels, elementSpandrelGroupItemList, remainingSpandrelsList, self.elementSpandrelItemList, elementTreeItemList, elementTreeItems, "Spandrels")

                    storeElasticBeamElementPatch = storeElementPatch[storeElementPatch['Element Type'] == 'ElasticBeam']
                    self.elementElasticBeamIndexList = storeElasticBeamElementPatch.index.to_list()
                    self.elementElasticBeamIndexList.sort()
                    self.elementElasticBeamItemList = []
                    elementElasticBeamGroupItemList = []
                    remainingElasticBeams = len(self.elementElasticBeamIndexList)
                    remainingElasticBeamsList = self.elementElasticBeamIndexList
                    [self.elementElasticBeamItemList, elementElasticBeamGroupItemList] = self.handleTreeItems(remainingElasticBeams, elementElasticBeamGroupItemList, remainingElasticBeamsList, self.elementElasticBeamItemList, beamElementTreeItemList, beamElementTreeItems, "Elastic Beams")

                    storeNlinBeamElementPatch = storeElementPatch[storeElementPatch['Element Type'] == 'NonlinearBeam']
                    self.elementNlinBeamIndexList = storeNlinBeamElementPatch.index.to_list()
                    self.elementNlinBeamIndexList.sort()
                    self.elementNlinBeamItemList = []
                    elementNlinBeamGroupItemList = []
                    remainingNlinBeams = len(self.elementNlinBeamIndexList)
                    remainingNlinBeamsList = self.elementNlinBeamIndexList
                    [self.elementNlinBeamItemList, elementNlinBeamGroupItemList] = self.handleTreeItems(remainingNlinBeams, elementNlinBeamGroupItemList, remainingNlinBeamsList, self.elementNlinBeamItemList, beamElementTreeItemList, beamElementTreeItems, "Nonlinear Beams")

                    storeZlenElementPatch = storeElementPatch[storeElementPatch['Element Type'] == 'ZeroLength']
                    self.elementZlenIndexList = storeZlenElementPatch.index.to_list()
                    self.elementZlenIndexList.sort()
                    self.elementZlenItemList = []
                    elementZlenGroupItemList = []
                    remainingZlens = len(self.elementZlenIndexList)
                    remainingZlensList = self.elementZlenIndexList
                    [self.elementZlenItemList, elementZlenGroupItemList] = self.handleTreeItems(remainingZlens, elementZlenGroupItemList, remainingZlensList, self.elementZlenItemList, elementTreeItemList, elementTreeItems, "Zero Lengths")

                    ConstraintTreeItems = ["Constraints", "Restraints [Node No.]"]
                    ConstraintTreeItemList = []
                    for ctItem in ConstraintTreeItems:
                        ConstraintTreeItemList.append(QTreeWidgetItem([ctItem]))
                        topLevelItemList[topLevelItems.index("Constraints/Restraints")].addChild(ConstraintTreeItemList[-1])

                    storeZlenElementPatch = storeElementPatch[storeElementPatch['Element Type'] == 'ZeroLength']
                    self.restraintIndexList = restraintActors.index.to_list()
                    self.restraintIndexList.sort()
                    self.restraintItemList = []
                    restraintGroupItemList = []
                    remainingRestraints = len(self.restraintIndexList)
                    remainingRestraintList = self.restraintIndexList
                    [self.restraintItemList, restraintGroupItemList] = \
                        self.handleTreeItems(remainingRestraints, restraintGroupItemList, remainingRestraintList,
                                             self.restraintItemList, ConstraintTreeItemList, ConstraintTreeItems, "Restraints [Node No.]")

                    self.mainSidePanel.setContextMenuPolicy(Qt.CustomContextMenu)
                    self.mainSidePanel.customContextMenuRequested.connect(self.openMenu)

                    self.mainSidePanel.itemClicked.connect(lambda: MyInteractorStyle(self.renderer, self.mainSidePanel, topLevelItems, topLevelItemList, ModelTreeItems,
                                                              ModelTreeItemList, elementTreeItems, elementTreeItemList,
                                                              beamElementTreeItems, beamElementTreeItemList, self.elementFloorIndexList, self.elementFloorItemList,
                                                              self.elementPierItemList, self.elementPierIndexList, self.elementSpandrelIndexList, self.elementSpandrelItemList,
                                                              self.elementElasticBeamIndexList, self.elementElasticBeamItemList,
                                                              self.elementNlinBeamIndexList, self.elementNlinBeamItemList,
                                                              self.elementZlenIndexList, self.elementZlenItemList, self.nodeIndexList, self.nodeItemList,
                                                              widgetItemList, "clicked"))

                    callCounter = 1
                    widgetItemList = [topLevelItemList, ModelTreeItemList, elementTreeItemList, beamElementTreeItemList,
                                      elementFloorGroupItemList, elementPierGroupItemList, self.elementSpandrelItemList,
                                      elementSpandrelGroupItemList, self.elementElasticBeamItemList, elementElasticBeamGroupItemList,
                                      self.elementNlinBeamItemList, elementNlinBeamGroupItemList, self.elementZlenItemList, elementZlenGroupItemList, nodeGroupItemList]

                    iren.SetInteractorStyle(MyInteractorStyle(self.renderer, self.mainSidePanel, topLevelItems, topLevelItemList, ModelTreeItems,
                                                              ModelTreeItemList, elementTreeItems, elementTreeItemList,
                                                              beamElementTreeItems, beamElementTreeItemList, self.elementFloorIndexList, self.elementFloorItemList,
                                                              self.elementPierItemList, self.elementPierIndexList, self.elementSpandrelIndexList, self.elementSpandrelItemList,
                                                              self.elementElasticBeamIndexList, self.elementElasticBeamItemList,
                                                              self.elementNlinBeamIndexList, self.elementNlinBeamItemList,
                                                              self.elementZlenIndexList, self.elementZlenItemList, self.nodeIndexList, self.nodeItemList,
                                                              widgetItemList, ""))


                    #nodeList.itemSelectionChanged.connect(
                        #lambda: viewUpdater().nodeHighlighter(nodeList, elementList, nodeIndexList, renderer, colors, iren))

                    self.mainSidePanel.setLayout(mainSidePanelLayout)
                    structureLayout.addWidget(self.mainSidePanel, 1, 0)

                    # Create the right panel widget for model navigation
                    propertySidePanelLayout = QVBoxLayout()
                    propertySidePanelLayout.setContentsMargins(5, 0, 5, 0)
                    self.propertySidePanel.setFixedWidth(300)

                    self.propertySidePanel.setLayout(propertySidePanelLayout)
                    structureLayout.addWidget(self.propertySidePanel, 1, 2)

                    topIconToolbar = QWidget()
                    topIconToolbarLayout = QHBoxLayout()
                    topIconToolbarLayout.setContentsMargins(0, 0, 0, 0)
                    topIconToolbarLayout.setSpacing(2)
                    topIconToolbar.setFixedHeight(25)
                    toolbarIconStyleSheet1 = "QPushButton {border: none;}"
                    toolbarIconStyleSheet2 = "QPushButton:hover {border: 1px solid #33E6FF;}"
                    toolbarIconStyleSheet3 = "QPushButton:pressed {border: 2px solid #8f8f91;}"

                    topToolbarNew = QPushButton()
                    topToolbarNew.setFixedWidth(25)
                    topToolbarNew.setIcon(QIcon("newFileIcon.png"))
                    topToolbarNew.setIconSize(QSize(25, 25))
                    topToolbarNew.setToolTip('Create New File...')
                    topToolbarNew.clicked.connect(self.newFile)
                    topIconToolbarLayout.addWidget(topToolbarNew, Qt.AlignLeft)
                    topToolbarNew.setStyleSheet(toolbarIconStyleSheet1 + toolbarIconStyleSheet2 + toolbarIconStyleSheet3)

                    topToolbarOpen = QPushButton()
                    topToolbarOpen.setFixedWidth(25)
                    topToolbarOpen.setIcon(QIcon("openFileIcon.png"))
                    topToolbarOpen.setIconSize(QSize(25, 25))
                    topToolbarOpen.setToolTip('Open Existing File...')
                    topToolbarOpen.clicked.connect(lambda: self.openFile())
                    topIconToolbarLayout.addWidget(topToolbarOpen, Qt.AlignLeft)
                    topToolbarOpen.setStyleSheet(toolbarIconStyleSheet1 + toolbarIconStyleSheet2 + toolbarIconStyleSheet3)

                    topToolbarSave = QPushButton()
                    topToolbarSave.setFixedWidth(25)
                    topToolbarSave.setIcon(QIcon("saveFileIcon.png"))
                    topToolbarSave.setIconSize(QSize(25, 25))
                    topToolbarSave.setToolTip('Save Current File...')
                    topToolbarSave.clicked.connect(lambda: self.handlePrint(mWindow))
                    topIconToolbarLayout.addWidget(topToolbarSave, Qt.AlignLeft)
                    topToolbarSave.setStyleSheet(toolbarIconStyleSheet1 + toolbarIconStyleSheet2 + toolbarIconStyleSheet3)

                    topToolbarPrint = QPushButton()
                    topToolbarPrint.setFixedWidth(25)
                    topToolbarPrint.setIcon(QIcon("printIcon.png"))
                    topToolbarPrint.setIconSize(QSize(25, 25))
                    topToolbarPrint.setToolTip('Print...')
                    topToolbarPrint.clicked.connect(lambda: self.handlePrint(mWindow))
                    topIconToolbarLayout.addWidget(topToolbarPrint, Qt.AlignLeft)
                    topToolbarPrint.setStyleSheet(toolbarIconStyleSheet1 + toolbarIconStyleSheet2 + toolbarIconStyleSheet3)

                    iconSeparator1 = QFrame(); iconSeparator1.setFrameShape(QFrame.VLine)
                    topIconToolbarLayout.addWidget(iconSeparator1, Qt.AlignLeft)

                    topToolbarUndo = QPushButton()
                    topToolbarUndo.setFixedWidth(25)
                    topToolbarUndo.setIcon(QIcon("undoIcon.png"))
                    topToolbarUndo.setIconSize(QSize(25, 25))
                    topToolbarUndo.setToolTip('Undo')
                    topToolbarUndo.clicked.connect(lambda: self.handlePrint(mWindow))
                    topIconToolbarLayout.addWidget(topToolbarUndo, Qt.AlignLeft)
                    topToolbarUndo.setStyleSheet(toolbarIconStyleSheet1 + toolbarIconStyleSheet2 + toolbarIconStyleSheet3)

                    topToolbarRedo = QPushButton()
                    topToolbarRedo.setFixedWidth(25)
                    topToolbarRedo.setIcon(QIcon("redoIcon.png"))
                    topToolbarRedo.setIconSize(QSize(25, 25))
                    topToolbarRedo.setToolTip('Redo')
                    topToolbarRedo.clicked.connect(lambda: self.handlePrint(mWindow))
                    topIconToolbarLayout.addWidget(topToolbarRedo, Qt.AlignLeft)
                    topToolbarRedo.setStyleSheet(toolbarIconStyleSheet1 + toolbarIconStyleSheet2 + toolbarIconStyleSheet3)

                    iconSeparator2 = QFrame(); iconSeparator2.setFrameShape(QFrame.VLine)
                    topIconToolbarLayout.addWidget(iconSeparator2, Qt.AlignLeft)

                    self.currentView = "3D"
                    xyViewSteps = [0, 1.8, 3.25, 4.75]
                    xzViewSteps = [0, 5.23]
                    yzViewSteps = [0, 2.71, 5.6201]
                    self.currentXYview = 0
                    self.currentXZview = 0
                    self.currentYZview = 0

                    topToolbarXY = QPushButton()
                    topToolbarXY.setFixedWidth(25)
                    topToolbarXY.setIcon(QIcon("xyIcon.png"))
                    topToolbarXY.setIconSize(QSize(25, 25))
                    topToolbarXY.setToolTip('xy View...')
                    topToolbarXY.clicked.connect(lambda: self.handleView(self.renderer, maxX, minX, maxY, minY, maxZ,
                                                                         minZ, "xy", IsoPos, IsoFocal, IsoNearClip, IsoFarClip, iren, xyViewSteps, xzViewSteps, yzViewSteps))
                    topIconToolbarLayout.addWidget(topToolbarXY, Qt.AlignLeft)
                    topToolbarXY.setStyleSheet(toolbarIconStyleSheet1 + toolbarIconStyleSheet2 + toolbarIconStyleSheet3)

                    topToolbarXZ = QPushButton()
                    topToolbarXZ.setFixedWidth(25)
                    topToolbarXZ.setIcon(QIcon("xzIcon.png"))
                    topToolbarXZ.setIconSize(QSize(25, 25))
                    topToolbarXZ.setToolTip('xz View...')
                    topToolbarXZ.clicked.connect(lambda: self.handleView(self.renderer, maxX, minX, maxY, minY, maxZ,
                                                                         minZ, "xz", IsoPos, IsoFocal, IsoNearClip, IsoFarClip, iren, xyViewSteps, xzViewSteps, yzViewSteps))
                    topIconToolbarLayout.addWidget(topToolbarXZ, Qt.AlignLeft)
                    topToolbarXZ.setStyleSheet(toolbarIconStyleSheet1 + toolbarIconStyleSheet2 + toolbarIconStyleSheet3)

                    topToolbarYZ = QPushButton()
                    topToolbarYZ.setFixedWidth(25)
                    topToolbarYZ.setIcon(QIcon("yzIcon.png"))
                    topToolbarYZ.setIconSize(QSize(25, 25))
                    topToolbarYZ.setToolTip('yz View...')
                    topToolbarYZ.clicked.connect(lambda: self.handleView(self.renderer, maxX, minX, maxY, minY, maxZ,
                                                                         minZ, "yz", IsoPos, IsoFocal, IsoNearClip, IsoFarClip, iren, xyViewSteps, xzViewSteps, yzViewSteps))
                    topIconToolbarLayout.addWidget(topToolbarYZ, Qt.AlignLeft)
                    topToolbarYZ.setStyleSheet(toolbarIconStyleSheet1 + toolbarIconStyleSheet2 + toolbarIconStyleSheet3)

                    topToolbar3D = QPushButton()
                    topToolbar3D.setFixedWidth(25)
                    topToolbar3D.setIcon(QIcon("3DIcon.png"))
                    topToolbar3D.setIconSize(QSize(25, 25))
                    topToolbar3D.setToolTip('3D View...')
                    topToolbar3D.clicked.connect(lambda: self.handleView(self.renderer, maxX, minX, maxY, minY, maxZ,
                                                                         minZ, "3D", IsoPos, IsoFocal, IsoNearClip, IsoFarClip, iren, xyViewSteps, xzViewSteps, yzViewSteps))
                    topIconToolbarLayout.addWidget(topToolbar3D, Qt.AlignLeft)
                    topToolbar3D.setStyleSheet(toolbarIconStyleSheet1 + toolbarIconStyleSheet2 + toolbarIconStyleSheet3)

                    topToolbarUp = QPushButton()
                    topToolbarUp.setFixedWidth(25)
                    topToolbarUp.setIcon(QIcon("upIcon.png"))
                    topToolbarUp.setIconSize(QSize(25, 25))
                    topToolbarUp.setToolTip('Next Level/Elevation')
                    topToolbarUp.clicked.connect(lambda: self.handleView(self.renderer, maxX, minX, maxY, minY, maxZ,
                                                                         minZ, "up", IsoPos, IsoFocal, IsoNearClip, IsoFarClip, iren, xyViewSteps, xzViewSteps, yzViewSteps))
                    topIconToolbarLayout.addWidget(topToolbarUp, Qt.AlignLeft)
                    topToolbarUp.setStyleSheet(toolbarIconStyleSheet1 + toolbarIconStyleSheet2 + toolbarIconStyleSheet3)

                    topToolbarDown = QPushButton()
                    topToolbarDown.setFixedWidth(25)
                    topToolbarDown.setIcon(QIcon("downIcon.png"))
                    topToolbarDown.setIconSize(QSize(25, 25))
                    topToolbarDown.setToolTip('Previous Level/Elevation')
                    topToolbarDown.clicked.connect(lambda: self.handleView(self.renderer, maxX, minX, maxY, minY, maxZ,
                                                                         minZ, "down", IsoPos, IsoFocal, IsoNearClip, IsoFarClip, iren, xyViewSteps, xzViewSteps, yzViewSteps))
                    topIconToolbarLayout.addWidget(topToolbarDown, Qt.AlignLeft)
                    topToolbarDown.setStyleSheet(toolbarIconStyleSheet1 + toolbarIconStyleSheet2 + toolbarIconStyleSheet3)

                    iconSeparator3 = QFrame()
                    iconSeparator3.setFrameShape(QFrame.VLine)
                    topIconToolbarLayout.addWidget(iconSeparator3, Qt.AlignLeft)

                    topToolbarTogglefill = QPushButton()
                    topToolbarTogglefill.setFixedWidth(25)
                    topToolbarTogglefill.setIcon(QIcon("ToggleFill.png"))
                    topToolbarTogglefill.setIconSize(QSize(25, 25))
                    topToolbarTogglefill.setToolTip('Toggle Fill')
                    topToolbarTogglefill.clicked.connect(lambda: self.renderType(self.renderer, "ToggleFill", topToolbarTogglefill))

                    topToolbarWireFrame = QPushButton()
                    topToolbarWireFrame.setFixedWidth(25)
                    topToolbarWireFrame.setIcon(QIcon("WireFrame.png"))
                    topToolbarWireFrame.setIconSize(QSize(25, 25))
                    topToolbarWireFrame.setToolTip('Wire Frame View')
                    topToolbarWireFrame.clicked.connect(lambda: self.renderType(self.renderer, "WireFrame", topToolbarTogglefill))

                    topToolbarSolid = QPushButton()
                    topToolbarSolid.setFixedWidth(25)
                    topToolbarSolid.setIcon(QIcon("solid.png"))
                    topToolbarSolid.setIconSize(QSize(25, 25))
                    topToolbarSolid.setToolTip('Solid View')
                    topToolbarSolid.clicked.connect(lambda: self.renderType(self.renderer, "solid", topToolbarTogglefill))
                    topIconToolbarLayout.addWidget(topToolbarSolid, Qt.AlignLeft)
                    topToolbarSolid.setStyleSheet(
                        toolbarIconStyleSheet1 + toolbarIconStyleSheet2 + toolbarIconStyleSheet3)
                    topIconToolbarLayout.addWidget(topToolbarWireFrame, Qt.AlignLeft)
                    topToolbarWireFrame.setStyleSheet(
                        toolbarIconStyleSheet1 + toolbarIconStyleSheet2 + toolbarIconStyleSheet3)
                    topIconToolbarLayout.addWidget(topToolbarTogglefill, Qt.AlignLeft)
                    topToolbarTogglefill.setStyleSheet(
                        toolbarIconStyleSheet1 + toolbarIconStyleSheet2 + toolbarIconStyleSheet3)
                    self.renderType(self.renderer, "solid", topToolbarTogglefill)

                    iconSeparator4 = QFrame()
                    iconSeparator4.setFrameShape(QFrame.VLine)
                    topIconToolbarLayout.addWidget(iconSeparator4, Qt.AlignLeft)

                    topToolbarRunAnalysis = QPushButton()
                    topToolbarRunAnalysis.setFixedWidth(25)
                    topToolbarRunAnalysis.setIcon(QIcon("RunIcon.png"))
                    topToolbarRunAnalysis.setIconSize(QSize(25, 25))
                    topToolbarRunAnalysis.setToolTip('Run Analysis')
                    topToolbarRunAnalysis.clicked.connect(lambda: runAnalysis())
                    topIconToolbarLayout.addWidget(topToolbarRunAnalysis, Qt.AlignLeft)
                    topToolbarRunAnalysis.setStyleSheet(
                        toolbarIconStyleSheet1 + toolbarIconStyleSheet2 + toolbarIconStyleSheet3)

                    topToolbarAnalysisOptions = QPushButton()
                    topToolbarAnalysisOptions.setFixedWidth(25)
                    topToolbarAnalysisOptions.setIcon(QIcon("AnalysisOptIcon.png"))
                    topToolbarAnalysisOptions.setIconSize(QSize(25, 25))
                    topToolbarAnalysisOptions.setToolTip('Analysis Options...')
                    topToolbarAnalysisOptions.clicked.connect(lambda: runAnalysis())
                    topIconToolbarLayout.addWidget(topToolbarAnalysisOptions, Qt.AlignLeft)
                    topToolbarAnalysisOptions.setStyleSheet(
                        toolbarIconStyleSheet1 + toolbarIconStyleSheet2 + toolbarIconStyleSheet3)

                    iconSeparator5 = QFrame()
                    iconSeparator5.setFrameShape(QFrame.VLine)
                    topIconToolbarLayout.addWidget(iconSeparator5, Qt.AlignLeft)

                    topToolbarRunAnalysis = QPushButton()
                    topToolbarRunAnalysis.setFixedWidth(25)
                    topToolbarRunAnalysis.setIcon(QIcon("UnDfrmd.png"))
                    topToolbarRunAnalysis.setIconSize(QSize(25, 25))
                    topToolbarRunAnalysis.setToolTip('Undeforemd Shape')
                    topToolbarRunAnalysis.clicked.connect(lambda: runAnalysis())
                    topIconToolbarLayout.addWidget(topToolbarRunAnalysis, Qt.AlignLeft)
                    topToolbarRunAnalysis.setStyleSheet(
                        toolbarIconStyleSheet1 + toolbarIconStyleSheet2 + toolbarIconStyleSheet3)

                    topToolbarAnalysisOptions = QPushButton()
                    topToolbarAnalysisOptions.setFixedWidth(25)
                    topToolbarAnalysisOptions.setIcon(QIcon("Dfrmd.png"))
                    topToolbarAnalysisOptions.setIconSize(QSize(25, 25))
                    topToolbarAnalysisOptions.setToolTip('Deformed Shape...')
                    topToolbarAnalysisOptions.clicked.connect(lambda: self.deformedShape())
                    topIconToolbarLayout.addWidget(topToolbarAnalysisOptions, Qt.AlignLeft)
                    topToolbarAnalysisOptions.setStyleSheet(
                        toolbarIconStyleSheet1 + toolbarIconStyleSheet2 + toolbarIconStyleSheet3)

                    topIconToolbar.setLayout(topIconToolbarLayout)
                    structureLayout.addWidget(topIconToolbar, 0, 0, 1, 2, Qt.AlignLeft)
                    structureLayout.setContentsMargins(5, 1, 5, 1)

                    return appMode, material, node, wall, element, polygon, analysis, fixConstraint, w2wConstraint, f2wConstraint, restraintActors, totalAnalysis, callCounter, storeElementPatch, prjName
                    # Add a button

                else:
                    appMode = "OpenSees"
                file.close()

    def handleTreeItems(self, remainingItems, groupItemList, remainingList, itemList, parentItemList, parentItems, objectType):
        while remainingItems > 10:
            groupItemList.append(QTreeWidgetItem([str(remainingList[0]) + " - " + str(
                remainingList[9])]))  # make node groups of 10 nodes
            parentItemList[parentItems.index(objectType)].addChild(groupItemList[-1])  # Add node groups to the tree
            for item in remainingList[0:10]:
                itemList.append(QTreeWidgetItem([str(item)]))  # Add nodes to the tree
                groupItemList[-1].addChild(itemList[-1])  # Add nodes to the tree
            remainingList = remainingList[10:remainingItems]
            remainingItems = len(remainingList)
        else:
            for item in remainingList:
                itemList.append(QTreeWidgetItem([str(item)]))  # Add nodes to the tree
                parentItemList[parentItems.index(objectType)].addChild(itemList[-1])  # Add nodes to the tree

        return itemList, groupItemList

    def handleView(self, renderer, maxX, minX, maxY, minY, maxZ, minZ, view, IsoPos, IsoFocal, IsoNearClip, IsoFarClip, iren, xyViewSteps, xzViewSteps, yzViewSteps):
        renderer.GetRenderWindow().Render()
        if view == "xz":
            for repeat in np.arange(2):
                focalX = 0.5 * (minX + maxX)
                focalY = maxY
                focalZ = 0.5 * (minZ + maxZ)
                renderer.GetActiveCamera().SetPosition(focalX, minY - 0.3, focalZ)
                renderer.GetActiveCamera().SetRoll(0)
                renderer.GetActiveCamera().ParallelProjectionOn()
                renderer.GetActiveCamera().SetClippingRange(0.30, 0.8)
                self.currentView = "xz"
                self.currentXYview = 0
                self.currentXZview = 0
                self.currentYZview = 0
                renderer.GetActiveCamera().SetFocalPoint(focalX, focalY, focalZ)
                renderer.GetRenderWindow().Render()
        elif view == "yz":
            for repeat in np.arange(2):
                focalX = maxX
                focalY = 0.5 * (minY + maxY)
                focalZ = 0.5 * (minZ + maxZ)
                renderer.GetActiveCamera().SetPosition(minX - 0.3, focalY, focalZ)
                renderer.GetActiveCamera().SetRoll(90)
                renderer.GetActiveCamera().ParallelProjectionOn()
                renderer.GetActiveCamera().SetClippingRange(0.3, 0.8)
                self.currentView = "yz"
                self.currentXYview = 0
                self.currentXZview = 0
                self.currentYZview = 0
                renderer.GetActiveCamera().SetFocalPoint(focalX, focalY, focalZ)
                renderer.GetRenderWindow().Render()
        elif view == "xy":
            for repeat in np.arange(2):
                focalX = 0.5 * (minX + maxX)
                focalY = 0.5 * (minY + maxY)
                focalZ = minZ
                renderer.GetActiveCamera().SetPosition(focalX, focalY, maxZ + 0.3)
                renderer.GetActiveCamera().SetRoll(0)
                renderer.GetActiveCamera().ParallelProjectionOn()
                renderer.GetActiveCamera().UpdateViewport(renderer)
                renderer.GetActiveCamera().SetClippingRange(0.01, maxZ - minZ + 0.6)
                self.currentView = "xy"
                self.currentXYview = 0
                self.currentXZview = 0
                self.currentYZview = 0
                renderer.GetActiveCamera().SetFocalPoint(focalX, focalY, focalZ)
                renderer.GetRenderWindow().Render()
        elif view == "3D":
            for repeat in np.arange(2):
                focalX = IsoFocal[0]
                focalY = IsoFocal[1]
                focalZ = IsoFocal[2]
                renderer.GetActiveCamera().SetPosition(IsoPos[0], IsoPos[1], IsoPos[2])
                renderer.GetActiveCamera().SetRoll(50)
                renderer.GetActiveCamera().OrthogonalizeViewUp()
                renderer.GetActiveCamera().ParallelProjectionOff()
                renderer.GetActiveCamera().SetClippingRange(IsoNearClip, IsoFarClip)
                self.currentView = "3D"
                self.currentXYview = 0
                self.currentXZview = 0
                self.currentYZview = 0
                renderer.GetActiveCamera().SetFocalPoint(focalX, focalY, focalZ)
                renderer.GetRenderWindow().Render()
        elif view == "up":
            if self.currentView == "xz":
                self.currentXZview += 1
                self.currentXZview = self.currentXZview % 2
                focalX = 0.5 * (minX + maxX)
                focalY = maxY
                focalZ = 0.5 * (minZ + maxZ)
                renderer.GetActiveCamera().SetPosition(focalX, xzViewSteps[self.currentXZview] - 0.3, focalZ)
                renderer.GetActiveCamera().SetRoll(0)
                renderer.GetActiveCamera().ParallelProjectionOn()
                renderer.GetActiveCamera().SetClippingRange(0.31, 0.8)
                renderer.GetActiveCamera().SetFocalPoint(focalX, focalY, focalZ)
                renderer.GetRenderWindow().Render()
            elif self.currentView == "yz":
                self.currentYZview += 1
                self.currentYZview = self.currentYZview % 3
                focalX = maxX
                focalY = 0.5 * (minY + maxY)
                focalZ = 0.5 * (minZ + maxZ)
                renderer.GetActiveCamera().SetPosition(yzViewSteps[self.currentYZview] - 0.3, focalY, focalZ)
                renderer.GetActiveCamera().SetRoll(90)
                renderer.GetActiveCamera().ParallelProjectionOn()
                renderer.GetActiveCamera().SetClippingRange(0.31, 0.8)
                renderer.GetActiveCamera().SetFocalPoint(focalX, focalY, focalZ)
                renderer.GetRenderWindow().Render()
        elif view == "down":
            if self.currentView == "xz":
                self.currentXZview -= 1
                self.currentXZview = self.currentXZview % 2
                focalX = 0.5 * (minX + maxX)
                focalY = maxY
                focalZ = 0.5 * (minZ + maxZ)
                renderer.GetActiveCamera().SetPosition(focalX, xzViewSteps[self.currentXZview] - 0.3, focalZ)
                renderer.GetActiveCamera().SetRoll(0)
                renderer.GetActiveCamera().ParallelProjectionOn()
                renderer.GetActiveCamera().SetClippingRange(0.31, 0.8)
                renderer.GetActiveCamera().SetFocalPoint(focalX, focalY, focalZ)
                renderer.GetRenderWindow().Render()
            elif self.currentView == "yz":
                self.currentYZview -= 1
                self.currentYZview = self.currentYZview % 3
                focalX = maxX
                focalY = 0.5 * (minY + maxY)
                focalZ = 0.5 * (minZ + maxZ)
                renderer.GetActiveCamera().SetPosition(yzViewSteps[self.currentYZview] - 0.3, focalY, focalZ)
                renderer.GetActiveCamera().SetRoll(90)
                renderer.GetActiveCamera().ParallelProjectionOn()
                renderer.GetActiveCamera().SetClippingRange(0.31, 0.8)
                renderer.GetActiveCamera().SetFocalPoint(focalX, focalY, focalZ)
                renderer.GetRenderWindow().Render()

    def renderType(self, renderer, renderType, toggleObj):
        totalStoredPatches = len(storeElementPatch.index.to_list())
        totalRestraintActors = len(restraintActors.index.to_list())
        if renderType == "solid":
            self.toggleFill = "on"
            for item in np.arange(totalStoredPatches):
                toggleObj.setDisabled(True)
                if storeElementPatch['Actor1-WireFrame'].iat[item] == storeElementPatch['Actor1-WireFrame'].iat[item]:
                    storeElementPatch['Actor1-WireFrame'].iat[item].SetVisibility(False)
                    storeElementPatch['Actor1-WireFrame-Wire'].iat[item].SetVisibility(False)
                if storeElementPatch['Actor1'].iat[item] == storeElementPatch['Actor1'].iat[item]:
                    storeElementPatch['Actor1'].iat[item].SetVisibility(True)
                if storeElementPatch['Object Type'].iat[item] == "Node":
                    storeElementPatch['Actor1-WireFrame-Node'].iat[item].SetVisibility(False)
                if storeElementPatch['Actor2'].iat[item] == storeElementPatch['Actor2'].iat[item]:
                    storeElementPatch['Actor2-WireFrame'].iat[item].SetVisibility(False)
                    storeElementPatch['Actor2-WireFrame-Wire'].iat[item].SetVisibility(False)
                    storeElementPatch['Actor2'].iat[item].SetVisibility(True)
            for restraintActorItem in np.arange(totalRestraintActors):
                restraintActors['Actor1'].iat[restraintActorItem].SetVisibility(False)
                if restraintActors['Actor2'].iat[restraintActorItem] == restraintActors['Actor2'].iat[restraintActorItem]:
                    restraintActors['Actor2'].iat[restraintActorItem].SetVisibility(False)

        elif renderType == "WireFrame":
            self.toggleFill = "off"
            toggleObj.setDisabled(False)
            for item in np.arange(totalStoredPatches):
                if storeElementPatch['Actor1'].iat[item] == storeElementPatch['Actor1'].iat[item]:
                    storeElementPatch['Actor1'].iat[item].SetVisibility(False)
                if storeElementPatch['Actor1-WireFrame'].iat[item] == storeElementPatch['Actor1-WireFrame'].iat[item]:
                    storeElementPatch['Actor1-WireFrame'].iat[item].SetVisibility(False)
                    storeElementPatch['Actor1-WireFrame-Wire'].iat[item].SetVisibility(True)
                if storeElementPatch['Object Type'].iat[item] == "Node":
                    storeElementPatch['Actor1-WireFrame-Node'].iat[item].SetVisibility(True)
                if storeElementPatch['Actor2'].iat[item] == storeElementPatch['Actor2'].iat[item]:
                    storeElementPatch['Actor2'].iat[item].SetVisibility(False)
                    storeElementPatch['Actor2-WireFrame'].iat[item].SetVisibility(False)
                    storeElementPatch['Actor2-WireFrame-Wire'].iat[item].SetVisibility(True)
            for restraintActorItem in np.arange(totalRestraintActors):
                restraintActors['Actor1'].iat[restraintActorItem].SetVisibility(True)
                if restraintActors['Actor2'].iat[restraintActorItem] == restraintActors['Actor2'].iat[restraintActorItem]:
                    restraintActors['Actor2'].iat[restraintActorItem].SetVisibility(True)
        elif renderType == "ToggleFill":
            if self.toggleFill == "off":
                self.toggleFill = "on"
                for item in np.arange(totalStoredPatches):
                    if storeElementPatch['Actor1-WireFrame'].iat[item] == storeElementPatch['Actor1-WireFrame'].iat[item]:
                        storeElementPatch['Actor1-WireFrame'].iat[item].SetVisibility(True)
                        storeElementPatch['Actor1-WireFrame-Wire'].iat[item].SetVisibility(False)
                    if storeElementPatch['Object Type'].iat[item] == "Node":
                        storeElementPatch['Actor1-WireFrame-Node'].iat[item].SetVisibility(False)
                    if storeElementPatch['Actor2'].iat[item] == storeElementPatch['Actor2'].iat[item]:
                        storeElementPatch['Actor2-WireFrame'].iat[item].SetVisibility(True)
                        storeElementPatch['Actor2-WireFrame-Wire'].iat[item].SetVisibility(False)
                for restraintActorItem in np.arange(totalRestraintActors):
                    restraintActors['Actor1'].iat[restraintActorItem].SetVisibility(False)
                    if restraintActors['Actor2'].iat[restraintActorItem] == restraintActors['Actor2'].iat[
                        restraintActorItem]:
                        restraintActors['Actor2'].iat[restraintActorItem].SetVisibility(False)
            else:
                self.toggleFill = "off"
                for item in np.arange(totalStoredPatches):
                    if storeElementPatch['Actor1-WireFrame'].iat[item] == storeElementPatch['Actor1-WireFrame'].iat[item]:
                        storeElementPatch['Actor1-WireFrame'].iat[item].SetVisibility(False)
                        storeElementPatch['Actor1-WireFrame-Wire'].iat[item].SetVisibility(True)
                    if storeElementPatch['Object Type'].iat[item] == "Node":
                        storeElementPatch['Actor1-WireFrame-Node'].iat[item].SetVisibility(True)
                    if storeElementPatch['Actor2'].iat[item] == storeElementPatch['Actor2'].iat[item]:
                        storeElementPatch['Actor2-WireFrame'].iat[item].SetVisibility(False)
                        storeElementPatch['Actor2-WireFrame-Wire'].iat[item].SetVisibility(True)
                for restraintActorItem in np.arange(totalRestraintActors):
                    restraintActors['Actor1'].iat[restraintActorItem].SetVisibility(True)
                    if restraintActors['Actor2'].iat[restraintActorItem] == restraintActors['Actor2'].iat[
                        restraintActorItem]:
                        restraintActors['Actor2'].iat[restraintActorItem].SetVisibility(True)
        renderer.GetRenderWindow().Render()

    def restraintPlotter(self, renderer):
        totalRestraints = restraintActors['Fx'].count()
        for restraintItem in np.arange(totalRestraints):
            nodeItem = restraintActors.index[restraintItem]
            if restraintActors['Fx'].iat[restraintItem] == 1:
                points = vtk.vtkPoints()
                polyLine = vtk.vtkCellArray()
                if restraintActors['Ry'].iat[restraintItem] == 1:
                    # create the representation of fixed restraint
                    points.SetNumberOfPoints(4)
                    points.SetPoint(0, node.at[nodeItem, 'x'] + 0.2, node.at[nodeItem, 'y'], node.at[nodeItem, 'z'])
                    points.SetPoint(1, node.at[nodeItem, 'x'] - 0.2, node.at[nodeItem, 'y'], node.at[nodeItem, 'z'])
                    points.SetPoint(2, node.at[nodeItem, 'x'] - 0.2, node.at[nodeItem, 'y'], node.at[nodeItem, 'z'] - 0.2)
                    points.SetPoint(3, node.at[nodeItem, 'x'] + 0.2, node.at[nodeItem, 'y'], node.at[nodeItem, 'z'] - 0.2)
                    polyLine.InsertNextCell(5)
                    polyLine.InsertCellPoint(0)
                    polyLine.InsertCellPoint(1)
                    polyLine.InsertCellPoint(2)
                    polyLine.InsertCellPoint(3)
                    polyLine.InsertCellPoint(0)
                else:
                    points.SetNumberOfPoints(3)
                    points.SetPoint(0, node.at[nodeItem, 'x'], node.at[nodeItem, 'y'], node.at[nodeItem, 'z'])
                    points.SetPoint(1, node.at[nodeItem, 'x'] + 0.23, node.at[nodeItem, 'y'], node.at[nodeItem, 'z'] - 0.2)
                    points.SetPoint(2, node.at[nodeItem, 'x'] - 0.23, node.at[nodeItem, 'y'], node.at[nodeItem, 'z'] - 0.2)
                    polyLine.InsertNextCell(4)
                    polyLine.InsertCellPoint(0)
                    polyLine.InsertCellPoint(1)
                    polyLine.InsertCellPoint(2)
                    polyLine.InsertCellPoint(0)
                # Create a PolyData
                polyLinePolyData = vtk.vtkPolyData()
                polyLinePolyData.SetPoints(points)
                polyLinePolyData.SetLines(polyLine)
                # Create a mapper and actor
                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputData(polyLinePolyData)
                mapper.Update()
                actor = vtk.vtkActor()
                actor.SetMapper(mapper)
                actor.GetProperty().SetColor(colors.GetColor3d("Cyan"))
                actor.GetProperty().SetLineWidth(5)
                renderer.AddActor(actor)
                restraintActors.at[nodeItem, 'Actor1'] = actor
            if restraintActors['Fy'].iat[restraintItem] == 1:
                points = vtk.vtkPoints()
                polyLine = vtk.vtkCellArray()
                if restraintActors['Rx'].iat[restraintItem] == 1:
                    # create the representation of fixed restraint
                    points.SetNumberOfPoints(4)
                    points.SetPoint(0, node.at[nodeItem, 'x'], node.at[nodeItem, 'y'] + 0.2, node.at[nodeItem, 'z'])
                    points.SetPoint(1, node.at[nodeItem, 'x'], node.at[nodeItem, 'y'] - 0.2, node.at[nodeItem, 'z'])
                    points.SetPoint(2, node.at[nodeItem, 'x'], node.at[nodeItem, 'y'] - 0.2, node.at[nodeItem, 'z'] - 0.2)
                    points.SetPoint(3, node.at[nodeItem, 'x'], node.at[nodeItem, 'y'] + 0.2, node.at[nodeItem, 'z'] - 0.2)
                    polyLine.InsertNextCell(5)
                    polyLine.InsertCellPoint(0)
                    polyLine.InsertCellPoint(1)
                    polyLine.InsertCellPoint(2)
                    polyLine.InsertCellPoint(3)
                    polyLine.InsertCellPoint(0)
                else:
                    points.SetNumberOfPoints(3)
                    points.SetPoint(0, node.at[nodeItem, 'x'], node.at[nodeItem, 'y'], node.at[nodeItem, 'z'])
                    points.SetPoint(1, node.at[nodeItem, 'x'], node.at[nodeItem, 'y'] + 0.23, node.at[nodeItem, 'z'] - 0.2)
                    points.SetPoint(2, node.at[nodeItem, 'x'], node.at[nodeItem, 'y'] - 0.23, node.at[nodeItem, 'z'] - 0.2)
                    polyLine.InsertNextCell(4)
                    polyLine.InsertCellPoint(0)
                    polyLine.InsertCellPoint(1)
                    polyLine.InsertCellPoint(2)
                    polyLine.InsertCellPoint(0)
                # Create a PolyData
                polyLinePolyData = vtk.vtkPolyData()
                polyLinePolyData.SetPoints(points)
                polyLinePolyData.SetLines(polyLine)
                # Create a mapper and actor
                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputData(polyLinePolyData)
                mapper.Update()
                actor = vtk.vtkActor()
                actor.SetMapper(mapper)
                actor.GetProperty().SetColor(colors.GetColor3d("Cyan"))
                actor.GetProperty().SetLineWidth(5)
                renderer.AddActor(actor)
                restraintActors.at[nodeItem, 'Actor2'] = actor

        renderer.GetRenderWindow().Render()

    def deformedShape(self):
        deformedShapeDialog = QtGui.QDialog()
        deformedShapeDialog.setWindowTitle("Define Analysis Cases")
        deformedShapeDialogLayout = QGridLayout()
        deformedShapeDialogBtn = QWidget()
        deformedShapeDialogBtnLayout = QGridLayout()
        AnalysisCaseSelecList = []

        for analysisItem in np.arange(analysis['type'].count()):
            if analysis["type"].iat[analysisItem] == "Dynamic":
                wTxtAnType = "Transient"
                wTxtAnSubType = " - Time History"
            elif analysis["type"].iat[analysisItem] == "selfWeight":
                wTxtAnType = "Static"
                wTxtAnSubType = " - Gravity"
            elif analysis["type"].iat[analysisItem] == "PushoverRectangular":
                wTxtAnType = "Static"
                wTxtAnSubType = " - Pushover"
            elif analysis["type"].iat[analysisItem] == "Modal":
                wTxtAnType = "Modal"
                wTxtAnSubType = ""
            AnalysisCaseSelecList.append(str(analysis.index.to_list()[analysisItem]) + ' - ' + wTxtAnType + wTxtAnSubType)

        AnalysisCaseTtl = QLabel("Analysis Case")
        AnalysisCaseSelec = QComboBox()
        for AnalysisCaseItem in AnalysisCaseSelecList:
            AnalysisCaseSelec.addItem(AnalysisCaseItem)
        AnalysisCaseSelec.setCurrentIndex(0)

        scaleFactorTtl = QLabel("Scale Factor")
        deformedShapeScaleFactor = QLineEdit(str(1.0))

        display_dt_ttl = QLabel("Display dt")
        display_dt = QLineEdit(str(0.2))
        display_dt.setDisabled(True)

        dt, ultimate_time = AnalysisCaseSelec.currentIndexChanged.connect(lambda: self.read_analysis_change(AnalysisCaseSelec, display_dt))

        # Add a button
        applyDeformedShapeBtn = QPushButton('Apply', deformedShapeDialogBtn)
        applyDeformedShapeBtn.setToolTip('Click to Apply')
        applyDeformedShapeBtn.clicked.connect(lambda: self.plotDeformed(deformedShapeScaleFactor, AnalysisCaseSelec, deformedShapeDialog, dt, display_dt, ultimate_time))
        applyDeformedShapeBtn.resize(applyDeformedShapeBtn.sizeHint())
        applyDeformedShapeBtn.move(100, 80)

        cancelDeformedShapeBtn = QPushButton('Cancel', deformedShapeDialogBtn)
        cancelDeformedShapeBtn.setToolTip('Cancel Modifications')
        cancelDeformedShapeBtn.clicked.connect(deformedShapeDialog.close)
        cancelDeformedShapeBtn.resize(cancelDeformedShapeBtn.sizeHint())
        cancelDeformedShapeBtn.move(100, 80)

        deformedShapeDialogLayout.addWidget(AnalysisCaseTtl, 1, 1)
        deformedShapeDialogLayout.addWidget(AnalysisCaseSelec, 2, 1)
        deformedShapeDialogLayout.addWidget(scaleFactorTtl, 3, 1)
        deformedShapeDialogLayout.addWidget(deformedShapeScaleFactor, 4, 1)
        deformedShapeDialogLayout.addWidget(display_dt_ttl, 3, 2)
        deformedShapeDialogLayout.addWidget(display_dt, 4, 2)
        deformedShapeDialogLayout.addWidget(deformedShapeDialogBtn, 1, 2, 2, 1)
        deformedShapeDialogBtnLayout.addWidget(applyDeformedShapeBtn, 0, 0)
        deformedShapeDialogBtnLayout.addWidget(cancelDeformedShapeBtn, 0, 1)
        deformedShapeDialog.setLayout(deformedShapeDialogLayout)
        deformedShapeDialogBtn.setLayout(deformedShapeDialogBtnLayout)
        deformedShapeDialog.setFixedSize(400, 150)

        if deformedShapeDialog.exec_() == QtGui.QDialog.Accepted:
            deformedShapeDialog.show()
        return tmp_analysis, deformedShapeDialog

    def read_analysis_change(self, anlz_case, display_dt):
        tmp_cwd = os.getcwd()
        tmp_cwd = str(tmp_cwd).replace('\\', '/')
        OUTPUTfilePath = tmp_cwd + "/" + "output/"
        fileName = "analysis" + str(anlz_case.currentIndex() + 1) + "_" + analysis["type"].iat[
            anlz_case.currentIndex()] + "_" + "allDispl.out"
        fileLocation = OUTPUTfilePath + fileName

        open_file = open(fileLocation, "r")  # Open the Tremuri file
        input_file = open_file.read()  # Read the Tremuri file

        # read the lines of the input file
        lines = input_file.splitlines()  # split the lines of the input file
        open_file.close()  # close the input file after reading its data
        dt = float(lines[0].split()[0])
        ultimate_time = float(lines[-1].split()[0])

        display_dt.setDisabled(False)
        display_dt.setText(str(dt))

        return dt, ultimate_time

    def plotDeformed(self, scale_factor, anlz_case, dialog, dt, display_dt, ultimate_time):
        import convertTremuriToOpensees_func
        import drawModelVTK_func
        scale = float(scale_factor.text())
        tmp_cwd = os.getcwd()
        tmp_cwd = str(tmp_cwd).replace('\\', '/')
        OUTPUTfilePath = tmp_cwd + "/" + "output/"
        fileName = "analysis" + str(anlz_case.currentIndex() + 1) + "_" + analysis["type"].iat[anlz_case.currentIndex()] + "_" + "allDispl.out"
        readAnalysis_func.completeFileLocation4 = OUTPUTfilePath + fileName
        readAnalysis_func.analysisType = analysis["type"].iat[anlz_case.currentIndex()]
        nodeList = node.index.to_list()
        readAnalysis_func.nodeList = nodeList
        readAnalysis_func.display_dt = display_dt
        readAnalysis_func.ultimate_time = ultimate_time
        readAnalysis_func.dt = dt
        node_disps, num_dt = readAnalysis_func.read_anlz_func()
        node_disps_backup = node_disps.copy(deep=True)

        # These are the point ids corresponding to each face.
        faces = [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
        faceId = vtk.vtkIdList()
        faceId.InsertNextId(6)  # Six faces make up the cell.
        for face in faces:
            faceId.InsertNextId(len(face))  # The number of points in the face.
            [faceId.InsertNextId(i) for i in face]

        totalStoredPatches = len(storeElementPatch.index.to_list())
        for dt in np.arange(num_dt):
            node_disps = node_disps_backup[dt * len(nodeList):(dt + 1) * len(nodeList)]
            node_disps = node_disps.set_index('Node')
            for item in np.arange(totalStoredPatches):
                # Calculating the deformed coordinates of the nodes
                if storeElementPatch['Object Type'].iat[item] == "Element" \
                        and (storeElementPatch['Element Type'].iat[item] == "Wall - Pier"
                             or storeElementPatch['Element Type'].iat[item] == "Wall - Spandrel"):
                    nodeE = node.at[int(element.at[storeElementPatch.index[item], 'nodeE']), 'pos']
                    nodeE = np.array([nodeE]).transpose()  # transpose to convert the variable to a column vector

                    tmp_val = np.dot(0.5 * element.at[storeElementPatch.index[item], 'h'], element.at[storeElementPatch.index[item], 'xAxis'])
                    tmp_val = np.array([tmp_val]).transpose()  # transpose to convert the variable to a column vector
                    nodeI = nodeE - tmp_val
                    nodeJ = nodeE + tmp_val
                    tmp_I = node.at[int(element.at[storeElementPatch.index[item], 'nodeI']), 'pos']
                    tmp_J = node.at[int(element.at[storeElementPatch.index[item], 'nodeJ']), 'pos']
                    tmp_I = np.array([tmp_I]).transpose()
                    tmp_J = np.array([tmp_J]).transpose()

                    offsetI = nodeI - tmp_I
                    offsetJ = nodeJ - tmp_J

                    node_disp_item_i = node_disps.at[int(element.at[storeElementPatch.index[item], 'nodeI']), 'Disp']
                    u_i = node_disp_item_i[0]
                    v_i = node_disp_item_i[1]
                    w_i = node_disp_item_i[2]
                    rotx_i = node_disp_item_i[3]
                    roty_i = node_disp_item_i[4]
                    rotz_i = node_disp_item_i[5]
                    anglesI = np.dot(scale, [rotx_i, roty_i, rotz_i])
                    anglesI = np.array([anglesI]).transpose()
                    node_disp_item_j = node_disps.at[int(element.at[storeElementPatch.index[item], 'nodeJ']), 'Disp']
                    u_j = node_disp_item_j[0]
                    v_j = node_disp_item_j[1]
                    w_j = node_disp_item_j[2]
                    rotx_j = node_disp_item_j[3]
                    roty_j = node_disp_item_j[4]
                    rotz_j = node_disp_item_j[5]
                    anglesJ = np.dot(scale, [rotx_j, roty_j, rotz_j])
                    anglesJ = np.array([anglesJ]).transpose()

                    offsetRotI = convertTremuriToOpensees_func.rotate3D(offsetI, anglesI)
                    offsetRotJ = convertTremuriToOpensees_func.rotate3D(offsetJ, anglesJ)

                    xAxisRotI = convertTremuriToOpensees_func.rotate3D(
                        element.at[storeElementPatch.index[item], 'xAxis'], anglesI)
                    zAxisRotI = convertTremuriToOpensees_func.rotate3D(
                        wall.at[int(element.at[storeElementPatch.index[item], 'wall']), 'zAxis'], anglesI)
                    yAxisRotI = np.cross(zAxisRotI, xAxisRotI)
                    zAxisRotI = np.reshape(zAxisRotI, (-1, 1))
                    xAxisRotJ = convertTremuriToOpensees_func.rotate3D(
                        element.at[storeElementPatch.index[item], 'xAxis'], anglesJ)
                    zAxisRotJ = convertTremuriToOpensees_func.rotate3D(
                        wall.at[int(element.at[storeElementPatch.index[item], 'wall']), 'zAxis'], anglesJ)
                    zAxisRotJ = np.reshape(zAxisRotJ, (-1, 1))

                    node_pos_i = node.at[int(element.at[storeElementPatch.index[item], 'nodeI']), 'pos']
                    node_pos_i = np.array([node_pos_i]).transpose()  # transpose to convert the variable to a column vector
                    node_def_i = np.dot(scale, [u_i, v_i, w_i])
                    node_def_i = np.array([node_def_i]).transpose()  # transpose to convert the variable to a column vector
                    nodeI = node_pos_i + offsetRotI + node_def_i

                    node_pos_j = node.at[int(element.at[storeElementPatch.index[item], 'nodeJ']), 'pos']
                    node_pos_j = np.array([node_pos_j]).transpose()  # transpose to convert the variable to a column vector
                    node_def_j = np.dot(scale, [u_j, v_j, w_j])
                    node_def_j = np.array([node_def_j]).transpose()  # transpose to convert the variable to a column vector
                    nodeJ = node_pos_j + offsetRotJ + node_def_j

                    node_disp_item_e = node_disps.at[int(element.at[storeElementPatch.index[item], 'nodeE']), 'Disp']
                    u_e = node_disp_item_e[0]
                    v_e = node_disp_item_e[1]
                    w_e = node_disp_item_e[2]
                    rotx_e = node_disp_item_e[3]
                    roty_e = node_disp_item_e[4]
                    rotz_e = node_disp_item_e[5]
                    nodeE1 = nodeE + np.array(np.dot(scale, [[u_e], [v_e], [w_e]]))
                    nodeE2 = nodeE + np.array(np.dot(scale, [[rotx_e], [roty_e], [rotz_e]]))

                    shift = np.dot((nodeE2 - nodeE1).transpose(), yAxisRotI)
                    shift = shift[0]

                    t = element.at[storeElementPatch.index[item], 't']

                    [xx1, yy1, zz1] = drawModelVTK_func.addWallToPatch(nodeI, nodeE1, zAxisRotI,
                                                                  element.at[storeElementPatch.index[item], 'b'], t,
                                                                  [[0], [0], [0]], [[0], [0.5 * shift], [0]], "wireframe")
                    [xx2, yy2, zz2] = drawModelVTK_func.addWallToPatch(nodeE2, nodeJ, zAxisRotJ,
                                                                  element.at[storeElementPatch.index[item], 'b'], t,
                                                                  [[0], [0], [0]], [[0], [-0.5 * shift], [0]], "wireframe")
                    object_actor = storeElementPatch['Actor1'].iat[item]

                    points = vtk.vtkPoints()
                    points.InsertNextPoint(xx1[0][0], yy1[0][0], zz1[0][0])
                    points.InsertNextPoint(xx1[1][0], yy1[1][0], zz1[1][0])
                    points.InsertNextPoint(xx1[2][0], yy1[2][0], zz1[2][0])
                    points.InsertNextPoint(xx1[3][0], yy1[3][0], zz1[3][0])
                    points.InsertNextPoint(xx1[0][1], yy1[0][1], zz1[0][1])
                    points.InsertNextPoint(xx1[1][1], yy1[1][1], zz1[1][1])
                    points.InsertNextPoint(xx1[2][1], yy1[2][1], zz1[2][1])
                    points.InsertNextPoint(xx1[3][1], yy1[3][1], zz1[3][1])

                    ugrid = vtk.vtkUnstructuredGrid()
                    ugrid.SetPoints(points)
                    ugrid.InsertNextCell(vtk.VTK_POLYHEDRON, faceId)

                    mapper = vtk.vtkDataSetMapper()
                    mapper.SetInputData(ugrid)
                    object_actor.SetMapper(mapper)

                    object_actor = storeElementPatch['Actor2'].iat[item]
                    if object_actor == object_actor:
                        points = vtk.vtkPoints()
                        points.InsertNextPoint(xx2[0][0], yy2[0][0], zz2[0][0])
                        points.InsertNextPoint(xx2[1][0], yy2[1][0], zz2[1][0])
                        points.InsertNextPoint(xx2[2][0], yy2[2][0], zz2[2][0])
                        points.InsertNextPoint(xx2[3][0], yy2[3][0], zz2[3][0])
                        points.InsertNextPoint(xx2[0][1], yy2[0][1], zz2[0][1])
                        points.InsertNextPoint(xx2[1][1], yy2[1][1], zz2[1][1])
                        points.InsertNextPoint(xx2[2][1], yy2[2][1], zz2[2][1])
                        points.InsertNextPoint(xx2[3][1], yy2[3][1], zz2[3][1])
                        ugrid = vtk.vtkUnstructuredGrid()
                        ugrid.SetPoints(points)
                        ugrid.InsertNextCell(vtk.VTK_POLYHEDRON, faceId)

                        mapper = vtk.vtkDataSetMapper()
                        mapper.SetInputData(ugrid)
                        object_actor.SetMapper(mapper)

            self.renderer.GetRenderWindow().Render()

        dialog.close()

    def openMenu(self, position):
        indexes = self.mainSidePanel.selectedIndexes()
        print(indexes)
        if len(indexes) > 0:
            level = 0
            index = indexes[0]
            while index.parent().isValid():
                index = index.parent()
                level += 1

            childLevel = 0
            index = indexes[0]
            while index.child(0, 0).isValid():
                index = index.child(0, 0)
                childLevel += 1

        menu = QMenu()
        actionExpand = []; actionCollapse = []; actionShowAll = []; actionHideAll = []; actionShow = []; actionHide = []
        if level == 0:
            actionExpand = menu.addAction("Expand")
            actionCollapse = menu.addAction("Collapse")
        elif childLevel > 0:
            actionExpand = menu.addAction("Expand")
            actionCollapse = menu.addAction("Collapse")
            actionShowAll = menu.addAction("Show All")
            actionHideAll = menu.addAction("Hide All")
        elif childLevel == 0:
            actionShow = menu.addAction("Show")
            actionHide = menu.addAction("Hide")

        action = menu.exec_(self.mainSidePanel.viewport().mapToGlobal(position))
        if action == actionExpand:
            print("Expand")
        elif action == actionCollapse:
            print("Collapse")
        elif action == actionShowAll:
            print("Show All")
        elif action == actionHideAll:
            print("Hide All")
        elif action == actionShow:
            for selectedItem in self.mainSidePanel.selectedItems():
                actor2hide = self.actorFinder(selectedItem)
                for actorItem in actor2hide:
                    actorItem.SetVisibility(True)
            self.renderer.GetRenderWindow().Render()
        elif action == actionHide:
            for selectedItem in self.mainSidePanel.selectedItems():
                actor2hide = self.actorFinder(selectedItem)
                for actorItem in actor2hide:
                    actorItem.SetVisibility(False)
            self.renderer.GetRenderWindow().Render()

    def handlePrint(self, mwindow):
        dialog = QtGui.QPrintDialog()
        if dialog.exec_() == QtGui.QDialog.Accepted:
            mwindow.editor.document().print_(dialog.printer())

    def actorFinder(self, selectedItem):
        actor2find = []
        if selectedItem in self.elementFloorItemList:
            indexOrder = self.elementFloorItemList.index(selectedItem)
            actor2find.append(storeElementPatch[storeElementPatch['Element Type'] == "FloorShell"].at[
                self.elementFloorIndexList[indexOrder], "Actor1"])
        elif selectedItem in self.elementPierItemList:
            indexOrder = self.elementPierItemList.index(selectedItem)
            actor2find.append(storeElementPatch[storeElementPatch['Element Type'] == "Wall - Pier"].at[
                self.elementPierIndexList[indexOrder], "Actor1"])
            actor2find.append(storeElementPatch[storeElementPatch['Element Type'] == "Wall - Pier"].at[
                self.elementPierIndexList[indexOrder], "Actor2"])
        elif selectedItem in self.elementSpandrelItemList:
            indexOrder = self.elementSpandrelItemList.index(selectedItem)
            actor2find.append(storeElementPatch[storeElementPatch['Element Type'] == "Wall - Spandrel"].at[
                self.elementSpandrelIndexList[indexOrder], "Actor1"])
            actor2find.append(storeElementPatch[storeElementPatch['Element Type'] == "Wall - Spandrel"].at[
                self.elementSpandrelIndexList[indexOrder], "Actor2"])
        elif selectedItem in self.elementElasticBeamItemList:
            indexOrder = self.elementElasticBeamItemList.index(selectedItem)
            actor2find.append(storeElementPatch[storeElementPatch['Element Type'] == "ElasticBeam"].at[
                self.elementElasticBeamIndexList[indexOrder], "Actor1"])
        elif selectedItem in self.elementNlinBeamItemList:
            indexOrder = self.elementNlinBeamItemList.index(selectedItem)
            actor2find.append(storeElementPatch[storeElementPatch['Element Type'] == "NonlinearBeam"].at[
                self.elementNlinBeamIndexList[indexOrder], "Actor1"])
        elif selectedItem in self.elementZlenItemList:
            indexOrder = self.elementZlenItemList.index(selectedItem)
            actor2find.append(storeElementPatch[storeElementPatch['Element Type'] == "ZeroLength"].at[
                self.elementZlenIndexList[indexOrder], "Actor1"])
        elif selectedItem in self.nodeItemList:
            indexOrder = self.nodeItemList.index(selectedItem)
            actor2find.append(storeElementPatch[storeElementPatch['Object Type'] == "Node"].at[
                self.nodeIndexList[indexOrder], "Actor1"])

        return actor2find


class MyInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):

    def __init__(self, renderer, mainSidePanel, topLevelItems, topLevelItemList, ModelTreeItems, ModelTreeItemList, elementTreeItems,
                 elementTreeItemList, beamElementTreeItems, beamElementTreeItemList, elementFloorIndexList, elementFloorItemList,
                 elementPierItemList, elementPierIndexList, elementSpandrelIndexList, elementSpandrelItemList,
                 elementElasticBeamIndexList, elementElasticBeamItemList, elementNlinBeamIndexList, elementNlinBeamItemList,
                 elementZlenIndexList, elementZlenItemList, nodeIndexList, nodeItemList, widgetItemList, status, parent=None):
        self.status = status
        self.LastPickedActor = None
        self.LastPickedProperty = vtk.vtkProperty()
        self.renderer = renderer
        self.mainSidePanel = mainSidePanel
        self.topLevelItems = topLevelItems
        self.topLevelItemList = topLevelItemList
        self.ModelTreeItems = ModelTreeItems
        self.ModelTreeItemList = ModelTreeItemList
        self.elementTreeItems = elementTreeItems
        self.elementTreeItemList = elementTreeItemList
        self.beamElementTreeItems = beamElementTreeItems
        self.beamElementTreeItemList = beamElementTreeItemList
        self.elementFloorIndexList = elementFloorIndexList
        self.elementFloorItemList = elementFloorItemList
        self.elementPierItemList = elementPierItemList
        self.elementPierIndexList = elementPierIndexList
        self.elementSpandrelIndexList = elementSpandrelIndexList
        self.elementSpandrelItemList = elementSpandrelItemList
        self.elementElasticBeamIndexList = elementElasticBeamIndexList
        self.elementElasticBeamItemList = elementElasticBeamItemList
        self.elementNlinBeamIndexList = elementNlinBeamIndexList
        self.elementNlinBeamItemList = elementNlinBeamItemList
        self.elementZlenIndexList = elementZlenIndexList
        self.elementZlenItemList = elementZlenItemList
        self.nodeIndexList = nodeIndexList
        self.nodeItemList = nodeItemList
        self.widgetItemList = widgetItemList
        self.pickedObjectProps = []
        self.pickedActorList = []

        # add the actors to the scene
        #renderWindow.Render()
        if self.status == "clicked":
            for actorItem in self.pickedActorList:
                if actorItem not in self.mainSidePanel.selectedItems():
                    self.pickedActorList.remove(actorItem)
            for selectedItem in self.mainSidePanel.selectedItems():
                if selectedItem not in self.pickedActorList:
                    if selectedItem in self.elementFloorItemList:
                        indexOrder = self.elementFloorItemList.index(selectedItem)
                        self.pickedActorList.append(storeElementPatch[storeElementPatch['Element Type'] == "FloorShell"].at[
                            self.elementFloorIndexList[indexOrder], "Actor1"])
                    elif selectedItem in self.elementPierItemList:
                        indexOrder = self.elementPierItemList.index(selectedItem)
                        self.pickedActorList.append(storeElementPatch[storeElementPatch['Element Type'] == "Wall - Pier"].at[
                                                        self.elementPierIndexList[indexOrder], "Actor1"])
                        self.pickedActorList.append(storeElementPatch[storeElementPatch['Element Type'] == "Wall - Pier"].at[
                                self.elementPierIndexList[indexOrder], "Actor2"])
                    elif selectedItem in self.elementSpandrelItemList:
                        indexOrder = self.elementSpandrelItemList.index(selectedItem)
                        self.pickedActorList.append(storeElementPatch[storeElementPatch['Element Type'] == "Wall - Spandrel"].at[
                                self.elementSpandrelIndexList[indexOrder], "Actor1"])
                        self.pickedActorList.append(storeElementPatch[storeElementPatch['Element Type'] == "Wall - Spandrel"].at[
                                self.elementSpandrelIndexList[indexOrder], "Actor2"])
                    elif selectedItem in self.elementElasticBeamItemList:
                        indexOrder = self.elementElasticBeamItemList.index(selectedItem)
                        self.pickedActorList.append(storeElementPatch[storeElementPatch['Element Type'] == "ElasticBeam"].at[
                                self.elementElasticBeamIndexList[indexOrder], "Actor1"])
                    elif selectedItem in self.elementNlinBeamItemList:
                        indexOrder = self.elementNlinBeamItemList.index(selectedItem)
                        self.pickedActorList.append(storeElementPatch[storeElementPatch['Element Type'] == "NonlinearBeam"].at[
                                self.elementNlinBeamIndexList[indexOrder], "Actor1"])
                    elif selectedItem in self.elementZlenItemList:
                        indexOrder = self.elementZlenItemList.index(selectedItem)
                        self.pickedActorList.append(storeElementPatch[storeElementPatch['Element Type'] == "ZeroLength"].at[
                                self.elementZlenIndexList[indexOrder], "Actor1"])
                    elif selectedItem in self.nodeItemList:
                        indexOrder = self.nodeItemList.index(selectedItem)
                        self.pickedActorList.append(storeElementPatch[storeElementPatch['Object Type'] == "Node"].at[
                                self.nodeIndexList[indexOrder], "Actor1"])

            totalStoredPatches = len(storeElementPatch.index.to_list())
            self.resetColor(totalStoredPatches)

            for pickedActorItem in self.pickedActorList:
                pickedActorItem.GetProperty().SetColor(1.0, 1.0, 0.0)
                pickedActorItem.GetProperty().SetDiffuse(1.0)
                pickedActorItem.GetProperty().SetSpecular(0.0)

            self.renderer.GetRenderWindow().Render()
        else:
            self.AddObserver("LeftButtonPressEvent", self.LeftButtonPressEvent)
            self.AddObserver("LeftButtonReleaseEvent", self.LeftButtonReleaseEvent)

    def LeftButtonPressEvent(self,obj,event):
        if self.status != "clicked":
            clickPos = self.GetInteractor().GetEventPosition()
            picker = vtk.vtkCellPicker()
            picker.Pick(clickPos[0], clickPos[1], 0, self.renderer)

            # get the new
            self.NewPickedActor = picker.GetActor()

        # If something was selected
        if self.NewPickedActor:
            if self.NewPickedActor in self.pickedActorList:
                self.pickedActorList.remove(self.NewPickedActor)
                if storeElementPatch['Actor2'][storeElementPatch['Actor1'] == self.NewPickedActor].count() != 0:
                    SecondNewPickedActor = storeElementPatch['Actor2'][storeElementPatch['Actor1'] == self.NewPickedActor].iloc[0]
                    if SecondNewPickedActor != "":
                        self.pickedActorList.remove(SecondNewPickedActor)
                if storeElementPatch['Actor1'][storeElementPatch['Actor2'] == self.NewPickedActor].count() != 0:
                    SecondNewPickedActor = storeElementPatch['Actor1'][storeElementPatch['Actor2'] == self.NewPickedActor].iloc[0]
                    if SecondNewPickedActor != "":
                        self.pickedActorList.remove(SecondNewPickedActor)
            else:
                self.pickedActorList.append(self.NewPickedActor)
                if storeElementPatch['Actor2'][storeElementPatch['Actor1'] == self.NewPickedActor].count() != 0:
                    SecondNewPickedActor = storeElementPatch['Actor2'][storeElementPatch['Actor1'] == self.NewPickedActor].iloc[0]
                    if self.NewPickedActor != "":
                        self.pickedActorList.append(SecondNewPickedActor)
                if storeElementPatch['Actor1'][storeElementPatch['Actor2'] == self.NewPickedActor].count() != 0:
                    SecondNewPickedActor = storeElementPatch['Actor1'][storeElementPatch['Actor2'] == self.NewPickedActor].iloc[0]
                    if self.NewPickedActor != "":
                        self.pickedActorList.append(SecondNewPickedActor)

            totalStoredPatches = len(storeElementPatch.index.to_list())
            self.resetColor(totalStoredPatches)

            for pickedActorItem in self.pickedActorList:
                pickedActorItem.GetProperty().SetColor(1.0, 1.0, 0.0)
                pickedActorItem.GetProperty().SetDiffuse(1.0)
                pickedActorItem.GetProperty().SetSpecular(0.0)

            # Highlight the picked actor by changing its properties
            self.pickedObjectProps = self.NewPickedActor.GetMapper().GetBounds()

            if self.status != "clicked":
                totalStoredPatches = len(storeElementPatch.index.to_list())
                for patchItem in np.arange(totalStoredPatches):
                    if np.array_equal(np.round_(self.pickedObjectProps, 4), np.round_(storeElementPatch['Bounds1'].iat[patchItem], 4)) or \
                            np.array_equal(np.round_(self.pickedObjectProps, 4), np.round_(storeElementPatch['Bounds2'].iat[patchItem], 4)):
                        if storeElementPatch['Element Type'].iat[patchItem] == "FloorShell":
                            self.treeCollapse()
                            indexOrder = self.elementFloorIndexList.index(storeElementPatch.index.to_list()[patchItem])
                            self.mainSidePanel.setCurrentItem(self.topLevelItemList[0])
                            self.mainSidePanel.setCurrentItem(self.elementFloorItemList[indexOrder])
                        elif storeElementPatch['Element Type'].iat[patchItem] == "Wall - Pier":
                            self.treeCollapse()
                            indexOrder = self.elementPierIndexList.index(storeElementPatch.index.to_list()[patchItem])
                            self.mainSidePanel.setCurrentItem(self.topLevelItemList[0])
                            self.mainSidePanel.setCurrentItem(self.elementPierItemList[indexOrder])
                        elif storeElementPatch['Element Type'].iat[patchItem] == "Wall - Spandrel":
                            self.treeCollapse()
                            indexOrder = self.elementSpandrelIndexList.index(storeElementPatch.index.to_list()[patchItem])
                            self.mainSidePanel.setCurrentItem(self.topLevelItemList[0])
                            self.mainSidePanel.setCurrentItem(self.elementSpandrelItemList[indexOrder])
                        elif storeElementPatch['Element Type'].iat[patchItem] == "ElasticBeam":
                            self.treeCollapse()
                            indexOrder = self.elementElasticBeamIndexList.index(storeElementPatch.index.to_list()[patchItem])
                            self.mainSidePanel.setCurrentItem(self.topLevelItemList[0])
                            self.mainSidePanel.setCurrentItem(self.elementElasticBeamItemList[indexOrder])
                        elif storeElementPatch['Element Type'].iat[patchItem] == "NonlinearBeam":
                            self.treeCollapse()
                            indexOrder = self.elementNlinBeamIndexList.index(storeElementPatch.index.to_list()[patchItem])
                            self.mainSidePanel.setCurrentItem(self.topLevelItemList[0])
                            self.mainSidePanel.setCurrentItem(self.elementNlinBeamItemList[indexOrder])
                        elif storeElementPatch['Element Type'].iat[patchItem] == "ZeroLength":
                            self.treeCollapse()
                            indexOrder = self.elementZlenIndexList.index(storeElementPatch.index.to_list()[patchItem])
                            self.mainSidePanel.setCurrentItem(self.topLevelItemList[0])
                            self.mainSidePanel.setCurrentItem(self.elementZlenItemList[indexOrder])
                        elif storeElementPatch['Object Type'].iat[patchItem] == "Node":
                            self.treeCollapse()
                            indexOrder = self.nodeIndexList.index(storeElementPatch.index.to_list()[patchItem])
                            self.mainSidePanel.setCurrentItem(self.topLevelItemList[0])
                            self.mainSidePanel.setCurrentItem(self.nodeItemList[indexOrder])
                        break

            self.renderer.GetRenderWindow().Render()


        self.OnLeftButtonDown()
        return

    def resetColor(self, totalStoredPatches):
        for patchItem in np.arange(totalStoredPatches):
            if storeElementPatch['Element Type'].iat[patchItem] == "FloorShell":
                storeElementPatch['Actor1'].iat[patchItem].GetProperty().SetColor(0.0, 1.0, 0.0)
                storeElementPatch['Actor1'].iat[patchItem].GetProperty().SetDiffuse(1.0)
                storeElementPatch['Actor1'].iat[patchItem].GetProperty().SetSpecular(0.0)
            elif storeElementPatch['Element Type'].iat[patchItem] == "Wall - Pier":
                storeElementPatch['Actor1'].iat[patchItem].GetProperty().SetColor(1.0, 0.0, 0.0)
                storeElementPatch['Actor1'].iat[patchItem].GetProperty().SetDiffuse(1.0)
                storeElementPatch['Actor1'].iat[patchItem].GetProperty().SetSpecular(0.0)
                if storeElementPatch['Actor2'].iat[patchItem] != "":
                    storeElementPatch['Actor2'].iat[patchItem].GetProperty().SetColor(1.0, 0.0, 0.0)
                    storeElementPatch['Actor2'].iat[patchItem].GetProperty().SetDiffuse(1.0)
                    storeElementPatch['Actor2'].iat[patchItem].GetProperty().SetSpecular(0.0)
            elif storeElementPatch['Element Type'].iat[patchItem] == "Wall - Spandrel":
                storeElementPatch['Actor1'].iat[patchItem].GetProperty().SetColor(0.0, 0.0, 1.0)
                storeElementPatch['Actor1'].iat[patchItem].GetProperty().SetDiffuse(1.0)
                storeElementPatch['Actor1'].iat[patchItem].GetProperty().SetSpecular(0.0)
                if storeElementPatch['Actor2'].iat[patchItem] != "":
                    storeElementPatch['Actor2'].iat[patchItem].GetProperty().SetColor(0.0, 0.0, 1.0)
                    storeElementPatch['Actor2'].iat[patchItem].GetProperty().SetDiffuse(1.0)
                    storeElementPatch['Actor2'].iat[patchItem].GetProperty().SetSpecular(0.0)
            elif storeElementPatch['Element Type'].iat[patchItem] == "ElasticBeam":
                storeElementPatch['Actor1'].iat[patchItem].GetProperty().SetColor(0.7529411764705882,
                                                                                  0.7529411764705882,
                                                                                  0.7529411764705882)
                storeElementPatch['Actor1'].iat[patchItem].GetProperty().SetDiffuse(1.0)
                storeElementPatch['Actor1'].iat[patchItem].GetProperty().SetSpecular(0.0)
            elif storeElementPatch['Element Type'].iat[patchItem] == "NonlinearBeam":
                storeElementPatch['Actor1'].iat[patchItem].GetProperty().SetColor(0.7529411764705882,
                                                                                  0.7529411764705882,
                                                                                  0.7529411764705882)
                storeElementPatch['Actor1'].iat[patchItem].GetProperty().SetDiffuse(1.0)
                storeElementPatch['Actor1'].iat[patchItem].GetProperty().SetSpecular(0.0)
            elif storeElementPatch['Element Type'].iat[patchItem] == "ZeroLength":
                storeElementPatch['Actor1'].iat[patchItem].GetProperty().SetColor(0.7529411764705882,
                                                                                  0.7529411764705882,
                                                                                  0.7529411764705882)
                storeElementPatch['Actor1'].iat[patchItem].GetProperty().SetDiffuse(1.0)
                storeElementPatch['Actor1'].iat[patchItem].GetProperty().SetSpecular(0.0)
            elif storeElementPatch['Object Type'].iat[patchItem] == "Node":
                if storeElementPatch['Actor1'].iat[patchItem] == storeElementPatch['Actor1'].iat[patchItem]:
                    storeElementPatch['Actor1'].iat[patchItem].GetProperty().SetColor(0.7529411764705882,
                                                                                      0.7529411764705882,
                                                                                      0.7529411764705882)
                    storeElementPatch['Actor1'].iat[patchItem].GetProperty().SetDiffuse(1.0)
                    storeElementPatch['Actor1'].iat[patchItem].GetProperty().SetSpecular(0.0)


    def treeCollapse(self):
        for parentItem in self.widgetItemList:
            for item in parentItem:
                item.setExpanded(False)

    def LeftButtonReleaseEvent(self,obj,event):
        self.OnLeftButtonUp()
        return

class vtkTimerCallback():
   def __init__(self, renderer, f_nodeList, f_elementList, f_nodeIndexList):
       self.timer_count = 0
       self.renderer = renderer
       self.elementList = f_elementList
       self.nodeList = f_nodeList
       self.nodeIndexList = f_nodeIndexList

   def dummyFunc(self, obj, event):
        print("I'm dummy")

   def execute(self,obj,event):
       self.timeInt = self.timer_count // 15
       if self.timer_count == 150:
           self.renIntract.DestroyTimer(self.tID)
           self.renderer.RemoveActor(self.actor)
           self.renIntract.RemoveObservers('TimerEvent')
           self.renIntract.SetInteractorStyle(MyInteractorStyle(self.renderer, self.nodeList, self.elementList, self.nodeIndexList))
       elif self.timeInt % 2 == 0:
           self.actor.SetVisibility(True)
       else:
           self.actor.SetVisibility(False)
       iren = obj
       iren.GetRenderWindow().Render()
       self.timer_count += 1

class viewUpdater():
    def __init__(self):
        super().__init__()

    def nodeHighlighter(self, f_nodeList, f_elementList, f_nodeIndexList, renderer, colors, iren):
        nodeSphere = vtk.vtkSphereSource()
        slctdNode = int(f_nodeList.currentItem().text())
        nodeSphere.SetCenter(node.at[slctdNode, 'x'], node.at[slctdNode, 'y'], node.at[slctdNode, 'z'])
        nodeSphere.SetRadius(0.1)
        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputConnection(nodeSphere.GetOutputPort())
        nodeActor = vtk.vtkActor()
        nodeActor.SetMapper(mapper)
        nodeActor.GetProperty().SetColor(colors.GetColor3d('Yellow'))
        renderer.AddActor(nodeActor)
        iren.GetRenderWindow().Render()
        cb = vtkTimerCallback(renderer, f_nodeList, f_elementList, f_nodeIndexList)
        cb.actor = nodeActor
        timerId = iren.CreateOneShotTimer(300)
        cb.tID = timerId
        cb.renIntract = iren
        cb.renderer = renderer
        iren.AddObserver('TimerEvent', cb.execute)


def handleExport():
    TCLfileName = QtGui.QFileDialog.getSaveFileName(parent=mWindow, caption="Save File", filter='OpenSees TCL files (*.tcl)')
    print(TCLfileName)


def get_prjName(f_prjName, f_mWindow, f_prjNameDialog):
    mainActions.prjName = f_prjName.text()
    f_mWindow.setWindowTitle("Masonry Interface  (" + f_prjName.text() + ")")
    f_prjNameDialog.close()


def matItemActivated_event(f_matList, f_copyMatBtn, f_editMatBtn, f_deleteMatBtn):
    global currentMatItem
    f_copyMatBtn.setDisabled(False)
    f_editMatBtn.setDisabled(False)
    f_deleteMatBtn.setDisabled(False)
    currentMatItem = f_matList.currentItem().text()
    return currentMatItem


def materialDialog():
    global tmp_material
    tmp_material = material.copy(deep=True)
    matDialog = QtGui.QDialog()
    matDialog.setWindowTitle("Define Material")
    matDialogLayout = QGridLayout()
    matDialogBtn = QWidget()
    matDialogBtnLayout = QGridLayout()

    matList = QListWidget()
    for matItem in np.arange(material['E'].count()):
        matList.addItem(str(material.index.to_list()[matItem]))
    matList.itemSelectionChanged.connect(lambda: matItemActivated_event(matList, copyMatBtn, editMatBtn, deleteMatBtn))

    addNewMatBtn = QPushButton('Add New Material...', matDialogBtn)
    addNewMatBtn.setToolTip('Define a new material')
    addNewMatBtn.clicked.connect(matEditDialog)
    addNewMatBtn.resize(addNewMatBtn.sizeHint())
    addNewMatBtn.move(200, 80)
    addNewMatBtn.setStyleSheet("padding-left: 10px; padding-right: 10px; padding-top: 5px; padding-bottom: 5px;")

    copyMatBtn = QPushButton('Copy Material', matDialogBtn)
    copyMatBtn.setToolTip('Copy existing material and create a new material')
    copyMatBtn.clicked.connect(matEditDialog)
    copyMatBtn.resize(copyMatBtn.sizeHint())
    copyMatBtn.move(200, 80)
    copyMatBtn.setDisabled(True)

    editMatBtn = QPushButton('Edit Material...', matDialogBtn)
    editMatBtn.setToolTip('Edit existing material')
    editMatBtn.clicked.connect(matEditDialog)
    editMatBtn.resize(editMatBtn.sizeHint())
    editMatBtn.move(200, 80)
    editMatBtn.setDisabled(True)

    deleteMatBtn = QPushButton('Delete Material', matDialogBtn)
    deleteMatBtn.setToolTip('Delete existing material')
    deleteMatBtn.clicked.connect(matEditDialog)
    deleteMatBtn.resize(deleteMatBtn.sizeHint())
    deleteMatBtn.move(200, 80)
    deleteMatBtn.setDisabled(True)

    # Add a button
    applyMainMatBtn = QPushButton('Apply', matDialogBtn)
    applyMainMatBtn.setToolTip('Click to Apply')
    applyMainMatBtn.clicked.connect(lambda: get_matEntries(matDialog))
    applyMainMatBtn.resize(applyMainMatBtn.sizeHint())
    applyMainMatBtn.move(100, 80)

    cancelMainMatBtn = QPushButton('Cancel', matDialogBtn)
    cancelMainMatBtn.setToolTip('Cancel Modifications')
    cancelMainMatBtn.clicked.connect(lambda: cancelMainMatBtnAct(matDialog, tmp_material))
    cancelMainMatBtn.resize(cancelMainMatBtn.sizeHint())
    cancelMainMatBtn.move(100, 80)

    matDialogLayout.addWidget(matList, 1, 1, 5, 1)
    matDialogLayout.addWidget(addNewMatBtn, 1, 3)
    matDialogLayout.addWidget(copyMatBtn, 2, 3)
    matDialogLayout.addWidget(editMatBtn, 3, 3)
    matDialogLayout.addWidget(deleteMatBtn, 4, 3)
    matDialogLayout.addWidget(matDialogBtn, 6, 1, 6, 3)
    matDialogBtnLayout.addWidget(applyMainMatBtn, 0, 0)
    matDialogBtnLayout.addWidget(cancelMainMatBtn, 0, 1)
    matDialog.setLayout(matDialogLayout)
    matDialogBtn.setLayout(matDialogBtnLayout)
    matDialog.setFixedSize(400, 200)

    if matDialog.exec_() == QtGui.QDialog.Accepted:
        matDialog.show()
    return tmp_material

def matEditDialog():
    matEdDialog = QtGui.QDialog()
    matEdDialog.setWindowTitle("Edit Material")
    matEdDialogLayout = QGridLayout()
    matEdDialogBtn = QWidget()
    matEdDialogBtnLayout = QGridLayout()

    matNumTtl = QLabel("Material No.")
    matNum = QLineEdit(currentMatItem)
    matYModulTtl = QLabel("Young Modulus (E)")
    matYModulUnt = QLabel("[MPa]")
    matYModul = QLineEdit('{:.2f}'.format(material.at[int(currentMatItem), "E"] * 10 ** (-6)))
    matShModulTtl = QLabel("Shear Modulus (G)")
    matShModulUnt = QLabel("[MPa]")
    matShModul = QLineEdit('{:.2f}'.format(material.at[int(currentMatItem), "G"] * 10 ** (-6)))
    matDenTtl = QLabel("Density (\u03C1)")
    matDenUnt = QLabel("[kg/m3]")
    if not np.isnan(material.at[int(currentMatItem), "rho"]):
        matDen = QLineEdit(str(material.at[int(currentMatItem), "rho"]))
    else:
        matDen = QLineEdit()
    fmTtl = QLabel("Compressive Strength (fm)")
    fmUnt = QLabel("[MPa]")
    if not np.isnan(material.at[int(currentMatItem), "fc"]):
        fm = QLineEdit('{:.2f}'.format(material.at[int(currentMatItem), "fc"] * 10 ** (-6)))
    else:
        fm = QLineEdit()
    fm.setDisabled(True)
    fyTtl = QLabel("Yield Strength (fy)")
    fyUnt = QLabel("[MPa]")
    if not np.isnan(material.at[int(currentMatItem), "fc"]):
        fy = QLineEdit('{:.2f}'.format(material.at[int(currentMatItem), "fc"] * 10 ** (-6)))
    else:
        fy = QLineEdit()
    fy.setDisabled(True)
    fcTtl = QLabel("Cylindrical Compressive Strength (fc)")
    fcUnt = QLabel("[MPa]")
    if not np.isnan(material.at[int(currentMatItem), "fc"]):
        fc = QLineEdit('{:.2f}'.format(material.at[int(currentMatItem), "fc"] * 10 ** (-6)))
    else:
        fc = QLineEdit()
    fc.setDisabled(True)
    tau0Ttl = QLabel("Shear Strength (\u03C40 or fv0)")
    tau0Unt = QLabel("[MPa]")
    if not np.isnan(material.at[int(currentMatItem), "tau0"]):
        tau0 = QLineEdit('{:.2f}'.format(material.at[int(currentMatItem), "tau0"] * 10 ** (-6)))
    else:
        tau0 = QLineEdit()
    tau0.setDisabled(True)
    fvlimTtl = QLabel("Maximum cohesion stress (fvlim)")
    fvlimUnt = QLabel("[MPa]")
    if not np.isnan(material.at[int(currentMatItem), "verification"]):
        fvlim = QLineEdit('{:.2f}'.format(material.at[int(currentMatItem), "verification"] * 10 ** (-6)))
    else:
        fvlim = QLineEdit()
    fvlim.setDisabled(False)
    shModeTtl = QLabel("Shear Model")
    shMode = QComboBox()
    shModeList = ["", "Turnsek & cacovic", "Mohr-Coulomb (Effective Shear Area)", "Mohr-Coulomb (Gross Shear Area)"]
    for shModeItem in shModeList:
        shMode.addItem(shModeItem)
    if not np.isnan(material.at[int(currentMatItem), "shear_model"]):
        shMode.setCurrentIndex(int(material.at[int(currentMatItem), "shear_model"]))
    shMode.setDisabled(True)
    GcTtl = QLabel("Nonlinear deformability parameter (Gc)")
    if not np.isnan(material.at[int(currentMatItem), "Gc"]):
        Gc = QLineEdit(str(material.at[int(currentMatItem), "Gc"]))
    else:
        Gc = QLineEdit()
    Gc.setDisabled(True)
    drift_STtl = QLabel("Shear ultimate drift ratio (\u03B4v)")
    if not np.isnan(material.at[int(currentMatItem), "drift_S"]):
        drift_S = QLineEdit(str(material.at[int(currentMatItem), "drift_S"]))
    else:
        drift_S = QLineEdit()
    drift_S.setDisabled(True)
    drift_FTtl = QLabel("Rocking ultimate drift ratio (\u03B4r)")
    if not np.isnan(material.at[int(currentMatItem), "drift_F"]):
        drift_F = QLineEdit(str(material.at[int(currentMatItem), "drift_F"]))
    else:
        drift_F = QLineEdit()
    drift_F.setDisabled(True)
    muTtl = QLabel("Friction coefficient (\u03BC)")
    if not np.isnan(material.at[int(currentMatItem), "mu"]):
        mu = QLineEdit(str(material.at[int(currentMatItem), "mu"]))
    else:
        mu = QLineEdit()
    mu.setDisabled(True)
    betaTtl = QLabel("Softening parameter (\u03B2)")
    if not np.isnan(material.at[int(currentMatItem), "beta"]):
        beta = QLineEdit(str(material.at[int(currentMatItem), "beta"]))
    else:
        beta = QLineEdit()
    beta.setDisabled(True)
    muRTtl = QLabel("\u03BCR")
    if not np.isnan(material.at[int(currentMatItem), "Gc"]):
        muR = QLineEdit(str(material.at[int(currentMatItem), "mu"] * 0.5))
    else:
        muR = QLineEdit()
    muR.setDisabled(True)

    # Add element type selection box
    elTypeSelecTtl = QLabel("Element Type")
    elTypeSelec = QComboBox()
    elTypeSelecList = ["Bilinear", "Concrete Beam", "Macroelement", "Masonry", "Steel Beam", "Elastic Beam"]
    for elTyItem in elTypeSelecList:
        elTypeSelec.addItem(elTyItem)

    if len(element[element['mat'] == int(currentMatItem)].index.to_list()) > 0:
        elTypeIndex = element[element['mat'] == int(currentMatItem)].index.to_list()[0]
        elType = element.at[elTypeIndex, "type"]

        if elType == "Macroelement3d":
            elTypeSelec.setCurrentIndex(2)
            fm.setDisabled(True)
            fy.setDisabled(True)
            fc.setDisabled(False)
            shMode.setDisabled(False)
            fvlim.setDisabled(True)
            tau0.setDisabled(False)
            Gc.setDisabled(False)
            drift_S.setDisabled(False)
            drift_F.setDisabled(False)
            if shMode.currentText() != "Turnsek & cacovic":
                mu.setDisabled(False)
            else:
                mu.setDisabled(True)
            beta.setDisabled(False)
            if not np.isnan(material.at[int(currentMatItem), "Gc"]):
                muR.setDisabled(False)
            else:
                muR.setDisabled(True)

        elif elType == "ElasticBeam":
            elTypeSelec.setCurrentIndex(1)
            fm.setDisabled(True)
            fy.setDisabled(True)
            fc.setDisabled(False)
            shMode.setDisabled(False)
            fvlim.setDisabled(True)
            tau0.setDisabled(True)
            Gc.setDisabled(True)
            drift_S.setDisabled(True)
            drift_F.setDisabled(True)
            mu.setDisabled(True)
            beta.setDisabled(True)
            if not np.isnan(material.at[int(currentMatItem), "Gc"]):
                muR.setDisabled(False)
            else:
                muR.setDisabled(True)

    elTypeSelec.currentIndexChanged.connect(lambda: elTypeChange(elTypeSelec, fm, fy, fc, shMode, fvlim, tau0, Gc, drift_S, drift_F, mu, beta, muR))
    shMode.currentIndexChanged.connect(lambda: shTypeChange(elTypeSelec, shMode, mu))
    mu.textChanged.connect(lambda: muTextChange(mu, muR))

    # Add a button
    applyMatBtn = QPushButton('Apply', widget)
    applyMatBtn.setToolTip('Click to Apply')
    applyMatBtn.clicked.connect(lambda: get_matEdEntries(matYModul, matShModul, fm, fy, fc, tau0, fvlim, matDen, shMode, Gc, drift_S, drift_F, mu, beta, muR, matEdDialog))
    applyMatBtn.resize(applyMatBtn.sizeHint())
    applyMatBtn.move(100, 80)

    cancelMatBtn = QPushButton('Cancel', widget)
    cancelMatBtn.setToolTip('Cancel Modifications')
    cancelMatBtn.clicked.connect(matEdDialog.close)
    cancelMatBtn.resize(cancelMatBtn.sizeHint())
    cancelMatBtn.move(100, 80)

    matEdDialogLayout.addWidget(matNumTtl, 1, 0)
    matEdDialogLayout.addWidget(matNum, 1, 1)
    matEdDialogLayout.addWidget(elTypeSelecTtl, 1, 6)
    matEdDialogLayout.addWidget(elTypeSelec, 1, 7)
    matEdDialogLayout.addWidget(matYModulTtl, 2, 0)
    matEdDialogLayout.addWidget(matYModul, 2, 1)
    matEdDialogLayout.addWidget(matYModulUnt, 2, 2)
    matEdDialogLayout.addWidget(matShModulTtl, 2, 3)
    matEdDialogLayout.addWidget(matShModul, 2, 4)
    matEdDialogLayout.addWidget(matShModulUnt, 2, 5)
    matEdDialogLayout.addWidget(matDenTtl, 2, 6)
    matEdDialogLayout.addWidget(matDen, 2, 7)
    matEdDialogLayout.addWidget(matDenUnt, 2, 8)
    matEdDialogLayout.addWidget(fmTtl, 3, 0)
    matEdDialogLayout.addWidget(fm, 3, 1)
    matEdDialogLayout.addWidget(fmUnt, 3, 2)
    matEdDialogLayout.addWidget(fyTtl, 3, 3)
    matEdDialogLayout.addWidget(fy, 3, 4)
    matEdDialogLayout.addWidget(fyUnt, 3, 5)
    matEdDialogLayout.addWidget(fcTtl, 3, 6)
    matEdDialogLayout.addWidget(fc, 3, 7)
    matEdDialogLayout.addWidget(fcUnt, 3, 8)
    matEdDialogLayout.addWidget(tau0Ttl, 4, 0)
    matEdDialogLayout.addWidget(tau0, 4, 1)
    matEdDialogLayout.addWidget(tau0Unt, 4, 2)
    matEdDialogLayout.addWidget(fvlimTtl, 4, 3)
    matEdDialogLayout.addWidget(fvlim, 4, 4)
    matEdDialogLayout.addWidget(fvlimUnt, 4, 5)
    matEdDialogLayout.addWidget(shModeTtl, 4, 6)
    matEdDialogLayout.addWidget(shMode, 4, 7)
    matEdDialogLayout.addWidget(GcTtl, 5, 0)
    matEdDialogLayout.addWidget(Gc, 5, 1)
    matEdDialogLayout.addWidget(drift_STtl, 5, 3)
    matEdDialogLayout.addWidget(drift_S, 5, 4)
    matEdDialogLayout.addWidget(drift_FTtl, 5, 6)
    matEdDialogLayout.addWidget(drift_F, 5, 7)
    matEdDialogLayout.addWidget(muTtl, 6, 0)
    matEdDialogLayout.addWidget(mu, 6, 1)
    matEdDialogLayout.addWidget(betaTtl, 6, 3)
    matEdDialogLayout.addWidget(beta, 6, 4)
    matEdDialogLayout.addWidget(muRTtl, 6, 6)
    matEdDialogLayout.addWidget(muR, 6, 7)
    matEdDialogLayout.addWidget(matEdDialogBtn, 7, 7)
    matEdDialogBtnLayout.addWidget(applyMatBtn, 0, 0)
    matEdDialogBtnLayout.addWidget(cancelMatBtn, 0, 1)

    matEdDialog.setLayout(matEdDialogLayout)
    matEdDialogBtn.setLayout(matEdDialogBtnLayout)

    if matEdDialog.exec_() == QtGui.QDialog.Accepted:
        matEdDialog.show()


def elTypeChange(f_elTypeSelec, f_fm, f_fy, f_fc, f_shMode, f_fvlim, f_tau0, f_Gc, f_drift_S, f_drift_F, f_mu, f_beta, f_muR):
    if f_elTypeSelec.currentText() == "Masonry":
        f_fm.setDisabled(False)
        f_fy.setDisabled(True)
        f_fc.setDisabled(True)
        f_shMode.setDisabled(False)
        f_fvlim.setDisabled(True)
        f_tau0.setDisabled(True)
        f_Gc.setDisabled(True)
        f_drift_S.setDisabled(False)
        f_drift_F.setDisabled(False)
        if f_shMode.currentText() != "Turnsek & cacovic":
            f_mu.setDisabled(False)
        else:
            f_mu.setDisabled(True)
        f_beta.setDisabled(True)
        if not np.isnan(material.at[int(currentMatItem), "Gc"]):
            f_muR.setDisabled(False)
        else:
            f_muR.setDisabled(True)
    elif f_elTypeSelec.currentText() == "Steel Beam":
        f_fm.setDisabled(True)
        f_fy.setDisabled(False)
        f_fc.setDisabled(True)
        f_shMode.setDisabled(False)
        f_fvlim.setDisabled(True)
        f_tau0.setDisabled(True)
        f_Gc.setDisabled(True)
        f_drift_S.setDisabled(True)
        f_drift_F.setDisabled(True)
        f_mu.setDisabled(True)
        f_beta.setDisabled(True)
        if not np.isnan(material.at[int(currentMatItem), "Gc"]):
            f_muR.setDisabled(False)
        else:
            f_muR.setDisabled(True)
    elif f_elTypeSelec.currentText() == "Concrete Beam":
        f_fm.setDisabled(True)
        f_fy.setDisabled(True)
        f_fc.setDisabled(False)
        f_shMode.setDisabled(False)
        f_fvlim.setDisabled(True)
        f_tau0.setDisabled(True)
        f_Gc.setDisabled(True)
        f_drift_S.setDisabled(True)
        f_drift_F.setDisabled(True)
        f_mu.setDisabled(True)
        f_beta.setDisabled(True)
        if not np.isnan(material.at[int(currentMatItem), "Gc"]):
            f_muR.setDisabled(False)
        else:
            f_muR.setDisabled(True)
    elif f_elTypeSelec.currentText() == "Macroelement":
        f_fm.setDisabled(True)
        f_fy.setDisabled(True)
        f_fc.setDisabled(False)
        f_shMode.setDisabled(False)
        f_fvlim.setDisabled(True)
        f_tau0.setDisabled(False)
        f_Gc.setDisabled(False)
        f_drift_S.setDisabled(False)
        f_drift_F.setDisabled(False)
        if f_shMode.currentText() != "Turnsek & cacovic":
            f_mu.setDisabled(False)
        else:
            f_mu.setDisabled(True)
        f_beta.setDisabled(False)
        if not np.isnan(material.at[int(currentMatItem), "Gc"]):
            f_muR.setDisabled(False)
        else:
            f_muR.setDisabled(True)
    else:
        f_fm.setDisabled(True)
        f_fy.setDisabled(True)
        f_fc.setDisabled(True)
        f_shMode.setDisabled(False)
        f_fvlim.setDisabled(False)
        f_tau0.setDisabled(False)
        f_Gc.setDisabled(True)
        f_drift_S.setDisabled(True)
        f_drift_F.setDisabled(True)
        f_mu.setDisabled(True)
        f_beta.setDisabled(True)
        if not np.isnan(material.at[int(currentMatItem), "Gc"]):
            f_muR.setDisabled(False)
        else:
            f_muR.setDisabled(True)


def shTypeChange(f_elTypeSelec, f_shMode, f_mu):
    if f_shMode.currentText() != "Turnsek & cacovic" and (f_elTypeSelec.currentText() == "Macroelement" or f_elTypeSelec.currentText() == "Masonry"):
        f_mu.setDisabled(False)
    else:
        f_mu.setDisabled(True)


def muTextChange(f_mu, f_muR):
    if (f_mu.text()) != "":
        f_muR.setText(str(float(f_mu.text()) * 0.5))
        f_muR.setDisabled(False)
    else:
        f_muR.setText("")
        f_muR.setDisabled(True)


def get_matEdEntries(f_matYModul, f_matShModul, f_fm, f_fy, f_fc, f_tau0, f_fvlim, f_matDen, f_shMode, f_Gc, f_drift_S, f_drift_F, f_mu, f_beta, f_muR, f_matEdDialog):
    tmp_material.at[int(currentMatItem), "E"] = float(f_matYModul.text()) * (10 ** 6)
    tmp_material.at[int(currentMatItem), "G"] = float(f_matShModul.text()) * (10 ** 6)
    if f_fm.isEnabled():
        tmp_material.at[int(currentMatItem), "fc"] = float(f_fm.text()) * (10 ** 6)
    else:
        tmp_material.at[int(currentMatItem), "fc"] = np.nan
    if f_fy.isEnabled():
        tmp_material.at[int(currentMatItem), "fc"] = float(f_fy.text()) * (10 ** 6)
    else:
        tmp_material.at[int(currentMatItem), "fc"] = np.nan
    if f_fc.isEnabled():
        tmp_material.at[int(currentMatItem), "fc"] = float(f_fc.text()) * (10 ** 6)
    else:
        tmp_material.at[int(currentMatItem), "fc"] = np.nan
    if f_tau0.isEnabled():
        tmp_material.at[int(currentMatItem), "tau0"] = float(f_tau0.text()) * (10 ** 6)
    else:
        tmp_material.at[int(currentMatItem), "tau0"] = np.nan
    if f_fvlim.isEnabled():
        tmp_material.at[int(currentMatItem), "verification"] = float(f_fvlim.text()) * (10 ** 6)
    else:
        tmp_material.at[int(currentMatItem), "verification"] = np.nan
    if f_matDen != "":
        tmp_material.at[int(currentMatItem), "rho"] = float(f_matDen.text())
    else:
        tmp_material.at[int(currentMatItem), "rho"] = np.nan
    if f_shMode.isEnabled():
        if f_shMode.currentText() == "":
            tmp_material.at[int(currentMatItem), "shear_model"] = np.nan
        elif f_shMode.currentText() == "Turnsek & cacovic":
            tmp_material.at[int(currentMatItem), "shear_model"] = 1
        elif f_shMode.currentText() == "Mohr-Coulomb (Effective Shear Area)":
            tmp_material.at[int(currentMatItem), "shear_model"] = 2
        elif f_shMode.currentText() == "Mohr-Coulomb (Gross Shear Area)":
            tmp_material.at[int(currentMatItem), "shear_model"] = 3
    else:
        tmp_material.at[int(currentMatItem), "shear_model"] = np.nan
    if f_Gc.isEnabled():
        tmp_material.at[int(currentMatItem), "Gc"] = float(f_Gc.text())
    else:
        tmp_material.at[int(currentMatItem), "Gc"] = np.nan
    if f_drift_S.isEnabled():
        tmp_material.at[int(currentMatItem), "drift_S"] = float(f_drift_S.text())
    else:
        tmp_material.at[int(currentMatItem), "drift_S"] = np.nan
    if f_drift_F.isEnabled():
        tmp_material.at[int(currentMatItem), "drift_F"] = float(f_drift_F.text())
    else:
        tmp_material.at[int(currentMatItem), "drift_F"] = np.nan
    if f_mu.isEnabled():
        tmp_material.at[int(currentMatItem), "mu"] = float(f_mu.text())
    else:
        tmp_material.at[int(currentMatItem), "mu"] = np.nan
    if f_beta.isEnabled():
        tmp_material.at[int(currentMatItem), "beta"] = float(f_beta.text())
    else:
        tmp_material.at[int(currentMatItem), "beta"] = np.nan
    if f_muR.isEnabled():
        tmp_material.at[int(currentMatItem), "muR"] = float(f_muR.text())
    else:
        tmp_material.at[int(currentMatItem), "muR"] = np.nan
    f_matEdDialog.close()


def get_matEntries(f_matDialog):
    material = tmp_material.copy(deep=True)
    f_matDialog.close()
    return material


def cancelMainMatBtnAct(f_matDialog, tmp_material):
    del tmp_material
    f_matDialog.close()


def analysisItemActivated_event(f_analysisList, f_copyAnalysisBtn, f_editAnalysisBtn, f_deleteAnalysisBtn):
    global currentAnalysisItem
    f_copyAnalysisBtn.setDisabled(False)
    f_editAnalysisBtn.setDisabled(False)
    f_deleteAnalysisBtn.setDisabled(False)
    currentAnalysisItem = str(analysis.index.to_list()[f_analysisList.currentRow()])
    return currentAnalysisItem


def restraintDialog():
    restDialog = QtGui.QDialog()
    restDialog.setWindowTitle("Edit Material")
    restDialogLayout = QGridLayout()
    restDialogBtn = QWidget()
    restDialogBtnLayout = QGridLayout()

    matNumTtl = QLabel("Material No.")
    matNum = QLineEdit(currentMatItem)
    matYModulTtl = QLabel("Young Modulus (E)")
    matYModulUnt = QLabel("[MPa]")
    matYModul = QLineEdit('{:.2f}'.format(material.at[int(currentMatItem), "E"] * 10 ** (-6)))
    matShModulTtl = QLabel("Shear Modulus (G)")
    matShModulUnt = QLabel("[MPa]")
    matShModul = QLineEdit('{:.2f}'.format(material.at[int(currentMatItem), "G"] * 10 ** (-6)))
    matDenTtl = QLabel("Density (\u03C1)")
    matDenUnt = QLabel("[kg/m3]")
    if not np.isnan(material.at[int(currentMatItem), "rho"]):
        matDen = QLineEdit(str(material.at[int(currentMatItem), "rho"]))
    else:
        matDen = QLineEdit()
    fmTtl = QLabel("Compressive Strength (fm)")
    fmUnt = QLabel("[MPa]")
    if not np.isnan(material.at[int(currentMatItem), "fc"]):
        fm = QLineEdit('{:.2f}'.format(material.at[int(currentMatItem), "fc"] * 10 ** (-6)))
    else:
        fm = QLineEdit()
    fm.setDisabled(True)
    fyTtl = QLabel("Yield Strength (fy)")
    fyUnt = QLabel("[MPa]")
    if not np.isnan(material.at[int(currentMatItem), "fc"]):
        fy = QLineEdit('{:.2f}'.format(material.at[int(currentMatItem), "fc"] * 10 ** (-6)))
    else:
        fy = QLineEdit()
    fy.setDisabled(True)
    fcTtl = QLabel("Cylindrical Compressive Strength (fc)")
    fcUnt = QLabel("[MPa]")
    if not np.isnan(material.at[int(currentMatItem), "fc"]):
        fc = QLineEdit('{:.2f}'.format(material.at[int(currentMatItem), "fc"] * 10 ** (-6)))
    else:
        fc = QLineEdit()
    fc.setDisabled(True)
    tau0Ttl = QLabel("Shear Strength (\u03C40 or fv0)")
    tau0Unt = QLabel("[MPa]")
    if not np.isnan(material.at[int(currentMatItem), "tau0"]):
        tau0 = QLineEdit('{:.2f}'.format(material.at[int(currentMatItem), "tau0"] * 10 ** (-6)))
    else:
        tau0 = QLineEdit()
    tau0.setDisabled(True)
    fvlimTtl = QLabel("Maximum cohesion stress (fvlim)")
    fvlimUnt = QLabel("[MPa]")
    if not np.isnan(material.at[int(currentMatItem), "verification"]):
        fvlim = QLineEdit('{:.2f}'.format(material.at[int(currentMatItem), "verification"] * 10 ** (-6)))
    else:
        fvlim = QLineEdit()
    fvlim.setDisabled(False)
    shModeTtl = QLabel("Shear Model")
    shMode = QComboBox()
    shModeList = ["", "Turnsek & cacovic", "Mohr-Coulomb (Effective Shear Area)", "Mohr-Coulomb (Gross Shear Area)"]
    for shModeItem in shModeList:
        shMode.addItem(shModeItem)
    if not np.isnan(material.at[int(currentMatItem), "shear_model"]):
        shMode.setCurrentIndex(int(material.at[int(currentMatItem), "shear_model"]))
    shMode.setDisabled(True)
    GcTtl = QLabel("Nonlinear deformability parameter (Gc)")
    if not np.isnan(material.at[int(currentMatItem), "Gc"]):
        Gc = QLineEdit(str(material.at[int(currentMatItem), "Gc"]))
    else:
        Gc = QLineEdit()
    Gc.setDisabled(True)
    drift_STtl = QLabel("Shear ultimate drift ratio (\u03B4v)")
    if not np.isnan(material.at[int(currentMatItem), "drift_S"]):
        drift_S = QLineEdit(str(material.at[int(currentMatItem), "drift_S"]))
    else:
        drift_S = QLineEdit()
    drift_S.setDisabled(True)
    drift_FTtl = QLabel("Rocking ultimate drift ratio (\u03B4r)")
    if not np.isnan(material.at[int(currentMatItem), "drift_F"]):
        drift_F = QLineEdit(str(material.at[int(currentMatItem), "drift_F"]))
    else:
        drift_F = QLineEdit()
    drift_F.setDisabled(True)
    muTtl = QLabel("Friction coefficient (\u03BC)")
    if not np.isnan(material.at[int(currentMatItem), "mu"]):
        mu = QLineEdit(str(material.at[int(currentMatItem), "mu"]))
    else:
        mu = QLineEdit()
    mu.setDisabled(True)
    betaTtl = QLabel("Softening parameter (\u03B2)")
    if not np.isnan(material.at[int(currentMatItem), "beta"]):
        beta = QLineEdit(str(material.at[int(currentMatItem), "beta"]))
    else:
        beta = QLineEdit()
    beta.setDisabled(True)
    muRTtl = QLabel("\u03BCR")
    if not np.isnan(material.at[int(currentMatItem), "Gc"]):
        muR = QLineEdit(str(material.at[int(currentMatItem), "mu"] * 0.5))
    else:
        muR = QLineEdit()
    muR.setDisabled(True)

    # Add element type selection box
    elTypeSelecTtl = QLabel("Element Type")
    elTypeSelec = QComboBox()
    elTypeSelecList = ["Bilinear", "Concrete Beam", "Macroelement", "Masonry", "Steel Beam", "Elastic Beam"]
    for elTyItem in elTypeSelecList:
        elTypeSelec.addItem(elTyItem)

    if len(element[element['mat'] == int(currentMatItem)].index.to_list()) > 0:
        elTypeIndex = element[element['mat'] == int(currentMatItem)].index.to_list()[0]
        elType = element.at[elTypeIndex, "type"]

        if elType == "Macroelement3d":
            elTypeSelec.setCurrentIndex(2)
            fm.setDisabled(True)
            fy.setDisabled(True)
            fc.setDisabled(False)
            shMode.setDisabled(False)
            fvlim.setDisabled(True)
            tau0.setDisabled(False)
            Gc.setDisabled(False)
            drift_S.setDisabled(False)
            drift_F.setDisabled(False)
            if shMode.currentText() != "Turnsek & cacovic":
                mu.setDisabled(False)
            else:
                mu.setDisabled(True)
            beta.setDisabled(False)
            if not np.isnan(material.at[int(currentMatItem), "Gc"]):
                muR.setDisabled(False)
            else:
                muR.setDisabled(True)

        elif elType == "ElasticBeam":
            elTypeSelec.setCurrentIndex(1)
            fm.setDisabled(True)
            fy.setDisabled(True)
            fc.setDisabled(False)
            shMode.setDisabled(False)
            fvlim.setDisabled(True)
            tau0.setDisabled(True)
            Gc.setDisabled(True)
            drift_S.setDisabled(True)
            drift_F.setDisabled(True)
            mu.setDisabled(True)
            beta.setDisabled(True)
            if not np.isnan(material.at[int(currentMatItem), "Gc"]):
                muR.setDisabled(False)
            else:
                muR.setDisabled(True)

    elTypeSelec.currentIndexChanged.connect(lambda: elTypeChange(elTypeSelec, fm, fy, fc, shMode, fvlim, tau0, Gc, drift_S, drift_F, mu, beta, muR))
    shMode.currentIndexChanged.connect(lambda: shTypeChange(elTypeSelec, shMode, mu))
    mu.textChanged.connect(lambda: muTextChange(mu, muR))

    # Add a button
    applyMatBtn = QPushButton('Apply', widget)
    applyMatBtn.setToolTip('Click to Apply')
    applyMatBtn.clicked.connect(lambda: get_matEdEntries(matYModul, matShModul, fm, fy, fc, tau0, fvlim, matDen, shMode, Gc, drift_S, drift_F, mu, beta, muR, matEdDialog))
    applyMatBtn.resize(applyMatBtn.sizeHint())
    applyMatBtn.move(100, 80)

    cancelMatBtn = QPushButton('Cancel', widget)
    cancelMatBtn.setToolTip('Cancel Modifications')
    cancelMatBtn.clicked.connect(restDialog.close)
    cancelMatBtn.resize(cancelMatBtn.sizeHint())
    cancelMatBtn.move(100, 80)

    restDialogLayout.addWidget(matNumTtl, 1, 0)
    restDialogLayout.addWidget(matNum, 1, 1)
    restDialogLayout.addWidget(elTypeSelecTtl, 1, 6)
    restDialogLayout.addWidget(elTypeSelec, 1, 7)
    restDialogLayout.addWidget(matYModulTtl, 2, 0)
    restDialogLayout.addWidget(matYModul, 2, 1)
    restDialogLayout.addWidget(matYModulUnt, 2, 2)
    restDialogLayout.addWidget(matShModulTtl, 2, 3)
    restDialogLayout.addWidget(matShModul, 2, 4)
    restDialogLayout.addWidget(matShModulUnt, 2, 5)
    restDialogLayout.addWidget(matDenTtl, 2, 6)
    restDialogLayout.addWidget(matDen, 2, 7)
    restDialogLayout.addWidget(matDenUnt, 2, 8)
    restDialogLayout.addWidget(fmTtl, 3, 0)
    restDialogLayout.addWidget(fm, 3, 1)
    restDialogLayout.addWidget(fmUnt, 3, 2)
    restDialogLayout.addWidget(fyTtl, 3, 3)
    restDialogLayout.addWidget(fy, 3, 4)
    restDialogLayout.addWidget(fyUnt, 3, 5)
    restDialogLayout.addWidget(fcTtl, 3, 6)
    restDialogLayout.addWidget(fc, 3, 7)
    restDialogLayout.addWidget(fcUnt, 3, 8)
    restDialogLayout.addWidget(tau0Ttl, 4, 0)
    restDialogLayout.addWidget(tau0, 4, 1)
    restDialogLayout.addWidget(tau0Unt, 4, 2)
    restDialogLayout.addWidget(fvlimTtl, 4, 3)
    restDialogLayout.addWidget(fvlim, 4, 4)
    restDialogLayout.addWidget(fvlimUnt, 4, 5)
    restDialogLayout.addWidget(shModeTtl, 4, 6)
    restDialogLayout.addWidget(shMode, 4, 7)
    restDialogLayout.addWidget(GcTtl, 5, 0)
    restDialogLayout.addWidget(Gc, 5, 1)
    restDialogLayout.addWidget(drift_STtl, 5, 3)
    restDialogLayout.addWidget(drift_S, 5, 4)
    restDialogLayout.addWidget(drift_FTtl, 5, 6)
    restDialogLayout.addWidget(drift_F, 5, 7)
    restDialogLayout.addWidget(muTtl, 6, 0)
    restDialogLayout.addWidget(mu, 6, 1)
    restDialogLayout.addWidget(betaTtl, 6, 3)
    restDialogLayout.addWidget(beta, 6, 4)
    restDialogLayout.addWidget(muRTtl, 6, 6)
    restDialogLayout.addWidget(muR, 6, 7)
    restDialogLayout.addWidget(restDialogBtn, 7, 7)
    restDialogBtnLayout.addWidget(applyMatBtn, 0, 0)
    restDialogBtnLayout.addWidget(cancelMatBtn, 0, 1)

    restDialog.setLayout(restDialogLayout)
    restDialogBtn.setLayout(restDialogBtnLayout)

    if restDialog.exec_() == QtGui.QDialog.Accepted:
        restDialog.show()


def analysisDialog():
    global tmp_analysis, analysisDialog
    tmp_analysis = analysis.copy(deep=True)
    analysisDialog = QtGui.QDialog()
    analysisDialog.setWindowTitle("Define Analysis Cases")
    analysisDialogLayout = QGridLayout()
    analysisDialogBtn = QWidget()
    analysisDialogBtnLayout = QGridLayout()

    analysisList = QListWidget()
    for analysisItem in np.arange(analysis['type'].count()):
        widgetItem = QListWidgetItem()
        listWidget = QtGui.QWidget()
        if analysis["type"].iat[analysisItem] == "Dynamic":
            wTxtAnType = "Transient"
            wTxtAnSubType = " - Time History"
        elif analysis["type"].iat[analysisItem] == "selfWeight":
            wTxtAnType = "Static"
            wTxtAnSubType = " - Gravity"
        elif analysis["type"].iat[analysisItem] == "PushoverRectangular":
            wTxtAnType = "Static"
            wTxtAnSubType = " - Pushover"
        elif analysis["type"].iat[analysisItem] == "Modal":
            wTxtAnType = "Modal"
            wTxtAnSubType = ""

        widgetText = QtGui.QLabel(str(analysis.index.to_list()[analysisItem]) + '<span style="color:#A9A9A9;"> [%s</span>' % wTxtAnType + '<span style="color:#A9A9A9;"> %s]</span>' % wTxtAnSubType)
        widgetLayout = QtGui.QHBoxLayout()
        widgetLayout.addWidget(widgetText)
        widgetLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        listWidget.setLayout(widgetLayout)
        analysisList.addItem(widgetItem)
        widgetItem.setSizeHint(listWidget.sizeHint())
        analysisList.setItemWidget(widgetItem, listWidget)
    analysisList.itemSelectionChanged.connect(lambda: analysisItemActivated_event(analysisList, copyAnalysisBtn, editAnalysisBtn, deleteAnalysisBtn))

    addNewAnalysisBtn = QPushButton('Add New Analysis...', analysisDialogBtn)
    addNewAnalysisBtn.setToolTip('Define a new analysis case')
    addNewAnalysisBtn.clicked.connect(analysisEditDialog)
    addNewAnalysisBtn.resize(addNewAnalysisBtn.sizeHint())
    addNewAnalysisBtn.move(200, 80)
    addNewAnalysisBtn.setStyleSheet("padding-left: 10px; padding-right: 10px; padding-top: 5px; padding-bottom: 5px;")

    copyAnalysisBtn = QPushButton('Copy Analysis', analysisDialogBtn)
    copyAnalysisBtn.setToolTip('Copy existing analysis and create a new analysis')
    copyAnalysisBtn.clicked.connect(analysisEditDialog)
    copyAnalysisBtn.resize(copyAnalysisBtn.sizeHint())
    copyAnalysisBtn.move(200, 80)
    copyAnalysisBtn.setDisabled(True)

    editAnalysisBtn = QPushButton('Edit Analysis...', analysisDialogBtn)
    editAnalysisBtn.setToolTip('Edit existing analysis')
    editAnalysisBtn.clicked.connect(analysisEditDialog)
    editAnalysisBtn.resize(editAnalysisBtn.sizeHint())
    editAnalysisBtn.move(200, 80)
    editAnalysisBtn.setDisabled(True)

    deleteAnalysisBtn = QPushButton('Delete Analysis', analysisDialogBtn)
    deleteAnalysisBtn.setToolTip('Delete existing analysis')
    deleteAnalysisBtn.clicked.connect(analysisEditDialog)
    deleteAnalysisBtn.resize(deleteAnalysisBtn.sizeHint())
    deleteAnalysisBtn.move(200, 80)
    deleteAnalysisBtn.setDisabled(True)

    # Add a button
    applyMainAnalysisBtn = QPushButton('Apply', analysisDialogBtn)
    applyMainAnalysisBtn.setToolTip('Click to Apply')
    applyMainAnalysisBtn.clicked.connect(lambda: get_matEntries(analysisDialog))
    applyMainAnalysisBtn.resize(applyMainAnalysisBtn.sizeHint())
    applyMainAnalysisBtn.move(100, 80)

    cancelMainAnalysisBtn = QPushButton('Cancel', analysisDialogBtn)
    cancelMainAnalysisBtn.setToolTip('Cancel Modifications')
    cancelMainAnalysisBtn.clicked.connect(lambda: cancelMainMatBtnAct(analysisDialog, tmp_analysis))
    cancelMainAnalysisBtn.resize(cancelMainAnalysisBtn.sizeHint())
    cancelMainAnalysisBtn.move(100, 80)

    analysisDialogLayout.addWidget(analysisList, 1, 1, 5, 1)
    analysisDialogLayout.addWidget(addNewAnalysisBtn, 1, 3)
    analysisDialogLayout.addWidget(copyAnalysisBtn, 2, 3)
    analysisDialogLayout.addWidget(editAnalysisBtn, 3, 3)
    analysisDialogLayout.addWidget(deleteAnalysisBtn, 4, 3)
    analysisDialogLayout.addWidget(analysisDialogBtn, 6, 1, 6, 3)
    analysisDialogBtnLayout.addWidget(applyMainAnalysisBtn, 0, 0)
    analysisDialogBtnLayout.addWidget(cancelMainAnalysisBtn, 0, 1)
    analysisDialog.setLayout(analysisDialogLayout)
    analysisDialogBtn.setLayout(analysisDialogBtnLayout)
    analysisDialog.setFixedSize(400, 200)

    if analysisDialog.exec_() == QtGui.QDialog.Accepted:
        analysisDialog.show()
    return tmp_analysis, analysisDialog


def analysisEditDialog():
    global analysisTransientTypeSelec, analysisTypeSelec, analysisEdDialog, \
        analysisOptionsDTTtl, analysisOptionsDT, \
        analysisOptionsDTminTtl, analysisOptionsDTmin, analysisOptionsDTmaxTtl, analysisOptionsDTmax, \
        analysisOptionsJDTtl, analysisOptionsJD, analysisConstraintSelec, analysisOptionsEgnValTtl, \
        analysisOptionsEgnVal, analysisOptionsEgnSolvTtl, analysisOptionsEgnSolv, analysisIntegratorSelec, \
        analysisIntegratorSelec, analysisAlgorithmSelec, analysisTestSelec, testNormUnblcPFlagSelec, algoBroydenCountFlag, \
        analysisSystemSelec, analysisAlgorithmSelecTtl, RayleighFlag, analysisEdDialogLayout, txtEditorDialog, \
        GMfig, GMcanvas, pointLoadDialog
    analysisEdDialog = QtGui.QDialog()
    analysisEdDialog.setWindowTitle("Edit Analysis")
    # analysisEdDialog.setFixedSize(1100, 350)
    analysisEdDialogLayout = QGridLayout()
    analysisEdDialogBtn = QWidget()
    analysisEdDialogBtnLayout = QGridLayout()

    analysisNumTtl = QLabel("Analysis No.")
    analysisNum = QLineEdit(currentAnalysisItem)
    addWidgetFixed(analysisEdDialogLayout, 140, analysisNumTtl, 0, 0, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    analysisNumTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, analysisNum, 1, 0, 1, 1, Qt.AlignVCenter)

    # Add analysis type selection box
    analysisTypeSelecTtl = QLabel("Analysis Type")
    analysisTypeSelec = QComboBox()
    analysisTypeSelecList = ["Static", "Modal", "Transient", "Variable Transient"]
    for analysisTyItem in analysisTypeSelecList:
        analysisTypeSelec.addItem(analysisTyItem)

    if analysis.at[int(currentAnalysisItem), "type"] == "Dynamic":
        analysisTypeSelec.setCurrentIndex(2)
    elif analysis.at[int(currentAnalysisItem), "type"] == "selfWeight" or analysis.at[int(currentAnalysisItem), "type"] == "PushoverRectangular":
        analysisTypeSelec.setCurrentIndex(0)
    elif analysis.at[int(currentAnalysisItem), "type"] == "Modal":
        analysisTypeSelec.setCurrentIndex(1)
    addWidgetFixed(analysisEdDialogLayout, 140, analysisTypeSelecTtl, 0, 5, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    analysisTypeSelecTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, analysisTypeSelec, 1, 5, 1, 1, Qt.AlignVCenter)

    recordSelectBtn = QPushButton('Select Record...', widget)
    recordSelectBtn.setToolTip('Select record for time history analysis')
    txtEditorDialog = QtGui.QDialog()
    txtEditorDialog.setWindowTitle("Select ground motion file")
    recordSelectBtn.resize(recordSelectBtn.sizeHint())
    recordSelectBtn.move(100, 80)
    addWidgetFixed(analysisEdDialogLayout, 140, recordSelectBtn, 1, 4, 1, 1, Qt.AlignVCenter)

    pointLoadtBtn = QPushButton('Define Point Load...', widget)
    pointLoadtBtn.setToolTip('Define point loads for pushover analysis')
    pointLoadDialog = QtGui.QDialog()
    pointLoadDialog.setWindowTitle("Define point loads")
    pointLoadtBtn.resize(pointLoadtBtn.sizeHint())
    pointLoadtBtn.move(100, 80)
    addWidgetFixed(analysisEdDialogLayout, 140, pointLoadtBtn, 1, 4, 1, 1, Qt.AlignVCenter)

    analysisTransientTypeSelec = QComboBox()
    analysisTransientTypeSelecList = ["Select analysis sub-type", "Gravity", "Pushover", "Time history", "Modal"]
    for analysisTransientTypeItem in analysisTransientTypeSelecList:
        analysisTransientTypeSelec.addItem(analysisTransientTypeItem)
    addWidgetFixed(analysisEdDialogLayout, 140, analysisTransientTypeSelec, 1, 6, 1, 1, Qt.AlignCenter | Qt.AlignCenter)
    if analysis.at[int(currentAnalysisItem), "type"] == "PushoverRectangular":
        analysisTransientTypeSelec.setCurrentIndex(2)
    separator1 = QFrame(); separator1.setFrameShape(QFrame.HLine)
    analysisEdDialogLayout.addWidget(separator1, 2, 0, 1, 7, QtCore.Qt.AlignTop)

    analysisOptionsDTTtl = QLabel("Time-Step Increment (dt)")
    if not np.isnan(analysis.at[int(currentAnalysisItem), "dt"]):
        analysisOptionsDT = QLineEdit(str(analysis.at[int(currentAnalysisItem), "dt"]))
    else:
        analysisOptionsDT = QLineEdit()
    analysisOptionsEgnValTtl = QLabel("No. of Eigenvalues")
    if not np.isnan(analysis.at[int(currentAnalysisItem), "nModes"]):
        analysisOptionsEgnVal = QLineEdit(str(analysis.at[int(currentAnalysisItem), "nModes"]))
    else:
        analysisOptionsEgnVal = QLineEdit()
    analysisOptionsEgnSolvTtl = QLabel("Eigenvalue Solver")
    analysisOptionsEgnSolv = QComboBox()
    analysisEigenSolverList = ["genBandArpack", "symmBandLapack", "FullGenLapack"]
    for analysisEigenSolverItem in analysisEigenSolverList:
        analysisOptionsEgnSolv.addItem(analysisEigenSolverItem)
    analysisOptionsEgnSolv.setCurrentIndex(0)
    addWidgetFixed(analysisEdDialogLayout, 140, analysisOptionsDTTtl, 3, 0, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    analysisOptionsDTTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, analysisOptionsDT, 4, 0, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, analysisOptionsEgnValTtl, 3, 0, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    analysisOptionsEgnValTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, analysisOptionsEgnVal, 4, 0, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, analysisOptionsEgnSolvTtl, 3, 1, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    analysisOptionsEgnSolvTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, analysisOptionsEgnSolv, 4, 1, 1, 1, Qt.AlignVCenter)

    analysisOptionsGravAccXttl = QLabel("Acceleration (X direction)")
    analysisOptionsGravAccYttl = QLabel("Acceleration (Y direction)")
    analysisOptionsGravAccZttl = QLabel("Acceleration (Z direction)")
    if analysis.at[int(currentAnalysisItem), "type"] == "selfWeight":
        analysisOptionsGravAccX = QLineEdit(str(analysis.at[int(currentAnalysisItem), "accVec1"]))
        analysisOptionsGravAccY = QLineEdit(str(analysis.at[int(currentAnalysisItem), "accVec2"]))
        analysisOptionsGravAccZ = QLineEdit(str(analysis.at[int(currentAnalysisItem), "accVec3"]))
    else:
        analysisOptionsGravAccX = QLineEdit(str(0))
        analysisOptionsGravAccY = QLineEdit(str(0))
        analysisOptionsGravAccZ = QLineEdit(str(-9.8))
    addWidgetFixed(analysisEdDialogLayout, 140, analysisOptionsGravAccXttl, 3, 0, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    analysisOptionsGravAccXttl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, analysisOptionsGravAccX, 4, 0, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, analysisOptionsGravAccYttl, 3, 1, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    analysisOptionsGravAccYttl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, analysisOptionsGravAccY, 4, 1, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, analysisOptionsGravAccZttl, 3, 2, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    analysisOptionsGravAccZttl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, analysisOptionsGravAccZ, 4, 2, 1, 1, Qt.AlignVCenter)

    analysisOptionsPushDirTtl = QLabel("Pushover Direction")
    analysisOptionsPushDirSelec = QComboBox()
    analysisOptionsPushDirList = ["Select Pushover Direction", "X", "Y", "Z"]
    for analysisOptionsPushDirItem in analysisOptionsPushDirList:
        analysisOptionsPushDirSelec.addItem(analysisOptionsPushDirItem)
    if analysis.at[int(currentAnalysisItem), "DOF"] == "ux":
        analysisOptionsPushDirSelec.setCurrentIndex(1)
    elif analysis.at[int(currentAnalysisItem), "DOF"] == "uy":
        analysisOptionsPushDirSelec.setCurrentIndex(2)
    elif analysis.at[int(currentAnalysisItem), "DOF"] == "uz":
        analysisOptionsPushDirSelec.setCurrentIndex(3)
    else:
        analysisOptionsPushDirSelec.setCurrentIndex(0)
    analysisOptionsPushMaxDispTtl = QLabel("Maximum Displacement")
    if not np.isnan(analysis.at[int(currentAnalysisItem), "maxDisp"]):
        analysisOptionsPushMaxDisp =QLineEdit(str(analysis.at[int(currentAnalysisItem), "maxDisp"]))
    else:
        analysisOptionsPushMaxDisp = QLineEdit()
    analysisOptionsGravMaxDispTtl = QLabel("Maximum Displacement")
    if not np.isnan(analysis.at[int(currentAnalysisItem), "maxDisp"]):
        analysisOptionsGravMaxDisp = QLineEdit(str(analysis.at[int(currentAnalysisItem), "maxDisp"]))
    else:
        analysisOptionsGravMaxDisp = QLineEdit()
    addWidgetFixed(analysisEdDialogLayout, 140, analysisOptionsPushDirTtl, 3, 0, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    analysisOptionsPushDirTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, analysisOptionsPushDirSelec, 4, 0, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, analysisOptionsPushMaxDispTtl, 3, 1, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    analysisOptionsPushMaxDispTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, analysisOptionsPushMaxDisp, 4, 1, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, analysisOptionsGravMaxDispTtl, 3, 3, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    analysisOptionsGravMaxDispTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, analysisOptionsGravMaxDisp, 4, 3, 1, 1, Qt.AlignVCenter)

    analysisOptionsDTminTtl = QLabel("Minimum Time-Step (dtMin)")
    analysisOptionsDTmin = QLineEdit()
    analysisOptionsDTmaxTtl = QLabel("Maximum Time-Step (dtMax)")
    analysisOptionsDTmax = QLineEdit()
    analysisOptionsJDTtl = QLabel("No. of Itrs. at each Step (Jd)")
    analysisOptionsJD = QLineEdit()
    addWidgetFixed(analysisEdDialogLayout, 140, analysisOptionsDTminTtl, 3, 1, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    analysisOptionsDTminTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, analysisOptionsDTmin, 4, 1, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, analysisOptionsDTmaxTtl, 3, 2, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    analysisOptionsDTmaxTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, analysisOptionsDTmax, 4, 2, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, analysisOptionsJDTtl, 3, 3, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    analysisOptionsJDTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, analysisOptionsJD, 4, 3, 1, 1, Qt.AlignVCenter)
    separator2 = QFrame(); separator2.setFrameShape(QFrame.HLine)
    analysisEdDialogLayout.addWidget(separator2, 5, 0, 1, 7, QtCore.Qt.AlignTop)

    analysisSystemSelecTtl = QLabel("System of Equations")
    analysisSystemSelec = QComboBox()
    analysisSystemSelecList = ["Band General", "Band SPD", "Profile SPD", "SuperLU (SparseGEN)", "UmfPack",
                               "Full General", "Sparse SYM", "CuSP"]
    for analysisSystemItem in analysisSystemSelecList:
        analysisSystemSelec.addItem(analysisSystemItem)

    addWidgetFixed(analysisEdDialogLayout, 140, analysisSystemSelecTtl, 6, 0, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    analysisSystemSelecTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, analysisSystemSelec, 7, 0, 1, 1, Qt.AlignVCenter)

    analysisNumbererSelecTtl = QLabel("DOF Numberer")
    analysisNumbererSelec = QComboBox()
    analysisNumbererSelecList = ["Plain", "Reverse Cuthill-McKee (RCM)", "Alternative Minimum Degree (AMD)"]
    for analysisNumbererItem in analysisNumbererSelecList:
        analysisNumbererSelec.addItem(analysisNumbererItem)
    analysisNumbererSelec.setCurrentIndex(1)
    addWidgetFixed(analysisEdDialogLayout, 140, analysisNumbererSelecTtl, 6, 1, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    analysisNumbererSelecTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, analysisNumbererSelec, 7, 1, 1, 1, Qt.AlignVCenter)

    analysisConstraintSelecTtl = QLabel("Constraints")
    analysisConstraintSelec = QComboBox()
    analysisConstraintList = ["Plain", "Lagrange", "Penalty", "Transformation"]
    for analysisConstraintItem in analysisConstraintList:
        analysisConstraintSelec.addItem(analysisConstraintItem)
    if analysis.at[int(currentAnalysisItem), "type"] == "PushoverRectangular":
        analysisConstraintSelec.setCurrentIndex(0)
    else:
        analysisConstraintSelec.setCurrentIndex(3)
    constraintAlphasTtl = QLabel("\u03B1S Factor on Single Points")
    constraintAlphamTtl = QLabel("\u03B1M Factor on Multiple Points")
    constraintAlphas = QLineEdit()
    constraintAlpham = QLineEdit()

    addWidgetFixed(analysisEdDialogLayout, 140, analysisConstraintSelecTtl, 6, 2, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    analysisConstraintSelecTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, analysisConstraintSelec, 7, 2, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, constraintAlphasTtl, 6, 3, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    constraintAlphasTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, constraintAlphas, 7, 3, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, constraintAlphamTtl, 6, 4, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    constraintAlphamTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, constraintAlpham, 7, 4, 1, 1, Qt.AlignVCenter)

    constraintTypeChange(False, constraintAlphas, constraintAlpham)
    analysisConstraintSelec.currentIndexChanged.connect(lambda: constraintTypeChange(True, constraintAlphas, constraintAlpham))

    analysisIntegratorSelecTtl = QLabel("Integrator")
    analysisIntegratorSelec = QComboBox()
    analysisIntegratorSelecList = ["Load Control", "Displacement Control", "Minimum Unbalanced Displacement Norm",
                                   "Arc Length", "Central Difference", "Newmark", "Hibler-Hughes-Taylor",
                                   "Generalized Alpha", "TRBDF2", "Explicit Difference"]
    for analysisIntegratorSelecItem in analysisIntegratorSelecList:
        analysisIntegratorSelec.addItem(analysisIntegratorSelecItem)
    addWidgetFixed(analysisEdDialogLayout, 140, analysisIntegratorSelecTtl, 8, 0, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    analysisIntegratorSelecTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, analysisIntegratorSelec, 9, 0, 1, 1, Qt.AlignVCenter)
    integratorLClambdaTtl = QLabel("Load Factor (\u03BB)")
    integratorLClambda = QLineEdit()
    integratorLCNumIterTtl = QLabel("Number of Iterations")
    if not np.isnan(analysis.at[int(currentAnalysisItem), "nSteps"]) and analysisTransientTypeSelec.currentText() == "Gravity":
        integratorLCNumIter = QLineEdit(str(analysis.at[int(currentAnalysisItem), "nSteps"]))
    else:
        integratorLCNumIter = QLineEdit(str(1))
    integratorLClambdaminTtl = QLabel("Minimum Load Factor (\u03BBmin)")
    integratorLClambdamin = QLineEdit(integratorLClambda.text())
    integratorLClambdamaxTtl = QLabel("Maximum Load Factor (\u03BBmax)")
    integratorLClambdamax = QLineEdit(integratorLClambda.text())
    addWidgetFixed(analysisEdDialogLayout, 140, integratorLClambdaTtl, 8, 1, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    integratorLClambdaTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, integratorLClambda, 9, 1, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, integratorLCNumIterTtl, 8, 2, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    integratorLCNumIterTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, integratorLCNumIter, 9, 2, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, integratorLClambdaminTtl, 8, 3, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    integratorLClambdaminTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, integratorLClambdamin, 9, 3, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, integratorLClambdamaxTtl, 8, 4, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    integratorLClambdamaxTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, integratorLClambdamax, 9, 4, 1, 1, Qt.AlignVCenter)
    integratorLClambda.textChanged.connect(lambda: integratorDefaults().LCLoadFacts(integratorLClambda, integratorLClambdamin, integratorLClambdamax))

    integratorDCnodeTtl = QLabel("Monitored Node")
    if not np.isnan(analysis.at[int(currentAnalysisItem), "controlNode"]):
        integratorDCnode = QLineEdit(str(analysis.at[int(currentAnalysisItem), "controlNode"]))
    else:
        integratorDCnode = QLineEdit()
    integratorDCdofTtl = QLabel("Monitored DOF")
    integratorDCdofSelec = QComboBox()
    integratorDCdofList = ["Select Monitored DOF", "X", "Y", "Z"]
    for integratorDCdofItem in integratorDCdofList:
        integratorDCdofSelec.addItem(integratorDCdofItem)
    if analysis.at[int(currentAnalysisItem), "DOF"] == "ux":
        integratorDCdofSelec.setCurrentIndex(1)
    elif analysis.at[int(currentAnalysisItem), "DOF"] == "uy":
        integratorDCdofSelec.setCurrentIndex(2)
    elif analysis.at[int(currentAnalysisItem), "DOF"] == "uz":
        integratorDCdofSelec.setCurrentIndex(3)
    else:
        integratorDCdofSelec.setCurrentIndex(0)
    integratorDCincrTtl = QLabel("Initial Displacement Increment")
    integratorDCincr = QLineEdit()
    integratorDCnumItrTtl = QLabel("Number of Iteration")
    integratorDCnumItr = QLineEdit(str(1))
    integratorDCdeltaUminTtl = QLabel("Minimum Displacement Step")
    integratorDCdeltaUmin = QLineEdit(integratorDCincr.text())
    integratorDCdeltaUmaxTtl = QLabel("Maximum Displacement Step")
    integratorDCdeltaUmax = QLineEdit(integratorDCincr.text())
    addWidgetFixed(analysisEdDialogLayout, 140, integratorDCnodeTtl, 8, 1, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    integratorDCnodeTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, integratorDCnode, 9, 1, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, integratorDCdofTtl, 8, 2, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    integratorDCdofTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, integratorDCdofSelec, 9, 2, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, integratorDCincrTtl, 8, 3, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    integratorDCincrTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, integratorDCincr, 9, 3, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, integratorDCnumItrTtl, 8, 4, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    integratorDCnumItrTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, integratorDCnumItr, 9, 4, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, integratorDCdeltaUminTtl, 8, 5, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    integratorDCdeltaUminTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, integratorDCdeltaUmin, 9, 5, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, integratorDCdeltaUmaxTtl, 8, 6, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    integratorDCdeltaUmaxTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, integratorDCdeltaUmax, 9, 6, 1, 1, Qt.AlignVCenter)
    integratorDCincr.textChanged.connect(lambda: integratorDefaults().DCincr(integratorDCincr, integratorDCdeltaUmin, integratorDCdeltaUmax))

    integratorMUDNdLambda1Ttl = QLabel("Initial Load Increment")
    integratorMUDNdLambda1 = QLineEdit()
    integratorMUDNJdTtl = QLabel("Jd factor")
    integratorMUDNJd = QLineEdit(str(1.0))
    integratorMUDNdminLambdaTtl = QLabel("Minimum Load Increment")
    integratorMUDNdminLambda = QLineEdit(integratorMUDNdLambda1.text())
    integratorMUDNdmaxLambdaTtl = QLabel("Maximum Load Increment")
    integratorMUDNdmaxLambda = QLineEdit(integratorMUDNdLambda1.text())
    addWidgetFixed(analysisEdDialogLayout, 140, integratorMUDNdLambda1Ttl, 8, 1, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    integratorMUDNdLambda1Ttl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, integratorMUDNdLambda1, 9, 1, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, integratorMUDNJdTtl, 8, 2, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    integratorMUDNJdTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, integratorMUDNJd, 9, 2, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, integratorMUDNdminLambdaTtl, 8, 3, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    integratorMUDNdminLambdaTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, integratorMUDNdminLambda, 9, 3, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, integratorMUDNdmaxLambdaTtl, 8, 4, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    integratorMUDNdmaxLambdaTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, integratorMUDNdmaxLambda, 9, 4, 1, 1, Qt.AlignVCenter)
    integratorMUDNdLambda1.textChanged.connect(lambda: integratorDefaults().MUDNlambda(integratorMUDNdLambda1, integratorMUDNdminLambda, integratorMUDNdmaxLambda))

    integratorALsTtl = QLabel("Arc Lenth (s)")
    integratorALs = QLineEdit()
    integratorALalphaTtl = QLabel("Reference Load Scale Factor (\u03B1)")
    integratorALalpha = QLineEdit()
    addWidgetFixed(analysisEdDialogLayout, 140, integratorALsTtl, 8, 1, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    integratorALsTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, integratorALs, 9, 1, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, integratorALalphaTtl, 8, 2, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    integratorALalphaTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, integratorALalpha, 9, 2, 1, 1, Qt.AlignVCenter)

    integratorNewmarkGammaTtl = QLabel("\u03B3 factor")
    integratorNewmarkGamma = QLineEdit()
    integratorNewmarkBetaTtl = QLabel("\u03B2 factor")
    integratorNewmarkBeta = QLineEdit()
    addWidgetFixed(analysisEdDialogLayout, 140, integratorNewmarkGammaTtl, 8, 1, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    integratorNewmarkGammaTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, integratorNewmarkGamma, 9, 1, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, integratorNewmarkBetaTtl, 8, 2, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    integratorNewmarkBetaTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, integratorNewmarkBeta, 9, 2, 1, 1, Qt.AlignVCenter)

    integratorHHTAlphaTtl = QLabel("\u03B1 factor")
    integratorHHTAlpha = QLineEdit()
    integratorHHTGammaTtl = QLabel("\u03B3 factor")
    if integratorHHTAlpha.text() == "":
        integratorHHTGamma = QLineEdit("")
    else:
        integratorHHTGamma = QLineEdit(str(3/2 - float(integratorHHTAlpha.text())))
    integratorHHTBetaTtl = QLabel("\u03B2 factor")
    if integratorHHTAlpha.text() == "":
        integratorHHTBeta = QLineEdit("")
    else:
        integratorHHTBeta = QLineEdit(str(((2 - float(integratorHHTAlpha.text())) ** 2) / 4))
    addWidgetFixed(analysisEdDialogLayout, 140, integratorHHTAlphaTtl, 8, 1, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    integratorHHTAlphaTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, integratorHHTAlpha, 9, 1, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, integratorHHTGammaTtl, 8, 2, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    integratorHHTGammaTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, integratorHHTGamma, 9, 2, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, integratorHHTBetaTtl, 8, 3, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    integratorHHTBetaTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, integratorHHTBeta, 9, 3, 1, 1, Qt.AlignVCenter)
    integratorHHTAlpha.textChanged.connect(lambda: integratorDefaults().HHTAlpha(integratorHHTAlpha, integratorHHTGamma,integratorHHTBeta))

    integratorGENalphAlphamTtl = QLabel("\u03B1M factor")
    integratorGENalphAlpham = QLineEdit()
    integratorGENalphAlphafTtl = QLabel("\u03B1F factor")
    integratorGENalphAlphaf = QLineEdit()
    integratorGENalphGammaTtl = QLabel("\u03B3 factor")
    if integratorGENalphAlpham.text() == "" or integratorGENalphAlphaf.text() == "":
        integratorGENalphGamma = QLineEdit("")
    else:
        integratorGENalphGamma = QLineEdit(str(1/2 + float(integratorGENalphAlpham.text()) - float(integratorGENalphAlphaf.text())))
    integratorGENalphBetaTtl = QLabel("\u03B2 factor")
    if integratorGENalphAlpham.text() == "" or integratorGENalphAlphaf.text() == "":
        integratorGENalphBeta = QLineEdit("")
    else:
        integratorGENalphBeta = QLineEdit(str(1/4 * (1 + float(integratorGENalphAlpham.text()) - float(integratorGENalphAlphaf.text())) ** 2))
    addWidgetFixed(analysisEdDialogLayout, 140, integratorGENalphAlphamTtl, 8, 1, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    integratorGENalphAlphamTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, integratorGENalphAlpham, 9, 1, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, integratorGENalphAlphafTtl, 8, 2, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    integratorGENalphAlphafTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, integratorGENalphAlphaf, 9, 2, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, integratorGENalphGammaTtl, 8, 3, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    integratorGENalphGammaTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, integratorGENalphGamma, 9, 3, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, integratorGENalphBetaTtl, 8, 4, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    integratorGENalphBetaTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, integratorGENalphBeta, 9, 4, 1, 1, Qt.AlignVCenter)

    integratorTypeChange(False, integratorLClambdaTtl, integratorLClambda, integratorLCNumIterTtl, integratorLCNumIter,
                         integratorLClambdaminTtl, integratorLClambdamin, integratorLClambdamaxTtl,
                         integratorLClambdamax, integratorDCnodeTtl, integratorDCnode, integratorDCdofTtl,
                         integratorDCdofSelec, integratorDCincrTtl, integratorDCincr, integratorDCnumItrTtl,
                         integratorDCnumItr, integratorDCdeltaUminTtl, integratorDCdeltaUmin, integratorDCdeltaUmaxTtl,
                         integratorDCdeltaUmax, integratorMUDNdLambda1Ttl, integratorMUDNdLambda1, integratorMUDNJdTtl,
                         integratorMUDNJd, integratorMUDNdminLambdaTtl, integratorMUDNdminLambda,
                         integratorMUDNdmaxLambdaTtl, integratorMUDNdmaxLambda, integratorALsTtl,
                         integratorALs, integratorALalphaTtl, integratorALalpha, integratorNewmarkGammaTtl,
                         integratorNewmarkGamma, integratorNewmarkBetaTtl, integratorNewmarkBeta,
                         integratorHHTAlphaTtl, integratorHHTAlpha, integratorHHTGammaTtl, integratorHHTGamma,
                         integratorGENalphAlphamTtl, integratorGENalphAlpham, integratorGENalphAlphafTtl,
                         integratorGENalphAlphaf, integratorGENalphGammaTtl, integratorGENalphGamma,
                         integratorGENalphBetaTtl, integratorGENalphBeta, integratorHHTBetaTtl, integratorHHTBeta,
                         analysisOptionsPushMaxDispTtl, analysisOptionsPushMaxDisp, analysisOptionsGravMaxDispTtl,
                         analysisOptionsGravMaxDisp, analysisTransientTypeSelec)
    analysisIntegratorSelec.currentIndexChanged.connect(
        lambda: integratorTypeChange(True, integratorLClambdaTtl, integratorLClambda, integratorLCNumIterTtl,
                                     integratorLCNumIter, integratorLClambdaminTtl, integratorLClambdamin,
                                     integratorLClambdamaxTtl, integratorLClambdamax, integratorDCnodeTtl,
                                     integratorDCnode, integratorDCdofTtl, integratorDCdofSelec, integratorDCincrTtl,
                                     integratorDCincr, integratorDCnumItrTtl, integratorDCnumItr,
                                     integratorDCdeltaUminTtl, integratorDCdeltaUmin, integratorDCdeltaUmaxTtl,
                                     integratorDCdeltaUmax, integratorMUDNdLambda1Ttl, integratorMUDNdLambda1,
                                     integratorMUDNJdTtl, integratorMUDNJd, integratorMUDNdminLambdaTtl,
                                     integratorMUDNdminLambda, integratorMUDNdmaxLambdaTtl, integratorMUDNdmaxLambda,
                                     integratorALsTtl, integratorALs, integratorALalphaTtl, integratorALalpha,
                                     integratorNewmarkGammaTtl, integratorNewmarkGamma, integratorNewmarkBetaTtl,
                                     integratorNewmarkBeta, integratorHHTAlphaTtl, integratorHHTAlpha,
                                     integratorHHTGammaTtl, integratorHHTGamma, integratorGENalphAlphamTtl,
                                     integratorGENalphAlpham, integratorGENalphAlphafTtl, integratorGENalphAlphaf,
                                     integratorGENalphGammaTtl, integratorGENalphGamma, integratorGENalphBetaTtl,
                                     integratorGENalphBeta, integratorHHTBetaTtl, integratorHHTBeta,
                                     analysisOptionsPushMaxDispTtl, analysisOptionsPushMaxDisp,
                                     analysisOptionsGravMaxDispTtl, analysisOptionsGravMaxDisp, analysisTransientTypeSelec))

    analysisAlgorithmSelecTtl = QLabel("Solution Algorithm")
    analysisAlgorithmSelec = QComboBox()
    analysisAlgorithmList = ["Linear", "Newton", "Newton with Line Search", "Modified Newton", "Krylov-Newton", "Secant Newton", "BFGS", "Broyden"]
    for analysisAlgorithmItem in analysisAlgorithmList:
        analysisAlgorithmSelec.addItem(analysisAlgorithmItem)
    analysisAlgorithmSelec.setCurrentIndex(1)
    addWidgetFixed(analysisEdDialogLayout, 140, analysisAlgorithmSelecTtl, 10, 0, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    analysisAlgorithmSelecTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, analysisAlgorithmSelec, 11, 0, 1, 1, Qt.AlignVCenter)

    algoLinSecantFlag = QCheckBox("Use Secant Stiffness")
    algoLinSecantFlag.setChecked(False)
    algoLinInitialFlag = QCheckBox("Use Initial Stiffness")
    algoLinInitialFlag.setChecked(False)
    algoLinFactorOnceFlag = QCheckBox("Setup and Factor Matrix Once")
    algoLinFactorOnceFlag.setChecked(False)
    addWidgetFixed(analysisEdDialogLayout, 140, algoLinSecantFlag, 11, 1, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, algoLinInitialFlag, 11, 2, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, algoLinFactorOnceFlag, 11, 3, 1, 1, Qt.AlignVCenter)

    algoNewInitialFlag = QCheckBox("Use Initial Stiffness")
    algoNewInitialFlag.setChecked(False)
    algoNewInitThenCurrentFlag = QCheckBox("Init. Stiff. for 1st Step + Curr. Stiff. for Subsequent Steps")
    algoNewInitThenCurrentFlag.setChecked(False)
    addWidgetFixed(analysisEdDialogLayout, 140, algoNewInitialFlag, 11, 1, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, algoNewInitThenCurrentFlag, 11, 2, 1, 1, Qt.AlignVCenter)

    algoNewWlineTypeSearchSelecTtl = QLabel("Line Search Algorithm")
    algoNewWlineTypeSearchSelec = QComboBox()
    algoNewWlineTypeSearchSelecList = ["Bisection", "Secant", "RegulaFalsi", "InitialInterpolated"]
    for algoNewWlineTypeSearchSelecItem in algoNewWlineTypeSearchSelecList:
        algoNewWlineTypeSearchSelec.addItem(algoNewWlineTypeSearchSelecItem)
    algoNewWlineTypeSearchSelec.setCurrentIndex(3)
    algoNewWlineTolTtl = QLabel("Tolerance for Search")
    if not np.isnan(analysis.at[int(currentAnalysisItem), "tol"]):
        algoNewWlineTol = QLineEdit(str(analysis.at[int(currentAnalysisItem), "tol"]))
    else:
        algoNewWlineTol = QLineEdit(str(0.8))
    algoNewWlineMaxItrTtl = QLabel("Maximum Number of Iterations")
    algoNewWlineMaxItr = QLineEdit(str(10))
    algoNewWlineMinEtaTtl = QLabel("Minimum \u03B7 value")
    algoNewWlineMinEta = QLineEdit(str(0.1))
    algoNewWlineMaxEtaTtl = QLabel("Maximum \u03B7 value")
    algoNewWlineMaxEta = QLineEdit(str(10))
    addWidgetFixed(analysisEdDialogLayout, 140, algoNewWlineTypeSearchSelecTtl, 10, 1, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    algoNewWlineTypeSearchSelecTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, algoNewWlineTypeSearchSelec, 11, 1, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, algoNewWlineTolTtl, 10, 2, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    algoNewWlineTolTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, algoNewWlineTol, 11, 2, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, algoNewWlineMaxItrTtl, 10, 3, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    algoNewWlineMaxItrTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, algoNewWlineMaxItr, 11, 3, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, algoNewWlineMinEtaTtl, 10, 4, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    algoNewWlineMinEtaTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, algoNewWlineMinEta, 11, 4, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, algoNewWlineMaxEtaTtl, 10, 5, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    algoNewWlineMaxEtaTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, algoNewWlineMaxEta, 11, 5, 1, 1, Qt.AlignVCenter)

    algoModNewInitialFlag = QCheckBox("Use Initial Stiffness")
    algoModNewInitialFlag.setChecked(False)
    addWidgetFixed(analysisEdDialogLayout, 140, algoModNewInitialFlag, 11, 1, 1, 1, Qt.AlignVCenter)

    algoKryNewTangItrSelecTtl = QLabel("Tangent to Iterate on")
    algoKryNewTangItrSelec = QComboBox()
    algoKryNewTangItrList = ["Current", "Initial", "No Tangent"]
    for algoKryNewTangItrItem in algoKryNewTangItrList:
        algoKryNewTangItrSelec.addItem(algoKryNewTangItrItem)
    algoKryNewTangItrSelec.setCurrentIndex(0)
    algoKryNewTangIncrSelecTtl = QLabel("Tangent to Iterate on")
    algoKryNewTangIncrSelec = QComboBox()
    algoKryNewTangIncrList = ["Current", "Initial", "No Tangent"]
    for algoKryNewTangIncrItem in algoKryNewTangIncrList:
        algoKryNewTangIncrSelec.addItem(algoKryNewTangIncrItem)
    algoKryNewTangIncrSelec.setCurrentIndex(0)
    algoKryNewMaxDimTtl = QLabel("Maximum Iterations till Tangent Reformation")
    algoKryNewMaxDim = QLineEdit(str(3))
    addWidgetFixed(analysisEdDialogLayout, 140, algoKryNewTangItrSelecTtl, 10, 1, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    algoKryNewTangItrSelecTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, algoKryNewTangItrSelec, 11, 1, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, algoKryNewTangIncrSelecTtl, 10, 2, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    algoKryNewTangIncrSelecTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, algoKryNewTangIncrSelec, 11, 2, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, algoKryNewMaxDimTtl, 10, 3, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    algoKryNewMaxDimTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, algoKryNewMaxDim, 11, 3, 1, 1, Qt.AlignVCenter)

    algoSecNewTangItrSelecTtl = QLabel("Tangent to Iterate on")
    algoSecNewTangItrSelec = QComboBox()
    algoSecNewTangItrList = ["Current", "Initial", "No Tangent"]
    for algoSecNewTangItrItem in algoSecNewTangItrList:
        algoSecNewTangItrSelec.addItem(algoSecNewTangItrItem)
    algoSecNewTangItrSelec.setCurrentIndex(0)
    algoSecNewTangIncrSelecTtl = QLabel("Tangent to Iterate on")
    algoSecNewTangIncrSelec = QComboBox()
    algoSecNewTangIncrList = ["Current", "Initial", "No Tangent"]
    for algoSecNewTangIncrItem in algoSecNewTangIncrList:
        algoSecNewTangIncrSelec.addItem(algoSecNewTangIncrItem)
    algoSecNewTangIncrSelec.setCurrentIndex(0)
    algoSecNewMaxDimTtl = QLabel("Max. Itrs. till Tangent Reformation")
    algoSecNewMaxDim = QLineEdit(str(3))
    addWidgetFixed(analysisEdDialogLayout, 140, algoSecNewTangItrSelecTtl, 10, 1, 1, 1, Qt.AlignVCenter)
    algoSecNewTangItrSelecTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, algoSecNewTangItrSelec, 11, 1, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, algoSecNewTangIncrSelecTtl, 10, 2, 1, 1, Qt.AlignVCenter)
    algoSecNewTangIncrSelecTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, algoSecNewTangIncrSelec, 11, 2, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, algoSecNewMaxDimTtl, 10, 3, 1, 1, Qt.AlignVCenter)
    algoSecNewMaxDimTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, algoSecNewMaxDim, 11, 3, 1, 1, Qt.AlignVCenter)

    algoBroydenCountFlag = QCheckBox("No. of Itrs. till a New Tangent is Reformed")
    algoBroydenCountFlag.setChecked(False)
    algoBroydenCountFlagValue = QLineEdit()
    addWidgetFixed(analysisEdDialogLayout, 140, algoBroydenCountFlag, 11, 1, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, algoBroydenCountFlagValue, 11, 2, 1, 1, Qt.AlignVCenter)

    broydenCheckChange(True, algoBroydenCountFlagValue)
    algoBroydenCountFlag.stateChanged.connect(lambda: broydenCheckChange(True, algoBroydenCountFlagValue))

    algorithmTypeChange(False, algoLinSecantFlag, algoLinInitialFlag, algoLinFactorOnceFlag,
                        algoNewInitialFlag, algoNewInitThenCurrentFlag, algoNewWlineTypeSearchSelecTtl,
                        algoNewWlineTypeSearchSelec, algoNewWlineTolTtl, algoNewWlineTol, algoNewWlineMaxItrTtl,
                        algoNewWlineMaxItr, algoNewWlineMinEtaTtl, algoNewWlineMinEta, algoNewWlineMaxEtaTtl,
                        algoNewWlineMaxEta, algoModNewInitialFlag, algoKryNewTangItrSelecTtl, algoKryNewTangItrSelec,
                        algoKryNewTangIncrSelecTtl, algoKryNewTangIncrSelec, algoKryNewMaxDimTtl, algoKryNewMaxDim,
                        algoSecNewTangItrSelecTtl, algoSecNewTangItrSelec, algoSecNewTangIncrSelecTtl,
                        algoSecNewTangIncrSelec, algoSecNewMaxDimTtl, algoSecNewMaxDim, algoBroydenCountFlag, algoBroydenCountFlagValue)
    analysisAlgorithmSelec.currentIndexChanged.connect(
        lambda: algorithmTypeChange(True, algoLinSecantFlag, algoLinInitialFlag, algoLinFactorOnceFlag,
                                    algoNewInitialFlag, algoNewInitThenCurrentFlag, algoNewWlineTypeSearchSelecTtl,
                                    algoNewWlineTypeSearchSelec, algoNewWlineTolTtl, algoNewWlineTol,
                                    algoNewWlineMaxItrTtl, algoNewWlineMaxItr, algoNewWlineMinEtaTtl,
                                    algoNewWlineMinEta, algoNewWlineMaxEtaTtl, algoNewWlineMaxEta,
                                    algoModNewInitialFlag, algoKryNewTangItrSelecTtl, algoKryNewTangItrSelec,
                                    algoKryNewTangIncrSelecTtl, algoKryNewTangIncrSelec, algoKryNewMaxDimTtl,
                                    algoKryNewMaxDim, algoSecNewTangItrSelecTtl, algoSecNewTangItrSelec,
                                    algoSecNewTangIncrSelecTtl, algoSecNewTangIncrSelec, algoSecNewMaxDimTtl,
                                    algoSecNewMaxDim, algoBroydenCountFlag, algoBroydenCountFlagValue))

    analysisTestSelecTtl = QLabel("Convergence Test")
    analysisTestSelec = QComboBox()
    analysisTestList = ["Norm Unbalance", "Norm Displacement Increment", "Energy Increment", "Relative Norm Unbalance",
                        "Relative Norm Displacement Increment", "Total Relative Norm Displacement Increment",
                        "Relative Energy Increment", "Fixed Number of Iterations"]
    for analysisTestItem in analysisTestList:
        analysisTestSelec.addItem(analysisTestItem)
    analysisTestSelec.setCurrentIndex(0)
    testNormUnblcItrTtl = QLabel("Maximum Number of Iterations")
    if not np.isnan(analysis.at[int(currentAnalysisItem), "maxStep"]):
        testNormUnblcItr = QLineEdit(str(analysis.at[int(currentAnalysisItem), "maxStep"]))
    else:
        testNormUnblcItr = QLineEdit(str(1))
    testNormUnblcPFlagSelecTtl = QLabel("Print")
    testNormUnblcPFlagSelec = QComboBox()
    testNormUnblcPFlagList = ["Nothing", "Information on Norms on test() invoke",
                              "Information on norm and number of iterations at the end",
                              "Norms and \u0394U and R(U) at each step",
                              "An error if failed to converge but return successful test"]
    for testNormUnblcPFlagItem in testNormUnblcPFlagList:
        testNormUnblcPFlagSelec.addItem(testNormUnblcPFlagItem)
    testNormUnblcPFlagSelec.setCurrentIndex(0)
    testNormUnblcNtypeTtl = QLabel("Type of Norm (0 = max-norm, 1 = 1-norm, ...)")
    testNormUnblcNType = QLineEdit(str(2))
    testNormUnblcTolTtl = QLabel("Convergence Tolerance")
    if not np.isnan(analysis.at[int(currentAnalysisItem), "tol"]):
        testNormUnblcTol = QLineEdit(str(analysis.at[int(currentAnalysisItem), "tol"]))
    else:
        testNormUnblcTol = QLineEdit()
    addWidgetFixed(analysisEdDialogLayout, 140, analysisTestSelecTtl, 12, 0, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    analysisTestSelecTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, analysisTestSelec, 13, 0, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, testNormUnblcItrTtl, 12, 1, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    testNormUnblcItrTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, testNormUnblcItr, 13, 1, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, testNormUnblcPFlagSelecTtl, 12, 2, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    testNormUnblcPFlagSelecTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, testNormUnblcPFlagSelec, 13, 2, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, testNormUnblcNtypeTtl, 12, 3, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    testNormUnblcNtypeTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, testNormUnblcNType, 13, 3, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, testNormUnblcTolTtl, 12, 4, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    testNormUnblcTolTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, testNormUnblcTol, 13, 4, 1, 1, Qt.AlignVCenter)

    RayleighFlag = QCheckBox("Rayleigh Damping")
    RayleighFlag.setChecked(True)
    RayleighAlphaMTtl = QLabel("\u03B1M")
    RayleighAlphaM = QLineEdit(str(analysis.at[int(currentAnalysisItem), "rayleigh1"]))
    RayleighBetaKTtl = QLabel("\u03B2K")
    RayleighBetaK = QLineEdit(str(analysis.at[int(currentAnalysisItem), "rayleigh2"]))
    RayleighBetaKinitTtl = QLabel("\u03B2K (initial)")
    RayleighBetaKinit = QLineEdit(str(analysis.at[int(currentAnalysisItem), "rayleigh2"]))
    RayleighBetaKcmmtTtl = QLabel("\u03B2K (commit)")
    RayleighBetaKcmmt = QLineEdit(str(analysis.at[int(currentAnalysisItem), "rayleigh2"]))
    rayleighCheckChange(True, RayleighAlphaMTtl, RayleighAlphaM, RayleighBetaKTtl, RayleighBetaK, RayleighBetaKinitTtl,
                        RayleighBetaKinit, RayleighBetaKcmmtTtl, RayleighBetaKcmmt)
    RayleighFlag.stateChanged.connect(lambda: rayleighCheckChange(True, RayleighAlphaMTtl, RayleighAlphaM,
                        RayleighBetaKTtl, RayleighBetaK, RayleighBetaKinitTtl,
                        RayleighBetaKinit, RayleighBetaKcmmtTtl, RayleighBetaKcmmt))

    addWidgetFixed(analysisEdDialogLayout, 140, RayleighFlag, 15, 0, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, RayleighAlphaMTtl, 14, 1, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    RayleighAlphaMTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, RayleighAlphaM, 15, 1, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, RayleighBetaKTtl, 14, 2, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    RayleighBetaKTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, RayleighBetaK, 15, 2, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, RayleighBetaKinitTtl, 14, 3, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    RayleighBetaKinitTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, RayleighBetaKinit, 15, 3, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, RayleighBetaKcmmtTtl, 14, 4, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    RayleighBetaKcmmtTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, RayleighBetaKcmmt, 15, 4, 1, 1, Qt.AlignVCenter)

    rcrTimeStepTtl = QLabel("Record Time Step")
    rcrTimeStep = QLineEdit()
    rcrDirTtl = QLabel("Ground Motion Direction")
    rcrDir = QComboBox()
    rcrDirList = ["Select GM direction", "X", "Y", "Z"]
    for rcrDirItem in rcrDirList:
        rcrDir.addItem(rcrDirItem)
    sclFctrTtl = QLabel("Scale Factor")
    sclFctr = QLineEdit()
    sclMotionGFlag = QCheckBox("Consider g in scaling")
    sclMotionGFlag.setChecked(True)
    frVbrDurTtl = QLabel("Free Vibration Duration")
    frVbrDur = QLineEdit(str(0))

    addWidgetFixed(analysisEdDialogLayout, 140, rcrTimeStepTtl, 16, 0, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    rcrTimeStepTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, rcrTimeStep, 17, 0, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, rcrDirTtl, 16, 1, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    rcrDirTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, rcrDir, 17, 1, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, sclFctrTtl, 16, 2, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    sclFctrTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, sclFctr, 17, 2, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, sclMotionGFlag, 17, 3, 1, 1, Qt.AlignVCenter)
    addWidgetFixed(analysisEdDialogLayout, 140, frVbrDurTtl, 16, 4, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
    frVbrDurTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
    addWidgetFixed(analysisEdDialogLayout, 140, frVbrDur, 17, 4, 1, 1, Qt.AlignVCenter)
    tmp_analysis = pd.DataFrame(
        columns=['analysisNumber', 'type', 'sub type', 'record', 'analysis number of increments', 'analysis dt',
                 'analysis dt min', 'analysis dt max', 'Jd', 'eigen nModes', 'eigen solver', 'system of equations',
                 'DOF numberer', 'constraint type', 'constraint alpha S', 'constraint alpha M', 'integrator type',
                 'integrator LC lambda', 'integrator LC lambda min', 'integrator LC lambda max',
                 'integrator LC number of iterations', 'integrator DC control node', 'integrator DC control DOF',
                 'integrator DC increment', 'integrator DC increment min', 'integrator DC increment max',
                 'integrator DC number of iterations', 'integrator MUDN lambda1', 'integrator MUDN lambda min',
                 'integrator MUDN lambda max', 'integrator MUDN JD', 'integrator ArcLength S',
                 'integrator ArcLength alpha', 'integrator Newmark Gamma', 'integrator Newmark Beta',
                 'integrator HHT Alpha', 'integrator HHT Gamma', 'integrator HHT Beta',
                 'integrator genaralized alpha AlphaM', 'integrator genaralized alpha AlphaF',
                 'integrator genaralized alpha Gamma', 'integrator genaralized alpha Beta', 'algorithm type',
                 'algorithm linear Secant', 'algorithm linear Initial Tangent', 'algorithm linear factor once',
                 'algorithm Newton Initial Tangent', 'algorithm Newton Initial Tangent then current',
                 'algorithm Newton line search type', 'algorithm Newton line search tolerance',
                 'algorithm Newton line search max iteration', 'algorithm Newton line search min ETA',
                 'algorithm Newton line search max ETA', 'algorithm modified Newton initial stiffness',
                 'algorithm Krylov Newton tangent iteration type', 'algorithm Krylov Newton tangent increment type',
                 'algorithm Krylov Newton max no. of iterations untill tangent reformed',
                 'algorithm secant Newton tangent to iterate on', 'algorithm secant Newton tangent to increment on',
                 'algorithm secant Newton max no. of iterations untill tangent reformed', 'algorithm Broyden count',
                 'test type', 'test norm unbalanced number of iterations', 'test norm unbalanced tolerance',
                 'test norm unbalanced print flag', 'test norm unbalanced type of norm', 'Rayleigh check',
                 'Rayleigh alpha M', 'Rayleigh beta K', 'Rayleigh beta K initial', 'Rayleigh beta K commit',
                 'record time step', 'record direction', 'record scale factor', 'record free vibration duration'],
        index=np.arange(totalAnalysis))
    GMfig = plt.figure()
    GMcanvas = FigureCanvas(GMfig)
    # addWidgetFixed(analysisEdDialogLayout, 140, GMcanvas, 18, 0, 1, 6, Qt.AlignVCenter)
    analysisEdDialogLayout.addWidget(GMcanvas, 18, 0, 1, 7, Qt.AlignVCenter)

    rcrTimeStep.textChanged.connect(lambda: updPlt(sclFctr, sclMotionGFlag, rcrTimeStep, frVbrDur, GMfig, GMcanvas))
    sclFctr.textChanged.connect(lambda: updPlt(sclFctr, sclMotionGFlag, rcrTimeStep, frVbrDur, GMfig, GMcanvas))
    sclMotionGFlag.stateChanged.connect(lambda: updPlt(sclFctr, sclMotionGFlag, rcrTimeStep, frVbrDur, GMfig, GMcanvas))
    frVbrDur.textChanged.connect(lambda: updPlt(sclFctr, sclMotionGFlag, rcrTimeStep, frVbrDur, GMfig, GMcanvas))



    recordSelectBtn.clicked.connect(lambda: getGMrecord(rcrTimeStepTtl, rcrTimeStep, rcrDirTtl, rcrDir, frVbrDurTtl,
                                                        frVbrDur, sclFctrTtl, sclFctr, sclMotionGFlag))
    pointLoadtBtn.clicked.connect(lambda: dataTable(800, 500, 7))

    analysisTypeChange(False, integratorLClambdaTtl, integratorLClambda, integratorLCNumIterTtl, integratorLCNumIter,
                       integratorLClambdaminTtl, integratorLClambdamin, integratorLClambdamaxTtl,
                       integratorLClambdamax, integratorDCnodeTtl, integratorDCnode, integratorDCdofTtl,
                       integratorDCdofSelec, integratorDCincrTtl, integratorDCincr, integratorDCnumItrTtl,
                       integratorDCnumItr, integratorDCdeltaUminTtl, integratorDCdeltaUmin, integratorDCdeltaUmaxTtl,
                       integratorDCdeltaUmax, integratorMUDNdLambda1Ttl, integratorMUDNdLambda1, integratorMUDNJdTtl,
                       integratorMUDNJd, integratorMUDNdminLambdaTtl, integratorMUDNdminLambda,
                       integratorMUDNdmaxLambdaTtl, integratorMUDNdmaxLambda, integratorALsTtl,
                       integratorALs, integratorALalphaTtl, integratorALalpha, integratorNewmarkGammaTtl,
                       integratorNewmarkGamma, integratorNewmarkBetaTtl, integratorNewmarkBeta,
                       integratorHHTAlphaTtl, integratorHHTAlpha, integratorHHTGammaTtl, integratorHHTGamma,
                       integratorGENalphAlphamTtl, integratorGENalphAlpham, integratorGENalphAlphafTtl,
                       integratorGENalphAlphaf, integratorGENalphGammaTtl, integratorGENalphGamma,
                       integratorGENalphBetaTtl, integratorGENalphBeta, integratorHHTBetaTtl, integratorHHTBeta,
                       algoLinSecantFlag, algoLinInitialFlag, algoLinFactorOnceFlag,
                       algoNewInitialFlag, algoNewInitThenCurrentFlag, algoNewWlineTypeSearchSelecTtl,
                       algoNewWlineTypeSearchSelec, algoNewWlineTolTtl, algoNewWlineTol, algoNewWlineMaxItrTtl,
                       algoNewWlineMaxItr, algoNewWlineMinEtaTtl, algoNewWlineMinEta, algoNewWlineMaxEtaTtl,
                       algoNewWlineMaxEta, algoModNewInitialFlag, algoKryNewTangItrSelecTtl, algoKryNewTangItrSelec,
                       algoKryNewTangIncrSelecTtl, algoKryNewTangIncrSelec, algoKryNewMaxDimTtl, algoKryNewMaxDim,
                       algoSecNewTangItrSelecTtl, algoSecNewTangItrSelec, algoSecNewTangIncrSelecTtl,
                       algoSecNewTangIncrSelec, algoSecNewMaxDimTtl, algoSecNewMaxDim, algoBroydenCountFlag,
                       algoBroydenCountFlagValue, testNormUnblcTolTtl, testNormUnblcTol, testNormUnblcPFlagSelec,
                       testNormUnblcNtypeTtl, testNormUnblcNType, analysisTestSelec, analysisTestSelecTtl,
                       testNormUnblcItrTtl, testNormUnblcItr, RayleighAlphaMTtl, RayleighAlphaM, RayleighBetaKTtl,
                       RayleighBetaK, RayleighBetaKinitTtl, RayleighBetaKinit, RayleighBetaKcmmtTtl, RayleighBetaKcmmt,
                       recordSelectBtn, rcrTimeStepTtl, rcrTimeStep, rcrDirTtl, rcrDir, frVbrDurTtl, frVbrDur,
                       sclFctrTtl, sclFctr, sclMotionGFlag, pointLoadtBtn)
    analysisTypeSelec.currentIndexChanged.connect(lambda: analysisTypeChange(True, integratorLClambdaTtl,
                        integratorLClambda, integratorLCNumIterTtl, integratorLCNumIter, integratorLClambdaminTtl,
                        integratorLClambdamin, integratorLClambdamaxTtl, integratorLClambdamax, integratorDCnodeTtl,
                        integratorDCnode, integratorDCdofTtl, integratorDCdofSelec, integratorDCincrTtl,
                        integratorDCincr, integratorDCnumItrTtl, integratorDCnumItr, integratorDCdeltaUminTtl,
                        integratorDCdeltaUmin, integratorDCdeltaUmaxTtl, integratorDCdeltaUmax, integratorMUDNdLambda1Ttl,
                        integratorMUDNdLambda1, integratorMUDNJdTtl, integratorMUDNJd, integratorMUDNdminLambdaTtl,
                        integratorMUDNdminLambda, integratorMUDNdmaxLambdaTtl, integratorMUDNdmaxLambda, integratorALsTtl,
                        integratorALs, integratorALalphaTtl, integratorALalpha, integratorNewmarkGammaTtl, integratorNewmarkGamma,
                        integratorNewmarkBetaTtl, integratorNewmarkBeta, integratorHHTAlphaTtl, integratorHHTAlpha,
                        integratorHHTGammaTtl, integratorHHTGamma, integratorGENalphAlphamTtl, integratorGENalphAlpham,
                        integratorGENalphAlphafTtl, integratorGENalphAlphaf, integratorGENalphGammaTtl, integratorGENalphGamma,
                        integratorGENalphBetaTtl, integratorGENalphBeta, integratorHHTBetaTtl, integratorHHTBeta,
                        algoLinSecantFlag, algoLinInitialFlag, algoLinFactorOnceFlag, algoNewInitialFlag, algoNewInitThenCurrentFlag,
                        algoNewWlineTypeSearchSelecTtl, algoNewWlineTypeSearchSelec, algoNewWlineTolTtl, algoNewWlineTol,
                        algoNewWlineMaxItrTtl, algoNewWlineMaxItr, algoNewWlineMinEtaTtl, algoNewWlineMinEta, algoNewWlineMaxEtaTtl,
                        algoNewWlineMaxEta, algoModNewInitialFlag, algoKryNewTangItrSelecTtl, algoKryNewTangItrSelec,
                        algoKryNewTangIncrSelecTtl, algoKryNewTangIncrSelec, algoKryNewMaxDimTtl, algoKryNewMaxDim,
                        algoSecNewTangItrSelecTtl, algoSecNewTangItrSelec, algoSecNewTangIncrSelecTtl, algoSecNewTangIncrSelec,
                        algoSecNewMaxDimTtl, algoSecNewMaxDim, algoBroydenCountFlag, algoBroydenCountFlagValue,
                        testNormUnblcTolTtl, testNormUnblcTol, testNormUnblcPFlagSelec, testNormUnblcNtypeTtl, testNormUnblcNType,
                        analysisTestSelec, analysisTestSelecTtl, testNormUnblcItrTtl, testNormUnblcItr,
                        RayleighAlphaMTtl, RayleighAlphaM, RayleighBetaKTtl, RayleighBetaK, RayleighBetaKinitTtl,
                        RayleighBetaKinit, RayleighBetaKcmmtTtl, RayleighBetaKcmmt, recordSelectBtn, rcrTimeStepTtl,
                        rcrTimeStep, rcrDirTtl, rcrDir, frVbrDurTtl, frVbrDur, sclFctrTtl, sclFctr, sclMotionGFlag, pointLoadtBtn))

    analysisSubTypeChange(analysisTransientTypeSelec, analysisOptionsGravAccXttl, analysisOptionsGravAccYttl,
                          analysisOptionsGravAccZttl, analysisOptionsGravAccX, analysisOptionsGravAccY,
                          analysisOptionsGravAccZ, analysisOptionsPushDirTtl, analysisOptionsPushDirSelec,
                          analysisOptionsGravMaxDispTtl, analysisOptionsGravMaxDisp, analysisOptionsPushMaxDispTtl,
                          analysisOptionsPushMaxDisp)
    analysisTransientTypeSelec.currentIndexChanged.connect(lambda: analysisSubTypeChange(analysisTransientTypeSelec,
                        analysisOptionsGravAccXttl, analysisOptionsGravAccYttl, analysisOptionsGravAccZttl,
                        analysisOptionsGravAccX, analysisOptionsGravAccY, analysisOptionsGravAccZ,
                        analysisOptionsPushDirTtl, analysisOptionsPushDirSelec, analysisOptionsGravMaxDispTtl,
                        analysisOptionsGravMaxDisp, analysisOptionsPushMaxDispTtl, analysisOptionsPushMaxDisp))

    testTypeChange(False, testNormUnblcTolTtl, testNormUnblcTol, testNormUnblcPFlagSelec)
    analysisTestSelec.currentIndexChanged.connect(lambda: testTypeChange(True, testNormUnblcTolTtl, testNormUnblcTol, testNormUnblcPFlagSelec))

    for row in np.arange(16):
        analysisEdDialogLayout.setRowStretch(row, 1)
    for column in np.arange(7):
        analysisEdDialogLayout.setColumnStretch(column, 1)
    analysisEdDialog.setLayout(analysisEdDialogLayout)

    # Add a button
    applyAnalysisBtn = QPushButton('Apply', widget)
    applyAnalysisBtn.setToolTip('Click to Apply')
    applyAnalysisBtn.clicked.connect(lambda: get_analysisEdEntries(True))
    applyAnalysisBtn.resize(applyAnalysisBtn.sizeHint())
    applyAnalysisBtn.move(100, 80)

    cancelAnalysisBtn = QPushButton('Cancel', widget)
    cancelAnalysisBtn.setToolTip('Cancel Modifications')
    cancelAnalysisBtn.clicked.connect(analysisEdDialog.close)
    cancelAnalysisBtn.resize(cancelAnalysisBtn.sizeHint())
    cancelAnalysisBtn.move(100, 80)

    # analysisEdDialogLayout.addWidget(analysisEdDialogBtn, 8, 8)
    analysisEdDialogBtnLayout.addWidget(applyAnalysisBtn, 0, 0)
    analysisEdDialogBtnLayout.addWidget(cancelAnalysisBtn, 0, 1)
    analysisEdDialogBtn.setLayout(analysisEdDialogBtnLayout)
    analysisEdDialogLayout.addWidget(analysisEdDialogBtn, 20, 2, 4, 3, Qt.AlignVCenter)

    if analysisEdDialog.exec_() == QtGui.QDialog.Accepted:
        analysisEdDialog.show()

    return analysisTransientTypeSelec, analysisTypeSelec, analysisEdDialog, \
           analysisOptionsDTTtl, analysisOptionsDT, \
           analysisOptionsDTminTtl, analysisOptionsDTmin, analysisOptionsDTmaxTtl, analysisOptionsDTmax, \
           analysisOptionsJDTtl, analysisOptionsJD, analysisConstraintSelec, analysisOptionsEgnValTtl, \
           analysisOptionsEgnVal, analysisOptionsEgnSolvTtl, analysisOptionsEgnSolv, analysisIntegratorSelec, \
           analysisIntegratorSelec, analysisAlgorithmSelec, analysisTestSelec, testNormUnblcPFlagSelec, algoBroydenCountFlag, \
           analysisSystemSelec, analysisAlgorithmSelecTtl, RayleighFlag, analysisEdDialogLayout, txtEditorDialog, \
           GMfig, GMcanvas, pointLoadDialog


def analysisTypeChange(changState, f_integratorLClambdaTtl, f_integratorLClambda, f_integratorLCNumIterTtl,
                         f_integratorLCNumIter, f_integratorLClambdaminTtl, f_integratorLClambdamin,
                         f_integratorLClambdamaxTtl, f_integratorLClambdamax, f_integratorDCnodeTtl, f_integratorDCnode,
                         f_integratorDCdofTtl, f_integratorDCdof, f_integratorDCincrTtl, f_integratorDCincr,
                         f_integratorDCnumItrTtl, f_integratorDCnumItr, f_integratorDCdeltaUminTtl,
                         f_integratorDCdeltaUmin, f_integratorDCdeltaUmaxTtl, f_integratorDCdeltaUmax,
                         f_integratorMUDNdLambda1Ttl, f_integratorMUDNdLambda1, f_integratorMUDNJdTtl,
                         f_integratorMUDNJd, f_integratorMUDNdminLambdaTtl, f_integratorMUDNdminLambda,
                         f_integratorMUDNdmaxLambdaTtl, f_integratorMUDNdmaxLambda, f_integratorALsTtl, f_integratorALs,
                         f_integratorALalphaTtl, f_integratorALalpha, f_integratorNewmarkGammaTtl, f_integratorNewmarkGamma,
                         f_integratorNewmarkBetaTtl, f_integratorNewmarkBeta, f_integratorHHTAlphaTtl, f_integratorHHTAlpha,
                         f_integratorHHTGammaTtl, f_integratorHHTGamma, integratorGENalphAlphamTtl, integratorGENalphAlpham, integratorGENalphAlphafTtl,
                         integratorGENalphAlphaf, integratorGENalphGammaTtl, integratorGENalphGamma,
                         integratorGENalphBetaTtl, integratorGENalphBeta, f_integratorHHTBetaTtl, f_integratorHHTBeta,
                       f_algoLinSecantFlag, f_algoLinInitialFlag, f_algoLinFactorOnceFlag,
                       f_algoNewInitialFlag, f_algoNewInitThenCurrentFlag, f_algoNewWlineTypeSearchSelecTtl,
                       f_algoNewWlineTypeSearchSelec, f_algoNewWlineTolTtl, f_algoNewWlineTol, f_algoNewWlineMaxItrTtl,
                       f_algoNewWlineMaxItr, f_algoNewWlineMinEtaTtl, f_algoNewWlineMinEta, f_algoNewWlineMaxEtaTtl,
                       f_algoNewWlineMaxEta, f_algoModNewInitialFlag, f_algoKryNewTangItrSelecTtl,
                       f_algoKryNewTangItrSelec, f_algoKryNewTangIncrSelecTtl, f_algoKryNewTangIncrSelec, f_algoKryNewMaxDimTtl,
                       f_algoKryNewMaxDim,f_algoSecNewTangItrSelecTtl, f_algoSecNewTangItrSelec, f_algoSecNewTangIncrSelecTtl,
                       f_algoSecNewTangIncrSelec, f_algoSecNewMaxDimTtl, f_algoSecNewMaxDim, f_algoBroydenCountFlag,
                       f_algoBroydenCountFlagValue, f_testNormUnblcTolTtl, f_testNormUnblcTol, f_testNormUnblcPFlagSelec,
                       f_testNormUnblcNtypeTtl, f_testNormUnblcNType, f_analysisTestSelec, f_analysisTestSelecTtl,
                       f_testNormUnblcItrTtl, f_testNormUnblcItr, f_RayleighAlphaMTtl, f_RayleighAlphaM,
                       f_RayleighBetaKTtl, f_RayleighBetaK, f_RayleighBetaKinitTtl, f_RayleighBetaKinit, f_RayleighBetaKcmmtTtl,
                       f_RayleighBetaKcmmt, f_recordSelectBtn, f_rcrTimeStepTtl, f_rcrTimeStep, f_rcrDirTtl, f_rcrDir,
                       f_frVbrDurTtl, f_frVbrDur, f_sclFctrTtl, f_sclFctr, f_sclMotionGFlag, f_pointLoadtBtn):
    f_rcrTimeStepTtl.setDisabled(True); f_rcrTimeStep.setDisabled(True); f_rcrDirTtl.setDisabled(True)
    f_rcrDir.setDisabled(True); f_frVbrDurTtl.setDisabled(True); f_frVbrDur.setDisabled(True)
    f_sclFctrTtl.setDisabled(True); f_sclFctr.setDisabled(True); f_sclMotionGFlag.setDisabled(True)
    if analysisTypeSelec.currentText() == "Static":
        analysisTransientTypeSelec.setDisabled(False)
        analysisTransientTypeSelec.model().item(1).setEnabled(True)
        analysisTransientTypeSelec.model().item(2).setEnabled(True)
        analysisTransientTypeSelec.model().item(3).setEnabled(False)
        analysisTransientTypeSelec.model().item(4).setEnabled(False)
        analysisTransientTypeSelec.setCurrentIndex(1)

        analysisOptionsDTTtl.hide(); analysisOptionsDT.hide()
        analysisOptionsDTminTtl.hide(); analysisOptionsDTmin.hide(); analysisOptionsDTmaxTtl.hide()
        analysisOptionsDTmax.hide(); analysisOptionsJDTtl.hide(); analysisOptionsJD.hide()
        analysisOptionsEgnValTtl.hide(); analysisOptionsEgnVal.hide(); analysisOptionsEgnSolvTtl.hide()
        analysisOptionsEgnSolv.hide()

        analysisIntegratorSelec.setDisabled(False)  # Integrator options
        analysisIntegratorSelec.model().item(0).setEnabled(True); analysisIntegratorSelec.model().item(1).setEnabled(True)
        analysisIntegratorSelec.model().item(2).setEnabled(True); analysisIntegratorSelec.model().item(3).setEnabled(True)
        analysisIntegratorSelec.model().item(4).setEnabled(False); analysisIntegratorSelec.model().item(5).setEnabled(False)
        analysisIntegratorSelec.model().item(6).setEnabled(False); analysisIntegratorSelec.model().item(7).setEnabled(False)
        analysisIntegratorSelec.model().item(8).setEnabled(False); analysisIntegratorSelec.model().item(9).setEnabled(False)
        if analysisTransientTypeSelec.currentText() == "Gravity":
            analysisIntegratorSelec.setCurrentIndex(0)
        elif analysisTransientTypeSelec.currentText() == "Pushover":
            analysisIntegratorSelec.setCurrentIndex(1)

        analysisSystemSelec.setCurrentIndex(0)

        f_integratorLClambdaTtl.setDisabled(False); f_integratorLClambda.setDisabled(False); f_integratorLCNumIterTtl.setDisabled(False)
        f_integratorLCNumIter.setDisabled(False); f_integratorLClambdaminTtl.setDisabled(False); f_integratorLClambdamin.setDisabled(False)
        f_integratorLClambdamaxTtl.setDisabled(False); f_integratorLClambdamax.setDisabled(False)
        f_integratorDCnodeTtl.setDisabled(False); f_integratorDCnode.setDisabled(False)
        f_integratorDCdofTtl.setDisabled(False); f_integratorDCdof.setDisabled(False); f_integratorDCincrTtl.setDisabled(False)
        f_integratorDCincr.setDisabled(False); f_integratorDCnumItrTtl.setDisabled(False); f_integratorDCnumItr.setDisabled(False)
        f_integratorDCdeltaUminTtl.setDisabled(False); f_integratorDCdeltaUmin.setDisabled(False)
        f_integratorDCdeltaUmaxTtl.setDisabled(False); f_integratorDCdeltaUmax.setDisabled(False); f_integratorMUDNdLambda1Ttl.setDisabled(False)
        f_integratorMUDNdLambda1.setDisabled(False); f_integratorMUDNJdTtl.setDisabled(False); f_integratorMUDNJd.setDisabled(False)
        f_integratorMUDNdminLambdaTtl.setDisabled(False); f_integratorMUDNdminLambda.setDisabled(False); f_integratorMUDNdmaxLambdaTtl.setDisabled(False)
        f_integratorMUDNdmaxLambda.setDisabled(False); f_integratorALsTtl.setDisabled(False); f_integratorALs.setDisabled(False)
        f_integratorALalphaTtl.setDisabled(False); f_integratorALalpha.setDisabled(False); f_integratorNewmarkGammaTtl.setDisabled(False)
        f_integratorNewmarkGamma.setDisabled(False); f_integratorNewmarkBetaTtl.setDisabled(False); f_integratorNewmarkBeta.setDisabled(False)
        f_integratorHHTAlphaTtl.setDisabled(False); f_integratorHHTAlpha.setDisabled(False); f_integratorHHTGammaTtl.setDisabled(False)
        f_integratorHHTGamma.setDisabled(False); integratorGENalphAlphamTtl.setDisabled(False); integratorGENalphAlpham.setDisabled(False)
        integratorGENalphAlphafTtl.setDisabled(False); integratorGENalphAlphaf.setDisabled(False); integratorGENalphGammaTtl.setDisabled(False)
        integratorGENalphGamma.setDisabled(False); integratorGENalphBetaTtl.setDisabled(False); integratorGENalphBeta.setDisabled(False)
        f_integratorHHTBetaTtl.setDisabled(False); f_integratorHHTBeta.setDisabled(False)
        f_algoLinSecantFlag.setDisabled(False); f_algoLinInitialFlag.setDisabled(False); f_algoLinFactorOnceFlag.setDisabled(False)
        f_algoNewInitialFlag.setDisabled(False); f_algoNewInitThenCurrentFlag.setDisabled(False); f_algoNewWlineTypeSearchSelecTtl.setDisabled(False)
        f_algoNewWlineTypeSearchSelec.setDisabled(False); f_algoNewWlineTolTtl.setDisabled(False); f_algoNewWlineTol.setDisabled(False)
        f_algoNewWlineMaxItrTtl.setDisabled(False); f_algoNewWlineMaxItr.setDisabled(False); f_algoNewWlineMinEtaTtl.setDisabled(False)
        f_algoNewWlineMinEta.setDisabled(False); f_algoNewWlineMaxEtaTtl.setDisabled(False); f_algoNewWlineMaxEta.setDisabled(False)
        f_algoModNewInitialFlag.setDisabled(False); f_algoKryNewTangItrSelecTtl.setDisabled(False); f_algoKryNewTangItrSelec.setDisabled(False)
        f_algoKryNewTangIncrSelecTtl.setDisabled(False); f_algoKryNewTangIncrSelec.setDisabled(False); f_algoKryNewMaxDimTtl.setDisabled(False)
        f_algoKryNewMaxDim.setDisabled(False); f_algoSecNewTangItrSelecTtl.setDisabled(False); f_algoSecNewTangItrSelec.setDisabled(False)
        f_algoSecNewTangIncrSelecTtl.setDisabled(False); f_algoSecNewTangIncrSelec.setDisabled(False); f_algoSecNewMaxDimTtl.setDisabled(False)
        f_algoSecNewMaxDim.setDisabled(False); f_algoBroydenCountFlag.setDisabled(False); f_algoBroydenCountFlagValue.setDisabled(False)
        analysisAlgorithmSelecTtl.setDisabled(False); analysisAlgorithmSelec.setDisabled(False)
        f_testNormUnblcTolTtl.setDisabled(False); f_testNormUnblcTol.setDisabled(False); f_testNormUnblcPFlagSelec.setDisabled(False)
        f_testNormUnblcNtypeTtl.setDisabled(False); f_testNormUnblcNType.setDisabled(False)
        f_analysisTestSelec.setDisabled(False); f_analysisTestSelecTtl.setDisabled(False); f_testNormUnblcItrTtl.setDisabled(False)
        f_testNormUnblcItr.setDisabled(False)
        f_recordSelectBtn.setDisabled(True); f_pointLoadtBtn.setDisabled(False); f_recordSelectBtn.hide(); f_pointLoadtBtn.show()
        RayleighFlag.setDisabled(True)
        rayleighCheckChange(False, f_RayleighAlphaMTtl, f_RayleighAlphaM, f_RayleighBetaKTtl, f_RayleighBetaK, f_RayleighBetaKinitTtl,
                        f_RayleighBetaKinit, f_RayleighBetaKcmmtTtl, f_RayleighBetaKcmmt)
    elif (analysisTypeSelec.currentText() == "Transient") or (analysisTypeSelec.currentText() == "Variable Transient"):
        analysisTransientTypeSelec.setDisabled(False)
        analysisTransientTypeSelec.model().item(1).setEnabled(False)
        analysisTransientTypeSelec.model().item(2).setEnabled(False)
        analysisTransientTypeSelec.model().item(3).setEnabled(True)
        analysisTransientTypeSelec.model().item(4).setEnabled(False)
        analysisTransientTypeSelec.setCurrentIndex(3)

        analysisOptionsDTTtl.show(); analysisOptionsDT.show()
        analysisOptionsDTminTtl.hide(); analysisOptionsDTmin.hide(); analysisOptionsDTmaxTtl.hide()
        analysisOptionsDTmax.hide(); analysisOptionsJDTtl.hide(); analysisOptionsJD.hide()
        analysisOptionsEgnValTtl.hide(); analysisOptionsEgnVal.hide(); analysisOptionsEgnSolvTtl.hide()
        analysisOptionsEgnSolv.hide()

        analysisIntegratorSelec.setDisabled(False)  # Integrator options
        analysisIntegratorSelec.model().item(0).setEnabled(False); analysisIntegratorSelec.model().item(1).setEnabled(False)
        analysisIntegratorSelec.model().item(2).setEnabled(False); analysisIntegratorSelec.model().item(3).setEnabled(False)
        analysisIntegratorSelec.model().item(4).setEnabled(True); analysisIntegratorSelec.model().item(5).setEnabled(True)
        analysisIntegratorSelec.model().item(6).setEnabled(True); analysisIntegratorSelec.model().item(7).setEnabled(True)
        analysisIntegratorSelec.model().item(8).setEnabled(True); analysisIntegratorSelec.model().item(9).setEnabled(True)
        analysisIntegratorSelec.setCurrentIndex(5)

        analysisSystemSelec.setCurrentIndex(3)

        f_integratorLClambdaTtl.setDisabled(False); f_integratorLClambda.setDisabled(False); f_integratorLCNumIterTtl.setDisabled(False)
        f_integratorLCNumIter.setDisabled(False); f_integratorLClambdaminTtl.setDisabled(False); f_integratorLClambdamin.setDisabled(False)
        f_integratorLClambdamaxTtl.setDisabled(False); f_integratorLClambdamax.setDisabled(False)
        f_integratorDCnodeTtl.setDisabled(False); f_integratorDCnode.setDisabled(False)
        f_integratorDCdofTtl.setDisabled(False); f_integratorDCdof.setDisabled(False); f_integratorDCincrTtl.setDisabled(False)
        f_integratorDCincr.setDisabled(False); f_integratorDCnumItrTtl.setDisabled(False); f_integratorDCnumItr.setDisabled(False)
        f_integratorDCdeltaUminTtl.setDisabled(False); f_integratorDCdeltaUmin.setDisabled(False)
        f_integratorDCdeltaUmaxTtl.setDisabled(False); f_integratorDCdeltaUmax.setDisabled(False); f_integratorMUDNdLambda1Ttl.setDisabled(False)
        f_integratorMUDNdLambda1.setDisabled(False); f_integratorMUDNJdTtl.setDisabled(False); f_integratorMUDNJd.setDisabled(False)
        f_integratorMUDNdminLambdaTtl.setDisabled(False); f_integratorMUDNdminLambda.setDisabled(False); f_integratorMUDNdmaxLambdaTtl.setDisabled(False)
        f_integratorMUDNdmaxLambda.setDisabled(False); f_integratorALsTtl.setDisabled(False); f_integratorALs.setDisabled(False)
        f_integratorALalphaTtl.setDisabled(False); f_integratorALalpha.setDisabled(False); f_integratorNewmarkGammaTtl.setDisabled(False)
        f_integratorNewmarkGamma.setDisabled(False); f_integratorNewmarkBetaTtl.setDisabled(False); f_integratorNewmarkBeta.setDisabled(False)
        f_integratorHHTAlphaTtl.setDisabled(False); f_integratorHHTAlpha.setDisabled(False); f_integratorHHTGammaTtl.setDisabled(False)
        f_integratorHHTGamma.setDisabled(False); integratorGENalphAlphamTtl.setDisabled(False); integratorGENalphAlpham.setDisabled(False)
        integratorGENalphAlphafTtl.setDisabled(False); integratorGENalphAlphaf.setDisabled(False); integratorGENalphGammaTtl.setDisabled(False)
        integratorGENalphGamma.setDisabled(False); integratorGENalphBetaTtl.setDisabled(False); integratorGENalphBeta.setDisabled(False)
        f_integratorHHTBetaTtl.setDisabled(False); f_integratorHHTBeta.setDisabled(False)
        f_algoLinSecantFlag.setDisabled(False); f_algoLinInitialFlag.setDisabled(False); f_algoLinFactorOnceFlag.setDisabled(False)
        f_algoNewInitialFlag.setDisabled(False); f_algoNewInitThenCurrentFlag.setDisabled(False); f_algoNewWlineTypeSearchSelecTtl.setDisabled(False)
        f_algoNewWlineTypeSearchSelec.setDisabled(False); f_algoNewWlineTolTtl.setDisabled(False); f_algoNewWlineTol.setDisabled(False)
        f_algoNewWlineMaxItrTtl.setDisabled(False); f_algoNewWlineMaxItr.setDisabled(False); f_algoNewWlineMinEtaTtl.setDisabled(False)
        f_algoNewWlineMinEta.setDisabled(False); f_algoNewWlineMaxEtaTtl.setDisabled(False); f_algoNewWlineMaxEta.setDisabled(False)
        f_algoModNewInitialFlag.setDisabled(False); f_algoKryNewTangItrSelecTtl.setDisabled(False); f_algoKryNewTangItrSelec.setDisabled(False)
        f_algoKryNewTangIncrSelecTtl.setDisabled(False); f_algoKryNewTangIncrSelec.setDisabled(False); f_algoKryNewMaxDimTtl.setDisabled(False)
        f_algoKryNewMaxDim.setDisabled(False); f_algoSecNewTangItrSelecTtl.setDisabled(False); f_algoSecNewTangItrSelec.setDisabled(False)
        f_algoSecNewTangIncrSelecTtl.setDisabled(False); f_algoSecNewTangIncrSelec.setDisabled(False); f_algoSecNewMaxDimTtl.setDisabled(False)
        f_algoSecNewMaxDim.setDisabled(False); f_algoBroydenCountFlag.setDisabled(False); f_algoBroydenCountFlagValue.setDisabled(False)
        analysisAlgorithmSelecTtl.setDisabled(False); analysisAlgorithmSelec.setDisabled(False)
        f_testNormUnblcTolTtl.setDisabled(False); f_testNormUnblcTol.setDisabled(False); f_testNormUnblcPFlagSelec.setDisabled(False)
        f_testNormUnblcNtypeTtl.setDisabled(False); f_testNormUnblcNType.setDisabled(False)
        f_analysisTestSelec.setDisabled(False); f_analysisTestSelecTtl.setDisabled(False); f_testNormUnblcItrTtl.setDisabled(False)
        f_testNormUnblcItr.setDisabled(False)
        f_recordSelectBtn.setDisabled(False); f_pointLoadtBtn.setDisabled(True); f_recordSelectBtn.show(); f_pointLoadtBtn.hide()
        RayleighFlag.setDisabled(False)
        rayleighCheckChange(False, f_RayleighAlphaMTtl, f_RayleighAlphaM, f_RayleighBetaKTtl, f_RayleighBetaK, f_RayleighBetaKinitTtl,
                            f_RayleighBetaKinit, f_RayleighBetaKcmmtTtl, f_RayleighBetaKcmmt)

        if analysisTypeSelec.currentText() == "Variable Transient":
            analysisOptionsDTminTtl.show(); analysisOptionsDTmin.show(); analysisOptionsDTmaxTtl.show()
            analysisOptionsDTmax.show(); analysisOptionsJDTtl.show(); analysisOptionsJD.show()
    elif analysisTypeSelec.currentText() == "Modal":
        analysisTransientTypeSelec.model().item(4).setEnabled(True)
        analysisTransientTypeSelec.setCurrentIndex(4)
        analysisTransientTypeSelec.setDisabled(True)
        analysisOptionsDTTtl.hide(); analysisOptionsDT.hide()
        analysisOptionsDTminTtl.hide(); analysisOptionsDTmin.hide(); analysisOptionsDTmaxTtl.hide()
        analysisOptionsDTmax.hide(); analysisOptionsJDTtl.hide(); analysisOptionsJD.hide()
        analysisOptionsEgnValTtl.show(); analysisOptionsEgnVal.show(); analysisOptionsEgnSolvTtl.show()
        analysisOptionsEgnSolv.show()

        analysisIntegratorSelec.setDisabled(True)  # Integrator options
        analysisSystemSelec.setCurrentIndex(0)
        f_integratorLClambdaTtl.setDisabled(True); f_integratorLClambda.setDisabled(True); f_integratorLCNumIterTtl.setDisabled(True)
        f_integratorLCNumIter.setDisabled(True); f_integratorLClambdaminTtl.setDisabled(True); f_integratorLClambdamin.setDisabled(True)
        f_integratorLClambdamaxTtl.setDisabled(True); f_integratorLClambdamax.setDisabled(True)
        f_integratorDCnodeTtl.setDisabled(True); f_integratorDCnode.setDisabled(True)
        f_integratorDCdofTtl.setDisabled(True); f_integratorDCdof.setDisabled(True); f_integratorDCincrTtl.setDisabled(True)
        f_integratorDCincr.setDisabled(True); f_integratorDCnumItrTtl.setDisabled(True); f_integratorDCnumItr.setDisabled(True)
        f_integratorDCdeltaUminTtl.setDisabled(True); f_integratorDCdeltaUmin.setDisabled(True)
        f_integratorDCdeltaUmaxTtl.setDisabled(True); f_integratorDCdeltaUmax.setDisabled(True); f_integratorMUDNdLambda1Ttl.setDisabled(True)
        f_integratorMUDNdLambda1.setDisabled(True); f_integratorMUDNJdTtl.setDisabled(True); f_integratorMUDNJd.setDisabled(True)
        f_integratorMUDNdminLambdaTtl.setDisabled(True); f_integratorMUDNdminLambda.setDisabled(True); f_integratorMUDNdmaxLambdaTtl.setDisabled(True)
        f_integratorMUDNdmaxLambda.setDisabled(True); f_integratorALsTtl.setDisabled(True); f_integratorALs.setDisabled(True)
        f_integratorALalphaTtl.setDisabled(True); f_integratorALalpha.setDisabled(True); f_integratorNewmarkGammaTtl.setDisabled(True)
        f_integratorNewmarkGamma.setDisabled(True); f_integratorNewmarkBetaTtl.setDisabled(True); f_integratorNewmarkBeta.setDisabled(True)
        f_integratorHHTAlphaTtl.setDisabled(True); f_integratorHHTAlpha.setDisabled(True); f_integratorHHTGammaTtl.setDisabled(True)
        f_integratorHHTGamma.setDisabled(True); integratorGENalphAlphamTtl.setDisabled(True); integratorGENalphAlpham.setDisabled(True)
        integratorGENalphAlphafTtl.setDisabled(True); integratorGENalphAlphaf.setDisabled(True); integratorGENalphGammaTtl.setDisabled(True)
        integratorGENalphGamma.setDisabled(True); integratorGENalphBetaTtl.setDisabled(True); integratorGENalphBeta.setDisabled(True)
        f_integratorHHTBetaTtl.setDisabled(True); f_integratorHHTBeta.setDisabled(True)
        f_algoLinSecantFlag.setDisabled(True); f_algoLinInitialFlag.setDisabled(True); f_algoLinFactorOnceFlag.setDisabled(True)
        f_algoNewInitialFlag.setDisabled(True); f_algoNewInitThenCurrentFlag.setDisabled(True); f_algoNewWlineTypeSearchSelecTtl.setDisabled(True)
        f_algoNewWlineTypeSearchSelec.setDisabled(True); f_algoNewWlineTolTtl.setDisabled(True); f_algoNewWlineTol.setDisabled(True)
        f_algoNewWlineMaxItrTtl.setDisabled(True); f_algoNewWlineMaxItr.setDisabled(True); f_algoNewWlineMinEtaTtl.setDisabled(True)
        f_algoNewWlineMinEta.setDisabled(True); f_algoNewWlineMaxEtaTtl.setDisabled(True); f_algoNewWlineMaxEta.setDisabled(True)
        f_algoModNewInitialFlag.setDisabled(True); f_algoKryNewTangItrSelecTtl.setDisabled(True); f_algoKryNewTangItrSelec.setDisabled(True)
        f_algoKryNewTangIncrSelecTtl.setDisabled(True); f_algoKryNewTangIncrSelec.setDisabled(True); f_algoKryNewMaxDimTtl.setDisabled(True)
        f_algoKryNewMaxDim.setDisabled(True); f_algoSecNewTangItrSelecTtl.setDisabled(True); f_algoSecNewTangItrSelec.setDisabled(True)
        f_algoSecNewTangIncrSelecTtl.setDisabled(True); f_algoSecNewTangIncrSelec.setDisabled(True); f_algoSecNewMaxDimTtl.setDisabled(True)
        f_algoSecNewMaxDim.setDisabled(True); f_algoBroydenCountFlag.setDisabled(True); f_algoBroydenCountFlagValue.setDisabled(True)
        analysisAlgorithmSelecTtl.setDisabled(True); analysisAlgorithmSelec.setDisabled(True)
        f_testNormUnblcTolTtl.setDisabled(True); f_testNormUnblcTol.setDisabled(True); f_testNormUnblcPFlagSelec.setDisabled(True)
        f_testNormUnblcNtypeTtl.setDisabled(True); f_testNormUnblcNType.setDisabled(True)
        f_analysisTestSelec.setDisabled(True); f_analysisTestSelecTtl.setDisabled(True); f_testNormUnblcItrTtl.setDisabled(True)
        f_testNormUnblcItr.setDisabled(True)
        f_recordSelectBtn.setDisabled(True); f_pointLoadtBtn.setDisabled(True)
        RayleighFlag.setDisabled(True)
        rayleighCheckChange(False, f_RayleighAlphaMTtl, f_RayleighAlphaM, f_RayleighBetaKTtl, f_RayleighBetaK, f_RayleighBetaKinitTtl,
                            f_RayleighBetaKinit, f_RayleighBetaKcmmtTtl, f_RayleighBetaKcmmt)

    return analysisEdDialog


def analysisSubTypeChange(f_analysisTransientTypeSelec, f_analysisOptionsGravAccXttl, f_analysisOptionsGravAccYttl,
                          f_analysisOptionsGravAccZttl, f_analysisOptionsGravAccX, f_analysisOptionsGravAccY,
                          f_analysisOptionsGravAccZ, f_analysisOptionsPushDirTtl, f_analysisOptionsPushDirSelec,
                          f_analysisOptionsGravMaxDispTtl, f_analysisOptionsGravMaxDisp, f_analysisOptionsPushMaxDispTtl,
                          f_analysisOptionsPushMaxDisp):
    if f_analysisTransientTypeSelec.currentText() == "Pushover":
        f_analysisOptionsGravAccXttl.hide(); f_analysisOptionsGravAccYttl.hide(); f_analysisOptionsGravAccZttl.hide()
        f_analysisOptionsGravAccX.hide(); f_analysisOptionsGravAccY.hide(); f_analysisOptionsGravAccZ.hide()
        f_analysisOptionsPushDirTtl.show(); f_analysisOptionsPushDirSelec.show()
        if analysisIntegratorSelec.currentText() == "Displacement Control":
            f_analysisOptionsGravMaxDispTtl.hide(); f_analysisOptionsGravMaxDisp.hide()
            f_analysisOptionsPushMaxDispTtl.show(); f_analysisOptionsPushMaxDisp.show()
        else:
            f_analysisOptionsGravMaxDispTtl.hide(); f_analysisOptionsGravMaxDisp.hide()
            f_analysisOptionsPushMaxDispTtl.hide(); f_analysisOptionsPushMaxDisp.hide()
    elif f_analysisTransientTypeSelec.currentText() == "Gravity":
        f_analysisOptionsGravAccXttl.show();  f_analysisOptionsGravAccYttl.show(); f_analysisOptionsGravAccZttl.show()
        f_analysisOptionsGravAccX.show(); f_analysisOptionsGravAccY.show(); f_analysisOptionsGravAccZ.show()
        f_analysisOptionsPushDirTtl.hide(); f_analysisOptionsPushDirSelec.hide()
        f_analysisOptionsGravMaxDispTtl.show(); f_analysisOptionsGravMaxDisp.show()
        if analysisIntegratorSelec.currentText() == "Displacement Control":
            f_analysisOptionsGravMaxDispTtl.show(); f_analysisOptionsGravMaxDisp.show()
            f_analysisOptionsPushMaxDispTtl.hide(); f_analysisOptionsPushMaxDisp.hide()
        else:
            f_analysisOptionsGravMaxDispTtl.hide(); f_analysisOptionsGravMaxDisp.hide()
            f_analysisOptionsPushMaxDispTtl.hide(); f_analysisOptionsPushMaxDisp.hide()
    else:
        f_analysisOptionsGravAccXttl.hide(); f_analysisOptionsGravAccYttl.hide(); f_analysisOptionsGravAccZttl.hide()
        f_analysisOptionsGravAccX.hide(); f_analysisOptionsGravAccY.hide(); f_analysisOptionsGravAccZ.hide()
        f_analysisOptionsPushDirTtl.hide(); f_analysisOptionsPushDirSelec.hide()
        f_analysisOptionsGravMaxDispTtl.hide(); f_analysisOptionsGravMaxDisp.hide()
        f_analysisOptionsPushMaxDispTtl.hide(); f_analysisOptionsPushMaxDisp.hide()

def constraintTypeChange(changState, f_constraintAlphas, f_constraintAlpham):
    if analysisConstraintSelec.currentText() == "Lagrange":
        f_constraintAlphas.setEnabled(True)
        f_constraintAlpham.setEnabled(True)
        f_constraintAlphas.setText(str(1.0))
        f_constraintAlpham.setText(str(1.0))
    elif analysisConstraintSelec.currentText() == "Penalty":
        f_constraintAlphas.setEnabled(True)
        f_constraintAlpham.setEnabled(True)
        f_constraintAlphas.setText("")
        f_constraintAlpham.setText("")
    else:
        f_constraintAlphas.setEnabled(False)
        f_constraintAlpham.setEnabled(False)
        f_constraintAlphas.setText("")
        f_constraintAlpham.setText("")


def integratorTypeChange(changeState, f_integratorLClambdaTtl, f_integratorLClambda, f_integratorLCNumIterTtl,
                         f_integratorLCNumIter, f_integratorLClambdaminTtl, f_integratorLClambdamin,
                         f_integratorLClambdamaxTtl, f_integratorLClambdamax, f_integratorDCnodeTtl, f_integratorDCnode,
                         f_integratorDCdofTtl, f_integratorDCdof, f_integratorDCincrTtl, f_integratorDCincr,
                         f_integratorDCnumItrTtl, f_integratorDCnumItr, f_integratorDCdeltaUminTtl,
                         f_integratorDCdeltaUmin, f_integratorDCdeltaUmaxTtl, f_integratorDCdeltaUmax,
                         f_integratorMUDNdLambda1Ttl, f_integratorMUDNdLambda1, f_integratorMUDNJdTtl,
                         f_integratorMUDNJd, f_integratorMUDNdminLambdaTtl, f_integratorMUDNdminLambda,
                         f_integratorMUDNdmaxLambdaTtl, f_integratorMUDNdmaxLambda, f_integratorALsTtl, f_integratorALs,
                         f_integratorALalphaTtl, f_integratorALalpha, f_integratorNewmarkGammaTtl, f_integratorNewmarkGamma,
                         f_integratorNewmarkBetaTtl, f_integratorNewmarkBeta, f_integratorHHTAlphaTtl, f_integratorHHTAlpha,
                         f_integratorHHTGammaTtl, f_integratorHHTGamma, integratorGENalphAlphamTtl, integratorGENalphAlpham, integratorGENalphAlphafTtl,
                         integratorGENalphAlphaf, integratorGENalphGammaTtl, integratorGENalphGamma,
                         integratorGENalphBetaTtl, integratorGENalphBeta, f_integratorHHTBetaTtl, f_integratorHHTBeta,
                         f_analysisOptionsPushMaxDispTtl, f_analysisOptionsPushMaxDisp, f_analysisOptionsGravMaxDispTtl,
                         f_analysisOptionsGravMaxDisp, f_analysisTransientTypeSelec):
    if analysisIntegratorSelec.currentText() == "Load Control":
        f_integratorLClambdaTtl.show(); f_integratorLClambda.show(); f_integratorLCNumIterTtl.show()
        f_integratorLCNumIter.show(); f_integratorLClambdaminTtl.show(); f_integratorLClambdamin.show()
        f_integratorLClambdamaxTtl.show(); f_integratorLClambdamax.show()
        f_integratorDCnodeTtl.hide(); f_integratorDCnode.hide(); f_integratorDCdofTtl.hide(); f_integratorDCdof.hide()
        f_integratorDCincrTtl.hide(); f_integratorDCincr.hide(); f_integratorDCnumItrTtl.hide()
        f_integratorDCnumItr.hide(); f_integratorDCdeltaUminTtl.hide(); f_integratorDCdeltaUmin.hide()
        f_integratorDCdeltaUmaxTtl.hide(); f_integratorDCdeltaUmax.hide()
        f_integratorMUDNdLambda1Ttl.hide(); f_integratorMUDNdLambda1.hide(); f_integratorMUDNJdTtl.hide()
        f_integratorMUDNJd.hide(); f_integratorMUDNdminLambdaTtl.hide(); f_integratorMUDNdminLambda.hide()
        f_integratorMUDNdmaxLambdaTtl.hide(); f_integratorMUDNdmaxLambda.hide()
        f_integratorALsTtl.hide(); f_integratorALs.hide(); f_integratorALalphaTtl.hide(); f_integratorALalpha.hide()
        f_integratorNewmarkGammaTtl.hide(); f_integratorNewmarkGamma.hide(); f_integratorNewmarkBetaTtl.hide()
        f_integratorNewmarkBeta.hide()
        f_integratorHHTAlphaTtl.hide(); f_integratorHHTAlpha.hide(); f_integratorHHTGammaTtl.hide(); f_integratorHHTGamma.hide()
        f_integratorHHTBetaTtl.hide(); f_integratorHHTBeta.hide()
        integratorGENalphAlphamTtl.hide(); integratorGENalphAlpham.hide(); integratorGENalphAlphafTtl.hide()
        integratorGENalphAlphaf.hide(); integratorGENalphGammaTtl.hide(); integratorGENalphGamma.hide()
        integratorGENalphBetaTtl.hide(); integratorGENalphBeta.hide()
        f_analysisOptionsPushMaxDispTtl.hide(); f_analysisOptionsPushMaxDisp.hide()
        f_analysisOptionsGravMaxDispTtl.hide(); f_analysisOptionsGravMaxDisp.hide()
    elif analysisIntegratorSelec.currentText() == "Displacement Control":
        f_integratorLClambdaTtl.hide(); f_integratorLClambda.hide(); f_integratorLCNumIterTtl.hide()
        f_integratorLCNumIter.hide(); f_integratorLClambdaminTtl.hide(); f_integratorLClambdamin.hide()
        f_integratorLClambdamaxTtl.hide(); f_integratorLClambdamax.hide()
        f_integratorDCnodeTtl.show(); f_integratorDCnode.show(); f_integratorDCdofTtl.show(); f_integratorDCdof.show()
        f_integratorDCincrTtl.show(); f_integratorDCincr.show(); f_integratorDCnumItrTtl.show()
        f_integratorDCnumItr.show(); f_integratorDCdeltaUminTtl.show(); f_integratorDCdeltaUmin.show()
        f_integratorDCdeltaUmaxTtl.show(); f_integratorDCdeltaUmax.show()
        f_integratorMUDNdLambda1Ttl.hide(); f_integratorMUDNdLambda1.hide(); f_integratorMUDNJdTtl.hide()
        f_integratorMUDNJd.hide(); f_integratorMUDNdminLambdaTtl.hide(); f_integratorMUDNdminLambda.hide()
        f_integratorMUDNdmaxLambdaTtl.hide(); f_integratorMUDNdmaxLambda.hide()
        f_integratorALsTtl.hide(); f_integratorALs.hide(); f_integratorALalphaTtl.hide(); f_integratorALalpha.hide()
        f_integratorNewmarkGammaTtl.hide(); f_integratorNewmarkGamma.hide(); f_integratorNewmarkBetaTtl.hide()
        f_integratorNewmarkBeta.hide()
        f_integratorHHTAlphaTtl.hide(); f_integratorHHTAlpha.hide(); f_integratorHHTGammaTtl.hide(); f_integratorHHTGamma.hide()
        f_integratorHHTBetaTtl.hide(); f_integratorHHTBeta.hide()
        integratorGENalphAlphamTtl.hide(); integratorGENalphAlpham.hide(); integratorGENalphAlphafTtl.hide()
        integratorGENalphAlphaf.hide(); integratorGENalphGammaTtl.hide(); integratorGENalphGamma.hide()
        integratorGENalphBetaTtl.hide(); integratorGENalphBeta.hide()
        if f_analysisTransientTypeSelec.currentText() == "Pushover":
            f_analysisOptionsPushMaxDispTtl.show(); f_analysisOptionsPushMaxDisp.show()
            f_analysisOptionsGravMaxDispTtl.hide(); f_analysisOptionsGravMaxDisp.hide()
        elif f_analysisTransientTypeSelec.currentText() == "Gravity":
            f_analysisOptionsGravMaxDispTtl.show(); f_analysisOptionsGravMaxDisp.show()
            f_analysisOptionsPushMaxDispTtl.hide(); f_analysisOptionsPushMaxDisp.hide()
    elif analysisIntegratorSelec.currentText() == "Minimum Unbalanced Displacement Norm":
        f_integratorLClambdaTtl.hide(); f_integratorLClambda.hide(); f_integratorLCNumIterTtl.hide()
        f_integratorLCNumIter.hide(); f_integratorLClambdaminTtl.hide(); f_integratorLClambdamin.hide()
        f_integratorLClambdamaxTtl.hide(); f_integratorLClambdamax.hide()
        f_integratorDCnodeTtl.hide(); f_integratorDCnode.hide(); f_integratorDCdofTtl.hide(); f_integratorDCdof.hide()
        f_integratorDCincrTtl.hide(); f_integratorDCincr.hide(); f_integratorDCnumItrTtl.hide()
        f_integratorDCnumItr.hide(); f_integratorDCdeltaUminTtl.hide(); f_integratorDCdeltaUmin.hide()
        f_integratorDCdeltaUmaxTtl.hide(); f_integratorDCdeltaUmax.hide()
        f_integratorMUDNdLambda1Ttl.show(); f_integratorMUDNdLambda1.show(); f_integratorMUDNJdTtl.show()
        f_integratorMUDNJd.show(); f_integratorMUDNdminLambdaTtl.show(); f_integratorMUDNdminLambda.show()
        f_integratorMUDNdmaxLambdaTtl.show(); f_integratorMUDNdmaxLambda.show()
        f_integratorALsTtl.hide(); f_integratorALs.hide(); f_integratorALalphaTtl.hide(); f_integratorALalpha.hide()
        f_integratorNewmarkGammaTtl.hide(); f_integratorNewmarkGamma.hide(); f_integratorNewmarkBetaTtl.hide()
        f_integratorNewmarkBeta.hide()
        f_integratorHHTAlphaTtl.hide(); f_integratorHHTAlpha.hide(); f_integratorHHTGammaTtl.hide(); f_integratorHHTGamma.hide()
        f_integratorHHTBetaTtl.hide(); f_integratorHHTBeta.hide()
        integratorGENalphAlphamTtl.hide(); integratorGENalphAlpham.hide(); integratorGENalphAlphafTtl.hide()
        integratorGENalphAlphaf.hide(); integratorGENalphGammaTtl.hide(); integratorGENalphGamma.hide()
        integratorGENalphBetaTtl.hide(); integratorGENalphBeta.hide()
        f_analysisOptionsPushMaxDispTtl.hide(); f_analysisOptionsPushMaxDisp.hide()
        f_analysisOptionsGravMaxDispTtl.hide(); f_analysisOptionsGravMaxDisp.hide()
    elif analysisIntegratorSelec.currentText() == "Arc Length":
        f_integratorLClambdaTtl.hide(); f_integratorLClambda.hide(); f_integratorLCNumIterTtl.hide()
        f_integratorLCNumIter.hide(); f_integratorLClambdaminTtl.hide(); f_integratorLClambdamin.hide()
        f_integratorLClambdamaxTtl.hide(); f_integratorLClambdamax.hide()
        f_integratorDCnodeTtl.hide(); f_integratorDCnode.hide(); f_integratorDCdofTtl.hide(); f_integratorDCdof.hide()
        f_integratorDCincrTtl.hide(); f_integratorDCincr.hide(); f_integratorDCnumItrTtl.hide()
        f_integratorDCnumItr.hide(); f_integratorDCdeltaUminTtl.hide(); f_integratorDCdeltaUmin.hide()
        f_integratorDCdeltaUmaxTtl.hide(); f_integratorDCdeltaUmax.hide()
        f_integratorMUDNdLambda1Ttl.hide(); f_integratorMUDNdLambda1.hide(); f_integratorMUDNJdTtl.hide()
        f_integratorMUDNJd.hide(); f_integratorMUDNdminLambdaTtl.hide(); f_integratorMUDNdminLambda.hide()
        f_integratorMUDNdmaxLambdaTtl.hide(); f_integratorMUDNdmaxLambda.hide()
        f_integratorALsTtl.show(); f_integratorALs.show(); f_integratorALalphaTtl.show(); f_integratorALalpha.show()
        f_integratorNewmarkGammaTtl.hide(); f_integratorNewmarkGamma.hide(); f_integratorNewmarkBetaTtl.hide()
        f_integratorNewmarkBeta.hide()
        f_integratorHHTAlphaTtl.hide(); f_integratorHHTAlpha.hide(); f_integratorHHTGammaTtl.hide(); f_integratorHHTGamma.hide()
        f_integratorHHTBetaTtl.hide(); f_integratorHHTBeta.hide()
        integratorGENalphAlphamTtl.hide(); integratorGENalphAlpham.hide(); integratorGENalphAlphafTtl.hide()
        integratorGENalphAlphaf.hide(); integratorGENalphGammaTtl.hide(); integratorGENalphGamma.hide()
        integratorGENalphBetaTtl.hide(); integratorGENalphBeta.hide()
        f_analysisOptionsPushMaxDispTtl.hide(); f_analysisOptionsPushMaxDisp.hide()
        f_analysisOptionsGravMaxDispTtl.hide(); f_analysisOptionsGravMaxDisp.hide()
    elif analysisIntegratorSelec.currentText() == "Newmark":
        f_integratorLClambdaTtl.hide(); f_integratorLClambda.hide(); f_integratorLCNumIterTtl.hide()
        f_integratorLCNumIter.hide(); f_integratorLClambdaminTtl.hide(); f_integratorLClambdamin.hide()
        f_integratorLClambdamaxTtl.hide(); f_integratorLClambdamax.hide()
        f_integratorDCnodeTtl.hide(); f_integratorDCnode.hide(); f_integratorDCdofTtl.hide(); f_integratorDCdof.hide()
        f_integratorDCincrTtl.hide(); f_integratorDCincr.hide(); f_integratorDCnumItrTtl.hide()
        f_integratorDCnumItr.hide(); f_integratorDCdeltaUminTtl.hide(); f_integratorDCdeltaUmin.hide()
        f_integratorDCdeltaUmaxTtl.hide(); f_integratorDCdeltaUmax.hide()
        f_integratorMUDNdLambda1Ttl.hide(); f_integratorMUDNdLambda1.hide(); f_integratorMUDNJdTtl.hide()
        f_integratorMUDNJd.hide(); f_integratorMUDNdminLambdaTtl.hide(); f_integratorMUDNdminLambda.hide()
        f_integratorMUDNdmaxLambdaTtl.hide(); f_integratorMUDNdmaxLambda.hide()
        f_integratorALsTtl.hide(); f_integratorALs.hide(); f_integratorALalphaTtl.hide(); f_integratorALalpha.hide()
        f_integratorNewmarkGammaTtl.show(); f_integratorNewmarkGamma.show(); f_integratorNewmarkBetaTtl.show()
        f_integratorNewmarkBeta.show()
        f_integratorHHTAlphaTtl.hide(); f_integratorHHTAlpha.hide(); f_integratorHHTGammaTtl.hide(); f_integratorHHTGamma.hide()
        f_integratorHHTBetaTtl.hide(); f_integratorHHTBeta.hide()
        integratorGENalphAlphamTtl.hide(); integratorGENalphAlpham.hide(); integratorGENalphAlphafTtl.hide()
        integratorGENalphAlphaf.hide(); integratorGENalphGammaTtl.hide(); integratorGENalphGamma.hide()
        integratorGENalphBetaTtl.hide(); integratorGENalphBeta.hide()
        f_analysisOptionsPushMaxDispTtl.hide(); f_analysisOptionsPushMaxDisp.hide()
        f_analysisOptionsGravMaxDispTtl.hide(); f_analysisOptionsGravMaxDisp.hide()
    elif analysisIntegratorSelec.currentText() == "Hibler-Hughes-Taylor":
        f_integratorLClambdaTtl.hide(); f_integratorLClambda.hide(); f_integratorLCNumIterTtl.hide()
        f_integratorLCNumIter.hide(); f_integratorLClambdaminTtl.hide(); f_integratorLClambdamin.hide()
        f_integratorLClambdamaxTtl.hide(); f_integratorLClambdamax.hide()
        f_integratorDCnodeTtl.hide(); f_integratorDCnode.hide(); f_integratorDCdofTtl.hide(); f_integratorDCdof.hide()
        f_integratorDCincrTtl.hide(); f_integratorDCincr.hide(); f_integratorDCnumItrTtl.hide()
        f_integratorDCnumItr.hide(); f_integratorDCdeltaUminTtl.hide(); f_integratorDCdeltaUmin.hide()
        f_integratorDCdeltaUmaxTtl.hide(); f_integratorDCdeltaUmax.hide()
        f_integratorMUDNdLambda1Ttl.hide(); f_integratorMUDNdLambda1.hide(); f_integratorMUDNJdTtl.hide()
        f_integratorMUDNJd.hide(); f_integratorMUDNdminLambdaTtl.hide(); f_integratorMUDNdminLambda.hide()
        f_integratorMUDNdmaxLambdaTtl.hide(); f_integratorMUDNdmaxLambda.hide()
        f_integratorALsTtl.hide(); f_integratorALs.hide(); f_integratorALalphaTtl.hide(); f_integratorALalpha.hide()
        f_integratorNewmarkGammaTtl.hide(); f_integratorNewmarkGamma.hide(); f_integratorNewmarkBetaTtl.hide()
        f_integratorNewmarkBeta.hide()
        f_integratorHHTAlphaTtl.show(); f_integratorHHTAlpha.show(); f_integratorHHTGammaTtl.show(); f_integratorHHTGamma.show()
        f_integratorHHTBetaTtl.show(); f_integratorHHTBeta.show()
        integratorGENalphAlphamTtl.hide(); integratorGENalphAlpham.hide(); integratorGENalphAlphafTtl.hide()
        integratorGENalphAlphaf.hide(); integratorGENalphGammaTtl.hide(); integratorGENalphGamma.hide()
        integratorGENalphBetaTtl.hide(); integratorGENalphBeta.hide()
        f_analysisOptionsPushMaxDispTtl.hide(); f_analysisOptionsPushMaxDisp.hide()
        f_analysisOptionsGravMaxDispTtl.hide(); f_analysisOptionsGravMaxDisp.hide()
    elif analysisIntegratorSelec.currentText() == "Generalized Alpha":
        f_integratorLClambdaTtl.hide(); f_integratorLClambda.hide(); f_integratorLCNumIterTtl.hide()
        f_integratorLCNumIter.hide(); f_integratorLClambdaminTtl.hide(); f_integratorLClambdamin.hide()
        f_integratorLClambdamaxTtl.hide(); f_integratorLClambdamax.hide()
        f_integratorDCnodeTtl.hide(); f_integratorDCnode.hide(); f_integratorDCdofTtl.hide(); f_integratorDCdof.hide()
        f_integratorDCincrTtl.hide(); f_integratorDCincr.hide(); f_integratorDCnumItrTtl.hide()
        f_integratorDCnumItr.hide(); f_integratorDCdeltaUminTtl.hide(); f_integratorDCdeltaUmin.hide()
        f_integratorDCdeltaUmaxTtl.hide(); f_integratorDCdeltaUmax.hide()
        f_integratorMUDNdLambda1Ttl.hide(); f_integratorMUDNdLambda1.hide(); f_integratorMUDNJdTtl.hide()
        f_integratorMUDNJd.hide(); f_integratorMUDNdminLambdaTtl.hide(); f_integratorMUDNdminLambda.hide()
        f_integratorMUDNdmaxLambdaTtl.hide(); f_integratorMUDNdmaxLambda.hide()
        f_integratorALsTtl.hide(); f_integratorALs.hide(); f_integratorALalphaTtl.hide(); f_integratorALalpha.hide()
        f_integratorNewmarkGammaTtl.hide(); f_integratorNewmarkGamma.hide(); f_integratorNewmarkBetaTtl.hide()
        f_integratorNewmarkBeta.hide()
        f_integratorHHTAlphaTtl.hide(); f_integratorHHTAlpha.hide(); f_integratorHHTGammaTtl.hide(); f_integratorHHTGamma.hide()
        f_integratorHHTBetaTtl.hide(); f_integratorHHTBeta.hide()
        integratorGENalphAlphamTtl.show(); integratorGENalphAlpham.show(); integratorGENalphAlphafTtl.show()
        integratorGENalphAlphaf.show(); integratorGENalphGammaTtl.show(); integratorGENalphGamma.show()
        integratorGENalphBetaTtl.show(); integratorGENalphBeta.show()
        f_analysisOptionsPushMaxDispTtl.hide(); f_analysisOptionsPushMaxDisp.hide()
        f_analysisOptionsGravMaxDispTtl.hide(); f_analysisOptionsGravMaxDisp.hide()
    else:
        f_integratorLClambdaTtl.hide(); f_integratorLClambda.hide(); f_integratorLCNumIterTtl.hide()
        f_integratorLCNumIter.hide(); f_integratorLClambdaminTtl.hide(); f_integratorLClambdamin.hide()
        f_integratorLClambdamaxTtl.hide(); f_integratorLClambdamax.hide()
        f_integratorDCnodeTtl.hide(); f_integratorDCnode.hide(); f_integratorDCdofTtl.hide(); f_integratorDCdof.hide()
        f_integratorDCincrTtl.hide(); f_integratorDCincr.hide(); f_integratorDCnumItrTtl.hide()
        f_integratorDCnumItr.hide(); f_integratorDCdeltaUminTtl.hide(); f_integratorDCdeltaUmin.hide()
        f_integratorDCdeltaUmaxTtl.hide(); f_integratorDCdeltaUmax.hide()
        f_integratorMUDNdLambda1Ttl.hide(); f_integratorMUDNdLambda1.hide(); f_integratorMUDNJdTtl.hide()
        f_integratorMUDNJd.hide(); f_integratorMUDNdminLambdaTtl.hide(); f_integratorMUDNdminLambda.hide()
        f_integratorMUDNdmaxLambdaTtl.hide(); f_integratorMUDNdmaxLambda.hide()
        f_integratorALsTtl.hide(); f_integratorALs.hide(); f_integratorALalphaTtl.hide(); f_integratorALalpha.hide()
        f_integratorNewmarkGammaTtl.hide(); f_integratorNewmarkGamma.hide(); f_integratorNewmarkBetaTtl.hide()
        f_integratorNewmarkBeta.hide()
        f_integratorHHTAlphaTtl.hide(); f_integratorHHTAlpha.hide(); f_integratorHHTGammaTtl.hide(); f_integratorHHTGamma.hide()
        f_integratorHHTBetaTtl.hide(); f_integratorHHTBeta.hide()
        integratorGENalphAlphamTtl.hide(); integratorGENalphAlpham.hide(); integratorGENalphAlphafTtl.hide()
        integratorGENalphAlphaf.hide(); integratorGENalphGammaTtl.hide(); integratorGENalphGamma.hide()
        integratorGENalphBetaTtl.hide(); integratorGENalphBeta.hide()
        f_analysisOptionsPushMaxDispTtl.hide(); f_analysisOptionsPushMaxDisp.hide()
        f_analysisOptionsGravMaxDispTtl.hide(); f_analysisOptionsGravMaxDisp.hide()


def algorithmTypeChange(changeState, f_algoLinSecantFlag, f_algoLinInitialFlag, f_algoLinFactorOnceFlag,
                        f_algoNewInitialFlag, f_algoNewInitThenCurrentFlag, f_algoNewWlineTypeSearchSelecTtl,
                        f_algoNewWlineTypeSearchSelec, f_algoNewWlineTolTtl, f_algoNewWlineTol, f_algoNewWlineMaxItrTtl,
                        f_algoNewWlineMaxItr, f_algoNewWlineMinEtaTtl, f_algoNewWlineMinEta, f_algoNewWlineMaxEtaTtl,
                        f_algoNewWlineMaxEta, f_algoModNewInitialFlag, f_algoKryNewTangItrSelecTtl, f_algoKryNewTangItrSelec,
                        f_algoKryNewTangIncrSelecTtl, f_algoKryNewTangIncrSelec, f_algoKryNewMaxDimTtl, f_algoKryNewMaxDim,
                        f_algoSecNewTangItrSelecTtl, f_algoSecNewTangItrSelec, f_algoSecNewTangIncrSelecTtl,
                        f_algoSecNewTangIncrSelec, f_algoSecNewMaxDimTtl, f_algoSecNewMaxDim, f_algoBroydenCountFlag,
                        f_algoBroydenCountFlagValue):
    if analysisAlgorithmSelec.currentText() == "Linear":
        f_algoLinSecantFlag.show(); f_algoLinInitialFlag.show(); f_algoLinFactorOnceFlag.show()
        f_algoNewInitialFlag.hide(); f_algoNewInitThenCurrentFlag.hide()
        f_algoNewWlineTypeSearchSelecTtl.hide(); f_algoNewWlineTypeSearchSelec.hide(); f_algoNewWlineTolTtl.hide()
        f_algoNewWlineTol.hide(); f_algoNewWlineMaxItrTtl.hide(); f_algoNewWlineMaxItr.hide(); f_algoNewWlineMinEtaTtl.hide()
        f_algoNewWlineMinEta.hide(); f_algoNewWlineMaxEtaTtl.hide(); f_algoNewWlineMaxEta.hide()
        f_algoModNewInitialFlag.hide()
        f_algoKryNewTangItrSelecTtl.hide(); f_algoKryNewTangItrSelec.hide(); f_algoKryNewTangIncrSelecTtl.hide()
        f_algoKryNewTangIncrSelec.hide(); f_algoKryNewMaxDimTtl.hide(); f_algoKryNewMaxDim.hide()
        f_algoSecNewTangItrSelecTtl.hide(); f_algoSecNewTangItrSelec.hide(); f_algoSecNewTangIncrSelecTtl.hide()
        f_algoSecNewTangIncrSelec.hide(); f_algoSecNewMaxDimTtl.hide(); f_algoSecNewMaxDim.hide()
        f_algoBroydenCountFlag.hide(); f_algoBroydenCountFlagValue.hide()
    elif analysisAlgorithmSelec.currentText() == "Newton":
        f_algoLinSecantFlag.hide(); f_algoLinInitialFlag.hide(); f_algoLinFactorOnceFlag.hide()
        f_algoNewInitialFlag.show(); f_algoNewInitThenCurrentFlag.show()
        f_algoNewWlineTypeSearchSelecTtl.hide(); f_algoNewWlineTypeSearchSelec.hide(); f_algoNewWlineTolTtl.hide()
        f_algoNewWlineTol.hide(); f_algoNewWlineMaxItrTtl.hide(); f_algoNewWlineMaxItr.hide(); f_algoNewWlineMinEtaTtl.hide()
        f_algoNewWlineMinEta.hide(); f_algoNewWlineMaxEtaTtl.hide(); f_algoNewWlineMaxEta.hide()
        f_algoModNewInitialFlag.hide()
        f_algoKryNewTangItrSelecTtl.hide(); f_algoKryNewTangItrSelec.hide(); f_algoKryNewTangIncrSelecTtl.hide()
        f_algoKryNewTangIncrSelec.hide(); f_algoKryNewMaxDimTtl.hide(); f_algoKryNewMaxDim.hide()
        f_algoSecNewTangItrSelecTtl.hide(); f_algoSecNewTangItrSelec.hide(); f_algoSecNewTangIncrSelecTtl.hide()
        f_algoSecNewTangIncrSelec.hide(); f_algoSecNewMaxDimTtl.hide(); f_algoSecNewMaxDim.hide()
        f_algoBroydenCountFlag.hide(); f_algoBroydenCountFlagValue.hide()
    elif analysisAlgorithmSelec.currentText() == "Newton with Line Search":
        f_algoLinSecantFlag.hide(); f_algoLinInitialFlag.hide(); f_algoLinFactorOnceFlag.hide()
        f_algoNewInitialFlag.hide(); f_algoNewInitThenCurrentFlag.hide()
        f_algoNewWlineTypeSearchSelecTtl.show(); f_algoNewWlineTypeSearchSelec.show(); f_algoNewWlineTolTtl.show()
        f_algoNewWlineTol.show(); f_algoNewWlineMaxItrTtl.show(); f_algoNewWlineMaxItr.show(); f_algoNewWlineMinEtaTtl.show()
        f_algoNewWlineMinEta.show(); f_algoNewWlineMaxEtaTtl.show(); f_algoNewWlineMaxEta.show()
        f_algoModNewInitialFlag.hide()
        f_algoKryNewTangItrSelecTtl.hide(); f_algoKryNewTangItrSelec.hide(); f_algoKryNewTangIncrSelecTtl.hide()
        f_algoKryNewTangIncrSelec.hide(); f_algoKryNewMaxDimTtl.hide(); f_algoKryNewMaxDim.hide()
        f_algoSecNewTangItrSelecTtl.hide(); f_algoSecNewTangItrSelec.hide(); f_algoSecNewTangIncrSelecTtl.hide()
        f_algoSecNewTangIncrSelec.hide(); f_algoSecNewMaxDimTtl.hide(); f_algoSecNewMaxDim.hide()
        f_algoBroydenCountFlag.hide(); f_algoBroydenCountFlagValue.hide()
    elif analysisAlgorithmSelec.currentText() == "Modified Newton":
        f_algoLinSecantFlag.hide(); f_algoLinInitialFlag.hide(); f_algoLinFactorOnceFlag.hide()
        f_algoNewInitialFlag.hide(); f_algoNewInitThenCurrentFlag.hide()
        f_algoNewWlineTypeSearchSelecTtl.hide(); f_algoNewWlineTypeSearchSelec.hide(); f_algoNewWlineTolTtl.hide()
        f_algoNewWlineTol.hide(); f_algoNewWlineMaxItrTtl.hide(); f_algoNewWlineMaxItr.hide(); f_algoNewWlineMinEtaTtl.hide()
        f_algoNewWlineMinEta.hide(); f_algoNewWlineMaxEtaTtl.hide(); f_algoNewWlineMaxEta.hide()
        f_algoModNewInitialFlag.show()
        f_algoKryNewTangItrSelecTtl.hide(); f_algoKryNewTangItrSelec.hide(); f_algoKryNewTangIncrSelecTtl.hide()
        f_algoKryNewTangIncrSelec.hide(); f_algoKryNewMaxDimTtl.hide(); f_algoKryNewMaxDim.hide()
        f_algoSecNewTangItrSelecTtl.hide(); f_algoSecNewTangItrSelec.hide(); f_algoSecNewTangIncrSelecTtl.hide()
        f_algoSecNewTangIncrSelec.hide(); f_algoSecNewMaxDimTtl.hide(); f_algoSecNewMaxDim.hide()
        f_algoBroydenCountFlag.hide(); f_algoBroydenCountFlagValue.hide()
    elif analysisAlgorithmSelec.currentText() == "Krylov-Newton":
        f_algoLinSecantFlag.hide(); f_algoLinInitialFlag.hide(); f_algoLinFactorOnceFlag.hide()
        f_algoNewInitialFlag.hide(); f_algoNewInitThenCurrentFlag.hide()
        f_algoNewWlineTypeSearchSelecTtl.hide(); f_algoNewWlineTypeSearchSelec.hide(); f_algoNewWlineTolTtl.hide()
        f_algoNewWlineTol.hide(); f_algoNewWlineMaxItrTtl.hide(); f_algoNewWlineMaxItr.hide(); f_algoNewWlineMinEtaTtl.hide()
        f_algoNewWlineMinEta.hide(); f_algoNewWlineMaxEtaTtl.hide(); f_algoNewWlineMaxEta.hide()
        f_algoModNewInitialFlag.hide()
        f_algoKryNewTangItrSelecTtl.show(); f_algoKryNewTangItrSelec.show(); f_algoKryNewTangIncrSelecTtl.show()
        f_algoKryNewTangIncrSelec.show(); f_algoKryNewMaxDimTtl.show(); f_algoKryNewMaxDim.show()
        f_algoSecNewTangItrSelecTtl.hide(); f_algoSecNewTangItrSelec.hide(); f_algoSecNewTangIncrSelecTtl.hide()
        f_algoSecNewTangIncrSelec.hide(); f_algoSecNewMaxDimTtl.hide(); f_algoSecNewMaxDim.hide()
        f_algoBroydenCountFlag.hide(); f_algoBroydenCountFlagValue.hide()
    elif analysisAlgorithmSelec.currentText() == "Secant Newton":
        f_algoLinSecantFlag.hide(); f_algoLinInitialFlag.hide(); f_algoLinFactorOnceFlag.hide()
        f_algoNewInitialFlag.hide(); f_algoNewInitThenCurrentFlag.hide()
        f_algoNewWlineTypeSearchSelecTtl.hide(); f_algoNewWlineTypeSearchSelec.hide(); f_algoNewWlineTolTtl.hide()
        f_algoNewWlineTol.hide(); f_algoNewWlineMaxItrTtl.hide(); f_algoNewWlineMaxItr.hide(); f_algoNewWlineMinEtaTtl.hide()
        f_algoNewWlineMinEta.hide(); f_algoNewWlineMaxEtaTtl.hide(); f_algoNewWlineMaxEta.hide()
        f_algoModNewInitialFlag.hide()
        f_algoKryNewTangItrSelecTtl.hide(); f_algoKryNewTangItrSelec.hide(); f_algoKryNewTangIncrSelecTtl.hide()
        f_algoKryNewTangIncrSelec.hide(); f_algoKryNewMaxDimTtl.hide(); f_algoKryNewMaxDim.hide()
        f_algoSecNewTangItrSelecTtl.show(); f_algoSecNewTangItrSelec.show(); f_algoSecNewTangIncrSelecTtl.show()
        f_algoSecNewTangIncrSelec.show(); f_algoSecNewMaxDimTtl.show(); f_algoSecNewMaxDim.show()
        f_algoBroydenCountFlag.hide(); f_algoBroydenCountFlagValue.hide()
    elif analysisAlgorithmSelec.currentText() == "Broyden":
        f_algoLinSecantFlag.hide(); f_algoLinInitialFlag.hide(); f_algoLinFactorOnceFlag.hide()
        f_algoNewInitialFlag.hide(); f_algoNewInitThenCurrentFlag.hide()
        f_algoNewWlineTypeSearchSelecTtl.hide(); f_algoNewWlineTypeSearchSelec.hide(); f_algoNewWlineTolTtl.hide()
        f_algoNewWlineTol.hide(); f_algoNewWlineMaxItrTtl.hide(); f_algoNewWlineMaxItr.hide(); f_algoNewWlineMinEtaTtl.hide()
        f_algoNewWlineMinEta.hide(); f_algoNewWlineMaxEtaTtl.hide(); f_algoNewWlineMaxEta.hide()
        f_algoModNewInitialFlag.hide()
        f_algoKryNewTangItrSelecTtl.hide(); f_algoKryNewTangItrSelec.hide(); f_algoKryNewTangIncrSelecTtl.hide()
        f_algoKryNewTangIncrSelec.hide(); f_algoKryNewMaxDimTtl.hide(); f_algoKryNewMaxDim.hide()
        f_algoSecNewTangItrSelecTtl.hide(); f_algoSecNewTangItrSelec.hide(); f_algoSecNewTangIncrSelecTtl.hide()
        f_algoSecNewTangIncrSelec.hide(); f_algoSecNewMaxDimTtl.hide(); f_algoSecNewMaxDim.hide()
        f_algoBroydenCountFlag.show(); f_algoBroydenCountFlagValue.show()
    else:
        f_algoLinSecantFlag.hide(); f_algoLinInitialFlag.hide(); f_algoLinFactorOnceFlag.hide()
        f_algoNewInitialFlag.hide(); f_algoNewInitThenCurrentFlag.hide()
        f_algoNewWlineTypeSearchSelecTtl.hide(); f_algoNewWlineTypeSearchSelec.hide(); f_algoNewWlineTolTtl.hide()
        f_algoNewWlineTol.hide(); f_algoNewWlineMaxItrTtl.hide(); f_algoNewWlineMaxItr.hide(); f_algoNewWlineMinEtaTtl.hide()
        f_algoNewWlineMinEta.hide(); f_algoNewWlineMaxEtaTtl.hide(); f_algoNewWlineMaxEta.hide()
        f_algoModNewInitialFlag.hide()
        f_algoKryNewTangItrSelecTtl.hide(); f_algoKryNewTangItrSelec.hide(); f_algoKryNewTangIncrSelecTtl.hide()
        f_algoKryNewTangIncrSelec.hide(); f_algoKryNewMaxDimTtl.hide(); f_algoKryNewMaxDim.hide()
        f_algoSecNewTangItrSelecTtl.hide(); f_algoSecNewTangItrSelec.hide(); f_algoSecNewTangIncrSelecTtl.hide()
        f_algoSecNewTangIncrSelec.hide(); f_algoSecNewMaxDimTtl.hide(); f_algoSecNewMaxDim.hide()
        f_algoBroydenCountFlag.hide(); f_algoBroydenCountFlagValue.hide()


def broydenCheckChange(changeState, f_algoBroydenCountFlagValue):
    if algoBroydenCountFlag.isChecked():
        f_algoBroydenCountFlagValue.setDisabled(False)
    else:
        f_algoBroydenCountFlagValue.setDisabled(True)


def testTypeChange(changeState, f_testNormUnblcTolTtl, f_testNormUnblcTol, f_testNormUnblcPFlagSelec):
    if analysisTestSelec.currentText() == "Fixed Number of Iterations":
        f_testNormUnblcPFlagSelec.model().item(4).setEnabled(False)
        f_testNormUnblcTolTtl.setDisabled(True)
        f_testNormUnblcTol.setDisabled(True)
    else:
        f_testNormUnblcPFlagSelec.model().item(4).setEnabled(True)
        f_testNormUnblcTolTtl.setDisabled(False)
        f_testNormUnblcTol.setDisabled(False)


def rayleighCheckChange(checkState, f_RayleighAlphaMTtl, f_RayleighAlphaM, f_RayleighBetaKTtl, f_RayleighBetaK, f_RayleighBetaKinitTtl,
                        f_RayleighBetaKinit, f_RayleighBetaKcmmtTtl, f_RayleighBetaKcmmt):
    if (RayleighFlag.isEnabled()) and (RayleighFlag.isChecked()):
        f_RayleighAlphaMTtl.setDisabled(False); f_RayleighAlphaM.setDisabled(False); f_RayleighBetaKTtl.setDisabled(False)
        f_RayleighBetaK.setDisabled(False); f_RayleighBetaKinitTtl.setDisabled(False); f_RayleighBetaKinit.setDisabled(False)
        f_RayleighBetaKcmmtTtl.setDisabled(False); f_RayleighBetaKcmmt.setDisabled(False)
    else:
        f_RayleighAlphaMTtl.setDisabled(True); f_RayleighAlphaM.setDisabled(True); f_RayleighBetaKTtl.setDisabled(True)
        f_RayleighBetaK.setDisabled(True); f_RayleighBetaKinitTtl.setDisabled(True); f_RayleighBetaKinit.setDisabled(True)
        f_RayleighBetaKcmmtTtl.setDisabled(True); f_RayleighBetaKcmmt.setDisabled(True)


def addWidgetFixed(f_layout, f_width, f_widget, strtRow, strtCol, expndRow, expndCol, frmtWdgt):
    f_layout.addWidget(f_widget, strtRow, strtCol, expndRow, expndCol, frmtWdgt)
    f_widget.setFixedWidth(f_width)


def getGMrecord(f_rcrTimeStepTtl, f_rcrTimeStep, f_rcrDirTtl, f_rcrDir, f_frVbrDurTtl, f_frVbrDur, f_sclFctrTtl,
                f_sclFctr, f_sclMotionGFlag):
    GMpath = QtGui.QFileDialog.getOpenFileName(parent=mWindow, caption="Select Ground Motion Record File", filter='Ground motion files (*.*)')
    print(GMpath)
    if GMpath:
        GMfile = QtCore.QFile(GMpath)
        if GMfile.open(QtCore.QIODevice.ReadOnly):
            txtEditorDialog = QtGui.QDialog()
            txtEditorDialog.setWindowTitle("Select ground motion file")
            txtEditorDialogLayout = QGridLayout()
            accelRecords = QtCore.QTextStream(GMfile)
            accelRecords = accelRecords.readAll()
            txtEditor = CodeEditor(accelRecords)
            txtEditorDialogLayout.addWidget(txtEditor, 0, 0, 6, 10, Qt.AlignVCenter)

            strtLnTtl = QLabel("Start Line No.")
            strtLn = QLineEdit()
            dataInLnTtl = QLabel("No. of Data in Line")
            dataInLn = QLineEdit()
            endLnTtl = QLabel("End Line No.")
            endLn = QLineEdit()

            okGMBtn = QPushButton('OK', widget)
            okGMBtn.setToolTip('Click to accept ground motion records')
            okGMBtn.clicked.connect(lambda: processGMRecords(accelRecords, strtLn, dataInLn, endLn, f_rcrTimeStepTtl,
                                                             f_rcrTimeStep, f_rcrDirTtl, f_rcrDir, f_frVbrDurTtl,
                                                             f_frVbrDur, f_sclFctrTtl, f_sclFctr, f_sclMotionGFlag,
                                                             txtEditorDialog))
            okGMBtn.resize(okGMBtn.sizeHint())
            okGMBtn.move(100, 80)

            cancelGMBtn = QPushButton('Cancel', widget)
            cancelGMBtn.setToolTip('Click to cancel')
            cancelGMBtn.clicked.connect(lambda: cancelGMProcess(txtEditorDialog, GMfile))
            cancelGMBtn.resize(cancelGMBtn.sizeHint())
            cancelGMBtn.move(100, 80)

            txtEditorDialogLayout.addWidget(strtLnTtl, 0, 10, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
            strtLnTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
            txtEditorDialogLayout.addWidget(strtLn, 1, 10, 1, 1, Qt.AlignVCenter)
            txtEditorDialogLayout.addWidget(dataInLnTtl, 2, 10, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
            dataInLnTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
            txtEditorDialogLayout.addWidget(dataInLn, 3, 10, 1, 1, Qt.AlignVCenter)
            txtEditorDialogLayout.addWidget(endLnTtl, 4, 10, 1, 1, Qt.AlignBottom | Qt.AlignLeft)
            endLnTtl.setFont(QFont('Open Sans Semibold', pointSize=7))
            txtEditorDialogLayout.addWidget(endLn, 5, 10, 1, 1, Qt.AlignVCenter)
            txtEditorDialogLayout.addWidget(okGMBtn, 6, 4, 1, 3, Qt.AlignVCenter)
            txtEditorDialogLayout.addWidget(cancelGMBtn, 6, 7, 1, 3, Qt.AlignVCenter)
            txtEditorDialog.setLayout(txtEditorDialogLayout)
            txtEditorDialog.setFixedHeight(200)
            if txtEditorDialog.exec_() == QtGui.QDialog.Accepted:
                txtEditorDialog.show()
            GMfile.close()


def processGMRecords(f_accelRecords, f_strtLn, f_dataInLn, f_endLn, f_rcrTimeStepTtl, f_rcrTimeStep, f_rcrDirTtl,
                     f_rcrDir, f_frVbrDurTtl, f_frVbrDur, f_sclFctrTtl, f_sclFctr, f_sclMotionGFlag, f_txtEditorDialog):
    global GMdata
    strt = int(f_strtLn.text())
    end = int(f_endLn.text())
    lines = f_accelRecords.splitlines()
    lines = lines[strt - 1: end]
    GMdata = []
    for lineCounter in np.arange(len(lines)):
        GMs = lines[lineCounter].split()
        dataInLnNum = 0
        for GMitems in GMs:
            dataInLnNum += 1
            if lineCounter == len(lines) - 1:
                if GMitems == "":
                    break
            else:
                if dataInLnNum > int(f_dataInLn.text()):
                    break
            GMdata.append(float(GMitems))

    f_rcrTimeStepTtl.setDisabled(False);
    f_rcrTimeStep.setDisabled(False);
    f_rcrDirTtl.setDisabled(False)
    f_rcrDir.setDisabled(False);
    f_frVbrDurTtl.setDisabled(False);
    f_frVbrDur.setDisabled(False)
    f_sclFctrTtl.setDisabled(False);
    f_sclFctr.setDisabled(False);
    f_sclMotionGFlag.setDisabled(False)
    if analysis.at[int(currentAnalysisItem), "DOF"] == "ux":
        f_rcrDir.setCurrentIndex(1)
    elif analysis.at[int(currentAnalysisItem), "DOF"] == "uy":
        f_rcrDir.setCurrentIndex(2)
    elif analysis.at[int(currentAnalysisItem), "DOF"] == "uz":
        f_rcrDir.setCurrentIndex(3)
    else:
        f_rcrDir.setCurrentIndex(0)
    f_txtEditorDialog.close()
    return GMdata

def cancelGMProcess(f_txtEditorDialog, f_GMfile):
    f_GMfile.close()
    f_txtEditorDialog.close()


class integratorDefaults(object):
    def __init__(self):
        super().__init__()

    def LCLoadFacts(self, f_integratorLClambda, f_integratorLClambdamin, f_integratorLClambdamax):
        f_integratorLClambdamin.setText(f_integratorLClambda.text())
        f_integratorLClambdamax.setText(f_integratorLClambda.text())

    def DCincr(self, f_integratorDCincr, f_integratorDCdeltaUmin, f_integratorDCdeltaUmax):
        f_integratorDCdeltaUmin.setText(f_integratorDCincr.text())
        f_integratorDCdeltaUmax.setText(f_integratorDCincr.text())

    def MUDNlambda(self, f_integratorMUDNdLambda1, f_integratorMUDNdminLambda, f_integratorMUDNdmaxLambda):
        f_integratorMUDNdminLambda.setText(f_integratorMUDNdLambda1.text())
        f_integratorMUDNdmaxLambda.setText(f_integratorMUDNdLambda1.text())

    def HHTAlpha(self, f_integratorHHTAlpha, f_integratorHHTGamma, f_integratorHHTBeta):
        f_integratorHHTGamma.setText(str(3 / 2 - float(f_integratorHHTAlpha.text())))
        f_integratorHHTBeta.setText(str(((2 - float(f_integratorHHTAlpha.text())) ** 2) / 4))


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.myeditor = editor

    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.myeditor.lineNumberAreaPaintEvent(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self, f_accelRecords):
        super().__init__()
        self.setPlainText(f_accelRecords)
        self.setFixedWidth(500)
        self.lineNumberArea = LineNumberArea(self)
        self.connect(self, SIGNAL('blockCountChanged(int)'), self.updateLineNumberAreaWidth)
        self.connect(self, SIGNAL('updateRequest(QRect,int)'), self.updateLineNumberArea)
        self.connect(self, SIGNAL('cursorPositionChanged()'), self.highlightCurrentLine)

        self.updateLineNumberAreaWidth(0)

    def lineNumberAreaWidth(self):
        digits = 1
        count = max(1, self.blockCount())
        while count >= 10:
            count /= 10
            digits += 1
        space = 3 + self.fontMetrics().width('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect();
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(),
                    self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        mypainter = QPainter(self.lineNumberArea)
        mypainter.fillRect(event.rect(), Qt.lightGray)
        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        # Just to make sure I use the right font
        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(blockNumber + 1)
                mypainter.setPen(Qt.black)
                mypainter.drawText(0, top, self.lineNumberArea.width(), height, Qt.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1

    def highlightCurrentLine(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(Qt.yellow).lighter(160)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)


def updPlt(f_sclFctr, f_sclMotionGFlag, f_rcrTimeStep, f_frVbrDur, f_GMfig, f_GMcanvas):
    if f_sclFctr.text() != "" and f_rcrTimeStep.text() != "":
        if f_sclMotionGFlag.isChecked():
            scaleFactor = 9.81
        else:
            scaleFactor = 1.0
        scaleFactor = scaleFactor * float(f_sclFctr.text())
        y = [gmdt * scaleFactor for gmdt in GMdata]
        x = []
        for item in np.arange(len(GMdata)):
            x.append(item * float(f_rcrTimeStep.text()))
        if float(f_frVbrDur.text()) > 0:
            nsteps = int(float(f_frVbrDur.text()) / float(f_rcrTimeStep.text()))
            for step in np.arange(nsteps):
                y.append(0)
                x.append(len(GMdata) * float(f_rcrTimeStep.text()) + step * float(f_rcrTimeStep.text()))
        f_GMfig.clear()
        ax = f_GMfig.add_subplot(111)
        ax.plot(x, y, '-')

    # refresh canvas
    f_GMcanvas.draw()


class dataTable(QTableWidget):
    def __init__(self, width, height, colNo):
        super().__init__()

        self.setFixedWidth(width)
        self.setFixedHeight(height)
        self.setColumnCount(colNo)
        self.setRowCount(100)
        self.setHorizontalHeaderLabels(('Node', 'FX', 'FY', 'FZ', 'MX', 'MY', 'MZ'))

        pointLoadDialog = QtGui.QDialog()
        pointLoadDialog.setWindowTitle("Define point loads")
        pointLoadDialogLayout = QGridLayout()
        pointLoadDialogLayout.addWidget(self, 0, 0, 1, 4)

        BtnWidget = QWidget()
        pointLoadDialogBtnLayout = QGridLayout()
        okPLBtn = QPushButton('OK', widget)
        okPLBtn.setToolTip('Click to accept ground motion records')
        okPLBtn.clicked.connect(lambda: self.processPointLoads())
        okPLBtn.resize(okPLBtn.sizeHint())
        okPLBtn.move(100, 80)

        cancelPLBtn = QPushButton('Cancel', widget)
        cancelPLBtn.setToolTip('Click to cancel')
        cancelPLBtn.clicked.connect(pointLoadDialog.close)
        cancelPLBtn.resize(cancelPLBtn.sizeHint())
        cancelPLBtn.move(100, 80)

        pointLoadDialogBtnLayout.addWidget(okPLBtn, 0, 0)
        pointLoadDialogBtnLayout.addWidget(cancelPLBtn, 0, 1)
        BtnWidget.setLayout(pointLoadDialogBtnLayout)
        pointLoadDialogLayout.addWidget(BtnWidget, 1, 1, 1, 2)

        pointLoadDialog.setLayout(pointLoadDialogLayout)
        pointLoadDialog.setFixedWidth(820)
        pointLoadDialog.setFixedHeight(570)
        if pointLoadDialog.exec_() == QtGui.QDialog.Accepted:
            pointLoadDialog.show()

    def processPointLoads(self):
        print("hey")


def get_analysisEdEntries(changeState):
    print("hey")


def recorderDialog():
    recDialog = QtGui.QDialog()
    recDialog.setWindowTitle("Define Recorders")
    if recDialog.exec_() == QtGui.QDialog.Accepted:
        recDialog.show()


def runAnalysis():
    import writeOpenSeesTCL_func
    writeOpenSeesTCL_func.impNode = node
    writeOpenSeesTCL_func.impWall = wall
    writeOpenSeesTCL_func.impElement = element
    writeOpenSeesTCL_func.impPolygon = polygon
    writeOpenSeesTCL_func.impMaterial = material
    writeOpenSeesTCL_func.impFixConstraint = fixConstraint
    writeOpenSeesTCL_func.impW2wConstraint = w2wConstraint
    writeOpenSeesTCL_func.impF2wConstraint = f2wConstraint
    writeOpenSeesTCL_func.impAnalysis = analysis
    writeOpenSeesTCL_func.projectName = mainActions.prjName
    writeOpenSeesTCL_func.wrtOPSfunc()

@pyqtSlot()
def dummy():
    print("yeeeah")

# Create an PyQT4 application object.
app = QApplication(sys.argv)
app.setWindowIcon(QtGui.QIcon('appIcon.png'))

# The QWidget widget is the base class of all user interface objects in PyQt4.
mWindow = QMainWindow()
widget = QWidget()
# mWindow.setCentralWidget(widget)
grid = QGridLayout()
materialWidget = QWidget()

# Set window size.
# mWindow.setFixedSize(400, 120)

# Set window title
mWindow.setWindowTitle("Masonry Interface")

# ###########################################
# Create Menu bar  ## mwindow
# ###########################################
mainMenu = mWindow.menuBar()
mainMenu.setNativeMenuBar(False)
fileMenu = mainMenu.addMenu('File')
editMenu = mainMenu.addMenu('Edit')
defineMenu = mainMenu.addMenu('Define')
assignMenu = mainMenu.addMenu('Assign')
analysisMenu = mainMenu.addMenu('Analysis')
displayMenu = mainMenu.addMenu('Display')
helpMenu = mainMenu.addMenu('Help')

# Some of the menu items are grayed out at the startup
editMenu.setDisabled(True)
defineMenu.setDisabled(True)
assignMenu.setDisabled(True)
analysisMenu.setDisabled(True)
displayMenu.setDisabled(True)

# Add buttons to the menu
# # File Menu
newFileMenu = QAction(QtGui.QIcon('newFileIcon.png'), 'New File...', mWindow)
newFileMenu.setShortcut('Ctrl+N')
newFileMenu.setStatusTip('New file from scratch')
newFileMenu.triggered.connect(mWindow.close)
fileMenu.addAction(newFileMenu)

openFileMenu = QAction(QtGui.QIcon('openFileIcon.png'), 'Open...', mWindow)
openFileMenu.setShortcut('Ctrl+O')
openFileMenu.setStatusTip('Open an existing Tremuri or OpenSees file')
openFileMenu.triggered.connect(lambda: mainActions().openFile())
fileMenu.addAction(openFileMenu)

saveFileMenu = QAction(QtGui.QIcon('saveFileIcon.png'), 'Save', mWindow)
saveFileMenu.setShortcut('Ctrl+S')
saveFileMenu.setStatusTip('Save and overwrite an existing file')
saveFileMenu.triggered.connect(mWindow.close)
fileMenu.addAction(saveFileMenu)

saveAsFileMenu = QAction(QtGui.QIcon('saveAsFileIcon.png'), 'Save as...', mWindow)
saveAsFileMenu.setStatusTip('Save as a new file')
saveAsFileMenu.triggered.connect(mWindow.close)
fileMenu.addAction(saveAsFileMenu)

importFileMenu = QAction(QtGui.QIcon('importFileIcon.png'), 'Import...', mWindow)
importFileMenu.setStatusTip('Export the results or rendered building')
importFileMenu.triggered.connect(handleExport)
fileMenu.addAction(importFileMenu)

exportFileMenu = QAction(QtGui.QIcon('exportFileIcon.png'), 'Export...', mWindow)
exportFileMenu.setStatusTip('Export the results or rendered building')
exportFileMenu.triggered.connect(handleExport)
fileMenu.addAction(exportFileMenu)

printFileMenu = QAction(QtGui.QIcon('printIcon.png'), 'Print...', mWindow)
printFileMenu.setShortcut('Ctrl+P')
printFileMenu.setStatusTip('Print the results')
printFileMenu.triggered.connect(lambda: mainActions().handlePrint(mWindow))
fileMenu.addAction(printFileMenu)

exitFileMenu = QAction(QtGui.QIcon('exitIcon.png'), 'Exit', mWindow)
exitFileMenu.setShortcut('Ctrl+Q')
exitFileMenu.setStatusTip('Terminate the program')
exitFileMenu.triggered.connect(mWindow.close)
fileMenu.addAction(exitFileMenu)

# Some of the menu items are grayed out at the startup
saveFileMenu.setDisabled(True)
saveAsFileMenu.setDisabled(True)
printFileMenu.setDisabled(True)
exportFileMenu.setDisabled(True)

# # Edit Menu
gridDataEditMenu = QAction(QtGui.QIcon('editGridIcon.png'), 'Grid Data...', mWindow)
gridDataEditMenu.setShortcut('Ctrl+G')
gridDataEditMenu.setStatusTip('Edit grid data')
gridDataEditMenu.triggered.connect(mWindow.close)
editMenu.addAction(gridDataEditMenu)

windowLayoutEditMenu = QAction(QtGui.QIcon('layoutIcon.png'), 'Window Layout...', mWindow)
windowLayoutEditMenu.setStatusTip('Edit layout of the main window')
windowLayoutEditMenu.triggered.connect(mWindow.close)
editMenu.addAction(windowLayoutEditMenu)

preferencesEditMenu = QAction(QtGui.QIcon('editPreferencesIcon.png'), 'Preferences...', mWindow)
preferencesEditMenu.setShortcut('Ctrl+Alt+S')
preferencesEditMenu.setStatusTip('Set general settings')
preferencesEditMenu.triggered.connect(mWindow.close)
editMenu.addAction(preferencesEditMenu)

# # Define Menu
materialDefineMenu = QAction('Materials...', mWindow)
materialDefineMenu.setStatusTip('Edit material data')
materialDefineMenu.triggered.connect(materialDialog)
defineMenu.addAction(materialDefineMenu)

sectionPropertiesDefineMenu = QAction('Section Properties...', mWindow)
sectionPropertiesDefineMenu.setStatusTip('Edit section data')
sectionPropertiesDefineMenu.triggered.connect(mWindow.close)
defineMenu.addAction(sectionPropertiesDefineMenu)

massSourceDefineMenu = QAction('Mass Source...', mWindow)
massSourceDefineMenu.setStatusTip('Edit mass source and distribution data')
massSourceDefineMenu.triggered.connect(mWindow.close)
defineMenu.addAction(massSourceDefineMenu)

analysisDefineMenu = QAction('Analysis...', mWindow)
analysisDefineMenu.setStatusTip('Edit analysis data')
analysisDefineMenu.triggered.connect(analysisDialog)
defineMenu.addAction(analysisDefineMenu)

recordersDefineMenu = QAction('recorders...', mWindow)
recordersDefineMenu.setStatusTip('Edit recorder data')
recordersDefineMenu.triggered.connect(recorderDialog)
defineMenu.addAction(recordersDefineMenu)

# # Assign Menu
constraintAssignMenu = QAction('Assign Constraints...', mWindow)
constraintAssignMenu.setStatusTip('Assign Constraints to the Selected Nodes')
constraintAssignMenu.triggered.connect(mWindow.close)
assignMenu.addAction(constraintAssignMenu)

restraintAssignMenu = QAction('Assign Restraints...', mWindow)
restraintAssignMenu.setStatusTip('Assign Restraints to the Selected Nodes...')
restraintAssignMenu.triggered.connect(restraintDialog)
assignMenu.addAction(restraintAssignMenu)

# # Analyze Menu
analyzeAnalysisMenu = QAction(QtGui.QIcon('analysisOptIcon.png'), 'Analysis Options...', mWindow)
analyzeAnalysisMenu.setStatusTip('Set analysis pereferences and run analysis')
analyzeAnalysisMenu.triggered.connect(mWindow.close)
analysisMenu.addAction(analyzeAnalysisMenu)

runAnalysisMenu = QAction(QtGui.QIcon('runIcon.png'), 'Run Analysis', mWindow)
runAnalysisMenu.setShortcut('F5')
runAnalysisMenu.setStatusTip('Run the preselected analyses')
runAnalysisMenu.triggered.connect(lambda: runAnalysis())
analysisMenu.addAction(runAnalysisMenu)

# # Display Menu
deformedShapeDisplayMenu = QAction('Deformed Shape...', mWindow)
deformedShapeDisplayMenu.setStatusTip('Show the structural deformed shape under various analysis cases')
deformedShapeDisplayMenu.triggered.connect(mWindow.close)
displayMenu.addAction(deformedShapeDisplayMenu)

THresultDisplayMenu = QAction('Time-History Results...', mWindow)
THresultDisplayMenu.setStatusTip('Display time-history results')
THresultDisplayMenu.triggered.connect(mWindow.close)
displayMenu.addAction(THresultDisplayMenu)

tableDisplayMenu = QAction('Tables...', mWindow)
tableDisplayMenu.setShortcut('Ctrl+T')
tableDisplayMenu.setStatusTip('Display results in table format')
tableDisplayMenu.triggered.connect(mWindow.close)
displayMenu.addAction(tableDisplayMenu)

# # Help Menu
helpHelpMenu = QAction(QtGui.QIcon('helpIcon.png'), 'Help...', mWindow)
helpHelpMenu.setShortcut('F1')
helpHelpMenu.setStatusTip('Help')
helpHelpMenu.triggered.connect(mWindow.close)
helpMenu.addAction(helpHelpMenu)

documentationHelpMenu = QAction('Documentation', mWindow)
documentationHelpMenu.setStatusTip('Documentation file')
documentationHelpMenu.triggered.connect(mWindow.close)
helpMenu.addAction(documentationHelpMenu)

aboutHelpMenu = QAction('About...', mWindow)
aboutHelpMenu.setStatusTip('About')
aboutHelpMenu.triggered.connect(mWindow.close)
helpMenu.addAction(aboutHelpMenu)

# #############################################
# Design the main window  widget
# #############################################
# Add input fields
prjTitle = QLabel("Project Name")
projectName = QLineEdit()
btchFName = QLabel("Batch File Name")
batchFileName = QLineEdit()
tclFName = QLabel("TCL File Name")
tclFileName = QLineEdit()

applyBtn = QPushButton('Apply', widget)
applyBtn.setToolTip('Click to Apply')
applyBtn.clicked.connect(dummy)
applyBtn.resize(applyBtn.sizeHint())
applyBtn.move(100, 80)

grid.addWidget(prjTitle, 1, 0)
grid.addWidget(projectName, 1, 1, 1, 3)
grid.addWidget(btchFName, 2, 0)
grid.addWidget(batchFileName, 2, 1)
grid.addWidget(tclFName, 2, 2)
grid.addWidget(tclFileName, 2, 3)
grid.addWidget(applyBtn, 3, 0)

# #############################################
# Design the define material window  ## materialWidget
# #############################################
materialWidget.setWindowTitle("Define Material Properties")
widget.setLayout(grid)
mWindow.showMaximized()
sys.exit(app.exec_())

if appMode == "Tremuri":
    import drawModelVTK
