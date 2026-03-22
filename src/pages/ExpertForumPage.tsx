import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'

// 简单的Switch组件实现
interface SwitchProps {
  checked: boolean
  onChange: (checked: boolean) => void
  className?: string
  children?: React.ReactNode
}

function Switch({ checked, onChange, className, children }: SwitchProps) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className={className}
    >
      {children}
    </button>
  )
}

interface Message {
  id: string
  role: 'system' | 'kimi' | 'expert' | 'user'
  expertType?: string
  content: string
  timestamp: string
  intent?: string
}

interface ExpertConfig {
  id: string
  name: string
  prompt: string
  model?: string  // 添加可选的模型字段
}

// 可用的模型选项
const AVAILABLE_MODELS = [
  { value: 'step-1-8k', label: 'Step-1-8k (快速，8k上下文)', description: '适合简单快速的分析' },
  { value: 'step-1-32k', label: 'Step-1-32k (标准，32k上下文)', description: '适合一般对话' },
  { value: 'step-1-256k', label: 'Step-1-256k (超长，256k上下文)', description: '适合长对话和深度分析' },
  { value: 'step-3.5-flash', label: 'Step-3.5-Flash (极速)', description: '最快响应速度' },
  { value: 'step-3', label: 'Step-3 (高级)', description: '更强的推理能力' },
  { value: 'step-r1-v-mini', label: 'Step-R1-V-Mini (推理)', description: '专注于逻辑推理' }
]

const DEFAULT_EXPERT_PROMPTS: ExpertConfig[] = [
  {
    id: 'stock_analyst',
    name: '选股分析师',
    prompt: '你是一位资深选股分析师，专注于投前分析。根据产业链状况、行业政策与前景、股票标的的近期表现以及财报等，综合推荐5-10只美股和港股。请提供具体的股票代码、推荐理由和风险提示。',
    model: 'step-1-256k'  // 默认使用256k模型
  },
  {
    id: 'industry_analyst',
    name: '产业链分析师',
    prompt: '你是一位产业链分析专家，专注于投中分析。通过目前已有股票的情况，根据行业政策、产业链拆解（如从新能源汽车拆到矿物，从服务运营模式到各个产品服务的表现），分析产业成本和利润的占比，和目前股票市场中这些产业的涨跌情况，并综合公司业绩分析股票目前合理的公允价格区间，以及买入和卖出的建议。',
    model: 'step-1-256k'
  },
  {
    id: 'market_analyst',
    name: '市场分析师',
    prompt: '你是一位短期价格投资分析师，专注于投后管理。根据目前持有股票短期的技术面和价格震荡判断是否需要做适当的减仓或者清仓以规避短期风险。请提供具体的技术指标分析和操作建议。',
    model: 'step-1-256k'
  },
  {
    id: 'value_investor',
    name: '长期价值投资分析师',
    prompt: '你是一位长期价值投资专家，专注于投后管理。根据持有股票长期的产业情况和长期方向做研判，提供长期持有的建议和支持。请关注企业的护城河、竞争优势和长期增长潜力。',
    model: 'step-1-256k'
  },
  {
    id: 'chief_economist',
    name: '首席经济学家',
    prompt: '你是一位首席经济学家（投资总监），拥有经济学博士学位。主要研究目前的全球各地区经济形势，收集其他分析师的建议，并根据各个角色提供的建议在适当的情况下进行指导和纠偏。请提供宏观经济视角的投资指导。',
    model: 'step-1-256k'
  }
]

