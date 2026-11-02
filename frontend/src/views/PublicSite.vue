<template>
  <div class="page-wrapper">
    <div class="bg-texture" aria-hidden="true"></div>
    
    <!-- Пункт 7: Скелетон-лоадер -->
    <SkeletonLoader v-if="loading" />
    
    <main v-else-if="organizer.name" class="content">
      <HeroSection :organizer="organizer" @scroll-to-form="scrollToForm" />
      
      <!-- Пункт 9: Фильтры -->
      <div v-if="allTags.length > 1" class="filters">
        <button 
          v-for="tag in allTags" 
          :key="tag"
          :class="{ active: selectedTag === tag }"
          @click="selectedTag = tag"
        >
          {{ tag }}
        </button>
      </div>

      <AfishaSection 
        :events="filteredEvents" 
        @select-event="handleEventSelect"
        @request-event="handleRequestEvent"
        @share-event="shareEvent"
        @join-waitlist="joinWaitlist"
      />
      
      <DirectionsSection 
        v-if="organizer.directions_data && organizer.directions_data.length"
        :directions="organizer.directions_data"
        @open-details="handleOpenDetails" 
      />
      
      <!-- Пункт 15: Юридический блок -->
      <div class="legal-links" v-if="organizer.privacy_policy_url || organizer.offer_url">
        <a v-if="organizer.privacy_policy_url" :href="organizer.privacy_policy_url" target="_blank">Политика конфиденциальности</a>
        <a v-if="organizer.offer_url" :href="organizer.offer_url" target="_blank">Публичная оферта</a>
      </div>

      <ContactSection 
        ref="contactRef" 
        :organizer-slug="slug" 
        :events-list="events" 
        :directions-list="organizer.directions_data || []" 
        :guarantee-text="organizer.guarantee_text"
      />
      
      <!-- Пункт 14: Отзывы -->
      <ReviewsSection />
    </main>

    <div v-if="!loading && !organizer.name" class="error-state">
      <h2>Пространство не найдено</h2>
      <router-link to="/" class="btn-back">На главную</router-link>
    </div>

    <AppFooter v-if="organizer.name" :organizer="organizer" />

    <!-- Пункт 11: Липкая кнопка на мобильном -->
    <div class="sticky-cta" v-if="isMobile && !loading">
      <button @click="scrollToForm">Связаться</button>
    </div>

    <!-- Модалка направлений -->
    <ModalDialog 
      :is-open="modalState.isOpen" 
      :title="modalState.title" 
      :description="modalState.description" 
      @close="modalState.isOpen = false" 
      @action="modalAction" 
    />

    <!-- Модалка расчета -->
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
            <input v-model="requestForm.name" required />
          </div>
          <div class="input-group">
            <label>Телефон или Email</label>
            <input v-model="requestForm.contact" required />
          </div>
          <div class="input-row">
            <div class="input-group">
              <label>Кол-во гостей</label>
              <input v-model.number="requestForm.guests_count" type="number" min="1" />
            </div>
            <div class="input-group">
              <label>Бюджет</label>
              <input v-model="requestForm.budget" />
            </div>
          </div>
          <div class="input-group">
            <label>Пожелания</label>
            <textarea v-model="requestForm.wishes" rows="3"></textarea>
          </div>
          <button type="submit" class="btn-submit" :disabled="requestLoading">
            {{ requestLoading ? 'Отправка...' : 'Отправить' }}
          </button>
        </form>
        <p v-if="requestMessage" :class="['request-message', requestMessageType]">{{ requestMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'

import HeroSection from '@/components/HeroSection.vue'
import AfishaSection from '@/components/AfishaSection.vue'
import DirectionsSection from '@/components/DirectionsSection.vue'
import ContactSection from '@/components/ContactSection.vue'
import AppFooter from '@/components/AppFooter.vue'
import ModalDialog from '@/components/ModalDialog.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import ReviewsSection from '@/components/ReviewsSection.vue'

const route = useRoute()
const slug = route.params.slug
const events = ref([])
const organizer = ref({})
const loading = ref(true)
const contactRef = ref(null)
const isMobile = ref(window.innerWidth < 768)

// Пункт 9: Фильтры
const selectedTag = ref('Все')
const allTags = computed(() => {
  const tags = new Set(['Все'])
  events.value.forEach(e => {
    if (e.tags) e.tags.split(',').forEach(t => tags.add(t.trim()))
  })
  return Array.from(tags)
})

const filteredEvents = computed(() => {
  if (selectedTag.value === 'Все') return events.value
  return events.value.filter(e => e.tags && e.tags.includes(selectedTag.value))
})

const modalState = reactive({ isOpen: false, title: '', description: '', directionTitle: '' })
const showRequestModal = ref(false)
const selectedEvent = ref(null)
const requestLoading = ref(false)
const requestMessage = ref('')
const requestMessageType = ref('')
const requestForm = reactive({ name: '', contact: '', guests_count: null, budget: '', wishes: '' })

const scrollToForm = () => { contactRef.value?.$el?.scrollIntoView({ behavior: 'smooth' }); }

onMounted(async () => {
  try {
    const [orgRes, eventsRes] = await Promise.all([
      api.get(`/public/${slug}/info/`),
      api.get(`/public/${slug}/events/`)
    ])
    organizer.value = orgRes.data
    events.value = eventsRes.data
    document.title = `${organizer.value.name} | Пространство развития`
    
    window.addEventListener('resize', () => { isMobile.value = window.innerWidth < 768 })
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
})

const handleEventSelect = (event) => {
  contactRef.value?.setDirection(event.direction, event.id)
  contactRef.value?.$el?.scrollIntoView({ behavior: 'smooth' })
}

const handleRequestEvent = (event) => {
  selectedEvent.value = event
  Object.assign(requestForm, { name: '', contact: '', guests_count: null, budget: '', wishes: '' })
  requestMessage.value = ''
  showRequestModal.value = true
}

const submitRequest = async () => {
  requestLoading.value = true
  try {
    await api.post('/leads/', { ...requestForm, direction: selectedEvent.value.direction, event: selectedEvent.value.id })
    requestMessage.value = 'Запрос отправлен!'
    requestMessageType.value = 'success'
    Object.assign(requestForm, { name: '', contact: '', guests_count: null, budget: '', wishes: '' })
    setTimeout(() => { showRequestModal.value = false }, 2000)
  } catch (e) {
    requestMessage.value = 'Ошибка отправки'
    requestMessageType.value = 'error'
  } finally {
    requestLoading.value = false
  }
}

// Пункт 8: Поделиться
const shareEvent = async (event) => {
  const url = `${window.location.origin}/${slug}#event-${event.id}`
  if (navigator.share) {
    try {
      await navigator.share({ title: event.title, text: `Присоединяйся!`, url })
    } catch (e) {}
  } else {
    navigator.clipboard.writeText(url)
    alert('Ссылка скопирована!')
  }
}

// Пункт 10: Waitlist
const joinWaitlist = async (event) => {
  const name = prompt('Ваше имя:')
  const contact = prompt('Телефон или Email:')
  if (!name || !contact) return
  try {
    await api.post(`/events/${event.id}/waitlist/`, { name, contact })
    alert('Вы в листе ожидания!')
  } catch (e) {
    alert('Ошибка')
  }
}

const handleOpenDetails = (direction) => {
  modalState.title = direction.title
  modalState.description = direction.fullDescription
  modalState.directionTitle = direction.title
  modalState.isOpen = true
}

const modalAction = () => {
  modalState.isOpen = false
  contactRef.value?.setDirection(modalState.directionTitle, null)
  contactRef.value?.$el?.scrollIntoView({ behavior: 'smooth' })
}
</script>

<style scoped>
/* Ваши стили + новые */
.page-wrapper { position: relative; min-height: 100vh; padding: 40px 20px; background: var(--color-bg); overflow: hidden; }
.bg-texture { position: absolute; inset: 0; z-index: 0; pointer-events: none; background-image: url("..."); opacity: 0.8; }
.content { position: relative; z-index: 1; max-width: 900px; margin: 0 auto; }
.error-state { display: flex; flex-direction: column; justify-content: center; align-items: center; min-height: 60vh; text-align: center; position: relative; z-index: 1; }
.error-state h2 { font-family: var(--font-serif); font-size: 2.5rem; margin-bottom: 15px; }
.btn-back { background: var(--color-text); color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; }

/* Пункт 9: Фильтры */
.filters { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin-bottom: 30px; }
.filters button { background: white; border: 1px solid var(--color-gold); padding: 8px 16px; border-radius: 50px; cursor: pointer; transition: 0.3s; }
.filters button.active { background: var(--color-text); color: white; }

/* Пункт 15: Юридические ссылки */
.legal-links { text-align: center; margin: 40px 0; font-size: 0.85rem; }
.legal-links a { color: var(--color-text-light); margin: 0 10px; text-decoration: underline; }

/* Пункт 11: Липкая кнопка */
.sticky-cta { position: fixed; bottom: 0; left: 0; right: 0; background: rgba(255,255,255,0.95); padding: 15px; box-shadow: 0 -5px 20px rgba(0,0,0,0.1); z-index: 100; display: none; text-align: center; }
.sticky-cta button { background: var(--color-text); color: white; border: none; padding: 15px 40px; border-radius: 4px; font-size: 1rem; width: 100%; }
@media (max-width: 768px) { .sticky-cta { display: block; } }

/* Модалка расчета */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(47, 62, 54, 0.7); backdrop-filter: blur(4px); display: flex; justify-content: center; align-items: center; z-index: 2000; }
.modal-box { background: var(--color-bg); padding: 40px; border-radius: 4px; border-top: 4px solid var(--color-accent); width: 100%; max-width: 500px; max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.2); }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.modal-header h2 { font-family: var(--font-serif); font-size: 2rem; }
.close-btn { background: none; border: none; font-size: 2rem; color: var(--color-text-light); cursor: pointer; }
.request-event-title { font-family: var(--font-serif); font-size: 1.3rem; color: var(--color-accent); margin-bottom: 20px; text-align: center; }
.request-form { display: flex; flex-direction: column; gap: 15px; }
.input-group { display: flex; flex-direction: column; gap: 5px; }
.input-group label { font-size: 0.85rem; color: var(--color-text-light); text-transform: uppercase; }
.input-group input, .input-group textarea { width: 100%; padding: 12px 15px; border: 1px solid rgba(197, 168, 128, 0.5); border-radius: 2px; font-family: var(--font-sans); font-size: 1rem; background: white; }
.input-row { display: flex; gap: 15px; }
.input-row .input-group { flex: 1; }
.btn-submit { background: var(--color-text); color: white; padding: 15px; border: none; border-radius: 2px; font-size: 1rem; cursor: pointer; transition: 0.3s; margin-top: 10px; }
.btn-submit:hover:not(:disabled) { background: var(--color-accent); }
.request-message { margin-top: 15px; padding: 10px; border-radius: 4px; text-align: center; }
.request-message.success { background: #e8f5e9; color: #2e7d32; }
.request-message.error { background: #ffebee; color: #c62828; }
</style>