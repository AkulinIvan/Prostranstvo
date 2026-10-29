<template>
  <header class="hero">
    <div class="hero-badge">Пространство развития</div>
    <h1>{{ organizer.name }}</h1>
    <p class="subtitle">
      {{ organizer.bio || 'Игротехник, ведущий и организатор.' }}
    </p>
  </header>
</template>

<script setup>
defineProps({
  organizer: {
    type: Object,
    required: true
  }
})
defineEmits(['scroll-to-form']);
</script>

<style scoped>
.hero { text-align: center; padding: 80px 20px 60px; }
.hero-badge { display: inline-block; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.3em; color: var(--color-accent); margin-bottom: 25px; font-weight: 500; border-bottom: 1px solid var(--color-gold); padding-bottom: 5px; }
.hero h1 { font-family: var(--font-serif); font-size: 4.5rem; font-weight: 600; color: var(--color-text); line-height: 1.1; margin-bottom: 25px; }
.subtitle { font-size: 1.15rem; color: var(--color-text-light); max-width: 650px; margin: 0 auto 45px auto; font-weight: 300; line-height: 1.8; font-style: italic; font-family: var(--font-serif); font-size: 1.3rem;}
.btn-primary { background-color: var(--color-text); color: var(--color-bg); border: none; padding: 16px 40px; border-radius: 4px; font-size: 1rem; cursor: pointer; letter-spacing: 0.05em; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(47, 62, 54, 0.2); }
.btn-primary:hover { background-color: var(--color-accent); color: var(--color-white); transform: translateY(-2px); }
</style>