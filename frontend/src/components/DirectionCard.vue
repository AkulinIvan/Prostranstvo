<template>
  <article class="card">
    <!-- Если есть фото, показываем его -->
    <div v-if="direction.image" class="card-image">
      <img :src="getFullImageUrl(direction.image)" :alt="direction.title" />
    </div>
    <!-- Если фото нет, показываем иконку (номер) -->
    <div v-else class="card-number">{{ direction.icon || '01' }}</div>
    
    <div class="card-content">
      <h3>{{ direction.title }}</h3>
      <p>{{ direction.description }}</p>
    </div>
    
    <button class="btn-text" type="button" @click="$emit('open-details', direction)">
      Узнать больше <span class="arrow">→</span>
    </button>
  </article>
</template>

<script setup>
defineProps({
  direction: { type: Object, required: true },
});
defineEmits(['open-details']);

// Функция для формирования полного пути к картинке
const getFullImageUrl = (url) => {
  if (!url) return '';
  if (url.startsWith('http')) return url;
  // Если путь относительный (например, /media/...), добавляем адрес бэкенда
  return `http://127.0.0.1:8000${url}`;
};
</script>

<style scoped>
/* Ваши стили карточки */
.card {
  background: var(--color-white);
  padding: 40px 30px;
  border-radius: 2px;
  border: 1px solid rgba(197, 168, 128, 0.3);
  box-shadow: 0 10px 30px rgba(47, 62, 54, 0.03);
  transition: all 0.4s ease;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(47, 62, 54, 0.08);
  border-color: var(--color-gold);
}

/* Стили для картинки */
.card-image {
  width: calc(100% + 60px);
  height: 180px;
  margin: -40px -30px 20px -30px;
  overflow: hidden;
}
.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-number {
  font-family: var(--font-serif);
  font-size: 1.2rem;
  color: var(--color-gold);
  margin-bottom: 20px;
  font-style: italic;
}

.card-content { flex-grow: 1; }

.card h3 {
  font-family: var(--font-serif);
  font-size: 1.8rem;
  color: var(--color-text);
  margin-bottom: 15px;
  line-height: 1.2;
}

.card p {
  font-size: 0.95rem;
  color: var(--color-text-light);
  margin-bottom: 30px;
  line-height: 1.7;
}

.btn-text {
  background: none;
  border: none;
  color: var(--color-text);
  font-weight: 500;
  cursor: pointer;
  padding: 0;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: color 0.3s;
  align-self: flex-start;
}

.btn-text:hover { color: var(--color-accent); }
.arrow { transition: transform 0.3s ease; }
.btn-text:hover .arrow { transform: translateX(5px); }
</style>