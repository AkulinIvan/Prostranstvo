<template>
  <div class="page-wrapper">
    <!-- Фоновая текстура -->
    <div class="bg-texture" aria-hidden="true"></div>
    
    <!-- Основной контент (показываем только если организатор найден) -->
    <main v-if="!loading && organizer.name" class="content">
      <HeroSection :organizer="organizer" @scroll-to-form="scrollToForm" />
      
      <AfishaSection 
        :events="events" 
        @select-event="handleEventSelect"
        @request-event="handleRequestEvent" 
      />
      
      <DirectionsSection 
        v-if="organizer.directions_data && organizer.directions_data.length"
        :directions="organizer.directions_data"
        @open-details="handleOpenDetails" 
      />
      
      <ContactSection 
        ref="contactRef" 
        :organizer-slug="slug" 
        :events-list="events" 
        :directions-list="organizer.directions_data || []" 
      />
    </main>

    <!-- Состояние загрузки -->
    <div v-if="loading" class="loading-state">
      <p>Загрузка пространства...</p>
    </div>

    <!-- Ошибка 404 (организатор не найден) -->
    <div v-if="!loading && !organizer.name" class="error-state">
      <h2>Пространство не найдено</h2>
      <p>Возможно, ссылка устарела или организатор еще не настроил свой профиль.</p>
      <router-link to="/" class="btn-back">На главную</router-link>
    </div>

    <!-- Подвал (показываем только если организатор есть) -->
    <AppFooter 
      v-if="organizer.name" 
      :organizer="organizer" 
    />

    <!-- Модальное окно (для подробностей о направлениях) -->
    <ModalDialog 
      :is-open="modalState.isOpen" 
      :title="modalState.title" 
      :description="modalState.description" 
      @close="modalState.isOpen = false" 
      @action="modalAction" 
    />

    <!-- МОДАЛЬНОЕ ОКНО ЗАПРОСА НА РАСЧЕТ -->
    <div v-if="showRequestModal" class="modal-overlay" @click.self="showRequestModal = false">
      <div class="modal-box request-box">
        <div class="modal-header">
          <h2>Расчет стоимости</h2>
          <button @click="showRequestModal = false" class="close-btn">&times;</button>
        </div>
        <p class="request-event-title">{{ selectedEvent?.title }}</p>
        
        <form @submit.prevent="submitRequest" class="request-form">
          <div class="input-group">
            <label>Ваше имя</label>
            <input v-model="requestForm.name" type="text" placeholder="Как к вам обращаться?" required />
          </div>
          
          <div class="input-group">
            <label>Телефон или Email</label>
            <input v-model="requestForm.contact" type="text" placeholder="+7... или example@mail.ru" required />
          </div>
          
          <div class="input-row">
            <div class="input-group">
              <label>Кол-во гостей</label>
              <input v-model.number="requestForm.guests_count" type="number" placeholder="Например, 20" min="1" />
            </div>
            <div class="input-group">
              <label>Бюджет (если есть)</label>
              <input v-model="requestForm.budget" type="text" placeholder="Например, 15000" />
            </div>
          </div>
          
          <div class="input-group">
            <label>Пожелания, дата, место</label>
            <textarea v-model="requestForm.wishes" placeholder="Расскажите о ваших планах..." rows="3"></textarea>
          </div>
          
          <button type="submit" class="btn-submit" :disabled="requestLoading">
            {{ requestLoading ? 'Отправка...' : 'Отправить запрос' }}
          </button>
        </form>
        
        <p v-if="requestMessage" :class="['request-message', requestMessageType]">
          {{ requestMessage }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'

// Импорт компонентов
import HeroSection from '@/components/HeroSection.vue'
import AfishaSection from '@/components/AfishaSection.vue'
import DirectionsSection from '@/components/DirectionsSection.vue'
import ContactSection from '@/components/ContactSection.vue'
import AppFooter from '@/components/AppFooter.vue'
import ModalDialog from '@/components/ModalDialog.vue'

const route = useRoute()
const slug = route.params.slug

const events = ref([])
const organizer = ref({})
const loading = ref(true)
const contactRef = ref(null)

// Состояние для модального окна (описание направлений)
const modalState = reactive({
  isOpen: false,
  title: '',
  description: '',
  directionTitle: ''
})

// Состояние для модального окна расчета
const showRequestModal = ref(false)
const selectedEvent = ref(null)
const requestLoading = ref(false)
const requestMessage = ref('')
const requestMessageType = ref('')
const requestForm = reactive({
  name: '',
  contact: '',
  guests_count: null,
  budget: '',
  wishes: ''
})

const scrollToForm = () => {
  contactRef.value?.$el?.scrollIntoView({ behavior: 'smooth' });
};

// 1. Загрузка данных при монтировании
onMounted(async () => {
  try {
    const [orgResponse, eventsResponse] = await Promise.all([
      api.get(`/public/${slug}/info/`),
      api.get(`/public/${slug}/events/`)
    ])
    const data = orgResponse.data
    if (!data.directions_data || data.directions_data.length === 0) {
      data.directions_data = [
        { id: '1', title: 'Мероприятия', description: 'Скоро здесь появится описание...', fullDescription: '<p>Подробности скоро появятся.</p>', icon: '01' }
      ]
    }
    organizer.value = data
    events.value = eventsResponse.data
    document.title = `${organizer.value.name} | Пространство развития`
  } catch (error) {
    console.error('Ошибка загрузки данных:', error)
  } finally {
    loading.value = false
  }
})

// 2. Клик по кнопке "Записаться" в афише
const handleEventSelect = (event) => {
  contactRef.value?.setDirection(event.direction, event.id)
  contactRef.value?.$el?.scrollIntoView({ behavior: 'smooth' })
}

// 3. Клик по кнопке "Узнать больше" в карточках направлений
const handleOpenDetails = (direction) => {
  modalState.title = direction.title
  modalState.description = direction.fullDescription
  modalState.directionTitle = direction.title
  modalState.isOpen = true
}

// 4. Действие внутри модального окна направлений
const modalAction = () => {
  modalState.isOpen = false
  contactRef.value?.setDirection(modalState.directionTitle, null)
  contactRef.value?.$el?.scrollIntoView({ behavior: 'smooth' })
}

// 5. Клик по кнопке "Узнать стоимость" в афише
const handleRequestEvent = (event) => {
  selectedEvent.value = event
  // Очищаем форму перед открытием
  Object.assign(requestForm, { name: '', contact: '', guests_count: null, budget: '', wishes: '' })
  requestMessage.value = ''
  showRequestModal.value = true
}

// 6. Отправка запроса на расчет
const submitRequest = async () => {
  requestLoading.value = true
  requestMessage.value = ''
  try {
    await api.post('/leads/', {
      ...requestForm,
      direction: selectedEvent.value.direction,
      event: selectedEvent.value.id,
    })
    requestMessage.value = 'Запрос отправлен! Мы свяжемся с вами.'
    requestMessageType.value = 'success'
    // Очищаем форму
    Object.assign(requestForm, { name: '', contact: '', guests_count: null, budget: '', wishes: '' })
    // Закрываем модалку через 2 секунды
    setTimeout(() => { showRequestModal.value = false }, 2000)
  } catch (e) {
    requestMessage.value = e.response?.data?.error || 'Ошибка отправки. Попробуйте позже.'
    requestMessageType.value = 'error'
  } finally {
    requestLoading.value = false
  }
}
</script>

<style scoped>
.page-wrapper {
  position: relative;
  min-height: 100vh;
  padding: 40px 20px;
  background-color: var(--color-bg);
  overflow: hidden;
}
.bg-texture {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.04'/%3E%3C/svg%3E");
  opacity: 0.8;
}
.content { position: relative; z-index: 1; max-width: 900px; margin: 0 auto; }
.loading-state, .error-state { display: flex; flex-direction: column; justify-content: center; align-items: center; min-height: 60vh; text-align: center; position: relative; z-index: 1; }
.loading-state p { font-family: var(--font-serif); font-size: 1.5rem; color: var(--color-text-light); animation: pulse 1.5s infinite; }
@keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }
.error-state h2 { font-family: var(--font-serif); font-size: 2.5rem; color: var(--color-text); margin-bottom: 15px; }
.error-state p { color: var(--color-text-light); margin-bottom: 30px; }
.btn-back { background: var(--color-text); color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; transition: background 0.3s; }
.btn-back:hover { background: var(--color-accent); }

