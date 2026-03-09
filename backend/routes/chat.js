const express = require('express')
const router = express.Router()
const { generateAIResponse } = require('../services/aiService')
const Article = require('../models/Article')

router.post('/', async (req, res) => {
  try {
    const { articleId, message, history = [] } = req.body
    
    // 获取文章上下文
    const article = await Article.findById(articleId)
    if (!article) {
      return res.status(404).json({ success: false, message: '文章不存在' })
    }
    
    // 构建上下文
    const context = `
文章标题: ${article.title}
文章分类: ${article.category}
文章内容摘要: ${article.summary}

用户问题: ${message}

请基于文章内容回答用户的问题，如果问题超出文章范围，可以适当扩展相关知识。
    `
    
    // 调用AI生成回复
    const reply = await generateAIResponse(context, history)
    
    res.json({ 
      success: true, 
      data: { reply } 
    })
  } catch (error) {
    res.status(500).json({ success: false, message: error.message })
  }
})

module.exports = router
