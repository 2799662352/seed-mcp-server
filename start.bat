@echo off
chcp 65001 >nul
rem 通过 cmd 调起，规避部分企业 DLP/加密软件对直接调 python.exe 的拦截
rem 如需指定 python 解释器路径，把下一行的 `python` 换成绝对路径，例如:
rem `C:\Users\you\AppData\Local\Programs\Python\Python312\python.exe`
python "%~dp0server.py"
