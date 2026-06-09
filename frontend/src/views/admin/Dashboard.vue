<!--
  @author beishi
  @date 2026/6/9
  @description Admin dashboard - stats row, post table with actions, logout button
-->
<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../../stores/app'
import {
  adminGetPosts,
  adminGetTags,
  adminGetCategories,
  adminDeletePost,
  adminTogglePublish,
} from '../../api'

const router = useRouter()
const appStore = useAppStore()

const posts = ref([])
const stats = ref({ posts: 0, tags: 0, categories: 0 })
const loading = ref(true)

async function fetchDashboard() {
  loading.value = true
  try {
    const [postsRes, tagsRes, categoriesRes] = await Promise.all([
      adminGetPosts({ page: 1, page_size: 50 }),
      adminGetTags(),
      adminGetCategories(),
    ])
    posts.value = postsRes.data?.items || postsRes.data || []
    stats.value = {
      posts: postsRes.data?.total || posts.value.length,
      tags: tagsRes.data?.length || 0,
      categories: categoriesRes.data?.length || 0,
    }
  } catch (err) {
    console.error('Dashboard.fetchDashboard - error:', err.message)
  } finally {
    loading.value = false
  }
}

async function handleTogglePublish(post) {
  try {
    await adminTogglePublish(post.id)
    await fetchDashboard()
  } catch (err) {
    console.error('Dashboard.handleTogglePublish - error:', err.message)
  }
}

async function handleDelete(post) {
  if (!confirm(`Delete "${post.title}"? This cannot be undone.`)) return
  try {
    await adminDeletePost(post.id)
    await fetchDashboard()
  } catch (err) {
    console.error('Dashboard.handleDelete - error:', err.message)
  }
}

function handleLogout() {
  appStore.logout()
  router.push('/admin/login')
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

onMounted(() => {
  fetchDashboard()
})
</script>

<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1 class="page-title">Dashboard</h1>
      <div class="header-actions">
        <router-link to="/admin/posts/new" class="new-post-btn">
          + New Post
        </router-link>
        <button class="logout-btn" @click="handleLogout">Logout</button>
      </div>
    </div>

    <!-- Stats Row -->
    <div class="stats-row">
      <div class="stat-card">
        <span class="stat-number">{{ stats.posts }}</span>
        <span class="stat-label">Posts</span>
      </div>
      <div class="stat-card">
        <span class="stat-number">{{ stats.tags }}</span>
        <span class="stat-label">Tags</span>
      </div>
      <div class="stat-card">
        <span class="stat-number">{{ stats.categories }}</span>
        <span class="stat-label">Categories</span>
      </div>
    </div>

    <!-- Posts Table -->
    <div class="posts-section">
      <h2 class="section-title">Posts</h2>

      <div v-if="loading" class="loading">Loading...</div>

      <div v-else-if="posts.length" class="table-wrapper">
        <table class="posts-table">
          <thead>
            <tr>
              <th>Title</th>
              <th>Status</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="post in posts" :key="post.id">
              <td class="post-title-cell">
                <router-link :to="`/admin/posts/${post.id}/edit`">
                  {{ post.title }}
                </router-link>
              </td>
              <td>
                <span
                  class="status-badge"
                  :class="post.is_published ? 'published' : 'draft'"
                >
                  {{ post.is_published ? 'Published' : 'Draft' }}
                </span>
              </td>
              <td class="date-cell">{{ formatDate(post.created_at) }}</td>
              <td class="actions-cell">
                <router-link
                  :to="`/admin/posts/${post.id}/edit`"
                  class="action-btn edit-btn"
                >
                  Edit
                </router-link>
                <button
                  class="action-btn publish-btn"
                  @click="handleTogglePublish(post)"
                >
                  {{ post.is_published ? 'Unpublish' : 'Publish' }}
                </button>
                <button
                  class="action-btn delete-btn"
                  @click="handleDelete(post)"
                >
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <p v-else class="empty">No posts yet. Create your first post!</p>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  padding: 40px 0 80px;
}

.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32px;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
}

.header-actions {
  display: flex;
  gap: 10px;
}

.new-post-btn {
  padding: 10px 20px;
  border-radius: 8px;
  background: var(--accent);
  color: var(--bg);
  font-size: 0.9rem;
  font-weight: 600;
  text-decoration: none;
  transition: opacity 0.2s ease;
}

.new-post-btn:hover {
  opacity: 0.9;
}

.logout-btn {
  padding: 10px 20px;
  border-radius: 8px;
  background: var(--bg-hover);
  border: 1px solid var(--border);
  color: var(--text-secondary);
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.logout-btn:hover {
  border-color: var(--border-hover);
  color: var(--text-primary);
}

/* Stats */
.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 40px;
}

.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--card-radius);
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: var(--accent);
}

.stat-label {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-top: 4px;
}

/* Table */
.section-title {
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--text-primary);
}

.table-wrapper {
  overflow-x: auto;
}

.posts-table {
  width: 100%;
  border-collapse: collapse;
}

.posts-table th,
.posts-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--border);
}

.posts-table th {
  font-size: 0.8rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 500;
}

.post-title-cell a {
  color: var(--text-primary);
  text-decoration: none;
  font-weight: 500;
}

.post-title-cell a:hover {
  color: var(--accent);
}

.date-cell {
  color: var(--text-muted);
  font-size: 0.85rem;
}

.status-badge {
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.published {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.status-badge.draft {
  background: var(--tag-bg);
  color: var(--tag-text);
}

.actions-cell {
  display: flex;
  gap: 6px;
}

.action-btn {
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
}

.edit-btn {
  background: var(--bg-hover);
  border: 1px solid var(--border);
  color: var(--text-secondary);
}

.edit-btn:hover {
  border-color: var(--border-hover);
  color: var(--text-primary);
}

.publish-btn {
  background: var(--bg-hover);
  border: 1px solid var(--border);
  color: var(--text-secondary);
}

.publish-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.delete-btn {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.delete-btn:hover {
  background: rgba(239, 68, 68, 0.2);
}

.loading,
.empty {
  text-align: center;
  color: var(--text-muted);
  padding: 40px;
}

@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .page-title {
    font-size: 1.5rem;
  }

  .stats-row {
    grid-template-columns: 1fr;
  }
}
</style>
