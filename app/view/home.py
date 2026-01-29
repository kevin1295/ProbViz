from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel
)
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from qfluentwidgets import (
    ScrollArea, FluentStyleSheet, TextWrap, FluentIcon, IconWidget,
    CardWidget, FlowLayout, TitleLabel, CaptionLabel, BodyLabel, SubtitleLabel
)

class HomeSignalBus(QObject):
    """ Signal bus """

    switchToSampleCard = pyqtSignal(str, int)
    micaEnableChanged = pyqtSignal(bool)
    supportSignal = pyqtSignal()

signalBus = HomeSignalBus()

class HomeCard(CardWidget):

    def __init__(self, title, content, routeKey, index, parent=None):
        super().__init__(parent=parent)
        self.index = index
        self.routekey = routeKey

        FluentStyleSheet.CARD_WIDGET.apply(self)
        
        # self.iconWidget = IconWidget(icon, self)
        self.titleLabel = SubtitleLabel(title, self)
        self.contentLabel = CaptionLabel(TextWrap.wrap(content, 45, False)[0], self)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.setFixedSize(360, 90)
        # self.iconWidget.setFixedSize(48, 48)

        self.hBoxLayout.setSpacing(28)
        self.hBoxLayout.setContentsMargins(20, 0, 0, 0)
        self.vBoxLayout.setSpacing(2)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setAlignment(Qt.AlignVCenter)

        self.hBoxLayout.setAlignment(Qt.AlignVCenter)
        # self.hBoxLayout.addWidget(self.iconWidget)
        self.hBoxLayout.addLayout(self.vBoxLayout)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addWidget(self.contentLabel)
        self.vBoxLayout.addStretch(1)

        self.titleLabel.setObjectName('titleLabel')
        self.contentLabel.setObjectName('contentLabel')

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        signalBus.switchToSampleCard.emit(self.routekey, self.index)


class HomeInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.banner = QWidget(self)
        self.bannerLayout = QHBoxLayout(self.banner)
        self.bannerLayout.setContentsMargins(18, 48, 36, 0)
        self.bannerLayout.setSpacing(24)
        self.bannerIcon = IconWidget(FluentIcon.HOME, self.banner)
        self.bannerIcon.setFixedSize(48, 48)
        self.bannerLayout.addWidget(self.bannerIcon)
        self.bannerTitle = TitleLabel("欢迎使用概率分布实验系统", self.banner)
        self.bannerLayout.addWidget(self.bannerTitle)
        
        self.banner.setObjectName('titleLabel')
        
        self.view = ScrollArea(self)
        self.view.setObjectName('View')
        self.flowLayout = FlowLayout(self.view)
        
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(18, 0, 0, 36)
        self.vBoxLayout.setSpacing(40)
        self.vBoxLayout.addWidget(self.banner)
        self.vBoxLayout.addWidget(self.view)
        
        self.setObjectName('主页')
        self.setStyleSheet("background-color: rgba(255, 255, 255, 0); border: none;")
        
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.view.setWidgetResizable(True)
        
        self.flowLayout.addWidget(HomeCard('二项分布', '二项分布是一种离散概率分布，用于描述在n次独立实验中成功次数的概率。', 'binomial_distribution', 0))
        self.flowLayout.addWidget(HomeCard('泊松分布', '泊松分布是一种离散概率分布，用于描述在单位时间内随机事件发生的次数。', 'poisson_distribution', 1))
        self.flowLayout.addWidget(HomeCard('泊松定理', '泊松定理是泊松分布的一个重要性质，用于描述在单位时间内随机事件发生的次数的分布。', 'poisson_theorem', 2))
        self.flowLayout.addWidget(HomeCard('中心极限定理', '中心极限定理是指，当独立随机变量的数量足够多的时候，算术平均值会趋向于服从正态分布。', 'central_limit_theorem', 3))
        self.flowLayout.addWidget(HomeCard('点估计的一致性', '点估计的一致性是指，当样本量足够大时，样本均值会趋向于服从正态分布。', 'consistency_of_point_estimation', 4))
        self.flowLayout.addWidget(HomeCard('两种错误', '在统计中，两种错误分别是类型I错误和类型II错误。', 'two_types_of_errors', 5))
        self.flowLayout.addWidget(HomeCard('一元正态分布', '一元正态分布是一种连续概率分布，用于描述随机变量的分布。', 'one_dim_norm', 6))
        self.flowLayout.addWidget(HomeCard('二维正态分布', '二维正态分布是一种连续概率分布，用于描述两个随机变量的分布。', 'two_dim_norm', 7))
        self.flowLayout.addWidget(HomeCard('骰子实验', '投掷骰子并统计结果分布与可视化。', 'dice_rolling_experiment', 8))
        self.flowLayout.addWidget(HomeCard('硬币实验', '投掷硬币并统计结果分布与可视化。', 'coin_tossing_experiment', 9))
        self.flowLayout.addWidget(HomeCard('连续随机变量分布', '若干种常见的连续随机变量的分布函数。', 'continuous_pdf', 10))
        self.flowLayout.addWidget(HomeCard('离散随机变量分布', '若干种常见的离散随机变量的分布函数。', 'discrete_pdf', 11))