export default function ExpertForumPage() {
  const navigate = useNavigate()
  
  // 从sessionStorage加载缓存的消息（如果有）
  const getCachedMessages = () => {
    try {
      const cached = sessionStorage.getItem('expertForumMessages')
      if (cached) {
        return JSON.parse(cached)
      }
    } catch (error) {
      console.error('加载缓存消息失败:', error)
    }
    return []
  }
  
  const [newsEnabled, setNewsEnabled] = useState(false)
  const [discussionEnabled, setDiscussionEnabled] = useState(false)
  const [messages, setMessages] = useState<Message[]>(getCachedMessages())  // 使用缓存初始化
  const [expertConfigs, setExpertConfigs] = useState<ExpertConfig[]>(DEFAULT_EXPERT_PROMPTS)
  const [showConfigModal, setShowConfigModal] = useState(false)
  const [editingExpert, setEditingExpert] = useState<ExpertConfig | null>(null)
  const [summaryPrompt, setSummaryPrompt] = useState('')
  const [showSummaryPromptModal, setShowSummaryPromptModal] = useState(false)
  const [editingSummaryPrompt, setEditingSummaryPrompt] = useState('')
  const [lastNewsTime, setLastNewsTime] = useState<string>('')
  const [lastExpertCallTime, setLastExpertCallTime] = useState<number>(0)
  const [lastStockAnalystCallTime, setLastStockAnalystCallTime] = useState<number>(0)
  const [userInput, setUserInput] = useState('')
  const [chatStats, setChatStats] = useState({ message_count: 0, has_summary: false })
  const [requestingExpert, setRequestingExpert] = useState<string | null>(null)  // 跟踪正在请求的专家
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  // 当消息更新时，保存到sessionStorage
  useEffect(() => {
    if (messages.length > 0) {
      try {
        sessionStorage.setItem('expertForumMessages', JSON.stringify(messages))
      } catch (error) {
        console.error('保存消息到缓存失败:', error)
      }
    }
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // 加载保存的专家配置和总结提示词
  useEffect(() => {
    const loadConfigs = async () => {
      try {
        // 加载专家配置
        const configResponse = await fetch('http://localhost:8000/api/expert-forum/configs')
        if (configResponse.ok) {
          const configs = await configResponse.json()
          if (configs.length > 0) {
            setExpertConfigs(configs)
          } else {
            // 如果后端没有配置，保存默认配置
            console.log('后端无配置，保存默认专家配置...')
            for (const expert of DEFAULT_EXPERT_PROMPTS) {
              await fetch('http://localhost:8000/api/expert-forum/configs', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(expert)
              })
            }
            console.log('默认专家配置已保存')
          }
        }
        
        // 加载总结提示词
        const promptResponse = await fetch('http://localhost:8000/api/expert-forum/summary-prompt')
        if (promptResponse.ok) {
          const data = await promptResponse.json()
          setSummaryPrompt(data.prompt)
        }
        
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
        
        // 加载聊天统计
        const statsResponse = await fetch('http://localhost:8000/api/expert-forum/chat-stats')
        if (statsResponse.ok) {
          const stats = await statsResponse.json()
          setChatStats(stats)
        }
      } catch (error) {
        console.error('加载配置失败:', error)
      }
    }
    loadConfigs()
  }, [])

  // 处理新闻开关
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null
    
    if (newsEnabled) {
      // 立即获取一次新闻
      fetchNews()
      
      // 每小时获取一次
      interval = setInterval(() => {
        fetchNews()
      }, 60 * 60 * 1000)
    } else {
      // 关闭时通知KimiClaw
      if (lastNewsTime) {
        notifyKimiStop()
      }
    }
    
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [newsEnabled])

  const fetchNews = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/expert-forum/news', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ last_time: lastNewsTime })
      })
      
      if (response.ok) {
        const data = await response.json()
        const newMessage: Message = {
          id: `kimi-${Date.now()}`,
          role: 'kimi',
          content: data.content,
          timestamp: new Date().toISOString()
        }
        setMessages(prev => [...prev, newMessage])
        setLastNewsTime(new Date().toISOString())
      }
    } catch (error) {
      console.error('获取新闻失败:', error)
    }
  }

  const notifyKimiStop = async () => {
    try {
      await fetch('http://localhost:8000/api/expert-forum/news/stop', {
        method: 'POST'
      })
      const stopMessage: Message = {
        id: `system-${Date.now()}`,
        role: 'system',
        content: 'KimiClaw已停止资讯推送',
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, stopMessage])
    } catch (error) {
      console.error('通知KimiClaw停止失败:', error)
    }
  }

  // 处理专家讨论开关
  const handleDiscussionToggle = async (enabled: boolean) => {
    setDiscussionEnabled(enabled)
    
    if (enabled) {
      // 检查调用频率限制
      const now = Date.now()
      const tenMinutes = 10 * 60 * 1000
      
      if (now - lastExpertCallTime < tenMinutes) {
        const waitTime = Math.ceil((tenMinutes - (now - lastExpertCallTime)) / 1000 / 60)
        alert(`请等待${waitTime}分钟后再次调用专家讨论`)
        setDiscussionEnabled(false)
        return
      }
      
      // 开始专家讨论
      await startExpertDiscussion()
      setLastExpertCallTime(now)
    }
  }

  const startExpertDiscussion = async () => {
    const systemMessage: Message = {
      id: `system-${Date.now()}`,
      role: 'system',
      content: '专家讨论开始...',
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, systemMessage])

    // 获取最后一次资讯总结的内容
    let lastNewsSummary = ''
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages[i].role === 'kimi') {
        lastNewsSummary = messages[i].content
        break
      }
    }
    
    // 如果没有资讯，提示用户
    if (!lastNewsSummary) {
      const warningMessage: Message = {
        id: `system-${Date.now()}-warning`,
        role: 'system',
        content: '提示：建议先开启"接收资讯"获取最新市场动态，专家分析将更加准确。',
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, warningMessage])
    }
    
    // 构建上下文（只包含最后一次资讯）
    const context = lastNewsSummary ? `[kimi] ${lastNewsSummary}` : '暂无最新资讯'
    
    // 依次调用每个专家
    for (const expert of expertConfigs) {
      // 选股分析师每天只调用一次
      if (expert.id === 'stock_analyst') {
        const now = Date.now()
        const oneDay = 24 * 60 * 60 * 1000
        if (now - lastStockAnalystCallTime < oneDay) {
          continue
        }
        setLastStockAnalystCallTime(now)
      }
      
      try {
        const response = await fetch('http://localhost:8000/api/expert-forum/expert-analysis', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            expert_id: expert.id,
            expert_name: expert.name,
            expert_prompt: expert.prompt,
            context: context,
            model: expert.model  // 传递模型参数
          })
        })
        
        if (response.ok) {
          const data = await response.json()
          
          // 检查专家是否选择不回复
          if (data.skipped) {
            console.log(`${expert.name}选择不回复此次讨论`)
          } else {
            // 只有当专家选择回复时，才添加消息
            const expertMessage: Message = {
              id: `expert-${expert.id}-${Date.now()}`,
              role: 'expert',
              expertType: expert.name,
              content: data.analysis,
              timestamp: new Date().toISOString()
            }
            setMessages(prev => [...prev, expertMessage])
          }
          
          // 添加延迟避免API限流
          await new Promise(resolve => setTimeout(resolve, 2000))
        }
      } catch (error) {
        console.error(`${expert.name}分析失败:`, error)
      }
    }
    
    const completeMessage: Message = {
      id: `system-${Date.now()}`,
      role: 'system',
      content: '专家讨论完成',
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, completeMessage])
  }

  // 调用单个专家进行分析
  const requestSingleExpert = async (expertId: string) => {
    // 查找专家配置
    const expert = expertConfigs.find(e => e.id === expertId)
    if (!expert) {
      console.error(`未找到专家: ${expertId}`)
      return
    }

    // 设置正在请求的专家
    setRequestingExpert(expertId)

    try {
      // 获取最后一次资讯总结的内容
      let lastNewsSummary = ''
      for (let i = messages.length - 1; i >= 0; i--) {
        if (messages[i].role === 'kimi') {
          lastNewsSummary = messages[i].content
          break
        }
      }
      
      // 构建上下文
      const context = lastNewsSummary ? `[kimi] ${lastNewsSummary}` : '暂无最新资讯'
      
      const response = await fetch('http://localhost:8000/api/expert-forum/expert-analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          expert_id: expert.id,
          expert_name: expert.name,
          expert_prompt: expert.prompt,
          context: context,
          model: expert.model  // 传递模型参数
        })
      })
      
      if (!response.ok) {
        // 处理HTTP错误
        const errorText = await response.text()
        console.error(`HTTP错误 ${response.status}:`, errorText)
        throw new Error(`HTTP ${response.status}: ${errorText}`)
      }
      
      const data = await response.json()
      
      // 检查专家是否选择不回复
      if (data.skipped) {
        console.log(`${expert.name}选择不回复此次讨论`)
        const skipMessage: Message = {
          id: `system-${Date.now()}`,
          role: 'system',
          content: `${expert.name}认为当前情况无需回复`,
          timestamp: new Date().toISOString()
        }
        setMessages(prev => [...prev, skipMessage])
      } else {
        // 添加专家回复
        const expertMessage: Message = {
          id: `expert-${expert.id}-${Date.now()}`,
          role: 'expert',
          expertType: expert.name,
          content: data.analysis,
          timestamp: new Date().toISOString()
        }
        setMessages(prev => [...prev, expertMessage])
      }
    } catch (error: any) {
      console.error(`${expert.name}分析失败:`, error)
      const errorMessage: Message = {
        id: `system-${Date.now()}`,
        role: 'system',
        content: `${expert.name}分析失败: ${error.message || '请稍后重试'}`,
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setRequestingExpert(null)
    }
  }

  const saveExpertConfig = async (config: ExpertConfig) => {
    try {
      const response = await fetch('http://localhost:8000/api/expert-forum/configs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      })
      
      if (response.ok) {
        const updatedConfigs = expertConfigs.map(c => 
          c.id === config.id ? config : c
        )
        setExpertConfigs(updatedConfigs)
        setShowConfigModal(false)
        setEditingExpert(null)
      }
    } catch (error) {
      console.error('保存专家配置失败:', error)
      alert('保存失败，请重试')
    }
  }

  const saveSummaryPrompt = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/expert-forum/summary-prompt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: editingSummaryPrompt })
      })
      
      if (response.ok) {
        setSummaryPrompt(editingSummaryPrompt)
        setShowSummaryPromptModal(false)
        alert('资讯总结提示词已保存')
      }
    } catch (error) {
      console.error('保存总结提示词失败:', error)
      alert('保存失败，请重试')
    }
  }
  
  const sendUserMessage = async () => {
    if (!userInput.trim()) return
    
    try {
      const response = await fetch('http://localhost:8000/api/expert-forum/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: userInput })
      })
      
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
        
        // 更新聊天统计
        const statsResponse = await fetch('http://localhost:8000/api/expert-forum/chat-stats')
        if (statsResponse.ok) {
          const stats = await statsResponse.json()
          setChatStats(stats)
        }
      }
    } catch (error) {
      console.error('发送消息失败:', error)
      alert('发送失败，请重试')
    }
  }
  
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendUserMessage()
    }
  }
  
  const resetConversation = async () => {
    if (!confirm('确定要重置对话吗？这将清除所有消息历史。')) {
      return
    }
    
    try {
      const response = await fetch('http://localhost:8000/api/expert-forum/conversation/reset', {
        method: 'POST'
      })
      
      if (response.ok) {
        setMessages([])
        setChatStats({ message_count: 0, has_summary: false })
        // 清除sessionStorage中的缓存
        sessionStorage.removeItem('expertForumMessages')
        alert('对话已重置')
      }
    } catch (error) {
      console.error('重置对话失败:', error)
      alert('重置失败，请重试')
    }
  }

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'kimi': return 'bg-blue-100 border-blue-300'
      case 'expert': return 'bg-green-100 border-green-300'
      case 'user': return 'bg-purple-100 border-purple-300'
      case 'system': return 'bg-gray-100 border-gray-300'
      default: return 'bg-white border-gray-200'
    }
  }

  const getRoleLabel = (message: Message) => {
    if (message.role === 'kimi') return 'KimiClaw资讯'
    if (message.role === 'expert') return message.expertType || '专家'
    if (message.role === 'system') return '系统'
    return '用户'
  }

  const getExpertGuidance = (expertType: string | undefined) => {
    if (!expertType) return null
    
    const guidanceMap: Record<string, { text: string; buttonText: string; route: string }> = {
      '选股分析师': {
        text: '如果有任何看中的股票信息，可以点击下方按钮添加心仪股票，我们会负责帮你盯盘了解动向',
        buttonText: '前往市场盯盘',
        route: '/market-insight'
      },
      '长期价值投资分析师': {
        text: '如果想进一步了解关注股票的风险，可以点击下方按钮用更专业的数据了解你的股票风险',
        buttonText: '查看风险分析',
        route: '/risk-analysis'
      },
      '首席经济学家': {
        text: '如果想了解世界各地区的舆情风险，可以点击下方按钮前往洞察',
        buttonText: '查看舆情地图',
        route: '/sentiment-map'
      }
    }
    
    return guidanceMap[expertType] || null
  }

  return (
    <div className="h-[calc(100vh-12rem)] flex flex-col">
      {/* 控制面板 */}
      <div className="bg-white rounded-lg shadow-sm p-4 mb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h2 className="text-xl font-semibold text-gray-900">智者论坛</h2>
            {chatStats.has_summary && (
              <span className="px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded-full">
                已总结
              </span>
            )}
            <span className="text-sm text-gray-600">
              消息数: {chatStats.message_count}/10
            </span>
          </div>
          
          <div className="flex items-center space-x-8">
            {/* 接收资讯开关 */}
            <div className="flex items-center space-x-3">
              <span className="text-sm font-medium text-gray-700">接收资讯</span>
              <Switch
                checked={newsEnabled}
                onChange={setNewsEnabled}
                className={`${
                  newsEnabled ? 'bg-blue-600' : 'bg-gray-300'
                } relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2`}
              >
                <span
                  className={`${
                    newsEnabled ? 'translate-x-6' : 'translate-x-1'
                  } inline-block h-4 w-4 transform rounded-full bg-white transition-transform`}
                />
              </Switch>
            </div>
            
            {/* 开始讨论开关 */}
            <div className="flex items-center space-x-3">
              <span className="text-sm font-medium text-gray-700">开始讨论</span>
              <Switch
                checked={discussionEnabled}
                onChange={handleDiscussionToggle}
                className={`${
                  discussionEnabled ? 'bg-green-600' : 'bg-gray-300'
                } relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2`}
              >
                <span
                  className={`${
                    discussionEnabled ? 'translate-x-6' : 'translate-x-1'
                  } inline-block h-4 w-4 transform rounded-full bg-white transition-transform`}
                />
              </Switch>
            </div>
            
            {/* 配置专家按钮 */}
            <button
              onClick={() => setShowConfigModal(true)}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              配置专家
            </button>
            
            {/* 配置资讯总结按钮 */}
            <button
              onClick={() => {
                setEditingSummaryPrompt(summaryPrompt)
                setShowSummaryPromptModal(true)
              }}
              className="px-4 py-2 text-sm font-medium text-blue-700 bg-blue-50 border border-blue-300 rounded-md hover:bg-blue-100"
            >
              配置资讯总结
            </button>
            
            {/* 重置对话按钮 */}
            <button
              onClick={resetConversation}
              className="px-4 py-2 text-sm font-medium text-red-700 bg-red-50 border border-red-300 rounded-md hover:bg-red-100"
            >
              重置对话
            </button>
          </div>
        </div>
        
        {/* 专家列表 */}
        <div className="mt-4 flex flex-wrap gap-2">
          {expertConfigs.map(expert => (
            <div
              key={expert.id}
              className="px-3 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded-full"
            >
              {expert.name}
            </div>
          ))}
        </div>
      </div>

      {/* 对话区域 - 使用绝对定位优化布局 */}
      <div className="flex-1 bg-white rounded-lg shadow-sm overflow-hidden relative">
        {/* 历史消息区域 - 占据除底部输入区外的所有空间 */}
        <div className="absolute inset-0 pb-[220px] overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center text-gray-500 mt-8">
              <p className="text-lg">欢迎来到智者论坛</p>
              <p className="text-sm mt-2">打开"接收资讯"获取市场动态，打开"开始讨论"让专家团队为您分析</p>
              <p className="text-sm mt-1">或者在下方输入您的问题和想法</p>
            </div>
          ) : (
            messages.map(message => {
              const guidance = message.role === 'expert' ? getExpertGuidance(message.expertType) : null
              
              return (
                <div
                  key={message.id}
                  className={`p-4 rounded-lg border-2 ${getRoleColor(message.role)}`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-semibold text-gray-900">
                        {getRoleLabel(message)}
                      </span>
                      {message.intent && (
                        <span className="px-2 py-0.5 text-xs bg-gray-200 text-gray-700 rounded">
                          {message.intent}
                        </span>
                      )}
                    </div>
                    <span className="text-xs text-gray-500">
                      {new Date(message.timestamp).toLocaleString('zh-CN')}
                    </span>
                  </div>
                  <div className="text-sm text-gray-800 whitespace-pre-wrap">
                    {message.content}
                  </div>
                  
                  {/* 专家引导按钮 */}
                  {guidance && (
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <p className="text-xs text-gray-600 mb-2">
                        💡 {guidance.text}
                      </p>
                      <button
                        onClick={() => navigate(guidance.route)}
                        className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors"
                      >
                        {guidance.buttonText} →
                      </button>
                    </div>
                  )}
                </div>
              )
            })
          )}
          <div ref={messagesEndRef} />
        </div>
        
        {/* 用户输入区域 - 固定在底部 */}
        <div className="absolute bottom-0 left-0 right-0 border-t bg-gray-50 p-4">
          <div className="flex space-x-2">
            <input
              type="text"
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="输入您的想法或问题... (按Enter发送，Shift+Enter换行)"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={sendUserMessage}
              disabled={!userInput.trim()}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              发送
            </button>
          </div>
          
          {/* 快捷专家咨询按钮 */}
          <div className="mt-3 pt-3 border-t border-gray-200">
            <p className="text-xs text-gray-600 mb-2">快速咨询专家：</p>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => requestSingleExpert('stock_analyst')}
                disabled={requestingExpert === 'stock_analyst'}
                className="px-3 py-1.5 text-sm font-medium text-blue-700 bg-blue-50 border border-blue-300 rounded-md hover:bg-blue-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {requestingExpert === 'stock_analyst' ? '分析中...' : '📊 选股分析'}
              </button>
              <button
                onClick={() => requestSingleExpert('industry_analyst')}
                disabled={requestingExpert === 'industry_analyst'}
                className="px-3 py-1.5 text-sm font-medium text-purple-700 bg-purple-50 border border-purple-300 rounded-md hover:bg-purple-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {requestingExpert === 'industry_analyst' ? '分析中...' : '🔗 产业链分析'}
              </button>
              <button
                onClick={() => requestSingleExpert('market_analyst')}
                disabled={requestingExpert === 'market_analyst'}
                className="px-3 py-1.5 text-sm font-medium text-orange-700 bg-orange-50 border border-orange-300 rounded-md hover:bg-orange-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {requestingExpert === 'market_analyst' ? '分析中...' : '📈 短期市场分析'}
              </button>
              <button
                onClick={() => requestSingleExpert('value_investor')}
                disabled={requestingExpert === 'value_investor'}
                className="px-3 py-1.5 text-sm font-medium text-green-700 bg-green-50 border border-green-300 rounded-md hover:bg-green-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {requestingExpert === 'value_investor' ? '分析中...' : '💎 长期价值投资分析'}
              </button>
              <button
                onClick={() => requestSingleExpert('chief_economist')}
                disabled={requestingExpert === 'chief_economist'}
                className="px-3 py-1.5 text-sm font-medium text-indigo-700 bg-indigo-50 border border-indigo-300 rounded-md hover:bg-indigo-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {requestingExpert === 'chief_economist' ? '分析中...' : '🌍 经济分析'}
              </button>
            </div>
          </div>
          
          <p className="text-xs text-gray-500 mt-2">
            提示：您的消息会被所有专家看到，他们会在下次讨论时考虑您的问题
          </p>
        </div>
      </div>

      {/* 专家配置模态框 */}
      {showConfigModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto p-6">
            <h3 className="text-lg font-semibold mb-4">配置专家提示词</h3>
            
            <div className="space-y-4">
              {expertConfigs.map(expert => (
                <div key={expert.id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-900">{expert.name}</h4>
                    <button
                      onClick={() => setEditingExpert(expert)}
                      className="text-sm text-blue-600 hover:text-blue-800"
                    >
                      编辑
                    </button>
                  </div>
                  {editingExpert?.id === expert.id ? (
                    <div className="space-y-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          模型选择
                        </label>
                        <select
                          value={editingExpert.model || 'step-1-256k'}
                          onChange={(e) => setEditingExpert({ ...editingExpert, model: e.target.value })}
                          className="w-full p-2 border rounded-md text-sm"
                        >
                          {AVAILABLE_MODELS.map(model => (
                            <option key={model.value} value={model.value}>
                              {model.label} - {model.description}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          提示词
                        </label>
                        <textarea
                          value={editingExpert.prompt}
                          onChange={(e) => setEditingExpert({ ...editingExpert, prompt: e.target.value })}
                          className="w-full h-32 p-2 border rounded-md text-sm"
                        />
                      </div>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => saveExpertConfig(editingExpert)}
                          className="px-3 py-1 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700"
                        >
                          保存
                        </button>
                        <button
                          onClick={() => setEditingExpert(null)}
                          className="px-3 py-1 text-sm bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                        >
                          取消
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <p className="text-xs text-gray-500 mb-1">
                        模型: {expert.model || 'step-1-256k'}
                      </p>
                      <p className="text-sm text-gray-600">{expert.prompt}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
            
            <div className="mt-6 flex justify-end">
              <button
                onClick={() => {
                  setShowConfigModal(false)
                  setEditingExpert(null)
                }}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
              >
                关闭
              </button>
            </div>
          </div>
        </div>
      )}
      {/* 资讯总结提示词配置模态框 */}
      {showSummaryPromptModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto p-6">
            <h3 className="text-lg font-semibold mb-4">配置资讯总结提示词</h3>
            
            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-2">
                这个提示词将用于指导AI如何总结新闻资讯。你可以根据自己的需求调整总结的重点和风格。
              </p>
              <textarea
                value={editingSummaryPrompt}
                onChange={(e) => setEditingSummaryPrompt(e.target.value)}
                className="w-full h-64 p-3 border rounded-md text-sm font-mono"
                placeholder="输入资讯总结提示词..."
              />
            </div>
            
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => setShowSummaryPromptModal(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
              >
                取消
              </button>
              <button
                onClick={saveSummaryPrompt}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
              >
                保存
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
