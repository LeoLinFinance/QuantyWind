#!/bin/bash

echo "🚀 启动量数风行应用"
echo "===================="
echo ""

# 检查是否在正确的目录
if [ ! -f "package.json" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

echo "📦 检查依赖..."
if [ ! -d "node_modules" ]; then
    echo "⚠️  未找到 node_modules，正在安装依赖..."
    npm install
fi

echo ""
echo "✅ 准备就绪！"
echo ""
echo "🌐 前端服务器将在 http://localhost:3000 启动"
echo ""
echo "📝 提示："
echo "   - 在浏览器中访问 http://localhost:3000"
echo "   - 点击地址栏的安装图标可以安装到桌面"
echo "   - 按 Ctrl+C 停止服务器"
echo ""
echo "===================="
echo ""

# 启动开发服务器
npm run dev
