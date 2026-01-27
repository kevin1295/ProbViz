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
        self.setMicaEffectEnabled(False) # disable mica effect for webengineview transparency issue
        
        self.homeInterface = Widget('导航', self)
        self.empirical_distribution = EmpiricalDistribution(self)
        self.binomial_distribution = BinominalDistribution(self)
        self.poisson_distribution = PoissonDistribution(self)
        self.poisson_theorem = PoissonTheorem(self)
        self.central_limit_theorem = Widget('中心极限定理', self)
        self.consistency_of_point_estimation = Widget('点估计的相合性', self)
        self.two_types_of_errors = Widget('假设检验两类错误', self)
        self.one_dim_norm = Widget('一维正态曲线', self)
        self.two_dim_norm = Widget('二维正态曲线', self)
        self.coin_tossing_experiment = Widget('投币实验', self)
        self.continuous_pdf = Widget('连续型随机变量概率分布', self)
        self.discrete_pdf = Widget('离散型随机变量概率分布', self)
        self.settings = SettingsInterface(self)

        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, '导航')
        self.addSubInterface(self.empirical_distribution, FIF.ALBUM, '经验分布')
        self.addSubInterface(self.binomial_distribution, FIF.ALBUM, '二项分布')
        self.addSubInterface(self.poisson_distribution, FIF.ALBUM, '泊松分布')
        self.addSubInterface(self.poisson_theorem, FIF.ALBUM, '泊松定理')
        self.addSubInterface(self.central_limit_theorem, FIF.ALBUM, '中心极限定理')
        self.addSubInterface(self.consistency_of_point_estimation, FIF.ALBUM, '点估计的相合性')
        self.addSubInterface(self.two_types_of_errors, FIF.ALBUM, '假设检验两类错误')
        self.addSubInterface(self.one_dim_norm, FIF.ALBUM, '一维正态曲线')
        self.addSubInterface(self.two_dim_norm, FIF.ALBUM, '二维正态曲线')
        self.addSubInterface(self.coin_tossing_experiment, FIF.ALBUM, '投币实验')
        self.addSubInterface(self.continuous_pdf, FIF.ALBUM, '连续型随机变量概率分布')
        self.addSubInterface(self.discrete_pdf, FIF.ALBUM, '离散型随机变量概率分布')

        self.navigationInterface.addSeparator()
        # add custom widget to bottom
        # self.navigationInterface.addWidget(
        #     routeKey='avatar',
        #     widget=NavigationAvatarWidget('zhiyiYo', 'resource/shoko.png'),
        #     onClick=self.showMessageBox,
        #     position=NavigationItemPosition.BOTTOM,
        # )

        self.addSubInterface(self.settings, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM)

        # add badge to navigation item
        # item = self.navigationInterface.widget(self.binomial_distribution.objectName())
        # InfoBadge.attension(
        #     text=9,
        #     parent=item.parent(),
        #     target=item,
        #     position=InfoBadgePosition.NAVIGATION_ITEM
        # )

        # NOTE: enable acrylic effect
        # self.navigationInterface.setAcrylicEnabled(True)

        # disable pop animation
        # self.stackedWidget.setAnimationEnabled(False)

    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle('PyQt-Fluent-Widgets')

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

        # set the minimum window width that allows the navigation panel to be expanded
        # self.navigationInterface.setMinimumExpandWidth(900)
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