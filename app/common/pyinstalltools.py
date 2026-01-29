import os, sys

def get_app_path():
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    else:
        return os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        ))

def get_rely_path():
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    else:
        base_path = get_app_path()
        return os.path.join(base_path, '.venv64', 'Lib', 'site-packages')

def setup_qtWebEngine():
    
    webengine_process_path = os.path.join(
        get_rely_path(),
        'PyQt5',
        'Qt5',
        'bin',
        'QtWebEngineProcess.exe'
    )
    
    if not os.path.exists(webengine_process_path):
        raise FileNotFoundError(f"未找到QtWebEngineProcess.exe，路径：{webengine_process_path}")
    
    os.environ['QTWEBENGINEPROCESS_PATH'] = webengine_process_path
    
def get_katex_path():
    base_path = get_app_path()
    katex_root = os.path.join(base_path, "app", "common", "katex")
    katex_js_path = os.path.join(katex_root, "katex.min.js")
    
    if not os.path.exists(katex_js_path):
        raise FileNotFoundError(f"未找到KaTeX的js文件，路径：{katex_js_path}")
    
    return katex_root, katex_js_path