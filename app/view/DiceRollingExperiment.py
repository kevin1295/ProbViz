from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QSizePolicy, QGridLayout
)
from qfluentwidgets import (
    FlowLayout, Slider, CompactDoubleSpinBox, CompactSpinBox, isDarkTheme,
    TitleLabel, BodyLabel, ScrollArea, FluentStyleSheet, TogglePushButton
)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import random

from .ExpWidget import ExpWidget
from ..common.MarkdownKatex import MarkdownKaTeXWidget
from ..common.config import cfg

class DiceRollingExperiment(ExpWidget):
    
    desc = r"""
# 掷骰子试验

1. 投掷一颗质地均匀的骰子，令 $X$ 表示其出现的点数，分析各点数出现的频率的稳定性及其变化规律。
2. 利用统计的方法，根据"频率的稳定性"规律求投掷一颗质地均匀的骰子出现某点数的概率。
3. 演示"随机变量 $X$ 的数学期望的统计意义"。
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
                self.mode = 'frequency'  # 'frequency' 或 'expectation'
                self.current_step = 0
                self.animation_timer = QTimer(self)
                self.animation_timer.timeout.connect(self.animate_plot)
                
                # 存储数据
                self.counts = [0] * 6  # 记录1-6点出现的次数
                self.less_than_4_history = []  # 记录点数<4的频率历史
                self.equal_to_5_history = []   # 记录点数=5的频率历史
                self.means = []                # 记录平均值历史
                
                self.update_plot(self.n)
                self.parent().windowResizeSignal.connect(self.onParentResize)
                
            def onParentResize(self, parent_width, parent_height):
                """响应父控件大小变化"""
                available_width = max(parent_width - 100, 400)
                max_width = 800
                width = min(available_width, max_width)
                height = width * 3 / 4  # 3:4 宽高比
                
                self.figure.set_size_inches(width / 100, height / 100)
                self.canvas.draw()
            
            def update_plot(self, n=None):
                if n is None:
                    n = self.n
                else:
                    self.n = n
                
                # 重置数据
                self.counts = [0] * 6
                self.less_than_4_history = []
                self.equal_to_5_history = []
                self.means = []
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
                
                # 模拟多次掷骰子
                for _ in range(actual_step_size):
                    result = random.randint(1, 6) - 1  # 0-5对应1-6点
                    self.counts[result] += 1
                    self.current_step += 1
                    
                    # 计算当前频率和均值
                    total = sum(self.counts)
                    if total > 0:
                        if self.mode == 'frequency':
                            # 计算频率
                            less_than_4 = sum(self.counts[:3]) / total  # 点数为1,2,3的频率
                            equal_to_5 = self.counts[4] / total  # 点数为5的频率
                            self.less_than_4_history.append(less_than_4)
                            self.equal_to_5_history.append(equal_to_5)
                        elif self.mode == 'expectation':
                            # 计算平均值
                            current_mean = sum((i+1)*count for i, count in enumerate(self.counts)) / total
                            self.means.append(current_mean)
                
                # 绘制图表
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                
                if self.mode == 'frequency':
                    # 绘制频率曲线
                    x_values = list(range(1, len(self.less_than_4_history) + 1))
                    if len(self.less_than_4_history) > 0:
                        ax.plot(x_values, self.less_than_4_history, 'b-', markersize=4, 
                               label='点数<4的实际频率', linewidth=1.5)
                    if len(self.equal_to_5_history) > 0:
                        ax.plot(x_values, self.equal_to_5_history, 'r-', markersize=4, 
                               label='点数=5的实际频率', linewidth=1.5)
                    
                    # 添加理论概率线
                    ax.axhline(y=0.5, color='b', linestyle='--', label='点数<4理论概率 (0.5)', alpha=0.7)
                    ax.axhline(y=1/6, color='r', linestyle='--', label='点数=5理论概率 (1/6)', alpha=0.7)
                    
                    ax.set_xlim(0, self.n)
                    ax.set_ylim(0, 1.1)
                    ax.set_xlabel("试验次数", color='black')
                    ax.set_ylabel("频率", color='black')
                    ax.set_title(f'掷骰子实验: 频率稳定性演示 (试验次数: {self.n})', color='black')
                elif self.mode == 'expectation':
                    # 绘制平均值曲线
                    x_values = list(range(1, len(self.means) + 1))
                    if len(self.means) > 0:
                        ax.plot(x_values, self.means, 'g-', markersize=4, 
                               label='实际平均值', linewidth=1.5)
                    
                    # 添加理论期望线
                    ax.axhline(y=3.5, color='g', linestyle='--', label='理论期望 (3.5)', alpha=0.7)
                    
                    ax.set_xlim(0, self.n)
                    ax.set_ylim(0, 7)
                    ax.set_xlabel("试验次数", color='black')
                    ax.set_ylabel("平均值", color='black')
                    ax.set_title(f'掷骰子实验: 数学期望的统计意义 (试验次数: {self.n})', color='black')
                
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
                
            def switch_mode(self, mode):
                """切换模式"""
                self.mode = mode
                self.update_plot(self.n)
                
        def __init__(self, parent=None):
            super().__init__(parent)
            self.flow_layout = FlowLayout(self)
            
            self.control_container = QWidget()
            self.control_container.setFixedWidth(400)
            self.controls_layout = QGridLayout(self.control_container)
            
            # n 参数设置 (试验次数)
            self.n_label = BodyLabel("n（试验次数）：", self)
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
            
            # 模式切换按钮
            self.mode_toggle = TogglePushButton("频率模式", self)
            self.mode_toggle.toggled.connect(self.on_mode_toggled)
            
            self.controls_layout.addWidget(self.mode_toggle, 1, 0, 1, 2)
            
            self.flow_layout.addWidget(self.control_container)
            
            # 绘图区域
            self.plot_widget = self.PlotWidget(self)
            self.flow_layout.addWidget(self.plot_widget)
                        
            # 连接信号
            self.n_spin.valueChanged.connect(self.n_slider.setValue)
            self.n_slider.valueChanged.connect(self.n_spin.setValue)
            self.n_spin.valueChanged.connect(lambda: self.plot_widget.update_plot(n=self.n_spin.value()))
            
            cfg.themeChanged.connect(lambda: self.plot_widget.update_plot())
            
        def on_mode_toggled(self, checked):
            """模式切换响应"""
            if checked:
                self.mode_toggle.setText("期望模式")
                self.plot_widget.switch_mode('expectation')
            else:
                self.mode_toggle.setText("频率模式")
                self.plot_widget.switch_mode('frequency')
            
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
            experimentInterface = DiceRollingExperiment.ExpInterface()
            scroll_area.setWidget(experimentInterface)
            scroll_area.setWidgetResizable(True)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            FluentStyleSheet.NAVIGATION_INTERFACE.apply(scroll_area)
            return scroll_area

        super().__init__(
            '掷骰子实验',
            descriptionFactory=create_description_interface,
            experimentFactory=create_experiment_interface,
            parent=parent
        )