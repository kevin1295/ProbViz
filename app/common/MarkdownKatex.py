from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import QUrl, QFileInfo
from PyQt5.QtGui import QColor
import markdown
import os
# 新增：导入PyQt-Fluent-Widgets的主题工具
from qfluentwidgets import isDarkTheme, qconfig

class MarkdownKaTeXWidget(QWidget):
    """继承QWidget的离线Markdown+KaTeX渲染控件（支持透明背景+跟随全局主题+字体大小调整）"""
    def __init__(self, parent=None):
        super().__init__(parent)
        # 字体大小相关配置
        self._default_font_size = 18  # 默认字体大小
        self._current_font_size = self._default_font_size  # 当前字体大小
        self._font_size_step = 2  # 放大/缩小的步长
        self._font_size_min = 12  # 最小字体大小限制
        self._font_size_max = 36  # 最大字体大小限制
        
        # 初始化核心控件和布局
        self._init_ui()
        # 监听全局主题变化信号，触发重新渲染
        qconfig.themeChanged.connect(self._on_theme_changed)
        self._last_markdown_text = "Markdown文本未初始化"

    def _init_ui(self):
        """初始化界面布局和内部控件（保留透明背景核心逻辑）"""
        # 1. 创建QWebEngineView（承载HTML+KaTeX+Markdown）
        self.web_view = QWebEngineView(self)
        self.web_view.setContextMenuPolicy(3)  # 禁用右键菜单
        
        self.web_page = QWebEnginePage(self)
        self.web_page.setBackgroundColor(QColor(0, 0, 0, 0))  # 完全透明
        self.web_view.setPage(self.web_page)
        self.web_view.setAutoFillBackground(False)
        
        self.web_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 2. 布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.web_view)
        self.setLayout(main_layout)
        
        # 3. 初始化提示文本
        self.set_markdown("请输入Markdown文本")

    def _on_theme_changed(self):
        """主题变化时触发：重新渲染当前Markdown文本，应用新主题样式"""
        self.set_markdown(getattr(self, '_last_markdown_text', "请输入Markdown文本"))

    def _re_render_with_new_theme(self, html=None):
        """回调函数：根据最新主题重新渲染Markdown（兼容原有逻辑，已复用set_markdown）"""
        self.set_markdown(getattr(self, '_last_markdown_text', "请输入Markdown文本"))

    def set_markdown(self, markdown_text: str):
        """
        公共接口：设置要渲染的Markdown文本（保存最后一次文本，用于主题切换/字体调整后重渲染）
        :param markdown_text: 原始Markdown字符串（可包含KaTeX公式）
        """
        # 保留：保存最后一次传入的Markdown文本
        self._last_markdown_text = markdown_text
        
        # 步骤1：Markdown转HTML
        markdown_html = markdown.markdown(
            markdown_text,
            extensions=['extra']
        )
        
        # 步骤2：构建带主题样式+动态字体大小的离线HTML
        offline_html = self._build_offline_html(markdown_html)
        
        # 步骤3：加载HTML
        current_dir = QFileInfo(__file__).absolutePath()
        
        self.web_view.page().profile().clearHttpCache()
        
        self.web_view.setHtml(offline_html, QUrl.fromLocalFile(current_dir + "/"))

    def _build_offline_html(self, markdown_html: str) -> str:
        """
        私有方法：构建完整的离线HTML内容（新增：动态字体大小）
        :param markdown_html: 解析后的Markdown HTML字符串
        :return: 完整的HTML字符串
        """
        # 1. KaTeX资源路径处理
        katex_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "katex")
        katex_css_path = QUrl.fromLocalFile(os.path.join(katex_dir, "katex.min.css")).toString()
        katex_js_path = QUrl.fromLocalFile(os.path.join(katex_dir, "katex.min.js")).toString()
        katex_render_js_path = QUrl.fromLocalFile(os.path.join(katex_dir, "contrib", "auto-render.min.js")).toString()
        
        # 2. 从全局主题动态判断颜色
        if isDarkTheme():
            # 深色主题：白色字体 + 深灰蓝半透明代码块
            font_color = "#ffffff"
            pre_bg_color = "rgba(52, 73, 94, 0.8)"
            code_bg_color = "rgba(52, 73, 94, 0.8)"
        else:
            # 浅色主题：黑色字体 + 浅灰半透明代码块
            font_color = "#000000"
            pre_bg_color = "rgba(245, 245, 245, 0.8)"
            code_bg_color = "rgba(245, 245, 245, 0.8)"
        
        # 3. HTML模板
        html_template = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Offline Markdown + KaTeX</title>
            <link rel="stylesheet" href="{katex_css_path}">
            <script src="{katex_js_path}"></script>
            <script src="{katex_render_js_path}"></script>
            <style>
                p {{
                    text-indent: 2em;
                    margin: 0.8em 0;
                }}
                body {{
                    font-family: "Microsoft YaHei", Arial, sans-serif;
                    font-size: {self._current_font_size}px;  /* 动态当前字体大小 */
                    padding: 24px;
                    margin: 0;
                    color: {font_color};
                    background-color: transparent;  /* 保留透明背景 */
                }}
                pre {{
                    background-color: {pre_bg_color};
                    padding: 18px;
                    border-radius: 4px;
                    overflow-x: auto;
                    font-size: {self._current_font_size - 2}px;  /* 代码块字体略小于正文，更美观 */
                }}
                code {{
                    background-color: {code_bg_color};
                    padding: 2px 4px;
                    border-radius: 2px;
                    font-size: {self._current_font_size - 2}px;  /* 行内代码字体略小于正文 */
                }}
                .katex {{ 
                    font-size: {self._current_font_size * 1.1}px !important;  /* 公式略大于正文，保持可读性，跟随当前字体大小 */
                    color: {font_color} !important;  /* 公式跟随主题颜色 */
                }}
            </style>
        </head>
        <body>
            {markdown_html}
            <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    try {{
                        renderMathInElement(
                            document.body,
                            {{
                                delimiters: [
                                    {{left: '$$', right: '$$', display: true}},
                                    {{left: '$', right: '$', display: false}}
                                ],
                                throwOnError: false
                            }}
                        );
                    }} catch (e) {{
                        console.error("KaTeX渲染失败：", e);
                    }}
                }});
            </script>
        </body>
        </html>
        """
        return html_template
    
    # ---------------------- 新增：字体大小调整公共接口 ----------------------
    def set_font_size(self, font_size: int):
        """
        公共接口：直接设置具体的字体大小（会自动限制在最小/最大值之间）
        :param font_size: 目标字体大小（像素）
        """
        # 限制字体大小在合理区间内，防止显示异常
        self._current_font_size = max(self._font_size_min, min(font_size, self._font_size_max))
        # 重新渲染Markdown，应用新字体大小
        self.set_markdown(self._last_markdown_text)
    
    def increase_font_size(self):
        """公共接口：放大字体（按预设步长递增）"""
        self.set_font_size(self._current_font_size + self._font_size_step)
    
    def decrease_font_size(self):
        """公共接口：缩小字体（按预设步长递减）"""
        self.set_font_size(self._current_font_size - self._font_size_step)
    
    def reset_font_size(self):
        """公共接口：重置字体大小为默认值"""
        self._current_font_size = self._default_font_size
        self.set_markdown(self._last_markdown_text)
    
    # ---------------------- 新增：获取当前字体大小的辅助接口 ----------------------
    def get_current_font_size(self) -> int:
        """公共接口：获取当前字体大小"""
        return self._current_font_size
    
    def get_default_font_size(self) -> int:
        """公共接口：获取默认字体大小"""
        return self._default_font_size
    
    def resizeEvent(self, event):
        return super().resizeEvent(event)