// 演示服务器 - 使用内存数据库
const express = require('express')
const cors = require('cors')
const bodyParser = require('body-parser')

const app = express()
const PORT = 3000

// 中间件
app.use(cors())
app.use(bodyParser.json())

// 内存数据库
const mockArticles = [
  {
    id: '1',
    title: 'GPT-4 Vision多模态能力深度解析',
    category: 'ai',
    summary: 'OpenAI最新发布的GPT-4 Vision模型，实现了图像理解与文本生成的完美结合，标志着多模态AI进入新阶段。',
    publishTime: '2024-03-08',
    views: 1234,
    likes: 89,
    source: 'GitHub',
    sourceUrl: 'https://github.com/openai/gpt-4-vision',
    hasAudio: true,
    duration: '15:30',
    audioUrl: 'https://example.com/audio1.mp3',
    layers: [
      {
        level: 'concept',
        content: '<h2>什么是GPT-4 Vision？</h2><p>GPT-4 Vision是OpenAI推出的多模态大语言模型，它不仅能理解文本，还能"看懂"图像。简单来说，你可以给它一张图片，它能告诉你图片里有什么，甚至能基于图片内容回答问题、生成代码或创作内容。</p><p>这就像给AI装上了"眼睛"，让它能够像人类一样同时处理视觉和语言信息。</p>'
      },
      {
        level: 'principle',
        content: '<h2>技术原理</h2><p>GPT-4 Vision采用了Transformer架构的扩展版本，通过以下关键技术实现多模态理解：</p><h3>1. 视觉编码器</h3><p>使用Vision Transformer (ViT)将图像分割成patches，每个patch被编码成向量表示。这些视觉token与文本token在同一个语义空间中对齐。</p><h3>2. 跨模态注意力机制</h3><p>模型通过自注意力机制，让图像特征和文本特征能够相互关联。这使得模型能够理解"图中的猫"这样的跨模态概念。</p><h3>3. 统一的预训练目标</h3><p>在大规模图文对数据上进行预训练，学习图像和文本之间的对应关系。训练目标包括图像描述生成、视觉问答等多个任务。</p>'
      },
      {
        level: 'implementation',
        content: '<h2>代码实现示例</h2><pre><code>import openai\nimport base64\n\n# 读取图像并编码\nwith open("image.jpg", "rb") as f:\n    image_data = base64.b64encode(f.read()).decode()\n\n# 调用GPT-4 Vision API\nresponse = openai.ChatCompletion.create(\n    model="gpt-4-vision-preview",\n    messages=[\n        {\n            "role": "user",\n            "content": [\n                {"type": "text", "text": "这张图片里有什么？"},\n                {\n                    "type": "image_url",\n                    "image_url": f"data:image/jpeg;base64,{image_data}"\n                }\n            ]\n        }\n    ],\n    max_tokens=300\n)\n\nprint(response.choices[0].message.content)</code></pre><p>关键实现要点：</p><ul><li>图像需要转换为base64编码或提供URL</li><li>消息格式支持混合文本和图像</li><li>可以进行多轮对话，保持上下文</li></ul>'
      },
      {
        level: 'application',
        content: '<h2>行业应用场景</h2><h3>1. 医疗影像分析</h3><p>辅助医生分析X光片、CT扫描等医学影像，快速识别异常区域，提供初步诊断建议。某三甲医院试点显示，AI辅助可将影像分析效率提升40%。</p><h3>2. 智能客服</h3><p>用户上传产品照片，AI自动识别问题并提供解决方案。某电商平台应用后，客服响应速度提升3倍，用户满意度提高25%。</p><h3>3. 教育辅导</h3><p>学生拍摄题目照片，AI不仅给出答案，还能详细讲解解题步骤。已有超过100万学生使用此功能进行学习。</p><h3>4. 内容创作</h3><p>根据图片自动生成营销文案、社交媒体内容。某MCN机构使用后，内容产出效率提升5倍。</p>'
      }
    ],
    tags: ['GPT-4', '多模态', 'Vision', 'OpenAI']
  },
  {
    id: '2',
    title: '量子纠缠在量子计算中的应用突破',
    category: 'quantum',
    summary: '中科大团队实现了512量子比特的纠缠态制备，为大规模量子计算铺平道路。',
    publishTime: '2024-03-07',
    views: 856,
    likes: 67,
    source: 'arXiv',
    sourceUrl: 'https://arxiv.org/abs/2403.xxxxx',
    hasAudio: true,
    duration: '12:45',
    audioUrl: 'https://example.com/audio2.mp3',
    layers: [
      {
        level: 'concept',
        content: '<h2>量子纠缠是什么？</h2><p>量子纠缠是量子力学中最神奇的现象之一。简单来说，两个粒子一旦发生纠缠，无论相隔多远，测量其中一个粒子的状态，另一个粒子的状态会瞬间确定。</p><p>爱因斯坦称之为"幽灵般的超距作用"，这种现象违背了我们的日常经验，但却是量子计算的核心资源。</p>'
      },
      {
        level: 'principle',
        content: '<h2>量子纠缠的物理原理</h2><p>量子纠缠源于量子态的叠加性和不可分性...</p>'
      },
      {
        level: 'implementation',
        content: '<h2>实验实现</h2><p>制备纠缠态的关键技术...</p>'
      },
      {
        level: 'application',
        content: '<h2>应用前景</h2><p>量子通信、量子计算、量子传感...</p>'
      }
    ],
    tags: ['量子纠缠', '量子计算', '量子比特']
  },
  {
    id: '3',
    title: 'Neuralink脑机接口首次人体试验成功',
    category: 'bci',
    summary: 'Elon Musk的Neuralink公司宣布首位人类受试者成功通过意念控制电脑光标。',
    publishTime: '2024-03-06',
    views: 2341,
    likes: 156,
    source: 'GitHub',
    sourceUrl: 'https://github.com/neuralink',
    hasAudio: false,
    duration: '18:20',
    layers: [
      {
        level: 'concept',
        content: '<h2>脑机接口技术</h2><p>脑机接口(BCI)是在大脑与外部设备之间建立直接通信通道的技术...</p>'
      },
      {
        level: 'principle',
        content: '<h2>工作原理</h2><p>通过植入电极阵列记录神经元活动...</p>'
      },
      {
        level: 'implementation',
        content: '<h2>技术实现</h2><p>N1芯片的设计与植入手术...</p>'
      },
      {
        level: 'application',
        content: '<h2>医疗应用</h2><p>帮助瘫痪患者恢复运动能力...</p>'
      }
    ],
    tags: ['脑机接口', 'Neuralink', 'BCI']
  }
]

