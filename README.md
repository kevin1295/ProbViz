# ProbViz

## Language

- [ProbViz](#probviz)
  - [Language](#language)
  - [English](#english)
  - [中文](#中文)

## English

This is a simple probability distribution visualization application.  
The application is written in Python and uses PyQt5 and matplotlib libraries. 
UI is based on the project [PyQt5-Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets).  

There are some problems when the window width is too small, and the image size is not adaptive. Switch to another tab and reload the image again can solve the problem.  
The WebEngine layer is a little strange, it will block some content, I haven't found a solution yet.

note: you should run the application with 64-bit Python, or the rendering will be disastrous.

## 中文

这是一个概率分布可视化程序。  
程序使用 Python 编写，主要使用 PyQt5 库和 matplotlib 库。  
UI 基于项目[PyQt5-Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets)

窗口宽度比较小时候，图像大小自适应会有点问题，切换一下 Tab，重新加载一下就好了。  
WebEngine 图层有点怪，会挡住部分内容，我还没有想到解决的办法。

注意：请使用64位Python运行程序，否则渲染会非常吃力甚至崩溃。
