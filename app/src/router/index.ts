import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import { BASE_URL } from '@/utils/config';

const Layout = () =>
  import(/* webpackChunkName: "layout" */ '@/views/Layout.vue');
const ErrorPage = () =>
  import(/* webpackChunkName: "not-found" */ '@/views/ErrorPage.vue');

const routes: Array<RouteRecordRaw> = [
  {
    path: '/files/:pathMatch(.*)*',
    name: 'Layout',
    component: Layout,
    beforeEnter: (to, _from, next) => {
      // Add a trailing slash if not exist
      if (to.path.endsWith('/')) {
        next();
      } else {
        next({
          path: `${to.path}/`,
          replace: true,
        });
      }
    },
  },
  {
    path: '/error',
    name: 'ErrorPage',
    component: ErrorPage,
    props: true,
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
