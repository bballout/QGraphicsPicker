'''
Created on Aug 7, 2016

@author: belalballout
'''

from PySide import QtCore,QtGui
import sys
import math

#graphics component
class BoxItem(QtGui.QGraphicsItem):
    def __init__(self,posX,posY,width,height,label,command,penColor,penIndex,brushColor,brushIndex):
        super(BoxItem, self).__init__()
        self.posX = posX
        self.posY = posY
        self.width = width
        self.height = height
        self.label = label
        self.command = command
        self.penColor = penColor
        self.penIndex = penIndex
        self.brushColor = brushColor
        self.brushIndex = brushIndex
        self.setAcceptHoverEvents(True)
           
    def boundingRect(self):
        return QtCore.QRectF(self.posX,self.posY,self.width,self.height)

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
        painter.drawRoundedRect(self.posX,self.posY,self.width,self.height,5,5)
        painter.drawText(self.boundingRect(),QtCore.Qt.AlignCenter,self.label)
    
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
           
    def addBox(self,label = '',command = '',fill = 0,stroke  = 1,posX = 1,posY = 1,width = 10,height = 10):
        strokeRGB =  ColorPickerSlider.colorFromIndex(stroke)
        filRGB = ColorPickerSlider.colorFromIndex(fill)
        penColor = QtGui.QColor(strokeRGB[0],strokeRGB[1],strokeRGB[2])
        brushColor = QtGui.QColor(filRGB[0],filRGB[1],filRGB[2])
        item = BoxItem(posX,posY,width,height,label,command,penColor,stroke,brushColor,fill)
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
        self.scaleView(math.pow(2.0, -event.delta() / 240.0))
        
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
        boxTextLayout = QtGui.QVBoxLayout()
        boxTextWidget.setLayout(boxTextLayout)
        boxTextLabel = QtGui.QLabel('Label:')
        self.boxText = QtGui.QLineEdit('temp')
        boxCommandLabel = QtGui.QLabel('Command:')
        self.boxCommandText = QtGui.QTextEdit()

        textEditStyle = '''QTextEdit {border: 2px solid #8f8f91;border-radius: 6px;
                        background-color: rgb(85, 85, 85);
                        color: rgb(15, 195, 255);;
                        font:  small "Courier"}'''
        
        self.boxCommandText.setStyleSheet(textEditStyle)
        self.boxCommandText.setTabStopWidth(20)

        boxTextLayout.addWidget(boxTextLabel)
        boxTextLayout.addWidget(self.boxText)
        boxTextLayout.addWidget(boxCommandLabel)
        boxTextLayout.addWidget(self.boxCommandText)
        
        itemSizeLayout.addWidget(itemWidthWidget)
        itemSizeLayout.addWidget(itemHeightWidget)
        
        itemPosLayout.addWidget(itemPosXWidget)
        itemPosLayout.addWidget(itemPosYWidget)
        
        spinBoxLayout.addWidget(itemSizeWidget)
        spinBoxLayout.addWidget(itemPosWidget)
        
        self.mainLayout.addWidget(boxTextWidget)
        self.mainLayout.addWidget(optionsWidget)
        self.mainLayout.setSpacing(0)
        
class CentralWidget(QtGui.QWidget):
    def __init__(self,parent = None):
        super(CentralWidget, self).__init__(parent)
        self.mainLayout = QtGui.QVBoxLayout(objectName = 'mainLayout')
        self.setLayout(self.mainLayout)
        
        itemWidget = QtGui.QGroupBox()
        itemLayout = QtGui.QHBoxLayout()
        itemWidget.setLayout(itemLayout)
        
        self.itemAddButton = QtGui.QPushButton()
        self.itemAddButton.setText('Add')
        self.removeItemButton = QtGui.QPushButton()
        self.removeItemButton.setText('Remove')
        
        itemLayout.addWidget(self.itemAddButton)
        itemLayout.addWidget(self.removeItemButton)
        
        graphicsView = GraphicsView()
        self.scene = BoxScene()
        graphicsView.setScene(self.scene)
        graphicsView.setBackgroundBrush(QtGui.QBrush(QtCore.Qt.gray, QtCore.Qt.SolidPattern))
        
        self.mainLayout.addWidget(graphicsView)
        self.mainLayout.addWidget(itemWidget)
        
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
        centralLayout = QtGui.QHBoxLayout()
        self.centralWidget.setLayout(centralLayout)
 
        #menuBar = ToolBoxMenuBar(self)
        #self.setMenuBar(menuBar)
        self.setCentralWidget(self.centralWidget)
        self.setupDock()
        self.centralWidget.itemAddButton.clicked.connect(self.addItem)
        self.centralWidget.removeItemButton.clicked.connect(self.removeItem)
        
        self.centralWidget.scene.selectionChanged.connect(self.setOptions)
        
    def addItem(self):
        posX = self.itemOptions.itemPosXBox.value()
        posY = self.itemOptions.itemPosYBox.value()
        width = self.itemOptions.itemWidthBox.value()
        height = self.itemOptions.itemHeightBox.value()
        stroke = self.itemOptions.penColorPicker.slider.value()
        fill = self.itemOptions.brushColorPicker.slider.value()
        label = self.itemOptions.boxText.text()
        command = self.itemOptions.boxCommandText.toPlainText()
        self.centralWidget.scene.addBox(posX = posX,posY = posY,height = height, width = width,
                                        label = label,command = command,stroke = stroke,fill = fill)
    def removeItem(self):
        selectedItems = self.centralWidget.scene.selectedItems()
        for item in selectedItems:
            self.centralWidget.scene.removeItem(item)
        
    def setupDock(self):
        dock = QtGui.QDockWidget('Item Options', self)
        #dock.setMaximumWidth(400)
        dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.itemOptions = BoxItemOptionsWidget(dock)
        
        dock.setWidget(self.itemOptions)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
        
    def setOptions(self):
        try:
            selectedItem = self.centralWidget.scene.selectedItems()[-1]
            pos = selectedItem.pos()
            size =  selectedItem.boundingRect()
            label =  selectedItem.label 
            command =  selectedItem.command
            penIndex =  selectedItem.penIndex
            brushIndex = selectedItem.brushIndex
            
            self.itemOptions.itemPosXBox.setValue(pos.x())
            self.itemOptions.itemPosYBox.setValue(pos.y())
            self.itemOptions.itemWidthBox.setValue(size.width())
            self.itemOptions.itemHeightBox.setValue(size.height())
            self.itemOptions.boxText.setText(label) 
            self.itemOptions.boxCommandText.setText(command)
            self.itemOptions.penColorPicker.slider.setValue(penIndex)
            self.itemOptions.brushColorPicker.slider.setValue(brushIndex)
        except:
            pass
        
def main():
        app = QtGui.QApplication(sys.argv)
        fileD = GraphicMainWin()
        fileD.show()
        sys.exit(app.exec_())      

if __name__ == '__main__':
    main()
