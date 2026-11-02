<template>
  <section class="reviews-section">
    <div class="section-header">
      <h2>Отзывы</h2>
      <p class="section-desc">Что говорят те, кто уже был на встречах.</p>
    </div>

    <div v-if="reviews.length" class="reviews-grid">
      <div v-for="review in reviews" :key="review.id" class="review-card">
        <div class="review-stars">{{ '★'.repeat(review.rating) }}{{ '☆'.repeat(5 - review.rating) }}</div>
        <p class="review-text">«{{ review.text }}»</p>
        <p class="review-author">— {{ review.author_name }}</p>
      </div>
    </div>
    <div v-else class="empty-reviews"><p>Пока нет отзывов. Станьте первым!</p></div>

    <div class="add-review-box">
      <h3>Оставить отзыв</h3>
      <form @submit.prevent="submitReview" class="review-form">
        <input v-model="form.author_name" placeholder="Ваше имя" required />
        <div class="rating-input">
          <span>Оценка:</span>
          <span v-for="star in 5" :key="star" @click="form.rating = star" class="star-btn" :class="{ active: star <= form.rating }">★</span>
        </div>
        <textarea v-model="form.text" placeholder="Поделитесь впечатлениями..." required></textarea>
        <button type="submit" :disabled="loading">{{ loading ? 'Отправка...' : 'Отправить отзыв' }}</button>
      </form>
      <p v-if="message" :class="messageType">{{ message }}</p>
    </div>
  </section>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'

const route = useRoute()
const slug = route.params.slug
const reviews = ref([])
const loading = ref(false)
const message = ref('')
const messageType = ref('')
const form = reactive({ author_name: '', text: '', rating: 5 })

const fetchReviews = async () => {
  try {
    const { data } = await api.get(`/public/${slug}/reviews/`)
    reviews.value = data
  } catch (e) { console.error(e) }
}

const submitReview = async () => {
  loading.value = true
  try {
    await api.post(`/public/${slug}/reviews/`, form)
    message.value = 'Спасибо! Отзыв отправлен на модерацию.'
    messageType.value = 'success'
    Object.assign(form, { author_name: '', text: '', rating: 5 })
  } catch (e) {
    message.value = 'Ошибка отправки'
    messageType.value = 'error'
  } finally { loading.value = false }
}
onMounted(fetchReviews)
</script>

<style scoped>
.reviews-section { padding: 60px 0; }
.section-header { text-align: center; margin-bottom: 40px; }
.section-header h2 { font-family: var(--font-serif); font-size: 2.8rem; margin-bottom: 15px; }
.reviews-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 25px; margin-bottom: 50px; }
.review-card { background: white; padding: 30px; border-radius: 4px; border-left: 4px solid var(--color-gold); box-shadow: 0 5px 15px rgba(0,0,0,0.03); }
.review-stars { color: #f5a623; font-size: 1.2rem; margin-bottom: 15px; }
.review-text { font-style: italic; color: var(--color-text); margin-bottom: 15px; line-height: 1.6; }
.review-author { font-family: var(--font-serif); color: var(--color-accent); font-weight: 600; }
.empty-reviews { text-align: center; color: var(--color-text-light); margin-bottom: 40px; }
.add-review-box { background: white; padding: 40px; border-radius: 4px; max-width: 600px; margin: 0 auto; border-top: 4px solid var(--color-accent); }
.add-review-box h3 { font-family: var(--font-serif); font-size: 1.8rem; margin-bottom: 20px; text-align: center; }
.review-form { display: flex; flex-direction: column; gap: 15px; }
.review-form input, .review-form textarea { padding: 15px; border: 1px solid rgba(197, 168, 128, 0.5); border-radius: 2px; font-family: var(--font-sans); }
.review-form textarea { min-height: 100px; resize: vertical; }
.rating-input { display: flex; align-items: center; gap: 10px; font-size: 1.5rem; }
.star-btn { cursor: pointer; color: #ddd; transition: 0.2s; }
.star-btn.active { color: #f5a623; }
.review-form button { background: var(--color-text); color: white; padding: 15px; border: none; cursor: pointer; border-radius: 2px; font-size: 1rem; }
.review-form button:hover:not(:disabled) { background: var(--color-accent); }
.message { margin-top: 15px; text-align: center; }
.success { color: #2e7d32; } .error { color: #c62828; }
</style>