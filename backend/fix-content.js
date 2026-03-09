require('dotenv').config()
const { db, ArticleDB } = require('./database')

console.log('🔧 开始修复文章内容格式...\n')

// 清理JSON格式的内容
function cleanJSONContent(content) {
    if (!content) return content
    
    let cleaned = content.trim()
    
    // 如果以 { 开头，尝试提取实际内容
    if (cleaned.startsWith('{') || cleaned.startsWith('```json')) {
        try {
            // 移除markdown代码块
            cleaned = cleaned.replace(/```json\s*/g, '').replace(/```\s*/g, '')
            
            // 尝试解析JSON
            const jsonMatch = cleaned.match(/\{[\s\S]*\}/)
            if (jsonMatch) {
                const parsed = JSON.parse(jsonMatch[0])
                
                // 提取content字段
                if (parsed.content) {
                    cleaned = parsed.content
                } else if (parsed.layers && Array.isArray(parsed.layers)) {
                    // 如果有layers，提取第一个的content
                    const firstLayer = parsed.layers.find(l => l.content)
                    if (firstLayer) {
                        cleaned = firstLayer.content
                    }
                }
            }
        } catch (e) {
            // JSON解析失败，尝试提取summary字段
            const summaryMatch = cleaned.match(/"summary":\s*"([^"]+)"/)
            if (summaryMatch) {
                cleaned = summaryMatch[1]
                console.log('  ℹ️  使用summary字段作为内容')
            } else {
                // 如果都失败了，移除JSON标记，保留文本
                cleaned = cleaned.replace(/^\{[\s\S]*?"summary":\s*"/, '')
                cleaned = cleaned.replace(/"[\s\S]*$/, '')
                console.log('  ℹ️  提取部分文本内容')
            }
        }
    }
    
    // 清理转义字符
    cleaned = cleaned.replace(/\\n/g, '\n')
    cleaned = cleaned.replace(/\\"/g, '"')
    cleaned = cleaned.replace(/\\t/g, '\t')
    
    return cleaned
}

// 获取所有文章
const stmt = db.prepare('SELECT * FROM articles ORDER BY id')
const articles = stmt.all()

let fixedCount = 0
let skippedCount = 0

console.log(`📊 共有 ${articles.length} 篇文章需要检查\n`)

articles.forEach(article => {
    let needsUpdate = false
    const updates = {}
    
    // 检查并修复concept
    if (article.concept && article.concept.startsWith('{')) {
        const cleaned = cleanJSONContent(article.concept)
        if (cleaned !== article.concept) {
            updates.concept = cleaned
            needsUpdate = true
            console.log(`  🔧 修复文章 ${article.id} 的concept层`)
        }
    }
    
    // 检查并修复principle
    if (article.principle && article.principle.startsWith('{')) {
        const cleaned = cleanJSONContent(article.principle)
        if (cleaned !== article.principle) {
            updates.principle = cleaned
            needsUpdate = true
            console.log(`  🔧 修复文章 ${article.id} 的principle层`)
        }
    }
    
    // 检查并修复implementation
    if (article.implementation && article.implementation.startsWith('{')) {
        const cleaned = cleanJSONContent(article.implementation)
        if (cleaned !== article.implementation) {
            updates.implementation = cleaned
            needsUpdate = true
            console.log(`  🔧 修复文章 ${article.id} 的implementation层`)
        }
    }
    
    // 检查并修复application
    if (article.application && article.application.startsWith('{')) {
        const cleaned = cleanJSONContent(article.application)
        if (cleaned !== article.application) {
            updates.application = cleaned
            needsUpdate = true
            console.log(`  🔧 修复文章 ${article.id} 的application层`)
        }
    }
    
    // 如果需要更新，执行更新
    if (needsUpdate) {
        const updateFields = []
        const updateValues = []
        
        if (updates.concept) {
            updateFields.push('concept = ?')
            updateValues.push(updates.concept)
        }
        if (updates.principle) {
            updateFields.push('principle = ?')
            updateValues.push(updates.principle)
        }
        if (updates.implementation) {
            updateFields.push('implementation = ?')
            updateValues.push(updates.implementation)
        }
        if (updates.application) {
            updateFields.push('application = ?')
            updateValues.push(updates.application)
        }
        
        updateValues.push(article.id)
        
        const updateStmt = db.prepare(`
            UPDATE articles 
            SET ${updateFields.join(', ')}
            WHERE id = ?
        `)
        
        try {
            updateStmt.run(...updateValues)
            fixedCount++
            console.log(`  ✅ 文章 ${article.id} 修复完成`)
        } catch (error) {
            console.error(`  ❌ 文章 ${article.id} 修复失败:`, error.message)
        }
    } else {
        skippedCount++
    }
})

console.log('\n' + '='.repeat(50))
console.log('📊 修复统计:')
console.log(`  ✅ 已修复: ${fixedCount} 篇`)
console.log(`  ⏭️  跳过: ${skippedCount} 篇`)
console.log(`  📈 总计: ${articles.length} 篇`)
console.log('='.repeat(50))

// 验证修复结果
console.log('\n🔍 验证修复结果...\n')

const verifyStmt = db.prepare(`
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN concept LIKE '{%' THEN 1 ELSE 0 END) as concept_json,
        SUM(CASE WHEN principle LIKE '{%' THEN 1 ELSE 0 END) as principle_json,
        SUM(CASE WHEN implementation LIKE '{%' THEN 1 ELSE 0 END) as impl_json,
        SUM(CASE WHEN application LIKE '{%' THEN 1 ELSE 0 END) as app_json
    FROM articles
`)

const result = verifyStmt.get()

console.log('📊 当前状态:')
console.log(`  总文章数: ${result.total}`)
console.log(`  concept有JSON格式: ${result.concept_json}`)
console.log(`  principle有JSON格式: ${result.principle_json}`)
console.log(`  implementation有JSON格式: ${result.impl_json}`)
console.log(`  application有JSON格式: ${result.app_json}`)

if (result.concept_json === 0 && result.principle_json === 0 && 
    result.impl_json === 0 && result.app_json === 0) {
    console.log('\n✅ 所有JSON格式问题已修复！')
} else {
    console.log('\n⚠️  仍有部分文章存在JSON格式问题')
}

console.log('\n✅ 修复完成！')
