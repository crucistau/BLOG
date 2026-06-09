<!--
  @author beishi
  @date 2026/6/9
  @description Posts list view - supports tag/category filtering and pagination
-->
<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import PostCard from '../components/PostCard.vue'
import Pagination from '../components/Pagination.vue'
import { getPosts } from '../api'

const route = useRoute()
const router = useRouter()

const posts = ref([])
const currentPage = ref(1)
const totalPages = ref(1)
const loading = ref(true)

async function fetchPosts() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: 12,
    }
    if (route.query.tag) {
      params.tag = route.query.tag
    }
    if (route.query.category) {
      params.category = route.query.category
    }

    const res = await getPosts(params)
    const data = res.data
    posts.value = data.items || data || []
    totalPages.value = data.total_pages || Math.ceil((data.total || 0) / 12) || 1
  } catch (err) {
    console.error('Posts.fetchPosts - error:', err.message)
    posts.value = []
  } finally {
    loading.value = false
  }
}

function onPageChange(page) {
  currentPage.value = page
  fetchPosts()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function clearFilters() {
  router.replace({ path: '/posts' })
}

watch(
  () => route.query,
  () => {
    currentPage.value = 1
    fetchPosts()
  }
)

onMounted(() => {
  fetchPosts()
})
</script>

<template>
  <div class="posts-page">
    <div class="posts-header">
      <h1 class="page-title">Posts</h1>
      <div v-if="route.query.tag || route.query.category" class="active-filters">
        <span v-if="route.query.tag" class="filter-tag">
          Tag: #{{ route.query.tag }}
        </span>
        <span v-if="route.query.category" class="filter-tag">
          Category: {{ route.query.category }}
        </span>
        <button class="clear-btn" @click="clearFilters">Clear</button>
      </div>
    </div>

    <div v-if="loading" class="loading">Loading...</div>

    <div v-else-if="posts.length" class="posts-grid">
      <PostCard
        v-for="post in posts"
        :key="post.id"
        :post="post"
      />
    </div>

    <p v-else class="empty">No posts found.</p>

    <Pagination
      v-if="!loading"
      :current-page="currentPage"
      :total-pages="totalPages"
      @page-change="onPageChange"
    />
  </div>
</template>

<style scoped>
.posts-page {
  padding: 40px 0 80px;
}

.posts-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32px;
  flex-wrap: wrap;
  gap: 12px;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
}

.active-filters {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-tag {
  padding: 4px 12px;
  border-radius: 20px;
  background: var(--tag-bg);
  color: var(--tag-text);
  font-size: 0.85rem;
}

.clear-btn {
  padding: 4px 12px;
  border-radius: 8px;
  background: var(--bg-hover);
  border: 1px solid var(--border);
  color: var(--text-secondary);
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.clear-btn:hover {
  border-color: var(--border-hover);
  color: var(--text-primary);
}

.posts-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.loading,
.empty {
  text-align: center;
  color: var(--text-muted);
  padding: 60px 0;
}

@media (max-width: 1023px) and (min-width: 769px) {
  .posts-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .posts-grid {
    grid-template-columns: 1fr;
  }

  .page-title {
    font-size: 1.5rem;
  }
}
</style>
