# ProbViz

## Language

- [ProbViz](#probviz)
  - [Language](#language)
  - [English](#english)
    - [About this Project](#about-this-project)
    - [Open Source License Statement](#open-source-license-statement)
    - [Third-party dependencies:](#third-party-dependencies)
    - [Compliance Statement:](#compliance-statement)
  - [中文](#中文)
    - [关于本项目](#关于本项目)
    - [开源协议整体声明](#开源协议整体声明)
    - [第三方依赖组件声明：](#第三方依赖组件声明)
    - [合规声明](#合规声明)

## English

### About this Project

This is a simple probability distribution visualization application.  
The application is written in Python and uses PyQt5 and matplotlib libraries. 
UI is based on the project [PyQt5-Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets).  

There are some problems when the window width is too small, and the image size is not adaptive. Switch to another tab and reload the image again can solve the problem.  
The WebEngine layer is a little strange, it will block some content, I haven't found a solution yet.

note:
- I write this program with Python 3.9.13, which is intended to make the packaged program smaller, theoretically updated versions can also run.
- you should run the application with 64-bit Python, or the rendering will be disastrous.

### Open Source License Statement

This project as a whole is open source under the **GNU General Public License v3.0 (GPLv3)**. The complete license text can be found in the `LICENSE` file in the root directory of the repository.

### Third-party dependencies:

- Dependency 1(GPLv3)  
  Name: qfluentwidgets  
  Version: 1.11.0  
  Official Source: https://github.com/zhiyiYo/PyQt-Fluent-Widgets  
  Open Source License: GNU General Public License v3.0 (GPLv3)  
- Dependency 2(MIT)  
  Name: KaTeX  
  Version: 0.16.28  
  Official Source: https://github.com/KaTeX/KaTeX  
  Open Source License: MIT License  
  Raw License Notice: KaTeX follows the permissive MIT license, and this project only integrates its release artifacts without modifying its core functionality.

### Compliance Statement:

- This project has fulfilled all obligations under the GPLv3 license, and derivative works must be released under the GPLv3 license.
- KaTeX follows the permissive MIT license, and this project only integrates its release artifacts without modifying its core functionality. The original MIT license text of KaTeX is stored in the `licenses/KaTeX-LICENSE-MIT` file in the root directory of this project.
- All open-source content in this project comes without any express or implied warranties, and the author assumes no legal liability arising from the use of this project.
- Copyright holders: Wanlin Shi, North China Electric Power University, Kevin1295

## 中文

### 关于本项目

这是一个概率分布可视化程序。  
程序使用 Python 编写，主要使用 PyQt5 库和 matplotlib 库。  
UI 基于项目[PyQt5-Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets)

窗口宽度比较小时候，图像大小自适应会有点问题，切换一下 Tab，重新加载一下就好了。  
WebEngine 图层有点怪，会挡住部分内容，我还没有想到解决的办法。

注意：

- 编写时使用的是 Python 3.9.13，目的是使打包后程序更小，理论上更新的版本也能运行。
- 请使用64位Python运行程序，否则渲染会非常吃力甚至崩溃。

### 开源协议整体声明

本项目整体遵循 **GNU General Public License v3.0 (GPLv3)** 协议开源，完整许可证文本见仓库根目录的 `LICENSE` 文件。

### 第三方依赖组件声明：

- 依赖1（GPLv3 协议）：  
  名称：qfluentwidgets  
  版本：1.11.0  
  官方来源：https://github.com/zhiyiYo/PyQt-Fluent-Widgets  
  开源协议：GNU General Public License v3.0 (GPLv3)  
- 依赖2（MIT 协议）：  
  名称：KaTeX  
  版本：0.16.28  
  官方来源：https://github.com/KaTeX/KaTeX  
  开源协议：MIT License  
  原始协议说明：KaTeX 自身遵循宽松 MIT 协议，本项目仅对其 Release 打包产物进行集成使用，未修改其核心功能。

### 合规声明

-  本项目已遵循 GPLv3 协议的所有义务，衍生作品必须以 GPLv3 协议开源。
-  KaTeX 自身遵循宽松 MIT 协议，本项目仅对其 Release 打包产物进行集成使用，未修改其核心功能。KaTeX 的原始 MIT 许可证文本已存放于本项目根目录 `licenses/KaTeX-LICENSE-MIT` 文件中。
-  本项目所有开源内容不提供任何明示或暗示的担保，作者不承担任何因使用本项目产生的法律责任。
-  版权所有：石万林，华北电力大学, Kevin1295
