import { createRouter, createWebHistory } from 'vue-router'
import LandingPage from '../views/LandingPage.vue'
import PublicSite from '../views/PublicSite.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Dashboard from '../views/Dashboard.vue'
import InviteResponse from '../views/InviteResponse.vue'
import VerifyEmail from '../views/VerifyEmail.vue'
import CheckEmail from '../views/CheckEmail.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // 1. Главная страница SaaS (презентация сервиса)
    { path: '/', component: LandingPage },
    
    // 2. Статичные маршруты
    { path: '/register', component: Register },
    { path: '/login', component: Login },
    { path: '/dashboard', component: Dashboard, meta: { requiresAuth: true } },
    { path: '/invite/:token', component: InviteResponse },
    { path: '/verify-email/:uid/:token', component: VerifyEmail },
    { path: '/check-email', component: CheckEmail },
    
    // 3. Динамический маршрут (сайт конкретной Жени)
    { path: '/:slug', component: PublicSite },
  ]
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) next('/login')
  else next()
})
router.afterEach((to, from) => {
  // Если мы перешли на публичную страницу (динамический slug)
  if (to.params.slug) {
    // Пока данные грузятся, ставим дефолтный заголовок
    document.title = 'Загрузка...'
    
    // Мы не знаем имени организатора на этом этапе, 
    // поэтому в компоненте PublicSite.vue мы изменим заголовок после загрузки данных.
  } 
  // Если мы на главной странице SaaS
  else if (to.path === '/') {
    document.title = 'Пространство развития | Создай свой сайт'
  }
  // Для остальных страниц (логин, регистрация, панель)
  else {
    document.title = 'Личный кабинет'
  }
})
export default router