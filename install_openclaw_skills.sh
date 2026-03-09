#!/bin/bash

# OpenClaw Skills 批量安装脚本
# 使用 --force 参数强制安装

echo "🦞 开始批量安装 OpenClaw Skills..."
echo "=================================="

# Skills 列表
skills=(
    "PyTorch"
    "accli"
    "agent-church"
    "agent-config"
    "agent-docs"
    "agent-identity-kit"
    "agent-mail"
    "agent-memory"
    "agent-orchestration"
    "agent-orchestrator"
    "agentic-compass"
    "agenticflow-skill"
    "agentledger"
    "agile-product-owner"
    "ai-brand-analyzer"
    "ai-humanizer"
    "ai-meeting-notes"
    "ai-picture-book"
    "ai-ppt-generate"
    "ai-proposal-generator"
    "ai-skill-scanner"
    "apple-calendar"
    "apple-reminders"
    "atl-mobile"
    "auto-updater"
    "automation-workflows"
    "autonomous-skill-orchestrator"
    "backend-patterns"
    "blog-writer"
    "camoufox-stealth"
    "causal-inference"
    "claw-swarm"
    "clawpenflow"
    "clean-code"
    "comfy-cli"
    "content-creator"
    "content-ideas-generator"
    "context-recovery"
    "copywriter"
    "create-cli"
    "curl-http"
    "data-analyst"
    "docker-sandbox"
    "error-guard"
    "first-principles-decomposer"
    "gitai-skill"
    "imsg"
    "let-me-know"
    "memory-baidu-embedding-db"
    "moltguard"
    "notion"
    "python"
    "qwen-image"
    "raglite-library"
    "rationality"
    "reddit"
    "reddit-search"
    "restart-guard"
    "self-evolving-skill"
    "senior-data-scientist"
    "skill-creator"
    "ssh-tunnel"
    "tiangong-wps-ppt-automation"
    "tiangong-wps-word-automation"
    "web-deploy-github"
    "xiaohongshu-mcp"
    "yt-dlp-downloader-skill"
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
    echo "[$current/$total] 正在安装: $skill"
    echo "-----------------------------------"
    
    if clawhub install "$skill" --force; then
        echo "✅ $skill 安装成功"
        ((success++))
    else
        echo "❌ $skill 安装失败"
        ((failed++))
        failed_skills+=("$skill")
    fi
done

# 输出统计结果
echo ""
echo "=================================="
echo "📊 安装完成统计"
echo "=================================="
echo "总计: $total"
echo "成功: $success"
echo "失败: $failed"

if [ $failed -gt 0 ]; then
    echo ""
    echo "❌ 失败的 Skills:"
    for skill in "${failed_skills[@]}"; do
        echo "  - $skill"
    done
fi

echo ""
echo "🦞 批量安装完成！"
