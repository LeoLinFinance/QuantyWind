#!/bin/bash

echo "🚀 滴答学术 - 静态网站部署脚本"
echo "================================"
echo ""

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 未安装Node.js，请先安装"
    exit 1
fi

echo "✅ Node.js已安装"

# 1. 导出数据
echo ""
echo "📦 步骤1: 导出静态数据..."
cd backend
node export-static.js
if [ $? -ne 0 ]; then
    echo "❌ 数据导出失败"
    exit 1
fi
cd ..

# 2. 创建部署目录
echo ""
echo "📁 步骤2: 创建部署目录..."
rm -rf deploy-static
mkdir -p deploy-static
cp demo-web/index-static.html deploy-static/index.html
cp demo-web/data.json deploy-static/data.json

echo "✅ 文件已复制到 deploy-static/ 目录"

# 3. 显示文件信息
echo ""
echo "📊 部署文件信息:"
ls -lh deploy-static/

# 4. 测试本地预览
echo ""
echo "🌐 步骤3: 启动本地预览..."
echo "访问: http://localhost:8888"
echo "按 Ctrl+C 停止服务器"
echo ""

cd deploy-static
python3 -m http.server 8888
