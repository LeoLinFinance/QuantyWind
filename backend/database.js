const Database = require('better-sqlite3')
const path = require('path')
const fs = require('fs')

// 确保数据目录存在
const dataDir = path.join(__dirname, 'data')
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true })
}

const dbPath = path.join(dataDir, 'didaxueshu.db')
const db = new Database(dbPath)

// 创建表
db.exec(`
  CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    source TEXT NOT NULL,
    sourceUrl TEXT NOT NULL,
    summary TEXT NOT NULL,
    concept TEXT,
    principle TEXT,
    implementation TEXT,
    application TEXT,
    audioUrl TEXT,
    duration TEXT,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    publishTime TEXT,
    crawledAt TEXT,
    contentHash TEXT UNIQUE,
    tags TEXT,
    createdAt TEXT DEFAULT CURRENT_TIMESTAMP
  );

  CREATE INDEX IF NOT EXISTS idx_category ON articles(category);
  CREATE INDEX IF NOT EXISTS idx_contentHash ON articles(contentHash);
  CREATE INDEX IF NOT EXISTS idx_publishTime ON articles(publishTime);
`)

// 数据库操作方法
const ArticleDB = {
  // 插入文章
  insert(article) {
    const stmt = db.prepare(`
      INSERT INTO articles (
        title, category, source, sourceUrl, summary,
        concept, principle, implementation, application,
        audioUrl, duration, publishTime, crawledAt, contentHash, tags
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `)
    
    try {
      const info = stmt.run(
        article.title,
        article.category,
        article.source,
        article.sourceUrl,
        article.summary,
        article.concept,
        article.principle,
        article.implementation,
        article.application,
        article.audioUrl || null,
        article.duration || null,
        article.publishTime,
        article.crawledAt,
        article.contentHash,
        JSON.stringify(article.tags || [])
      )
      return info.lastInsertRowid
    } catch (error) {
      if (error.message.includes('UNIQUE constraint failed')) {
        console.log(`  ⚠️  文章已存在: ${article.title.substring(0, 50)}...`)
        return null
      }
      throw error
    }
  },

  // 查询所有文章
  findAll(category = 'all', page = 1, pageSize = 10) {
    const offset = (page - 1) * pageSize
    let query = 'SELECT * FROM articles'
    let params = []
    
    if (category !== 'all') {
      query += ' WHERE category = ?'
      params.push(category)
    }
    
    query += ' ORDER BY publishTime DESC LIMIT ? OFFSET ?'
    params.push(pageSize, offset)
    
    const stmt = db.prepare(query)
    return stmt.all(...params).map(this.formatArticle)
  },

  // 根据ID查询
  findById(id) {
    const stmt = db.prepare('SELECT * FROM articles WHERE id = ?')
    const article = stmt.get(id)
    return article ? this.formatArticle(article) : null
  },

  // 搜索
  search(keyword, page = 1, pageSize = 10) {
    const offset = (page - 1) * pageSize
    const stmt = db.prepare(`
      SELECT * FROM articles 
      WHERE title LIKE ? OR summary LIKE ?
      ORDER BY publishTime DESC 
      LIMIT ? OFFSET ?
    `)
    const pattern = `%${keyword}%`
    return stmt.all(pattern, pattern, pageSize, offset).map(this.formatArticle)
  },

  // 检查是否存在
  existsByHash(hash) {
    const stmt = db.prepare('SELECT id FROM articles WHERE contentHash = ?')
    return stmt.get(hash) !== undefined
  },

  // 统计
  count(category = 'all') {
    let query = 'SELECT COUNT(*) as count FROM articles'
    let params = []
    
    if (category !== 'all') {
      query += ' WHERE category = ?'
      params.push(category)
    }
    
    const stmt = db.prepare(query)
    return stmt.get(...params).count
  },

  // 分类统计
  countByCategory() {
    const stmt = db.prepare(`
      SELECT category, COUNT(*) as count 
      FROM articles 
      GROUP BY category
    `)
    return stmt.all()
  },

  // 格式化文章（转换为前端需要的格式）
  formatArticle(row) {
    return {
      id: row.id.toString(),
      title: row.title,
      category: row.category,
      source: row.source,
      sourceUrl: row.sourceUrl,
      summary: row.summary,
      layers: [
        { level: 'concept', content: row.concept || '' },
        { level: 'principle', content: row.principle || '' },
        { level: 'implementation', content: row.implementation || '' },
        { level: 'application', content: row.application || '' }
      ],
      audioUrl: row.audioUrl,
      duration: row.duration,
      views: row.views,
      likes: row.likes,
      shares: row.shares,
      publishTime: row.publishTime,
      hasAudio: !!row.audioUrl,
      tags: row.tags ? JSON.parse(row.tags) : []
    }
  },

  // 增加浏览量
  incrementViews(id) {
    const stmt = db.prepare('UPDATE articles SET views = views + 1 WHERE id = ?')
    stmt.run(id)
  }
}

module.exports = { db, ArticleDB }
