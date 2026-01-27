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
from scipy.stats import poisson
import numpy as np

from .ExpWidget import expWidget
from ..common.MarkdownKatex import MarkdownKaTeXWidget
from ..common.config import cfg

class PoissonDistribution(expWidget):
    
    desc = r"""
# 泊松分布简介
如果随机变量 $X$ 的概率分布为
$$
P(X=k) = \cfrac{\lambda^k}{k!} e^{-\lambda}, \quad k=0,1,2,\ldots,n
$$
则称 $X$ 服从参数为 $\lambda$ 的泊松分布，记为 $X \sim P(\lambda)$

泊松分布常用于描述单位时间内随机事件发生的次数。例如，单位时间内某路口通过的车辆数、单位时间内某电话交换机收到的呼叫数等，都是泊松分布的具体应用。
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
                
                self.lambda_ = 10
                self.update_plot(self.lambda_)
                
            def update_plot(self, lambda_=None):
                if lambda_ is None:
                    lambda_ = self.lambda_
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                
                # begin core plotting code
                x_max = max(10, int(lambda_ + 4 * np.sqrt(lambda_)))
                x = np.arange(0, x_max + 1)
                pmf = poisson.pmf(x, lambda_)
                ax.bar(x, pmf)
                # end core plotting code
                
                ax.patch.set_alpha(0.1)
                if isDarkTheme():
                    for spine in ax.spines.values():
                        spine.set_color('white')
                    ax.tick_params(colors='white', which='both')
                    ax.set_xlabel('$k$', color='white')
                    ax.set_ylabel('$P(X=k)$', color='white')
                    ax.set_title(f'泊松分布 $P(\\lambda={lambda_:.3f})$ 的概率质量函数', color='white')
                    ax.grid(True, alpha=0.3)
                else:
                    for spine in ax.spines.values():
                        spine.set_color('black')
                    ax.tick_params(colors='black', which='both')
                    ax.set_xlabel('$k$', color='black')
                    ax.set_ylabel('$P(X=k)$', color='black')
                    ax.set_title(f'泊松分布 $P(\\lambda={lambda_:.3f})$ 的概率质量函数', color='black')
                    ax.grid(True, alpha=0.7)
                
                self.figure.tight_layout()
                self.canvas.draw()
        def __init__(self, parent=None):
            super().__init__(parent)
            self.content_layout = FlowLayout(self)

            # lambda 参数设置
            self.lambda_label = BodyLabel("λ（参数）：", self)
            self.lambda_spin = CompactSpinBox(self)
            self.lambda_spin.setRange(0, 20)
            self.lambda_spin.setValue(10)
            self.lambda_slider = Slider(Qt.Horizontal, self)
            self.lambda_slider.setRange(0, 20)
            self.lambda_slider.setSingleStep(1)
            self.lambda_slider.setValue(10)
            
            self.lambda_layout = QHBoxLayout()
            self.lambda_layout.addWidget(self.lambda_label)
            self.lambda_layout.addWidget(self.lambda_spin)
            self.lambda_layout.addWidget(self.lambda_slider)
            self.lambda_layout.setSpacing(10)
            self.lambda_widget = QWidget(self)
            self.lambda_widget.setLayout(self.lambda_layout)

            self.content_layout.addWidget(self.lambda_widget)
            
            # 同步 slider 和 spinbox
            self.lambda_slider.valueChanged.connect(self.lambda_spin.setValue)
            self.lambda_spin.valueChanged.connect(self.lambda_slider.setValue)

            # 绘图区域
            self.plot_widget = self.PlotWidget(self)
            self.content_layout.addWidget(self.plot_widget)
            
            # 连接信号更新图表
            self.lambda_spin.valueChanged.connect(lambda: self.plot_widget.update_plot(lambda_=self.lambda_spin.value()))
            cfg.themeChanged.connect(lambda: self.plot_widget.update_plot())
            
    def __init__(self, parent=None):
        
        descriptionInterface = MarkdownKaTeXWidget(parent=None)
        descriptionInterface.set_markdown(self.desc)
        
        experimentInterface = self.ExpInterface(parent=None)

        super().__init__('泊松分布', descriptionInterface=descriptionInterface, experimentInterface=experimentInterface, parent=parent)
        # descriptionInterface.setParent(self)