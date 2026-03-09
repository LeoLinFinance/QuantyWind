const app = getApp()

Page({
  data: {
    articleId: '',
    article: {},
    layers: [
      { name: '概念', key: 'concept' },
      { name: '原理', key: 'principle' },
      { name: '实现', key: 'implementation' },
      { name: '应用', key: 'application' }
    ],
    currentLayer: 0,
    currentContent: '',
    isPlaying: false,
    progress: 0,
    currentTime: '00:00',
    totalTime: '00:00',
    isFavorited: false,
    chatMessages: [],
    inputText: '',
    audioContext: null
  },

  onLoad(options) {
    this.setData({ articleId: options.id })
    this.loadArticle()
    this.checkFavoriteStatus()
    this.initAudio()
  },

  loadArticle() {
    wx.showLoading({ title: '加载中' })
    wx.request({
      url: `${app.globalData.apiBase}/articles/${this.data.articleId}`,
      success: (res) => {
        if (res.data.success) {
          const article = res.data.data
          this.setData({
            article,
            currentContent: article.layers[0].content
          })
        }
      },
      fail: () => {
        wx.showToast({ title: '加载失败', icon: 'none' })
      },
      complete: () => {
        wx.hideLoading()
      }
    })
  },

  switchLayer(e) {
    const index = e.currentTarget.dataset.index
    this.setData({
      currentLayer: index,
      currentContent: this.data.article.layers[index].content
    })
  },

  initAudio() {
    const audioContext = wx.createInnerAudioContext()
    audioContext.onPlay(() => {
      this.setData({ isPlaying: true })
    })
    audioContext.onPause(() => {
      this.setData({ isPlaying: false })
    })
    audioContext.onTimeUpdate(() => {
      const progress = (audioContext.currentTime / audioContext.duration) * 100
      this.setData({
        progress,
        currentTime: this.formatTime(audioContext.currentTime),
        totalTime: this.formatTime(audioContext.duration)
      })
    })
    this.setData({ audioContext })
  },

  togglePlay() {
    const { audioContext, article } = this.data
    if (!audioContext.src) {
      audioContext.src = article.audioUrl
    }
    if (this.data.isPlaying) {
      audioContext.pause()
    } else {
      audioContext.play()
    }
  },

  onProgressChange(e) {
    const { audioContext } = this.data
    const progress = e.detail.value
    audioContext.seek((progress / 100) * audioContext.duration)
  },

  formatTime(seconds) {
    if (!seconds || isNaN(seconds)) return '00:00'
    const min = Math.floor(seconds / 60)
    const sec = Math.floor(seconds % 60)
    return `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`
  },

  checkFavoriteStatus() {
    const favorites = wx.getStorageSync('favorites') || []
    this.setData({
      isFavorited: favorites.includes(this.data.articleId)
    })
  },

  toggleFavorite() {
    let favorites = wx.getStorageSync('favorites') || []
    const { articleId, isFavorited } = this.data
    
    if (isFavorited) {
      favorites = favorites.filter(id => id !== articleId)
      wx.showToast({ title: '已取消收藏', icon: 'none' })
    } else {
      favorites.push(articleId)
      wx.showToast({ title: '收藏成功', icon: 'success' })
    }
    
    wx.setStorageSync('favorites', favorites)
    this.setData({ isFavorited: !isFavorited })
  },

  onInput(e) {
    this.setData({ inputText: e.detail.value })
  },

  sendMessage() {
    const { inputText, chatMessages, articleId } = this.data
    if (!inputText.trim()) return

    const userMessage = { role: 'user', content: inputText }
    this.setData({
      chatMessages: [...chatMessages, userMessage],
      inputText: ''
    })

    wx.request({
      url: `${app.globalData.apiBase}/chat`,
      method: 'POST',
      data: {
        articleId,
        message: inputText,
        history: chatMessages
      },
      success: (res) => {
        if (res.data.success) {
          const aiMessage = { role: 'assistant', content: res.data.data.reply }
          this.setData({
            chatMessages: [...this.data.chatMessages, aiMessage]
          })
        }
      }
    })
  },

  shareArticle() {
    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage', 'shareTimeline']
    })
  },

  onShareAppMessage() {
    return {
      title: this.data.article.title,
      path: `/pages/detail/detail?id=${this.data.articleId}`
    }
  },

  onUnload() {
    if (this.data.audioContext) {
      this.data.audioContext.destroy()
    }
  }
})
