const Database = require('better-sqlite3');
const fs = require('fs');
const path = require('path');

console.log('📦 开始导出静态数据...');

try {
    const db = new Database('./data/didaxueshu.db', { readonly: true });
    console.log('✅ 数据库连接成功');
    
    const rows = db.prepare('SELECT * FROM articles ORDER BY createdAt DESC').all();
    console.log(`📊 查询到 ${rows.length} 篇文章`);
    
    // 转换为前端需要的格式
    const articles = rows.map(row => {
        return {
            id: row.id,
            title: row.title,
            category: row.category,
            source: row.source,
            sourceUrl: row.sourceUrl,
            summary: row.summary,
            views: row.views || 0,
            likes: row.likes || 0,
            shares: row.shares || 0,
            publishTime: row.publishTime,
            createdAt: row.createdAt,
            // 将4个字段转换为layers数组
            layers: [
                { level: 'concept', content: row.concept || '' },
                { level: 'principle', content: row.principle || '' },
                { level: 'implementation', content: row.implementation || '' },
                { level: 'application', content: row.application || '' }
            ]
        };
    });
    
    // 保存为JSON
    const outputPath = path.join(__dirname, '../demo-web/data.json');
    fs.writeFileSync(outputPath, JSON.stringify(articles, null, 2), 'utf-8');
    
    console.log(`✅ 成功导出 ${articles.length} 篇文章到 ${outputPath}`);
    
    // 统计信息
    const stats = {};
    articles.forEach(a => {
        stats[a.category] = (stats[a.category] || 0) + 1;
    });
    
    console.log('\n📈 分类统计:');
    Object.entries(stats).forEach(([cat, count]) => {
        console.log(`   ${cat}: ${count}篇`);
    });
    
    console.log(`\n💾 文件大小: ${(fs.statSync(outputPath).size / 1024).toFixed(2)} KB`);
    
    db.close();
    console.log('\n✅ 导出完成！');
} catch (err) {
    console.error('❌ 导出失败:', err.message);
    process.exit(1);
}
