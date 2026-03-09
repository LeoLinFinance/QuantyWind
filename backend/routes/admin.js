const express = require('express')
const router = express.Router()
const Article = require('../models/Article')

// 获取统计数据
router.get('/stats', async (req, res) => {
  try {
    const totalArticles = await Article.countDocuments()
    const totalViews = await Article.aggregate([
      { $group: { _id: null, total: { $sum: '$views' } } }
    ])
    const totalLikes = await Article.aggregate([
      { $group: { _id: null, total: { $sum: '$likes' } } }
    ])
    
    const categoryStats = await Article.aggregate([
      { $group: { _id: '$category', count: { $sum: 1 } } }
    ])

    res.json({
      success: true,
      data: {
        totalArticles,
        totalViews: totalViews[0]?.total || 0,
        totalLikes: totalLikes[0]?.total || 0,
        categoryStats
      }
    })
  } catch (error) {
    res.status(500).json({ success: false, message: error.message })
  }
})

// 获取文章列表（管理）
router.get('/articles', async (req, res) => {
  try {
    const { page = 1, pageSize = 20, status } = req.query
    const skip = (page - 1) * pageSize
    
    const query = status ? { status } : {}
    
    const articles = await Article.find(query)
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(parseInt(pageSize))
    
    const total = await Article.countDocuments(query)
    
    res.json({ 
      success: true, 
      data: { articles, total, page: parseInt(page), pageSize: parseInt(pageSize) }
    })
  } catch (error) {
    res.status(500).json({ success: false, message: error.message })
  }
})

// 更新文章
router.put('/articles/:id', async (req, res) => {
  try {
    const article = await Article.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true }
    )
    
    if (!article) {
      return res.status(404).json({ success: false, message: '文章不存在' })
    }
    
    res.json({ success: true, data: article })
  } catch (error) {
    res.status(500).json({ success: false, message: error.message })
  }
})

// 删除文章
router.delete('/articles/:id', async (req, res) => {
  try {
    const article = await Article.findByIdAndDelete(req.params.id)
    
    if (!article) {
      return res.status(404).json({ success: false, message: '文章不存在' })
    }
    
    res.json({ success: true, message: '删除成功' })
  } catch (error) {
    res.status(500).json({ success: false, message: error.message })
  }
})

// 采集状态监控
router.get('/crawler/status', async (req, res) => {
  try {
    const last24h = new Date(Date.now() - 24 * 60 * 60 * 1000)
    const recentArticles = await Article.countDocuments({
      crawledAt: { $gte: last24h }
    })
    
    res.json({
      success: true,
      data: {
        recentArticles,
        lastCrawl: await Article.findOne().sort({ crawledAt: -1 }).select('crawledAt')
      }
    })
  } catch (error) {
    res.status(500).json({ success: false, message: error.message })
  }
})

module.exports = router
