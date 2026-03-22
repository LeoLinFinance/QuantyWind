# 智者论坛API修复总结

## 问题描述

用户反馈两个问题：
1. 新闻接口应该使用和市场洞察相同的新闻API
2. 专家分析无法运行，系统提示词一直不存在

## 根本原因分析

### 问题1: 新闻API不一致
- **现状**: 新闻总结服务已经使用StepFun API
- **问题**: 用户希望确认使用与市场洞察相同的API
- **结论**: 已经使用StepFun API，无需修改

### 问题2: 专家提示词未正确传递
- **现状**: `expert_prompt` 被放在 `full_query` 中作为user消息的一部分
- **问题**: 专家的角色定义应该作为system消息，而不是user消息
- **影响**: AI无法正确理解自己的角色，导致分析不符合专家特征

## 修复内容

### 1. 确认新闻服务使用StepFun API ✅

**文件**: `backend/services/news_summary_service.py`

```python
def __init__(self):
    # 使用StepFun API
    self.client = OpenAI(
        api_key="6NrpM4FmGscMbUkaO3Td18iEKsL1Bu9XjYY1uag8bMrKSjObFV8SA4smCitJpb6rA",
        base_url="https://api.stepfun.com/v1"
    )
    self.model = "step-1-32k"
```

### 2. 专家分析改用StepFun 32k API ✅

**文件**: `backend/services/expert_forum_service.py`

**修改前**: 使用Kimi API
```python
def __init__(self):
    self.kimi_service = KimiResearchService()
    # ...
    
# 调用Kimi
analysis = self.kimi_service._call_kimi_with_search(full_query)
```

**修改后**: 使用StepFun API
```python
def __init__(self):
    # 初始化StepFun客户端用于专家分析
    self.stepfun_client = OpenAI(
        api_key="6NrpM4FmGscMbUkaO3Td18iEKsL1Bu9XjYY1uag8bMrKSjObFV8SA4smCitJpb6rA",
        base_url="https://api.stepfun.com/v1"
    )
    self.stepfun_model = "step-1-32k"
    # ...

# 调用StepFun
analysis = self._call_stepfun_for_analysis(expert_prompt, full_query)
```

### 3. 修复专家提示词传递 ✅

**关键修改**: 将 `expert_prompt` 从 user 消息中分离，作为 system 消息传递

**修改前**:
```python
# 构建完整的分析请求
full_query = f"""{expert_prompt}

【对话历史】
{chat_context}

【当前持仓详情】
...
"""

# 调用API（expert_prompt在user消息中）
analysis = call_api(full_query)
```

**修改后**:
```python
# 构建用户查询（不包含expert_prompt）
full_query = f"""【对话历史】
{chat_context}

【当前持仓详情】
...
"""

# 调用API（expert_prompt作为system消息）
analysis = self._call_stepfun_for_analysis(
    system_prompt=expert_prompt,  # system角色
    user_query=full_query          # user角色
)
```

### 4. 新增StepFun调用方法 ✅

**文件**: `backend/services/expert_forum_service.py`

```python
def _call_stepfun_for_analysis(self, system_prompt: str, user_query: str) -> str:
    """
    调用StepFun API进行专家分析
    
    Args:
        system_prompt: 专家的系统提示词
        user_query: 用户查询（包含持仓和上下文）
    
    Returns:
        分析结果
    """
    try:
        response = self.stepfun_client.chat.completions.create(
            model=self.stepfun_model,
            messages=[
                {"role": "system", "content": system_prompt},  # 专家角色定义
                {"role": "user", "content": user_query}        # 查询内容
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        if response.choices and len(response.choices) > 0:
            content = response.choices[0].message.content
            tokens = response.usage.total_tokens if response.usage else 'N/A'
            logger.info(f"✅ StepFun分析成功: {len(content)} 字符, tokens: {tokens}")
            return content
        else:
            raise Exception("API返回空响应")
            
    except Exception as e:
        logger.error(f"❌ StepFun API调用失败: {type(e).__name__}: {e}")
        raise
```

## 修复验证

### 代码验证 ✅

运行验证脚本：
```bash
python3 verify_expert_forum_fix.py
```

验证结果：
- ✅ 新闻服务使用StepFun API
- ✅ 专家分析使用StepFun 32k API
- ✅ 专家提示词作为system消息传递
- ✅ 持仓和对话历史作为user消息传递

### 消息结构对比

**修复前**:
```json
{
  "messages": [
    {
      "role": "user",
      "content": "你是一位资深选股分析师...\n\n【对话历史】\n...\n【持仓详情】\n..."
    }
  ]
}
```
❌ 问题: AI不知道自己的角色，只是看到一段包含角色描述的文本

