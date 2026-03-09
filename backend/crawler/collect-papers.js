require('dotenv').config()
const arxivCrawler = require('./sources/arxiv')
const contentProcessor = require('./processor')
const { ArticleDB } = require('../database')

// 目标配置
const TARGET_ARTICLES = parseInt(process.env.TARGET_ARTICLES) || 50
const MIN_PER_CATEGORY = parseInt(process.env.MIN_PER_CATEGORY) || 5

// 分类映射
const CATEGORIES = {
  'ai': ['cs.AI', 'cs.LG', 'cs.CL', 'cs.CV'],
  'quantum': ['quant-ph'],
  'bci': ['cs.HC', 'q-bio.NC'],
  'chip': ['cs.AR'],
  'embodied': ['cs.RO'],
  'biotech': ['q-bio.GN', 'q-bio.QM']
}

async function collectPapers() {
  console.log('╔══════════════════════════════════════════════════════════════╗')
  console.log('║                                                              ║')
  console.log('║          📚 开始采集论文数据                                  ║')
  console.log('║                                                              ║')
  console.log('╚══════════════════════════════════════════════════════════════╝')
  console.log('')
  console.log(`🎯 目标: 采集 ${TARGET_ARTICLES} 篇论文`)
  console.log(`📊 要求: 每个分类至少 ${MIN_PER_CATEGORY} 篇`)
  console.log('')

  const allPapers = []
  const categoryCount = {}

  // 初始化分类计数
  Object.keys(CATEGORIES).forEach(cat => {
    categoryCount[cat] = ArticleDB.count(cat)
  })

  console.log('📊 当前数据库状态:')
  Object.entries(categoryCount).forEach(([cat, count]) => {
    console.log(`  - ${cat}: ${count} 篇`)
  })
  console.log('')

  // 按分类采集
  for (const [category, arxivCats] of Object.entries(CATEGORIES)) {
    const needed = Math.max(MIN_PER_CATEGORY - categoryCount[category], 0)
    
    if (needed === 0) {
      console.log(`✓ ${category}: 已满足最小要求，跳过`)
      continue
    }

    console.log(`\n📡 采集 ${category} 分类 (需要 ${needed} 篇)...`)
    
    for (const arxivCat of arxivCats) {
      try {
        const papers = await arxivCrawler.searchPapers(arxivCat, Math.ceil(needed / arxivCats.length) + 5)
        console.log(`  ✓ ${arxivCat}: 获取 ${papers.length} 篇`)
        allPapers.push(...papers)
        
        // 避免请求过快
        await sleep(2000)
      } catch (error) {
        console.error(`  ✗ ${arxivCat}: ${error.message}`)
      }
    }
  }

  console.log(`\n📦 共采集到 ${allPapers.length} 篇论文`)
  
  // 限制处理数量，避免一次性处理太多
  const papersToProcess = allPapers.slice(0, Math.min(allPapers.length, TARGET_ARTICLES))
  
  console.log(`\n🤖 开始AI处理和生成内容 (处理 ${papersToProcess.length} 篇)...`)
  console.log('⏰ 这可能需要一些时间，请耐心等待...')
  console.log('💡 使用阶跃星辰 Step-1-32k 模型\n')

  // 分批处理，每批5篇
  const batchSize = 5
  let totalProcessed = 0
  let totalErrors = 0
  
  for (let i = 0; i < papersToProcess.length; i += batchSize) {
    const batch = papersToProcess.slice(i, i + batchSize)
    console.log(`\n📦 处理批次 ${Math.floor(i / batchSize) + 1}/${Math.ceil(papersToProcess.length / batchSize)} (${batch.length} 篇)`)
    
    const result = await contentProcessor.processAll(batch)
    totalProcessed += result.processed
    totalErrors += result.errors
    
    // 显示进度
    const progress = Math.round((i + batch.length) / papersToProcess.length * 100)
    console.log(`📊 总进度: ${progress}% (成功: ${totalProcessed}, 失败: ${totalErrors})`)
    
    // 批次间休息，避免API限流
    if (i + batchSize < papersToProcess.length) {
      console.log('⏸️  休息3秒...')
      await sleep(3000)
    }
  }

  // 最终统计
  console.log('\n╔══════════════════════════════════════════════════════════════╗')
  console.log('║                                                              ║')
  console.log('║          ✅ 采集完成！                                        ║')
  console.log('║                                                              ║')
  console.log('╚══════════════════════════════════════════════════════════════╝')
  console.log('')
  console.log('📊 最终统计:')
  console.log(`  - 总文章数: ${ArticleDB.count()}`)
  console.log('')
  console.log('📈 分类分布:')
  
  const finalStats = ArticleDB.countByCategory()
  finalStats.forEach(stat => {
    const emoji = stat.count >= MIN_PER_CATEGORY ? '✅' : '⚠️'
    console.log(`  ${emoji} ${stat.category}: ${stat.count} 篇`)
  })
  
  console.log('')
  console.log('🎉 数据已准备就绪！')
  console.log('💡 运行 node production-server.js 启动服务器')
  console.log('')
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

// 运行采集
if (require.main === module) {
  collectPapers()
    .then(() => {
      console.log('✅ 采集任务完成')
      process.exit(0)
    })
    .catch(error => {
      console.error('❌ 采集任务失败:', error)
      process.exit(1)
    })
}

module.exports = collectPapers