/* Стили для модалки расчета */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; width: 100vw; height: 100vh;
  background: rgba(47, 62, 54, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}
.modal-box {
  background: var(--color-bg);
  padding: 40px;
  border-radius: 4px;
  border-top: 4px solid var(--color-accent);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.modal-header h2 {
  font-family: var(--font-serif);
  font-size: 2rem;
  color: var(--color-text);
}
.close-btn {
  background: none; border: none; font-size: 2rem; color: var(--color-text-light); cursor: pointer; line-height: 1;
}
.request-event-title {
  font-family: var(--font-serif);
  font-size: 1.3rem;
  color: var(--color-accent);
  margin-bottom: 20px;
  text-align: center;
}
.request-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.input-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.input-group label {
  font-size: 0.85rem;
  color: var(--color-text-light);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.input-group input,
.input-group textarea {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid rgba(197, 168, 128, 0.5);
  border-radius: 2px;
  font-family: var(--font-sans);
  font-size: 1rem;
  background: white;
}
.input-group input:focus,
.input-group textarea:focus {
  outline: none;
  border-color: var(--color-text);
}
.input-group textarea { resize: vertical; }
.input-row {
  display: flex;
  gap: 15px;
}
.input-row .input-group { flex: 1; }
.btn-submit {
  background: var(--color-text);
  color: white;
  padding: 15px;
  border: none;
  border-radius: 2px;
  font-size: 1rem;
  cursor: pointer;
  transition: 0.3s;
  margin-top: 10px;
}
.btn-submit:hover:not(:disabled) { background: var(--color-accent); }
.btn-submit:disabled { background: #ccc; cursor: not-allowed; }
.request-message {
  margin-top: 15px;
  padding: 10px;
  border-radius: 4px;
  text-align: center;
}
.request-message.success { background: #e8f5e9; color: #2e7d32; }
.request-message.error { background: #ffebee; color: #c62828; }

@media (max-width: 600px) {
  .input-row { flex-direction: column; }
  .modal-box { padding: 25px 20px; }
}
</style>