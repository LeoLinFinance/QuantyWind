#!/bin/bash

# OpenClaw 失败 Skills 重试安装脚本
# 只安装在仓库中存在的 skills

echo "🦞 开始重试安装失败的 OpenClaw Skills..."
echo "=================================="

# 在仓库中存在的失败 skills 列表
skills=(
    "agent-memory"
    "ai-ppt-generator"
    "ai-proposal-generator"
    "blog-writer"
    "causal-inference"
    "camoufox-stealth"
    "claw-swarm"
    "content-ideas-generator"
    "context-recovery"
    "copywriter"
    "create-cli"
    "memory-baidu-embedding-db"
    "moltguard"
    "notion"
    "qwen-image"
    "senior-data-scientist"
    "skill-creator"
)

# 统计
total=${#skills[@]}
success=0
failed=0
failed_skills=()

# 安装每个 skill
for i in "${!skills[@]}"; do
    skill="${skills[$i]}"
    current=$((i + 1))
    
    echo ""
    echo "[$current/$total] 正在重试安装: $skill"
    echo "-----------------------------------"
    
    if clawhub install "$skill" --force; then
        echo "✅ $skill 安装成功"
        ((success++))
    else
        echo "❌ $skill 安装失败"
        ((failed++))
        failed_skills+=("$skill")
    fi
    
    # 添加短暂延迟，避免速率限制
    sleep 2
done

# 输出统计结果
echo ""
echo "=================================="
echo "📊 重试安装完成统计"
echo "=================================="
echo "总计: $total"
echo "成功: $success"
echo "失败: $failed"

if [ $failed -gt 0 ]; then
    echo ""
    echo "❌ 仍然失败的 Skills:"
    for skill in "${failed_skills[@]}"; do
        echo "  - $skill"
    done
fi

echo ""
echo "🦞 重试安装完成！"
