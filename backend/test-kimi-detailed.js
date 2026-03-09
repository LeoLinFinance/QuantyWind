require('dotenv').config()
const axios = require('axios')

async function testKimiDetailed() {
  const apiKey = process.env.KIMI_API_KEY
  console.log('Kimi API Key:', apiKey.substring(0, 20) + '...')
  console.log('API Key 长度:', apiKey.length)
  
  // 测试不同的模型
  const models = ['moonshot-v1-8k', 'moonshot-v1-32k', 'moonshot-v1-128k']
  
  for (const model of models) {
    console.log(`\n测试模型: ${model}`)
    
    try {
      const response = await axios.post(
        'https://api.moonshot.cn/v1/chat/completions',
        {
          model: model,
          messages: [
            { role: 'user', content: '你好' }
          ],
          temperature: 0.3
        },
        {
          headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
          },
          timeout: 30000
        }
      )
      
      console.log(`✅ ${model} 成功!`)
      console.log('回复:', response.data.choices[0].message.content)
      return true
    } catch (error) {
      console.error(`❌ ${model} 失败:`)
      if (error.response) {
        console.error('状态码:', error.response.status)
        console.error('错误信息:', JSON.stringify(error.response.data, null, 2))
      } else {
        console.error('错误:', error.message)
      }
    }
  }
  
  return false
}

testKimiDetailed()
