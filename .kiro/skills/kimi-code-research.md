---
name: kimi-code-research
description: 使用Kimi Code进行在线信息研究和数据挖掘
version: 1.0.0
---

# Kimi Code 在线研究技能

这个技能允许你使用Kimi Code API来获取实时的在线信息，用于辅助AI分析。

## API配置

- API ID: 19cdc354-b242-8ea9-8000-000006667892
- API Key: sk-kimi-cpp9rp8QVOmqkmTv51bmaP6rGLRgUUNI1ztpAXjVWfCdi5Mb1nbrdODF5Fd25xJ0
- Endpoint: https://api.moonshot.cn/v1/chat/completions

## 使用场景

### 1. 股票基本面研究
获取公司最新的财务数据、新闻、分析师评级等信息。

### 2. 行业趋势分析
研究特定行业的最新动态、技术变革、政策影响。

### 3. 宏观经济数据
获取最新的经济指标、央行政策、市场情绪。

### 4. 竞争对手分析
比较同行业公司的表现、市场份额、创新能力。

## 调用示例

```python
import requests

def research_with_kimi_code(query: str) -> str:
    """使用Kimi Code进行在线研究"""
    
    headers = {
        'Authorization': 'Bearer sk-kimi-cpp9rp8QVOmqkmTv51bmaP6rGLRgUUNI1ztpAXjVWfCdi5Mb1nbrdODF5Fd25xJ0',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': 'moonshot-v1-8k',  # 使用8k模型降低成本
        'messages': [
            {
                'role': 'system',
                'content': '你是一个专业的金融研究助手，擅长从互联网上搜集和分析最新的市场信息。'
            },
            {
                'role': 'user',
                'content': query
            }
        ],
        'tools': [
            {
                'type': 'builtin_function',
                'function': {
                    'name': '$web_search'
                }
            }
        ],
        'temperature': 0.3
    }
    
    response = requests.post(
        'https://api.moonshot.cn/v1/chat/completions',
        headers=headers,
        json=data,
        timeout=60
    )
    
    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content']
    else:
        return f"研究失败: {response.status_code}"
```

## 研究模板

### 股票深度研究
```
请研究{symbol}公司的最新情况：
1. 最近一个季度的财务表现
2. 近期重大新闻和事件
3. 分析师评级和目标价
4. 行业地位和竞争优势
5. 主要风险因素
```

### 行业趋势研究
```
请分析{industry}行业的最新趋势：
1. 行业增长率和市场规模
2. 技术创新和变革
3. 政策法规影响
4. 主要参与者和竞争格局
5. 未来发展机会
```

### 宏观经济研究
```
请分析当前宏观经济环境对{sector}板块的影响：
1. 最新经济指标（GDP、通胀、就业）
2. 央行货币政策
3. 市场情绪和投资者信心
4. 地缘政治风险
5. 对该板块的具体影响
```

## 注意事项

1. **API配额**: Kimi Code有调用限制，请合理使用
2. **缓存结果**: 对于相同的研究问题，建议缓存结果
3. **信息验证**: 在线信息需要交叉验证，不要完全依赖单一来源
4. **时效性**: 在线信息更新快，注意信息的时间戳
5. **合规性**: 确保使用的信息符合相关法规要求

## 集成到AI分析

在AI分析服务中，可以这样使用：

```python
# 1. 使用Kimi Code获取最新信息
research_result = research_with_kimi_code(
    f"请研究{symbol}公司最近的重大新闻和财务表现"
)

# 2. 将研究结果整合到分析prompt中
user_prompt = f"""
...现有的技术分析数据...

【在线研究信息】
{research_result}

请综合以上信息进行分析...
"""
```

## 优势

- ✅ 实时信息：获取最新的市场动态
- ✅ 深度研究：可以进行多轮对话深入挖掘
- ✅ 多维度：覆盖财务、新闻、分析师观点等
- ✅ 智能总结：自动提取关键信息
- ✅ 可验证：提供信息来源链接
