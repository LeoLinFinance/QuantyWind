#!/bin/bash

echo "🚀 一键启动远程访问"
echo "================================"
echo ""

# 检查 ngrok 配置
if ! ngrok config check &> /dev/null; then
    echo "❌ ngrok 配置有问题"
    exit 1
fi

echo "✅ ngrok 已配置"
echo ""

echo "🔧 正在启动前端..."
echo ""

# 启动前端（后台运行）
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!

echo "⏳ 等待前端启动（约 8 秒）..."
sleep 8

# 检查前端是否启动成功
if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "❌ 前端启动失败，查看日志："
    tail -20 /tmp/frontend.log
    kill $FRONTEND_PID 2>/dev/null
    exit 1
fi

echo "✅ 前端启动成功（http://localhost:3000）"
echo ""

echo "🌐 正在启动 ngrok 隧道..."
echo ""

# 启动 ngrok（后台运行）
ngrok http 3000 --log=stdout > /tmp/ngrok.log 2>&1 &
NGROK_PID=$!

echo "⏳ 等待 ngrok 连接（约 3 秒）..."
sleep 3

# 获取 ngrok URL
NGROK_URL=""
for i in {1..10}; do
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | grep -o 'https://[^"]*ngrok[^"]*' | head -1)
    if [ -n "$NGROK_URL" ]; then
        break
    fi
    sleep 1
done

echo ""
echo "================================"
echo "✅ 远程访问已启动！"
echo "================================"
echo ""

if [ -n "$NGROK_URL" ]; then
    echo "🌍 公网访问地址："
    echo ""
    echo "   $NGROK_URL"
    echo ""
    echo "📋 把这个地址发给别人，他们就能访问了！"
else
    echo "⚠️  无法自动获取 ngrok URL"
    echo ""
    echo "请访问 http://localhost:4040 查看 ngrok 控制台"
fi

echo ""
echo "================================"
echo ""
echo "💡 提示："
echo "   - 你的电脑必须保持开启"
echo "   - 按 Ctrl+C 停止所有服务"
echo "   - ngrok 控制台：http://localhost:4040"
echo ""
echo "📊 服务状态："
echo "   - 前端：http://localhost:3000"
echo "   - 公网：$NGROK_URL"
echo ""
echo "================================"
echo ""
echo "按 Ctrl+C 停止..."
echo ""

# 清理函数
cleanup() {
    echo ""
    echo "🛑 正在停止服务..."
    kill $FRONTEND_PID 2>/dev/null
    kill $NGROK_PID 2>/dev/null
    echo "✅ 所有服务已停止"
    exit 0
}

# 捕获 Ctrl+C
trap cleanup INT TERM

# 保持脚本运行
wait
