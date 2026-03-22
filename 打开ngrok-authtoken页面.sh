#!/bin/bash

echo "🔑 打开 ngrok authtoken 页面"
echo "================================"
echo ""

# 打开 authtoken 页面
open https://dashboard.ngrok.com/get-started/your-authtoken

echo "✅ 已在浏览器中打开 ngrok authtoken 页面"
echo ""
echo "📝 接下来的步骤："
echo ""
echo "1. 如果还没登录，先登录 ngrok 账号"
echo "   （可以用 Google/GitHub 账号快速登录）"
echo ""
echo "2. 登录后会看到你的 authtoken"
echo "   （一串很长的字符）"
echo ""
echo "3. 点击复制按钮 📋 复制 token"
echo ""
echo "4. 回到终端，运行："
echo "   ngrok config add-authtoken 你复制的token"
echo ""
echo "================================"
echo ""
echo "💡 提示："
echo "   - authtoken 是私密的，不要分享给别人"
echo "   - 只需要配置一次，以后就不用了"
echo ""
