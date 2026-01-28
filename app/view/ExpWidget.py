from qfluentwidgets import (FlowLayout, Pivot, qrouter)
from PyQt5.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

class ExpWidget(QWidget):
    def __init__(self, name, descriptionFactory=None, experimentFactory=None, parent=None):
        super().__init__(parent)
        self.setObjectName(name)
        
        self.pivot = Pivot(self)
        self.stackedWidget = QStackedWidget(self)
        self.vBoxLayout = QVBoxLayout(self)
        
        self._descriptionFactory = descriptionFactory
        self._experimentFactory = experimentFactory
        self._descriptionInterface = None
        self._experimentInterface = None
        
        # 添加界面，使用懒加载逻辑
        self.addSubInterface('description', '描述')
        self.addSubInterface('experiment', '实验')
        
        self.vBoxLayout.addWidget(self.pivot, 0, Qt.AlignLeft)
        self.vBoxLayout.addWidget(self.stackedWidget)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        
        # 初始化时先添加描述占位符
        description_placeholder = QLabel('Loading Description...')
        self.stackedWidget.addWidget(description_placeholder)
        self.stackedWidget.setCurrentWidget(description_placeholder)
        self.pivot.setCurrentItem('description')

        qrouter.setDefaultRouteKey(self.stackedWidget, 'description')
        
        # 立即加载描述界面
        self.ensureDescriptionLoaded()
        
        # 连接信号
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)

    def ensureDescriptionLoaded(self):
        """确保描述界面已加载"""
        if self._descriptionInterface is None and self._descriptionFactory:
            self._descriptionInterface = self._descriptionFactory()
            # 获取当前占位符的索引
            for i in range(self.stackedWidget.count()):
                if self.stackedWidget.widget(i).text() == 'Loading Description...':
                    self.stackedWidget.removeWidget(self.stackedWidget.widget(i))
                    break
            self.stackedWidget.addWidget(self._descriptionInterface)
            self.stackedWidget.setCurrentWidget(self._descriptionInterface)

    def ensureExperimentLoaded(self):
        """确保实验界面已加载"""
        if self._experimentInterface is None and self._experimentFactory:
            # 先添加加载提示
            experiment_placeholder = QLabel('Loading Experiment...')
            self.stackedWidget.addWidget(experiment_placeholder)
            self.stackedWidget.setCurrentWidget(experiment_placeholder)
            
            # 创建实际界面
            self._experimentInterface = self._experimentFactory()
            
            # 替换占位符
            for i in range(self.stackedWidget.count()):
                if self.stackedWidget.widget(i).text() == 'Loading Experiment...':
                    self.stackedWidget.removeWidget(self.stackedWidget.widget(i))
                    break
            self.stackedWidget.addWidget(self._experimentInterface)
            self.stackedWidget.setCurrentWidget(self._experimentInterface)

    def addSubInterface(self, objectName, text):
        """添加子界面，使用懒加载"""
        self.pivot.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.switchToInterface(objectName)
        )

    def switchToInterface(self, objectName):
        """切换到指定界面，必要时加载组件"""
        if objectName == 'description':
            self.ensureDescriptionLoaded()
            self.stackedWidget.setCurrentWidget(self.descriptionInterface)
        elif objectName == 'experiment':
            self.ensureExperimentLoaded()
            self.stackedWidget.setCurrentWidget(self.experimentInterface)

    @property
    def descriptionInterface(self):
        """获取描述界面（首次访问时创建）"""
        if self._descriptionInterface is None:
            self.ensureDescriptionLoaded()
        return self._descriptionInterface

    @property
    def experimentInterface(self):
        """获取实验界面（首次访问时创建）"""
        if self._experimentInterface is None:
            self.ensureExperimentLoaded()
        return self._experimentInterface

    def onCurrentIndexChanged(self, index):
        """当索引改变时更新pivot和路由"""
        widget = self.stackedWidget.widget(index)
        self.pivot.setCurrentItem(widget.objectName())
        qrouter.push(self.stackedWidget, widget.objectName())