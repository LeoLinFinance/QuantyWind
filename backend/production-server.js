require('dotenv').config()
const express = require('express')
const cors = require('cors')
const bodyParser = require('body-parser')
const { ArticleDB } = require('./database')
const aiService = require('./services/aiService')

const app = express()
const PORT = process.env.PORT || 3000

// 中间件
app.use(cors())
app.use(bodyParser.json())

// 健康检查
app.get('/health', (req, res) => {
  const stats = ArticleDB.countByCategory()
  res.json({ 
    status: 'ok', 
    timestamp: new Date(),
    mode: 'production',
    totalArticles: ArticleDB.count(),
    categoryStats: stats
  })
})

// 获取文章列表
app.get('/api/articles', (req, res) => {
  try {
    const { category = 'all', page = 1, pageSize = 10 } = req.query
    const articles = ArticleDB.findAll(category, parseInt(page), parseInt(pageSize))
    res.json({ success: true, data: articles })
  } catch (error) {
    console.error('获取文章列表失败:', error)
    res.status(500).json({ success: false, message: error.message })
  }
})

// 获取文章详情
app.get('/api/articles/:id', (req, res) => {
  try {
    const article = ArticleDB.findById(req.params.id)
    
    if (!article) {
      return res.status(404).json({ success: false, message: '文章不存在' })
    }
    
    // 尝试增加浏览量，但不影响文章返回
    try {
      ArticleDB.incrementViews(req.params.id)
    } catch (viewError) {
      console.warn('更新浏览量失败:', viewError.message)
    }
    
    res.json({ success: true, data: article })
  } catch (error) {
    console.error('获取文章详情失败:', error)
    res.status(500).json({ success: false, message: error.message })
  }
})

// 搜索文章
app.get('/api/articles/search', (req, res) => {
  try {
    const { keyword, page = 1, pageSize = 10 } = req.query
    const articles = ArticleDB.search(keyword, parseInt(page), parseInt(pageSize))
    res.json({ success: true, data: articles })
  } catch (error) {
    console.error('搜索失败:', error)
    res.status(500).json({ success: false, message: error.message })
  }
})

// AI聊天
app.post('/api/chat', async (req, res) => {
  try {
    const { articleId, message, history = [] } = req.body
    
    const article = ArticleDB.findById(articleId)
    if (!article) {
      return res.status(404).json({ success: false, message: '文章不存在' })
    }
    
    const context = `
你是一位专业的AI技术助手，正在帮助用户理解以下文章：

文章标题: ${article.title}
文章分类: ${article.category}
文章摘要: ${article.summary}

用户问题: ${message}

请基于文章内容简洁地回答用户的问题（200字以内）。如果问题超出文章范围，可以适当扩展相关知识。
    `
    
    const reply = await aiService.generateAIResponse(context, history)
    
    res.json({ 
      success: true, 
      data: { reply } 
    })
  } catch (error) {
    console.error('AI聊天失败:', error)
    res.status(500).json({ success: false, message: error.message })
  }
})

// 统计数据
app.get('/api/admin/stats', (req, res) => {
  try {
    const categoryStats = ArticleDB.countByCategory()
    res.json({
      success: true,
      data: {
        totalArticles: ArticleDB.count(),
        categoryStats
      }
    })
  } catch (error) {
    console.error('获取统计失败:', error)
    res.status(500).json({ success: false, message: error.message })
  }
})

// 错误处理
app.use((err, req, res, next) => {
  console.error(err.stack)
  res.status(500).json({ 
    success: false, 
    message: '服务器错误',
    error: process.env.NODE_ENV === 'development' ? err.message : undefined
  })
})

app.listen(PORT, () => {
  console.log('🎉 ========================================')
  console.log('🚀 滴答学术生产服务器启动成功！')
  console.log('🎉 ========================================')
  console.log('')
  console.log(`📍 服务地址: http://localhost:${PORT}`)
  console.log(`📍 健康检查: http://localhost:${PORT}/health`)
  console.log(`📍 文章列表: http://localhost:${PORT}/api/articles`)
  console.log('')
  console.log('💡 使用真实AI模型和数据库')
  console.log(`💡 当前文章数: ${ArticleDB.count()}`)
  console.log('')
  console.log('按 Ctrl+C 停止服务')
  console.log('========================================')
})
