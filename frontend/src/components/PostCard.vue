<!--
  @author beishi
  @date 2026/6/9
  @description PostCard component - displays post preview with date, category, title, summary, tags
-->
<script setup>
defineProps({
  post: {
    type: Object,
    required: true,
  },
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}
</script>

<template>
  <router-link :to="`/posts/${post.slug}`" class="post-card">
    <article>
      <div class="post-meta">
        <span class="post-date">{{ formatDate(post.created_at) }}</span>
        <span v-if="post.category" class="post-category">
          {{ post.category.name || post.category }}
        </span>
      </div>

      <h3 class="post-title">{{ post.title }}</h3>

      <p v-if="post.summary" class="post-summary">{{ post.summary }}</p>

      <div v-if="post.tags && post.tags.length" class="post-tags">
        <span
          v-for="tag in post.tags"
          :key="tag.id || tag"
          class="tag"
        >
          #{{ tag.name || tag }}
        </span>
      </div>
    </article>
  </router-link>
</template>

<style scoped>
.post-card {
  display: block;
  padding: 24px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--card-radius);
  text-decoration: none;
  color: var(--text-primary);
  transition: all 0.2s ease;
}

.post-card:hover {
  border-color: var(--border-hover);
  background: var(--bg-hover);
  transform: translateY(-2px);
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.post-date {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.post-category {
  font-size: 0.75rem;
  padding: 2px 10px;
  border-radius: 20px;
  background: var(--tag-bg);
  color: var(--tag-text);
}

.post-title {
  font-size: 1.15rem;
  font-weight: 600;
  line-height: 1.4;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.post-summary {
  font-size: 0.9rem;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  font-size: 0.75rem;
  padding: 2px 8px;
  border-radius: 6px;
  background: var(--tag-bg);
  color: var(--tag-text);
}
</style>
