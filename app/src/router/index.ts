import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';

const Main = () => import(/* webpackChunkName: "main" */ '@/views/Main.vue');

const routes: Array<RouteRecordRaw> = [
  { path: '/', name: 'Main', component: Main },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
