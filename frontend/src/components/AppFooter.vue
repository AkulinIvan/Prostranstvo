<template>
  <footer class="footer">
    <div class="footer-line"></div>
    <p class="footer-copy">© {{ year }} Все права защищены.</p>
  </footer>
</template>

<script setup>
defineProps({
  organizer: {
    type: Object,
    default: () => ({})
  }
})
const year = new Date().getFullYear();
</script>

<style scoped>
.footer { text-align: center; padding: 60px 0 20px; color: var(--color-text-light); font-size: 0.9rem; position: relative; z-index: 1; }
.footer-line { width: 40px; height: 1px; background: var(--color-gold); margin: 0 auto 20px; }
.footer-name { font-family: var(--font-serif); font-size: 1.2rem; color: var(--color-text); margin-bottom: 5px; }
.footer-desc { font-size: 0.85rem; margin-bottom: 20px; opacity: 0.8; }
.footer-copy { font-size: 0.75rem; opacity: 0.6; }
</style>