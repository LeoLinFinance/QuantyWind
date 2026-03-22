# 开发指南

## 下一步开发任务

### 优先级P0（核心功能完善）

#### 1. 接入真实API数据
当前使用模拟数据，需要接入真实API：

**市场数据API集成**
- 在 `backend/services/market_service.py` 中集成IEX Cloud API
- 实现实时股价获取
- 实现指数数据获取

**舆情数据API集成**
- 在 `backend/services/sentiment_service.py` 中集成NewsAPI
- 实现新闻抓取和过滤
- 实现舆情数据清洗

**示例代码**：
```python
import requests
import os

class MarketDataAPI:
    def __init__(self):
        self.iex_token = os.getenv('IEX_CLOUD_TOKEN')
        self.base_url = 'https://cloud.iexapis.com/stable'
    
    def get_quote(self, symbol):
        url = f'{self.base_url}/stock/{symbol}/quote'
        params = {'token': self.iex_token}
        response = requests.get(url, params=params)
        return response.json()
```

#### 2. AI模型集成
集成大语言模型进行智能分析：

**创建AI服务**
- 新建 `backend/services/ai_service.py`
- 集成OpenAI API或开源模型
- 实现舆情分析、市场洞察生成

**示例代码**：
```python
import openai
import os

class AIService:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
    
    def analyze_sentiment(self, news_text):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一个专业的金融分析师"},
                {"role": "user", "content": f"分析以下新闻的市场影响（50字内）：{news_text}"}
            ]
        )
        return response.choices[0].message.content
```

#### 3. 数据集构建
为风险模型建立历史数据集：

**数据收集**
- 创建 `backend/data/` 目录
- 实现历史价格数据下载
- 实现历史舆情数据存储

**数据处理**
- 新建 `backend/services/data_processor.py`
- 实现数据清洗和标准化
- 建立训练/测试数据集

#### 4. 风险模型实现
将模拟的风险模型替换为真实计算：

**在 `backend/services/risk_service.py` 中实现**：
```python
import numpy as np
import pandas as pd
from scipy import stats

class RiskCalculator:
    def calculate_var(self, returns, confidence=0.95):
        """计算VaR"""
        return np.percentile(returns, (1 - confidence) * 100)
    
    def calculate_es(self, returns, confidence=0.95):
        """计算ES（CVaR）"""
        var = self.calculate_var(returns, confidence)
        return returns[returns <= var].mean()
    
    def calculate_garch_volatility(self, returns):
        """计算GARCH波动率"""
        # 使用arch库实现GARCH模型
        from arch import arch_model
        model = arch_model(returns, vol='Garch', p=1, q=1)
        result = model.fit(disp='off')
        return result.conditional_volatility
```

### 优先级P1（用户体验优化）

#### 5. 用户系统
- 实现用户注册/登录
- 个性化盯盘股设置
- 用户偏好存储

#### 6. 实时更新优化
- 使用WebSocket实现实时数据推送
- 优化前端数据刷新机制
- 添加加载状态和错误处理

#### 7. 图表可视化增强
- 添加K线图
- 添加风险指标趋势图
- 实现交互式图表

### 优先级P2（高级功能）

#### 8. 预警系统
- 邮件预警功能
- 价格阈值监控
- 舆情关键词监控

#### 9. 数据导出
- CSV格式导出
- PDF报告生成
- 历史数据查询

#### 10. 移动端适配
- 响应式设计优化
- PWA支持
- 移动端专属功能

## 开发规范

### 代码风格
- Python: 遵循PEP 8
- TypeScript: 使用ESLint配置
- 组件命名: PascalCase
- 函数命名: camelCase

### Git提交规范
```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 重构
test: 测试相关
chore: 构建/工具链相关
```

### 测试要求
- 单元测试覆盖率 > 70%
- 关键业务逻辑必须有测试
- API接口需要集成测试

## 性能优化建议

1. **前端优化**
   - 使用React.memo减少不必要的重渲染
   - 实现虚拟滚动处理大量数据
   - 使用懒加载优化首屏加载

2. **后端优化**
   - 实现Redis缓存热点数据
   - 使用异步任务处理耗时操作
   - 数据库查询优化和索引

3. **API优化**
   - 实现请求限流
   - 批量请求合并
   - 响应数据压缩

## 部署建议

### 开发环境
- 使用Docker Compose一键启动
- 配置热重载

### 生产环境
- 前端: Vercel / Netlify
- 后端: AWS EC2 / Google Cloud Run
- 数据库: PostgreSQL
- 缓存: Redis
- CDN: Cloudflare

## 常见问题

### Q: API调用频率限制怎么办？
A: 实现本地缓存，合理设置更新频率，考虑升级到付费API。

### Q: 如何处理大量历史数据？
A: 使用时序数据库（如InfluxDB），实现数据分片和归档。

### Q: 风险模型计算太慢？
A: 使用NumPy向量化计算，考虑使用Numba加速，或迁移到C++实现核心算法。

## 联系方式

如有问题，请提交Issue或联系开发团队。
