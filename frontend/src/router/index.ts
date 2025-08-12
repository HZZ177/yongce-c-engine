import { createRouter, createWebHistory } from 'vue-router'
import CloseApp from '@/views/CloseApp.vue'
import RoadApp from '@/views/RoadApp.vue'

const routes = [
  {
    path: '/',
    redirect: '/close'
  },
  {
    path: '/close',
    name: 'CloseApp',
    component: CloseApp,
    meta: {
      title: '封闭车场管理'
    }
  },
  {
    path: '/road',
    name: 'RoadApp',
    component: RoadApp,
    meta: {
      title: '路侧车场管理'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 永策C端引擎测试工具` : '永策C端引擎测试工具'
  next()
})

export default router 