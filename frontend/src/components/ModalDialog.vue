<!-- frontend\src\components\ModalDialog.vue -->
<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen" class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-content" role="dialog" aria-modal="true">
          <button class="modal-close" @click="$emit('close')" aria-label="Закрыть окно">
            &times;
          </button>
          
          <div class="modal-header">
            <span class="modal-badge">Направление</span>
            <h2>{{ title }}</h2>
          </div>
          
          <div class="modal-body" v-html="description"></div>
          
          <div class="modal-footer">
            <button class="btn-primary" @click="$emit('action')">
              Записаться на курс
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({
  isOpen: Boolean,
  title: String,
  description: String,
});

defineEmits(['close', 'action']);
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(47, 62, 54, 0.6); /* Хвойный полупрозрачный */
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: var(--color-bg);
  width: 100%;
  max-width: 600px;
  border-radius: 4px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  position: relative;
  padding: 40px;
  max-height: 90vh;
  overflow-y: auto;
  border-top: 4px solid var(--color-accent);
}

.modal-close {
  position: absolute;
  top: 15px;
  right: 20px;
  background: none;
  border: none;
  font-size: 2rem;
  color: var(--color-text-light);
  cursor: pointer;
  transition: color 0.3s;
  line-height: 1;
}

.modal-close:hover {
  color: var(--color-accent);
}

.modal-header {
  margin-bottom: 25px;
  text-align: center;
}

.modal-badge {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  color: var(--color-gold);
  display: block;
  margin-bottom: 10px;
}

.modal-header h2 {
  font-family: var(--font-serif);
  font-size: 2.2rem;
  color: var(--color-text);
  line-height: 1.2;
}

.modal-body {
  font-size: 1rem;
  color: var(--color-text-light);
  line-height: 1.7;
  margin-bottom: 30px;
}

/* Стилизация текста внутри описания */
.modal-body :deep(p) {
  margin-bottom: 15px;
}
.modal-body :deep(ul) {
  margin-left: 20px;
  margin-bottom: 15px;
}
.modal-body :deep(li) {
  margin-bottom: 8px;
}
.modal-body :deep(strong) {
  color: var(--color-text);
  font-weight: 600;
}

.modal-footer {
  text-align: center;
  border-top: 1px solid rgba(197, 168, 128, 0.3);
  padding-top: 25px;
}

.btn-primary {
  background-color: var(--color-text);
  color: var(--color-bg);
  border: none;
  padding: 15px 35px;
  border-radius: 2px;
  font-size: 1rem;
  cursor: pointer;
  letter-spacing: 0.05em;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  background-color: var(--color-accent);
  color: var(--color-white);
}

/* Анимации (Vue Transition) */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-content,
.modal-leave-active .modal-content {
  transition: transform 0.3s ease;
}

.modal-enter-from .modal-content,
.modal-leave-to .modal-content {
  transform: translateY(20px) scale(0.95);
}

@media (max-width: 600px) {
  .modal-content {
    padding: 30px 20px;
  }
  .modal-header h2 {
    font-size: 1.8rem;
  }
}
</style>