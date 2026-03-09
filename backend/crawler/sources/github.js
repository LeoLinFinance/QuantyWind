const axios = require('axios')

class GitHubCrawler {
  constructor() {
    this.token = process.env.GITHUB_TOKEN
    this.baseUrl = 'https://api.github.com'
    this.topics = ['artificial-intelligence', 'machine-learning', 'quantum-computing', 'brain-computer-interface']
  }

  async crawl() {
    const allRepos = []
    
    for (const topic of this.topics) {
      try {
        const repos = await this.searchRepos(topic)
        allRepos.push(...repos)
      } catch (error) {
        console.error(`GitHub ${topic} 采集失败:`, error.message)
      }
    }

    return allRepos
  }

  async searchRepos(topic) {
    const threeDaysAgo = new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
    
    const response = await axios.get(`${this.baseUrl}/search/repositories`, {
      params: {
        q: `topic:${topic} created:>${threeDaysAgo}`,
        sort: 'stars',
        order: 'desc',
        per_page: 10
      },
      headers: {
        'Authorization': `token ${this.token}`,
        'Accept': 'application/vnd.github.v3+json'
      }
    })

    return response.data.items.map(repo => ({
      source: 'github',
      sourceUrl: repo.html_url,
      title: repo.full_name,
      description: repo.description || '',
      category: this.mapCategory(topic),
      rawContent: `
项目名称: ${repo.full_name}
Stars: ${repo.stargazers_count}
描述: ${repo.description || '无'}
主要语言: ${repo.language || '未知'}
创建时间: ${repo.created_at}
README: ${repo.html_url}/blob/main/README.md
      `,
      metadata: {
        stars: repo.stargazers_count,
        language: repo.language,
        topics: repo.topics
      }
    }))
  }

  mapCategory(topic) {
    const mapping = {
      'artificial-intelligence': 'ai',
      'machine-learning': 'ai',
      'quantum-computing': 'quantum',
      'brain-computer-interface': 'bci'
    }
    return mapping[topic] || 'ai'
  }
}

module.exports = new GitHubCrawler()
