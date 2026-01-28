from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QSizePolicy, QGridLayout
)
from qfluentwidgets import (
    FlowLayout, Slider, CompactDoubleSpinBox, CompactSpinBox, isDarkTheme,
    TitleLabel, BodyLabel, ScrollArea, FluentStyleSheet
)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from scipy.stats import norm, binom
import numpy as np

from .ExpWidget import ExpWidget
from ..common.MarkdownKatex import MarkdownKaTeXWidget
from ..common.config import cfg

class CentralLimitTheorem(ExpWidget):
    
    desc = r"""
# 中心极限定理简介
（列维-林德伯格定理）设 $X_1, X_2, \ldots, X_n, \ldots$ 为 i.i.d. 序列，
数学期望均为 $\mu$，方差 $\sigma^2 > 0$，则当 $n$ 充分大时，
$\sum_{i=1}^n X_i$ 近似服从 $\mathcal{N}(n \mu, n \sigma^2)$。
特别地，若 $X \sim \mathcal{B}(n, p)$，则当 $n$ 充分大时，
标准化变量 $\cfrac{X-np}{\sqrt{np(1-p)}}$ 近似服从标准正态分布 $\mathcal{N}(0, 1)$。
"""

    class ExpInterface(ScrollArea):
        windowResizeSignal = pyqtSignal(int, int)
        
        class PlotWidget(QWidget):
            def __init__(self, parent=None):
                super().__init__(parent)
                
                self.figure = Figure(figsize=(8, 6), dpi=100)
                self.figure.patch.set_facecolor("none")
                self.figure.patch.set_edgecolor("none")
                self.canvas = FigureCanvas(self.figure)
                self.canvas.setStyleSheet("background: transparent;")
                self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                
                self._layout = QVBoxLayout(self)
                self._layout.addWidget(self.canvas)
                self.setLayout(self._layout)
                
                self.n = 50
                self.p = 0.5
                
                self.update_plot(self.n, self.p)
                self.parent().windowResizeSignal.connect(self.onParentResize)
                
            def onParentResize(self, parent_width, parent_height):
                """响应父控件大小变化"""
                available_width = max(parent_width - 100, 400)
                max_width = 800
                width = min(available_width, max_width)
                height = width * 3 / 4  # 3:4 宽高比
                
                self.figure.set_size_inches(width / 100, height / 100)
                self.canvas.draw()
                
            def update_plot(self, n=None, p=None):
                if n is None:
                    n = self.n
                if p is None:
                    p = self.p
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                
                mu = n * p
                sigma = np.sqrt(n * p * (1 - p))
                x = np.arange(max(0, int(mu - 4*sigma)), int(mu + 4*sigma) + 1)
                pmf_binom = binom.pmf(x, n, p)
                x_continuous = np.linspace(x[0], x[-1], 1000)
                pdf_normal = norm.pdf(x_continuous, loc=mu, scale=sigma)
                ax.bar(x, pmf_binom, width=0.8, label=f'二项分布 B(n={n}, p={p})', alpha=0.6, color='blue', align='center')
                ax.plot(x_continuous, pdf_normal, label=f'正态分布 N(μ={mu:.1f}, σ²={sigma**2:.1f})', color='red', linewidth=2)
                
                ax.patch.set_alpha(0.1)
                ax.legend()
                
                if isDarkTheme():
                    for spine in ax.spines.values():
                        spine.set_color('white')
                    ax.tick_params(colors='white', which='both')
                    ax.set_xlabel('$k$', color='white')
                    ax.set_ylabel('概率密度', color='white')
                    ax.set_title(f'中心极限定理演示: 二项分布 vs 正态分布', color='white')
                    ax.grid(True, alpha=0.3)
                else:
                    for spine in ax.spines.values():
                        spine.set_color('black')
                    ax.tick_params(colors='black', which='both')
                    ax.set_xlabel('$k$', color='black')
                    ax.set_ylabel('概率密度', color='black')
                    ax.set_title(f'中心极限定理演示: 二项分布 vs 正态分布', color='black')
                    ax.grid(True, alpha=0.7)
                
                self.figure.tight_layout()
                self.canvas.draw()

        def __init__(self, parent=None):
            super().__init__(parent)
            self.flow_layout = FlowLayout(self)
            
            self.control_container = QWidget()
            self.control_container.setFixedWidth(400)
            self.controls_layout = QGridLayout(self.control_container)
            
            # n 参数设置
            self.n_label = BodyLabel("n（实验次数）：", self)
            self.n_spin = CompactSpinBox(self)
            self.n_spin.setRange(10, 200)
            self.n_spin.setValue(50)
            self.n_slider = Slider(Qt.Horizontal, self)
            self.n_slider.setRange(10, 200)
            self.n_slider.setSingleStep(1)
            self.n_slider.setValue(50)
            
            self.controls_layout.addWidget(self.n_label, 0, 0)
            self.controls_layout.addWidget(self.n_spin, 0, 1)
            self.controls_layout.addWidget(self.n_slider, 0, 2)
            
            # p 参数设置
            self.p_label = BodyLabel("p（成功概率）：", self)
            self.p_spin = CompactDoubleSpinBox(self)
            self.p_spin.setRange(0.01, 0.99)
            self.p_spin.setSingleStep(0.01)
            self.p_spin.setValue(0.5)
            self.p_slider = Slider(Qt.Horizontal, self)
            self.p_slider.setRange(1, 99)
            self.p_slider.setSingleStep(1)
            self.p_slider.setValue(50)

            self.controls_layout.addWidget(self.p_label, 1, 0)
            self.controls_layout.addWidget(self.p_spin, 1, 1)
            self.controls_layout.addWidget(self.p_slider, 1, 2)
            
            self.flow_layout.addWidget(self.control_container)
            
            # 绘图区域
            self.plot_widget = self.PlotWidget(self)
            self.flow_layout.addWidget(self.plot_widget)
            
            # 连接信号
            self.n_spin.valueChanged.connect(self.n_slider.setValue)
            self.n_slider.valueChanged.connect(self.n_spin.setValue)
            self.p_spin.valueChanged.connect(
                lambda: self.p_slider.setValue(self.p_spin.value() * 100)
            )
            self.p_slider.valueChanged.connect(
                lambda: self.p_spin.setValue(self.p_slider.value() / 100)
            )
            
            self.n_spin.valueChanged.connect(lambda: self.plot_widget.update_plot(n=self.n_spin.value(), p=self.p_spin.value()))
            self.p_spin.valueChanged.connect(lambda: self.plot_widget.update_plot(n=self.n_spin.value(), p=self.p_spin.value()))
            
            cfg.themeChanged.connect(lambda: self.plot_widget.update_plot())

        def resizeEvent(self, event):
            """当ExpInterface大小改变时，发送信号给PlotWidget调整大小"""
            super().resizeEvent(event)
            current_size = event.size()
            self.windowResizeSignal.emit(current_size.width(), current_size.height())
            event.accept()

    def __init__(self, parent=None):
        # 创建工厂函数用于懒加载
        def create_description_interface():
            descriptionInterface = MarkdownKaTeXWidget()
            descriptionInterface.set_markdown(self.desc)
            return descriptionInterface

        def create_experiment_interface():
            scroll_area = ScrollArea()
            experimentInterface = CentralLimitTheorem.ExpInterface()
            scroll_area.setWidget(experimentInterface)
            scroll_area.setWidgetResizable(True)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            FluentStyleSheet.NAVIGATION_INTERFACE.apply(scroll_area)
            return scroll_area

        super().__init__(
            '中心极限定理',
            descriptionFactory=create_description_interface,
            experimentFactory=create_experiment_interface,
            parent=parent
        )