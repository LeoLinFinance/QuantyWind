const axios = require('axios')

async function testNewKey() {
  const apiKey = 'sk-lFxuEqj2Ke57WONHYzewESJhEKAAiU11ftadXRiRRN5i35lk'
  
  console.log('测试新的 API Key...')
  console.log('Key 前缀:', apiKey.substring(0, 20) + '...')
  console.log('Key 长度:', apiKey.length)
  
  // 测试 Kimi API
  console.log('\n尝试 Kimi API (Moonshot)...')
  try {
    const response = await axios.post(
      'https://api.moonshot.cn/v1/chat/completions',
      {
        model: 'moonshot-v1-32k',
        messages: [
          { role: 'user', content: '你好，请简单介绍一下你自己' }
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
    
    console.log('✅ Kimi API 测试成功!')
    console.log('模型:', response.data.model)
    console.log('回复:', response.data.choices[0].message.content)
    return 'kimi'
  } catch (error) {
    console.error('❌ Kimi API 失败:')
    if (error.response) {
      console.error('状态码:', error.response.status)
      console.error('错误:', error.response.data)
    } else {
      console.error('错误:', error.message)
    }
  }
  
  // 测试其他可能的 API
  console.log('\n尝试 OpenAI 兼容 API...')
  try {
    const response = await axios.post(
      'https://api.openai.com/v1/chat/completions',
      {
        model: 'gpt-3.5-turbo',
        messages: [
          { role: 'user', content: '你好' }
        ]
      },
      {
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        },
        timeout: 30000
      }
    )
    
    console.log('✅ OpenAI API 测试成功!')
    console.log('回复:', response.data.choices[0].message.content)
    return 'openai'
  } catch (error) {
    console.error('❌ OpenAI API 失败:')
    if (error.response) {
      console.error('状态码:', error.response.status)
    } else {
      console.error('错误:', error.message)
    }
  }
  
  return null
}

testNewKey().then(result => {
  if (result) {
    console.log(`\n✅ 该密钥可用于: ${result}`)
  } else {
    console.log('\n❌ 该密钥无法使用')
  }
})
