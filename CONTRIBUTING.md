# 贡献指南

感谢您对量数风行项目的关注！我们欢迎各种形式的贡献。

## 如何贡献

### 报告问题

如果您发现了 bug 或有功能建议：

1. 在 [Issues](https://github.com/yourusername/quantywind/issues) 中搜索，确认问题尚未被报告
2. 创建新的 Issue，清晰描述问题或建议
3. 提供必要的信息：
   - 问题描述
   - 复现步骤
   - 预期行为
   - 实际行为
   - 环境信息（操作系统、Python 版本、Node.js 版本等）

### 提交代码

1. Fork 本项目
2. 创建您的特性分支：
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. 提交您的更改：
   ```bash
   git commit -m 'Add some amazing feature'
   ```
4. 推送到分支：
   ```bash
   git push origin feature/amazing-feature
   ```
5. 开启 Pull Request

### 代码规范

#### Python 代码

- 遵循 PEP 8 规范
- 使用类型注解
- 编写文档字符串
- 添加必要的注释

```python
def calculate_risk(portfolio: List[Dict], metrics: Dict) -> float:
    """
    计算投资组合风险
    
    Args:
        portfolio: 投资组合配置
        metrics: 风险指标
    
    Returns:
        风险评分
    """
    pass
```

#### TypeScript/React 代码

- 使用 TypeScript 类型
- 遵循 React Hooks 最佳实践
- 组件使用函数式写法
- 使用有意义的变量名

```typescript
interface PortfolioProps {
  symbols: string[]
  onUpdate: (data: PortfolioData) => void
}

export function Portfolio({ symbols, onUpdate }: PortfolioProps) {
  // 组件实现
}
```

### 提交信息规范

使用清晰的提交信息：

- `feat: 添加新功能`
- `fix: 修复 bug`
- `docs: 更新文档`
- `style: 代码格式调整`
- `refactor: 代码重构`
- `test: 添加测试`
- `chore: 构建/工具链更新`

### 测试

- 为新功能添加测试
- 确保所有测试通过：
  ```bash
  # 后端测试
  pytest
  
  # 前端测试
  npm test
  ```

### 文档

- 更新相关文档
- 为新功能添加使用说明
- 保持 README 和 API 文档同步

## 开发环境设置

### 后端开发

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖
```

### 前端开发

```bash
npm install
npm run dev
```

### 代码检查

```bash
# Python 代码检查
flake8 backend/
mypy backend/

# TypeScript 代码检查
npm run lint
```

## 行为准则

- 尊重所有贡献者
- 保持友好和专业
- 接受建设性的批评
- 关注对项目最有利的事情

## 许可证

通过贡献代码，您同意您的贡献将在 MIT 许可证下发布。

## 问题？

如有任何问题，欢迎：
- 在 Issues 中提问
- 发送邮件至 your.email@example.com

感谢您的贡献！🎉
