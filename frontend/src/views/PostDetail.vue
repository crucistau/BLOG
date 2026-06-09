<!--
  @author beishi
  @date 2026/6/9
  @description Post detail view - renders content_html with styled code blocks
-->
<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getPost } from '../api'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'

const route = useRoute()
const router = useRouter()

const post = ref(null)
const loading = ref(true)
const error = ref(null)

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

function highlightCodeBlocks() {
  const blocks = document.querySelectorAll('.post-content pre code')
  blocks.forEach((block) => {
    hljs.highlightElement(block)
  })
}

onMounted(async () => {
  try {
    const res = await getPost(route.params.slug)
    post.value = res.data
  } catch (err) {
    console.error('PostDetail.mounted fetchPost - error:', err.message)
    error.value = 'Post not found'
  } finally {
    loading.value = false
  }

  setTimeout(highlightCodeBlocks, 100)
})
</script>

<template>
  <div class="post-detail">
    <div v-if="loading" class="loading">Loading...</div>

    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <router-link to="/posts" class="back-link">&larr; Back to Posts</router-link>
    </div>

    <article v-else-if="post" class="post-article">
      <div class="post-header">
        <router-link to="/posts" class="back-link">&larr; Back to Posts</router-link>

        <div class="post-meta">
          <span class="post-date">{{ formatDate(post.created_at) }}</span>
          <span v-if="post.category" class="post-category">
            {{ post.category.name || post.category }}
          </span>
        </div>

        <h1 class="post-title">{{ post.title }}</h1>

        <div v-if="post.tags && post.tags.length" class="post-tags">
          <router-link
            v-for="tag in post.tags"
            :key="tag.id || tag"
            :to="`/posts?tag=${tag.slug || tag}`"
            class="tag"
          >
            #{{ tag.name || tag }}
          </router-link>
        </div>
      </div>

      <div
        class="post-content"
        v-html="post.content_html"
      />
    </article>
  </div>
</template>

<style scoped>
.post-detail {
  padding: 40px 0 80px;
  max-width: 800px;
  margin: 0 auto;
}

.loading,
.error {
  text-align: center;
  color: var(--text-muted);
  padding: 60px 0;
}

.back-link {
  display: inline-block;
  margin-bottom: 24px;
  font-size: 0.9rem;
  color: var(--text-secondary);
  transition: color 0.2s ease;
}

.back-link:hover {
  color: var(--accent);
}

.post-header {
  margin-bottom: 40px;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.post-date {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.post-category {
  font-size: 0.8rem;
  padding: 2px 12px;
  border-radius: 20px;
  background: var(--tag-bg);
  color: var(--tag-text);
}

.post-title {
  font-size: 2.2rem;
  font-weight: 700;
  line-height: 1.3;
  margin-bottom: 16px;
  color: var(--text-primary);
}

.post-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  padding: 4px 10px;
  border-radius: 6px;
  background: var(--tag-bg);
  color: var(--tag-text);
  font-size: 0.8rem;
  transition: all 0.2s ease;
}

.tag:hover {
  color: var(--accent);
}

.post-content {
  font-size: 1.05rem;
  line-height: 1.8;
  color: var(--text-primary);
}

.post-content :deep(h1),
.post-content :deep(h2),
.post-content :deep(h3),
.post-content :deep(h4) {
  margin-top: 2em;
  margin-bottom: 0.6em;
  font-weight: 600;
  color: var(--text-primary);
}

.post-content :deep(h2) {
  font-size: 1.6rem;
}

.post-content :deep(h3) {
  font-size: 1.3rem;
}

.post-content :deep(p) {
  margin-bottom: 1.2em;
}

.post-content :deep(a) {
  color: var(--accent);
  text-decoration: underline;
}

.post-content :deep(blockquote) {
  border-left: 3px solid var(--accent);
  padding: 12px 20px;
  margin: 1.5em 0;
  background: var(--bg-hover);
  border-radius: 0 8px 8px 0;
  color: var(--text-secondary);
}

.post-content :deep(code) {
  padding: 2px 6px;
  border-radius: 4px;
  background: var(--bg-hover);
  font-size: 0.9em;
}

.post-content :deep(pre) {
  margin: 1.5em 0;
  padding: 20px;
  border-radius: 10px;
  background: #1a1b26;
  overflow-x: auto;
}

.post-content :deep(pre code) {
  padding: 0;
  background: none;
  font-size: 0.9rem;
  line-height: 1.6;
}

.post-content :deep(ul),
.post-content :deep(ol) {
  margin: 1em 0;
  padding-left: 2em;
}

.post-content :deep(li) {
  margin-bottom: 0.4em;
}

.post-content :deep(img) {
  border-radius: 8px;
  margin: 1.5em 0;
  max-width: 100%;
}

.post-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1.5em 0;
}

.post-content :deep(th),
.post-content :deep(td) {
  padding: 10px 14px;
  border: 1px solid var(--border);
  text-align: left;
}

.post-content :deep(th) {
  background: var(--bg-hover);
  font-weight: 600;
}

@media (max-width: 768px) {
  .post-title {
    font-size: 1.6rem;
  }

  .post-content {
    font-size: 1rem;
  }
}
</style>
