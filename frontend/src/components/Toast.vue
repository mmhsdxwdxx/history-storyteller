<template>
  <Transition name="toast">
    <div v-if="show" :class="['toast', `toast-${type}`]">
      {{ message }}
    </div>
  </Transition>
</template>

<script>
export default {
  props: {
    show: Boolean,
    message: String,
    type: {
      type: String,
      default: 'info'
    }
  }
}
</script>

<style scoped>
.toast {
  position: fixed;
  top: var(--spacing-lg);
  right: var(--spacing-lg);
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--radius-md);
  color: var(--color-white);
  font-weight: 500;
  box-shadow: var(--shadow-lg);
  z-index: 1000;
  max-width: 400px;
}

.toast-success { background: var(--color-completed); }
.toast-error { background: var(--color-error); }
.toast-warning { background: var(--color-processing); }
.toast-info { background: var(--color-jade); }

.toast-enter-active, .toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.toast-leave-to {
  opacity: 0;
}
</style>
