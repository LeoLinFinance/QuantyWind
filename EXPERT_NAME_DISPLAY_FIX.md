# 专家名称显示修复

## 问题描述

在智者论坛的对话框中，专家的回复没有显示专家的名称，只显示"专家"这个通用标签。

## 问题原因

前后端字段命名不一致导致的数据映射问题：

1. **后端返回的字段名**：`expert_type`（Python下划线命名风格）
2. **前端期望的字段名**：`expertType`（JavaScript驼峰命名风格）

当前端直接使用后端返回的数据时，`message.expertType` 为 `undefined`，导致 `getRoleLabel` 函数返回默认值"专家"。

## 解决方案

在前端接收后端数据时，进行字段名转换，将 `expert_type` 转换为 `expertType`。

### 修改的位置

**文件**：`src/pages/ExpertForumPage.tsx`

#### 1. 加载历史消息时转换

```typescript
// 加载对话历史
const historyResponse = await fetch('http://localhost:8000/api/expert-forum/messages')
if (historyResponse.ok) {
  const data = await historyResponse.json()
  if (data.messages && data.messages.length > 0) {
    // 转换字段名：expert_type -> expertType
    const convertedMessages = data.messages.map((msg: any) => ({
      ...msg,
      expertType: msg.expert_type,
      expert_type: undefined
    }))
    setMessages(convertedMessages)
  }
}
```

#### 2. 发送用户消息后转换

```typescript
if (response.ok) {
  const message = await response.json()
  // 转换字段名：expert_type -> expertType
  const convertedMessage = {
    ...message,
    expertType: message.expert_type,
    expert_type: undefined
  }
  setMessages(prev => [...prev, convertedMessage])
  setUserInput('')
}
```

## 显示逻辑

`getRoleLabel` 函数已经正确实现了专家名称的显示逻辑：

```typescript
const getRoleLabel = (message: Message) => {
  if (message.role === 'kimi') return 'KimiClaw资讯'
  if (message.role === 'expert') return message.expertType || '专家'
  if (message.role === 'system') return '系统'
  return '用户'
}
```

当 `message.expertType` 有值时，会显示具体的专家名称（如"选股分析师"、"产业链分析师"等），否则显示默认的"专家"。

## 效果

修复后，对话框中的专家消息会显示具体的专家名称：

- ✅ **选股分析师** - 根据产业链状况、行业政策...
- ✅ **产业链分析师** - 通过目前已有股票的情况...
- ✅ **市场分析师** - 根据目前持有股票短期的技术面...
- ✅ **长期价值投资分析师** - 根据持有股票长期的产业情况...
- ✅ **首席经济学家** - 主要研究目前的全球各地区经济形势...

## 其他说明

### 为什么不修改后端？

虽然也可以修改后端返回驼峰命名的字段，但是：

1. Python 社区的标准是使用下划线命名
2. 后端的数据模型和数据库字段通常使用下划线命名
3. 在前端进行转换更符合各自语言的最佳实践

### 未来改进

可以考虑：

1. 创建一个统一的数据转换工具函数
2. 使用 TypeScript 的类型守卫确保数据格式正确
3. 在 API 层面统一处理字段名转换

## 测试建议

1. 启动应用后，打开智者论坛
2. 开启"接收资讯"和"开始讨论"
3. 等待专家回复
4. 检查每个专家的消息是否显示了正确的专家名称
5. 刷新页面，检查历史消息是否正确显示专家名称
