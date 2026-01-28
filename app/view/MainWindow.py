import sys

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout
from qfluentwidgets import (NavigationItemPosition, MessageBox, setTheme, Theme, FluentWindow,
                            NavigationAvatarWidget, qrouter, SubtitleLabel, setFont, InfoBadge,
                            InfoBadgePosition, FluentBackgroundTheme)
from qfluentwidgets import FluentIcon as FIF

from .BinominalDistribution import BinominalDistribution
from .EmpiricalDistribution import EmpiricalDistribution
from .PoissonDistribution import PoissonDistribution
from .PoissonTheorem import PoissonTheorem
from .CentralLimitTheorem import CentralLimitTheorem
from .Settings import SettingsInterface

class Widget(QWidget):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))

class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.setMicaEffectEnabled(False)
        
        # 只初始化必需的界面（主页和设置）
        self.homeInterface = Widget('导航', self)
        self.settings = SettingsInterface(self)
        
        # 定义其他界面的工厂函数
        self.interface_factories = {
            'empirical_distribution': lambda: EmpiricalDistribution(self),
            'binomial_distribution': lambda: BinominalDistribution(self),
            'poisson_distribution': lambda: PoissonDistribution(self),
            'poisson_theorem': lambda: PoissonTheorem(self),
            'central_limit_theorem': lambda: CentralLimitTheorem(self),
            'consistency_of_point_estimation': lambda: Widget('点估计的相合性', self),
            'two_types_of_errors': lambda: Widget('假设检验两类错误', self),
            'one_dim_norm': lambda: Widget('一维正态曲线', self),
            'two_dim_norm': lambda: Widget('二维正态曲线', self),
            'coin_tossing_experiment': lambda: Widget('投币实验', self),
            'continuous_pdf': lambda: Widget('连续型随机变量概率分布', self),
            'discrete_pdf': lambda: Widget('离散型随机变量概率分布', self),
        }
        
        # 存储已创建的界面
        self.created_interfaces = {
            'home': self.homeInterface,
            'settings': self.settings
        }

        self.initNavigation()
        self.initWindow()

    def getOrCreateInterface(self, key):
        """获取现有界面或创建新界面（懒加载）"""
        if key not in self.created_interfaces:
            self.created_interfaces[key] = self.interface_factories[key]()
            # 将新创建的界面添加到堆叠小部件
            self.stackedWidget.addWidget(self.created_interfaces[key])
        return self.created_interfaces[key]

    def initNavigation(self):
        # 直接添加已创建的界面
        self.addSubInterface(self.homeInterface, FIF.HOME, '导航')
        
        # 为其他界面创建懒加载代理
        self.addLazySubInterface('empirical_distribution', FIF.ALBUM, '经验分布')
        self.addLazySubInterface('binomial_distribution', FIF.ALBUM, '二项分布')
        self.addLazySubInterface('poisson_distribution', FIF.ALBUM, '泊松分布')
        self.addLazySubInterface('poisson_theorem', FIF.ALBUM, '泊松定理')
        self.addLazySubInterface('central_limit_theorem', FIF.ALBUM, '中心极限定理')
        self.addLazySubInterface('consistency_of_point_estimation', FIF.ALBUM, '点估计的相合性')
        self.addLazySubInterface('two_types_of_errors', FIF.ALBUM, '假设检验两类错误')
        self.addLazySubInterface('one_dim_norm', FIF.ALBUM, '一维正态曲线')
        self.addLazySubInterface('two_dim_norm', FIF.ALBUM, '二维正态曲线')
        self.addLazySubInterface('coin_tossing_experiment', FIF.ALBUM, '投币实验')
        self.addLazySubInterface('continuous_pdf', FIF.ALBUM, '连续型随机变量概率分布')
        self.addLazySubInterface('discrete_pdf', FIF.ALBUM, '离散型随机变量概率分布')

        self.navigationInterface.addSeparator()
        self.addSubInterface(self.settings, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM)

    def addLazySubInterface(self, key, icon, text):
        """添加懒加载子界面"""
        def load_and_show():
            interface = self.getOrCreateInterface(key)
            self.stackedWidget.setCurrentWidget(interface)
        
        # 添加导航项，点击时才创建界面
        self.navigationInterface.addItem(
            routeKey=key,
            icon=icon,
            text=text,
            onClick=load_and_show
        )
    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle('PyQt-Fluent-Widgets')

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

        # self.navigationInterface.raise_()
        # set the minimum window width that allows the navigation panel to be expanded
        self.navigationInterface.setMinimumExpandWidth(900)
        # self.navigationInterface.expand(useAni=False)

    def showMessageBox(self):
        w = MessageBox(
            '鸣谢🥰',
            '感谢UI框架开发者@zhiyiYo，可以考虑请作者喝一瓶快乐水🥤。您的支持就是作者开发和维护项目的动力🚀',
            self
        )
        w.yesButton.setText('来啦老弟')
        w.cancelButton.setText('下次一定')

        if w.exec():
            QDesktopServices.openUrl(QUrl("https://afdian.net/a/zhiyiYo"))


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec_()