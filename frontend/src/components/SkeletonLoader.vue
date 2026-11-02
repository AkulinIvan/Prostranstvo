<template>
  <div class="skeleton-wrapper">
    <div class="skeleton-hero"></div>
    <div class="skeleton-filters"></div>
    <div class="skeleton-cards">
      <div v-for="i in 3" :key="i" class="skeleton-card"></div>
    </div>
  </div>
</template>
<style scoped>
.skeleton-wrapper { max-width: 900px; margin: 0 auto; padding: 40px 20px; }
.skeleton-hero { height: 250px; background: #e0e0e0; border-radius: 8px; margin-bottom: 40px; animation: pulse 1.5s infinite; }
.skeleton-filters { height: 40px; width: 60%; background: #e0e0e0; border-radius: 50px; margin: 0 auto 30px; animation: pulse 1.5s infinite; }
.skeleton-cards { display: flex; flex-direction: column; gap: 20px; }
.skeleton-card { height: 120px; background: #e0e0e0; border-radius: 8px; animation: pulse 1.5s infinite; }
@keyframes pulse { 0% { opacity: 0.6; } 50% { opacity: 1; } 100% { opacity: 0.6; } }
</style>