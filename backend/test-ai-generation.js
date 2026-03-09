require('dotenv').config()
const aiService = require('./services/aiService')

async function testAIGeneration() {
  console.log('测试AI内容生成...\n')
  
  const testPaper = `
论文标题: RoboPocket: Improve Robot Policies Instantly with Your Phone
分类: AI与机器学习
摘要: Scaling imitation learning is fundamentally constrained by the efficiency of data collection. While handheld interfaces have emerged as a scalable solution for in-the-wild data acquisition, they predominantly rely on teleoperation, which is slow and cognitively demanding.
  `
  
  try {
    console.log('调用AI生成内容...')
    const result = await aiService.generateContent(testPaper, 'ai')
    
    console.log('\n✅ AI生成成功!')
    console.log('生成内容长度:', result.length, '字符')
    console.log('\n前500字符:')
    console.log(result.substring(0, 500))
    console.log('...')
    
  } catch (error) {
    console.error('\n❌ AI生成失败:')
    console.error(error.message)
  }
}

testAIGeneration()
