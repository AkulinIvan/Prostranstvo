<template>
  <div class="dashboard-page">
    <!-- Шапка панели -->
    <header class="dashboard-header">
      <div class="header-left">
        <h1>Панель управления</h1>
        <span class="organizer-name" v-if="organizerName">Пространство: {{ organizerName }}</span>
        <span v-if="isSaving" class="saving-indicator">Сохранение...</span>
        <span v-else-if="lastSaved" class="saved-indicator">✅ Сохранено в {{ lastSaved.toLocaleTimeString() }}</span>
      </div>
      <div class="header-actions">
        <button @click="logout" class="btn-logout">Выйти</button>
        <button @click="showProfile = true" class="btn-action">⚙️ Профиль</button>
      </div>
    </header>

    <main class="dashboard-content">
      
      <!-- === БЛОК НАПРАВЛЕНИЙ (На главном экране) === -->
      <section class="dashboard-section">
        <div class="section-top">
          <h2>Мои направления</h2>
          <button @click="addDirection" class="btn-primary">+ Добавить направление</button>
        </div>
        
        <div v-if="profileForm.directions_data.length" class="directions-grid">
          <div v-for="(dir, index) in profileForm.directions_data" :key="index" class="direction-card">
            <div class="dir-image" v-if="dir.image">
              <img :src="getFullImageUrl(dir.image)" alt="Фото" />
            </div>
            <div class="dir-content">
              <input v-model="dir.title" placeholder="Название" class="dir-title-input" />
              <textarea v-model="dir.description" placeholder="Краткое описание" rows="2" class="dir-desc-input"></textarea>
              <div class="dir-upload">
                <label class="upload-label">
                  {{ dir.image ? 'Заменить фото' : 'Загрузить фото' }}
                  <input type="file" @change="uploadImage($event, index)" accept="image/*" hidden />
                </label>
              </div>
              <!-- Кнопка удаления -->
              <button @click="removeDirection(index)" class="btn-remove">Удалить</button>
            </div>
          </div>
        </div>
        <div v-else class="empty-dirs">
          <p>У вас пока нет направлений. Нажмите «Добавить», чтобы создать первое.</p>
        </div>
      </section>

      <!-- === БЛОК СОБЫТИЙ === -->
      <section class="dashboard-section mt-4">
        <div class="section-top">
          <h2>Мои события</h2>
          <button @click="openCreateModal" class="btn-primary">➕ Добавить событие</button>
        </div>
        
        <div v-if="events.length" class="events-list">
          <div v-for="event in events" :key="event.id" class="event-card">
            <div class="event-header">
              <h3>
                <span v-if="event.event_type === 'open'">📝</span>
                <span v-else>💼</span>
                {{ event.title }}</h3>
              <span class="event-date">{{ formatDate(event.date) }}</span>
            </div>
            
            <div class="event-stats">
              <div v-if="event.event_type === 'open'" class="stat-item">
                <span>Записались:</span>
                <strong>{{ event.lead_count }}</strong> / {{ event.min_people }}
              </div>
              <div v-else class="stat-item">
                <span>Тип:</span> <strong>Запрос на расчет</strong>
              </div>
              <div :class="['status-badge', event.is_confirmed ? 'status-ok' : 'status-wait']">
                {{ event.is_confirmed ? '✅ Группа набрана' : '⏳ Идет набор' }}
              </div>
            </div>

            <div class="event-actions">
              <button @click="viewLeads(event)" class="btn-action">👥 Участники ({{ event.lead_count }})</button>
              <button @click="toggleConfirm(event)" class="btn-action">
                {{ event.is_confirmed ? 'Снять статус' : 'Провести' }}
              </button>
              <button @click="openInviteModal(event)" class="btn-action">📩 Пригласить из базы</button>
              <button @click="sendReminders(event)" class="btn-action">📧 Напомнить</button>
            </div>
          </div>
        </div>
        
        <div v-else class="empty-state">
          <p>У вас пока нет созданных событий.</p>
          <p class="empty-sub">Нажмите «Добавить событие», чтобы начать.</p>
        </div>
      </section>

      <!-- === БЛОК ОТЗЫВОВ === -->
      <section class="dashboard-section mt-4">
        <div class="section-top">
          <h2>Отзывы</h2>
        </div>
        
        <div v-if="reviews.length" class="reviews-admin-list">
          <div v-for="review in reviews" :key="review.id" class="review-admin-card" :class="{ 'approved': review.is_approved }">
            <div class="review-admin-header">
              <strong>{{ review.author_name }}</strong>
              <span class="review-stars">{{ '★'.repeat(review.rating) }}{{ '☆'.repeat(5 - review.rating) }}</span>
              <span class="review-date">{{ new Date(review.created_at).toLocaleDateString('ru-RU') }}</span>
            </div>
            <p class="review-admin-text">{{ review.text }}</p>
            <div class="review-admin-actions">
              <button v-if="!review.is_approved" @click="approveReview(review.id)" class="btn-small btn-approve">Одобрить</button>
              <span v-else class="status-approved">✅ На сайте</span>
              <button @click="deleteReview(review.id)" class="btn-delete">Удалить</button>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <p>Пока нет отзывов.</p>
        </div>
      </section>
      <!-- <section class="dashboard-section mt-4">
        <div class="section-top"><h2>Шаблоны приглашений</h2></div>
        <p style="color: #666; margin-bottom: 15px;">Используйте эти тексты при ручном приглашении клиентов.</p>
        <div class="template-list">
          <div class="template-item">
            <strong>Стандартное</strong>
            <p>Привет! Приглашаю тебя на [Название]. Будет интересно!</p>
          </div>
          <div class="template-item">
            <strong>Теплое</strong>
            <p>Здравствуй! Я подумала, что тебе может понравиться [Название]. Жду!</p>
          </div>
        </div>
      </section> -->
      <!-- Кнопка сохранения всех изменений (направлений) -->
      <div class="save-bar">
        <button @click="saveProfile" class="btn-primary save-btn" :disabled="loading">
          {{ loading ? 'Сохранение...' : 'Сохранить изменения' }}
        </button>
      </div>

    </main>

    <!-- Модалка создания события -->
    <div v-if="showCreate" class="modal-overlay" @click.self="showCreate = false">
      <div class="modal-box form-box">
        <h2>Новое событие</h2>
        
        <div class="input-group">
          <label>Название</label>
          <input v-model="form.title" type="text" placeholder="Например: Игра 'Внутренний ребенок'" />
        </div>
        
        <div class="input-group">
          <label>Дата и время</label>
          <input v-model="form.date" type="datetime-local" />
        </div>
        
        <div class="input-group">
          <label>Тип события</label>
          <select v-model="form.event_type">
            <option value="open">Открытая запись (клиенты записываются сами)</option>
            <option value="request">Запрос на расчет (клиент оставляет заявку, вы звоните)</option>
          </select>
        </div>

        <!-- Список направлений БЕРЕТСЯ ИЗ ПРОФИЛЯ -->
        <div class="input-group">
          <label>Направление</label>
          <select v-model="form.direction">
            <option value="" disabled>Выберите направление</option>
            <option 
              v-for="dir in profileForm.directions_data" 
              :key="dir.id" 
              :value="dir.title"
            >
              {{ dir.title }}
            </option>
          </select>
        </div>
        
        <div class="input-group">
          <label>Место проведения</label>
          <input v-model="form.location" type="text" placeholder="Адрес" />
        </div>
        
        <div class="input-group">
          <label>Минимум человек для проведения</label>
          <input v-model.number="form.min_people" type="number" min="1" />
        </div>
        
        <div class="input-group">
          <label>Описание</label>
          <textarea v-model="form.description" placeholder="Подробности..."></textarea>
        </div>

        <p v-if="error" class="error-text">{{ error }}</p>

        <div class="modal-actions">
          <button @click="showCreate = false" class="btn-cancel">Отмена</button>
          <button @click="createEvent" class="btn-primary" :disabled="loading">
            {{ loading ? 'Сохранение...' : 'Сохранить' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Модалка профиля (оставим для базовых настроек и паролей) -->
    <div v-if="showProfile" class="modal-overlay" @click.self="showProfile = false">
      <div class="modal-box form-box profile-box">
        <h2>Настройки профиля</h2>    

        <div class="input-group">
          <label>Имя бренда</label>
          <input v-model="profileForm.name" type="text" />
        </div>    
        <div class="input-group">
          <label>О себе (био)</label>
          <textarea v-model="profileForm.bio"></textarea>
        </div>    

        <div class="input-group mt-4">
          <label>Яндекс.Email (для календаря)</label>
          <input v-model="profileForm.yandex_email" type="email" />
        </div>    
        <div class="input-group">
          <label>Пароль приложения Яндекса</label>
          <input v-model="profileForm.yandex_app_password" type="password" />
        </div>    

        <div class="modal-actions">
          <button @click="showProfile = false" class="btn-cancel">Отмена</button>
          <button @click="saveProfile" class="btn-primary">Сохранить</button>
        </div>
      </div>
    </div>

    <!-- Модалка со списком лидов -->
    <div v-if="showLeads" class="modal-overlay" @click.self="showLeads = false">
      <div class="modal-box leads-box">
        <div class="modal-header">
          <h2>Участники: {{ selectedEvent?.title }}</h2>
          <button @click="showLeads = false" class="close-btn">&times;</button>
        </div>
        
        <div v-if="leads.length" class="leads-list">
          <div v-for="lead in leads" :key="lead.id" class="lead-item">
            <div class="lead-info">
              <strong>{{ lead.name }}</strong>
              <span class="lead-contact">{{ lead.contact }}</span>
              <!-- Показываем статус -->
              <span :class="['lead-status', lead.status]">{{ getStatusText(lead.status) }}</span>
            </div>
            <div class="lead-actions">
              <button 
                v-if="lead.status === 'pending'" 
                @click="inviteLead(lead)" 
                class="btn-small btn-invite"
              >
                📩 Пригласить
              </button>
              <button @click="deleteLead(lead.id)" class="btn-delete" title="Удалить">&times;</button>
            </div>
          </div>
        </div>
        <p v-else class="empty-leads">На это событие пока никто не записался.</p>
      </div>
    </div>
    <!-- Модалка приглашения из базы -->
    <div v-if="showInviteModal" class="modal-overlay" @click.self="showInviteModal = false">
      <div class="modal-box">
        <div class="modal-header">
          <h2>Пригласить на: {{ selectedEvent?.title }}</h2>
          <button @click="showInviteModal = false" class="close-btn">&times;</button>
        </div>

        <div class="input-group">
          <label>Поиск по имени или контакту</label>
          <input v-model="searchQuery" type="text" placeholder="Введите имя или email..." />
        </div>

        <div v-if="filteredContacts.length" class="contacts-list">
          <div v-for="contact in filteredContacts" :key="contact.id" class="contact-item">
            <div>
              <strong>{{ contact.name }}</strong>
              <span class="contact-email">{{ contact.contact }}</span>
            </div>
            <button @click="inviteContact(contact.id)" class="btn-invite-contact">Пригласить</button>
          </div>
        </div>
        <p v-else class="empty-leads">Контактов не найдено.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'

const router = useRouter()
const events = ref([])
const leads = ref([])
const showCreate = ref(false)
const showLeads = ref(false)
const showProfile = ref(false)
const selectedEvent = ref(null)
const loading = ref(false)
const error = ref('')
const organizerName = ref('')
const reviews = ref([])

const form = reactive({ 
  title: '', date: '', direction: '', location: '', min_people: 3, description: '',
  event_type: 'open'
})

const profileForm = reactive({ 
  name: '', bio: '', yandex_email: '', yandex_app_password: '', directions_data: [] 
})

const isSaving = ref(false)
const lastSaved = ref(null)

watch(profileForm, debounce(async () => {
  isSaving.value = true
  try {
    await api.post('/dashboard/profile/', profileForm)
    lastSaved.value = new Date()
  } catch (e) {
    console.error('Ошибка автосохранения')
  } finally {
    isSaving.value = false
  }
}, 2000), { deep: true })

// Устанавливаем токен при загрузке
api.defaults.headers.common['Authorization'] = `Bearer ${localStorage.getItem('token')}`

const fetchEvents = async () => {
  try {
    const { data } = await api.get('/dashboard/events/')
    events.value = data
  } catch (e) {
    console.error('Ошибка загрузки событий', e)
    if (e.response?.status === 401) logout()
  }
}

const fetchProfile = async () => {
  try {
    const { data } = await api.get('/dashboard/profile/')
    Object.assign(profileForm, data)
    organizerName.value = data.name
    
    if (!profileForm.directions_data) {
      profileForm.directions_data = []
    }
  } catch (e) {
    console.error('Ошибка загрузки профиля', e)
  }
}

const createEvent = async () => {
  if (!form.title || !form.date || !form.direction) {
    error.value = 'Заполните обязательные поля'
    return
  }
  loading.value = true
  error.value = ''
  try {
    await api.post('/dashboard/events/', form)
    showCreate.value = false
    Object.assign(form, { title: '', date: '', direction: '', location: '', min_people: 3, description: '' })
    fetchEvents()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка создания события'
  } finally {
    loading.value = false
  }
}

const toggleConfirm = async (event) => {
  await api.post(`/dashboard/events/${event.id}/toggle_confirm/`)
  fetchEvents()
}

const sendReminders = async (event) => {
  await api.post(`/dashboard/events/${event.id}/send_reminders/`)
  alert('Напоминания отправлены всем участникам!')
}

const viewLeads = async (event) => {
  selectedEvent.value = event
  try {
    const { data } = await api.get(`/dashboard/leads/?event=${event.id}`)
    leads.value = data
    showLeads.value = true
  } catch (e) {
    console.error(e)
  }
}

const deleteLead = async (id) => {
  if (!confirm('Удалить эту заявку?')) return
  await api.delete(`/dashboard/leads/${id}/`)
  leads.value = leads.value.filter(l => l.id !== id)
  fetchEvents()
}

const addDirection = () => {
  profileForm.directions_data.push({
    id: Date.now().toString(),
    title: '',
    description: '',
    fullDescription: '',
    image: '' 
  })
}

const removeDirection = (index) => {
  profileForm.directions_data.splice(index, 1)
}

const saveProfile = async () => {
  loading.value = true
  try {
    await api.post('/dashboard/profile/', profileForm)
    alert('Профиль и направления обновлены!')
  } catch (e) {
    alert('Ошибка сохранения профиля')
  } finally {
    loading.value = false
  }
}

const uploadImage = async (event, index) => {
  const file = event.target.files[0]
  if (!file) return
  
  const formData = new FormData()
  formData.append('image', file)
  
  try {
    const { data } = await api.post('/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    profileForm.directions_data[index].image = data.url
    alert('Фото загружено! Не забудьте нажать "Сохранить изменения".')
  } catch (e) {
    alert('Ошибка загрузки фото')
  }
}

const getFullImageUrl = (url) => {
  if (!url) return '';
  if (url.startsWith('http')) return url;
  return `http://127.0.0.1:8000${url}`;
}

const openCreateModal = () => {
  // Очищаем форму при открытии
  Object.assign(form, { title: '', date: '', direction: '', location: '', min_people: 3, description: '', event_type: 'open' })
  showCreate.value = true
}

const logout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}

const formatDate = (iso) => {
  if (!iso) return ''
  return new Date(iso).toLocaleString('ru-RU', { 
    day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' 
  })
}

const getStatusText = (status) => {
  const map = {
    'pending': 'Ожидает',
    'invited': 'Приглашен',
    'accepted': '✅ Принял',
    'declined': '❌ Отказался'
  }
  return map[status] || status
}

const inviteLead = async (lead) => {
  try {
    await api.post(`/dashboard/leads/${lead.id}/invite/`)
    // Обновляем статус локально
    lead.status = 'invited'
    alert('Приглашение отправлено на почту!')
  } catch (e) {
    alert(e.response?.data?.error || 'Ошибка отправки приглашения')
  }
}

const showInviteModal = ref(false)
const allContacts = ref([])
const searchQuery = ref('')

// Загрузка контактов при открытии модалки
const openInviteModal = async (event) => {
  selectedEvent.value = event
  searchQuery.value = ''
  try {
    const { data } = await api.get('/contacts/')
    allContacts.value = data
    showInviteModal.value = true
  } catch (e) {
    alert('Ошибка загрузки базы контактов')
  }
}

// Фильтрация для поиска
const filteredContacts = computed(() => {
  if (!searchQuery.value) return allContacts.value
  const q = searchQuery.value.toLowerCase()
  return allContacts.value.filter(c => 
    c.name.toLowerCase().includes(q) || c.contact.toLowerCase().includes(q)
  )
})

// Отправка приглашения
const inviteContact = async (contactId) => {
  try {
    await api.post('/invite-contact/', {
      contact_id: contactId,
      event_id: selectedEvent.value.id
    })
    alert('Приглашение отправлено!')
    // Обновляем список лидов у события (счетчик)
    fetchEvents()
    showInviteModal.value = false
  } catch (e) {
    alert(e.response?.data?.error || 'Ошибка отправки приглашения')
  }
}

const fetchReviews = async () => {
  try {
    const { data } = await api.get('/dashboard/reviews/')
    reviews.value = data
  } catch (e) { console.error(e) }
}

const approveReview = async (id) => {
  try {
    await api.post(`/dashboard/reviews/${id}/approve/`)
    
    // Находим отзыв в локальном массиве и меняем его статус
    const review = reviews.value.find(r => r.id === id)
    if (review) {
      review.is_approved = true // Реактивно обновляем интерфейс
    }
    
    // Опционально: показать уведомление
    alert('Отзыв одобрен и появился на сайте!')
  } catch (e) {
    alert('Ошибка при одобрении отзыва')
    // Если ошибка, лучше перезагрузить данные, чтобы синхронизироваться с сервером
    fetchReviews()
  }
}

const deleteReview = async (id) => {
  if (!confirm('Удалить отзыв?')) return
  await api.delete(`/dashboard/reviews/${id}/`)
  fetchReviews()
}

function debounce(func, wait) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

onMounted(() => {
  fetchEvents()
  fetchProfile()
  fetchReviews()
})
</script>

<style scoped>
.dir-upload {
  margin-bottom: 15px;
}

.upload-label {
  display: inline-block;
  background: #f0f0f0;
  border: 1px dashed var(--color-gold);
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 0.85rem;
  cursor: pointer;
  color: var(--color-text);
  transition: 0.3s;
}

.upload-label:hover {
  background: var(--color-gold);
  color: white;
}

.dashboard-page {
  min-height: 100vh;
  background-color: var(--color-bg);
  padding: 40px 20px;
  font-family: var(--font-sans);
}

.dashboard-header {
  max-width: 1000px;
  margin: 0 auto 40px;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-bottom: 1px solid rgba(197, 168, 128, 0.3);
  padding-bottom: 20px;
}

.header-left h1 {
  font-family: var(--font-serif);
  font-size: 2.5rem;
  color: var(--color-text);
  margin-bottom: 5px;
}

.organizer-name {
  color: var(--color-text-light);
  font-size: 0.9rem;
}

.header-actions {
  display: flex;
  gap: 15px;
}

.dashboard-content {
  max-width: 1000px;
  margin: 0 auto;
  padding-bottom: 80px; /* Место для кнопки сохранения */
}

/* Блоки контента */
.dashboard-section {
  background: white;
  padding: 30px;
  border-radius: 4px;
  border-top: 4px solid var(--color-gold);
  box-shadow: 0 5px 15px rgba(47, 62, 54, 0.03);
}
.section-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.section-top h2 {
  font-family: var(--font-serif);
  font-size: 1.8rem;
  color: var(--color-text);
}
.mt-4 { margin-top: 30px; }

/* Сетка направлений */
.directions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}
.direction-card {
  border: 1px solid #eee;
  border-radius: 4px;
  overflow: hidden;
  background: #FDFBF7;
}
.dir-image {
  width: 100%;
  height: 120px;
}
.dir-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.dir-content {
  padding: 15px;
}
.dir-title-input {
  width: 100%;
  font-family: var(--font-serif);
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 8px;
  border: none;
  background: transparent;
  border-bottom: 1px solid #ccc;
}
.dir-desc-input {
  width: 100%;
  border: none;
  background: transparent;
  font-size: 0.9rem;
  resize: none;
  margin-bottom: 10px;
}
.dir-title-input:focus, .dir-desc-input:focus {
  outline: none;
  border-color: var(--color-gold);
}
.btn-remove {
  background: none;
  border: none;
  color: red;
  font-size: 0.8rem;
  cursor: pointer;
  padding: 0;
}

/* Кнопки */
.btn-primary {
  background: var(--color-text);
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 2px;
  cursor: pointer;
  transition: 0.3s;
}
.btn-primary:hover { background: var(--color-accent); }
.btn-primary:disabled { background: #ccc; cursor: not-allowed; }

.btn-logout {
  background: transparent;
  border: 1px solid var(--color-text-light);
  color: var(--color-text-light);
  padding: 12px 24px;
  border-radius: 2px;
  cursor: pointer;
  transition: 0.3s;
}
.btn-logout:hover { background: var(--color-text-light); color: white; }

.btn-action {
  background: white;
  border: 1px solid var(--color-gold);
  color: var(--color-text);
  padding: 8px 16px;
  border-radius: 2px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: 0.3s;
}
.btn-action:hover { background: var(--color-gold); color: white; }

/* Блок событий */
.events-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.event-card {
  background: #FDFBF7;
  padding: 25px 30px;
  border-radius: 4px;
  border-left: 4px solid var(--color-accent);
}
.event-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 15px;
}
.event-header h3 {
  font-family: var(--font-serif);
  font-size: 1.5rem;
  color: var(--color-text);
}
.event-date { color: var(--color-text-light); font-size: 0.9rem; }
.event-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  font-size: 0.95rem;
  color: #555;
}
.stat-item strong { color: var(--color-text); font-size: 1.1rem; }
.status-badge {
  padding: 5px 12px;
  border-radius: 50px;
  font-size: 0.85rem;
  font-weight: 500;
}
.status-ok { background: #e8f5e9; color: #2e7d32; }
.status-wait { background: #fff3e0; color: #e65100; }
.event-actions { display: flex; gap: 10px; flex-wrap: wrap; }

/* Пустые состояния */
.empty-state, .empty-dirs {
  text-align: center;
  padding: 40px 20px;
  color: var(--color-text-light);
}
.empty-dirs {
  border: 1px dashed var(--color-gold);
  border-radius: 4px;
  margin-bottom: 20px;
}

/* Панель сохранения */
.save-bar {
  position: fixed;
  bottom: 0; left: 0; width: 100%;
  background: rgba(244, 241, 234, 0.9);
  backdrop-filter: blur(5px);
  padding: 20px;
  text-align: center;
  border-top: 1px solid var(--color-gold);
  z-index: 100;
}
.save-btn {
  min-width: 300px;
  font-size: 1.1rem;
}

/* Модалки */
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
.modal-box h2 {
  font-family: var(--font-serif);
  font-size: 2rem;
  color: var(--color-text);
  margin-bottom: 25px;
}
.input-group { margin-bottom: 20px; }
.input-group label {
  display: block;
  font-size: 0.85rem;
  color: var(--color-text-light);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.input-group input, .input-group select, .input-group textarea {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid rgba(197, 168, 128, 0.5);
  border-radius: 2px;
  font-family: var(--font-sans);
  font-size: 1rem;
  background: white;
  transition: 0.3s;
}
.input-group input:focus, .input-group select:focus, .input-group textarea:focus {
  outline: none;
  border-color: var(--color-text);
}
.input-group textarea { min-height: 100px; resize: vertical; }
.error-text { color: var(--color-accent); font-size: 0.9rem; margin-bottom: 15px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 15px; margin-top: 30px; }
.btn-cancel {
  background: transparent;
  border: 1px solid #ccc;
  padding: 12px 24px;
  cursor: pointer;
  border-radius: 2px;
}
.leads-box { max-width: 600px; }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.close-btn { background: none; border: none; font-size: 2rem; color: var(--color-text-light); cursor: pointer; line-height: 1; }
.leads-list { display: flex; flex-direction: column; gap: 10px; }
.lead-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: white;
  border: 1px solid #eee;
  border-radius: 2px;
}
.lead-info { display: flex; flex-direction: column; }
.lead-info strong { font-size: 1rem; color: var(--color-text); }
.lead-contact { color: var(--color-accent); font-weight: 500; font-size: 0.9rem; }
.lead-time { font-size: 0.75rem; color: #999; margin-top: 3px; }
.btn-delete { background: none; border: none; color: #ff4444; font-size: 1.5rem; cursor: pointer; padding: 0 10px; opacity: 0.6; transition: 0.2s; }
.btn-delete:hover { opacity: 1; }
.empty-leads { text-align: center; color: var(--color-text-light); padding: 40px; font-style: italic; }

.lead-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}
.lead-status {
  font-size: 0.8rem;
  padding: 2px 8px;
  border-radius: 10px;
  display: inline-block;
  margin-top: 5px;
}
.lead-status.pending { background: #f0f0f0; color: #666; }
.lead-status.invited { background: #fff3e0; color: #e65100; }
.lead-status.accepted { background: #e8f5e9; color: #2e7d32; }
.lead-status.declined { background: #ffebee; color: #c62828; }
.btn-invite {
  background: #e3f2fd;
  border: 1px solid #90caf9;
  color: #1565c0;
  padding: 5px 10px;
  border-radius: 2px;
  cursor: pointer;
  font-size: 0.8rem;
}
.reviews-admin-list { display: flex; flex-direction: column; gap: 15px; }
.review-admin-card { background: #FDFBF7; padding: 20px; border-left: 4px solid #ccc; border-radius: 4px; }
.review-admin-card.approved { border-left-color: #2e7d32; background: #f4fcf5; }
.review-admin-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; font-size: 0.9rem; }
.review-stars { color: #f5a623; letter-spacing: 2px; }
.review-admin-text { color: #555; margin-bottom: 15px; font-style: italic; }
.review-admin-actions { display: flex; gap: 15px; align-items: center; }
.btn-approve { background: #e8f5e9; border: 1px solid #2e7d32; color: #2e7d32; padding: 5px 10px; cursor: pointer; }
.status-approved { color: #2e7d32; font-size: 0.85rem; }
</style>