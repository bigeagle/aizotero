import { createRouter, createWebHistory } from 'vue-router';
import PaperList from '@/views/PaperList.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'paper-list',
      component: PaperList,
    },
    {
      path: '/read/zotero/:id',
      name: 'paper-reader-zotero',
      component: () => import('@/views/PaperReader.vue'),
      props: { source: 'zotero' },
    },
    {
      path: '/read/arxiv/:id',
      name: 'paper-reader-arxiv',
      component: () => import('@/views/PaperReader.vue'),
      props: { source: 'arxiv' },
    },
  ],
});

export default router;
