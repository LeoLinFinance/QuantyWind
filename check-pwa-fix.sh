#!/bin/bash

echo "🔧 PWA 修复检查"
echo "===================="
echo ""

# Check type definitions
echo "✓ 检查类型定义..."
if [ -f "src/vite-env.d.ts" ]; then
    echo "  ✅ src/vite-env.d.ts 已创建"
    if grep -q "vite-plugin-pwa/client" src/vite-env.d.ts; then
        echo "  ✅ PWA 类型声明已添加"
    else
        echo "  ❌ PWA 类型声明缺失"
    fi
else
    echo "  ❌ src/vite-env.d.ts 不存在"
fi

echo ""

# Check icon files match config
echo "✓ 检查图标配置..."
svg_count=$(ls public/icon-*.svg 2>/dev/null | wc -l)
echo "  ✅ 找到 $svg_count 个 SVG 图标"

if grep -q "icon-192.svg" vite.config.ts; then
    echo "  ✅ vite.config.ts 使用 SVG 图标"
else
    echo "  ⚠️  vite.config.ts 可能使用 PNG 图标"
fi

if grep -q "icon-192.svg" public/manifest.json; then
    echo "  ✅ manifest.json 使用 SVG 图标"
else
    echo "  ⚠️  manifest.json 可能使用 PNG 图标"
fi

echo ""

# Check dependencies
echo "✓ 检查依赖..."
if grep -q "vite-plugin-pwa" package.json && grep -q "workbox-window" package.json; then
    echo "  ✅ PWA 依赖已安装"
else
    echo "  ❌ PWA 依赖未安装"
fi

echo ""
echo "===================="
echo "✅ 修复检查完成！"
echo ""
echo "现在可以运行："
echo "  npm run dev"
echo ""
