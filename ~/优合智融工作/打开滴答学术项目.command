#!/bin/bash

# 打开滴答学术项目

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎓 滴答学术 (Dida Scholar) 项目"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📁 项目位置："
echo "   ~/优合智融工作/滴答学术-Dida-Scholar/"
echo ""
echo "🌐 在线地址："
echo "   https://leolinfin.github.io/Dida-Scholar/"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "请选择操作："
echo "1) 在Finder中打开项目文件夹"
echo "2) 在浏览器中打开网站"
echo "3) 在终端中打开项目"
echo "4) 查看项目文档"
echo "5) 退出"
echo ""
read -p "请输入选项 (1-5): " choice

case $choice in
    1)
        echo "正在打开项目文件夹..."
        open ~/优合智融工作/滴答学术-Dida-Scholar/
        ;;
    2)
        echo "正在打开网站..."
        open https://leolinfin.github.io/Dida-Scholar/
        ;;
    3)
        echo "正在打开终端..."
        cd ~/优合智融工作/滴答学术-Dida-Scholar/
        exec $SHELL
        ;;
    4)
        echo "正在打开项目文档..."
        open ~/优合智融工作/滴答学术-Dida-Scholar/项目归档说明.md
        ;;
    5)
        echo "再见！"
        exit 0
        ;;
    *)
        echo "无效的选项"
        ;;
esac
