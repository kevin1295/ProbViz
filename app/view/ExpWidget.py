from qfluentwidgets import (FlowLayout, Pivot, qrouter)
from PyQt5.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

class expWidget(QWidget):
    def __init__(self, name, descriptionInterface=None, experimentInterface=None, parent=None):
        super().__init__(parent)
        self.setObjectName(name)
        
        self.pivot = Pivot(self)
        self.stackedWidget = QStackedWidget(self)
        self.vBoxLayout = QVBoxLayout(self)
        
        if descriptionInterface:
            self.descriptionInterface = descriptionInterface
        else:
            self.descriptionInterface = QLabel('Empty Description', self)
        if experimentInterface:
            self.experimentInterface = experimentInterface
        else:
            self.experimentInterface = QLabel('Empty Experiment', self)
        
        self.addSubInterface(self.descriptionInterface, 'description', '描述')
        self.addSubInterface(self.experimentInterface, 'experiment', '实验')
        
        self.vBoxLayout.addWidget(self.pivot, 0, Qt.AlignLeft)
        self.vBoxLayout.addWidget(self.stackedWidget)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        # StyleSheet.NAVIGATION_VIEW_INTERFACE.apply(self)
        
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.stackedWidget.setCurrentWidget(self.descriptionInterface)
        self.pivot.setCurrentItem(self.descriptionInterface.objectName())
        
        qrouter.setDefaultRouteKey(self.stackedWidget, self.descriptionInterface.objectName())
        
    def addSubInterface(self, widget: QLabel, objectName, text):
        widget.setObjectName(objectName)
        widget.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget)
        )

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.pivot.setCurrentItem(widget.objectName())
        qrouter.push(self.stackedWidget, widget.objectName())
    
    