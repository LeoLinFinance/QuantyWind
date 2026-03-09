const app = getApp()

Page({
  data: {
    categories: [
      { id: 'all', name: '全部' },
      { id: 'ai', name: 'AI世界模型' },
      { id: 'embodied', name: '具身智能' },
      { id: 'quantum', name: '量子计算' },
      { id: 'bci', name: '脑机接口' },
      { id: 'chip', name: '芯片架构' },
      { id: 'biotech', name: '生物医疗' }
    ],
    currentCategory: 'all',
    articles: [],
    page: 1,
    pageSize: 10,
    loading: false,
    noMore: false
  },

  onLoad() {
    this.loadArticles()
  },

  onCategoryChange(e) {
    const categoryId = e.currentTarget.dataset.id
    this.setData({
      currentCategory: categoryId,
      articles: [],
      page: 1,
      noMore: false
    })
    this.loadArticles()
  },

  loadArticles() {
    if (this.data.loading || this.data.noMore) return

    this.setData({ loading: true })

    wx.request({
      url: `${app.globalData.apiBase}/articles`,
      data: {
        category: this.data.currentCategory,
        page: this.data.page,
        pageSize: this.data.pageSize
      },
      success: (res) => {
        if (res.data.success) {
          const newArticles = res.data.data
          this.setData({
            articles: [...this.data.articles, ...newArticles],
            page: this.data.page + 1,
            noMore: newArticles.length < this.data.pageSize
          })
        }
      },
      fail: (err) => {
        wx.showToast({ title: '加载失败', icon: 'none' })
      },
      complete: () => {
        this.setData({ loading: false })
      }
    })
  },

  loadMore() {
    this.loadArticles()
  },

  goToDetail(e) {
    const articleId = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/detail/detail?id=${articleId}`
    })
  },

  goToSearch() {
    wx.navigateTo({
      url: '/pages/search/search'
    })
  },

  onPullDownRefresh() {
    this.setData({
      articles: [],
      page: 1,
      noMore: false
    })
    this.loadArticles()
    wx.stopPullDownRefresh()
  }
})
