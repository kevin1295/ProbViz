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
from scipy.stats import norm, uniform, expon, t as student_t, gamma, beta
import numpy as np

from .ExpWidget import ExpWidget
from ..common.MarkdownKatex import MarkdownKaTeXWidget
from ..common.config import cfg


class ContinuousPDF(ExpWidget):
    
    desc = r"""
# 连续型随机变量概率分布

连续型随机变量是指其可能取值充满某个区间或多个区间的随机变量。对于连续型随机变量 $X$，存在一个非负可积函数 $f(x)$，使得对任意实数 $a < b$，有：

$$P(a \leq X \leq b) = \int_a^b f(x)dx$$

其中 $f(x)$ 称为 $X$ 的概率密度函数（PDF），满足：

1. $f(x) \geq 0$
2. $\int_{-\infty}^{\infty} f(x) dx = 1$

常见的连续型随机变量分布包括：

---

<details>
<summary>均匀分布</summary>

概率密度函数：
$$f(x) = \begin{cases}
\frac{1}{b-a} & a \leq x \leq b \\
0 & \text{其他}
\end{cases}$$

分布函数：
$$F(x) = \begin{cases}
0 & x < a \\
\frac{x-a}{b-a} & a \leq x < b \\
1 & x \geq b
\end{cases}$$

其中 $a$ 和 $b$ 分别是分布的下界和上界。

</details>

---

<details>
<summary>正态分布（高斯分布）</summary>

概率密度函数：
$$f(x) = \frac{1}{\sqrt{2\pi\sigma^2}}e^{-\frac{(x-\mu)^2}{2\sigma^2}}$$

其中 $\mu$ 是均值，$\sigma > 0$ 是标准差。

分布函数：
$$F(x) = \frac{1}{2}\left[1 + \operatorname{erf}\left(\frac{x-\mu}{\sigma\sqrt{2}}\right)\right]$$

其中 $\operatorname{erf}$ 是误差函数。

</details>

---

<details>
<summary>指数分布</summary>

概率密度函数：
$$f(x) = \begin{cases}
\lambda e^{-\lambda x} & x \geq 0 \\
0 & x < 0
\end{cases}$$

分布函数：
$$F(x) = \begin{cases}
1 - e^{-\lambda x} & x \geq 0 \\
0 & x < 0
\end{cases}$$

其中 $\lambda > 0$ 是率参数，表示单位时间内事件发生的平均次数。

</details>

---

<details>
<summary>t分布（学生t分布）</summary>

概率密度函数：
$$f(x) = \frac{\Gamma\left(\frac{\nu+1}{2}\right)}{\sqrt{\nu\pi}\,\Gamma\left(\frac{\nu}{2}\right)}\left(1+\frac{x^2}{\nu}\right)^{-\frac{\nu+1}{2}}$$

其中 $\nu > 0$ 是自由度，$\Gamma$ 是伽马函数。

</details>

---

<details>
<summary>伽马分布</summary>

概率密度函数：
$$f(x) = \frac{\beta^\alpha}{\Gamma(\alpha)}x^{\alpha-1}e^{-\beta x}$$

其中 $\alpha > 0$ 是形状参数，$\beta > 0$ 是速率参数。

分布函数：
$$F(x) = \frac{\gamma(\alpha, \beta x)}{\Gamma(\alpha)}$$

其中 $\gamma(\alpha, \beta x)$ 是不完全伽马函数。

</details>

---

<details>
<summary>贝塔分布</summary>

概率密度函数：
$$f(x) = \frac{1}{B(\alpha, \beta)}x^{\alpha-1}(1-x)^{\beta-1}$$

其中 $0 \leq x \leq 1$，$\alpha, \beta > 0$ 是形状参数，$B(\alpha, \beta)$ 是贝塔函数。

分布函数：
$$F(x) = I_x(\alpha, \beta)$$

其中 $I_x(\alpha, \beta)$ 是正则化不完全贝塔函数。

</details>

---

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
                
                self.distribution_type = 'normal'
                self.params = {'mu': 0, 'sigma': 1}
                
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
                    if self.distribution_type == 'uniform':
                        # 均匀分布
                        a = self.params.get('a', 0)
                        b = self.params.get('b', 1)
                        
                        # 参数验证
                        if a >= b:
                            raise ValueError("均匀分布参数错误：a必须小于b")
                        
                        # 定义x范围
                        x_range = b - a
                        x = np.linspace(a - 0.1 * x_range, b + 0.1 * x_range, 1000)
                        
                        # PDF
                        pdf_values = uniform.pdf(x, loc=a, scale=b-a)
                        ax.plot(x, pdf_values, label='PDF', color='blue', linewidth=2)
                        
                        # CDF
                        cdf_values = uniform.cdf(x, loc=a, scale=b-a)
                        ax.plot(x, cdf_values, label='CDF', color='red', linewidth=2)
                        
                        ax.set_xlim(a - 0.1 * x_range, b + 0.1 * x_range)
                        ax.set_ylim(0, max(1, max(pdf_values)) * 1.1)
                        
                    elif self.distribution_type == 'normal':
                        # 正态分布
                        mu = self.params.get('mu', 0)
                        sigma = self.params.get('sigma', 1)
                        
                        # 参数验证
                        if sigma <= 0:
                            raise ValueError("正态分布参数错误：标准差σ必须大于0")
                        
                        # 定义x范围
                        x = np.linspace(mu - 4*sigma, mu + 4*sigma, 1000)
                        
                        # PDF
                        pdf_values = norm.pdf(x, loc=mu, scale=sigma)
                        ax.plot(x, pdf_values, label='PDF', color='blue', linewidth=2)
                        
                        # CDF
                        cdf_values = norm.cdf(x, loc=mu, scale=sigma)
                        ax.plot(x, cdf_values, label='CDF', color='red', linewidth=2)
                        
                        ax.set_xlim(mu - 4*sigma, mu + 4*sigma)
                        ax.set_ylim(0, max(1, max(pdf_values)) * 1.1)
                        
                    elif self.distribution_type == 'exponential':
                        # 指数分布
                        lam = self.params.get('lambda', 1)
                        
                        # 参数验证
                        if lam <= 0:
                            raise ValueError("指数分布参数错误：率参数λ必须大于0")
                        
                        # 定义x范围
                        x = np.linspace(0, 5/lam, 1000)
                        
                        # PDF
                        pdf_values = expon.pdf(x, scale=1/lam)
                        ax.plot(x, pdf_values, label='PDF', color='blue', linewidth=2)
                        
                        # CDF
                        cdf_values = expon.cdf(x, scale=1/lam)
                        ax.plot(x, cdf_values, label='CDF', color='red', linewidth=2)
                        
                        ax.set_xlim(0, 5/lam)
                        ax.set_ylim(0, max(1, max(pdf_values)) * 1.1)
                        
                    elif self.distribution_type == 't':
                        # t分布
                        df = self.params.get('df', 5)
                        
                        # 参数验证
                        if df <= 0:
                            raise ValueError("t分布参数错误：自由度ν必须大于0")
                        
                        # 定义x范围
                        x = np.linspace(-5, 5, 1000)
                        
                        # PDF
                        pdf_values = student_t.pdf(x, df=df)
                        ax.plot(x, pdf_values, label='PDF', color='blue', linewidth=2)
                        
                        # CDF
                        cdf_values = student_t.cdf(x, df=df)
                        ax.plot(x, cdf_values, label='CDF', color='red', linewidth=2)
                        
                        ax.set_xlim(-5, 5)
                        ax.set_ylim(0, max(1, max(pdf_values)) * 1.1)
                        
                    elif self.distribution_type == 'gamma':
                        # 伽马分布
                        alpha = self.params.get('alpha', 2)
                        beta = self.params.get('beta', 1)
                        
                        # 参数验证
                        if alpha <= 0 or beta <= 0:
                            raise ValueError("伽马分布参数错误：形状参数α和速率参数β都必须大于0")
                        
                        # 定义x范围
                        x = np.linspace(0, 10, 1000)
                        
                        # PDF
                        pdf_values = gamma.pdf(x, a=alpha, scale=1/beta)
                        ax.plot(x, pdf_values, label='PDF', color='blue', linewidth=2)
                        
                        # CDF
                        cdf_values = gamma.cdf(x, a=alpha, scale=1/beta)
                        ax.plot(x, cdf_values, label='CDF', color='red', linewidth=2)
                        
                        ax.set_xlim(0, 10)
                        ax.set_ylim(0, max(1, max(pdf_values)) * 1.1)
                        
                    elif self.distribution_type == 'beta':
                        # 贝塔分布
                        alpha = self.params.get('alpha', 2)
                        beta = self.params.get('beta', 5)
                        
                        # 参数验证
                        if alpha <= 0 or beta <= 0:
                            raise ValueError("贝塔分布参数错误：形状参数α和β都必须大于0")
                        
                        # 定义x范围
                        x = np.linspace(0, 1, 1000)
                        
                        # PDF
                        pdf_values = beta.pdf(x, a=alpha, b=beta)
                        ax.plot(x, pdf_values, label='PDF', color='blue', linewidth=2)
                        
                        # CDF
                        cdf_values = beta.cdf(x, a=alpha, b=beta)
                        ax.plot(x, cdf_values, label='CDF', color='red', linewidth=2)
                        
                        ax.set_xlim(0, 1)
                        ax.set_ylim(0, max(1, max(pdf_values)) * 1.1)
                    
                    ax.patch.set_alpha(0.1)
                    
                    if isDarkTheme():
                        for spine in ax.spines.values():
                            spine.set_color('white')
                        ax.tick_params(colors='white', which='both')
                        ax.set_xlabel('$x$', color='white')
                        ax.set_ylabel('$f(x)$', color='white')
                        ax.set_title(f'{self.get_dist_name()} 分布的概率密度函数与分布函数', color='white')
                        ax.grid(True, alpha=0.3)
                        ax.legend(labelcolor='white')
                    else:
                        for spine in ax.spines.values():
                            spine.set_color('black')
                        ax.tick_params(colors='black', which='both')
                        ax.set_xlabel('$x$', color='black')
                        ax.set_ylabel('$f(x)$', color='black')
                        ax.set_title(f'{self.get_dist_name()} 分布的概率密度函数与分布函数', color='black')
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
                    'uniform': '均匀',
                    'normal': '正态',
                    'exponential': '指数',
                    't': 't',
                    'gamma': '伽马',
                    'beta': '贝塔'
                }
                return names.get(self.distribution_type, '未知')
                
            def set_distribution(self, dist_type):
                self.distribution_type = dist_type
                # 设置默认参数
                if dist_type == 'uniform':
                    self.params = {'a': 0, 'b': 1}
                elif dist_type == 'normal':
                    self.params = {'mu': 0, 'sigma': 1}
                elif dist_type == 'exponential':
                    self.params = {'lambda': 1}
                elif dist_type == 't':
                    self.params = {'df': 5}
                elif dist_type == 'gamma':
                    self.params = {'alpha': 2, 'beta': 1}
                elif dist_type == 'beta':
                    self.params = {'alpha': 2, 'beta': 5}
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
                "均匀分布", "正态分布", "指数分布", 
                "t分布", "伽马分布", "贝塔分布"
            ])
            self.dist_combo.setCurrentIndex(1)  # 默认正态分布
            
            # 均匀分布参数
            self.a_label = BodyLabel("a（下界）：", self)
            self.a_spin = CompactDoubleSpinBox(self)
            self.a_spin.setRange(-10, 10)
            self.a_spin.setSingleStep(0.01)
            self.a_spin.setValue(0)
            self.a_slider = Slider(Qt.Horizontal, self)
            self.a_slider.setRange(-1000, 1000)
            self.a_slider.setSingleStep(1)
            self.a_slider.setValue(0)
            
            self.b_label = BodyLabel("b（上界）：", self)
            self.b_spin = CompactDoubleSpinBox(self)
            self.b_spin.setRange(0, 20)
            self.b_spin.setSingleStep(0.01)
            self.b_spin.setValue(10)
            self.b_slider = Slider(Qt.Horizontal, self)
            self.b_slider.setRange(0, 2000)
            self.b_slider.setSingleStep(1)
            self.b_slider.setValue(1000)
            
            # 正态分布参数
            self.mu_label = BodyLabel("μ（均值）：", self)
            self.mu_spin = CompactDoubleSpinBox(self)
            self.mu_spin.setRange(-10, 10)
            self.mu_spin.setSingleStep(0.01)
            self.mu_spin.setValue(0)
            self.mu_slider = Slider(Qt.Horizontal, self)
            self.mu_slider.setRange(-1000, 1000)
            self.mu_slider.setSingleStep(1)
            self.mu_slider.setValue(0)
            
            self.sigma_label = BodyLabel("σ（标准差）：", self)
            self.sigma_spin = CompactDoubleSpinBox(self)
            self.sigma_spin.setRange(0.1, 10)
            self.sigma_spin.setSingleStep(0.1)
            self.sigma_spin.setValue(1)
            self.sigma_slider = Slider(Qt.Horizontal, self)
            self.sigma_slider.setRange(1, 100)
            self.sigma_slider.setSingleStep(1)
            self.sigma_slider.setValue(10)
            
            # 指数分布参数
            self.lambda_exp_label = BodyLabel("λ（率参数）：", self)
            self.lambda_exp_spin = CompactDoubleSpinBox(self)
            self.lambda_exp_spin.setRange(0.1, 10)
            self.lambda_exp_spin.setSingleStep(0.1)
            self.lambda_exp_spin.setValue(1)
            self.lambda_exp_slider = Slider(Qt.Horizontal, self)
            self.lambda_exp_slider.setRange(1, 100)
            self.lambda_exp_slider.setSingleStep(1)
            self.lambda_exp_slider.setValue(10)
            
            # t分布参数
            self.df_label = BodyLabel("ν（自由度）：", self)
            self.df_spin = CompactSpinBox(self)
            self.df_spin.setRange(1, 100)
            self.df_spin.setValue(5)
            self.df_slider = Slider(Qt.Horizontal, self)
            self.df_slider.setRange(1, 100)
            self.df_slider.setSingleStep(1)
            self.df_slider.setValue(5)
            
            # 伽马分布参数
            self.alpha_gamma_label = BodyLabel("α（形状参数）：", self)
            self.alpha_gamma_spin = CompactDoubleSpinBox(self)
            self.alpha_gamma_spin.setRange(0.1, 20)
            self.alpha_gamma_spin.setSingleStep(0.1)
            self.alpha_gamma_spin.setValue(2)
            self.alpha_gamma_slider = Slider(Qt.Horizontal, self)
            self.alpha_gamma_slider.setRange(1, 200)
            self.alpha_gamma_slider.setSingleStep(1)
            self.alpha_gamma_slider.setValue(20)
            
            self.beta_gamma_label = BodyLabel("β（速率参数）：", self)
            self.beta_gamma_spin = CompactDoubleSpinBox(self)
            self.beta_gamma_spin.setRange(0.1, 10)
            self.beta_gamma_spin.setSingleStep(0.1)
            self.beta_gamma_spin.setValue(1)
            self.beta_gamma_slider = Slider(Qt.Horizontal, self)
            self.beta_gamma_slider.setRange(1, 100)
            self.beta_gamma_slider.setSingleStep(1)
            self.beta_gamma_slider.setValue(10)
            
            # 贝塔分布参数
            self.alpha_beta_label = BodyLabel("α（形状参数）：", self)
            self.alpha_beta_spin = CompactDoubleSpinBox(self)
            self.alpha_beta_spin.setRange(0.1, 20)
            self.alpha_beta_spin.setSingleStep(0.1)
            self.alpha_beta_spin.setValue(2)
            self.alpha_beta_slider = Slider(Qt.Horizontal, self)
            self.alpha_beta_slider.setRange(1, 200)
            self.alpha_beta_slider.setSingleStep(1)
            self.alpha_beta_slider.setValue(20)
            
            self.beta_beta_label = BodyLabel("β（形状参数）：", self)
            self.beta_beta_spin = CompactDoubleSpinBox(self)
            self.beta_beta_spin.setRange(0.1, 20)
            self.beta_beta_spin.setSingleStep(0.1)
            self.beta_beta_spin.setValue(5)
            self.beta_beta_slider = Slider(Qt.Horizontal, self)
            self.beta_beta_slider.setRange(1, 200)
            self.beta_beta_slider.setSingleStep(1)
            self.beta_beta_slider.setValue(50)
            
            # 添加所有控件到布局中，但初始时隐藏不需要的控件
            self.control_layout.addWidget(self.dist_label, 0, 0)
            self.control_layout.addWidget(self.dist_combo, 0, 1, 1, 2)
            
            # 均匀分布控件
            self.control_layout.addWidget(self.a_label, 1, 0)
            self.control_layout.addWidget(self.a_spin, 1, 1)
            self.control_layout.addWidget(self.a_slider, 1, 2)
            self.control_layout.addWidget(self.b_label, 2, 0)
            self.control_layout.addWidget(self.b_spin, 2, 1)
            self.control_layout.addWidget(self.b_slider, 2, 2)
            
            # 正态分布控件
            self.control_layout.addWidget(self.mu_label, 3, 0)
            self.control_layout.addWidget(self.mu_spin, 3, 1)
            self.control_layout.addWidget(self.mu_slider, 3, 2)
            self.control_layout.addWidget(self.sigma_label, 4, 0)
            self.control_layout.addWidget(self.sigma_spin, 4, 1)
            self.control_layout.addWidget(self.sigma_slider, 4, 2)
            
            # 指数分布控件
            self.control_layout.addWidget(self.lambda_exp_label, 5, 0)
            self.control_layout.addWidget(self.lambda_exp_spin, 5, 1)
            self.control_layout.addWidget(self.lambda_exp_slider, 5, 2)
            
            # t分布控件
            self.control_layout.addWidget(self.df_label, 6, 0)
            self.control_layout.addWidget(self.df_spin, 6, 1)
            self.control_layout.addWidget(self.df_slider, 6, 2)
            
            # 伽马分布控件
            self.control_layout.addWidget(self.alpha_gamma_label, 7, 0)
            self.control_layout.addWidget(self.alpha_gamma_spin, 7, 1)
            self.control_layout.addWidget(self.alpha_gamma_slider, 7, 2)
            self.control_layout.addWidget(self.beta_gamma_label, 8, 0)
            self.control_layout.addWidget(self.beta_gamma_spin, 8, 1)
            self.control_layout.addWidget(self.beta_gamma_slider, 8, 2)
            
            # 贝塔分布控件
            self.control_layout.addWidget(self.alpha_beta_label, 9, 0)
            self.control_layout.addWidget(self.alpha_beta_spin, 9, 1)
            self.control_layout.addWidget(self.alpha_beta_slider, 9, 2)
            self.control_layout.addWidget(self.beta_beta_label, 10, 0)
            self.control_layout.addWidget(self.beta_beta_spin, 10, 1)
            self.control_layout.addWidget(self.beta_beta_slider, 10, 2)
            
            # 初始时只显示正态分布控件
            self.show_only_normal_controls()
            
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
            # 均匀分布连接
            self.a_spin.valueChanged.connect(
                lambda: self.a_slider.setValue(self.a_spin.value() * 100)
            )
            self.a_slider.valueChanged.connect(
                lambda: self.a_spin.setValue(self.a_slider.value() / 100)
            )
            self.b_spin.valueChanged.connect(
                lambda: self.b_slider.setValue(self.b_spin.value() * 100)
            )
            self.b_slider.valueChanged.connect(
                lambda: self.b_spin.setValue(self.b_slider.value() / 100)
            )
            
            # 正态分布连接
            self.mu_spin.valueChanged.connect(
                lambda: self.mu_slider.setValue(self.mu_spin.value() * 100)
            )
            self.mu_slider.valueChanged.connect(
                lambda: self.mu_spin.setValue(self.mu_slider.value() / 100)
            )
            self.sigma_spin.valueChanged.connect(
                lambda: self.sigma_slider.setValue(self.sigma_spin.value() * 100)
            )
            self.sigma_slider.valueChanged.connect(
                lambda: self.sigma_spin.setValue(self.sigma_slider.value() / 100)
            )
            
            # 指数分布连接
            self.lambda_exp_spin.valueChanged.connect(
                lambda: self.lambda_exp_slider.setValue(self.lambda_exp_spin.value() * 100)
            )
            self.lambda_exp_slider.valueChanged.connect(
                lambda: self.lambda_exp_spin.setValue(self.lambda_exp_slider.value() / 100)
            )
            
            # t分布连接
            self.df_spin.valueChanged.connect(self.df_slider.setValue)
            self.df_slider.valueChanged.connect(self.df_spin.setValue)
            
            # 伽马分布连接
            self.alpha_gamma_spin.valueChanged.connect(
                lambda: self.alpha_gamma_slider.setValue(self.alpha_gamma_spin.value() * 10)
            )
            self.alpha_gamma_slider.valueChanged.connect(
                lambda: self.alpha_gamma_spin.setValue(self.alpha_gamma_slider.value() / 10)
            )
            self.beta_gamma_spin.valueChanged.connect(
                lambda: self.beta_gamma_slider.setValue(self.beta_gamma_spin.value() * 10)
            )
            self.beta_gamma_slider.valueChanged.connect(
                lambda: self.beta_gamma_spin.setValue(self.beta_gamma_slider.value() / 10)
            )
            
            # 贝塔分布连接
            self.alpha_beta_spin.valueChanged.connect(
                lambda: self.alpha_beta_slider.setValue(self.alpha_beta_spin.value() * 10)
            )
            self.alpha_beta_slider.valueChanged.connect(
                lambda: self.alpha_beta_spin.setValue(self.alpha_beta_slider.value() / 10)
            )
            self.beta_beta_spin.valueChanged.connect(
                lambda: self.beta_beta_slider.setValue(self.beta_beta_spin.value() * 10)
            )
            self.beta_beta_slider.valueChanged.connect(
                lambda: self.beta_beta_spin.setValue(self.beta_beta_slider.value() / 10)
            )
            
            # 更新绘图的连接
            self.a_spin.valueChanged.connect(self.update_parameters)
            self.b_spin.valueChanged.connect(self.update_parameters)
            self.mu_spin.valueChanged.connect(self.update_parameters)
            self.sigma_spin.valueChanged.connect(self.update_parameters)
            self.lambda_exp_spin.valueChanged.connect(self.update_parameters)
            self.df_spin.valueChanged.connect(self.update_parameters)
            self.alpha_gamma_spin.valueChanged.connect(self.update_parameters)
            self.beta_gamma_spin.valueChanged.connect(self.update_parameters)
            self.alpha_beta_spin.valueChanged.connect(self.update_parameters)
            self.beta_beta_spin.valueChanged.connect(self.update_parameters)
        
        def hide_all_param_controls(self):
            # 隐藏所有参数控件
            for i in range(1, self.control_layout.rowCount()):
                for j in range(self.control_layout.columnCount()):
                    item = self.control_layout.itemAtPosition(i, j)
                    if item and item.widget():
                        item.widget().hide()
        
        def show_only_uniform_controls(self):
            self.hide_all_param_controls()
            # 显示均匀分布控件
            self.a_label.show()
            self.a_spin.show()
            self.a_slider.show()
            self.b_label.show()
            self.b_spin.show()
            self.b_slider.show()
        
        def show_only_normal_controls(self):
            self.hide_all_param_controls()
            # 显示正态分布控件
            self.mu_label.show()
            self.mu_spin.show()
            self.mu_slider.show()
            self.sigma_label.show()
            self.sigma_spin.show()
            self.sigma_slider.show()
        
        def show_only_exponential_controls(self):
            self.hide_all_param_controls()
            # 显示指数分布控件
            self.lambda_exp_label.show()
            self.lambda_exp_spin.show()
            self.lambda_exp_slider.show()
        
        def show_only_t_controls(self):
            self.hide_all_param_controls()
            # 显示t分布控件
            self.df_label.show()
            self.df_spin.show()
            self.df_slider.show()
        
        def show_only_gamma_controls(self):
            self.hide_all_param_controls()
            # 显示伽马分布控件
            self.alpha_gamma_label.show()
            self.alpha_gamma_spin.show()
            self.alpha_gamma_slider.show()
            self.beta_gamma_label.show()
            self.beta_gamma_spin.show()
            self.beta_gamma_slider.show()
        
        def show_only_beta_controls(self):
            self.hide_all_param_controls()
            # 显示贝塔分布控件
            self.alpha_beta_label.show()
            self.alpha_beta_spin.show()
            self.alpha_beta_slider.show()
            self.beta_beta_label.show()
            self.beta_beta_spin.show()
            self.beta_beta_slider.show()
        
        def on_distribution_changed(self, text):
            if text == "均匀分布":
                self.show_only_uniform_controls()
                self.plot_widget.set_distribution('uniform')
            elif text == "正态分布":
                self.show_only_normal_controls()
                self.plot_widget.set_distribution('normal')
            elif text == "指数分布":
                self.show_only_exponential_controls()
                self.plot_widget.set_distribution('exponential')
            elif text == "t分布":
                self.show_only_t_controls()
                self.plot_widget.set_distribution('t')
            elif text == "伽马分布":
                self.show_only_gamma_controls()
                self.plot_widget.set_distribution('gamma')
            elif text == "贝塔分布":
                self.show_only_beta_controls()
                self.plot_widget.set_distribution('beta')
            
            self.update_parameters()
        
        def update_parameters(self):
            dist_type = self.dist_combo.currentText()
            
            try:
                if dist_type == "均匀分布":
                    a = self.a_spin.value()
                    b = self.b_spin.value()
                    if a >= b:
                        raise ValueError("均匀分布参数错误：a必须小于b")
                    self.plot_widget.params = {'a': a, 'b': b}
                elif dist_type == "正态分布":
                    mu = self.mu_spin.value()
                    sigma = self.sigma_spin.value()
                    if sigma <= 0:
                        raise ValueError("正态分布参数错误：标准差σ必须大于0")
                    self.plot_widget.params = {'mu': mu, 'sigma': sigma}
                elif dist_type == "指数分布":
                    lam = self.lambda_exp_spin.value()
                    if lam <= 0:
                        raise ValueError("指数分布参数错误：率参数λ必须大于0")
                    self.plot_widget.params = {'lambda': lam}
                elif dist_type == "t分布":
                    df = self.df_spin.value()
                    if df <= 0:
                        raise ValueError("t分布参数错误：自由度ν必须大于0")
                    self.plot_widget.params = {'df': df}
                elif dist_type == "伽马分布":
                    alpha = self.alpha_gamma_spin.value()
                    beta = self.beta_gamma_spin.value()
                    if alpha <= 0 or beta <= 0:
                        raise ValueError("伽马分布参数错误：形状参数α和速率参数β都必须大于0")
                    self.plot_widget.params = {'alpha': alpha, 'beta': beta}
                elif dist_type == "贝塔分布":
                    alpha = self.alpha_beta_spin.value()
                    beta = self.beta_beta_spin.value()
                    if alpha <= 0 or beta <= 0:
                        raise ValueError("贝塔分布参数错误：形状参数α和β都必须大于0")
                    self.plot_widget.params = {'alpha': alpha, 'beta': beta}
                
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
            experimentInterface = ContinuousPDF.ExpInterface()
            scroll_area.setWidget(experimentInterface)
            scroll_area.setWidgetResizable(True)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            FluentStyleSheet.NAVIGATION_INTERFACE.apply(scroll_area)
            return scroll_area

        super().__init__(
            '连续型随机变量概率分布',
            descriptionFactory=create_description_interface,
            experimentFactory=create_experiment_interface,
            parent=parent
        )