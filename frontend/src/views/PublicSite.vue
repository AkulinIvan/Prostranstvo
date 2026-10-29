<!-- frontend\src\views\PublicSite.vue -->
<template>
  <div class="page-wrapper">
    <!-- Фоновая текстура -->
    <div class="bg-texture" aria-hidden="true"></div>
    
    <!-- Основной контент (показываем только если организатор найден) -->
    <main v-if="!loading && organizer.name" class="content">
      <HeroSection :organizer="organizer" />
      
      <AfishaSection 
        :events="events" 
        @select-event="handleEventSelect" 
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
const slug = route.params.slug // Получаем slug из URL (например, /jenyaz)

const events = ref([])
const organizer = ref({})
const loading = ref(true)
const contactRef = ref(null)
const scrollToForm = () => {
  contactRef.value?.$el?.scrollIntoView({ behavior: 'smooth' });
};

// Состояние для модального окна (описание направлений)
const modalState = reactive({
  isOpen: false,
  title: '',
  description: '',
  directionTitle: ''
})

// 1. Загрузка данных при монтировании
onMounted(async () => {
  try {
    // Запрашиваем данные организатора и его афишу
    // (Предполагается, что на бэкенде есть эндпоинт /public/<slug>/info/)
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
    organizer.value = orgResponse.data
    events.value = eventsResponse.data
    document.title = `${organizer.value.name} | Пространство развития`
  } catch (error) {
    console.error('Ошибка загрузки данных:', error)
    // Если 404, organizer останется пустым объектом, и сработает v-if в шаблоне
  } finally {
    loading.value = false
  }
})

// 2. Клик по кнопке "Записаться" в афише
const handleEventSelect = (event) => {
  // Передаем в форму направление и ID конкретного события
  contactRef.value?.setDirection(event.direction, event.id)
  // Плавно скроллим к форме
  contactRef.value?.$el?.scrollIntoView({ behavior: 'smooth' })
}

// 3. Клик по кнопке "Узнать больше" в карточках направлений
const handleOpenDetails = (direction) => {
  modalState.title = direction.title
  modalState.description = direction.fullDescription
  modalState.directionTitle = direction.title
  modalState.isOpen = true
}

// 4. Действие внутри модального окна (кнопка "Записаться на курс")
const modalAction = () => {
  modalState.isOpen = false
  // Передаем направление в форму (без привязки к событию)
  contactRef.value?.setDirection(modalState.directionTitle, null)
  contactRef.value?.$el?.scrollIntoView({ behavior: 'smooth' })
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

/* Текстура пергамента на фоне */
.bg-texture {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.04'/%3E%3C/svg%3E");
  opacity: 0.8;
}

/* Контент поверх фона */
.content {
  position: relative;
  z-index: 1;
  max-width: 900px;
  margin: 0 auto;
}

/* Состояния загрузки и ошибки */
.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
  text-align: center;
  position: relative;
  z-index: 1;
}

.loading-state p {
  font-family: var(--font-serif);
  font-size: 1.5rem;
  color: var(--color-text-light);
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { opacity: 0.5; }
  50% { opacity: 1; }
  100% { opacity: 0.5; }
}

.error-state h2 {
  font-family: var(--font-serif);
  font-size: 2.5rem;
  color: var(--color-text);
  margin-bottom: 15px;
}

.error-state p {
  color: var(--color-text-light);
  margin-bottom: 30px;
}

.btn-back {
  background: var(--color-text);
  color: white;
  padding: 12px 24px;
  text-decoration: none;
  border-radius: 4px;
  transition: background 0.3s;
}

.btn-back:hover {
  background: var(--color-accent);
}
</style>