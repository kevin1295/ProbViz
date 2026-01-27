from app.common.MarkdownKatex import MarkdownKaTeXWidget
from PyQt5.QtGui import QColor

# 测试示例：创建窗口并设置背景色，演示透明效果
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow
    from PyQt5.QtGui import QPalette, QBrush, QPixmap  # 新增：用于设置窗口背景（演示透明）

    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("PyQt5 离线Markdown+KaTeX渲染（透明背景）")
    window.resize(800, 600)

    # 演示：给窗口设置一个彩色/图片背景，方便查看透明效果
    palette = QPalette()
    # 选项1：设置纯色背景（浅蓝）
    palette.setBrush(QPalette.Window, QBrush(QColor(173, 216, 230)))
    # 选项2：设置图片背景（取消注释即可使用，需替换为你的图片路径）
    # palette.setBrush(QPalette.Window, QBrush(QPixmap("background.jpg").scaled(window.size())))
    window.setPalette(palette)

    # 初始化控件（可切换theme=0/1，查看透明效果）
    md_katex_widget = MarkdownKaTeXWidget(theme=1)
    window.setCentralWidget(md_katex_widget)

    # 测试带KaTeX公式的Markdown文本
    test_markdown = """
# 离线Markdown+KaTeX渲染测试（透明背景）
## 1. 行内公式示例
这是一个行内数学公式：$E=mc^2$，这是另一个：$\sum_{i=1}^n i = \\frac{n(n+1)}{2}$

## 2. 块级公式示例
$$
f(x) = x^2 + 2x + 1
$$

## 3. 普通Markdown语法支持
- 列表项1
- 列表项2
**加粗文本** | *斜体文本*

```python
# 代码块示例（半透明背景）
print("Hello, KaTeX + Markdown + Transparent Background!")
```
"""
md_katex_widget.set_markdown(test_markdown)
window.show()
sys.exit(app.exec_())