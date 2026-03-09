require('dotenv').config()
const axios = require('axios')

async function testStepFun() {
  console.log('测试阶跃星辰API...')
  
  try {
    const response = await axios.post(
      'https://api.stepfun.com/v1/chat/completions',
      {
        model: 'step-1-32k',
        messages: [
          { role: 'user', content: '你好，请用一句话介绍你自己' }
        ]
      },
      {
        headers: {
          'Authorization': `Bearer ${process.env.STEPFUN_API_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    )
    
    console.log('✅ 阶跃星辰API测试成功!')
    console.log('回复:', response.data.choices[0].message.content)
    return true
  } catch (error) {
    console.error('❌ 阶跃星辰API测试失败:')
    console.error('错误:', error.response?.data || error.message)
    return false
  }
}

async function testKimi() {
  console.log('\n测试Kimi API...')
  
  try {
    const response = await axios.post(
      'https://api.moonshot.cn/v1/chat/completions',
      {
        model: 'moonshot-v1-32k',
        messages: [
          { role: 'user', content: '你好，请用一句话介绍你自己' }
        ]
      },
      {
        headers: {
          'Authorization': `Bearer ${process.env.KIMI_API_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    )
    
    console.log('✅ Kimi API测试成功!')
    console.log('回复:', response.data.choices[0].message.content)
    return true
  } catch (error) {
    console.error('❌ Kimi API测试失败:')
    console.error('错误:', error.response?.data || error.message)
    return false
  }
}

async function main() {
  const stepfunOk = await testStepFun()
  const kimiOk = await testKimi()
  
  console.log('\n========================================')
  console.log('测试结果:')
  console.log(`阶跃星辰: ${stepfunOk ? '✅ 可用' : '❌ 不可用'}`)
  console.log(`Kimi: ${kimiOk ? '✅ 可用' : '❌ 不可用'}`)
  console.log('========================================')
}

main()
