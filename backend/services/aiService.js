const axios = require('axios')

class AIService {
  constructor() {
    this.provider = process.env.AI_PROVIDER || 'kimi'
    this.kimiKey = process.env.KIMI_API_KEY
    this.stepfunKey = process.env.STEPFUN_API_KEY
  }

  async generateContent(rawContent, category) {
    const categoryContext = this.getCategoryContext(category)
    
    const prompt = `
你是一位专业的技术内容编辑，请将以下原始内容转化为四层结构的深度解析。

${categoryContext}

原始内容：
${rawContent}

分类：${category}

请按以下结构生成内容（所有内容必须用中文，专业术语可以括号标注英文）：

1. 概念层（200-400字）：用通俗易懂的语言解释核心概念，让非专业人士也能理解
2. 原理层（2000-4000字）：深入讲解技术原理、工作机制、理论基础，包含数学模型或生物机制
3. 实现层（3000-6000字）：提供详细的技术实现、算法流程、代码示例或实验方法
4. 应用层（2000-3000字）：分析行业应用场景、实际案例、市场前景和未来发展

内容要求：
- 必须包含具体的数据、图表描述、对比分析
- 原理层要有数学公式或生物机制的详细说明
- 实现层要有伪代码或算法流程
- 应用层要有真实案例和市场分析
- 总字数不少于8000字

请以JSON格式返回：
{
  "title": "文章标题（中文）",
  "summary": "文章摘要（200-300字）",
  "layers": [
    {"level": "concept", "content": "概念层内容（使用markdown格式，包含标题、段落）"},
    {"level": "principle", "content": "原理层内容（使用markdown格式，包含公式、表格）"},
    {"level": "implementation", "content": "实现层内容（使用markdown格式，包含代码块）"},
    {"level": "application", "content": "应用层内容（使用markdown格式，包含案例分析）"}
  ],
  "tags": ["标签1", "标签2", "标签3"]
}
    `

    return await this.callAI(prompt)
  }

  getCategoryContext(category) {
    const contexts = {
      'world-model': '这是关于AI世界模型的内容。世界模型是AI系统理解和预测环境的核心能力，涉及表征学习、因果推理、时空建模等。请重点关注模型架构、训练方法、应用场景。',
      'embodied': '这是关于具身智能的内容。具身智能强调AI与物理世界的交互，包括机器人控制、感知-行动循环、多模态学习。请重点关注硬件集成、控制算法、实际部署。',
      'bci': '这是关于脑机接口的内容。脑机接口连接大脑与外部设备，涉及神经信号采集、解码算法、应用场景。请重点关注信号处理、机器学习方法、医疗应用。',
      'chip': '这是关于芯片架构的内容。芯片架构决定计算性能和能效，涉及处理器设计、存储层次、互连网络。请重点关注架构创新、性能优化、制造工艺。',
      'biotech': '这是关于生物医疗的内容。生物医疗结合生物学和技术创新，涉及基因编辑、药物研发、精准医疗。请重点关注技术原理、临床应用、市场前景和监管挑战。'
    }
    return contexts[category] || '这是前沿技术内容，请深入分析其技术原理和应用价值。'
  }

  async generateAIResponse(context, history = []) {
    const messages = [
      { role: 'system', content: '你是一位专业的AI技术助手，帮助用户理解复杂的技术概念。' },
      ...history,
      { role: 'user', content: context }
    ]

    return await this.callAI(messages)
  }

  async callAI(prompt) {
    try {
      if (this.provider === 'kimi') {
        return await this.callKimi(prompt)
      } else if (this.provider === 'stepfun') {
        return await this.callStepFun(prompt)
      }
    } catch (error) {
      console.error('AI调用失败:', error.response?.data || error.message)
      throw new Error('AI服务暂时不可用: ' + (error.response?.data?.error?.message || error.message))
    }
  }

  async callKimi(prompt) {
    const response = await axios.post(
      'https://api.moonshot.cn/v1/chat/completions',
      {
        model: 'moonshot-v1-32k',
        messages: typeof prompt === 'string' 
          ? [{ role: 'user', content: prompt }]
          : prompt,
        temperature: 0.7
      },
      {
        headers: {
          'Authorization': `Bearer ${this.kimiKey}`,
          'Content-Type': 'application/json'
        }
      }
    )
    
    return response.data.choices[0].message.content
  }

  async callStepFun(prompt) {
    const response = await axios.post(
      'https://api.stepfun.com/v1/chat/completions',
      {
        model: 'step-1-32k',
        messages: typeof prompt === 'string'
          ? [{ role: 'user', content: prompt }]
          : prompt,
        temperature: 0.7
      },
      {
        headers: {
          'Authorization': `Bearer ${this.stepfunKey}`,
          'Content-Type': 'application/json'
        }
      }
    )
    
    return response.data.choices[0].message.content
  }
}

module.exports = new AIService()
