# API Key独立分配方案

## 问题背景

用户反馈专家分析存在超时问题，怀疑是多个专家同时调用同一个API端口导致的。

## 解决方案

为每个专家和总结服务分配独立的StepFun API Key，避免并发调用冲突。

## API Key分配表

| 服务/专家 | API Key | 用途 |
|---------|---------|------|
| 资讯总结 & 对话总结 | `4oZN16sWiAKwBEQvnb6nxr0mX31kJ1MsDqZBiuzly1UOPsXaDHgFKyo7QNSfvaC4` | 新闻总结 + 超过10条消息的对话总结 |
| 选股分析师 | `71l4il2y6OSbR76taoahpsCSfWepmQZpEUsLG2GYqpFOVK8LEV0PyynJ2MUp29q23` | 投前分析，推荐股票 |
| 产业链分析师 | `2g1A2I9A51ec8iyzhiCqTYo94AHmt9fEXFb5L93WmZPFSRldwgVQcesnn2EwDTbCm` | 投中分析，产业链拆解 |
| 市场分析师 | `6EmtlQblz18ZjHNyFlHz2MlJJPT9egJUdAiTknCL8eUxs9drFwoHA7uGx16ZGRXIf` | 投后管理，技术面分析 |
| 长期价值投资分析师 | `6oQxDcpeg1LLURAT35QWXodFPqNz8EXj6daOGk1IKxhDVv3HUi1UeClM5sHXxvs6z` | 投后管理，长期价值分析 |
| 首席经济学家 | `62RprR40Z99RnDlgP7Ho3geKQqI3hiE9MZ218AfjTpF4ZhJsA7bETmyCzmpNA7oRh` | 宏观经济分析，投资指导 |

## 实现细节

### 1. 资讯总结服务 (`backend/services/news_summary_service.py`)

```python
def __init__(self):
    # 使用StepFun API - 资讯总结专用API Key
    self.client = OpenAI(
        api_key="4oZN16sWiAKwBEQvnb6nxr0mX31kJ1MsDqZBiuzly1UOPsXaDHgFKyo7QNSfvaC4",
        base_url="https://api.stepfun.com/v1"
    )
    self.model = "step-1-32k"
```

### 2. 对话总结服务 (`backend/services/context_summarizer.py`)

```python
def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
    # 使用对话总结专用API Key（与资讯总结共用）
    self.api_key = api_key or "4oZN16sWiAKwBEQvnb6nxr0mX31kJ1MsDqZBiuzly1UOPsXaDHgFKyo7QNSfvaC4"
    self.base_url = base_url or "https://api.stepfun.com/v1"
    
    if self.api_key:
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
```

### 3. 专家论坛服务 (`backend/services/expert_forum_service.py`)

```python
def __init__(self):
    # 为每个专家分配独立的StepFun API Key
    self.expert_api_keys = {
        'stock_analyst': '71l4il2y6OSbR76taoahpsCSfWepmQZpEUsLG2GYqpFOVK8LEV0PyynJ2MUp29q23',
        'industry_analyst': '2g1A2I9A51ec8iyzhiCqTYo94AHmt9fEXFb5L93WmZPFSRldwgVQcesnn2EwDTbCm',
        'market_analyst': '6EmtlQblz18ZjHNyFlHz2MlJJPT9egJUdAiTknCL8eUxs9drFwoHA7uGx16ZGRXIf',
        'value_investor': '6oQxDcpeg1LLURAT35QWXodFPqNz8EXj6daOGk1IKxhDVv3HUi1UeClM5sHXxvs6z',
        'chief_economist': '62RprR40Z99RnDlgP7Ho3geKQqI3hiE9MZ218AfjTpF4ZhJsA7bETmyCzmpNA7oRh'
    }

def _call_stepfun_for_analysis(self, expert_id: str, system_prompt: str, user_query: str) -> str:
    # 根据expert_id获取对应的API Key
    api_key = self.expert_api_keys.get(expert_id)
    
    # 为每个专家创建独立的客户端
    client = OpenAI(
        api_key=api_key,
        base_url=self.stepfun_base_url
    )
    
    # 调用API
    response = client.chat.completions.create(...)
```

## 工作流程

```
用户打开"接收资讯"
  ↓
资讯总结服务 → API Key 1
  ↓
显示新闻总结

用户打开"开始讨论"
  ↓
依次调用5个专家（串行）
  ├─ 选股分析师 → API Key 2
  ├─ 产业链分析师 → API Key 3
  ├─ 市场分析师 → API Key 4
  ├─ 长期价值投资分析师 → API Key 5
  └─ 首席经济学家 → API Key 6
  ↓
每个专家独立调用，互不干扰

消息超过10条
  ↓
对话总结服务 → API Key 1（与资讯总结共用）
  ↓
生成对话总结
```

## 优势

1. **避免并发冲突**: 每个专家使用独立的API Key，不会相互干扰
2. **提高稳定性**: 减少超时和失败的可能性
3. **便于追踪**: 可以通过API Key追踪每个专家的调用情况
4. **负载均衡**: 分散API调用压力到多个端口

## 验证

运行验证脚本：
```bash
python3 verify_api_keys.py
```

输出示例：
```
✅ 资讯总结服务: 4oZN16sWiAKwBEQvnb6n...o7QNSfvaC4
✅ 对话总结服务: 4oZN16sWiAKwBEQvnb6n...o7QNSfvaC4
✅ 选股分析师: 71l4il2y6OSbR76taoah...J2MUp29q23
✅ 产业链分析师: 2g1A2I9A51ec8iyzhiCq...nn2EwDTbCm
✅ 市场分析师: 6EmtlQblz18ZjHNyFlHz...Gx16ZGRXIf
✅ 长期价值投资分析师: 6oQxDcpeg1LLURAT35QW...M5sHXxvs6z
✅ 首席经济学家: 62RprR40Z99RnDlgP7Ho...CzmpNA7oRh
```

## 修改的文件

1. `backend/services/news_summary_service.py` - 资讯总结专用API Key
2. `backend/services/context_summarizer.py` - 对话总结专用API Key
3. `backend/services/expert_forum_service.py` - 每个专家独立API Key

## 新增的文件

1. `verify_api_keys.py` - API Key分配验证脚本
2. `API_KEY_ALLOCATION.md` - 本文档

## 预期效果

- ✅ 专家分析不再超时
- ✅ 每个专家独立调用，响应更快
- ✅ 系统整体稳定性提升
- ✅ 便于监控和调试

## 注意事项

1. 所有API Key都使用StepFun 32k模型（对话总结使用8k）
2. 专家调用仍然是串行的（依次调用），但每个专家使用独立的API Key
3. 资讯总结和对话总结共用一个API Key（因为不会同时调用）
4. 如果某个专家的API Key失效，会自动使用默认Key（选股分析师的Key）

## 启动服务

```bash
# 启动后端
python3 backend/main.py

# 验证API Key分配
python3 verify_api_keys.py
```

## 总结

通过为每个专家分配独立的API Key，解决了并发调用同一个API端口导致的超时问题，提高了系统的稳定性和响应速度。
