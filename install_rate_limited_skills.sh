#!/bin/bash

# OpenClaw 速率限制失败 Skills 重试安装脚本
# 使用更长的延迟时间避免速率限制

echo "🦞 开始重试安装因速率限制失败的 OpenClaw Skills..."
echo "⏰ 使用较长延迟时间避免速率限制"
echo "=================================="

# 因速率限制失败的 skills 列表
skills=(
    "agent-memory"
    "ai-ppt-generator"
    "content-ideas-generator"
    "context-recovery"
    "copywriter"
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
    echo "[$current/$total] 正在安装: $skill"
    echo "-----------------------------------"
    
    # 尝试安装，最多重试3次
    retry_count=0
    max_retries=3
    installed=false
    
    while [ $retry_count -lt $max_retries ] && [ "$installed" = false ]; do
        if [ $retry_count -gt 0 ]; then
            echo "⚠️  第 $((retry_count + 1)) 次尝试..."
            sleep 10  # 重试前等待10秒
        fi
        
        if clawhub install "$skill" --force 2>&1 | tee /tmp/install_output.txt; then
            if ! grep -q "Rate limit exceeded" /tmp/install_output.txt; then
                echo "✅ $skill 安装成功"
                ((success++))
                installed=true
            else
                echo "⚠️  遇到速率限制，等待后重试..."
                ((retry_count++))
                sleep 15
            fi
        else
            if grep -q "Rate limit exceeded" /tmp/install_output.txt; then
                echo "⚠️  遇到速率限制，等待后重试..."
                ((retry_count++))
                sleep 15
            else
                echo "❌ $skill 安装失败（非速率限制原因）"
                ((failed++))
                failed_skills+=("$skill")
                break
            fi
        fi
    done
    
    if [ "$installed" = false ] && [ $retry_count -ge $max_retries ]; then
        echo "❌ $skill 安装失败（达到最大重试次数）"
        ((failed++))
        failed_skills+=("$skill")
    fi
    
    # 每个skill之间添加较长延迟，避免速率限制
    if [ $current -lt $total ]; then
        echo "⏳ 等待 20 秒后继续下一个..."
        sleep 20
    fi
done

# 清理临时文件
rm -f /tmp/install_output.txt

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
    echo "❌ 仍然失败的 Skills:"
    for skill in "${failed_skills[@]}"; do
        echo "  - $skill"
    done
    echo ""
    echo "💡 建议: 可以稍后手动重试这些 skills"
    echo "   命令: clawhub install <skill-name> --force"
fi

echo ""
echo "🦞 重试安装完成！"
