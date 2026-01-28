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
from scipy.stats import binom, poisson
import numpy as np

from .ExpWidget import ExpWidget
from ..common.MarkdownKatex import MarkdownKaTeXWidget
from ..common.config import cfg

class PoissonTheorem(ExpWidget):
    
    desc = r"""
# 泊松定理
在 $n$ 重伯努利试验中，成功次数 $X$ 服从二项分布，假设每次试验成功的概率为 $P_n(0<P_n<1)$，
并且 $\lim_{n \to \infty} n P_n = \lambda > 0$ 则对于任何非负整数 $k$，都有
$$
\lim_{n \to \infty} P(X=k) = \lim_{n \to \infty} C_n^k P_n^k (1-P_n)^{n-k} = \cfrac{\lambda^k}{k!} e^{-\lambda}
$$

对于成功率为 $p$ 的 $n$ 重伯努利试验，只要 $n$ 充分大，而 $p$ 充分小，
则其成功次数 $X$ 就近似地服从参数为 $\lambda = n p$ 的泊松分布。
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
                
                self.n = 200
                self.lambda_ = 20
                
                self.update_plot(self.n, self.lambda_)
                self.parent().windowResizeSignal.connect(self.onParentResize)
                
            def onParentResize(self, parent_width, parent_height):
                available_width = max(parent_width - 100, 400)
                max_width = 800
                width = min(available_width, max_width)
                height = width * 3 / 4  # 3:4 宽高比
                
                self.figure.set_size_inches(width / 100, height / 100)
                self.canvas.draw()
            
            def update_plot(self, n=None, lambda_=None):
                if n is None:
                    n = self.n
                if lambda_ is None:
                    lambda_ = self.lambda_
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                
                # begin core plotting code
                x = np.arange(0, lambda_ + 4*np.sqrt(lambda_) + 1)
                p = lambda_ / n
                pmf_binom = binom.pmf(x, n, p)
                pmf_poisson = poisson.pmf(x, lambda_)
                
                ax.bar(x, pmf_binom, width=0.4, label=f'二项分布 $B(n={n}, p={p:.3f})$', alpha=0.6, color='blue', align='center')
                ax.bar(x, pmf_poisson, width=0.4, label=f'泊松分布 $P(\\lambda={lambda_:.3f})$', alpha=0.6, color='red', align='center')
                # end core plotting code
                
                ax.patch.set_alpha(0.1)
                ax.legend()
                
                if isDarkTheme():
                    for spine in ax.spines.values():
                        spine.set_color('white')
                    ax.tick_params(colors='white', which='both')
                    ax.set_xlabel('$k$', color='white')
                    ax.set_ylabel('$P(X=k)$', color='white')
                    ax.set_title(f'泊松定理演示: 二项分布 vs 泊松分布', color='white')
                    ax.grid(True, alpha=0.3)
                else:
                    for spine in ax.spines.values():
                        spine.set_color('black')
                    ax.tick_params(colors='black', which='both')
                    ax.set_xlabel('$k$', color='black')
                    ax.set_ylabel('$P(X=k)$', color='black')
                    ax.set_title(f'泊松定理演示: 二项分布 vs 泊松分布', color='black')
                    ax.grid(True, alpha=0.7)
                
                self.figure.tight_layout()
                self.canvas.draw()
        def __init__(self, parent=None):
            super().__init__(parent)
            self.flow_layout = FlowLayout(self)
            
            self.control_container = QWidget()
            self.control_container.setFixedWidth(400)
            self.control_layout = QGridLayout(self.control_container)
            
            self.n_label = BodyLabel("n（实验次数）：", self)
            self.n_spin = CompactSpinBox(self)
            self.n_spin.setRange(50, 400)
            self.n_spin.setValue(200)
            self.n_slider = Slider(Qt.Horizontal, self)
            self.n_slider.setRange(50, 400)
            self.n_slider.setSingleStep(1)
            self.n_slider.setValue(200)
            
            self.control_layout.addWidget(self.n_label, 0, 0)
            self.control_layout.addWidget(self.n_spin, 0, 1)
            self.control_layout.addWidget(self.n_slider, 0, 2)
            
            self.lambda_label = BodyLabel("λ（泊松参数）：", self)
            self.lambda_spin = CompactDoubleSpinBox(self)
            self.lambda_spin.setRange(15, 25)
            self.lambda_spin.setSingleStep(0.01)
            self.lambda_spin.setValue(20)
            self.lambda_slider = Slider(Qt.Horizontal, self)
            self.lambda_slider.setRange(1500, 2500)
            self.lambda_slider.setSingleStep(1)
            self.lambda_slider.setValue(2000)

            self.control_layout.addWidget(self.lambda_label, 1, 0)
            self.control_layout.addWidget(self.lambda_spin, 1, 1)
            self.control_layout.addWidget(self.lambda_slider, 1, 2)
            
            self.flow_layout.addWidget(self.control_container)

            # 绘图区域
            self.plot_widget = self.PlotWidget(self)
            self.flow_layout.addWidget(self.plot_widget)
            
            # 同步 slider 和 spinbox
            self.n_spin.valueChanged.connect(self.n_slider.setValue)
            self.n_slider.valueChanged.connect(self.n_spin.setValue)
            self.lambda_spin.valueChanged.connect(
                lambda: self.lambda_slider.setValue(self.lambda_spin.value() * 100)
            )
            self.lambda_slider.valueChanged.connect(
                lambda: self.lambda_spin.setValue(self.lambda_slider.value() / 100)
            )

            # 连接信号更新图表
            self.n_spin.valueChanged.connect(lambda: self.plot_widget.update_plot(n=self.n_spin.value(), lambda_=self.lambda_spin.value()))
            self.lambda_spin.valueChanged.connect(lambda: self.plot_widget.update_plot(n=self.n_spin.value(), lambda_=self.lambda_spin.value()))
            
            cfg.themeChanged.connect(lambda: self.plot_widget.update_plot(self.n_spin.value(), self.lambda_spin.value()))
            
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
            '泊松定理',
            descriptionFactory=create_description_interface,
            experimentFactory=create_experiment_interface,
            parent=parent
        )