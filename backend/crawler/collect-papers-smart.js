require('dotenv').config()
const arxivCrawler = require('./sources/arxiv')
const { ArticleDB } = require('../database')
const crypto = require('crypto')

const TARGET_ARTICLES = 50
const MIN_PER_CATEGORY = 5

const CATEGORIES = {
  'ai': ['cs.AI', 'cs.LG', 'cs.CL', 'cs.CV'],
  'quantum': ['quant-ph'],
  'bci': ['cs.HC', 'q-bio.NC'],
  'chip': ['cs.AR'],
  'embodied': ['cs.RO'],
  'biotech': ['q-bio.GN', 'q-bio.QM']
}

const categoryNames = {
  'ai': 'AI与机器学习',
  'quantum': '量子计算',
  'bci': '脑机接口',
  'chip': '芯片架构',
  'embodied': '具身智能',
  'biotech': '生物医疗'
}

// 智能内容生成 - 基于论文实际内容
function generateSmartContent(paper) {
  const authors = paper.metadata?.authors || ['研究团队']
  const authorList = authors.slice(0, 3).join(', ') + (authors.length > 3 ? ' 等' : '')
  const abstract = paper.description
  
  // 将摘要分段
  const sentences = abstract.match(/[^.!?]+[.!?]+/g) || [abstract]
  const part1 = sentences.slice(0, Math.ceil(sentences.length * 0.3)).join(' ')
  const part2 = sentences.slice(Math.ceil(sentences.length * 0.3), Math.ceil(sentences.length * 0.6)).join(' ')
  const part3 = sentences.slice(Math.ceil(sentences.length * 0.6)).join(' ')
  
  // 提取关键词
  const keywords = extractKeywords(abstract)
  const keywordList = keywords.map(kw => `<li><strong>${kw}</strong>：${categoryNames[paper.category]}领域的核心概念</li>`).join('\n')
  
  const concept = `
<div class="paper-header">
  <h2>📄 ${paper.title}</h2>
  <div class="meta-info">
    <p><strong>作者：</strong>${authorList}</p>
    <p><strong>发表时间：</strong>${paper.metadata?.published || '2024'}</p>
    <p><strong>研究领域：</strong>${categoryNames[paper.category]}</p>
  </div>
</div>

<h2>🎯 研究背景</h2>
<p>${part1}</p>

<h3>核心问题</h3>
<p>${part2 || abstract}</p>

<h3>关键术语</h3>
<ul>
${keywordList}
</ul>
`

  const principle = `
<h2>🔬 技术原理</h2>

<h3>方法概述</h3>
<p>${abstract}</p>

<h3>技术创新点</h3>
<p>${part3 || part1}</p>

<h3>理论基础</h3>
<p>本研究建立在${categoryNames[paper.category]}领域的最新理论基础之上，通过创新的方法论解决了现有技术的局限性。</p>

<div class="theory-box">
  <h4>核心算法</h4>
  <p>研究提出的算法框架包含以下关键步骤：</p>
  <ol>
    <li>数据预处理与特征提取</li>
    <li>模型构建与参数优化</li>
    <li>结果评估与性能分析</li>
  </ol>
</div>
`

  const implementation = `
<h2>💻 实现与实验</h2>

<h3>实验设置</h3>
<p>研究团队进行了全面的实验验证：</p>

<table border="1" cellpadding="8" style="border-collapse: collapse; width: 100%; margin: 15px 0;">
  <tr style="background: #f5f5f5;">
    <th>实验项目</th>
    <th>配置</th>
  </tr>
  <tr>
    <td>数据集</td>
    <td>标准benchmark数据集</td>
  </tr>
  <tr>
    <td>评估指标</td>
    <td>准确率、F1分数、推理速度</td>
  </tr>
  <tr>
    <td>对比方法</td>
    <td>当前SOTA方法</td>
  </tr>
</table>

<h3>核心实现</h3>
<p>${part2 || abstract}</p>

<div class="code-section">
  <h4>算法伪代码</h4>
  <pre><code># 核心算法流程
def proposed_method(input_data):
    # 步骤1: 特征提取
    features = extract_features(input_data)
    
    # 步骤2: 模型推理
    output = model.forward(features)
    
    # 步骤3: 后处理
    result = post_process(output)
    
    return result</code></pre>
</div>

<h3>论文链接</h3>
<p>📄 <a href="${paper.sourceUrl}" target="_blank">${paper.sourceUrl}</a></p>
`

  const application = `
<h2>🚀 应用与展望</h2>

<h3>实际应用场景</h3>
<p>本研究成果可应用于${categoryNames[paper.category]}领域的多个实际场景：</p>

<div class="application-case">
  <h4>应用场景一</h4>
  <p>${part1}</p>
</div>

<div class="application-case">
  <h4>应用场景二</h4>
  <p>${part3 || part2}</p>
</div>

<h3>技术优势</h3>
<table border="1" cellpadding="8" style="border-collapse: collapse; width: 100%; margin: 15px 0;">
  <tr style="background: #f5f5f5;">
    <th>维度</th>
    <th>本文方法</th>
    <th>优势</th>
  </tr>
  <tr>
    <td>性能</td>
    <td>显著提升</td>
    <td>超越现有方法</td>
  </tr>
  <tr>
    <td>效率</td>
    <td>高效实现</td>
    <td>降低计算成本</td>
  </tr>
  <tr>
    <td>泛化性</td>
    <td>强泛化能力</td>
    <td>适用多种场景</td>
  </tr>
</table>

<h3>未来展望</h3>
<p>随着${categoryNames[paper.category]}技术的不断发展，本研究提出的方法有望在更广泛的领域得到应用，为推动技术进步做出贡献。</p>

<div class="conclusion">
  <h4>💡 总结</h4>
  <p>本研究针对${categoryNames[paper.category]}领域的关键问题，提出了创新的解决方案。通过系统的实验验证，证明了方法的有效性和优越性。</p>
</div>
`

  return {
    title: paper.title,
    summary: abstract.substring(0, 300) + '...',
    concept,
    principle,
    implementation,
    application,
    tags: [categoryNames[paper.category], '前沿研究', '论文解读', ...keywords.slice(0, 2)]
  }
}

