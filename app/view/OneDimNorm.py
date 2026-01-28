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
from scipy.stats import norm
import numpy as np

from .ExpWidget import ExpWidget
from ..common.MarkdownKatex import MarkdownKaTeXWidget
from ..common.config import cfg

class OneDimNorm(ExpWidget):
    
    desc = r"""
# 一维正态分布简介
如果随机变量 $X$ 的概率密度为
$$
f(x) = \cfrac{1}{\sqrt{2\pi}\sigma} e^{- \frac{(x-\mu)^2}{2\sigma^2}}, \quad -\infty < x < \infty
$$
其中 $\sigma>0$，则称 $X$ 服从参数为 $\mu, \sigma^2$ 的正态分布。简记为 $\mathcal{N}(\mu, \sigma^2)$。

正态分布无论在实践中还是在理论上都非常重要。测量误差和很多产品的物理指标（如产品的长度、宽度、质量指标……）都可以看作服从正态分布。
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
                
                self.layout = QVBoxLayout(self)
                self.layout.addWidget(self.canvas)
                self.setLayout(self.layout)
                
                self.mu = 0
                self.sigma = 1
                
                self.update_plot(self.mu, self.sigma)
                self.parent().windowResizeSignal.connect(self.onParentResize)
                
            def onParentResize(self, parent_width, parent_height):
                available_width = max(parent_width - 100, 400)
                max_width = 800
                width = min(available_width, max_width)
                height = width * 3 / 4
                
                self.figure.set_size_inches(width / 100, height / 100)
                self.canvas.draw()
            
            def update_plot(self, mu=None, sigma=None):
                if mu is None:
                    mu = self.mu
                if sigma is None:
                    sigma = self.sigma
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                
                # begin core plotting code
                x = np.linspace(-10, 10, 1000)  # Fixed x range
                pdf = norm.pdf(x, mu, sigma)
                
                # Find maximum possible y value for any normal distribution in our x range
                # For comparison, we calculate the max possible pdf value when sigma is smallest
                max_y = norm.pdf(mu, mu, 0.1)  # Maximum possible value for any normal distribution
                y_max = min(max_y, 1.0)  # Cap the y-axis to make visualization better
                
                ax.plot(x, pdf, linewidth=2)
                
                # Add coordinate axes
                ax.axhline(0, color='black', linewidth=0.8)  # x-axis
                ax.axvline(0, color='black', linewidth=0.8)  # y-axis
                
                # Add grid lines
                ax.grid(True, alpha=0.3)
                
                # Set fixed axis limits
                ax.set_xlim(-10, 10)
                ax.set_ylim(0, y_max)
                # end core plotting code
                
                ax.patch.set_alpha(0.1)
                if isDarkTheme():
                    for spine in ax.spines.values():
                        spine.set_color('white')
                    ax.tick_params(colors='white', which='both')
                    ax.set_xlabel('$x$', color='white')
                    ax.set_ylabel('$f(x)$', color='white')
                    ax.set_title(f'正态分布 $N(\\mu={mu:.3f}, \\sigma^2={sigma**2:.3f})$ 的概率密度函数', color='white')
                else:
                    for spine in ax.spines.values():
                        spine.set_color('black')
                    ax.tick_params(colors='black', which='both')
                    ax.set_xlabel('$x$', color='black')
                    ax.set_ylabel('$f(x)$', color='black')
                    ax.set_title(f'正态分布 $N(\\mu={mu:.3f}, \\sigma^2={sigma**2:.3f})$ 的概率密度函数', color='black')
                
                self.figure.tight_layout()
                self.canvas.draw()

        def __init__(self, parent=None):
            super().__init__(parent)
            self.flow_layout = FlowLayout(self)
            
            self.control_container = QWidget()
            self.control_container.setFixedWidth(400)
            self.control_layout = QGridLayout(self.control_container)

            # mu 参数设置
            self.mu_label = BodyLabel("μ（均值）：", self)
            self.mu_spin = CompactDoubleSpinBox(self)
            self.mu_spin.setRange(-10, 10)
            self.mu_spin.setSingleStep(0.01)
            self.mu_spin.setValue(0)
            self.mu_slider = Slider(Qt.Horizontal, self)
            self.mu_slider.setRange(-1000, 1000)
            self.mu_slider.setSingleStep(1)
            self.mu_slider.setValue(0)
            
            self.control_layout.addWidget(self.mu_label, 0, 0)
            self.control_layout.addWidget(self.mu_spin, 0, 1)
            self.control_layout.addWidget(self.mu_slider, 0, 2)
            
            # sigma 参数设置
            self.sigma_label = BodyLabel("σ（标准差）：", self)
            self.sigma_spin = CompactDoubleSpinBox(self)
            self.sigma_spin.setRange(0.1, 5)
            self.sigma_spin.setSingleStep(0.01)
            self.sigma_spin.setValue(1)
            self.sigma_slider = Slider(Qt.Horizontal, self)
            self.sigma_slider.setRange(10, 500)
            self.sigma_slider.setSingleStep(1)
            self.sigma_slider.setValue(100)
            
            self.control_layout.addWidget(self.sigma_label, 1, 0)
            self.control_layout.addWidget(self.sigma_spin, 1, 1)
            self.control_layout.addWidget(self.sigma_slider, 1, 2)
            
            self.flow_layout.addWidget(self.control_container)
            
            # 绘图区域
            self.plot_widget = self.PlotWidget(self)
            self.flow_layout.addWidget(self.plot_widget)
            
            # 同步 slider 和 spinbox
            self.mu_spin.valueChanged.connect(
                lambda: self.mu_slider.setValue(int(self.mu_spin.value() * 100))
            )
            self.mu_slider.valueChanged.connect(
                lambda: self.mu_spin.setValue(self.mu_slider.value() / 100)
            )
            
            self.sigma_spin.valueChanged.connect(
                lambda: self.sigma_slider.setValue(int(self.sigma_spin.value() * 100))
            )
            self.sigma_slider.valueChanged.connect(
                lambda: self.sigma_spin.setValue(self.sigma_slider.value() / 100)
            )

            # 连接信号更新图表
            self.mu_spin.valueChanged.connect(lambda: self.plot_widget.update_plot(mu=self.mu_spin.value(), sigma=self.sigma_spin.value()))
            self.sigma_spin.valueChanged.connect(lambda: self.plot_widget.update_plot(mu=self.mu_spin.value(), sigma=self.sigma_spin.value()))
            
            cfg.themeChanged.connect(lambda: self.plot_widget.update_plot())
            
        def resizeEvent(self, event):
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
            experimentInterface = self.ExpInterface()
            scroll_area.setWidget(experimentInterface)
            scroll_area.setWidgetResizable(True)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            FluentStyleSheet.NAVIGATION_INTERFACE.apply(scroll_area)
            return scroll_area

        super().__init__(
            '一维正态分布',
            descriptionFactory=create_description_interface,
            experimentFactory=create_experiment_interface,
            parent=parent
        )