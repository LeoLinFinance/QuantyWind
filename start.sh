#!/bin/bash

echo "🚀 启动滴答学术系统"

# 检查MongoDB
if ! pgrep -x "mongod" > /dev/null; then
    echo "⚠️  MongoDB未运行，请先启动MongoDB"
    exit 1
fi

# 检查环境变量
if [ ! -f "backend/.env" ]; then
    echo "⚠️  未找到.env文件，请先配置环境变量"
    echo "   cp backend/.env.example backend/.env"
    exit 1
fi

# 安装依赖
if [ ! -d "backend/node_modules" ]; then
    echo "📦 安装后端依赖..."
    cd backend && npm install && cd ..
fi

# 启动后端服务
echo "🔧 启动后端服务..."
cd backend
npm start &
BACKEND_PID=$!
cd ..

# 启动采集器
echo "🕷️  启动采集器..."
cd backend
npm run crawler &
CRAWLER_PID=$!
cd ..

echo ""
echo "✅ 系统启动成功！"
echo ""
echo "📍 后端服务: http://localhost:3000"
echo "📍 健康检查: http://localhost:3000/health"
echo ""
echo "按 Ctrl+C 停止服务"

# 等待中断信号
trap "echo ''; echo '🛑 停止服务...'; kill $BACKEND_PID $CRAWLER_PID; exit" INT

wait
