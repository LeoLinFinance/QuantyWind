const mongoose = require('mongoose')

const articleSchema = new mongoose.Schema({
  title: { type: String, required: true },
  category: { 
    type: String, 
    enum: ['ai', 'embodied', 'quantum', 'bci', 'chip', 'biotech'],
    required: true 
  },
  source: { type: String, required: true },
  sourceUrl: { type: String, required: true },
  summary: { type: String, required: true },
  
  // 四层内容结构
  layers: [{
    level: { type: String, enum: ['concept', 'principle', 'implementation', 'application'] },
    content: { type: String, required: true },
    wordCount: Number
  }],
  
  // 音频
  audioUrl: String,
  duration: String,
  
  // 统计数据
  views: { type: Number, default: 0 },
  likes: { type: Number, default: 0 },
  shares: { type: Number, default: 0 },
  
  // 元数据
  publishTime: { type: Date, default: Date.now },
  crawledAt: { type: Date, default: Date.now },
  status: { 
    type: String, 
    enum: ['draft', 'published', 'archived'],
    default: 'published'
  },
  
  // 去重标识
  contentHash: { type: String, unique: true },
  
  // 知识图谱关联
  relatedArticles: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Article' }],
  tags: [String]
}, {
  timestamps: true
})

// 索引
articleSchema.index({ category: 1, publishTime: -1 })
articleSchema.index({ contentHash: 1 })
articleSchema.index({ tags: 1 })

module.exports = mongoose.model('Article', articleSchema)
