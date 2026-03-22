#!/bin/bash

echo "🚀 量数风行 PWA 配置脚本"
echo "=========================="
echo ""

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 未找到 Node.js，请先安装 Node.js"
    exit 1
fi

echo "✅ Node.js 版本: $(node -v)"
echo ""

# 安装 PWA 依赖
echo "📦 安装 PWA 依赖..."
npm install -D vite-plugin-pwa workbox-window

if [ $? -eq 0 ]; then
    echo "✅ PWA 依赖安装成功"
else
    echo "❌ 依赖安装失败"
    exit 1
fi

echo ""
echo "🎨 准备应用图标..."

# 检查是否有图标
if [ ! -f "public/icon-192.png" ] || [ ! -f "public/icon-512.png" ]; then
    echo "⚠️  未找到应用图标"
    echo ""
    echo "请准备以下尺寸的图标并放到 public/ 目录："
    echo "  - icon-72.png (72x72)"
    echo "  - icon-96.png (96x96)"
    echo "  - icon-128.png (128x128)"
    echo "  - icon-144.png (144x144)"
    echo "  - icon-152.png (152x152)"
    echo "  - icon-192.png (192x192) ⭐ 必需"
    echo "  - icon-384.png (384x384)"
    echo "  - icon-512.png (512x512) ⭐ 必需"
    echo ""
    echo "💡 提示：可以使用在线工具生成："
    echo "   https://realfavicongenerator.net/"
    echo "   https://www.pwabuilder.com/imageGenerator"
    echo ""
    
    read -p "是否继续（使用临时图标）？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    
    # 创建临时图标（使用 ImageMagick 如果可用）
    if command -v convert &> /dev/null; then
        echo "📸 生成临时图标..."
        convert -size 192x192 xc:#1890ff -gravity center \
                -pointsize 48 -fill white -annotate +0+0 "量数\n风行" \
                public/icon-192.png
        convert -size 512x512 xc:#1890ff -gravity center \
                -pointsize 128 -fill white -annotate +0+0 "量数\n风行" \
                public/icon-512.png
        echo "✅ 临时图标已生成"
    else
        echo "⚠️  请手动添加图标文件"
    fi
else
    echo "✅ 找到应用图标"
fi

echo ""
echo "=========================="
echo "✅ PWA 配置完成！"
echo "=========================="
echo ""
echo "下一步："
echo "  1. 启动开发服务器："
echo "     npm run dev"
echo ""
echo "  2. 在浏览器中访问："
echo "     http://localhost:3000"
echo ""
echo "  3. 测试 PWA 功能："
echo "     - 按 F12 打开开发者工具"
echo "     - 切换到 Application 标签"
echo "     - 检查 Manifest 和 Service Workers"
echo ""
echo "  4. 测试安装："
echo "     - 地址栏右侧会出现安装图标"
echo "     - 点击安装到桌面"
echo ""
echo "📖 详细说明请查看："
echo "   - PWA_SETUP_COMPLETE.md"
echo "   - INSTALL_PWA_INSTRUCTIONS.md"
echo ""
