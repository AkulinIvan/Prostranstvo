<!-- frontend\src\App.vue -->
<template>
  <router-view />
</template>

<script setup>
</script>

<style scoped>
.page-wrapper {
  position: relative;
  min-height: 100vh;
  padding: 40px 20px;
  overflow: hidden;
  background-color: var(--color-bg);
}

/* 1. Текстура бумаги (шум) */
.bg-texture {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  /* Используем SVG-шум для эффекта пергамента */
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.04'/%3E%3C/svg%3E");
  opacity: 0.8;
}

/* 2. Геометрический паттерн */
.bg-geometry {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 150vh; /* Большой размер, чтобы выходило за края */
  height: 150vh;
  z-index: 0;
  pointer-events: none;
  color: var(--color-gold);
  opacity: 0.08; /* Едва заметно, создает глубину */
  animation: slow-spin 120s linear infinite; /* Медленное вращение */
}

@keyframes slow-spin {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

/* Останавливаем анимацию для тех, кто предпочитает меньше движения */
@media (prefers-reduced-motion: reduce) {
  .bg-geometry {
    animation: none;
  }
}

/* Контент поверх фона */
.content {
  position: relative;
  z-index: 1;
  max-width: 900px;
  margin: 0 auto;
}

.organizer-access {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 100;
}
</style>