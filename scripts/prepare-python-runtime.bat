@echo off
REM 量数风行 - Python 运行时准备脚本 (Windows)
REM 用于准备打包所需的 Python 运行时环境

echo =========================================
echo 准备 Python 运行时环境 (Windows)
echo =========================================
echo.

REM 创建目录
if not exist "python-runtime\win" mkdir python-runtime\win

echo 请按照以下步骤准备 Python 运行时:
echo.
echo 1. 下载嵌入式 Python:
echo    访问: https://www.python.org/downloads/windows/
echo    下载: Windows embeddable package (64-bit)
echo    例如: python-3.11.8-embed-amd64.zip
echo.
echo 2. 解压到: python-runtime\win\
echo.
echo 3. 下载并安装 pip:
echo    cd python-runtime\win
echo    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
echo    python.exe get-pip.py
echo.
echo 4. 修改 python311._pth 文件:
echo    打开 python-runtime\win\python311._pth
echo    取消注释这一行: import site
echo    (删除行首的 # 号)
echo.
echo 5. 安装依赖:
echo    python.exe -m pip install -r ..\..\backend\requirements.txt
echo.
echo 6. 验证安装:
echo    python.exe -m pip list
echo.
echo =========================================
echo 准备完成后，运行: npm run electron:build:win
echo =========================================
echo.

pause
