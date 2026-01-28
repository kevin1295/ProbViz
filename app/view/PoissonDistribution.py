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
from scipy.stats import poisson
import numpy as np

from .ExpWidget import ExpWidget
from ..common.MarkdownKatex import MarkdownKaTeXWidget
from ..common.config import cfg

class PoissonDistribution(ExpWidget):
    
    desc = r"""
# 泊松分布简介
如果随机变量 $X$ 的概率分布为
$$
P(X=k) = \cfrac{\lambda^k}{k!} e^{-\lambda}, \quad k=0,1,2,\ldots,n
$$
则称 $X$ 服从参数为 $\lambda$ 的泊松分布，记为 $X \sim \mathcal{P}(\lambda)$

泊松分布常用于描述单位时间内随机事件发生的次数。例如，单位时间内某路口通过的车辆数、单位时间内某电话交换机收到的呼叫数等，都是泊松分布的具体应用。
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
                
                self.lambda_ = 10
                self.update_plot(self.lambda_)
                self.parent().windowResizeSignal.connect(self.onParentResize)
                
            def onParentResize(self, parent_width, parent_height):
                available_width = max(parent_width - 100, 400)
                max_width = 800
                width = min(available_width, max_width)
                height = width * 3 / 4
                
                self.figure.set_size_inches(width / 100, height / 100)
                self.canvas.draw()
                
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
            self.flow_layout = FlowLayout(self)
            
            self.control_container = QWidget()
            self.control_container.setFixedWidth(400)
            self.control_layout = QGridLayout(self.control_container)

            # lambda 参数设置
            self.lambda_label = BodyLabel("λ（参数）：", self)
            self.lambda_spin = CompactDoubleSpinBox(self)
            self.lambda_spin.setRange(0, 20)
            self.lambda_spin.setSingleStep(0.01)
            self.lambda_spin.setValue(10)
            self.lambda_slider = Slider(Qt.Horizontal, self)
            self.lambda_slider.setRange(0, 2000)
            self.lambda_slider.setSingleStep(1)
            self.lambda_slider.setValue(1000)
            
            self.control_layout.addWidget(self.lambda_label, 0, 0)
            self.control_layout.addWidget(self.lambda_spin, 0, 1)
            self.control_layout.addWidget(self.lambda_slider, 0, 2)
            
            self.flow_layout.addWidget(self.control_container)
            
            # 绘图区域
            self.plot_widget = self.PlotWidget(self)
            self.flow_layout.addWidget(self.plot_widget)
            
            # 同步 slider 和 spinbox
            self.lambda_slider.valueChanged.connect(lambda value: self.lambda_spin.setValue(value / 100))
            self.lambda_spin.valueChanged.connect(lambda value: self.lambda_slider.setValue(value * 100))

            # 连接信号更新图表
            self.lambda_spin.valueChanged.connect(lambda: self.plot_widget.update_plot(lambda_=self.lambda_spin.value()))
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
            '泊松分布',
            descriptionFactory=create_description_interface,
            experimentFactory=create_experiment_interface,
            parent=parent
        )