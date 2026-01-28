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

class TwoTypesOfErrors(ExpWidget):
    
    desc = r"""
# 假设检验中关于两类错误的演示实验
设 $X_1, X_2, \ldots, X_n$ 是取自正太总体 $\mathcal N(\mu, \sigma^2)$ 的一个样本，$\sigma^2$ 为已知，
在显著水平 $\alpha$ 下，检验员假设 $H_0: \mu = \mu_0 \quad H_1: \mu \neq \mu_0$；
$\alpha = P(\text{拒绝} H_0 | H_0 \text{为真})$；$\beta = P(\text{接受} H_0 | H_0 \text{为假})$

| | $H_0$ 为真 | H_0 为假 |
| --- | --- | --- |
| 拒绝 $H_0$ | 第 I 类错误（概率为 $\alpha$） | 正确（概率为 $1-\beta$） |
| 接受 $H_0$ | 正确（概率为 $1-\alpha$） | 第 II 类错误（概率为 $\beta$） | 
"""

    class ExpInterface(ScrollArea):
        windowResizeSignal = pyqtSignal(int, int)
        
        class PlotWidget(QWidget):
            def __init__(self, parent=None):
                super().__init__(parent)
                
                self.figure = Figure(figsize=(9, 6), dpi=100)
                self.figure.patch.set_facecolor("none")
                self.figure.patch.set_edgecolor("none")
                self.canvas = FigureCanvas(self.figure)
                self.canvas.setStyleSheet("background: transparent;")
                self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                
                self.layout = QVBoxLayout(self)
                self.layout.addWidget(self.canvas)
                self.setLayout(self.layout)
                
                self.alpha = 0.05
                self.mu_0 = 0
                self.mu_1 = 1
                
                self.update_plot(self.alpha, self.mu_0, self.mu_1)
                self.parent().windowResizeSignal.connect(self.onParentResize)
                
            def onParentResize(self, parent_width, parent_height):
                """响应父控件大小变化"""
                available_width = max(parent_width - 100, 400)
                max_width = 900
                width = min(available_width, max_width)
                height = width * 2 / 3  # 2:3 宽高比
                
                self.figure.set_size_inches(width / 100, height / 100)
                self.canvas.draw()
            
            def update_plot(self, alpha=None, mu_0=None, mu_1=None):
                if alpha is None:
                    alpha = self.alpha
                if mu_0 is None:
                    mu_0 = self.mu_0
                if mu_1 is None:
                    mu_1 = self.mu_1
                
                self.figure.clear()
                
                # 设置标准差为1，简化演示
                sigma = 1
                n = 1  # 单个样本
                
                # 计算临界值
                z_alpha_half = norm.ppf(1 - alpha/2)
                critical_lower = mu_0 - z_alpha_half * sigma / np.sqrt(n)
                critical_upper = mu_0 + z_alpha_half * sigma / np.sqrt(n)
                
                # 设置x轴范围
                x_range = max(abs(mu_0 - 3*sigma/np.sqrt(n)), abs(mu_1 + 3*sigma/np.sqrt(n)))
                x_min = min(mu_0, mu_1) - x_range
                x_max = max(mu_0, mu_1) + x_range
                x = np.linspace(x_min, x_max, 1000)
                
                # 计算两个分布的概率密度
                y_null = norm.pdf(x, mu_0, sigma/np.sqrt(n))  # H0为真的情况
                y_alt = norm.pdf(x, mu_1, sigma/np.sqrt(n))   # H0为假的情况
                
                ax = self.figure.add_subplot(111)
                
                # 绘制原假设分布
                ax.plot(x, y_null, label=f'$H_0$: $\mu = {mu_0}$', color='blue', linewidth=2)
                
                # 绘制备择假设分布
                ax.plot(x, y_alt, label=f'$H_1$: $\mu = {mu_1}$', color='red', linewidth=2)
                
                # 填充第一类错误区域（α错误）
                x_fill = np.linspace(critical_upper, x_max, 500)
                y_fill = norm.pdf(x_fill, mu_0, sigma/np.sqrt(n))
                ax.fill_between(x_fill, 0, y_fill, alpha=0.4, color='blue', label=f'第I类错误 ($\\alpha={alpha}$)')
                
                x_fill = np.linspace(x_min, critical_lower, 500)
                y_fill = norm.pdf(x_fill, mu_0, sigma/np.sqrt(n))
                ax.fill_between(x_fill, 0, y_fill, alpha=0.4, color='blue')
                
                # 计算第二类错误概率（β错误）
                beta = norm.cdf(critical_upper, mu_1, sigma/np.sqrt(n)) - norm.cdf(critical_lower, mu_1, sigma/np.sqrt(n))
                
                # 填充第二类错误区域
                x_fill = np.linspace(critical_lower, critical_upper, 500)
                y_fill_alt = norm.pdf(x_fill, mu_1, sigma/np.sqrt(n))
                ax.fill_between(x_fill, 0, y_fill_alt, alpha=0.4, color='red', label=f'第II类错误 ($\\beta={beta:.3f}$)')
                
                # 添加临界线
                ax.axvline(critical_lower, color='gray', linestyle='--', alpha=0.7, label='临界值')
                ax.axvline(critical_upper, color='gray', linestyle='--', alpha=0.7)
                
                ax.set_xlabel('样本均值', fontsize=12)
                ax.set_ylabel('概率密度', fontsize=12)
                title = f'两类错误示意图: $\\alpha={alpha}, \\mu_0={mu_0}, \\mu_1={mu_1}$'
                ax.set_title(title, fontsize=14)
                
                ax.grid(True, alpha=0.3)
                ax.legend(loc='upper right')
                
                if isDarkTheme():
                    for spine in ax.spines.values():
                        spine.set_color('white')
                    ax.tick_params(colors='white', which='both')
                    ax.set_xlabel('样本均值', color='white', fontsize=12)
                    ax.set_ylabel('概率密度', color='white', fontsize=12)
                    ax.set_title(title, color='white', fontsize=14)
                    ax.legend(loc='upper right', facecolor='black', edgecolor='white', labelcolor='white')
                else:
                    for spine in ax.spines.values():
                        spine.set_color('black')
                    ax.tick_params(colors='black', which='both')
                    ax.set_xlabel('样本均值', color='black', fontsize=12)
                    ax.set_ylabel('概率密度', color='black', fontsize=12)
                    ax.set_title(title, color='black', fontsize=14)
                
                self.figure.tight_layout()
                self.canvas.draw()

        def __init__(self, parent=None):
            super().__init__(parent)
            self.flow_layout = FlowLayout(self)
            
            self.control_container = QWidget()
            self.control_container.setFixedWidth(400)
            self.controls_layout = QGridLayout(self.control_container)
            
            # alpha 参数设置
            self.alpha_label = BodyLabel("α（显著性水平）：", self)
            self.alpha_spin = CompactDoubleSpinBox(self)
            self.alpha_spin.setDecimals(3)
            self.alpha_spin.setRange(0.001, 0.2)
            self.alpha_spin.setSingleStep(0.001)
            self.alpha_spin.setValue(0.05)
            self.alpha_slider = Slider(Qt.Horizontal, self)
            self.alpha_slider.setRange(1, 200)
            self.alpha_slider.setSingleStep(1)
            self.alpha_slider.setValue(50)

            self.controls_layout.addWidget(self.alpha_label, 0, 0)
            self.controls_layout.addWidget(self.alpha_spin, 0, 1)
            self.controls_layout.addWidget(self.alpha_slider, 0, 2)
            
            # mu_0 参数设置
            self.mu_0_label = BodyLabel("μ₀（原假设均值）：", self)
            self.mu_0_spin = CompactDoubleSpinBox(self)
            self.mu_0_spin.setRange(-5, 5)
            self.mu_0_spin.setSingleStep(0.01)
            self.mu_0_spin.setValue(0)
            self.mu_0_slider = Slider(Qt.Horizontal, self)
            self.mu_0_slider.setRange(-500, 500)
            self.mu_0_slider.setSingleStep(1)
            self.mu_0_slider.setValue(0)

            self.controls_layout.addWidget(self.mu_0_label, 1, 0)
            self.controls_layout.addWidget(self.mu_0_spin, 1, 1)
            self.controls_layout.addWidget(self.mu_0_slider, 1, 2)
            
            # mu_1 参数设置
            self.mu_1_label = BodyLabel("μ₁（备择假设均值）：", self)
            self.mu_1_spin = CompactDoubleSpinBox(self)
            self.mu_1_spin.setRange(-5, 5)
            self.mu_1_spin.setSingleStep(0.01)
            self.mu_1_spin.setValue(1)
            self.mu_1_slider = Slider(Qt.Horizontal, self)
            self.mu_1_slider.setRange(-500, 500)
            self.mu_1_slider.setSingleStep(1)
            self.mu_1_slider.setValue(100)

            self.controls_layout.addWidget(self.mu_1_label, 2, 0)
            self.controls_layout.addWidget(self.mu_1_spin, 2, 1)
            self.controls_layout.addWidget(self.mu_1_slider, 2, 2)
            
            self.flow_layout.addWidget(self.control_container)
            
            self.plot_widget = self.PlotWidget(self)
            self.flow_layout.addWidget(self.plot_widget)
                        
            # 连接 alpha 控制器
            self.alpha_spin.valueChanged.connect(
                lambda: self.alpha_slider.setValue(int(self.alpha_spin.value() * 1000))
            )
            self.alpha_slider.valueChanged.connect(
                lambda: self.alpha_spin.setValue(self.alpha_slider.value() / 1000)
            )
            
            # 连接 mu_0 控制器
            self.mu_0_spin.valueChanged.connect(
                lambda: self.mu_0_slider.setValue(int(self.mu_0_spin.value() * 100))
            )
            self.mu_0_slider.valueChanged.connect(
                lambda: self.mu_0_spin.setValue(self.mu_0_slider.value() / 100)
            )
            
            # 连接 mu_1 控制器
            self.mu_1_spin.valueChanged.connect(
                lambda: self.mu_1_slider.setValue(int(self.mu_1_spin.value() * 100))
            )
            self.mu_1_slider.valueChanged.connect(
                lambda: self.mu_1_spin.setValue(self.mu_1_slider.value() / 100)
            )
            
            # 连接更新信号
            self.alpha_spin.valueChanged.connect(
                lambda: self.plot_widget.update_plot(
                    alpha=self.alpha_spin.value(),
                    mu_0=self.mu_0_spin.value(),
                    mu_1=self.mu_1_spin.value()
                )
            )
            self.mu_0_spin.valueChanged.connect(
                lambda: self.plot_widget.update_plot(
                    alpha=self.alpha_spin.value(),
                    mu_0=self.mu_0_spin.value(),
                    mu_1=self.mu_1_spin.value()
                )
            )
            self.mu_1_spin.valueChanged.connect(
                lambda: self.plot_widget.update_plot(
                    alpha=self.alpha_spin.value(),
                    mu_0=self.mu_0_spin.value(),
                    mu_1=self.mu_1_spin.value()
                )
            )
            
            cfg.themeChanged.connect(
                lambda: self.plot_widget.update_plot(
                    alpha=self.alpha_spin.value(),
                    mu_0=self.mu_0_spin.value(),
                    mu_1=self.mu_1_spin.value()
                )
            )

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
            experimentInterface = TwoTypesOfErrors.ExpInterface()
            scroll_area.setWidget(experimentInterface)
            scroll_area.setWidgetResizable(True)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            FluentStyleSheet.NAVIGATION_INTERFACE.apply(scroll_area)
            return scroll_area

        super().__init__(
            '两类错误',
            descriptionFactory=create_description_interface,
            experimentFactory=create_experiment_interface,
            parent=parent
        )