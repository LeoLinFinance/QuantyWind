#!/bin/bash

# 量数风行 - GitHub 发布脚本
# 此脚本将帮助您快速发布项目到 GitHub

set -e

echo "=================================="
echo "量数风行 - GitHub 发布助手"
echo "=================================="
echo ""

# 检查是否是 Git 仓库
if [ ! -d .git ]; then
    echo "⚠️  当前目录不是 Git 仓库"
    read -p "是否初始化 Git 仓库？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git init
        echo "✅ Git 仓库已初始化"
    else
        echo "❌ 取消发布"
        exit 1
    fi
fi

# 检查 .env 文件
if [ -f .env ]; then
    echo "⚠️  检测到 .env 文件"
    if git check-ignore .env > /dev/null 2>&1; then
        echo "✅ .env 文件已被 .gitignore 忽略"
    else
        echo "❌ 警告：.env 文件可能会被提交！"
        echo "   请确保 .gitignore 中包含 .env"
        read -p "是否继续？(y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo ""
    echo "📝 检测到未提交的更改："
    git status --short
    echo ""
    read -p "是否提交这些更改？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add .
        read -p "请输入提交信息: " commit_msg
        if [ -z "$commit_msg" ]; then
            commit_msg="Initial commit: 量数风行 - 美股舆情风险分析平台"
        fi
        git commit -m "$commit_msg"
        echo "✅ 更改已提交"
    fi
fi

# 检查是否已配置远程仓库
if git remote | grep -q origin; then
    echo ""
    echo "✅ 已配置远程仓库："
    git remote -v
    echo ""
    read -p "是否推送到远程仓库？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # 获取当前分支
        current_branch=$(git branch --show-current)
        echo "📤 推送到 origin/$current_branch..."
        git push -u origin "$current_branch"
        echo "✅ 推送成功！"
    fi
else
    echo ""
    echo "⚠️  未配置远程仓库"
    echo ""
    echo "请按照以下步骤操作："
    echo ""
    echo "1. 访问 https://github.com/new 创建新仓库"
    echo "2. 仓库名称建议：quantywind"
    echo "3. 选择 Public（公开）"
    echo "4. 不要勾选任何初始化选项"
    echo "5. 创建后复制仓库 URL"
    echo ""
    read -p "请输入您的 GitHub 仓库 URL: " repo_url
    
    if [ -z "$repo_url" ]; then
        echo "❌ 未输入仓库 URL，取消发布"
        exit 1
    fi
    
    # 添加远程仓库
    git remote add origin "$repo_url"
    echo "✅ 已添加远程仓库"
    
    # 推送
    current_branch=$(git branch --show-current)
    if [ -z "$current_branch" ]; then
        current_branch="main"
        git branch -M main
    fi
    
    echo "📤 推送到 origin/$current_branch..."
    git push -u origin "$current_branch"
    echo "✅ 推送成功！"
fi

echo ""
echo "=================================="
echo "🎉 发布完成！"
echo "=================================="
echo ""
echo "下一步："
echo ""
echo "1. 访问您的 GitHub 仓库"
echo "2. 检查所有文件是否正确上传"
echo "3. 更新 README.md 中的链接（替换 yourusername）"
echo "4. 在仓库设置中添加 Topics 标签"
echo "5. 创建第一个 Release (可选)"
echo ""
echo "📖 详细说明请查看 HOW_TO_PUBLISH.md"
echo ""
