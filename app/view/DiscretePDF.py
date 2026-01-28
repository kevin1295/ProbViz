from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QSizePolicy, QGridLayout
)
from qfluentwidgets import (
    FlowLayout, Slider, CompactDoubleSpinBox, CompactSpinBox, isDarkTheme,
    TitleLabel, BodyLabel, ScrollArea, FluentStyleSheet, ComboBox,
    TeachingTip, InfoBarIcon
)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from scipy.stats import binom, poisson
import numpy as np

from .ExpWidget import ExpWidget
from ..common.MarkdownKatex import MarkdownKaTeXWidget
from ..common.config import cfg

class DiscretePDF(ExpWidget):
    
    desc = r"""
# 离散型随机变量概率分布

离散型随机变量是指取值为有限个或可列个的随机变量。设离散型随机变量 $X$ 所有可能的取值为 $x_i (i=1,2,\ldots)$，这些值对应的概率为 $P(X=x_i)=p_i (i=1,2,\ldots)$，满足：

1. $p_i \geq 0$
2. $\sum_{i} p_i = 1$

常见的离散型随机变量分布包括：

---

<details>
<summary>两点分布（伯努利分布）</summary>

概率质量函数：
$$P(X=k) = p^k(1-p)^{1-k}, \quad k \in \{0,1\}$$

分布函数：
$$F(x) = P(X \leq x) = \begin{cases}
0 & x < 0 \\
1-p & 0 \leq x < 1 \\
1 & x \geq 1
\end{cases}$$

其中 $0 < p < 1$ 是成功概率。

</details>

---

<details>
<summary>二项分布</summary>

概率质量函数：
$$P(X=k) = \binom{n}{k}p^k(1-p)^{n-k}, \quad k = 0,1,2,\ldots,n$$

分布函数：
$$F(x) = P(X \leq x) = \sum_{k=0}^{\lfloor x \rfloor}\binom{n}{k}p^k(1-p)^{n-k}$$

其中 $n$ 是试验次数，$0 < p < 1$ 是单次试验成功概率。

</details>

---

<details>
<summary>泊松分布</summary>

概率质量函数：
$$P(X=k) = \frac{\lambda^k e^{-\lambda}}{k!}, \quad k = 0,1,2,3,\ldots$$

分布函数：
$$F(x) = P(X \leq x) = \sum_{k=0}^{\lfloor x \rfloor}\frac{\lambda^k e^{-\lambda}}{k!}$$

其中 $\lambda > 0$ 是分布的参数，表示单位时间（或单位面积、体积等）内随机事件的平均发生次数。

</details>

---

<details>
<summary>超几何分布</summary>

概率质量函数：
$$P(X=k) = \frac{\binom{M}{k}\binom{N-M}{n-k}}{\binom{N}{n}}, \quad k = \max(0,n-N+M),\ldots,\min(n,M)$$

分布函数：
$$F(x) = P(X \leq x) = \sum_{i=\max(0,n-N+M)}^{\lfloor x \rfloor}\frac{\binom{M}{i}\binom{N-M}{n-i}}{\binom{N}{n}}$$

其中 $N$ 是总体大小，$M$ 是总体中具有某种特征的个体数，$n$ 是抽样数量。

</details>

---

<details>
<summary>几何分布</summary>

概率质量函数：
$$P(X=k) = (1-p)^{k-1}p, \quad k = 1,2,3,\ldots$$

分布函数：
$$F(x) = P(X \leq x) = \sum_{k=1}^{\lfloor x \rfloor}(1-p)^{k-1}p = 1-(1-p)^{\lfloor x \rfloor}$$

其中 $0 < p < 1$ 是每次试验成功的概率，$X$ 表示首次成功所需的试验次数。

</details>

---

<details>
<summary>负二项分布</summary>

概率质量函数：
$$P(X=k) = \binom{k+r-1}{k}p^r(1-p)^k, \quad k = 0,1,2,3,\ldots$$

分布函数：
$$F(x) = P(X \leq x) = \sum_{k=0}^{\lfloor x \rfloor}\binom{k+r-1}{k}p^r(1-p)^k$$

其中 $r > 0$ 是正整数（有时也推广到实数），表示我们想要观察到的成功次数，$0 < p < 1$ 是每次试验成功的概率。

</details>
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
                
                self.distribution_type = 'binomial'
                self.params = {'n': 10, 'p': 0.5}
                
                # Add a timer to debounce error messages
                self.error_timer = QTimer()
                self.error_timer.setSingleShot(True)
                self.last_error_time = 0
                
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
                try:
                    self.figure.clear()
                    ax = self.figure.add_subplot(111)
                    
                    # 根据分布类型绘制相应的图形
                    if self.distribution_type == 'bernoulli':
                        # 两点分布
                        p = self.params.get('p', 0.5)
                        
                        # 参数验证
                        if not 0 < p < 1:
                            raise ValueError("两点分布参数错误：p必须在(0,1)之间")
                        
                        x = [0, 1]
                        pmf = [1-p, p]
                        ax.bar(x, pmf, width=0.4, label='PMF', alpha=0.7, color='blue')
                        
                        # 分布函数
                        cdf_vals = [1-p, 1.0]
                        # 为分布函数创建正确的横坐标
                        x_cdf = [-0.5, 0, 0, 1, 1, 1.5]  # 对应阶梯函数的转折点
                        y_cdf = [0, 0, 1-p, 1-p, 1.0, 1.0]  # 对应阶梯函数的值
                        ax.plot(x_cdf, y_cdf, label='CDF', color='red', linewidth=2, drawstyle='steps-post')
                        
                        ax.set_xticks([0, 1])
                        ax.set_xlim(-0.5, 1.5)
                        ax.set_ylim(0, 1.1)
                        
                    elif self.distribution_type == 'binomial':
                        # 二项分布
                        n = self.params.get('n', 10)
                        p = self.params.get('p', 0.5)
                        
                        # 参数验证
                        if n <= 0 or not 0 < p < 1:
                            raise ValueError("二项分布参数错误：n必须大于0，p必须在(0,1)之间")
                        
                        x = np.arange(0, n+1)
                        pmf = binom.pmf(x, n, p)
                        ax.bar(x, pmf, width=0.4, label='PMF', alpha=0.7, color='blue')
                        
                        # 分布函数
                        cdf_vals = binom.cdf(x, n, p)
                        ax.step(np.concatenate([[-0.5], x, [x[-1]+0.5]]), 
                               np.concatenate([[0], cdf_vals, [cdf_vals[-1]]]), 
                               where='post', label='CDF', color='red', linewidth=2)
                        
                        ax.set_xlim(-0.5, n+0.5)
                        ax.set_ylim(0, 1.1)
                        
                    elif self.distribution_type == 'poisson':
                        # 泊松分布
                        lambda_ = self.params.get('lambda', 5)
                        
                        # 参数验证
                        if lambda_ <= 0:
                            raise ValueError("泊松分布参数错误：λ必须大于0")
                        
                        x_max = max(10, int(lambda_ + 4 * np.sqrt(lambda_)))
                        x = np.arange(0, x_max + 1)
                        pmf = poisson.pmf(x, lambda_)
                        ax.bar(x, pmf, width=0.4, label='PMF', alpha=0.7, color='blue')
                        
                        # 分布函数
                        cdf_vals = poisson.cdf(x, lambda_)
                        ax.step(np.concatenate([[-0.5], x, [x[-1]+0.5]]), 
                               np.concatenate([[0], cdf_vals, [cdf_vals[-1]]]), 
                               where='post', label='CDF', color='red', linewidth=2)
                        
                        ax.set_xlim(-0.5, x_max+0.5)
                        ax.set_ylim(0, 1.1)
                        
                    elif self.distribution_type == 'hypergeometric':
                        # 超几何分布
                        M = self.params.get('M', 50)
                        n = self.params.get('n', 10)
                        N = self.params.get('N', 20)
                        
                        # 参数验证
                        if M <= 0 or n <= 0 or N <= 0 or n > M or N > M:
                            raise ValueError("超几何分布参数错误：M、n、N必须大于0，且n≤M，N≤M")
                        
                        x = np.arange(max(0, N-M+n), min(n, N)+1)
                        from scipy.stats import hypergeom
                        pmf = hypergeom.pmf(x, M, n, N)
                        ax.bar(x, pmf, width=0.4, label='PMF', alpha=0.7, color='blue')
                        
                        # 分布函数
                        cdf_vals = hypergeom.cdf(x, M, n, N)
                        ax.step(np.concatenate([[-0.5], x, [x[-1]+0.5]]), 
                               np.concatenate([[0], cdf_vals, [cdf_vals[-1]]]), 
                               where='post', label='CDF', color='red', linewidth=2)
                        
                        ax.set_xlim(x[0]-0.5, x[-1]+0.5)
                        ax.set_ylim(0, 1.1)
                        
                    elif self.distribution_type == 'geometric':
                        # 几何分布
                        p = self.params.get('p', 0.5)
                        
                        # 参数验证
                        if not 0 < p < 1:
                            raise ValueError("几何分布参数错误：p必须在(0,1)之间")
                        
                        x = np.arange(1, 21)  # 显示前20项
                        from scipy.stats import geom
                        pmf = geom.pmf(x, p)
                        ax.bar(x, pmf, width=0.4, label='PMF', alpha=0.7, color='blue')
                        
                        # 分布函数
                        cdf_vals = geom.cdf(x, p)
                        ax.step(np.concatenate([[0], x, [x[-1]+0.5]]), 
                               np.concatenate([[0], cdf_vals, [cdf_vals[-1]]]), 
                               where='post', label='CDF', color='red', linewidth=2)
                        
                        ax.set_xlim(0.5, x[-1]+0.5)
                        ax.set_ylim(0, 1.1)
                        
                    elif self.distribution_type == 'negative_binomial':
                        # 负二项分布
                        r = self.params.get('r', 5)
                        p = self.params.get('p', 0.5)
                        
                        # 参数验证
                        if r <= 0 or not 0 < p < 1:
                            raise ValueError("负二项分布参数错误：r必须大于0，p必须在(0,1)之间")
                        
                        x = np.arange(0, 20)
                        from scipy.stats import nbinom
                        pmf = nbinom.pmf(x, r, p)
                        ax.bar(x, pmf, width=0.4, label='PMF', alpha=0.7, color='blue')
                        
                        # 分布函数
                        cdf_vals = nbinom.cdf(x, r, p)
                        ax.step(np.concatenate([[-0.5], x, [x[-1]+0.5]]), 
                               np.concatenate([[0], cdf_vals, [cdf_vals[-1]]]), 
                               where='post', label='CDF', color='red', linewidth=2)
                        
                        ax.set_xlim(-0.5, x[-1]+0.5)
                        ax.set_ylim(0, 1.1)
                    
                    ax.patch.set_alpha(0.1)
                    
                    if isDarkTheme():
                        for spine in ax.spines.values():
                            spine.set_color('white')
                        ax.tick_params(colors='white', which='both')
                        ax.set_xlabel('$k$', color='white')
                        ax.set_ylabel('$P(X=k)$', color='white')
                        ax.set_title(f'{self.get_dist_name()} 分布的概率质量函数与分布函数', color='white')
                        ax.grid(True, alpha=0.3)
                        ax.legend(labelcolor='white')
                    else:
                        for spine in ax.spines.values():
                            spine.set_color('black')
                        ax.tick_params(colors='black', which='both')
                        ax.set_xlabel('$k$', color='black')
                        ax.set_ylabel('$P(X=k)$', color='black')
                        ax.set_title(f'{self.get_dist_name()} 分布的概率质量函数与分布函数', color='black')
                        ax.grid(True, alpha=0.7)
                        ax.legend()
                    
                    self.figure.tight_layout()
                    self.canvas.draw()
                    
                except ValueError as ve:
                    # 处理参数错误
                    self._show_error_message(str(ve))
                    self.canvas.draw()  # 确保画布仍然更新，即使出错
                except Exception as e:
                    # 处理其他可能的错误
                    self._show_error_message(f"绘图过程中出现错误: {str(e)}")
                    self.canvas.draw()  # 确保画布仍然更新，即使出错
            
            def _show_error_message(self, message):
                """Show error message using Flyout with debouncing"""
                import time
                current_time = time.time()
                
                # Only show error if enough time has passed since last one
                if current_time - self.last_error_time > 0.5:  # 500ms debounce
                    TeachingTip.create(
                        target=self,
                        icon=InfoBarIcon.ERROR,
                        title='参数错误',
                        content=message,
                        isClosable=True
                    )
                    self.last_error_time = current_time
            
            def get_dist_name(self):
                names = {
                    'bernoulli': '两点',
                    'binomial': '二项',
                    'poisson': '泊松',
                    'hypergeometric': '超几何',
                    'geometric': '几何',
                    'negative_binomial': '负二项'
                }
                return names.get(self.distribution_type, '未知')
                
            def set_distribution(self, dist_type):
                self.distribution_type = dist_type
                # 设置默认参数
                if dist_type == 'bernoulli':
                    self.params = {'p': 0.5}
                elif dist_type == 'binomial':
                    self.params = {'n': 10, 'p': 0.5}
                elif dist_type == 'poisson':
                    self.params = {'lambda': 5}
                elif dist_type == 'hypergeometric':
                    self.params = {'M': 50, 'n': 10, 'N': 20}
                elif dist_type == 'geometric':
                    self.params = {'p': 0.5}
                elif dist_type == 'negative_binomial':
                    self.params = {'r': 5, 'p': 0.5}
                self.update_plot()

        def __init__(self, parent=None):
            super().__init__(parent)
            self.flow_layout = FlowLayout(self)
            
            # 控制容器
            self.control_container = QWidget()
            self.control_container.setFixedWidth(400)
            self.control_layout = QGridLayout(self.control_container)
            
            # 分布选择
            self.dist_label = BodyLabel("分布类型：", self)
            self.dist_combo = ComboBox(self)
            self.dist_combo.addItems([
                "两点分布", "二项分布", "泊松分布", 
                "超几何分布", "几何分布", "负二项分布"
            ])
            self.dist_combo.setCurrentIndex(1)  # 默认二项分布
            
            # 二项分布参数
            self.n_label = BodyLabel("n（试验次数）：", self)
            self.n_spin = CompactSpinBox(self)
            self.n_spin.setRange(1, 100)
            self.n_spin.setValue(10)
            self.n_slider = Slider(Qt.Horizontal, self)
            self.n_slider.setRange(1, 100)
            self.n_slider.setSingleStep(1)
            self.n_slider.setValue(10)
            
            self.p_label = BodyLabel("p（成功概率）：", self)
            self.p_spin = CompactDoubleSpinBox(self)
            self.p_spin.setRange(0.01, 0.99)
            self.p_spin.setSingleStep(0.01)
            self.p_spin.setValue(0.5)
            self.p_slider = Slider(Qt.Horizontal, self)
            self.p_slider.setRange(1, 99)
            self.p_slider.setSingleStep(1)
            self.p_slider.setValue(50)
            
            # 泊松分布参数
            self.lambda_label = BodyLabel("λ（参数）：", self)
            self.lambda_spin = CompactDoubleSpinBox(self)
            self.lambda_spin.setRange(0.1, 20)
            self.lambda_spin.setSingleStep(0.01)
            self.lambda_spin.setValue(5)
            self.lambda_slider = Slider(Qt.Horizontal, self)
            self.lambda_slider.setRange(10, 2000)
            self.lambda_slider.setSingleStep(1)
            self.lambda_slider.setValue(500)
            
            # 超几何分布参数
            self.M_label = BodyLabel("M（总体大小）：", self)
            self.M_spin = CompactSpinBox(self)
            self.M_spin.setRange(1, 100)
            self.M_spin.setValue(50)
            self.M_slider = Slider(Qt.Horizontal, self)
            self.M_slider.setRange(1, 100)
            self.M_slider.setSingleStep(1)
            self.M_slider.setValue(50)
            
            self.n_hyper_label = BodyLabel("n（成功总数）：", self)
            self.n_hyper_spin = CompactSpinBox(self)
            self.n_hyper_spin.setRange(1, 100)
            self.n_hyper_spin.setValue(10)
            self.n_hyper_slider = Slider(Qt.Horizontal, self)
            self.n_hyper_slider.setRange(1, 100)
            self.n_hyper_slider.setSingleStep(1)
            self.n_hyper_slider.setValue(10)
            
            self.N_label = BodyLabel("N（抽取数量）：", self)
            self.N_spin = CompactSpinBox(self)
            self.N_spin.setRange(1, 50)
            self.N_spin.setValue(20)
            self.N_slider = Slider(Qt.Horizontal, self)
            self.N_slider.setRange(1, 50)
            self.N_slider.setSingleStep(1)
            self.N_slider.setValue(20)
            
            # 几何分布参数
            self.p_geom_label = BodyLabel("p（成功概率）：", self)
            self.p_geom_spin = CompactDoubleSpinBox(self)
            self.p_geom_spin.setRange(0.01, 0.99)
            self.p_geom_spin.setSingleStep(0.01)
            self.p_geom_spin.setValue(0.5)
            self.p_geom_slider = Slider(Qt.Horizontal, self)
            self.p_geom_slider.setRange(1, 99)
            self.p_geom_slider.setSingleStep(1)
            self.p_geom_slider.setValue(50)
            
            # 负二项分布参数
            self.r_label = BodyLabel("r（成功次数）：", self)
            self.r_spin = CompactSpinBox(self)
            self.r_spin.setRange(1, 20)
            self.r_spin.setValue(5)
            self.r_slider = Slider(Qt.Horizontal, self)
            self.r_slider.setRange(1, 20)
            self.r_slider.setSingleStep(1)
            self.r_slider.setValue(5)
            
            self.p_neg_label = BodyLabel("p（成功概率）：", self)
            self.p_neg_spin = CompactDoubleSpinBox(self)
            self.p_neg_spin.setRange(0.01, 0.99)
            self.p_neg_spin.setSingleStep(0.01)
            self.p_neg_spin.setValue(0.5)
            self.p_neg_slider = Slider(Qt.Horizontal, self)
            self.p_neg_slider.setRange(1, 99)
            self.p_neg_slider.setSingleStep(1)
            self.p_neg_slider.setValue(50)
            
            # 添加所有控件到布局中，但初始时隐藏不需要的控件
            self.control_layout.addWidget(self.dist_label, 0, 0)
            self.control_layout.addWidget(self.dist_combo, 0, 1, 1, 2)
            
            # 二项分布控件
            self.control_layout.addWidget(self.n_label, 1, 0)
            self.control_layout.addWidget(self.n_spin, 1, 1)
            self.control_layout.addWidget(self.n_slider, 1, 2)
            self.control_layout.addWidget(self.p_label, 2, 0)
            self.control_layout.addWidget(self.p_spin, 2, 1)
            self.control_layout.addWidget(self.p_slider, 2, 2)
            
            # 泊松分布控件
            self.control_layout.addWidget(self.lambda_label, 3, 0)
            self.control_layout.addWidget(self.lambda_spin, 3, 1)
            self.control_layout.addWidget(self.lambda_slider, 3, 2)
            
            # 超几何分布控件
            self.control_layout.addWidget(self.M_label, 4, 0)
            self.control_layout.addWidget(self.M_spin, 4, 1)
            self.control_layout.addWidget(self.M_slider, 4, 2)
            self.control_layout.addWidget(self.n_hyper_label, 5, 0)
            self.control_layout.addWidget(self.n_hyper_spin, 5, 1)
            self.control_layout.addWidget(self.n_hyper_slider, 5, 2)
            self.control_layout.addWidget(self.N_label, 6, 0)
            self.control_layout.addWidget(self.N_spin, 6, 1)
            self.control_layout.addWidget(self.N_slider, 6, 2)
            
            # 几何分布控件
            self.control_layout.addWidget(self.p_geom_label, 7, 0)
            self.control_layout.addWidget(self.p_geom_spin, 7, 1)
            self.control_layout.addWidget(self.p_geom_slider, 7, 2)
            
            # 负二项分布控件
            self.control_layout.addWidget(self.r_label, 8, 0)
            self.control_layout.addWidget(self.r_spin, 8, 1)
            self.control_layout.addWidget(self.r_slider, 8, 2)
            self.control_layout.addWidget(self.p_neg_label, 9, 0)
            self.control_layout.addWidget(self.p_neg_spin, 9, 1)
            self.control_layout.addWidget(self.p_neg_slider, 9, 2)
            
            # 初始时只显示二项分布控件
            self.show_only_binomial_controls()
            
            # 连接信号
            self.dist_combo.currentTextChanged.connect(self.on_distribution_changed)
            self.setup_connections()
            
            # 添加控制容器到流式布局
            self.flow_layout.addWidget(self.control_container)
            
            # 绘图区域
            self.plot_widget = self.PlotWidget(self)
            self.flow_layout.addWidget(self.plot_widget)
            
            cfg.themeChanged.connect(lambda: self.plot_widget.update_plot())
            
        def setup_connections(self):
            # 二项分布连接
            self.n_spin.valueChanged.connect(self.n_slider.setValue)
            self.n_slider.valueChanged.connect(self.n_spin.setValue)
            self.p_spin.valueChanged.connect(
                lambda: self.p_slider.setValue(self.p_spin.value() * 100)
            )
            self.p_slider.valueChanged.connect(
                lambda: self.p_spin.setValue(self.p_slider.value() / 100)
            )
            
            # 泊松分布连接
            self.lambda_spin.valueChanged.connect(
                lambda: self.lambda_slider.setValue(self.lambda_spin.value() * 100)
            )
            self.lambda_slider.valueChanged.connect(
                lambda: self.lambda_spin.setValue(self.lambda_slider.value() / 100)
            )
            
            # 超几何分布连接
            self.M_spin.valueChanged.connect(self.M_slider.setValue)
            self.M_slider.valueChanged.connect(self.M_spin.setValue)
            self.n_hyper_spin.valueChanged.connect(self.n_hyper_slider.setValue)
            self.n_hyper_slider.valueChanged.connect(self.n_hyper_spin.setValue)
            self.N_spin.valueChanged.connect(self.N_slider.setValue)
            self.N_slider.valueChanged.connect(self.N_spin.setValue)
            
            # 几何分布连接
            self.p_geom_spin.valueChanged.connect(
                lambda: self.p_geom_slider.setValue(self.p_geom_spin.value() * 100)
            )
            self.p_geom_slider.valueChanged.connect(
                lambda: self.p_geom_spin.setValue(self.p_geom_slider.value() / 100)
            )
            
            # 负二项分布连接
            self.r_spin.valueChanged.connect(self.r_slider.setValue)
            self.r_slider.valueChanged.connect(self.r_spin.setValue)
            self.p_neg_spin.valueChanged.connect(
                lambda: self.p_neg_slider.setValue(self.p_neg_spin.value() * 100)
            )
            self.p_neg_slider.valueChanged.connect(
                lambda: self.p_neg_spin.setValue(self.p_neg_slider.value() / 100)
            )
            
            # 更新绘图的连接
            self.n_spin.valueChanged.connect(self.update_parameters)
            self.p_spin.valueChanged.connect(self.update_parameters)
            self.lambda_spin.valueChanged.connect(self.update_parameters)
            self.M_spin.valueChanged.connect(self.update_parameters)
            self.n_hyper_spin.valueChanged.connect(self.update_parameters)
            self.N_spin.valueChanged.connect(self.update_parameters)
            self.p_geom_spin.valueChanged.connect(self.update_parameters)
            self.r_spin.valueChanged.connect(self.update_parameters)
            self.p_neg_spin.valueChanged.connect(self.update_parameters)
        
        def hide_all_param_controls(self):
            # 隐藏所有参数控件
            for i in range(1, self.control_layout.rowCount()):
                for j in range(self.control_layout.columnCount()):
                    item = self.control_layout.itemAtPosition(i, j)
                    if item and item.widget():
                        item.widget().hide()
        
        def show_only_binomial_controls(self):
            self.hide_all_param_controls()
            # 显示二项分布控件
            self.n_label.show()
            self.n_spin.show()
            self.n_slider.show()
            self.p_label.show()
            self.p_spin.show()
            self.p_slider.show()
        
        def show_only_poisson_controls(self):
            self.hide_all_param_controls()
            # 显示泊松分布控件
            self.lambda_label.show()
            self.lambda_spin.show()
            self.lambda_slider.show()
        
        def show_only_hypergeometric_controls(self):
            self.hide_all_param_controls()
            # 显示超几何分布控件
            self.M_label.show()
            self.M_spin.show()
            self.M_slider.show()
            self.n_hyper_label.show()
            self.n_hyper_spin.show()
            self.n_hyper_slider.show()
            self.N_label.show()
            self.N_spin.show()
            self.N_slider.show()
        
        def show_only_geometric_controls(self):
            self.hide_all_param_controls()
            # 显示几何分布控件
            self.p_geom_label.show()
            self.p_geom_spin.show()
            self.p_geom_slider.show()
        
        def show_only_negative_binomial_controls(self):
            self.hide_all_param_controls()
            # 显示负二项分布控件
            self.r_label.show()
            self.r_spin.show()
            self.r_slider.show()
            self.p_neg_label.show()
            self.p_neg_spin.show()
            self.p_neg_slider.show()
        
        def show_only_bernoulli_controls(self):
            self.hide_all_param_controls()
            # 显示两点分布控件
            self.p_label.show()
            self.p_spin.show()
            self.p_slider.show()
        
        def on_distribution_changed(self, text):
            if text == "两点分布":
                self.show_only_bernoulli_controls()
                self.plot_widget.set_distribution('bernoulli')
            elif text == "二项分布":
                self.show_only_binomial_controls()
                self.plot_widget.set_distribution('binomial')
            elif text == "泊松分布":
                self.show_only_poisson_controls()
                self.plot_widget.set_distribution('poisson')
            elif text == "超几何分布":
                self.show_only_hypergeometric_controls()
                self.plot_widget.set_distribution('hypergeometric')
            elif text == "几何分布":
                self.show_only_geometric_controls()
                self.plot_widget.set_distribution('geometric')
            elif text == "负二项分布":
                self.show_only_negative_binomial_controls()
                self.plot_widget.set_distribution('negative_binomial')
            
            self.update_parameters()
        
        def update_parameters(self):
            dist_type = self.dist_combo.currentText()
            
            try:
                if dist_type == "两点分布":
                    p = self.p_spin.value()
                    if not 0 < p < 1:
                        raise ValueError("两点分布参数错误：p必须在(0,1)之间")
                    self.plot_widget.params = {'p': p}
                elif dist_type == "二项分布":
                    n = self.n_spin.value()
                    p = self.p_spin.value()
                    if n <= 0 or not 0 < p < 1:
                        raise ValueError("二项分布参数错误：n必须大于0，p必须在(0,1)之间")
                    self.plot_widget.params = {
                        'n': n,
                        'p': p
                    }
                elif dist_type == "泊松分布":
                    lambda_val = self.lambda_spin.value()
                    if lambda_val <= 0:
                        raise ValueError("泊松分布参数错误：λ必须大于0")
                    self.plot_widget.params = {'lambda': lambda_val}
                elif dist_type == "超几何分布":
                    M = self.M_spin.value()
                    n = self.n_hyper_spin.value()
                    N = self.N_spin.value()
                    if M <= 0 or n <= 0 or N <= 0 or n > M or N > M:
                        raise ValueError("超几何分布参数错误：M、n、N必须大于0，且n≤M，N≤M")
                    self.plot_widget.params = {
                        'M': M,
                        'n': n,
                        'N': N
                    }
                elif dist_type == "几何分布":
                    p = self.p_geom_spin.value()
                    if not 0 < p < 1:
                        raise ValueError("几何分布参数错误：p必须在(0,1)之间")
                    self.plot_widget.params = {'p': p}
                elif dist_type == "负二项分布":
                    r = self.r_spin.value()
                    p = self.p_neg_spin.value()
                    if r <= 0 or not 0 < p < 1:
                        raise ValueError("负二项分布参数错误：r必须大于0，p必须在(0,1)之间")
                    self.plot_widget.params = {
                        'r': r,
                        'p': p
                    }
                
                self.plot_widget.update_plot()
            except ValueError as ve:
                self.plot_widget._show_error_message(str(ve))
            except Exception as e:
                self.plot_widget._show_error_message(f"更新参数时出现错误: {str(e)}")

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
            experimentInterface = DiscretePDF.ExpInterface()
            scroll_area.setWidget(experimentInterface)
            scroll_area.setWidgetResizable(True)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            FluentStyleSheet.NAVIGATION_INTERFACE.apply(scroll_area)
            return scroll_area

        super().__init__(
            '离散型随机变量概率分布',
            descriptionFactory=create_description_interface,
            experimentFactory=create_experiment_interface,
            parent=parent
        )