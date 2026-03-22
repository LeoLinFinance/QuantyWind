# 数据持久化功能说明

## 问题描述

之前每次后端重启时，以下数据都会丢失：
- 个股盯盘列表
- 自定义的AI系统提示词
- 用户设置

这导致在开发调试或技术迭代时，需要重复添加股票和配置，影响开发效率。

## 解决方案

实现了一个持久化存储服务，将关键数据保存到本地JSON文件中。

### 持久化的数据

1. **盯盘股票列表** (`data/config/watchlist.json`)
   - 保存所有添加到盯盘的股票代码
   - 添加/删除股票时自动保存
   - 后端启动时自动加载

2. **系统提示词** (`data/config/system_prompt.json`)
   - 保存用户自定义的AI分析提示词
   - 修改提示词时自动保存
   - 后端启动时自动加载

3. **用户设置** (`data/config/user_settings.json`)
   - 保存用户的个性化设置
   - 可扩展用于保存主题、语言等配置

## 技术实现

### 1. 持久化服务 (`backend/services/persistence_service.py`)

```python
class PersistenceService:
    def save_watchlist(symbols: List[str]) -> bool
    def load_watchlist() -> List[str]
    def add_to_watchlist(symbol: str) -> bool
    def remove_from_watchlist(symbol: str) -> bool
    
    def save_system_prompt(prompt: str) -> bool
    def load_system_prompt() -> Optional[str]
    
    def save_user_settings(settings: Dict) -> bool
    def load_user_settings() -> Dict
    def update_user_setting(key: str, value) -> bool
    
    def get_all_data_info() -> Dict
    def clear_all_data() -> bool
```

### 2. MarketService集成

MarketService在初始化时自动加载持久化数据：

```python
class MarketService:
    def __init__(self):
        self.persistence = PersistenceService()
        
        # 加载盯盘列表
        saved_watchlist = self.persistence.load_watchlist()
        if saved_watchlist:
            self.watchlist_symbols = saved_watchlist
        else:
            # 使用默认列表并保存
            self.watchlist_symbols = ['AAPL', 'MSFT', ...]
            self.persistence.save_watchlist(self.watchlist_symbols)
        
        # 加载系统提示词
        self.system_prompt = self.persistence.load_system_prompt()
```

### 3. 自动保存

在以下操作时自动保存到持久化存储：
- 添加股票到盯盘列表
- 从盯盘列表移除股票
- 更新系统提示词

## 数据文件位置

```
backend/
  data/
    config/
      watchlist.json          # 盯盘列表
      system_prompt.json      # 系统提示词
      user_settings.json      # 用户设置
    historical/
      market_data.json        # 历史数据（已有）
```

## 数据格式

### watchlist.json
```json
{
  "symbols": ["AAPL", "MSFT", "TSLA", "GOOGL"],
  "updated_at": "2026-03-10T15:30:00",
  "count": 4
}
```

### system_prompt.json
```json
{
  "prompt": "你是一个专业的美股市场分析师...",
  "updated_at": "2026-03-10T15:30:00"
}
```

### user_settings.json
```json
{
  "settings": {
    "theme": "dark",
    "language": "zh-CN",
    "auto_refresh": true
  },
  "updated_at": "2026-03-10T15:30:00"
}
```

## API端点

新增了持久化数据管理API：

```bash
# 获取所有持久化数据信息
GET /api/persistence/info

# 获取盯盘列表
GET /api/persistence/watchlist

# 获取系统提示词
GET /api/persistence/system-prompt

# 获取用户设置
GET /api/persistence/user-settings

# 清除所有持久化数据（慎用）
DELETE /api/persistence/clear-all
```

## 使用示例

### 查看持久化数据信息

```bash
curl http://localhost:8000/api/persistence/info
```

响应：
```json
{
  "success": true,
  "data": {
    "watchlist": {
      "exists": true,
      "count": 4
    },
    "system_prompt": {
      "exists": true,
      "has_content": true
    },
    "user_settings": {
      "exists": true,
      "count": 2
    }
  }
}
```

### 查看盯盘列表

```bash
curl http://localhost:8000/api/persistence/watchlist
```

响应：
```json
{
  "success": true,
  "symbols": ["AAPL", "MSFT", "TSLA", "GOOGL"],
  "count": 4
}
```

## 测试结果

```
✅ 持久化服务初始化成功
✅ 盯盘列表保存/加载成功
✅ 系统提示词保存/加载成功
✅ 用户设置保存/加载成功
✅ MarketService成功加载持久化数据
```

## 工作流程

### 首次启动
1. 后端启动
2. PersistenceService初始化，创建`data/config`目录
3. MarketService尝试加载持久化数据
4. 如果没有保存的数据，使用默认值并保存
5. 用户添加股票或修改提示词时，自动保存

### 后续启动
1. 后端启动
2. PersistenceService初始化
3. MarketService加载持久化数据
4. 恢复上次的盯盘列表和提示词
5. 用户可以继续使用，无需重新配置

## 优势

1. **开发效率提升**：不需要每次重启后重新添加股票
2. **配置持久化**：自定义的提示词和设置得以保留
3. **数据安全**：本地JSON文件，易于备份和迁移
4. **易于扩展**：可以轻松添加更多需要持久化的数据
5. **透明可见**：JSON格式，可以直接查看和编辑

## 注意事项

1. **数据文件位置**：`backend/data/config/`目录
2. **备份建议**：定期备份`data/config`目录
3. **清除数据**：使用`DELETE /api/persistence/clear-all`可以清除所有持久化数据
4. **Git忽略**：建议将`data/config/*.json`添加到`.gitignore`（如果不想提交个人配置）

## 未来扩展

可以考虑持久化的其他数据：
- [ ] 用户的图表配置
- [ ] 自定义的风险阈值
- [ ] 页面布局偏好
- [ ] 最近查看的股票历史
- [ ] AI分析的缓存结果

---

**实现日期**: 2026年3月10日
**状态**: 已完成并测试通过
**影响范围**: 盯盘列表、系统提示词、用户设置
