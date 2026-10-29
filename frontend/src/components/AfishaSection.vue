<!-- frontend\src\components\AfishaSection.vue -->
<template>
  <section class="afisha" aria-labelledby="afisha-title">
    <div class="section-header">
      <h2 id="afisha-title">Ближайшие встречи</h2>
      <p class="section-desc">Выберите событие, которое вам откликается, и присоединяйтесь.</p>
    </div>

    <!-- Сетка событий -->
    <div v-if="events.length" class="events-grid">
      <div v-for="event in events" :key="event.id" class="event-card">
        
        <!-- Блок с датой (слева) -->
        <div class="event-date-block">
          <span class="event-day">{{ getDay(event.date) }}</span>
          <span class="event-month">{{ getMonth(event.date) }}</span>
          <span class="event-time">{{ getTime(event.date) }}</span>
        </div>

        <!-- Информация о событии (по центру) -->
        <div class="event-info">
          <h3>{{ event.title }}</h3>
          <p class="event-desc">{{ event.description }}</p>
          
          <div class="event-meta">
            <span v-if="event.location" class="event-loc">📍 {{ event.location }}</span>
            <span class="event-direction">Направление: {{ event.direction }}</span>
          </div>
        </div>

        <!-- Кнопка (справа) -->
        <div class="event-action">
          <button class="btn-event" @click="$emit('select-event', event)">
            Записаться
            <span class="arrow">→</span>
          </button>
        </div>

      </div>
    </div>
    
    <!-- Если событий нет -->
    <div v-else class="empty-state">
      <p>Пока нет запланированных встреч.</p>
      <p class="empty-sub">Загляните позже или напишите мне напрямую!</p>
    </div>
  </section>
</template>

<script setup>
defineProps({
  events: {
    type: Array,
    default: () => []
  }
});

defineEmits(['select-event']);

// Функции для красивого форматирования даты
const getDay = (isoString) => new Date(isoString).toLocaleDateString('ru-RU', { day: 'numeric' });
const getMonth = (isoString) => new Date(isoString).toLocaleDateString('ru-RU', { month: 'short' }).replace('.', '');
const getTime = (isoString) => new Date(isoString).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
</script>

<style scoped>
.afisha {
  padding: 60px 0;
}

.section-header {
  text-align: center;
  margin-bottom: 50px;
}

.afisha h2 {
  font-family: var(--font-serif);
  font-size: 2.8rem;
  color: var(--color-text);
  margin-bottom: 15px;
}

.section-desc {
  color: var(--color-text-light);
  font-size: 1.05rem;
}

/* Сетка карточек */
.events-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 850px;
  margin: 0 auto;
}

/* Карточка события */
.event-card {
  display: flex;
  align-items: stretch;
  background: var(--color-white);
  border-radius: 4px;
  box-shadow: 0 10px 30px rgba(47, 62, 54, 0.04);
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border-left: 4px solid var(--color-accent);
}

.event-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 15px 40px rgba(47, 62, 54, 0.08);
}

/* Блок с датой */
.event-date-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 25px 30px;
  background: #FDFBF7; /* Очень светлый фон для контраста */
  border-right: 1px solid rgba(197, 168, 128, 0.2);
  min-width: 120px;
}

.event-day {
  font-family: var(--font-serif);
  font-size: 2.5rem;
  font-weight: 600;
  color: var(--color-text);
  line-height: 1;
}

.event-month {
  font-family: var(--font-sans);
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--color-accent);
  margin-top: 5px;
  font-weight: 500;
}

.event-time {
  font-size: 0.85rem;
  color: var(--color-text-light);
  margin-top: 8px;
}

/* Информация */
.event-info {
  flex-grow: 1;
  padding: 30px;
}

.event-info h3 {
  font-family: var(--font-serif);
  font-size: 1.6rem;
  color: var(--color-text);
  margin-bottom: 10px;
  line-height: 1.2;
}

.event-desc {
  color: var(--color-text-light);
  font-size: 0.95rem;
  margin-bottom: 15px;
  line-height: 1.6;
}

.event-meta {
  display: flex;
  gap: 20px;
  font-size: 0.85rem;
  color: var(--color-gold);
}

/* Кнопка */
.event-action {
  display: flex;
  align-items: center;
  padding: 30px;
  border-left: 1px solid rgba(197, 168, 128, 0.2);
}

.btn-event {
  background: transparent;
  border: 1px solid var(--color-text);
  color: var(--color-text);
  padding: 12px 24px;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-event .arrow {
  transition: transform 0.3s ease;
}

.btn-event:hover {
  background: var(--color-text);
  color: var(--color-white);
}

.btn-event:hover .arrow {
  transform: translateX(5px);
}

/* Пустое состояние */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: var(--color-white);
  border-radius: 4px;
  border: 1px dashed var(--color-gold);
  max-width: 850px;
  margin: 0 auto;
}
.empty-state p {
  font-family: var(--font-serif);
  font-size: 1.5rem;
  color: var(--color-text);
}
.empty-sub {
  font-family: var(--font-sans) !important;
  font-size: 1rem !important;
  color: var(--color-text-light) !important;
  margin-top: 10px;
}

/* Адаптивность для мобильных */
@media (max-width: 768px) {
  .event-card {
    flex-direction: column;
    border-left: none;
    border-top: 4px solid var(--color-accent);
  }
  
  .event-date-block {
    flex-direction: row;
    gap: 15px;
    padding: 15px 20px;
    border-right: none;
    border-bottom: 1px solid rgba(197, 168, 128, 0.2);
    justify-content: flex-start;
    align-items: baseline;
  }
  
  .event-day { font-size: 2rem; }
  .event-month { margin-top: 0; }
  .event-time { margin-top: 0; margin-left: auto; } /* Время уходит вправо */
  
  .event-info { padding: 20px; }
  .event-action { padding: 0 20px 20px; border-left: none; }
  .btn-event { width: 100%; justify-content: center; }
}
</style>