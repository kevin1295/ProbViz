import sys
from PyQt5.QtWidgets import QApplication, QTextBrowser, QVBoxLayout, QWidget, QPushButton, QTextEdit
from PyQt5.QtCore import Qt

class MathMLViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 创建文本浏览器显示 MathML
        self.browser = QTextBrowser()
        
        # 示例 MathML 公式
        mathml_content = '''
        <math xmlns="http://www.w3.org/1998/Math/MathML">
          <mrow>
            <mi>x</mi>
            <mo>=</mo>
            <mfrac>
              <mrow>
                <mo>-</mo>
                <mi>b</mi>
                <mo>&#xB1;<!-- ± --></mo>
                <msqrt>
                  <mrow>
                    <msup>
                      <mi>b</mi>
                      <mn>2</mn>
                    </msup>
                    <mo>-</mo>
                    <mn>4</mn>
                    <mi>a</mi>
                    <mi>c</mi>
                  </mrow>
                </msqrt>
              </mrow>
              <mrow>
                <mn>2</mn>
                <mi>a</mi>
              </mrow>
            </mfrac>
          </mrow>
        </math>
        '''
        
        # 设置 HTML 内容
        self.browser.setHtml(f"""
        <h3>MathML 测试</h3>
        <p>二次方程求根公式：</p>
        {mathml_content}
        
        <p>更多示例：</p>
        <p>简单分数：<math><mfrac><mn>1</mn><mn>2</mn></mfrac></math></p>
        
        <p>积分：<math>
          <mrow>
            <mo>∫</mo>
            <msup>
              <mi>x</mi>
              <mn>2</mn>
            </msup>
            <mi>d</mi>
            <mi>x</mi>
          </mrow>
        </math></p>
        """)
        
        # 添加一个按钮来测试交互
        test_btn = QPushButton("测试更多 MathML")
        test_btn.clicked.connect(self.test_more_mathml)
        
        layout.addWidget(self.browser)
        layout.addWidget(test_btn)
        
        self.setLayout(layout)
        self.setWindowTitle("PyQt MathML 测试")
        self.setGeometry(100, 100, 600, 400)
        
    def test_more_mathml(self):
        """测试更多 MathML 表达式"""
        more_mathml = """
        <p>求和：<math>
          <mrow>
            <munderover>
              <mo>∑</mo>
              <mrow>
                <mi>i</mi>
                <mo>=</mo>
                <mn>1</mn>
              </mrow>
              <mi>n</mi>
            </munderover>
            <mi>i</mi>
          </mrow>
        </math></p>
        
        <p>矩阵：<math>
          <mrow>
            <mo>[</mo>
            <mtable>
              <mtr>
                <mtd><mn>1</mn></mtd>
                <mtd><mn>2</mn></mtd>
              </mtr>
              <mtr>
                <mtd><mn>3</mn></mtd>
                <mtd><mn>4</mn></mtd>
              </mtr>
            </mtable>
            <mo>]</mo>
          </mrow>
        </math></p>
        """
        
        current_html = self.browser.toHtml()
        self.browser.setHtml(current_html + more_mathml)

def main():
    # 创建应用实例
    app = QApplication(sys.argv)
    
    # 创建并显示窗口
    viewer = MathMLViewer()
    viewer.show()
    
    # 启动事件循环
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()