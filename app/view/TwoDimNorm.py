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
from mpl_toolkits.mplot3d import Axes3D
from scipy.stats import multivariate_normal
import numpy as np

from .ExpWidget import ExpWidget
from ..common.MarkdownKatex import MarkdownKaTeXWidget
from ..common.config import cfg

class TwoDimNorm(ExpWidget):
    
    desc = r"""
# 二维正态分布简介
若二维随机向量 $(X, Y)$ 的联合概率密度为
$$
f(x, y) = \left( 2\pi \sigma_1 \sigma_2 \sqrt{1-\rho^2} \right) ^{-1}
\exp 
\left[
    -\frac{1}{2(1-\rho^2)}
    \left(
        \frac{(x-\mu_1)^2}{\sigma_1^2}
        - 2\rho \cfrac{(x-\mu_1)(y-\mu_2)}{\sigma_1\sigma_2}
        + \frac{(y-\mu_2)^2}{\sigma_2^2}
    \right)
\right]
$$

其中 $-\infty < \mu_1, \mu_2 < + \infty, \quad \sigma_1^2 > 0, \quad \sigma_2^2 > 0, \quad \left| \rho \right| < 1$，则称随机向量 $(X, Y)$ 服从参数为 $\mu_1, \mu_2, \sigma_1, \sigma_2, \rho$ 的二维正态分布，记作
$(X, Y) \sim \mathcal{N}(\mu_1, \mu_2, \sigma_1, \sigma_2, \rho)$
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
                
                self.mu1 = 0
                self.mu2 = 0
                self.sigma1 = 1
                self.sigma2 = 1
                self.rho = 0
                
                # 初始化视角参数
                self.elev = 20  # 仰角
                self.azim = 45  # 方位角
                
                self.update_plot()
                self.parent().windowResizeSignal.connect(self.onParentResize)
                
            def onParentResize(self, parent_width, parent_height):
                available_width = max(parent_width - 100, 400)
                max_width = 800
                width = min(available_width, max_width)
                height = width * 3 / 4
                
                self.figure.set_size_inches(width / 100, height / 100)
                self.canvas.draw()
            
            def update_plot(self):
                # 保存当前视角
                if hasattr(self, 'ax'):
                    self.elev = self.ax.elev
                    self.azim = self.ax.azim
                
                self.figure.clear()
                self.ax = self.figure.add_subplot(111, projection='3d')
                
                # begin core plotting code
                x = np.linspace(-5, 5, 100)
                y = np.linspace(-5, 5, 100)
                X, Y = np.meshgrid(x, y)
                
                pos = np.dstack((X, Y))
                
                mean = [self.mu1, self.mu2]
                cov = [[self.sigma1**2, self.rho*self.sigma1*self.sigma2],
                       [self.rho*self.sigma1*self.sigma2, self.sigma2**2]]
                
                rv = multivariate_normal(mean, cov)
                Z = rv.pdf(pos)
                surf = self.ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
                self.ax.contour(X, Y, Z, zdir='z', offset=Z.min(), cmap='viridis', alpha=0.5)
                
                # 设置之前保存的视角
                self.ax.view_init(elev=self.elev, azim=self.azim)
                
                # end core plotting code
                
                self.ax.patch.set_alpha(0.1)
                if isDarkTheme():
                    self.ax.xaxis.pane.fill = False
                    self.ax.yaxis.pane.fill = False
                    self.ax.zaxis.pane.fill = False
                    self.ax.xaxis.pane.set_edgecolor('w')
                    self.ax.yaxis.pane.set_edgecolor('w')
                    self.ax.zaxis.pane.set_edgecolor('w')
                    self.ax.xaxis.pane.set_alpha(0.1)
                    self.ax.yaxis.pane.set_alpha(0.1)
                    self.ax.zaxis.pane.set_alpha(0.1)
                    
                    self.ax.tick_params(colors='white', which='both')
                    self.ax.set_xlabel('$X$', color='white')
                    self.ax.set_ylabel('$Y$', color='white')
                    self.ax.set_zlabel('$f(X,Y)$', color='white')
                    self.ax.set_title(f'二维正态分布 $N(\\mu_1={self.mu1:.2f}, \\mu_2={self.mu2:.2f}, \\sigma_1^2={self.sigma1**2:.2f}, \\sigma_2^2={self.sigma2**2:.2f}, \\rho={self.rho:.2f})$', color='white')
                else:
                    self.ax.xaxis.pane.fill = False
                    self.ax.yaxis.pane.fill = False
                    self.ax.zaxis.pane.fill = False
                    self.ax.xaxis.pane.set_edgecolor('k')
                    self.ax.yaxis.pane.set_edgecolor('k')
                    self.ax.zaxis.pane.set_edgecolor('k')
                    self.ax.xaxis.pane.set_alpha(0.1)
                    self.ax.yaxis.pane.set_alpha(0.1)
                    self.ax.zaxis.pane.set_alpha(0.1)
                    
                    self.ax.tick_params(colors='black', which='both')
                    self.ax.set_xlabel('$X$', color='black')
                    self.ax.set_ylabel('$Y$', color='black')
                    self.ax.set_zlabel('$f(X,Y)$', color='black')
                    self.ax.set_title(f'二维正态分布 $N(\\mu_1={self.mu1:.2f}, \\mu_2={self.mu2:.2f}, \\sigma_1^2={self.sigma1**2:.2f}, \\sigma_2^2={self.sigma2**2:.2f}, \\rho={self.rho:.2f})$', color='black')
                
                # Add colorbar
                self.figure.colorbar(surf, shrink=0.5, aspect=5)
                
                self.figure.tight_layout()
                self.canvas.draw()

        def __init__(self, parent=None):
            super().__init__(parent)
            self.flow_layout = FlowLayout(self)
            
            self.control_container = QWidget()
            self.control_container.setFixedWidth(400)
            self.control_layout = QGridLayout(self.control_container)

            # mu1 参数设置
            self.mu1_label = BodyLabel("μ₁（均值1）：", self)
            self.mu1_spin = CompactDoubleSpinBox(self)
            self.mu1_spin.setRange(-5, 5)
            self.mu1_spin.setSingleStep(0.01)
            self.mu1_spin.setValue(0)
            self.mu1_slider = Slider(Qt.Horizontal, self)
            self.mu1_slider.setRange(-500, 500)
            self.mu1_slider.setSingleStep(1)
            self.mu1_slider.setValue(0)
            
            self.control_layout.addWidget(self.mu1_label, 0, 0)
            self.control_layout.addWidget(self.mu1_spin, 0, 1)
            self.control_layout.addWidget(self.mu1_slider, 0, 2)
            
            # mu2 参数设置
            self.mu2_label = BodyLabel("μ₂（均值2）：", self)
            self.mu2_spin = CompactDoubleSpinBox(self)
            self.mu2_spin.setRange(-5, 5)
            self.mu2_spin.setSingleStep(0.01)
            self.mu2_spin.setValue(0)
            self.mu2_slider = Slider(Qt.Horizontal, self)
            self.mu2_slider.setRange(-500, 500)
            self.mu2_slider.setSingleStep(1)
            self.mu2_slider.setValue(0)
            
            self.control_layout.addWidget(self.mu2_label, 1, 0)
            self.control_layout.addWidget(self.mu2_spin, 1, 1)
            self.control_layout.addWidget(self.mu2_slider, 1, 2)
            
            # sigma1 参数设置
            self.sigma1_label = BodyLabel("σ₁（标准差1）：", self)
            self.sigma1_spin = CompactDoubleSpinBox(self)
            self.sigma1_spin.setRange(0.1, 3)
            self.sigma1_spin.setSingleStep(0.01)
            self.sigma1_spin.setValue(1)
            self.sigma1_slider = Slider(Qt.Horizontal, self)
            self.sigma1_slider.setRange(10, 300)
            self.sigma1_slider.setSingleStep(1)
            self.sigma1_slider.setValue(100)
            
            self.control_layout.addWidget(self.sigma1_label, 2, 0)
            self.control_layout.addWidget(self.sigma1_spin, 2, 1)
            self.control_layout.addWidget(self.sigma1_slider, 2, 2)
            
            # sigma2 参数设置
            self.sigma2_label = BodyLabel("σ₂（标准差2）：", self)
            self.sigma2_spin = CompactDoubleSpinBox(self)
            self.sigma2_spin.setRange(0.1, 3)
            self.sigma2_spin.setSingleStep(0.01)
            self.sigma2_spin.setValue(1)
            self.sigma2_slider = Slider(Qt.Horizontal, self)
            self.sigma2_slider.setRange(10, 300)
            self.sigma2_slider.setSingleStep(1)
            self.sigma2_slider.setValue(100)
            
            self.control_layout.addWidget(self.sigma2_label, 3, 0)
            self.control_layout.addWidget(self.sigma2_spin, 3, 1)
            self.control_layout.addWidget(self.sigma2_slider, 3, 2)
            
            # rho 参数设置
            self.rho_label = BodyLabel("ρ（相关系数）：", self)
            self.rho_spin = CompactDoubleSpinBox(self)
            self.rho_spin.setRange(-0.99, 0.99)
            self.rho_spin.setSingleStep(0.01)
            self.rho_spin.setValue(0)
            self.rho_slider = Slider(Qt.Horizontal, self)
            self.rho_slider.setRange(-99, 99)
            self.rho_slider.setSingleStep(1)
            self.rho_slider.setValue(0)
            
            self.control_layout.addWidget(self.rho_label, 4, 0)
            self.control_layout.addWidget(self.rho_spin, 4, 1)
            self.control_layout.addWidget(self.rho_slider, 4, 2)
            
            self.flow_layout.addWidget(self.control_container)
            
            # 绘图区域
            self.plot_widget = self.PlotWidget(self)
            self.flow_layout.addWidget(self.plot_widget)
            
            # 同步 slider 和 spinbox
            self.mu1_spin.valueChanged.connect(
                lambda: self.mu1_slider.setValue(int(self.mu1_spin.value() * 100))
            )
            self.mu1_slider.valueChanged.connect(
                lambda: self.mu1_spin.setValue(self.mu1_slider.value() / 100)
            )
            
            self.mu2_spin.valueChanged.connect(
                lambda: self.mu2_slider.setValue(int(self.mu2_spin.value() * 100))
            )
            self.mu2_slider.valueChanged.connect(
                lambda: self.mu2_spin.setValue(self.mu2_slider.value() / 100)
            )
            
            self.sigma1_spin.valueChanged.connect(
                lambda: self.sigma1_slider.setValue(int(self.sigma1_spin.value() * 100))
            )
            self.sigma1_slider.valueChanged.connect(
                lambda: self.sigma1_spin.setValue(self.sigma1_slider.value() / 100)
            )
            
            self.sigma2_spin.valueChanged.connect(
                lambda: self.sigma2_slider.setValue(int(self.sigma2_spin.value() * 100))
            )
            self.sigma2_slider.valueChanged.connect(
                lambda: self.sigma2_spin.setValue(self.sigma2_slider.value() / 100)
            )
            
            self.rho_spin.valueChanged.connect(
                lambda: self.rho_slider.setValue(int(self.rho_spin.value() * 100))
            )
            self.rho_slider.valueChanged.connect(
                lambda: self.rho_spin.setValue(self.rho_slider.value() / 100)
            )

            # 连接信号更新图表
            self.mu1_spin.valueChanged.connect(lambda: self.update_parameters())
            self.mu2_spin.valueChanged.connect(lambda: self.update_parameters())
            self.sigma1_spin.valueChanged.connect(lambda: self.update_parameters())
            self.sigma2_spin.valueChanged.connect(lambda: self.update_parameters())
            self.rho_spin.valueChanged.connect(lambda: self.update_parameters())
            
            cfg.themeChanged.connect(lambda: self.plot_widget.update_plot())
            
        def update_parameters(self):
            self.plot_widget.mu1 = self.mu1_spin.value()
            self.plot_widget.mu2 = self.mu2_spin.value()
            self.plot_widget.sigma1 = self.sigma1_spin.value()
            self.plot_widget.sigma2 = self.sigma2_spin.value()
            self.plot_widget.rho = self.rho_spin.value()
            self.plot_widget.update_plot()

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
            '二维正态分布',
            descriptionFactory=create_description_interface,
            experimentFactory=create_experiment_interface,
            parent=parent
        )