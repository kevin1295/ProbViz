import os, sys

def get_work_dir():
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    else:
        return os.path.abspath(".")

def get_katex_path():
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    
    katex_root = os.path.join(base_path, "app", "common", "katex")
    katex_js_path = os.path.join(katex_root, "katex.min.js")
    
    if not os.path.exists(katex_js_path):
        raise FileNotFoundError(f"未找到KaTeX的js文件，路径：{katex_js_path}")
    
    return katex_root, katex_js_path