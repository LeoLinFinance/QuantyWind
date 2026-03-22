# 市场风险舆情地图 - 功能增强完成报告

## 完成时间
2026年3月10日

## 新增功能概览

### 1. 地图标记详细信息展示 ✅

**功能描述**：
- 点击地图上的风险标记，弹出详细信息窗口
- 显示完整的风险分析内容

**展示内容**：
- 风险等级标签（高/中/低）
- 事件摘要（50字以内）
- 风险详情（100-200字详细描述）
- 受影响产业列表
- 国家/地区信息
- 事件时间
- 相关股票代码
- 新闻来源链接

**交互方式**：
- 点击地图标记打开详情弹窗
- 点击弹窗外部或关闭按钮关闭
- 点击"查看新闻来源"跳转到原始新闻

**技术实现**：
- 前端：React状态管理 + 模态窗口
- 后端：AI分析时提取`risk_details`和`affected_industries`字段
- 数据结构：
  ```typescript
  {
    summary: string           // 简短摘要
    riskDetails: string       // 详细风险描述
    affectedIndustries: []    // 受影响产业
    relatedStocks: []         // 相关股票
    country: string           // 国家
    timestamp: string         // 时间
    url: string              // 新闻链接
  }
  ```

### 2. 自定义System Prompt编辑 ✅

**功能描述**：
- 用户可以自定义AI分析的system prompt
- 类似市场洞察页面的编辑功能
- 支持恢复默认提示词

**使用方式**：
1. 点击"编辑提示词"按钮
2. 在文本框中编辑提示词
3. 点击"应用并刷新"使用新提示词重新分析
4. 点击"恢复默认"回到默认提示词

**应用场景**：
- 调整风险评估标准（更保守/更激进）
- 关注特定行业或地区
- 自定义分析角度和重点
- 调整风险等级分布比例

**技术实现**：
- 前端：`customPrompt`状态管理
- 后端：`get_map_data(custom_prompt)`参数传递
- 缓存：不同prompt使用不同缓存key
- API：`GET /api/sentiment-map?custom_prompt=xxx`

**默认提示词**：
```
你是一个专业的金融风险分析师...
（包含完整的风险等级定义、地理位置判断规则等）
```

### 3. 产业链洞察功能 ✅

**功能描述**：
- 替换原"不确定地区舆情"栏目
- 基于盯盘股票分析产业链动态
- 提供1-3个深度洞见判断

**洞见内容**：
1. 细分市场动态分析
2. 产业链上下游影响
3. 国际/国内形势研判

**展示信息**：
- 洞见标题（不超过30字）
- 详细分析内容（100-200字）
- 相关股票代码
- 情绪标签（积极/中性/消极）

**数据来源**：
- 从市场洞察页面获取盯盘股票列表
- 获取这些股票的最新新闻（每只3条）
- AI综合分析产业链动态

**技术实现**：
- API端点：`POST /api/industry-insights`
- 请求体：`["AAPL", "MSFT", "NVDA", ...]`
- 响应：
  ```json
  [
    {
      "title": "AI芯片产业链持续升温",
      "content": "Nvidia等AI芯片厂商...",
      "related_stocks": ["NVDA", "AMD"],
      "sentiment": "positive"
    }
  ]
  ```

**颜色标识**：
- 积极：绿色边框 + 绿色标签
- 中性：灰色边框 + 灰色标签
- 消极：红色边框 + 红色标签

## 技术架构更新

### 后端服务 (sentiment_service.py)

**新增方法**：
```python
1. get_map_data(custom_prompt: Optional[str] = None)
   - 支持自定义prompt参数
   - 不同prompt使用不同缓存

2. get_industry_insights(watchlist_symbols: List[str])
   - 获取盯盘股票新闻
   - AI分析产业链动态
   - 返回1-3个洞见

3. default_system_prompt (类属性)
   - 存储默认提示词
   - 供前端获取和恢复使用
```

**数据结构增强**：
```python
event = {
    'id': str,
    'summary': str,              # 原有
    'riskDetails': str,          # 新增：详细风险描述
    'affectedIndustries': [],    # 新增：受影响产业
    'timestamp': str,            # 原有
    'riskLevel': str,            # 原有
    'relatedStocks': [],         # 原有
    'country': str,              # 原有
    'coordinates': [],           # 原有
    'source': str,               # 原有
    'url': str                   # 原有
}
```

### API路由 (sentiment.py)

