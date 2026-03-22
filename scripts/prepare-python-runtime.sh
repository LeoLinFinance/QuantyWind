#!/bin/bash

# 量数风行 - Python 运行时准备脚本
# 用于准备打包所需的 Python 运行时环境

set -e

echo "========================================="
echo "准备 Python 运行时环境"
echo "========================================="

# 检测操作系统
OS="$(uname -s)"
case "${OS}" in
    Linux*)     PLATFORM=linux;;
    Darwin*)    PLATFORM=darwin;;
    CYGWIN*|MINGW*|MSYS*)    PLATFORM=win;;
    *)          PLATFORM="UNKNOWN:${OS}"
esac

echo "检测到平台: $PLATFORM"

# 创建 python-runtime 目录
mkdir -p python-runtime/$PLATFORM

if [ "$PLATFORM" = "darwin" ] || [ "$PLATFORM" = "linux" ]; then
    echo ""
    echo "创建 Python 虚拟环境..."
    python3 -m venv python-runtime/$PLATFORM
    
    echo ""
    echo "激活虚拟环境并安装依赖..."
    source python-runtime/$PLATFORM/bin/activate
    
    echo ""
    echo "升级 pip..."
    pip install --upgrade pip
    
    echo ""
    echo "安装后端依赖..."
    pip install -r backend/requirements.txt
    
    echo ""
    echo "验证安装..."
    pip list
    
    deactivate
    
    echo ""
    echo "✅ Python 运行时准备完成！"
    echo "位置: python-runtime/$PLATFORM"
    
elif [ "$PLATFORM" = "win" ]; then
    echo ""
    echo "Windows 平台检测到！"
    echo "请按照以下步骤手动准备 Python 运行时："
    echo ""
    echo "1. 下载嵌入式 Python:"
    echo "   访问: https://www.python.org/downloads/windows/"
    echo "   下载: Windows embeddable package (64-bit)"
    echo ""
    echo "2. 解压到: python-runtime/win/"
    echo ""
    echo "3. 配置 pip:"
    echo "   cd python-runtime/win"
    echo "   curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py"
    echo "   python.exe get-pip.py"
    echo ""
    echo "4. 安装依赖:"
    echo "   python.exe -m pip install -r ../../backend/requirements.txt"
    echo ""
    echo "5. 修改 python311._pth 文件，取消注释 'import site'"
    echo ""
else
    echo "❌ 不支持的平台: $PLATFORM"
    exit 1
fi

echo ""
echo "========================================="
echo "准备完成！"
echo "========================================="
