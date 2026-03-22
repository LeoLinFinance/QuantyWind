#!/bin/bash

echo "========================================"
echo "智者论坛启动脚本"
echo "========================================"
echo ""

# 检查是否在正确的目录
if [ ! -f "backend/main.py" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 初始化专家配置
echo "1. 初始化专家配置..."
python3 init_expert_configs.py
if [ $? -ne 0 ]; then
    echo "❌ 专家配置初始化失败"
    exit 1
fi
echo "✅ 专家配置初始化完成"
echo ""

# 验证修复
echo "2. 验证API修复..."
python3 verify_expert_forum_fix.py
if [ $? -ne 0 ]; then
    echo "⚠️  验证过程有警告，但继续启动"
fi
echo ""

# 启动后端
echo "3. 启动后端服务..."
echo "========================================"
echo "后端将在 http://0.0.0.0:8000 运行"
echo "按 Ctrl+C 停止服务"
echo "========================================"
echo ""

python3 backend/main.py
