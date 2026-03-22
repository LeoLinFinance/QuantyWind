import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Trash2, Plus, Save, Eye, EyeOff } from 'lucide-react'

interface Provider {
  id: string
  name: string
  base_url: string
  models: string[]
  description: string
}

interface APIKey {
  id: string
  provider: string
  api_key_preview: string
  base_url?: string
  model?: string
  name?: string
  description?: string
  is_active: boolean
}

export default function SettingsPage() {
  const [providers, setProviders] = useState<Provider[]>([])
  const [apiKeys, setApiKeys] = useState<APIKey[]>([])
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)
  
  // 新增表单状态
  const [showAddForm, setShowAddForm] = useState(false)
  const [newKey, setNewKey] = useState({
    provider: '',
    api_key: '',
    base_url: '',
    model: '',
    name: '',
    description: ''
  })
  const [showApiKey, setShowApiKey] = useState(false)

  useEffect(() => {
    loadProviders()
    loadApiKeys()
  }, [])

  const loadProviders = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/api-keys/providers/list')
      const data = await response.json()
      setProviders(data.providers)
    } catch (error) {
      console.error('Failed to load providers:', error)
    }
  }

  const loadApiKeys = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/api-keys/')
      const data = await response.json()
      setApiKeys(data)
    } catch (error) {
      console.error('Failed to load API keys:', error)
    }
  }

  const handleAddKey = async () => {
    if (!newKey.provider || !newKey.api_key) {
      setMessage({ type: 'error', text: '请至少填写服务商和 API Key' })
      return
    }

    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/api-keys/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newKey)
      })

      if (response.ok) {
        setMessage({ type: 'success', text: 'API Key 添加成功' })
        setShowAddForm(false)
        setNewKey({
          provider: '',
          api_key: '',
          base_url: '',
          model: '',
          name: '',
          description: ''
        })
        loadApiKeys()
      } else {
        const error = await response.json()
        setMessage({ type: 'error', text: error.detail || '添加失败' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: '网络错误' })
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteKey = async (keyId: string) => {
    if (!confirm('确定要删除这个 API Key 吗？')) return

    setLoading(true)
    try {
      const response = await fetch(`http://localhost:8000/api/api-keys/${keyId}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        setMessage({ type: 'success', text: 'API Key 删除成功' })
        loadApiKeys()
      } else {
        setMessage({ type: 'error', text: '删除失败' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: '网络错误' })
    } finally {
      setLoading(false)
    }
  }

  const selectedProvider = providers.find(p => p.id === newKey.provider)

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <h1 className="text-3xl font-bold mb-6">系统设置</h1>

      {message && (
        <Alert className={`mb-4 ${message.type === 'error' ? 'border-red-500' : 'border-green-500'}`}>
          <AlertDescription>{message.text}</AlertDescription>
        </Alert>
      )}

      {/* API Key 管理 */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>AI 服务配置</CardTitle>
          <CardDescription>
            配置您自己的大模型 API Key，系统将优先使用您配置的密钥
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* 已有的 API Keys */}
          <div className="space-y-4 mb-6">
            {apiKeys.length === 0 ? (
              <p className="text-gray-500 text-center py-4">暂无配置的 API Key</p>
            ) : (
              apiKeys.map(key => (
                <div key={key.id} className="border rounded-lg p-4 flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="font-semibold">{key.name || providers.find(p => p.id === key.provider)?.name}</span>
                      <span className={`text-xs px-2 py-1 rounded ${key.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}`}>
                        {key.is_active ? '启用' : '禁用'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-1">API Key: {key.api_key_preview}</p>
                    {key.model && <p className="text-sm text-gray-600">模型: {key.model}</p>}
                    {key.description && <p className="text-sm text-gray-500 mt-2">{key.description}</p>}
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDeleteKey(key.id)}
                    disabled={loading}
                  >
                    <Trash2 className="h-4 w-4 text-red-500" />
                  </Button>
                </div>
              ))
            )}
          </div>

          {/* 添加新 Key 按钮 */}
          {!showAddForm && (
            <Button onClick={() => setShowAddForm(true)} className="w-full">
              <Plus className="h-4 w-4 mr-2" />
              添加 API Key
            </Button>
          )}

          {/* 添加表单 */}
          {showAddForm && (
            <div className="border rounded-lg p-4 space-y-4">
              <div>
                <Label>服务商 *</Label>
                <Select value={newKey.provider} onValueChange={(value) => {
                  const provider = providers.find(p => p.id === value)
                  setNewKey({
                    ...newKey,
                    provider: value,
                    base_url: provider?.base_url || '',
                    model: provider?.models[0] || ''
                  })
                }}>
                  <SelectTrigger>
                    <SelectValue placeholder="选择服务商" />
                  </SelectTrigger>
                  <SelectContent>
                    {providers.map(provider => (
                      <SelectItem key={provider.id} value={provider.id}>
                        {provider.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {selectedProvider && (
                  <p className="text-sm text-gray-500 mt-1">{selectedProvider.description}</p>
                )}
              </div>

              <div>
                <Label>API Key *</Label>
                <div className="relative">
                  <Input
                    type={showApiKey ? 'text' : 'password'}
                    value={newKey.api_key}
                    onChange={(e) => setNewKey({ ...newKey, api_key: e.target.value })}
                    placeholder="sk-..."
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0"
                    onClick={() => setShowApiKey(!showApiKey)}
                  >
                    {showApiKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
              </div>

              {selectedProvider && (
                <div>
                  <Label>模型</Label>
                  <Select value={newKey.model} onValueChange={(value) => setNewKey({ ...newKey, model: value })}>
                    <SelectTrigger>
                      <SelectValue placeholder="选择模型" />
                    </SelectTrigger>
                    <SelectContent>
                      {selectedProvider.models.map(model => (
                        <SelectItem key={model} value={model}>
                          {model}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}

              <div>
                <Label>配置名称（可选）</Label>
                <Input
                  value={newKey.name}
                  onChange={(e) => setNewKey({ ...newKey, name: e.target.value })}
                  placeholder="例如：我的 StepFun Key"
                />
              </div>

              <div>
                <Label>描述（可选）</Label>
                <Textarea
                  value={newKey.description}
                  onChange={(e) => setNewKey({ ...newKey, description: e.target.value })}
                  placeholder="备注信息"
                  rows={2}
                />
              </div>

              <div className="flex gap-2">
                <Button onClick={handleAddKey} disabled={loading} className="flex-1">
                  <Save className="h-4 w-4 mr-2" />
                  保存
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowAddForm(false)
                    setNewKey({
                      provider: '',
                      api_key: '',
                      base_url: '',
                      model: '',
                      name: '',
                      description: ''
                    })
                  }}
                  disabled={loading}
                >
                  取消
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 使用说明 */}
      <Card>
        <CardHeader>
          <CardTitle>使用说明</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="font-semibold mb-2">如何获取 API Key？</h3>
            <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
              <li>阶跃星辰：访问 <a href="https://platform.stepfun.com" target="_blank" className="text-blue-500 hover:underline">platform.stepfun.com</a> 注册并获取</li>
              <li>Kimi：访问 <a href="https://platform.moonshot.cn" target="_blank" className="text-blue-500 hover:underline">platform.moonshot.cn</a> 注册并获取</li>
              <li>OpenAI：访问 <a href="https://platform.openai.com" target="_blank" className="text-blue-500 hover:underline">platform.openai.com</a> 注册并获取</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold mb-2">安全提示</h3>
            <p className="text-sm text-gray-600">
              您的 API Key 将被加密存储在本地数据库中，不会被上传到任何第三方服务器。
              请妥善保管您的 API Key，不要分享给他人。
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
