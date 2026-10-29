<template>
  <section id="contact" class="contact-section">
    <div class="form-wrapper">
      <h2>Связаться со мной</h2>
      <form @submit.prevent="handleSubmit" class="contact-form">
        <input v-model="form.name" placeholder="Ваше имя" required />
        <input v-model="form.contact" placeholder="Телефон или Email" required />
        
        <select v-model="selection" required>
          <option value="" disabled>Выберите направление или событие</option>
          
          <!-- Группа 1: Ближайшие события -->
          <optgroup v-if="eventsList.length" label="Ближайшие встречи">
            <option 
              v-for="event in eventsList" 
              :key="'event-' + event.id" 
              :value="{ type: 'event', id: event.id, direction: event.direction }"
            >
              {{ formatDate(event.date) }} — {{ event.title }}
            </option>
          </optgroup>

          <!-- Группа 2: Направления (общие вопросы) -->
          <optgroup v-if="directionsList.length" label="Направления (без привязки к дате)">
            <option 
              v-for="dir in directionsList" 
              :key="'dir-' + dir.id" 
              :value="{ type: 'direction', id: null, direction: dir.title }"
            >
              {{ dir.title }}
            </option>
          </optgroup>
          
          <option value="other">Другое / Вопрос</option>
        </select>

        <input type="hidden" v-model="form.website" style="display:none" /> <!-- honeypot -->

        <button type="submit" class="btn-submit" :disabled="loading">
          {{ loading ? 'Отправка...' : 'Отправить' }}
        </button>
      </form>
      <p v-if="message" :class="messageType">{{ message }}</p>
    </div>
  </section>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import api from '@/api'

// Принимаем события и направления из родительского компонента (PublicSite.vue)
const props = defineProps({ 
  organizerSlug: String,
  eventsList: {
    type: Array,
    default: () => []
  },
  directionsList: {
    type: Array,
    default: () => []
  }
})

// Используем объект для выбора (чтобы понимать, событие это или просто направление)
const selection = ref('')
const form = reactive({ 
  name: '', 
  contact: '', 
  direction: '',
  event: null, // ID события (или null)
  website: '' 
})

const loading = ref(false)
const message = ref('')
const messageType = ref('')

// Форматирование даты для селекта
const formatDate = (isoString) => {
  const date = new Date(isoString);
  return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
};

const handleSubmit = async () => {
  if (!selection.value) return;
  
  loading.value = true
  message.value = ''
  
  try {
    // Если выбран "Другое" или направление
    let eventId = null;
    let directionName = '';
    
    if (selection.value === 'other') {
      directionName = 'Другое / Вопрос';
    } else if (selection.value.type === 'event') {
      eventId = selection.value.id;
      directionName = selection.value.direction;
    } else if (selection.value.type === 'direction') {
      directionName = selection.value.direction;
    }

    const payload = {
      name: form.name,
      contact: form.contact,
      direction: directionName,
      event: eventId // Передаем ID события или null
    }
    
    await api.post('/leads/', payload)
    
    message.value = 'Спасибо! Я свяжусь с вами.'
    messageType.value = 'success'
    
    // Очищаем форму
    form.name = ''
    form.contact = ''
    selection.value = ''
    
  } catch (e) {
    console.error(e)
    message.value = 'Ошибка отправки. Попробуйте позже.'
    messageType.value = 'error'
  } finally {
    loading.value = false
  }
}

// Метод для вызова из афиши (когда клиент нажимает "Записаться" на карточке события)
const setDirection = (dir, eventId = null) => {
  // Автоматически выбираем событие в селекте, если оно передано
  if (eventId) {
    const eventOption = props.eventsList.find(e => e.id === eventId);
    if (eventOption) {
      selection.value = { type: 'event', id: eventOption.id, direction: eventOption.direction };
      return;
    }
  }
  // Если события нет, ищем направление
  const dirOption = props.directionsList.find(d => d.title === dir);
  if (dirOption) {
    selection.value = { type: 'direction', id: null, direction: dirOption.title };
  }
}

defineExpose({ setDirection })
</script>

<style scoped>
/* Ваши стили остаются без изменений, добавьте только стили для optgroup */
.contact-section { padding: 80px 0; }
.form-wrapper { background: #ffffff; padding: 50px; border-radius: 30px; box-shadow: 0 20px 50px rgba(0, 0, 0, 0.05); max-width: 600px; margin: 0 auto; }
.form-wrapper h2 { font-family: 'Cormorant Garamond', serif; font-size: 2.5rem; color: #4a4036; margin-bottom: 10px; }
.contact-form { display: flex; flex-direction: column; gap: 20px; }
.contact-form input, .contact-form select { padding: 16px; border: 1px solid #e5e0d8; border-radius: 12px; font-size: 1rem; font-family: 'Inter', sans-serif; background: #f9f6f0; transition: border-color 0.3s; }
.contact-form input:focus, .contact-form select:focus { outline: none; border-color: #8b7d6b; box-shadow: 0 0 0 3px rgba(139, 125, 107, 0.1); }
.btn-submit { padding: 18px; background: #4a4036; color: #fff; border: none; border-radius: 12px; font-size: 1rem; cursor: pointer; transition: background 0.3s; margin-top: 10px; }
.btn-submit:hover:not(:disabled) { background: #2e2822; }
.btn-submit:disabled { background: #b0b0b0; cursor: not-allowed; }
.message { margin-top: 20px; padding: 15px; border-radius: 8px; text-align: center; }
.success { background: #e8f5e9; color: #2e7d32; }
.error { background: #ffebee; color: #c62828; }
</style>