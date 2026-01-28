from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QSizePolicy, QGridLayout
)
from qfluentwidgets import (
    FlowLayout, Slider, CompactDoubleSpinBox, CompactSpinBox, isDarkTheme,
    TitleLabel, BodyLabel, ScrollArea, FluentStyleSheet
)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import random

from .ExpWidget import ExpWidget
from ..common.MarkdownKatex import MarkdownKaTeXWidget
from ..common.config import cfg

class CoinTossingExperiment(ExpWidget):
    
    desc = r"""
# 投币试验

1. 投掷一枚质地均匀的硬币，观察其出现正面的频数，并同时计算出现正面的概率，分析频率的变化规律
2. 利用图形动态演示频率的稳定性规律：随着投掷硬币次数的增加，出现正面的频率振幅越来越小，逐渐地稳定于 $\frac{1}{2}$ 。
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
                
                self.n = 100
                self.current_step = 0
                self.animation_timer = QTimer(self)
                self.animation_timer.timeout.connect(self.animate_plot)
                
                # 存储数据
                self.heads_count = 0
                self.total_tosses = 0
                self.frequency_history = []
                
                self.update_plot(self.n)
                self.parent().windowResizeSignal.connect(self.onParentResize)
                
            def onParentResize(self, parent_width, parent_height):
                """响应父控件大小变化"""
                available_width = max(parent_width - 100, 400)
                max_width = 800
                width = min(available_width, max_width)
                height = width * 3 / 4
                
                self.figure.set_size_inches(width / 100, height / 100)
                self.canvas.draw()
            
            def update_plot(self, n=None):
                if n is None:
                    n = self.n
                else:
                    self.n = n
                
                # 重置数据
                self.heads_count = 0
                self.total_tosses = 0
                self.frequency_history = []
                self.current_step = 0
                
                # 计算每次绘制的步长（总次数的1%或至少1次）
                self.step_size = max(1, self.n // 50)
                
                # 开始动画
                self.animation_timer.start(20)  # 每20ms更新一次
            
            def animate_plot(self):
                """动画更新绘图 - 每次绘制多个点"""
                if self.current_step >= self.n:
                    self.animation_timer.stop()
                    return
                
                # 计算本次要添加的点数
                remaining_steps = self.n - self.current_step
                actual_step_size = min(self.step_size, remaining_steps)
                
                # 模拟多次投币
                for _ in range(actual_step_size):
                    result = random.randint(0, 1)  # 0: 反面, 1: 正面
                    self.heads_count += result
                    self.total_tosses += 1
                    
                    # 计算当前频率
                    current_frequency = self.heads_count / self.total_tosses
                    self.frequency_history.append(current_frequency)
                    self.current_step += 1
                
                # 绘制图表
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                
                # 绘制频率曲线
                x_values = list(range(1, len(self.frequency_history) + 1))
                if len(self.frequency_history) > 0:
                    ax.plot(x_values, self.frequency_history, 'b-', linewidth=1.5, 
                           label='实际频率')
                
                # 添加理论概率线
                ax.axhline(y=0.5, color='r', linestyle='--', label='理论概率 (0.5)', alpha=0.7)
                
                ax.set_xlim(0, self.n)
                ax.set_ylim(0, 1.1)
                ax.set_xlabel("投币次数", color='black')
                ax.set_ylabel("正面频率", color='black')
                ax.set_title(f'投币实验: 频率稳定性演示 (投币次数: {self.n})', color='black')
                
                ax.legend()
                
                ax.patch.set_alpha(0.1)
                if isDarkTheme():
                    for spine in ax.spines.values():
                        spine.set_color('white')
                    ax.tick_params(colors='white', which='both')
                    ax.set_xlabel(ax.get_xlabel(), color='white')
                    ax.set_ylabel(ax.get_ylabel(), color='white')
                    ax.set_title(ax.get_title(), color='white')
                    ax.grid(True, alpha=0.3)
                else:
                    for spine in ax.spines.values():
                        spine.set_color('black')
                    ax.tick_params(colors='black', which='both')
                    ax.set_xlabel(ax.get_xlabel(), color='black')
                    ax.set_ylabel(ax.get_ylabel(), color='black')
                    ax.set_title(ax.get_title(), color='black')
                    ax.grid(True, alpha=0.7)
                
                self.figure.tight_layout()
                self.canvas.draw()
                
        def __init__(self, parent=None):
            super().__init__(parent)
            self.flow_layout = FlowLayout(self)
            
            self.control_container = QWidget()
            self.control_container.setFixedWidth(400)
            self.controls_layout = QGridLayout(self.control_container)
            
            # n 参数设置 (投币次数)
            self.n_label = BodyLabel("n（投币次数）：", self)
            self.n_spin = CompactSpinBox(self)
            self.n_spin.setRange(10, 1000)
            self.n_spin.setValue(100)
            self.n_slider = Slider(Qt.Horizontal, self)
            self.n_slider.setRange(10, 1000)
            self.n_slider.setSingleStep(10)
            self.n_slider.setValue(100)
            
            self.controls_layout.addWidget(self.n_label, 0, 0)
            self.controls_layout.addWidget(self.n_spin, 0, 1)
            self.controls_layout.addWidget(self.n_slider, 0, 2)
            
            self.flow_layout.addWidget(self.control_container)
            
            # 绘图区域
            self.plot_widget = self.PlotWidget(self)
            self.flow_layout.addWidget(self.plot_widget)
                        
            # 连接信号
            self.n_spin.valueChanged.connect(self.n_slider.setValue)
            self.n_slider.valueChanged.connect(self.n_spin.setValue)
            self.n_spin.valueChanged.connect(lambda: self.plot_widget.update_plot(n=self.n_spin.value()))
            
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
            experimentInterface = CoinTossingExperiment.ExpInterface()
            scroll_area.setWidget(experimentInterface)
            scroll_area.setWidgetResizable(True)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            FluentStyleSheet.NAVIGATION_INTERFACE.apply(scroll_area)
            return scroll_area

        super().__init__(
            '投币实验',
            descriptionFactory=create_description_interface,
            experimentFactory=create_experiment_interface,
            parent=parent
        )