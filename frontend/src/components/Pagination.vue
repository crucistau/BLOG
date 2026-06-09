<!--
  @author beishi
  @date 2026/6/9
  @description Pagination component with prev/next buttons and page numbers
-->
<script setup>
defineProps({
  currentPage: {
    type: Number,
    required: true,
  },
  totalPages: {
    type: Number,
    required: true,
  },
})

defineEmits(['page-change'])
</script>

<template>
  <div v-if="totalPages > 1" class="pagination">
    <button
      class="page-btn"
      :disabled="currentPage <= 1"
      @click="$emit('page-change', currentPage - 1)"
    >
      &larr; Prev
    </button>

    <div class="page-numbers">
      <button
        v-for="page in totalPages"
        :key="page"
        class="page-num"
        :class="{ active: page === currentPage }"
        @click="$emit('page-change', page)"
      >
        {{ page }}
      </button>
    </div>

    <button
      class="page-btn"
      :disabled="currentPage >= totalPages"
      @click="$emit('page-change', currentPage + 1)"
    >
      Next &rarr;
    </button>
  </div>
</template>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 40px;
}

.page-btn {
  padding: 8px 16px;
  border-radius: 8px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  color: var(--text-secondary);
  font-size: 0.85rem;
  transition: all 0.2s ease;
}

.page-btn:hover:not(:disabled) {
  border-color: var(--border-hover);
  color: var(--text-primary);
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 4px;
}

.page-num {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  color: var(--text-secondary);
  font-size: 0.85rem;
  transition: all 0.2s ease;
}

.page-num:hover {
  border-color: var(--border-hover);
  color: var(--text-primary);
}

.page-num.active {
  background: var(--accent);
  border-color: var(--accent);
  color: var(--bg);
}

@media (max-width: 768px) {
  .pagination {
    gap: 8px;
  }

  .page-numbers {
    display: none;
  }
}
</style>
