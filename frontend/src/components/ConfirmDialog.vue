<template>
  <div v-if="isOpen" class="modal-overlay" @click="close">
    <div class="modal-content" @click.stop>
      <div class="modal-body">
        <div class="icon warning">⚠️</div>
        <h2>{{ title }}</h2>
        <p>{{ message }}</p>
      </div>

      <div class="modal-actions">
        <button class="btn btn-secondary" @click="close">
          Cancel
        </button>
        <button class="btn btn-danger" @click="confirm">
          {{ confirmText || 'Delete' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  isOpen: Boolean,
  title: {
    type: String,
    default: 'Are you sure?'
  },
  message: {
    type: String,
    default: 'This action cannot be undone.'
  },
  confirmText: String
})

const emit = defineEmits(['close', 'confirm'])

const close = () => {
  emit('close')
}

const confirm = () => {
  emit('confirm')
  close()
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  padding: 0;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.modal-body {
  padding: 30px 20px 20px;
  text-align: center;
}

.icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.icon.warning {
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.modal-body h2 {
  margin: 16px 0 12px;
  font-size: 18px;
  color: #333;
}

.modal-body p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  padding: 20px;
  border-top: 1px solid #eee;
}

.btn {
  flex: 1;
  padding: 10px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-secondary {
  background: #f0f0f0;
  color: #333;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-danger:hover {
  background: #c82333;
}
</style>
