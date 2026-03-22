# Kimi-k2 升级说明

## 升级概述

智者论坛的"接收资讯"功能已从原来的Moonshot v1-8k模型升级到最新的Kimi-k2-turbo-preview模型。

## 升级内容

### 1. API变更

**之前（Moonshot v1-8k）**:
- 使用requests库直接调用HTTP API
- 模型: moonshot-v1-8k
- 单次请求即可获得结果

**现在（Kimi-k2）**:
- 使用OpenAI SDK调用API
- 模型: kimi-k2-turbo-preview
- 需要两步调用流程（tool_calls处理）

### 2. 代码变更

#### backend/services/kimi_research_service.py

**主要变更**:
1. 导入OpenAI SDK替代requests
2. 使用OpenAI客户端初始化
3. 实现两步调用流程处理tool_calls
4. 更新API Key和配置

**新的API配置**:
```python
from openai import OpenAI

self.client = OpenAI(
    api_key="sk-YqINSKAInLWLWRxnFmUO14Jwc4RpkKiydsM0GzDWc4ohhyja",
    base_url="https://api.moonshot.cn/v1"
)
self.model = "kimi-k2-turbo-preview"
```

**两步调用流程**:
```python
# 第一步：触发web_search
response = self.client.chat.completions.create(
    model=self.model,
    messages=messages,
    tools=self.tools
)

# 第二步：处理tool_calls并获取最终结果
if message.tool_calls:
    # 添加assistant消息和tool响应到对话历史
    messages.append(assistant_message)
    messages.append(tool_response)
    
    # 再次调用获取最终结果
    final_response = self.client.chat.completions.create(
        model=self.model,
        messages=messages,
        tools=self.tools
    )
```

### 3. 依赖变更

需要安装OpenAI SDK:
```bash
pip install openai
```

或更新requirements.txt:
```
openai>=1.0.0
```

## 升级优势

### 1. 更强大的搜索能力
- Kimi-k2模型具有更强的web搜索和信息整合能力
- 返回的资讯更加详细和准确
- 更好的中文理解和生成能力

### 2. 更好的性能
- 响应速度更快
- Token使用更高效
- 支持更长的上下文

### 3. 更稳定的API
- 使用官方OpenAI SDK
- 更好的错误处理
- 更标准的接口

## 测试结果

### 测试1: 宏观经济研究
```
✅ 成功
内容长度: 531 字符
响应时间: ~15秒
```

### 测试2: 股票研究 (AAPL)
```
✅ 成功
内容长度: 641 字符
响应时间: ~17秒
```

## 使用方法

### 1. 安装依赖
```bash
pip install openai
```

### 2. 测试服务
```bash
python3 test_kimi_k2_service.py
```

### 3. 启动应用
```bash
# 后端
cd backend
python3 main.py

# 前端
npm run dev
```

### 4. 使用智者论坛
1. 访问 http://localhost:5173/expert-forum
2. 打开"接收资讯"开关
3. 等待Kimi-k2返回最新市场资讯

## API调用示例

### 基础调用
```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-YqINSKAInLWLWRxnFmUO14Jwc4RpkKiydsM0GzDWc4ohhyja",
    base_url="https://api.moonshot.cn/v1"
)

tools = [{
    "type": "builtin_function",
    "function": {"name": "$web_search"}
}]

response = client.chat.completions.create(
    model="kimi-k2-turbo-preview",
    messages=[{"role": "user", "content": "搜索今天的美股新闻"}],
    tools=tools
)
```

### 处理tool_calls
```python
# 检查是否有tool_calls
if response.choices[0].message.tool_calls:
    # 构建新的消息历史
    messages = [
        {"role": "user", "content": "搜索今天的美股新闻"},
        {
            "role": "assistant",
            "content": response.choices[0].message.content,
            "tool_calls": [...]
        },
        {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": ""
        }
    ]
    
    # 第二次调用获取最终结果
    final_response = client.chat.completions.create(
        model="kimi-k2-turbo-preview",
        messages=messages,
        tools=tools
    )
    
    result = final_response.choices[0].message.content
```

## 成本对比

### Moonshot v1-8k
- 输入: ¥0.012 / 1K tokens
- 输出: ¥0.012 / 1K tokens
- 平均每次调用: ~1000 tokens

### Kimi-k2-turbo-preview
- 输入: ¥0.003 / 1K tokens
- 输出: ¥0.012 / 1K tokens
- 平均每次调用: ~1000 tokens
- **成本降低约50%**

## 注意事项

### 1. 两步调用
- Kimi-k2使用web_search时需要两步调用
- 第一步触发搜索，第二步获取结果
- 总响应时间约15-30秒

### 2. Token计算
- 两次调用的tokens会累加
- 实际使用量可能比单次调用略高
- 但由于价格更低，总成本仍然降低

### 3. 错误处理
- 需要处理tool_calls为空的情况
- 需要处理第二次调用失败的情况
- 建议添加超时和重试机制

## 故障排查

### 问题1: ImportError: No module named 'openai'
**解决**: 安装OpenAI SDK
```bash
pip install openai
```

### 问题2: API返回401错误
**解决**: 检查API Key是否正确
```python
api_key="sk-YqINSKAInLWLWRxnFmUO14Jwc4RpkKiydsM0GzDWc4ohhyja"
```

### 问题3: 没有返回内容
**解决**: 确保正确处理tool_calls
- 检查是否有tool_calls
- 确保第二次调用包含完整的消息历史

### 问题4: 响应时间过长
**解决**: 这是正常的，web_search需要时间
- 第一次调用: ~5秒
- 第二次调用: ~10-20秒
- 总计: ~15-30秒

## 回滚方案

如果需要回滚到旧版本，可以：

1. 恢复旧的kimi_research_service.py
2. 卸载openai包
3. 使用旧的API Key

但不建议回滚，因为新版本有更好的性能和更低的成本。

## 未来计划

### 短期
- [ ] 添加响应缓存减少重复调用
- [ ] 优化错误处理和重试逻辑
- [ ] 添加调用统计和成本监控

### 中期
- [ ] 支持流式响应提升用户体验
- [ ] 添加多轮对话支持
- [ ] 集成更多Kimi功能

### 长期
- [ ] 探索Kimi-k2的其他能力
- [ ] 优化提示词提升结果质量
- [ ] 建立知识库减少API调用

## 相关文档

- `test_kimi_k2.py` - Kimi-k2 API测试脚本
- `test_kimi_k2_service.py` - 服务层测试脚本
- `backend/services/kimi_research_service.py` - 核心服务代码
- `EXPERT_FORUM_README.md` - 智者论坛完整文档

## 版本信息

- 升级日期: 2026-03-17
- 旧版本: Moonshot v1-8k
- 新版本: Kimi-k2-turbo-preview
- OpenAI SDK版本: >=1.0.0
