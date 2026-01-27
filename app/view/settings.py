from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget
)
from qfluentwidgets import (
    TitleLabel, ScrollArea, ExpandLayout,
    FluentIcon, setTheme, FluentStyleSheet,
    HyperlinkCard, OptionsSettingCard, SettingCardGroup
)
from ..common.config import cfg

class SettingsInterface(ScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('Settings')
        
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)
        
        # title
        self.settingsTitle = TitleLabel("设置", self)
        
        # info
        self.infoGroup = SettingCardGroup("信息", self.scrollWidget)
        self.appInfo = HyperlinkCard(
            url="https://github.com/kevin1295/ProbViz",
            text="关于 ProbViz",
            icon=FluentIcon.INFO,
            title="ProbViz",
            content="ProbViz 是一个概率分布可视化软件",
            parent=self.infoGroup
        )
        self.frameInfo = HyperlinkCard(
            url="https://qfluentwidgets.com",
            text="关于 PyQt-Fluent-Widgets",
            icon=FluentIcon.CAFE,
            title="鸣谢 PyQt-Fluent-Widgets",
            content="发现 PyQt-Fluent-Widgets 的最佳实践",
            parent=self.infoGroup
        )
        
        # personalization
        self.personalGroup = SettingCardGroup("个性化", self.scrollWidget)
        self.themeSwitch = OptionsSettingCard(
            cfg.themeMode,
            FluentIcon.BRUSH,
            "应用主题",
            "调整你的应用外观",
            texts=["浅色", "深色", "跟随系统设置"],
            parent=self.personalGroup
        )
        self.zoomCard = OptionsSettingCard(
            cfg.dpiScale,
            FluentIcon.ZOOM,
            "界面缩放",
            "调整控件和字体的大小",
            texts=[
                "100%", "125%", "150%", "175%", "200%",
                "应用系统设置"
            ],
            parent=self.personalGroup
        )
        
        # initWidget
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingsTitle.setObjectName('settingLabel')
        FluentStyleSheet.NAVIGATION_INTERFACE.apply(self)
        
        self.expandLayout.addWidget(self.settingsTitle)
        self.infoGroup.addSettingCard(self.appInfo)
        self.infoGroup.addSettingCard(self.frameInfo)
        self.expandLayout.addWidget(self.infoGroup)
        self.personalGroup.addSettingCard(self.themeSwitch)
        self.personalGroup.addSettingCard(self.zoomCard)
        self.expandLayout.addWidget(self.personalGroup)
        
        cfg.themeChanged.connect(setTheme)

