#!/bin/bash

# 量数风行 - 快速设置脚本
# 此脚本将帮助您快速设置开发环境

set -e

echo "=================================="
echo "量数风行 QuantyWind - 快速设置"
echo "=================================="
echo ""

# 检查 Python
echo "检查 Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python 3，请先安装 Python 3.9+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python 版本: $PYTHON_VERSION"

# 检查 Node.js
echo "检查 Node.js..."
if ! command -v node &> /dev/null; then
    echo "❌ 未找到 Node.js，请先安装 Node.js 16+"
    exit 1
fi

NODE_VERSION=$(node --version)
echo "✅ Node.js 版本: $NODE_VERSION"

# 创建 .env 文件
echo ""
echo "配置环境变量..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ 已创建 .env 文件"
    echo "💡 提示: 您可以稍后在应用设置页面配置 API Key"
else
    echo "⏭️  .env 文件已存在，跳过"
fi

# 安装后端依赖
echo ""
echo "安装后端依赖..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ 已创建虚拟环境"
fi

source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null || true
pip install -r requirements.txt
echo "✅ 后端依赖安装完成"

# 初始化数据库
echo ""
echo "初始化数据库..."
if [ ! -d "alembic/versions" ]; then
    mkdir -p alembic/versions
fi

alembic upgrade head
echo "✅ 数据库初始化完成"

cd ..

# 安装前端依赖
echo ""
echo "安装前端依赖..."
npm install
echo "✅ 前端依赖安装完成"

# 完成
echo ""
echo "=================================="
echo "✅ 设置完成！"
echo "=================================="
echo ""
echo "下一步："
echo ""
echo "1. 启动后端服务（终端 1）："
echo "   cd backend"
echo "   source venv/bin/activate  # Windows: venv\\Scripts\\activate"
echo "   python main.py"
echo ""
echo "2. 启动前端服务（终端 2）："
echo "   npm run dev"
echo ""
echo "3. 访问应用："
echo "   http://localhost:3000"
echo ""
echo "4. 配置 API Key："
echo "   访问 http://localhost:3000/settings"
echo "   添加您的 AI 服务 API Key"
echo ""
echo "📖 更多信息请查看 README.md 和 QUICKSTART.md"
echo ""