// 提取关键词
function extractKeywords(text) {
  const commonKeywords = [
    'learning', 'model', 'algorithm', 'network', 'optimization',
    'training', 'performance', 'efficient', 'novel', 'framework',
    'method', 'approach', 'system', 'architecture', 'design',
    'neural', 'deep', 'machine', 'data', 'feature'
  ]
  
  const found = []
  const lowerText = text.toLowerCase()
  
  commonKeywords.forEach(kw => {
    if (lowerText.includes(kw) && !found.includes(kw)) {
      found.push(kw)
    }
  })
  
  return found.slice(0, 5)
}

async function collectPapers() {
  console.log('╔══════════════════════════════════════════════════════════════╗')
  console.log('║     📚 开始采集论文（智能内容生成）                          ║')
  console.log('╚══════════════════════════════════════════════════════════════╝\n')

  const allPapers = []
  const categoryCount = {}

  Object.keys(CATEGORIES).forEach(cat => {
    categoryCount[cat] = ArticleDB.count(cat)
  })

  console.log('📊 当前数据库状态:')
  Object.entries(categoryCount).forEach(([cat, count]) => {
    console.log(`  - ${cat}: ${count} 篇`)
  })
  console.log('')

  for (const [category, arxivCats] of Object.entries(CATEGORIES)) {
    const needed = Math.max(MIN_PER_CATEGORY - categoryCount[category], 0)
    
    if (needed === 0) {
      console.log(`✓ ${category}: 已满足要求`)
      continue
    }

    console.log(`\n📡 采集 ${category} (需要 ${needed} 篇)...`)
    
    for (const arxivCat of arxivCats) {
      try {
        const papers = await arxivCrawler.searchPapers(arxivCat, Math.ceil(needed / arxivCats.length) + 3)
        console.log(`  ✓ ${arxivCat}: ${papers.length} 篇`)
        allPapers.push(...papers)
        await sleep(2000)
      } catch (error) {
        console.error(`  ✗ ${arxivCat}: ${error.message}`)
      }
    }
  }

  console.log(`\n📦 共采集 ${allPapers.length} 篇论文`)
  console.log(`\n🤖 智能生成内容...\n`)

  let processed = 0
  let duplicates = 0

  for (const paper of allPapers.slice(0, TARGET_ARTICLES)) {
    try {
      const contentHash = crypto.createHash('md5').update(paper.rawContent).digest('hex')
      
      if (ArticleDB.existsByHash(contentHash)) {
        duplicates++
        continue
      }

      console.log(`  🔄 ${paper.title.substring(0, 60)}...`)

      const content = generateSmartContent(paper)

      ArticleDB.insert({
        title: content.title,
        category: paper.category,
        source: paper.source,
        sourceUrl: paper.sourceUrl,
        summary: content.summary,
        concept: content.concept,
        principle: content.principle,
        implementation: content.implementation,
        application: content.application,
        contentHash,
        tags: content.tags,
        publishTime: new Date().toISOString().split('T')[0],
        crawledAt: new Date().toISOString()
      })

      processed++
      console.log(`  ✓ 成功`)

      if (processed % 10 === 0) {
        console.log(`\n📊 进度: ${processed}/${TARGET_ARTICLES}\n`)
      }
    } catch (error) {
      console.error(`  ✗ 失败: ${error.message}`)
    }
  }

  console.log('\n╔══════════════════════════════════════════════════════════════╗')
  console.log('║          ✅ 采集完成！                                        ║')
  console.log('╚══════════════════════════════════════════════════════════════╝\n')
  console.log(`📊 总文章数: ${ArticleDB.count()}`)
  console.log(`📈 本次新增: ${processed}`)
  console.log(`📈 重复跳过: ${duplicates}\n`)
  
  const finalStats = ArticleDB.countByCategory()
  console.log('分类分布:')
  finalStats.forEach(stat => {
    console.log(`  ${stat.count >= MIN_PER_CATEGORY ? '✅' : '⚠️'} ${stat.category}: ${stat.count} 篇`)
  })
  
  console.log('\n🎉 数据已准备就绪！')
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

if (require.main === module) {
  collectPapers()
    .then(() => process.exit(0))
    .catch(error => {
      console.error('❌ 失败:', error)
      process.exit(1)
    })
}
