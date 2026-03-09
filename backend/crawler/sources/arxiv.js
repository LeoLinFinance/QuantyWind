const axios = require('axios')
const cheerio = require('cheerio')

class ArxivCrawler {
  constructor() {
    this.baseUrl = 'http://export.arxiv.org/api/query'
    this.categories = ['cs.AI', 'cs.LG', 'quant-ph', 'cs.HC']
  }

  async crawl() {
    const allPapers = []
    
    for (const category of this.categories) {
      try {
        const papers = await this.searchPapers(category)
        allPapers.push(...papers)
      } catch (error) {
        console.error(`arXiv ${category} 采集失败:`, error.message)
      }
    }

    return allPapers
  }

  async searchPapers(category, maxResults = 10) {
    const response = await axios.get(this.baseUrl, {
      params: {
        search_query: `cat:${category}`,
        sortBy: 'submittedDate',
        sortOrder: 'descending',
        max_results: maxResults
      }
    })

    const $ = cheerio.load(response.data, { xmlMode: true })
    const papers = []

    $('entry').each((i, elem) => {
      const $entry = $(elem)
      const title = $entry.find('title').text().trim()
      const summary = $entry.find('summary').text().trim()
      const authors = $entry.find('author name').map((i, el) => $(el).text()).get()
      const published = $entry.find('published').text()
      const link = $entry.find('id').text()

      papers.push({
        source: 'arxiv',
        sourceUrl: link,
        title: title,
        description: summary.substring(0, 200) + '...',
        category: this.mapCategory(category),
        rawContent: `
论文标题: ${title}
作者: ${authors.join(', ')}
分类: ${category}
发布时间: ${published}
摘要: ${summary}
论文链接: ${link}
        `,
        metadata: {
          authors: authors,
          arxivCategory: category,
          published: published
        }
      })
    })

    return papers
  }

  mapCategory(arxivCat) {
    const mapping = {
      'cs.AI': 'ai',
      'cs.LG': 'ai',
      'cs.CL': 'ai',
      'cs.CV': 'ai',
      'quant-ph': 'quantum',
      'cs.HC': 'bci',
      'q-bio.NC': 'bci',
      'cs.AR': 'chip',
      'cs.RO': 'embodied',
      'q-bio.GN': 'biotech',
      'q-bio.QM': 'biotech'
    }
    return mapping[arxivCat] || 'ai'
  }
}

module.exports = new ArxivCrawler()
