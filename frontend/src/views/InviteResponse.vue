<template>
  <div class="invite-page">
    <div class="invite-card">
      <div v-if="loading" class="loading">Загрузка...</div>
      
      <div v-else-if="error" class="error">
        <h2>Ошибка</h2>
        <p>{{ error }}</p>
      </div>
      
      <div v-else-if="inviteInfo">
        <h2>Приглашение</h2>
        <p><strong>{{ inviteInfo.lead_name }}</strong>, вы приглашены на событие:</p>
        <h3>{{ inviteInfo.event_title }}</h3>
        <p>📅 {{ inviteInfo.event_date }}</p>
        <p>📍 {{ inviteInfo.event_location }}</p>
        
        <!-- Если уже ответил -->
        <div v-if="inviteInfo.status === 'accepted'" class="status accepted">
          Вы уже <strong>подтвердили</strong> участие. Ждем вас!
        </div>
        <div v-else-if="inviteInfo.status === 'declined'" class="status declined">
          Вы <strong>отказались</strong> от участия. Спасибо за ответ!
        </div>
        
        <!-- Кнопки для ответа -->
        <div v-else class="actions">
          <button @click="respond('accept')" class="btn-accept">✅ Я приду</button>
          <button @click="respond('decline')" class="btn-decline">❌ Не смогу</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'

const route = useRoute()
const token = route.params.token
const inviteInfo = ref(null)
const loading = ref(true)
const error = ref('')

const fetchInfo = async () => {
  try {
    const { data } = await api.get(`/invite/${token}/`)
    inviteInfo.value = data
  } catch (e) {
    error.value = 'Приглашение не найдено или устарело.'
  } finally {
    loading.value = false
  }
}

const respond = async (action) => {
  try {
    await api.post(`/invite/${token}/respond/`, { action })
    inviteInfo.value.status = action === 'accept' ? 'accepted' : 'declined'
  } catch (e) {
    alert('Ошибка. Попробуйте позже.')
  }
}

onMounted(fetchInfo)
</script>

<style scoped>
.invite-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: var(--color-bg);
  padding: 20px;
}
.invite-card {
  background: white;
  padding: 50px;
  border-radius: 8px;
  border-top: 4px solid var(--color-accent);
  box-shadow: 0 20px 60px rgba(0,0,0,0.1);
  text-align: center;
  max-width: 500px;
}
.invite-card h2 { font-family: var(--font-serif); font-size: 2rem; margin-bottom: 15px; }
.invite-card h3 { font-family: var(--font-serif); font-size: 1.5rem; color: var(--color-text); margin: 15px 0; }
.actions { display: flex; gap: 20px; margin-top: 30px; justify-content: center; }
.btn-accept {
  background: #2e7d32; color: white; padding: 15px 30px; border: none; border-radius: 4px; font-size: 1.1rem; cursor: pointer;
}
.btn-decline {
  background: #c62828; color: white; padding: 15px 30px; border: none; border-radius: 4px; font-size: 1.1rem; cursor: pointer;
}
.status {
  margin-top: 20px;
  padding: 20px;
  border-radius: 8px;
  font-size: 1.1rem;
}
.status.accepted { background: #e8f5e9; color: #2e7d32; }
.status.declined { background: #ffebee; color: #c62828; }
</style>