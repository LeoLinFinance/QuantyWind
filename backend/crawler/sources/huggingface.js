const axios = require('axios')

class HuggingFaceCrawler {
  constructor() {
    this.token = process.env.HUGGINGFACE_TOKEN
    this.baseUrl = 'https://huggingface.co/api'
  }

  async crawl() {
    const [models, spaces] = await Promise.all([
      this.crawlModels(),
      this.crawlSpaces()
    ])

    return [...models, ...spaces]
  }

  async crawlModels() {
    try {
      const response = await axios.get(`${this.baseUrl}/models`, {
        params: {
          sort: 'lastModified',
          direction: -1,
          limit: 20,
          filter: 'text-generation'
        },
        headers: this.token ? { 'Authorization': `Bearer ${this.token}` } : {}
      })

      return response.data.map(model => ({
        source: 'huggingface',
        sourceUrl: `https://huggingface.co/${model.id}`,
        title: model.id,
        description: model.description || '',
        category: 'ai',
        rawContent: `
模型名称: ${model.id}
下载量: ${model.downloads || 0}
点赞数: ${model.likes || 0}
任务类型: ${model.pipeline_tag || '未知'}
更新时间: ${model.lastModified}
模型卡片: https://huggingface.co/${model.id}
        `,
        metadata: {
          downloads: model.downloads,
          likes: model.likes,
          tags: model.tags
        }
      }))
    } catch (error) {
      console.error('HuggingFace模型采集失败:', error.message)
      return []
    }
  }

  async crawlSpaces() {
    try {
      const response = await axios.get(`${this.baseUrl}/spaces`, {
        params: {
          sort: 'lastModified',
          direction: -1,
          limit: 10
        },
        headers: this.token ? { 'Authorization': `Bearer ${this.token}` } : {}
      })

      return response.data.map(space => ({
        source: 'huggingface',
        sourceUrl: `https://huggingface.co/spaces/${space.id}`,
        title: `Space: ${space.id}`,
        description: space.description || '',
        category: 'ai',
        rawContent: `
Space名称: ${space.id}
点赞数: ${space.likes || 0}
SDK: ${space.sdk || '未知'}
更新时间: ${space.lastModified}
访问地址: https://huggingface.co/spaces/${space.id}
        `,
        metadata: {
          likes: space.likes,
          sdk: space.sdk
        }
      }))
    } catch (error) {
      console.error('HuggingFace Spaces采集失败:', error.message)
      return []
    }
  }
}

module.exports = new HuggingFaceCrawler()
