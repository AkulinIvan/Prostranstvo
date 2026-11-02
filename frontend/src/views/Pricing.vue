<template>
  <div class="pricing-page">
    <h1>Выберите тариф</h1>
    <div class="plans-grid">
      <div v-for="plan in plans" :key="plan.id" class="plan-card" :class="{ 'popular': plan.slug === 'pro' }">
        <h2>{{ plan.name }}</h2>
        <p class="price">{{ plan.price }} ₽ <span>/ мес</span></p>
        <ul>
          <li v-if="plan.max_events === 0">Безлимит событий</li>
          <li v-else>До {{ plan.max_events }} событий</li>
          <li v-if="plan.has_calendar_sync">Синхронизация с календарем</li>
        </ul>
        <button @click="pay(plan)" class="btn-buy">
          {{ plan.price == 0 ? 'Начать бесплатно' : 'Оформить' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const plans = ref([])

onMounted(async () => {
  const { data } = await api.get('/billing/plans/')
  plans.value = data
})

const pay = async (plan) => {
  if (plan.price == 0) return alert('Вы уже на бесплатном тарифе')
  try {
    const { data } = await api.post(`/billing/pay/${plan.id}/`)
    window.location.href = data.payment_url // Перенаправляем на ЮKassa
  } catch (e) {
    alert('Ошибка создания платежа')
  }
}
</script>

<style scoped>
/* Стили для карточек тарифов */
.pricing-page { padding: 80px 20px; max-width: 1000px; margin: 0 auto; text-align: center; }
.plans-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 30px; margin-top: 50px; }
.plan-card { background: white; padding: 40px 30px; border-radius: 8px; border-top: 4px solid var(--color-gold); box-shadow: 0 10px 30px rgba(0,0,0,0.05); }
.plan-card.popular { border-top-color: var(--color-accent); transform: scale(1.05); }
.price { font-size: 2.5rem; font-family: var(--font-serif); margin: 20px 0; }
.btn-buy { background: var(--color-text); color: white; width: 100%; padding: 15px; border: none; border-radius: 4px; cursor: pointer; font-size: 1rem; margin-top: 30px; }
</style>