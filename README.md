# 2b2t.xin-queue-tool

## 阐述
就是一个在2b2t.xin排队自动答题的py脚本

适用于 Windows 平台.
请使用 [Python](https://www.python.org/downloads/) 3.14 及以上的 Python 运行此脚本.

直接使用上述脚本前请在终端输入```pip install pywin32```以安装脚本依赖

**直接使用 [Releases](https://github.com/EJIAOFEN/2b2t.xin-queue-tool/releases) 中的无需安装**<sup>(指v0.2+)</sup>

脚本具体使用方法见[Releases](https://github.com/EJIAOFEN/2b2t.xin-queue-tool/releases)


## 如何打包

1.在你的 **Windows 终端** (**cmd**, **Powershell**, **Windows Terminal** 等) 中使用```cd [drive:][path]```切换到存放脚本的路径

2.在终端中键入```pip install pyinstaller```以安装 **Pyinstaller**

3.在终端中键入```pip install pywin32```以安装 **Pywin32 组件**

4.在终端中键入```pyinstaller --onefile --hidden-import=win32gui --hidden-import=win32con --hidden-import=win32api [脚本名称].py```

5.在脚本同一路径下的dist中会存放打包后的*.exe文件
