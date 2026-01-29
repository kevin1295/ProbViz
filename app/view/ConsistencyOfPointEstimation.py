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

class ConsistencyOfPointEstimation(ExpWidget):
    
    desc = r"""
# 点估计的相合性
设 $\hat \theta$ 为总体（样本）分布的（一维或多维）未知参数，$\hat \theta$ 为 $\theta$ 的一个估计，
当样本容量 $n \to \infty$ 时，$\hat \theta$ 依概率收敛与 $\theta$ ，即对任意的 $\varepsilon > 0$
$$
\lim_{n \to \infty} P\left(|\hat \theta - \theta| \geq \varepsilon\right) = 0
$$
则 $\hat \theta$ 为 $\theta$ 的相合估计，又称一致估计。

本实验演示用样本均值作为正态总体期望的点估计时的相合性。
演示中加入了动态调整模拟试验的次数，对小样本情形模拟了更多次试验，目的是平衡计算效率和统计稳定性。
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
                self.n = 30
                
                self.update_plot(self.mu, self.sigma, self.n)
                self.parent().windowResizeSignal.connect(self.onParentResize)
                
            def onParentResize(self, parent_width, parent_height):
                """响应父控件大小变化"""
                available_width = max(parent_width - 100, 400)
                max_width = 800
                width = min(available_width, max_width)
                height = width * 3 / 4  # 3:4 宽高比
                
                self.figure.set_size_inches(width / 100, height / 100)
                self.canvas.draw()
            
            def update_plot(self, mu=None, sigma=None, n=None):
                if mu is None:
                    mu = self.mu
                if sigma is None:
                    sigma = self.sigma
                if n is None:
                    n = self.n
                
                self.figure.clear()
                
                sample_sizes = [2, n//4, n//2, n//4*3, n]
                sample_sizes = sorted(list(set([max(2, s) for s in sample_sizes])))
                
                axes = []
                for i in range(len(sample_sizes)):
                    ax = self.figure.add_subplot(len(sample_sizes), 1, i+1)
                    ax.patch.set_alpha(0.1)
                    axes.append(ax)
                
                x_range = 6 * sigma
                x_min = mu - x_range/2
                x_max = mu + x_range/2
                
                colors = ['red', 'green', 'blue', 'orange', 'purple']
                
                for i, size in enumerate(sample_sizes):
                    ax = axes[i]
                    
                    estimates = []
                    n_trials = min(1000, max(100, 2000 // size))
                    for _ in range(n_trials):
                        sample = np.random.normal(mu, sigma, size)
                        sample_mean = np.mean(sample)
                        estimates.append(sample_mean)
                    
                    ax.hist(estimates, bins=30, density=True, alpha=0.6, 
                        color=colors[i % len(colors)], edgecolor='black', linewidth=0.5,
                        label=f'n={size}')
                    
                    ax.axvline(mu, color='black', linestyle='--', linewidth=2, label=f'μ={mu}')
                    ax.set_xlim(x_min, x_max)
                    
                    if i == len(sample_sizes) - 1:
                        ax.set_xlabel('Sample Mean', fontsize=10)
                    else:
                        ax.set_xticklabels([])
                    ax.set_ylabel('密度', fontsize=10)
                    ax.legend(loc='upper right')
                    
                    if isDarkTheme():
                        for spine in ax.spines.values():
                            spine.set_color('white')
                        ax.tick_params(colors='white', which='both')
                        ax.set_ylabel('密度', color='white', fontsize=10)
                        if i == len(sample_sizes) - 1:
                            ax.set_xlabel('Sample Mean', color='white', fontsize=10)
                    else:
                        for spine in ax.spines.values():
                            spine.set_color('black')
                        ax.tick_params(colors='black', which='both')
                        ax.set_ylabel('密度', color='black', fontsize=10)
                        if i == len(sample_sizes) - 1:
                            ax.set_xlabel('Sample Mean', color='black', fontsize=10)
                
                suptitle = f'点估计的相合性: 样本均值随样本量增加趋于真实均值 (μ={mu}, σ={sigma})'
                if isDarkTheme():
                    self.figure.suptitle(suptitle, color='white')
                else:
                    self.figure.suptitle(suptitle, color='black')
                
                self.figure.tight_layout()
                self.canvas.draw()

        def __init__(self, parent=None):
            super().__init__(parent)
            self.flow_layout = FlowLayout(self)
            
            self.control_container = QWidget()
            self.control_container.setFixedWidth(400)
            self.controls_layout = QGridLayout(self.control_container)
            
            self.mu_label = BodyLabel("μ（总体均值）：", self)
            self.mu_spin = CompactDoubleSpinBox(self)
            self.mu_spin.setRange(-10, 10)
            self.mu_spin.setSingleStep(0.01)
            self.mu_spin.setValue(0)
            self.mu_slider = Slider(Qt.Horizontal, self)
            self.mu_slider.setRange(-1000, 1000)
            self.mu_slider.setSingleStep(1)
            self.mu_slider.setValue(0)

            self.controls_layout.addWidget(self.mu_label, 0, 0)
            self.controls_layout.addWidget(self.mu_spin, 0, 1)
            self.controls_layout.addWidget(self.mu_slider, 0, 2)
            
            self.sigma_label = BodyLabel("σ（总体标准差）：", self)
            self.sigma_spin = CompactDoubleSpinBox(self)
            self.sigma_spin.setRange(0.1, 10)
            self.sigma_spin.setSingleStep(0.1)
            self.sigma_spin.setValue(1)
            self.sigma_slider = Slider(Qt.Horizontal, self)
            self.sigma_slider.setRange(10, 1000)
            self.sigma_slider.setSingleStep(1)
            self.sigma_slider.setValue(100)

            self.controls_layout.addWidget(self.sigma_label, 1, 0)
            self.controls_layout.addWidget(self.sigma_spin, 1, 1)
            self.controls_layout.addWidget(self.sigma_slider, 1, 2)
            
            self.n_label = BodyLabel("n（最大样本量）：", self)
            self.n_spin = CompactSpinBox(self)
            self.n_spin.setRange(10, 1000)
            self.n_spin.setValue(30)
            self.n_slider = Slider(Qt.Horizontal, self)
            self.n_slider.setRange(10, 1000)
            self.n_slider.setSingleStep(1)
            self.n_slider.setValue(30)
            
            self.controls_layout.addWidget(self.n_label, 2, 0)
            self.controls_layout.addWidget(self.n_spin, 2, 1)
            self.controls_layout.addWidget(self.n_slider, 2, 2)
            
            self.flow_layout.addWidget(self.control_container)
            
            self.plot_widget = self.PlotWidget(self)
            self.flow_layout.addWidget(self.plot_widget)
                        
            self.mu_spin.valueChanged.connect(lambda value: self.mu_slider.setValue(value * 100))
            self.mu_slider.valueChanged.connect(lambda value: self.mu_spin.setValue(value / 100))
            
            self.sigma_spin.valueChanged.connect(
                lambda: self.sigma_slider.setValue(self.sigma_spin.value() * 100)
            )
            self.sigma_slider.valueChanged.connect(
                lambda: self.sigma_spin.setValue(self.sigma_slider.value() / 100)
            )
            
            self.n_spin.valueChanged.connect(self.n_slider.setValue)
            self.n_slider.valueChanged.connect(self.n_spin.setValue)
            
            self.mu_spin.valueChanged.connect(lambda: self.plot_widget.update_plot(
                mu=self.mu_spin.value(), 
                sigma=self.sigma_spin.value(), 
                n=self.n_spin.value()))
            self.sigma_spin.valueChanged.connect(lambda: self.plot_widget.update_plot(
                mu=self.mu_spin.value(), 
                sigma=self.sigma_spin.value(), 
                n=self.n_spin.value()))
            self.n_spin.valueChanged.connect(lambda: self.plot_widget.update_plot(
                mu=self.mu_spin.value(), 
                sigma=self.sigma_spin.value(), 
                n=self.n_spin.value()))
            
            cfg.themeChanged.connect(lambda: self.plot_widget.update_plot(
                mu=self.mu_spin.value(), 
                sigma=self.sigma_spin.value(), 
                n=self.n_spin.value()))

        def resizeEvent(self, event):
            super().resizeEvent(event)
            current_size = event.size()
            self.windowResizeSignal.emit(current_size.width(), current_size.height())
            event.accept()

    def __init__(self, parent=None):
        def create_description_interface():
            descriptionInterface = MarkdownKaTeXWidget()
            descriptionInterface.set_markdown(self.desc)
            return descriptionInterface

        def create_experiment_interface():
            scroll_area = ScrollArea()
            experimentInterface = ConsistencyOfPointEstimation.ExpInterface()
            scroll_area.setWidget(experimentInterface)
            scroll_area.setWidgetResizable(True)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            FluentStyleSheet.NAVIGATION_INTERFACE.apply(scroll_area)
            return scroll_area

        super().__init__(
            '点估计的相合性',
            descriptionFactory=create_description_interface,
            experimentFactory=create_experiment_interface,
            parent=parent
        )