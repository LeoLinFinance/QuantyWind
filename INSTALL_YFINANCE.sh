#!/bin/bash

echo "=================================================="
echo "安装yfinance库"
echo "=================================================="

cd backend

echo ""
echo "📦 安装yfinance..."
pip3 install yfinance==0.2.32

echo ""
echo "✅ 验证安装..."
python3 -c "import yfinance as yf; print('yfinance版本:', yf.__version__)"

echo ""
echo "=================================================="
echo "安装完成！"
echo "=================================================="
echo ""
echo "下一步："
echo "1. 重启后端服务: python3 main.py"
echo "2. 打开浏览器测试历史数据更新"
echo ""
