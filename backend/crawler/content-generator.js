// 基于论文实际内容的深度解读生成器

const categoryNames = {
  'ai': 'AI与机器学习',
  'quantum': '量子计算',
  'bci': '脑机接口',
  'chip': '芯片架构',
  'embodied': '具身智能',
  'biotech': '生物医疗'
}

// 从摘要中提取关键短语
function extractKeyPhrases(text) {
  const keywords = [
    'learning', 'model', 'algorithm', 'network', 'optimization',
    'training', 'performance', 'efficient', 'novel', 'framework',
    'method', 'approach', 'system', 'architecture', 'design'
  ]
  
  const found = []
  keywords.forEach(kw => {
    if (text.toLowerCase().includes(kw)) {
      found.push(kw)
    }
  })
  return found.slice(0, 5)
}

// 生成概念层内容
function generateConceptLayer(paper) {
  const authors = paper.metadata?.authors || ['研究团队']
  const authorList = authors.slice(0, 3).join(', ') + (authors.length > 3 ? ' 等' : '')
  const abstract = paper.description
  
  // 将摘要分成几个部分
  const sentences = abstract.match(/[^.!?]+[.!?]+/g) || [abstract]
  const intro = sentences.slice(0, 2).join(' ')
  const problem = sentences.slice(2, 4).join(' ') || abstract
  const contribution = sentences.slice(4).join(' ') || '本研究提出了创新的解决方案。'
  
  return `
<div class="paper-header">
  <h2>📄 论文概览</h2>
  <div class="meta-info">
    <p><strong>作者：</strong>${authorList}</p>
    <p><strong>发表时间：</strong>${paper.metadata?.published || '2024'}</p>
    <p><strong>研究领域：</strong>${categoryNames[paper.category]}</p>
    <p><strong>arXiv分类：</strong>${paper.metadata?.arxivCategory || 'cs.AI'}</p>
  </div>
</div>

<h2>🎯 研究背景与动机</h2>
<p>${intro}</p>

<h3>核心问题 (Core Problem)</h3>
<p>${problem}</p>

<h3>主要贡献</h3>
<p>${contribution}</p>

<h3>研究意义</h3>
<ul>
  <li><strong>理论贡献：</strong>为${categoryNames[paper.category]}领域提供了新的理论框架和分析方法</li>
  <li><strong>实践价值：</strong>提出的方法可以直接应用于实际系统，提升性能指标</li>
  <li><strong>创新点：</strong>在方法论、算法设计、系统架构等方面都有显著创新</li>
</ul>
`
}

module.exports = {
  generateConceptLayer,
  categoryNames
}
