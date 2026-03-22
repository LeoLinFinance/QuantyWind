#!/bin/bash

echo "🔍 PWA 设置检查"
echo "===================="
echo ""

# Check dependencies
echo "✓ 检查依赖..."
if grep -q "vite-plugin-pwa" package.json; then
    echo "  ✅ vite-plugin-pwa 已安装"
else
    echo "  ❌ vite-plugin-pwa 未安装"
fi

if grep -q "workbox-window" package.json; then
    echo "  ✅ workbox-window 已安装"
else
    echo "  ❌ workbox-window 未安装"
fi

echo ""

# Check files
echo "✓ 检查文件..."
files=(
    "vite.config.ts"
    "src/registerSW.ts"
    "src/main.tsx"
    "src/components/InstallPWA.tsx"
    "public/manifest.json"
    "public/robots.txt"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file 缺失"
    fi
done

echo ""

# Check icons
echo "✓ 检查图标..."
icon_count=$(ls public/icon-*.svg 2>/dev/null | wc -l)
if [ "$icon_count" -ge 8 ]; then
    echo "  ✅ 找到 $icon_count 个图标文件"
else
    echo "  ⚠️  只找到 $icon_count 个图标文件（需要 8 个）"
fi

echo ""
echo "===================="
echo "✅ PWA 设置检查完成！"
echo ""
echo "下一步："
echo "1. 运行 'npm run dev' 启动开发服务器"
echo "2. 在 Chrome 中打开 http://localhost:3000"
echo "3. 按 F12 打开开发者工具"
echo "4. 切换到 Application 标签查看 PWA 配置"
echo ""