**新增端点**：
```python
1. GET /api/sentiment-map?custom_prompt=xxx
   - 获取舆情地图数据
   - 支持自定义prompt参数

2. GET /api/sentiment-map/default-prompt
   - 获取默认system prompt
   - 用于前端显示和恢复

3. POST /api/industry-insights
   - 请求体：股票代码列表
   - 返回：产业链洞见列表
```

### 前端页面 (SentimentMapPage.tsx)

**新增状态**：
```typescript
const [selectedEvent, setSelectedEvent] = useState<SentimentEvent | null>(null)
const [showPromptEditor, setShowPromptEditor] = useState(false)
const [customPrompt, setCustomPrompt] = useState('')
const [defaultPrompt, setDefaultPrompt] = useState('')
const [industryInsights, setIndustryInsights] = useState<IndustryInsight[]>([])
```

**新增组件**：
1. System Prompt编辑器（可折叠）
2. 事件详情弹窗（模态窗口）
3. 产业链洞察卡片列表

**交互优化**：
- 地图标记可点击
- 详情弹窗支持点击外部关闭
- 提示词编辑器支持展开/收起
- 产业链洞察支持情绪颜色标识

## 用户体验提升

### 1. 信息深度
- 从简单摘要 → 详细风险分析
- 从单一维度 → 多维度信息（产业、股票、地区）
- 从静态展示 → 交互式探索

### 2. 个性化
- 可自定义AI分析角度
- 可调整风险评估标准
- 可关注特定行业/地区

### 3. 实用性
- 产业链洞察直接关联盯盘股票
- 提供可操作的投资参考
- 形势研判帮助决策

### 4. 视觉优化
- 详情弹窗清晰展示完整信息
- 产业标签和股票代码醒目
- 情绪颜色标识直观

## 测试验证

### 功能测试
```bash
python3 test_new_features.py
```

**测试项目**：
1. ✅ 风险事件详细信息提取
2. ✅ 产业链洞察生成
3. ✅ 自定义System Prompt支持
4. ✅ API端点正常响应
5. ✅ 前端交互流畅

### 数据质量
- 风险详情：100-200字详细描述
- 受影响产业：准确识别相关行业
- 产业链洞见：1-3个深度判断
- 情绪分析：positive/neutral/negative

## 使用示例

### 场景1：查看高风险事件详情
1. 在地图上筛选"高风险"
2. 点击红色标记
3. 查看详细风险描述和受影响产业
4. 点击相关股票代码查看影响
5. 点击新闻链接了解详情

### 场景2：自定义风险分析角度
1. 点击"编辑提示词"
2. 修改为："你是一个关注科技行业的分析师，特别关注AI和半导体领域的风险"
3. 点击"应用并刷新"
4. 查看针对科技行业的风险分析结果

### 场景3：查看产业链洞察
1. 在市场洞察页面添加关注的股票
2. 切换到舆情地图页面
3. 滚动到"产业链洞察"栏目
4. 查看基于盯盘股票的产业链分析
5. 根据洞见调整投资策略

## 性能优化

1. **缓存策略**：
   - 不同prompt使用独立缓存
   - 1小时缓存有效期
   - 避免重复AI调用

2. **数据限制**：
   - 产业链洞察限制5只股票
   - 每只股票获取3条新闻
   - 最多分析10条新闻

3. **错误处理**：
   - 新闻获取失败返回默认洞见
   - AI解析失败使用备用内容
   - 网络错误友好提示

## 下一步优化建议

1. **历史对比**：保存历史洞见，对比产业链变化趋势
2. **预警系统**：产业链出现重大变化时推送通知
3. **关联分析**：分析风险事件对特定产业链的影响路径
4. **数据导出**：支持导出产业链洞察报告
5. **多模型对比**：使用不同AI模型生成洞见，对比分析

## 相关文件

### 新增文件
- `test_new_features.py` - 新功能测试脚本
- `SENTIMENT_MAP_ENHANCED.md` - 本文档

### 修改文件
- `backend/services/sentiment_service.py` - 核心服务增强
- `backend/routers/sentiment.py` - API路由扩展
- `src/pages/SentimentMapPage.tsx` - 前端页面重构

## 总结

本次更新显著提升了市场风险舆情地图的功能深度和用户体验：

1. **信息更丰富**：从简单摘要扩展到详细风险分析和产业影响
2. **交互更友好**：点击查看详情，自定义分析角度
3. **实用性更强**：产业链洞察直接关联投资决策
4. **个性化更高**：支持自定义AI分析提示词

所有功能已完成开发和测试，代码质量良好，无TypeScript错误，性能表现优秀。
