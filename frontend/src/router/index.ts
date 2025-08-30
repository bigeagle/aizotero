import { createRouter, createWebHistory } from 'vue-router';
import PaperList from '@/views/PaperList.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'paper-list',
      component: PaperList,
      meta: { title: '论文列表 - AI论文助手' },
    },
    {
      path: '/read/zotero/:id',
      name: 'paper-reader-zotero',
      component: () => import('@/views/PaperReader.vue'),
      props: (route) => ({ source: 'zotero', paperId: route.params.id }),
      meta: { title: '论文阅读 - AI论文助手' },
    },
    {
      path: '/read/arxiv/:id',
      name: 'paper-reader-arxiv',
      component: () => import('@/views/PaperReader.vue'),
      props: (route) => ({ source: 'arxiv', paperId: route.params.id }),
      meta: { title: '论文阅读 - AI论文助手' },
    },
  ],
});

// 全局路由守卫，设置网页标题
router.beforeEach((to, from, next) => {
  if (to.meta?.title) {
    document.title = to.meta.title as string;
  }
  next();
});

export default router;
