<!-- frontend\src\views\Register.vue -->
<template>
  <div class="auth-page">
    <div class="auth-box">
      <h2>Создать пространство</h2>
      <p class="subtitle">Начните принимать заявки и управлять событиями.</p>
      
      <form @submit.prevent="register">
        <div class="input-group">
          <label>Имя бренда (как вас увидят клиенты)</label>
          <input v-model="form.name" type="text" placeholder="Например: Женя Зонова" required />
        </div>

        <div class="input-group">
          <label>Ссылка (латиницей, без пробелов)</label>
          <input v-model="form.slug" type="text" placeholder="jenyaz" required />
          <span class="hint">Ваш сайт будет доступен по адресу: /{{ form.slug || 'slug' }}</span>
        </div>

        <div class="input-group">
          <label>Логин (для входа в панель)</label>
          <input v-model="form.username" type="text" placeholder="admin" required />
        </div>

        <div class="input-group">
          <label>Пароль</label>
          <input v-model="form.password" type="password" placeholder="••••••••" required />
        </div>
        <div class="input-group">
          <label>Ваш Email</label>
          <input v-model="form.email" type="email" placeholder="example@mail.ru" required />
        </div>
        <div class="input-group">
          <label>О себе (философия/миссия)</label>
          <textarea v-model="form.bio" placeholder="Игротехник и Хороводница..."></textarea>
        </div>

        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? 'Создание...' : 'Создать пространство' }}
        </button>
      </form>
      
      <p v-if="error" class="error">{{ error }}</p>
      <p class="auth-link">Уже есть аккаунт? <router-link to="/login">Войти</router-link></p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const form = reactive({ name: '', slug: '', username: '', password: '', bio: '', email: '' })

const register = async () => {
  loading.value = true
  error.value = ''
  try {
    // Отправляем данные на бэкенд
    const { data } = await api.post('/register/', form)
    
    // Если регистрация успешна, перенаправляем на страницу ожидания
    router.push({ 
      path: '/check-email', 
      query: { email: form.email, uid: data.uid } // uid можно вернуть с бэкенда
    })
  } catch (e) {
    error.value = e.response?.data?.error || 'Ошибка регистрации'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: var(--color-bg);
  padding: 20px;
}
.auth-box {
  background: white;
  padding: 40px;
  border-radius: 4px;
  border-top: 4px solid var(--color-accent);
  width: 100%;
  max-width: 480px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05);
}
.auth-box h2 {
  font-family: var(--font-serif);
  font-size: 2rem;
  margin-bottom: 5px;
}
.subtitle {
  color: var(--color-text-light);
  margin-bottom: 25px;
  font-size: 0.95rem;
}
.input-group {
  margin-bottom: 15px;
}
.input-group label {
  display: block;
  font-size: 0.85rem;
  color: var(--color-text-light);
  margin-bottom: 5px;
}
.input-group input, .input-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--color-gold);
  border-radius: 2px;
  font-family: var(--font-sans);
}
.input-group textarea {
  min-height: 80px;
  resize: vertical;
}
.hint {
  display: block;
  font-size: 0.75rem;
  color: #999;
  margin-top: 4px;
}
.btn-primary {
  width: 100%;
  background: var(--color-text);
  color: white;
  padding: 14px;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  margin-top: 10px;
}
.btn-primary:disabled {
  background: #ccc;
}
.error {
  color: var(--color-accent);
  margin-top: 15px;
  text-align: center;
}
.auth-link {
  text-align: center;
  margin-top: 20px;
  font-size: 0.9rem;
}
.auth-link a {
  color: var(--color-accent);
  font-weight: 500;
}
</style>