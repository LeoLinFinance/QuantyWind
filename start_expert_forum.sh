#!/bin/bash

# 智者论坛启动脚本

echo "=========================================="
echo "  智者论坛 - 启动脚本"
echo "=========================================="
echo ""

# 检查数据是否初始化
if [ ! -f "data/portfolio.json" ]; then
    echo "📦 初始化测试数据..."
    python3 init_expert_forum.py
    echo ""
fi

echo "🚀 启动服务..."
echo ""
echo "请在两个终端中分别运行："
echo ""
echo "终端1 (后端):"
echo "  cd backend && python3 main.py"
echo ""
echo "终端2 (前端):"
echo "  npm run dev"
echo ""
echo "然后访问: http://localhost:5173/expert-forum"
echo ""
echo "=========================================="
echo "  提示: 使用 Ctrl+C 停止服务"
echo "=========================================="
