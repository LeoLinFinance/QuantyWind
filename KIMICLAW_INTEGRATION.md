# KimiClaw API 集成说明

## 概述

智者论坛使用KimiClaw机器人进行自动化的新闻资讯抓取和总结。本文档说明如何与KimiClaw进行集成。

## 当前实现

目前系统使用Kimi API（Moonshot）的web_search功能来模拟KimiClaw的行为。

### API配置
- **API地址**: https://api.moonshot.cn/v1/chat/completions
- **API Key**: 已在`backend/services/kimi_research_service.py`中配置
- **模型**: moonshot-v1-8k
- **功能**: 启用$web_search工具进行实时信息搜索

## 如果你有独立的KimiClaw服务

如果你已经部署了独立的KimiClaw机器人服务，需要进行以下集成：

### 1. KimiClaw服务端点

你需要提供以下信息：
- **KimiClaw API地址**: 例如 `https://your-kimiclaw-service.com/api`
- **认证方式**: API Key、Token或其他认证方式
- **输入格式**: KimiClaw期望接收的请求格式
- **输出格式**: KimiClaw返回的响应格式

### 2. 修改集成代码

在`backend/services/expert_forum_service.py`中修改`fetch_news_summary`方法：

```python
async def fetch_news_summary(self, last_time: Optional[str] = None) -> Dict:
    """使用独立的KimiClaw服务"""
    
    # 构建请求
    kimiclaw_request = {
        'action': 'summarize_news',
        'time_range': {
            'from': last_time or (datetime.now() - timedelta(hours=24)).isoformat(),
            'to': datetime.now().isoformat()
        },
        'topics': [
            '宏观经济信息',
            '全球金融市场动态',
            '市场及国家风险舆情',
            '央行和联储态度'
        ],
        'stock_symbols': self.portfolio_service.get_holdings_symbols()
    }
    
    # 调用KimiClaw API
    response = requests.post(
        'YOUR_KIMICLAW_API_URL',
        headers={'Authorization': 'Bearer YOUR_API_KEY'},
        json=kimiclaw_request,
        timeout=60
    )
    
    if response.status_code == 200:
        data = response.json()
        return {
            'content': data['summary'],  # 根据实际返回格式调整
            'timestamp': datetime.now().isoformat(),
            'stock_symbols': kimiclaw_request['stock_symbols']
        }
    else:
        raise Exception(f"KimiClaw API错误: {response.status_code}")
```

### 3. 周期性任务配置

如果KimiClaw需要后端定时触发（而不是前端定时），可以在`backend/services/scheduler.py`中添加：

```python
from apscheduler.schedulers.background import BackgroundScheduler
from services.expert_forum_service import ExpertForumService

scheduler = BackgroundScheduler()
expert_service = ExpertForumService()

def scheduled_news_fetch():
    """每小时获取一次新闻"""
    # 检查是否启用
    if expert_service.is_news_enabled():
        asyncio.run(expert_service.fetch_news_summary())

# 每小时执行一次
scheduler.add_job(scheduled_news_fetch, 'interval', hours=1)
scheduler.start()
```

## 输入输出规范

### 输入到KimiClaw

```json
{
  "query": "请帮我总结2024-01-01T00:00:00到目前关键的金融经济资讯...",
  "last_update_time": "2024-01-01T00:00:00",
  "stock_symbols": ["AAPL", "TSLA", "NVDA"],
  "topics": [
    "宏观经济信息",
    "全球金融市场动态",
    "市场及国家风险舆情",
    "央行和联储态度"
  ]
}
```

### 从KimiClaw接收输出

```json
{
  "summary": "【宏观经济】...\n【金融市场】...\n【风险舆情】...",
  "timestamp": "2024-01-01T12:00:00",
  "sources": ["Bloomberg", "Reuters", "WSJ"],
  "stock_updates": {
    "AAPL": "苹果公司发布新产品...",
    "TSLA": "特斯拉交付量超预期..."
  }
}
```

## 停止推送

当用户关闭"接收资讯"开关时，系统会调用：

```
POST /api/expert-forum/news/stop
```

你可以在KimiClaw端实现相应的停止逻辑，例如：
- 标记该用户为"暂停状态"
- 停止向该用户推送消息
- 清理相关的定时任务

## 测试KimiClaw集成

使用以下命令测试：

```bash
python test_expert_forum.py
```

这将测试：
1. 投资组合管理
2. 新闻资讯获取
3. 专家配置保存
4. 专家分析功能

## 需要确认的信息

请提供以下信息以完成KimiClaw集成：

1. **KimiClaw API地址**: _________________
2. **认证方式**: _________________
3. **API Key/Token**: _________________
4. **请求格式**: _________________
5. **响应格式**: _________________
6. **是否支持周期性推送**: 是 / 否
7. **推送方式**: Webhook / 轮询 / 其他

提供这些信息后，我可以帮你完成精确的集成。
