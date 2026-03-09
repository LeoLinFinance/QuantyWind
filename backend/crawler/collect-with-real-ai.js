require('dotenv').config({ path: require('path').join(__dirname, '../.env') })
const arxivCrawler = require('./sources/arxiv')
const biotechCrawler = require('./sources/biotech')
const { ArticleDB } = require('../database')
const aiService = require('../services/aiService')
const crypto = require('crypto')

const TARGET_ARTICLES = 50  // 生成50篇
const MIN_PER_CATEGORY = 5

const CATEGORIES = {
  'world-model': ['cs.AI', 'cs.CV', 'cs.LG'],  // 世界模型
  'embodied': ['cs.RO', 'cs.AI'],              // 具身智能
  'bci': ['cs.HC', 'q-bio.NC'],                // 脑机接口
  'chip': ['cs.AR', 'cs.DC'],                  // 芯片架构
  'biotech': ['q-bio.QM', 'q-bio.GN']          // 生物医疗
}

async function collectWithRealAI() {
  console.log('╔══════════════════════════════════════════════════════════════╗')
  console.log('║     🤖 使用真实AI生成独特内容                                 ║')
  console.log('╚══════════════════════════════════════════════════════════════╝\n')
  console.log('💡 使用阶跃星辰 Step-1-32k 模型')
  console.log('⏰ 每篇文章需要约30-60秒生成\n')

  const allPapers = []
  
  // 采集论文
  for (const [category, arxivCats] of Object.entries(CATEGORIES)) {
    const current = ArticleDB.count(category)
    const needed = Math.max(MIN_PER_CATEGORY - current, 0)
    
    if (needed === 0) continue
    
    console.log(`📡 采集 ${category} (需要 ${needed} 篇)...`)
    
    // 生物医疗使用专门的采集器
    if (category === 'biotech') {
      try {
        const papers = await biotechCrawler.searchBiotechPapers(needed + 2)
        console.log(`  ✓ biotech: ${papers.length} 篇`)
        allPapers.push(...papers)
        await sleep(2000)
      } catch (error) {
        console.error(`  ✗ biotech: ${error.message}`)
      }
    } else {
      // 其他类别使用arXiv
      for (const arxivCat of arxivCats) {
        try {
          const papers = await arxivCrawler.searchPapers(arxivCat, needed + 2)
          papers.forEach(p => p.category = category)
          console.log(`  ✓ ${arxivCat}: ${papers.length} 篇`)
          allPapers.push(...papers)
          await sleep(2000)
        } catch (error) {
          console.error(`  ✗ ${arxivCat}: ${error.message}`)
        }
      }
    }
  }

  console.log(`\n📦 共采集 ${allPapers.length} 篇论文`)
  console.log(`\n🤖 开始AI生成（这需要一些时间）...\n`)

  let processed = 0
  let errors = 0

  for (const paper of allPapers.slice(0, TARGET_ARTICLES)) {
    try {
      const contentHash = crypto.createHash('md5').update(paper.rawContent).digest('hex')
      
      if (ArticleDB.existsByHash(contentHash)) {
        console.log(`  ⚠️  已存在: ${paper.title.substring(0, 50)}...`)
        continue
      }

      console.log(`\n  🔄 [${processed + 1}/${TARGET_ARTICLES}] ${paper.title.substring(0, 60)}...`)
      console.log(`     调用AI生成内容...`)

      // 调用真实AI生成内容
      const generatedContent = await aiService.generateContent(paper.rawContent, paper.category)
      
      let contentData
      try {
        contentData = typeof generatedContent === 'string' 
          ? JSON.parse(generatedContent) 
          : generatedContent
      } catch (parseError) {
        console.log(`     ⚠️  AI返回非JSON，使用简化处理`)
        // 如果AI没返回JSON，手动构造
        contentData = {
          title: paper.title,
          summary: paper.description.substring(0, 300),
          layers: [
            { level: 'concept', content: generatedContent.substring(0, 1000) },
            { level: 'principle', content: generatedContent.substring(1000, 3000) },
            { level: 'implementation', content: generatedContent.substring(3000, 6000) },
            { level: 'application', content: generatedContent.substring(6000) }
          ],
          tags: []
        }
      }

      ArticleDB.insert({
        title: contentData.title || paper.title,
        category: paper.category,
        source: paper.source,
        sourceUrl: paper.sourceUrl,
        summary: contentData.summary || paper.description.substring(0, 300),
        concept: contentData.layers[0]?.content || '',
        principle: contentData.layers[1]?.content || '',
        implementation: contentData.layers[2]?.content || '',
        application: contentData.layers[3]?.content || '',
        contentHash,
        tags: contentData.tags || [],
        publishTime: new Date().toISOString().split('T')[0],
        crawledAt: new Date().toISOString()
      })

      processed++
      console.log(`     ✅ 成功生成`)

    } catch (error) {
      errors++
      console.error(`     ❌ 失败: ${error.message}`)
    }
  }

  console.log('\n╔══════════════════════════════════════════════════════════════╗')
  console.log('║          ✅ 完成！                                            ║')
  console.log('╚══════════════════════════════════════════════════════════════╝\n')
  console.log(`📊 成功: ${processed} 篇`)
  console.log(`❌ 失败: ${errors} 篇`)
  console.log(`📈 总计: ${ArticleDB.count()} 篇\n`)
  
  const stats = ArticleDB.countByCategory()
  console.log('分类分布:')
  stats.forEach(s => console.log(`  ${s.category}: ${s.count} 篇`))
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

if (require.main === module) {
  collectWithRealAI()
    .then(() => process.exit(0))
    .catch(error => {
      console.error('❌ 失败:', error)
      process.exit(1)
    })
}
