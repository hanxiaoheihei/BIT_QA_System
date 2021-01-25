import Vue from 'vue';
import Router from 'vue-router';
import Home from './views/Home.vue';

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home,
    },
    {
      path: '/docs',
      name: 'docs',
      component: () => import('./views/Docs.vue'),
    },
    {
      path: '/faqs',
      name: 'faqs',
      component: () => import('./views/Faqs.vue'),
    },
    {
      path: '/sort',
      name: 'Sort',
      component: () => import('./views/Sort.vue'),
    },
    {
      path: '/sort2',
      name: 'Sort2',
      component: () => import('./views/Sort2.vue'),
    }
  ],
});
