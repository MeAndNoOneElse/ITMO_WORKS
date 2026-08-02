import { createRouter, createWebHistory } from 'vue-router';
import { isLoggedIn } from '../services/authService';
import LoginView from '../views/LoginView.vue';
import RegisterView from '../views/RegisterView.vue';
import MainView from '../views/MainView.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', component: LoginView },
    { path: '/register', component: RegisterView },
    {
      path: '/main',
      component: MainView,
      beforeEnter: (_to, _from, next) => {
        if (isLoggedIn()) {
          next();
        } else {
          next('/login');
        }
      }
    }
  ]
});

export default router;

