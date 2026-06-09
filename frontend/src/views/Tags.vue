<!--
  @author beishi
  @date 2026/6/9
  @description Tags view - grid of tag links showing post counts
-->
<script setup>
import { ref, onMounted } from 'vue'
import { getTags } from '../api'

const tags = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await getTags()
    tags.value = res.data || []
  } catch (err) {
    console.error('Tags.mounted fetchTags - error:', err.message)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="tags-page">
    <h1 class="page-title">Tags</h1>

    <div v-if="loading" class="loading">Loading...</div>

    <div v-else-if="tags.length" class="tags-grid">
      <router-link
        v-for="tag in tags"
        :key="tag.id"
        :to="`/posts?tag=${tag.slug}`"
        class="tag-card"
      >
        <span class="tag-name">#{{ tag.name }}</span>
        <span class="tag-count">{{ tag.post_count || 0 }} posts</span>
      </router-link>
    </div>

    <p v-else class="empty">No tags yet.</p>
  </div>
</template>

<style scoped>
.tags-page {
  padding: 40px 0 80px;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 32px;
  color: var(--text-primary);
}

.tags-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.tag-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 16px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--card-radius);
  text-decoration: none;
  color: var(--text-primary);
  transition: all 0.2s ease;
}

.tag-card:hover {
  border-color: var(--accent);
  transform: translateY(-2px);
}

.tag-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--tag-text);
  margin-bottom: 6px;
}

.tag-count {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.loading,
.empty {
  text-align: center;
  color: var(--text-muted);
  padding: 60px 0;
}

@media (max-width: 1023px) and (min-width: 769px) {
  .tags-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .tags-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .page-title {
    font-size: 1.5rem;
  }
}
</style>
