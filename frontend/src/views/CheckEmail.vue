<template>
  <div class="check-email-page">
    <div class="check-email-box">
      <div class="icon">📧</div>
      <h2>Проверьте вашу почту</h2>
      <p class="desc">
        Мы отправили письмо с ссылкой для подтверждения на адрес <strong>{{ email }}</strong>.
      </p>
      <p class="hint">
        Не видите письмо? Проверьте папку «Спам» или «Промоакции».
      </p>

      <div class="actions">
        <button @click="resendEmail" class="btn-primary" :disabled="resending">
          {{ resending ? 'Отправка...' : 'Отправить письмо еще раз' }}
        </button>
        <router-link to="/login" class="btn-link">Я уже подтвердил, войти</router-link>
      </div>
      
      <p v-if="message" :class="messageType">{{ message }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api'

const route = useRoute()
const router = useRouter()
const email = ref(route.query.email || 'вашу почту')
const resending = ref(false)
const message = ref('')
const messageType = ref('')

onMounted(() => {
  // Сохраняем данные пользователя в localStorage, 
  // чтобы можно было повторить запрос на отправку, если пользователь обновит страницу
  if (route.query.email) {
    localStorage.setItem('pending_email', route.query.email)
    localStorage.setItem('pending_uid', route.query.uid || '')
  }
})

const resendEmail = async () => {
  const savedEmail = localStorage.getItem('pending_email')
  const savedUid = localStorage.getItem('pending_uid')
  
  if (!savedEmail) {
    message.value = 'Не удалось найти email. Попробуйте зарегистрироваться заново.'
    messageType.value = 'error'
    return
  }

  resending.value = true
  message.value = ''
  
  try {
    // Отправляем запрос на повторную отправку (нужно будет добавить на бэкенде)
    await api.post('/resend-verification/', { email: savedEmail })
    message.value = 'Письмо отправлено повторно!'
    messageType.value = 'success'
  } catch (e) {
    message.value = e.response?.data?.error || 'Ошибка отправки. Попробуйте позже.'
    messageType.value = 'error'
  } finally {
    resending.value = false
  }
}
</script>

<style scoped>
.check-email-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: var(--color-bg);
  padding: 20px;
}

.check-email-box {
  background: white;
  padding: 50px;
  border-radius: 8px;
  border-top: 4px solid var(--color-accent);
  box-shadow: 0 20px 60px rgba(0,0,0,0.1);
  text-align: center;
  max-width: 500px;
  width: 100%;
}

.icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.check-email-box h2 {
  font-family: var(--font-serif);
  font-size: 2rem;
  color: var(--color-text);
  margin-bottom: 15px;
}

.desc {
  font-size: 1.1rem;
  color: var(--color-text-light);
  margin-bottom: 10px;
  line-height: 1.5;
}

.desc strong {
  color: var(--color-text);
}

.hint {
  font-size: 0.9rem;
  color: #999;
  margin-bottom: 30px;
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.btn-primary {
  background: var(--color-text);
  color: white;
  padding: 15px 30px;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: 0.3s;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-accent);
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-link {
  color: var(--color-accent);
  text-decoration: underline;
  font-size: 0.95rem;
}

.message {
  margin-top: 20px;
  padding: 10px;
  border-radius: 4px;
}

.message.success { background: #e8f5e9; color: #2e7d32; }
.message.error { background: #ffebee; color: #c62828; }
</style>