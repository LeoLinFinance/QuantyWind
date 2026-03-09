const express = require('express')
const router = express.Router()
const Article = require('../models/Article')

// 获取文章列表
router.get('/', async (req, res) => {
  try {
    const { category = 'all', page = 1, pageSize = 10 } = req.query
    const skip = (page - 1) * pageSize
    
    const query = category === 'all' ? {} : { category }
    
    const articles = await Article.find(query)
      .select('title category summary publishTime views likes audioUrl duration')
      .sort({ publishTime: -1 })
      .skip(skip)
      .limit(parseInt(pageSize))
    
    res.json({ success: true, data: articles })
  } catch (error) {
    res.status(500).json({ success: false, message: error.message })
  }
})

// 获取文章详情
router.get('/:id', async (req, res) => {
  try {
    const article = await Article.findById(req.params.id)
      .populate('relatedArticles', 'title category')
    
    if (!article) {
      return res.status(404).json({ success: false, message: '文章不存在' })
    }
    
    // 增加浏览量
    article.views += 1
    await article.save()
    
    res.json({ success: true, data: article })
  } catch (error) {
    res.status(500).json({ success: false, message: error.message })
  }
})

// 搜索文章
router.get('/search', async (req, res) => {
  try {
    const { keyword, page = 1, pageSize = 10 } = req.query
    const skip = (page - 1) * pageSize
    
    const articles = await Article.find({
      $or: [
        { title: { $regex: keyword, $options: 'i' } },
        { summary: { $regex: keyword, $options: 'i' } },
        { tags: { $in: [new RegExp(keyword, 'i')] } }
      ]
    })
    .select('title category summary publishTime')
    .sort({ publishTime: -1 })
    .skip(skip)
    .limit(parseInt(pageSize))
    
    res.json({ success: true, data: articles })
  } catch (error) {
    res.status(500).json({ success: false, message: error.message })
  }
})

module.exports = router