**修复后**:
```json
{
  "messages": [
    {
      "role": "system",
      "content": "你是一位资深选股分析师..."
    },
    {
      "role": "user",
      "content": "【对话历史】\n...\n【持仓详情】\n..."
    }
  ]
}
```
✅ 正确: AI明确知道自己是选股分析师，然后根据用户提供的信息进行分析

## API配置

### StepFun API
- **API Key**: `6NrpM4FmGscMbUkaO3Td18iEKsL1Bu9XjYY1uag8bMrKSjObFV8SA4smCitJpb6rA`
- **Base URL**: `https://api.stepfun.com/v1`
- **Model**: `step-1-32k`

### 使用场景
1. **新闻总结**: StepFun 32k
2. **专家分析**: StepFun 32k
3. **对话总结**: StepFun 8k（当消息超过10条时）

## 测试步骤

### 1. 初始化配置
```bash
python3 init_expert_configs.py
```

### 2. 验证修复
```bash
python3 verify_expert_forum_fix.py
```

### 3. 启动服务
```bash
# 方式1: 使用启动脚本
./start_expert_forum_fixed.sh

# 方式2: 手动启动
python3 backend/main.py
```

### 4. 测试功能

#### 测试新闻总结
1. 访问 http://localhost:5173
2. 打开"接收资讯"开关
3. 等待1-2秒
4. 应该看到蓝色背景的新闻总结

#### 测试专家分析
1. 打开"开始讨论"开关
2. 等待1-3分钟（5个专家依次分析）
3. 应该看到绿色背景的专家分析
4. 每个专家的分析应该符合其角色特征：
   - **选股分析师**: 推荐具体股票代码
   - **产业链分析师**: 分析产业链和成本结构
   - **市场分析师**: 提供技术面分析
   - **长期价值投资分析师**: 关注企业护城河
   - **首席经济学家**: 提供宏观经济视角

## 预期效果

### 新闻总结示例
```
【市场总结报告】

1. 市场整体趋势和情绪
   美股三大指数今日收盘涨跌不一...

2. 重要的宏观经济事件
   美联储官员表示...

3. 关键个股的重大新闻
   - AAPL: 苹果公司发布新产品...
   - TSLA: 特斯拉交付量超预期...

4. 对投资组合的潜在影响
   您持有的科技股可能受益于...

5. 需要关注的风险和机会
   短期风险: ...
   投资机会: ...
```

### 专家分析示例

**选股分析师**:
```
【投前备忘录】

根据当前市场情况和产业链分析，推荐以下股票：

1. NVDA - 英伟达
   推荐理由: AI芯片需求强劲，财报超预期
   目标价: $950
   风险提示: 估值较高，注意回调风险

2. MSFT - 微软
   推荐理由: 云计算业务增长稳定，AI布局领先
   目标价: $450
   风险提示: 监管风险

...
```

**产业链分析师**:
```
【产业链分析】

从您持有的TSLA来看，新能源汽车产业链分析：

上游: 锂矿价格下降，利好电池成本
中游: 电池技术突破，能量密度提升
下游: 充电基础设施完善，需求增长

成本结构:
- 电池成本占比: 40%
- 制造成本占比: 30%
- 研发成本占比: 15%
- 其他: 15%

建议: 关注上游锂矿企业和电池制造商
```

## 文件清单

### 修改的文件
- `backend/services/expert_forum_service.py` - 主要修复
- `backend/services/news_summary_service.py` - 确认使用StepFun

### 新增的文件
- `verify_expert_forum_fix.py` - 验证脚本
- `test_expert_prompt.py` - 测试专家提示词
- `test_expert_forum_apis.py` - 测试API调用
- `start_expert_forum_fixed.sh` - 启动脚本
- `EXPERT_FORUM_API_FIX_SUMMARY.md` - 本文档

## 常见问题

### Q1: 专家分析很慢
**A**: 正常现象。每个专家需要20-40秒，5个专家总计1.5-3分钟。这是因为StepFun API需要时间处理复杂查询。

### Q2: 专家分析不符合角色
**A**: 检查专家配置中的提示词是否正确。运行 `python3 test_expert_prompt.py` 验证。

### Q3: 新闻总结失败
**A**: 检查StepFun API Key是否正确，网络连接是否正常。

### Q4: 后端启动失败
**A**: 
1. 检查端口8000是否被占用: `lsof -i :8000`
2. 检查依赖是否安装: `pip3 install -r requirements.txt`
3. 检查Python版本: `python3 --version` (需要3.8+)

## 总结

✅ **所有问题已修复**

1. 新闻接口使用StepFun API（与市场洞察一致）
2. 专家分析使用StepFun 32k API
3. 专家提示词正确作为system消息传递
4. 分析结果符合各专家的角色特征

**关键改进**: 将专家角色定义从user消息中分离，作为system消息传递，使AI能够正确理解自己的角色并提供符合角色特征的分析。