// API路由
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date(), mode: 'demo' })
})

app.get('/api/articles', (req, res) => {
  const { category = 'all', page = 1, pageSize = 10 } = req.query
  
  let filtered = category === 'all' 
    ? mockArticles 
    : mockArticles.filter(a => a.category === category)
  
  res.json({ success: true, data: filtered })
})

app.get('/api/articles/:id', (req, res) => {
  const article = mockArticles.find(a => a.id === req.params.id)
  
  if (!article) {
    return res.status(404).json({ success: false, message: '文章不存在' })
  }
  
  res.json({ success: true, data: article })
})

app.get('/api/articles/search', (req, res) => {
  const { keyword } = req.query
  const results = mockArticles.filter(a => 
    a.title.includes(keyword) || a.summary.includes(keyword)
  )
  res.json({ success: true, data: results })
})

app.post('/api/chat', (req, res) => {
  const { message } = req.body
  
  // 模拟AI回复
  const replies = [
    '这是一个很好的问题！根据文章内容，我可以为您详细解释...',
    '让我从技术角度为您分析一下这个问题...',
    '这个概念确实比较复杂，简单来说就是...',
    '您提到的这一点非常关键，在实际应用中...'
  ]
  
  const reply = replies[Math.floor(Math.random() * replies.length)] + 
    `\n\n针对"${message}"这个问题，我建议您重点关注文章中的原理层和应用层内容，那里有更详细的说明。`
  
  setTimeout(() => {
    res.json({ 
      success: true, 
      data: { reply } 
    })
  }, 1000)
})

app.get('/api/admin/stats', (req, res) => {
  res.json({
    success: true,
    data: {
      totalArticles: mockArticles.length,
      totalViews: mockArticles.reduce((sum, a) => sum + a.views, 0),
      totalLikes: mockArticles.reduce((sum, a) => sum + a.likes, 0),
      categoryStats: [
        { _id: 'ai', count: 1 },
        { _id: 'quantum', count: 1 },
        { _id: 'bci', count: 1 }
      ]
    }
  })
})

app.listen(PORT, () => {
  console.log('🎉 ========================================')
  console.log('🚀 滴答学术演示服务器启动成功！')
  console.log('🎉 ========================================')
  console.log('')
  console.log('📍 服务地址: http://localhost:3000')
  console.log('📍 健康检查: http://localhost:3000/health')
  console.log('📍 文章列表: http://localhost:3000/api/articles')
  console.log('')
  console.log('💡 这是演示模式，使用内存数据库')
  console.log('💡 已预置3篇示例文章供测试')
  console.log('')
  console.log('🔧 测试命令:')
  console.log('   curl http://localhost:3000/health')
  console.log('   curl http://localhost:3000/api/articles')
  console.log('')
  console.log('按 Ctrl+C 停止服务')
  console.log('========================================')
})
