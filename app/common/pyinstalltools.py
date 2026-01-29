import os, sys

def get_katex_path():
    """
    动态获取KaTeX的根目录路径（兼容开发环境和打包后环境）
    """
    # 1. 判断是否是PyInstaller打包后的运行环境
    if hasattr(sys, '_MEIPASS'):
        # 打包后：sys._MEIPASS 是临时解压目录的根路径
        base_path = sys._MEIPASS
    else:
        # 开发环境：当前脚本所在目录（即项目根目录）
        base_path = os.path.abspath(".")
    
    # 2. 拼接KaTeX的根目录路径（对应项目中的static/katex）
    katex_root = os.path.join(base_path, "app", "common", "katex")
    # 3. 拼接katex.min.js的完整路径（如果需要直接调用js文件，可返回这个路径）
    katex_js_path = os.path.join(katex_root, "katex.min.js")
    
    # 验证路径是否存在（可选，方便调试）
    if not os.path.exists(katex_js_path):
        raise FileNotFoundError(f"未找到KaTeX的js文件，路径：{katex_js_path}")
    
    return katex_root, katex_js_path