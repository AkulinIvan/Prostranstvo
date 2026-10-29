<template>
  <div class="verify-page">
    <div class="verify-box">
      <div v-if="loading" class="loading">
        <h2>Подтверждение...</h2>
        <p>Пожалуйста, подождите.</p>
      </div>
      <div v-else-if="success" class="success">
        <h2>🎉 Аккаунт подтвержден!</h2>
        <p>{{ message }}</p>
        <router-link to="/login" class="btn-primary">Перейти ко входу</router-link>
      </div>
      <div v-else class="error">
        <h2>Ошибка</h2>
        <p>{{ error }}</p>
        <router-link to="/" class="btn-back">На главную</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'

const route = useRoute()
const loading = ref(true)
const success = ref(false)
const message = ref('')
const error = ref('')

onMounted(async () => {
  const uid = route.params.uid
  const token = route.params.token
  
  if (!uid || !token) {
    loading.value = false
    error.value = 'Неверная ссылка подтверждения.'
    return
  }
  
  try {
    const { data } = await api.post('/verify-email/', { uid, token })
    success.value = true
    message.value = data.message
  } catch (e) {
    error.value = e.response?.data?.error || 'Не удалось подтвердить аккаунт. Возможно, ссылка устарела.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.verify-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: var(--color-bg);
  padding: 20px;
}
.verify-box {
  background: white;
  padding: 50px;
  border-radius: 8px;
  border-top: 4px solid var(--color-accent);
  box-shadow: 0 20px 60px rgba(0,0,0,0.1);
  text-align: center;
  max-width: 500px;
  width: 100%;
}
.verify-box h2 {
  font-family: var(--font-serif);
  font-size: 2rem;
  margin-bottom: 15px;
}
.btn-primary {
  display: inline-block;
  background: var(--color-text);
  color: white;
  padding: 15px 30px;
  border-radius: 4px;
  text-decoration: none;
  margin-top: 20px;
  transition: 0.3s;
}
.btn-primary:hover { background: var(--color-accent); }
.btn-back {
  color: var(--color-accent);
  text-decoration: underline;
}
</style>