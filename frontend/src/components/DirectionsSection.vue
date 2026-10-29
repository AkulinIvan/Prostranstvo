<template>
  <section class="directions" aria-labelledby="directions-title">
    <div class="section-header">
      <h2 id="directions-title">Мои направления</h2>
      <p class="section-desc">Выберите то, что сейчас откликается вам больше всего.</p>
    </div>

    <div class="cards">
      <DirectionCard
        v-for="dir in directions"
        :key="dir.id"
        :direction="dir"
        @open-details="$emit('open-details', $event)"
      />
    </div>
  </section>
</template>

<script setup>
import DirectionCard from './DirectionCard.vue';

// Принимаем направления из родительского компонента
defineProps({
  directions: {
    type: Array,
    default: () => []
  }
});

defineEmits(['open-details']);
</script>

<style scoped>
/* Ваши стили */
.directions { padding: 60px 0; }
.section-header { text-align: center; margin-bottom: 50px; }
.directions h2 { font-family: var(--font-serif); font-size: 2.8rem; color: var(--color-text); margin-bottom: 15px; }
.section-desc { color: var(--color-text-light); font-size: 1.05rem; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 25px; }
</style>