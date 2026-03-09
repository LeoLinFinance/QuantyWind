const crypto = require('crypto')
const { ArticleDB } = require('../database')
const aiService = require('../services/aiService')

class ContentProcessor {
  async processAll(rawContents) {
    console.log(`\n🔄 开始处理 ${rawContents.length} 条内容`)
    
    let processed = 0
    let duplicates = 0
    let errors = 0

    for (const raw of rawContents) {
      try {
        // 去重检查
        const contentHash = this.generateHash(raw.rawContent)
        
        if (ArticleDB.existsByHash(contentHash)) {
          duplicates++
          continue
        }

        console.log(`  🔄 处理中: ${raw.title.substring(0, 50)}...`)

        // AI生成分层内容
        const generatedContent = await aiService.generateContent(raw.rawContent, raw.category)
        
        let contentData
        try {
          // 尝试解析JSON
          contentData = typeof generatedContent === 'string' 
            ? JSON.parse(generatedContent) 
            : generatedContent
        } catch (parseError) {
          // 如果不是JSON，使用原始内容
          console.log(`  ⚠️  AI返回非JSON格式，使用原始内容`)
          contentData = {
            title: raw.title,
            summary: raw.description,
            layers: [
              { level: 'concept', content: raw.rawContent.substring(0, 500) },
              { level: 'principle', content: raw.rawContent },
              { level: 'implementation', content: '详细实现请参考原文链接' },
              { level: 'application', content: '应用场景分析中...' }
            ],
            tags: []
          }
        }

        // 保存文章
        const articleId = ArticleDB.insert({
          title: contentData.title || raw.title,
          category: raw.category,
          source: raw.source,
          sourceUrl: raw.sourceUrl,
          summary: contentData.summary || raw.description,
          concept: contentData.layers[0]?.content || '',
          principle: contentData.layers[1]?.content || '',
          implementation: contentData.layers[2]?.content || '',
          application: contentData.layers[3]?.content || '',
          contentHash,
          tags: contentData.tags || [],
          publishTime: new Date().toISOString().split('T')[0],
          crawledAt: new Date().toISOString()
        })

        if (articleId) {
          processed++
          console.log(`  ✓ 处理成功: ${contentData.title?.substring(0, 50) || raw.title.substring(0, 50)}...`)
        }

      } catch (error) {
        errors++
        console.error(`  ✗ 处理失败: ${error.message}`)
      }
    }

    console.log(`\n📈 处理统计:`)
    console.log(`  - 成功: ${processed}`)
    console.log(`  - 重复: ${duplicates}`)
    console.log(`  - 失败: ${errors}`)
    
    return { processed, duplicates, errors }
  }

  generateHash(content) {
    return crypto.createHash('md5').update(content).digest('hex')
  }

  async generateAudio(articleId) {
    // TODO: 集成TTS服务生成音频
    console.log(`  🎧 音频生成任务已加入队列: ${articleId}`)
  }
}

module.exports = new ContentProcessor()
