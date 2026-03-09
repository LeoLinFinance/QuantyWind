const axios = require('axios')

/**
 * 生物医疗数据源
 * 从多个来源采集生物医疗前沿技术
 */

// 生物医疗热门关键词（中英文）
const BIOTECH_KEYWORDS = [
  'CRISPR', 'gene therapy', 'mRNA vaccine', 'CAR-T', 
  'organoid', 'brain-computer interface', 'synthetic biology',
  'precision medicine', 'immunotherapy', 'regenerative medicine',
  'AI drug discovery', 'protein folding', 'AlphaFold',
  'liquid biopsy', 'microbiome', 'gene editing'
]

/**
 * 从arXiv采集生物医疗论文
 */
async function searchBiotechPapers(maxResults = 10) {
  const papers = []
  
  // 使用q-bio分类
  const categories = ['q-bio.QM', 'q-bio.GN', 'q-bio.MN', 'q-bio.NC']
  
  for (const category of categories) {
    try {
      const url = `http://export.arxiv.org/api/query?search_query=cat:${category}&sortBy=submittedDate&sortOrder=descending&max_results=${Math.ceil(maxResults / categories.length)}`
      
      const response = await axios.get(url, {
        headers: { 'User-Agent': 'Mozilla/5.0' }
      })
      
      const entries = parseArxivXML(response.data)
      papers.push(...entries.map(entry => ({
        title: entry.title,
        description: entry.summary,
        rawContent: `Title: ${entry.title}\n\nAbstract: ${entry.summary}\n\nAuthors: ${entry.authors.join(', ')}\n\nPublished: ${entry.published}`,
        source: 'arxiv',
        sourceUrl: entry.link,
        category: 'biotech',
        publishTime: entry.published.split('T')[0]
      })))
      
      await sleep(2000)
    } catch (error) {
      console.error(`采集 ${category} 失败:`, error.message)
    }
  }
  
  return papers.slice(0, maxResults)
}

/**
 * 解析arXiv XML响应
 */
function parseArxivXML(xml) {
  const entries = []
  const entryMatches = xml.match(/<entry>[\s\S]*?<\/entry>/g) || []
  
  for (const entryXml of entryMatches) {
    const title = extractTag(entryXml, 'title')
    const summary = extractTag(entryXml, 'summary')
    const published = extractTag(entryXml, 'published')
    const link = entryXml.match(/<id>(.*?)<\/id>/)?.[1] || ''
    
    const authorMatches = entryXml.match(/<author>[\s\S]*?<name>(.*?)<\/name>[\s\S]*?<\/author>/g) || []
    const authors = authorMatches.map(a => a.match(/<name>(.*?)<\/name>/)?.[1] || '')
    
    if (title && summary) {
      entries.push({
        title: title.replace(/\s+/g, ' ').trim(),
        summary: summary.replace(/\s+/g, ' ').trim(),
        published,
        link,
        authors
      })
    }
  }
  
  return entries
}

function extractTag(xml, tag) {
  const match = xml.match(new RegExp(`<${tag}>(.*?)<\/${tag}>`, 's'))
  return match ? match[1].trim() : ''
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

module.exports = {
  searchBiotechPapers
}
