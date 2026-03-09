require('dotenv').config()
const cron = require('node-cron')
const githubCrawler = require('./sources/github')
const huggingfaceCrawler = require('./sources/huggingface')
const arxivCrawler = require('./sources/arxiv')
const contentProcessor = require('./processor')

class CrawlerScheduler {
  constructor() {
    this.interval = process.env.CRAWLER_INTERVAL || 3
    this.isRunning = false
  }

  start() {
    console.log(`🕐 采集调度器启动，每${this.interval}小时执行一次`)
    
    // 立即执行一次
    this.runCrawlers()
    
    // 定时执行
    cron.schedule(`0 */${this.interval} * * *`, () => {
      this.runCrawlers()
    })
  }

  async runCrawlers() {
    if (this.isRunning) {
      console.log('⏳ 上次采集尚未完成，跳过本次执行')
      return
    }

    this.isRunning = true
    console.log(`\n🚀 开始采集 - ${new Date().toLocaleString()}`)

    try {
      const results = await Promise.allSettled([
        this.crawlGitHub(),
        this.crawlHuggingFace(),
        this.crawlArxiv()
      ])

      const allContent = results
        .filter(r => r.status === 'fulfilled')
        .flatMap(r => r.value)

      console.log(`📊 本次采集到 ${allContent.length} 条内容`)

      // 处理内容
      await contentProcessor.processAll(allContent)

      console.log('✅ 采集完成\n')
    } catch (error) {
      console.error('❌ 采集失败:', error)
    } finally {
      this.isRunning = false
    }
  }

  async crawlGitHub() {
    try {
      console.log('📡 采集GitHub...')
      const content = await githubCrawler.crawl()
      console.log(`  ✓ GitHub: ${content.length}条`)
      return content
    } catch (error) {
      console.error('  ✗ GitHub采集失败:', error.message)
      return []
    }
  }

  async crawlHuggingFace() {
    try {
      console.log('📡 采集HuggingFace...')
      const content = await huggingfaceCrawler.crawl()
      console.log(`  ✓ HuggingFace: ${content.length}条`)
      return content
    } catch (error) {
      console.error('  ✗ HuggingFace采集失败:', error.message)
      return []
    }
  }

  async crawlArxiv() {
    try {
      console.log('📡 采集arXiv...')
      const content = await arxivCrawler.crawl()
      console.log(`  ✓ arXiv: ${content.length}条`)
      return content
    } catch (error) {
      console.error('  ✗ arXiv采集失败:', error.message)
      return []
    }
  }
}

// 启动调度器
if (require.main === module) {
  const scheduler = new CrawlerScheduler()
  scheduler.start()
}

module.exports = CrawlerScheduler
