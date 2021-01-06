import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import { BASE_URL } from '@/utils/config';

const Layout = () =>
  import(/* webpackChunkName: "layout" */ '@/views/Layout.vue');
const NotFound = () =>
  import(/* webpackChunkName: "not-found" */ '@/views/NotFound.vue');

const routes: Array<RouteRecordRaw> = [
  {
    path: '/files/:pathMatch(.*)*/',
    name: 'Layout',
    component: Layout,
  },
  {
    path: '/404',
    name: 'NotFound',
    component: NotFound,
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: { name: 'Layout' },
  },
];

const router = createRouter({
  history: createWebHistory(BASE_URL),
  routes,
});

export default router;
