#!/bin/bash

echo "🌐 局域网共享设置"
echo "===================="
echo ""

# 获取本机 IP
echo "📍 正在获取你的 IP 地址..."
IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null)

if [ -z "$IP" ]; then
    echo "❌ 无法获取 IP 地址"
    echo "请手动运行: ifconfig | grep 'inet '"
    exit 1
fi

echo "✅ 你的 IP 地址是: $IP"
echo ""

# 检查 vite.config.ts 配置
echo "📝 检查配置文件..."
if grep -q "host: '0.0.0.0'" vite.config.ts; then
    echo "✅ 配置已正确设置"
else
    echo "⚠️  需要修改配置文件"
    echo ""
    echo "请在 vite.config.ts 的 server 配置中添加："
    echo "  host: '0.0.0.0',"
    echo ""
    read -p "是否自动修改配置？(y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # 备份原文件
        cp vite.config.ts vite.config.ts.backup
        
        # 修改配置
        sed -i '' "s/server: {/server: {\n    host: '0.0.0.0',/" vite.config.ts
        
        echo "✅ 配置已修改（原文件备份为 vite.config.ts.backup）"
    fi
fi

echo ""
echo "===================="
echo "✅ 设置完成！"
echo ""
echo "🚀 启动应用："
echo "   npm run dev"
echo ""
echo "📱 别人访问地址："
echo "   http://$IP:3000"
echo ""
echo "💡 提示："
echo "   - 确保你和对方在同一 WiFi 下"
echo "   - 你的电脑必须保持开启"
echo "   - 防火墙可能需要允许 3000 端口"
echo ""
echo "===================="
