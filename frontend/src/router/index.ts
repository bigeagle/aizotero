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
      path: '/read/:id',
      name: 'paper-reader',
      component: () => import('@/views/PaperReader.vue'),
    },
  ],
});

export default router;
