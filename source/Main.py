'''
Created on Aug 7, 2016

@author: belalballout
'''`

from PySide import QtCore,QtGui
import sys
import math

iconDir = './icons'

#adding comment here.

#graphics component
class BoxItem(QtGui.QGraphicsItem):
    def __init__(self,**kwargs):
        super(BoxItem, self).__init__()
        self.posX = kwargs.get('posX',0)
        self.posY = kwargs.get('posY',0)
        self.width = kwargs.get('width',20)
        self.height = kwargs.get('height',20)
        self.label = kwargs.get('label','temp')
        self.command = kwargs.get('command',None)
        self.penColor = kwargs['penColor']
        self.penIndex = kwargs['penIndex']
        self.brushColor = kwargs['brushColor']
        self.brushIndex = kwargs['brushIndex']
        self.type = kwargs.get('type','ellipse')
        self.setAcceptHoverEvents(True) 
         
    def boundingRect(self):
        return QtCore.QRectF(0,0,self.width,self.height)

    def paint(self, painter, option, widget):
        pen = QtGui.QPen()
        brushColor = self.brushColor
        penColor = self.penColor
        
        if option.state & QtGui.QStyle.State_MouseOver:
            pen.setColor(self.penColor)
            pen.setStyle(QtCore.Qt.CustomDashLine)
            pen.setDashPattern([4, 4])
            pen.setWidth(2)              
        if option.state & QtGui.QStyle.State_Selected:
            brushColor = self.brushColor.lighter(180)
            penColor = self.penColor.darker(200)
        pen.setColor(penColor)
        painter.setBrush(brushColor)
        painter.setPen(pen)
        if self.type == 'rect':
            painter.drawRect(0,0,self.width,self.height)
        elif self.type == 'roundRect':
            painter.drawRoundedRect(0,0,self.width,self.height,5,5)
        elif self.type == 'ellipse':
            rect = QtCore.QRect(0,0,self.width,self.height)
            painter.drawEllipse(rect)
                   
        painter.drawText(self.boundingRect(),QtCore.Qt.AlignCenter,self.label)
        
    def move(self):
        pointZero = QtCore.QPoint(0,0)
        point = QtCore.QPoint(self.posX,self.posY)
        self.setPos(pointZero)
        self.setPos(point)
        
    def mousePressEvent(self, event):
        self.update()
        QtGui.QGraphicsItem.mousePressEvent(self, event)
  
    def mouseReleaseEvent(self, event):
        self.update()
        QtGui.QGraphicsItem.mouseReleaseEvent(self, event)
        
    def hoverEnterEvent(self, event):
        QtGui.QGraphicsItem.hoverEnterEvent(self, event)
        self.update()

    def hoverMoveEvent(self, event):
        QtGui.QGraphicsItem.hoverMoveEvent(self, event)
        self.update()
  
    def hoverLeaveEvent(self, event):
        QtGui.QGraphicsItem.hoverLeaveEvent(self, event)
        self.update()

class BoxScene(QtGui.QGraphicsScene):
    def __init__(self,parent = None):
        super(BoxScene, self).__init__(parent)
        self.selectionChanged.connect(self.itemInfo)
        rect =  QtCore.QRect(0,0,0,0)
        self.setSceneRect(rect)
        self.drawBoundary()
           
    def addBox(self,label = '',command = '',fill = 0,stroke  = 1,posX = 1,posY = 1,width = 10,height = 10,type = 'rect'):
        strokeRGB =  ColorPickerSlider.colorFromIndex(stroke)
        filRGB = ColorPickerSlider.colorFromIndex(fill)
        penColor = QtGui.QColor(strokeRGB[0],strokeRGB[1],strokeRGB[2])
        brushColor = QtGui.QColor(filRGB[0],filRGB[1],filRGB[2])
        item = BoxItem(posX = posX,posY = posY,width = width,height = height,label = label,command = command,
                       penColor = penColor,penIndex = stroke,brushColor = brushColor,
                       brushIndex = fill,type = type)
        item.setPos(QtCore.QPoint(posX,posY))
        item.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        item.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
        self.addItem(item)
        
    def drawBoundary(self):
        rect = QtCore.QRect()
        rect.setWidth(300)
        rect.setHeight(500)
        point = QtCore.QPoint(-150,-250)
        rect.moveTo(point)
        boundary = QtGui.QGraphicsRectItem(rect)
        pen = QtGui.QPen(QtCore.Qt.black)
        boundary.setPen(pen)
        self.addItem(boundary)
        #boundary.setBrush()
        
    def itemInfo(self):
        #=======================================================================
        # selectedItems = self.selectedItems()
        # for item in selectedItems:
        #     print item
        #     print item.label
        #     print item.command
        #=======================================================================
        pass
            
class GraphicsView(QtGui.QGraphicsView):
    posSignal = QtCore.Signal(QtCore.QObject)
    def __init__(self,parent = None):
        super(GraphicsView, self).__init__(parent)
        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setRenderHint(QtGui.QPainter.TextAntialiasing)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setAlignment(QtCore.Qt.AlignJustify)
        
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtGui.QFrame.NoFrame)
        
        self.setMaxSize()
        self.centerOn(0, 0)
        
        self.VIEW_CENTER  = self.viewport().rect().center()
        self.VIEW_WIDTH  = self.viewport().rect().width()
        self.VIEW_HEIGHT  = self.viewport().rect().height()
        
        self._lastMousePos = QtCore.QPoint()
        self._panSpeed = 1.5
        self._scale = 1.0
        self._doPan = False
        self._selected = []
        
    def mousePressEvent(self,event):
        super(GraphicsView, self).mousePressEvent(event)
        if event.button() == QtCore.Qt.LeftButton:
            self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
            if  event.modifiers() == QtCore.Qt.ShiftModifier:
                for item in self._selected:
                    item.setSelected(True)
            elif event.modifiers() == QtCore.Qt.AltModifier:
                self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
                self._doPan = True
                for item in self._selected:
                    item.setSelected(True)
    
    def mouseReleaseEvent(self,event):
        super(GraphicsView, self).mouseReleaseEvent(event)
        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        if event.button() == QtCore.Qt.LeftButton:
            if event.modifiers() in  [QtCore.Qt.ShiftModifier,QtCore.Qt.AltModifier]:
                    for item in self._selected:
                        item.setSelected(True)
            
            if self.scene().selectedItems() and len(self.scene().selectedItems()) == 1:
                pos = self.scene().selectedItems()[0].pos()
                self.posSignal.emit(pos)
                print 'emiting...',pos.x(),pos.y()             

        self._doPan = False
        self._selected = self.scene().selectedItems()

          
    def mouseMoveEvent(self, event):
        if self._doPan:
            mouseDelta = self._lastMousePos -  event.pos()
            self.pan(mouseDelta)
        super(GraphicsView, self).mouseMoveEvent(event)
        self._lastMousePos = event.pos()
          
    def wheelEvent(self, event):
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.scaleView(math.pow(2.0, event.delta() / 240.0))
        
    def scaleView(self, scaleFactor):
        factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()
        if factor < 0.07 or factor > 100:
            return
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.scale(scaleFactor, scaleFactor)

    def pan(self, delta):        
        delta *= self._scale
        delta *= self._panSpeed
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        sceneRect = self.scene().sceneRect()
        self.scene().setSceneRect(self.sceneRect().x()+delta.x(), self.sceneRect().y()+delta.y(), sceneRect.width(), sceneRect.height())
        
    def setMaxSize(self):
        pass

#ui elements
class ColorPickerSlider(QtGui.QWidget):
    def __init__(self,parent = None,label = 'temp',colorIndex = 0):
        super(ColorPickerSlider,self).__init__(parent)
        self.colorIndex = colorIndex
        self.label = QtGui.QLabel(label)
        self.label.setMinimumWidth(40)

        self.layout = QtGui.QHBoxLayout()
        
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(30)
        self.slider.setValue(colorIndex)
        self.slider.setSingleStep(1)
        self.slider.setMinimumWidth(80)

        self.button = QtGui.QPushButton()
        self.button.setMaximumWidth(40)
        self.button.setMaximumHeight(40)
        
        self.slider.valueChanged.connect(self.buttonStyle)
        
        self.ic = [0,0,0]
        buttonStyle = self.buttonStyle(colorIndex)
        
        self.button.setStyleSheet(buttonStyle)

        self.layout.setSpacing(20)
        self.setLayout(self.layout)
        
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.slider)
        self.layout.addWidget(self.button)
        
    def buttonStyle(self,index):
        color = ColorPickerSlider.colorFromIndex(index)
        buttonStyle = '''QPushButton {
                        border: 2px solid #8f8f91;
                        border-radius: 6px;
                        background-color: rgb(%i, %i, %i);}'''%(color[0],color[1],color[2])
                        
        self.button.setStyleSheet(buttonStyle)
        return buttonStyle
    
    @property
    def indexColor(self):
        return self.indexColor

    @indexColor.setter
    def indexColor(self, value):
        self._indexColor = value
        
    @staticmethod       
    def colorFromIndex(index):
        indexColors = ([0,0,0],
                       [0.25,0.25,0.25],
                       [0.5,0.5,0.5],
                       [0.608,0,0.157],
                       [0,0.016,0.376],
                       [0,0,1],
                       [0,0.275,0.098],
                       [0.149,0,0.263],
                       [0.784,0,0.784],
                       [0.541,0.282,0.2],
                       [0.247,0.137,0.122],
                       [0.6,0.149,0],
                       [1,0,0],
                       [0,1,0],
                       [0,0.255,0.6],
                       [1,1,1],
                       [1,1,0],
                       [0.392,0.863,1],
                       [0.263,1,0.639],
                       [1,0.69,0.69],
                       [0.894,0.675,0.475],
                       [1,1,0.388],
                       [0,0.6,0.329],
                       [0.63,0.41391,0.189],
                       [0.62118,0.63,0.189],
                       [0.4095,0.63,0.189],
                       [0.189,0.63,0.3654],
                       [0.189,0.63,0.63],
                       [0.189,0.4051,0.63],
                       [0.43596,0.189,0.63],
                       [0.63,0.189,0.41391])
        
        ic = indexColors[index]
        ic[0] = ic[0]*255
        ic[1] = ic[1]*255
        ic[2] = ic[2]*255
        return ic
        
class BoxItemOptionsWidget(QtGui.QWidget):
    def __init__(self,parent = None):
        super(BoxItemOptionsWidget, self).__init__(parent)
        self.mainLayout = QtGui.QVBoxLayout(objectName = 'mainLayout')
        self.setLayout(self.mainLayout)

        colorPickerWidget = QtGui.QGroupBox('Color')
        colorPickerLayout = QtGui.QVBoxLayout()
        self.penColorPicker = ColorPickerSlider(parent = self,label = 'stroke',colorIndex = 0)
        self.brushColorPicker = ColorPickerSlider(parent = self,label = 'fill',colorIndex = 11)
        colorPickerLayout.addWidget(self.penColorPicker)
        colorPickerLayout.addWidget(self.brushColorPicker)
        colorPickerWidget.setLayout(colorPickerLayout)

        optionsWidget = QtGui.QWidget()
        optionsLayout = QtGui.QVBoxLayout()
        optionsWidget.setLayout(optionsLayout)
        
        spinBoxWidgets = QtGui.QGroupBox('Size/Position')
        spinBoxLayout = QtGui.QHBoxLayout()
        spinBoxWidgets.setLayout(spinBoxLayout)
        
        itemSizeWidget = QtGui.QWidget()
        itemSizeLayout = QtGui.QVBoxLayout()
        itemSizeWidget.setLayout(itemSizeLayout)
        
        itemWidthWidget = QtGui.QWidget()
        itemWidthLayout = QtGui.QHBoxLayout()
        itemWidthLayout.setSpacing(0)
        itemWidthWidget.setLayout(itemWidthLayout)
        self.itemWidthBox = QtGui.QSpinBox()
        self.itemWidthBox.setMinimum(20)
        self.itemWidthBox.setMaximum(1000)
        widthLabel = QtGui.QLabel('width:')
        itemWidthLayout.addWidget(widthLabel)
        itemWidthLayout.addWidget(self.itemWidthBox)
        
        itemHeightWidget = QtGui.QWidget()
        itemHeightLayout = QtGui.QHBoxLayout()
        itemHeightLayout.setSpacing(0)
        itemHeightWidget.setLayout(itemHeightLayout)
        self.itemHeightBox = QtGui.QSpinBox()
        self.itemHeightBox.setMinimum(20)
        self.itemHeightBox.setMaximum(1000)
        HeightLabel = QtGui.QLabel('height:')
        itemHeightLayout.addWidget(HeightLabel)
        itemHeightLayout.addWidget(self.itemHeightBox)
               
        itemPosWidget = QtGui.QWidget()
        itemPosLayout = QtGui.QVBoxLayout()
        itemPosWidget.setLayout(itemPosLayout)
        
        itemPosXWidget = QtGui.QWidget()
        itemPosXLayout = QtGui.QHBoxLayout()
        itemPosXLayout.setSpacing(0)
        itemPosXWidget.setLayout(itemPosXLayout)
        self.itemPosXBox = QtGui.QSpinBox()
        self.itemPosXBox.setMinimum(-9999)
        self.itemPosXBox.setMaximum(9999)
        PosXLabel = QtGui.QLabel('Position X:')
        itemPosXLayout.addWidget(PosXLabel)
        itemPosXLayout.addWidget(self.itemPosXBox)
        
        itemPosYWidget = QtGui.QWidget()
        itemPosYLayout = QtGui.QHBoxLayout()
        itemPosYLayout.setSpacing(0)
        itemPosYWidget.setLayout(itemPosYLayout)
        self.itemPosYBox = QtGui.QSpinBox()
        self.itemPosYBox.setMinimum(-9999)
        self.itemPosYBox.setMaximum(9999)
        PosYLabel = QtGui.QLabel('Position Y:')
        itemPosYLayout.addWidget(PosYLabel)
        itemPosYLayout.addWidget(self.itemPosYBox)
        
        optionsLayout.addWidget(colorPickerWidget)
        optionsLayout.addWidget(spinBoxWidgets)
        
        boxTextWidget = QtGui.QWidget()
        boxTextLayout = QtGui.QHBoxLayout()
        boxTextWidget.setLayout(boxTextLayout)
        typeLabel = QtGui.QLabel('Type')
        self.typeBox = QtGui.QComboBox()
        self.typeBox.addItem('rect')
        self.typeBox.addItem('roundRect')
        self.typeBox.addItem('ellipse')
        self.typeBox.addItem('polygon')
        boxTextLabel = QtGui.QLabel('Label:')
        self.boxText = QtGui.QLineEdit('temp')
        
        boxTextLayout.addWidget(typeLabel)
        boxTextLayout.addWidget(self.typeBox)
        boxTextLayout.addWidget(boxTextLabel)
        boxTextLayout.addWidget(self.boxText)
        
        boxCommandWidget = QtGui.QWidget()
        boxCommandLayout = QtGui.QVBoxLayout()
        boxCommandWidget.setLayout(boxCommandLayout)
        boxCommandLabel = QtGui.QLabel('Command:')
        self.boxCommandText = QtGui.QTextEdit()
        boxCommandLayout.addWidget(boxCommandLabel)
        boxCommandLayout.addWidget(self.boxCommandText)

        textEditStyle = '''QTextEdit {border: 2px solid #8f8f91;border-radius: 6px;
                        background-color: rgb(85, 85, 85);
                        color: rgb(15, 195, 255);;
                        font:  small "Courier"}'''
        
        self.boxCommandText.setStyleSheet(textEditStyle)
        self.boxCommandText.setTabStopWidth(20)
        
        itemSizeLayout.addWidget(itemWidthWidget)
        itemSizeLayout.addWidget(itemHeightWidget)
        
        itemPosLayout.addWidget(itemPosXWidget)
        itemPosLayout.addWidget(itemPosYWidget)
        
        spinBoxLayout.addWidget(itemSizeWidget)
        spinBoxLayout.addWidget(itemPosWidget)
        
        self.mainLayout.addWidget(boxTextWidget)
        self.mainLayout.addWidget(optionsWidget)
        self.mainLayout.addWidget(boxCommandWidget)
        self.mainLayout.setSpacing(0)
        
class CentralWidget(QtGui.QWidget):
    def __init__(self,parent = None):
        super(CentralWidget, self).__init__(parent)
        self.mainLayout = QtGui.QVBoxLayout(objectName = 'mainLayout')
        self.setLayout(self.mainLayout)
        self.tabWidget = QtGui.QTabWidget()
        
        self.scenes = []
        self.graphicsViews = []
        self.mainLayout.addWidget(self.tabWidget)
        
    def addTab(self,label='temp'):
        tabItem = QtGui.QWidget()
        tabLayout = QtGui.QHBoxLayout()
        tabItem.setLayout(tabLayout)
        
        scene = BoxScene()
        self.scenes.append(scene)
        self.tabWidget.addTab(tabItem,label)
        graphicsView = GraphicsView() 
        self.graphicsViews.append(graphicsView)
        graphicsView.setBackgroundBrush(QtGui.QBrush(QtCore.Qt.gray, QtCore.Qt.SolidPattern))
        graphicsView.setScene(scene)
        tabLayout.addWidget(graphicsView)
        
class ToolBar(QtGui.QToolBar):
    def __init__(self,parent = None):
        super(ToolBar, self).__init__(parent)
        addItemIcon = QtGui.QIcon('%s/addItemIcon.png'%iconDir)
        removeItemIcon = QtGui.QIcon('%s/removeItemIcon.png'%iconDir)
        addSceneIcon = QtGui.QIcon('%s/addSceneIcon.png'%iconDir)
        removeSceneIcon = QtGui.QIcon('%s/removeSceneIcon.png'%iconDir)
        '''
        QWidgetAction *widgetAction = new QWidgetAction(this);
        widgetAction->setDefaultWidget(new QProgressBar(this));
        menubar.addAction(widgetAction);
        '''
        self.lineEditAction = QtGui.QWidgetAction(self)
        self.lineEdit = QtGui.QLineEdit()
        self.lineEdit.setMaximumWidth(125)
        self.lineEditAction.setDefaultWidget(self.lineEdit)
        tabNameLabel = QtGui.QLabel('Tab Name:')
        
        
        self.addItemAction = self.addAction(addItemIcon, 'Add Item')
        self.removeItemAction = self.addAction(removeItemIcon, 'Remove Item')
        self.addSeparator()
        self.addSceneAction = self.addAction(addSceneIcon,'Add Scene')
        self.removeSceneAction = self.addAction(removeSceneIcon,'Remove Scene')
        self.addWidget(tabNameLabel)
        self.addAction(self.lineEditAction)
        self.addSeparator()
        
        
        #self.removeSceneAction.setEnabled(False)
            
class GraphicMainWin(QtGui.QMainWindow):
    def __init__(self,parent = None):
        super(GraphicMainWin,self).__init__(parent)
        self.setupUI()
        
    def setupUI(self):
        self.setWindowTitle('Test Graphics')
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setGeometry(300,0,800,800)
        
        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)
        
        self.centralWidget = CentralWidget(self)
        self.addScene()
        centralLayout = QtGui.QHBoxLayout()
        self.centralWidget.setLayout(centralLayout)
 
        self.toolbar = ToolBar(self)
        self.addToolBar(QtCore.Qt.TopToolBarArea ,self.toolbar)
        
        self.toolbar.addItemAction.triggered.connect(self.addItem)
        self.toolbar.removeItemAction.triggered.connect(self.removeItem)
        self.toolbar.addSceneAction.triggered.connect(self.addScene) 
        self.toolbar.lineEdit.textChanged.connect(self.setTabName)
        
        self.centralWidget.tabWidget.currentChanged.connect(self.setTabField)  
        
        
        self.setCentralWidget(self.centralWidget)
        self.setupDock()
            
        self.itemOptions.itemWidthBox.valueChanged.connect(self.setItemWidth)
        self.itemOptions.itemHeightBox.valueChanged.connect(self.setItemHeight)
        self.itemOptions.itemPosXBox.valueChanged.connect(self.setItemPosX)
        self.itemOptions.itemPosYBox.valueChanged.connect(self.setItemPosY)
        self.itemOptions.typeBox.activated.connect(self.setItemShape)
        self.itemOptions.boxText.textChanged.connect(self.setItemLabel)
        self.itemOptions.penColorPicker.slider.valueChanged.connect(self.setItemStroke)
        self.itemOptions.brushColorPicker.slider.valueChanged.connect(self.setItemBrush)
        self.itemOptions.boxCommandText.textChanged.connect(self.setItemCommand)
        
    def addItem(self):
        currentScene = self.centralWidget.scenes[self.centralWidget.tabWidget.currentIndex()]
        posX = self.itemOptions.itemPosXBox.value()+10
        posY = self.itemOptions.itemPosYBox.value()+10
        width = self.itemOptions.itemWidthBox.value()
        height = self.itemOptions.itemHeightBox.value()
        stroke = self.itemOptions.penColorPicker.slider.value()
        fill = self.itemOptions.brushColorPicker.slider.value()
        label = self.itemOptions.boxText.text()
        typeStr = self.itemOptions.typeBox.currentText()
        command = self.itemOptions.boxCommandText.toPlainText()
        currentScene.addBox(posX = posX,posY = posY,height = height, width = width,
                                        label = label,command = command,stroke = stroke,fill = fill,
                                        type = typeStr)
    def removeItem(self):
        currentScene = self.centralWidget.scenes[self.centralWidget.tabWidget.currentIndex()]
        selectedItems = currentScene.selectedItems()
        for item in selectedItems:
            currentScene.removeItem(item)
            
    def addScene(self):
        self.centralWidget.addTab('label')
        for scene in self.centralWidget.scenes:
            scene.selectionChanged.connect(self.getOptions)
        for view in self.centralWidget.graphicsViews:
            view.posSignal.connect(self.setItemPos) 
            
    def setTabName(self,name):
        i = self.centralWidget.tabWidget.currentIndex()
        self.centralWidget.tabWidget.setTabText(i,name)
        
    def setTabField(self,index):
        tabName = self.centralWidget.tabWidget.tabText(index)
        self.toolbar.lineEdit.setText(tabName)
        
    def setupDock(self):
        dock = QtGui.QDockWidget('Item Options', self)
        #dock.setMaximumWidth(400)
        dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.itemOptions = BoxItemOptionsWidget(dock)
        
        dock.setWidget(self.itemOptions)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
        
    @QtCore.Slot(QtCore.QPoint)      
    def setItemPos(self,pos):
        print 'Slotted...',pos.x(),pos.y()
        self.itemOptions.itemPosXBox.setValue(pos.x())
        self.itemOptions.itemPosYBox.setValue(pos.y())

       
    def setItemWidth(self,width):
        selectedItem = self.centralWidget.scenes[self.centralWidget.tabWidget.currentIndex()].selectedItems()
        for item in selectedItem:
            item.width = width
            item.update()
            item.move()
            
    def setItemHeight(self,height):
        selectedItem = self.centralWidget.scenes[self.centralWidget.tabWidget.currentIndex()].selectedItems()
        for item in selectedItem:
            item.height = height
            item.update()
            item.move()
            
    def setItemPosX(self,posX):
        selectedItem = self.centralWidget.scenes[self.centralWidget.tabWidget.currentIndex()].selectedItems()
        for item in selectedItem:
            item.posX = posX
            item.move()
            
    def setItemPosY(self,posY):
        selectedItem = self.centralWidget.scenes[self.centralWidget.tabWidget.currentIndex()].selectedItems()
        for item in selectedItem:
            item.posY = posY
            item.move()
            
    def setItemShape(self,shapeIndex):
        selectedItem = self.centralWidget.scenes[self.centralWidget.tabWidget.currentIndex()].selectedItems()
        for item in selectedItem:
            shapes = ['rect','roundRect','ellipse','polygon']
            item.type =  shapes[shapeIndex]
            item.update()
            item.move()
            
    def setItemLabel(self,label):
        selectedItem = self.centralWidget.scenes[self.centralWidget.tabWidget.currentIndex()].selectedItems()
        for item in selectedItem:
            item.label = label
            item.update()
            
    def setItemStroke(self,colorIndex):
        selectedItem = self.centralWidget.scenes[self.centralWidget.tabWidget.currentIndex()].selectedItems()
        for item in selectedItem:
            color = ColorPickerSlider.colorFromIndex(colorIndex)
            item.penColor = QtGui.QColor(color[0],color[1],color[2])
            item.penIndex = colorIndex
            item.update()
            
    def setItemBrush(self,colorIndex):
        selectedItem = self.centralWidget.scenes[self.centralWidget.tabWidget.currentIndex()].selectedItems()
        for item in selectedItem:
            color = ColorPickerSlider.colorFromIndex(colorIndex)
            item.brushColor = QtGui.QColor(color[0],color[1],color[2])
            item.brushIndex = colorIndex
            item.update()
            
    def setItemCommand(self):
        selectedItem = self.centralWidget.scenes[self.centralWidget.tabWidget.currentIndex()].selectedItems()
        for item in selectedItem:
            item.command = self.itemOptions.boxCommandText.toPlainText()
           
    def getOptions(self):
        selectedItems = self.centralWidget.scenes[self.centralWidget.tabWidget.currentIndex()].selectedItems()
        if len(selectedItems) == 1:
            selectedItem = selectedItems[-1]
            pos = selectedItem.pos()
            size =  selectedItem.boundingRect()
            label =  selectedItem.label 
            command =  selectedItem.command
            penIndex =  selectedItem.penIndex
            brushIndex = selectedItem.brushIndex
            typeStr = selectedItem.type
            typeIndex = self.itemOptions.typeBox.findText(typeStr, QtCore.Qt.MatchFixedString)
            
            print 'point get at %i %i'%(pos.x(),pos.y())
    
            self.itemOptions.itemPosXBox.setValue(pos.x())
            self.itemOptions.itemPosYBox.setValue(pos.y())
            self.itemOptions.itemWidthBox.setValue(size.width())
            self.itemOptions.itemHeightBox.setValue(size.height())
            self.itemOptions.boxText.setText(label) 
            self.itemOptions.boxCommandText.setText(command)
            self.itemOptions.penColorPicker.slider.setValue(penIndex)
            self.itemOptions.brushColorPicker.slider.setValue(brushIndex)
            self.itemOptions.typeBox.setCurrentIndex(typeIndex)
            
def main():
        app = QtGui.QApplication(sys.argv)
        fileD = GraphicMainWin()
        fileD.show()
        sys.exit(app.exec_())      

if __name__ == '__main__':
    main()