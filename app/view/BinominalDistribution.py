from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy
)
from qfluentwidgets import (
    FlowLayout, Slider, CompactDoubleSpinBox, CompactSpinBox, isDarkTheme,
    TitleLabel, BodyLabel, ScrollArea, VBoxLayout
)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from scipy.stats import binom
import numpy as np

from .ExpWidget import expWidget
from ..common.MarkdownKatex import MarkdownKaTeXWidget
from ..common.config import cfg

class BinominalDistribution(expWidget):
    
    desc = """
# 二项分布简介
如果随机变量 $X$ 的概率分布为
$$
P(X=k) = C_{n}^{k} p^k (1-p)^{n-k}, \quad k=0,1,2,\ldots,n
$$
则称 $X$ 服从参数为 $n$ 和 $p$ 的二项分布，记为 $X \sim B(n,p)$

$n$ 重伯努利实验就是二项分布的试验背景。现实中有放回的摸球模型，产品检验中抽得次品的概率模型等，都是二项分布的具体应用。
"""
    
    class ExpInterface(QWidget):
        
        class PlotWidget(QWidget):
            def __init__(self, parent=None):
                super().__init__(parent)
                
                self.figure = Figure(figsize=(6, 4), dpi=100)
                self.figure.patch.set_facecolor("none")
                self.figure.patch.set_edgecolor("none")
                self.canvas = FigureCanvas(self.figure)
                self.canvas.setStyleSheet("background: transparent;")
                self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                
                self.layout = QVBoxLayout(self)
                self.layout.addWidget(self.canvas)
                self.setLayout(self.layout)
                
                self.n = 10
                self.p = 0.5
                
                self.update_plot(self.n, self.p)
                
            def update_plot(self, n=None, p=None):
                if n is None:
                    n = self.n
                if p is None:
                    p = self.p
                self.figure.clear()
                
                ax = self.figure.add_subplot(111)
                x = np.arange(0, n+1)
                pmf = binom.pmf(x, n, p)
                ax.bar(x, pmf)
                ax.patch.set_alpha(0.0)

                if isDarkTheme():
                    for spine in ax.spines.values():
                        spine.set_color('white')
                    ax.tick_params(colors='white', which='both')
                    ax.set_xlabel('$k$', color='white')
                    ax.set_ylabel('$P(X=k)$', color='white')
                    ax.set_title(f'二项分布 $B(n={n}, p={p})$ 的概率质量函数', color='white')
                    ax.grid(True, alpha=0.3)
                else:
                    for spine in ax.spines.values():
                        spine.set_color('black')
                    ax.tick_params(colors='black', which='both')
                    ax.set_xlabel('$k$', color='black')
                    ax.set_ylabel('$P(X=k)$', color='black')
                    ax.set_title(f'二项分布 $B(n={n}, p={p})$ 的概率质量函数', color='black')
                    ax.grid(True, alpha=0.7)
                
                self.figure.tight_layout()
                self.canvas.draw()
        def __init__(self, parent=None):
            super().__init__(parent)
            self.content_layout = FlowLayout(self)
            
            # n 参数设置
            # self.n_label = MarkdownKaTeXWidget(self)
            # self.n_label.set_markdown("$n$（实验次数）：")
            # self.n_label.set_font_size(14)
            # self.n_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            # self.n_label.setFixedWidth(200)
            # self.n_label.setFixedHeight(100)
            self.n_label = BodyLabel("n（实验次数）：", self)
            self.n_spin = CompactSpinBox(self)
            self.n_spin.setRange(1, 100)
            self.n_spin.setValue(10)
            self.n_slider = Slider(Qt.Horizontal, self)
            self.n_slider.setRange(1, 100)
            self.n_slider.setSingleStep(1)
            self.n_slider.setValue(10)
            
            self.n_layout = QHBoxLayout()
            self.n_layout.addWidget(self.n_label)
            self.n_layout.addWidget(self.n_spin)
            self.n_layout.addWidget(self.n_slider)
            self.n_layout.setSpacing(10)
            self.n_widget = QWidget(self)
            self.n_widget.setLayout(self.n_layout)
            
            self.content_layout.addWidget(self.n_widget)
            
            # p 参数设置
            # self.p_label = MarkdownKaTeXWidget(self)
            # self.p_label.set_markdown("$p$（成功概率）：")
            # self.p_label.set_font_size(14)
            # self.p_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            # self.p_label.setFixedWidth(200)
            # self.p_label.setFixedHeight(100)
            self.p_label = BodyLabel("p（成功概率）：", self)
            self.p_spin = CompactDoubleSpinBox(self)
            self.p_spin.setRange(0, 1)
            self.p_spin.setSingleStep(0.01)
            self.p_spin.setValue(0.5)
            self.p_slider = Slider(Qt.Horizontal, self)
            self.p_slider.setRange(0, 100)
            self.p_slider.setSingleStep(0.01)
            self.p_slider.setValue(50)

            self.p_layout = QHBoxLayout()
            self.p_layout.addWidget(self.p_label)
            self.p_layout.addWidget(self.p_spin)
            self.p_layout.addWidget(self.p_slider)
            self.p_layout.setSpacing(10)
            self.p_widget = QWidget(self)
            self.p_widget.setLayout(self.p_layout)
            
            self.content_layout.addWidget(self.p_widget)
            
            # 同步 slider 和 spinbox
            self.n_spin.valueChanged.connect(self.n_slider.setValue)
            self.n_slider.valueChanged.connect(self.n_spin.setValue)
            self.p_spin.valueChanged.connect(
                lambda: self.p_slider.setValue(self.p_spin.value() * 100)
            )
            self.p_slider.valueChanged.connect(
                lambda: self.p_spin.setValue(self.p_slider.value() / 100)
            )

            # 绘图区域
            self.plot_widget = self.PlotWidget(self)
            self.content_layout.addWidget(self.plot_widget)
            
            # 连接信号更新图表
            self.n_spin.valueChanged.connect(lambda: self.plot_widget.update_plot(n=self.n_spin.value(), p=self.p_spin.value()))
            self.p_spin.valueChanged.connect(lambda: self.plot_widget.update_plot(n=self.n_spin.value(), p=self.p_spin.value()))
            
            cfg.themeChanged.connect(lambda: self.plot_widget.update_plot())
            
    def __init__(self, parent=None):
        
        descriptionInterface = MarkdownKaTeXWidget(parent=None)
        descriptionInterface.set_markdown(self.desc)
        
        experimentInterface = self.ExpInterface(parent=None)

        super().__init__('二项分布', descriptionInterface=descriptionInterface, experimentInterface=experimentInterface, parent=parent)
        # descriptionInterface.setParent(self)