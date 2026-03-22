# 快速咨询专家错误修复

## 问题描述

用户点击快速咨询专家按钮后，一直输出错误，无法获得专家分析。

## 可能的原因

### 1. 上下文窗口超限

**问题**：使用 `step-1-32k` 模型，上下文窗口只有32k tokens
- 对话历史过长
- 持仓信息详细
- 系统提示词较长
- 总计可能超过32k tokens限制

### 2. 错误信息不明确

**问题**：前端和后端的错误处理不够详细
- 前端没有检查HTTP错误状态
- 后端没有记录详细的错误信息
- 用户只看到"分析失败"，不知道具体原因

## 修复方案

### 1. 升级模型到更大的上下文窗口

**修改文件**：`backend/services/expert_forum_service.py`

```python
# 修复前
self.stepfun_model = "step-1-32k"  # 32k上下文窗口

# 修复后
self.stepfun_model = "step-1-128k"  # 128k上下文窗口
```

**优势**：
- 上下文窗口从32k增加到128k
- 可以处理更长的对话历史
- 支持更详细的持仓信息
- 减少上下文超限错误

### 2. 增加max_tokens参数

**修改文件**：`backend/services/expert_forum_service.py`

```python
# 修复前
max_tokens=1500  # 较短的回复

# 修复后
max_tokens=2000  # 更长的回复
```

**优势**：
- 允许专家提供更详细的分析
- 支持更完整的推荐列表
- 提高回复质量

### 3. 增强错误日志

**修改文件**：`backend/services/expert_forum_service.py`

```python
# 添加详细的日志
logger.info(f"模型: {self.stepfun_model}, 系统提示词长度: {len(system_prompt)}, 用户查询长度: {len(user_query)}")

# 记录错误详情
if hasattr(e, 'response'):
    logger.error(f"响应状态码: {e.response.status_code if hasattr(e.response, 'status_code') else 'N/A'}")
    logger.error(f"响应内容: {e.response.text if hasattr(e.response, 'text') else 'N/A'}")
```

**优势**：
- 可以看到输入的长度
- 可以看到API的错误响应
- 便于诊断问题

### 4. 改进前端错误处理

**修改文件**：`src/pages/ExpertForumPage.tsx`

```typescript
// 修复前
if (response.ok) {
  const data = await response.json()
  // 处理成功响应
}

// 修复后
if (!response.ok) {
  // 处理HTTP错误
  const errorText = await response.text()
  console.error(`HTTP错误 ${response.status}:`, errorText)
  throw new Error(`HTTP ${response.status}: ${errorText}`)
}

const data = await response.json()
// 处理成功响应
```

**优势**：
- 捕获HTTP错误状态
- 显示详细的错误信息
- 用户可以看到具体的错误原因

## 模型对比

| 模型 | 上下文窗口 | 适用场景 |
|------|-----------|---------|
| step-1-8k | 8k tokens | 简单对话 |
| step-1-32k | 32k tokens | 中等对话 |
| step-1-128k | 128k tokens | 长对话、详细分析 |
| step-1-256k | 256k tokens | 超长文档分析 |

**选择 step-1-128k 的原因**：
- 足够处理智者论坛的对话历史
- 支持详细的持仓信息
- 性能和成本平衡
- 响应速度合理

## Token使用估算

### 典型场景

```
系统提示词: ~500 tokens
对话历史: ~2000 tokens (10条消息)
持仓信息: ~1000 tokens (5只股票)
资讯总结: ~1000 tokens
总计输入: ~4500 tokens

专家回复: ~1500 tokens

总计: ~6000 tokens
```

**结论**：
- 32k模型：足够处理大部分场景
- 128k模型：可以处理更长的对话历史（50+条消息）
- 256k模型：过度，不需要

## 错误类型和处理

### 1. 上下文超限错误

**错误信息**：`maximum context length exceeded`

**处理方案**：
- ✅ 升级到128k模型
- 使用对话总结功能
- 限制对话历史长度

