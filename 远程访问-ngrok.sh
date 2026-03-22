#!/bin/bash

echo "🌐 远程访问启动脚本（ngrok）"
echo "================================"
echo ""

# 检查 ngrok 是否安装
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok 未安装"
    echo ""
    echo "请先安装 ngrok："
    echo "  brew install ngrok"
    echo ""
    echo "或访问：https://ngrok.com/download"
    exit 1
fi

echo "✅ ngrok 已安装"
echo ""

# 检查是否配置了 authtoken
if ! ngrok config check &> /dev/null; then
    echo "⚠️  ngrok 未配置"
    echo ""
    echo "请先配置 authtoken："
    echo "1. 访问 https://dashboard.ngrok.com/signup 注册"
    echo "2. 获取 authtoken"
    echo "3. 运行: ngrok config add-authtoken 你的token"
    echo ""
    exit 1
fi

echo "✅ ngrok 已配置"
echo ""

# 询问是否需要启动后端
read -p "是否需要同时暴露后端 API？(y/n) " -n 1 -r
echo ""
EXPOSE_BACKEND=$REPLY

echo ""
echo "🚀 正在启动服务..."
echo ""

# 启动前端
echo "📦 启动前端（端口 3000）..."
npm run dev > /dev/null 2>&1 &
FRONTEND_PID=$!

# 等待前端启动
echo "⏳ 等待前端启动..."
sleep 8

# 检查前端是否启动成功
if ! curl -s http://localhost:3000 > /dev/null; then
    echo "❌ 前端启动失败"
    kill $FRONTEND_PID 2>/dev/null
    exit 1
fi

echo "✅ 前端启动成功"
echo ""

# 如果需要启动后端
if [[ $EXPOSE_BACKEND =~ ^[Yy]$ ]]; then
    echo "📦 启动后端（端口 8000）..."
    cd backend
    python3 -m uvicorn main:app --reload --port 8000 > /dev/null 2>&1 &
    BACKEND_PID=$!
    cd ..
    
    echo "⏳ 等待后端启动..."
    sleep 5
    
    if ! curl -s http://localhost:8000/docs > /dev/null; then
        echo "⚠️  后端可能未启动成功，但继续..."
    else
        echo "✅ 后端启动成功"
    fi
    echo ""
fi

# 创建临时文件存储 ngrok 输出
NGROK_LOG=$(mktemp)

# 启动 ngrok
echo "🌐 启动 ngrok 隧道..."
ngrok http 3000 --log=stdout > "$NGROK_LOG" &
NGROK_PID=$!

# 等待 ngrok 启动并获取 URL
echo "⏳ 等待 ngrok 连接..."
sleep 3

# 从日志中提取 URL
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o 'https://[^"]*ngrok[^"]*' | head -1)

echo ""
echo "================================"
echo "✅ 远程访问已启动！"
echo "================================"
echo ""

if [ -n "$NGROK_URL" ]; then
    echo "🌍 公网访问地址："
    echo "   $NGROK_URL"
    echo ""
    echo "📋 复制这个地址发给别人，他们就能访问了！"
else
    echo "⚠️  无法自动获取 ngrok URL"
    echo "请查看 ngrok 终端输出获取访问地址"
fi

echo ""
echo "💡 提示："
echo "   - 你的电脑必须保持开启"
echo "   - 关闭此脚本后服务会停止"
echo "   - 按 Ctrl+C 停止所有服务"
echo ""

if [[ $EXPOSE_BACKEND =~ ^[Yy]$ ]]; then
    echo "🔧 后端 API 地址："
    echo "   需要单独暴露后端，或修改前端配置"
    echo "   运行: ngrok http 8000"
    echo ""
fi

echo "================================"
echo ""
echo "📊 ngrok 控制台："
echo "   http://localhost:4040"
echo ""
echo "按 Ctrl+C 停止所有服务..."
echo ""

# 清理函数
cleanup() {
    echo ""
    echo "🛑 正在停止服务..."
    kill $FRONTEND_PID 2>/dev/null
    [ -n "$BACKEND_PID" ] && kill $BACKEND_PID 2>/dev/null
    kill $NGROK_PID 2>/dev/null
    rm -f "$NGROK_LOG"
    echo "✅ 所有服务已停止"
    exit 0
}

# 捕获 Ctrl+C
trap cleanup INT TERM

# 保持脚本运行
wait
