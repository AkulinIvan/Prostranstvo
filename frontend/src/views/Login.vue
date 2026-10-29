<!-- frontend\src\views\Login.vue -->
<template>
  <div class="login-page">
    <div class="login-box">
      <h2>Вход для организатора</h2>
      <form @submit.prevent="login">
        <input v-model="username" placeholder="Логин" required />
        <input v-model="password" type="password" placeholder="Пароль" required />
        <button type="submit" class="btn-primary">Войти</button>
      </form>
      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'

const username = ref('')
const password = ref('')
const error = ref('')
const router = useRouter()

const login = async () => {
  try {
    const { data } = await api.post('/token/', { username: username.value, password: password.value })
    localStorage.setItem('token', data.access)
    router.push('/dashboard')
  } catch (e) {
    error.value = 'Неверный логин или пароль'
  }
}
</script>

<style scoped>
.login-page { display: flex; justify-content: center; align-items: center; min-height: 100vh; background: var(--color-bg); }
.login-box { background: white; padding: 40px; border-radius: 4px; border-top: 4px solid var(--color-accent); width: 100%; max-width: 400px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }
.login-box h2 { font-family: var(--font-serif); margin-bottom: 20px; }
.login-box input { width: 100%; padding: 12px; margin-bottom: 15px; border: 1px solid var(--color-gold); }
.btn-primary { width: 100%; background: var(--color-text); color: white; padding: 12px; border: none; cursor: pointer; }
.error { color: var(--color-accent); margin-top: 10px; text-align: center; }
</style>