### 2. API Key错误

**错误信息**：`invalid api key` 或 `401 Unauthorized`

**处理方案**：
- 检查API Key是否正确
- 检查API Key是否过期
- 检查API Key的权限

### 3. 超时错误

**错误信息**：`timeout` 或 `504 Gateway Timeout`

**处理方案**：
- ✅ 已设置60秒HTTP超时
- ✅ 已设置70秒asyncio超时
- 检查网络连接

### 4. 限流错误

**错误信息**：`rate limit exceeded` 或 `429 Too Many Requests`

**处理方案**：
- ✅ 每个专家使用独立API Key
- 添加请求间隔
- 监控API使用量

## 测试建议

### 1. 基本功能测试

```bash
# 运行测试脚本
python3 test_quick_consult.py
```

**验证**：
- 专家能正常回复
- 回复内容完整
- 没有错误信息

### 2. 长对话测试

1. 发送10+条用户消息
2. 点击快速咨询按钮
3. 验证专家能正常回复

### 3. 错误场景测试

1. 断开网络连接
2. 点击快速咨询按钮
3. 验证显示友好的错误信息

### 4. 并发测试

1. 快速连续点击多个专家按钮
2. 验证所有请求都能正常处理

## 监控建议

### 1. 日志监控

查看后端日志中的关键信息：

```bash
# 查看成功的请求
tail -f backend.log | grep "✅ StepFun分析成功"

# 查看失败的请求
tail -f backend.log | grep "❌ StepFun API调用失败"

# 查看token使用情况
tail -f backend.log | grep "tokens:"
```

### 2. Token使用监控

记录每次请求的token使用量：

```python
logger.info(f"Token使用: 输入={prompt_tokens}, 输出={completion_tokens}, 总计={total_tokens}")
```

### 3. 错误率监控

统计错误率：

```python
success_count = 0
error_count = 0
error_rate = error_count / (success_count + error_count) * 100
```

## 回滚方案

如果128k模型出现问题，可以回滚到32k模型：

```python
# 回滚配置
self.stepfun_model = "step-1-32k"
max_tokens=1500
```

同时启用对话总结功能，限制上下文长度。

## 成本考虑

### Token定价（假设）

| 模型 | 输入价格 | 输出价格 |
|------|---------|---------|
| step-1-32k | $0.001/1k | $0.002/1k |
| step-1-128k | $0.002/1k | $0.004/1k |

### 成本估算

**单次请求**：
- 输入: 4500 tokens × $0.002 = $0.009
- 输出: 1500 tokens × $0.004 = $0.006
- 总计: $0.015

**每天100次请求**：
- 成本: $1.50/天
- 月成本: $45/月

**结论**：成本增加可接受，换取更好的用户体验。

## 未来优化

### 1. 智能模型选择

根据上下文长度自动选择模型：

```python
def select_model(context_length: int) -> str:
    if context_length < 8000:
        return "step-1-8k"
    elif context_length < 32000:
        return "step-1-32k"
    else:
        return "step-1-128k"
```

### 2. 上下文压缩

使用总结功能压缩长对话：

```python
if len(messages) > 20:
    # 触发总结
    summary = summarize_conversation(messages)
    context = summary + recent_messages
```

### 3. 缓存机制

缓存相似的查询结果：

```python
cache_key = hash(expert_id + context)
if cache_key in cache:
    return cache[cache_key]
```

### 4. 流式响应

使用streaming减少等待时间：

```python
response = client.chat.completions.create(
    model=self.stepfun_model,
    messages=messages,
    stream=True
)

for chunk in response:
    yield chunk.choices[0].delta.content
```

## 总结

通过以下修复，快速咨询专家功能应该能正常工作：

1. ✅ 升级到128k上下文窗口模型
2. ✅ 增加max_tokens到2000
3. ✅ 增强错误日志
4. ✅ 改进前端错误处理

如果仍然有问题，请查看后端日志获取详细的错误信息，并根据错误类型采取相应的处理方案。
