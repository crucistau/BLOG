<!--
  @author beishi
  @date 2026/6/9
  @description Home page with Bento Grid layout - hero, profile, social, featured post, categories, tags, recent posts
-->
<script setup>
import { ref, onMounted } from 'vue'
import PostCard from '../components/PostCard.vue'
import { getPosts, getTags, getCategories } from '../api'

const recentPosts = ref([])
const tags = ref([])
const categories = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const [postsRes, tagsRes, categoriesRes] = await Promise.all([
      getPosts({ page: 1, page_size: 6 }),
      getTags(),
      getCategories(),
    ])
    recentPosts.value = postsRes.data?.items || postsRes.data || []
    tags.value = tagsRes.data || []
    categories.value = categoriesRes.data || []
  } catch (err) {
    console.error('Home.mounted fetchData - error:', err.message)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="home">
    <!-- Bento Grid -->
    <section class="bento-grid">
      <!-- Hero (span 2 rows) -->
      <div class="bento-card bento-hero">
        <h1 class="hero-greeting">Hello, I'm a Developer</h1>
        <p class="hero-subtitle">Welcome to my devlog.</p>
        <div class="hero-stats">
          <div class="stat">
            <span class="stat-number">{{ recentPosts.length }}</span>
            <span class="stat-label">Posts</span>
          </div>
          <div class="stat">
            <span class="stat-number">{{ tags.length }}</span>
            <span class="stat-label">Tags</span>
          </div>
          <div class="stat">
            <span class="stat-number">{{ categories.length }}</span>
            <span class="stat-label">Categories</span>
          </div>
        </div>
      </div>

      <!-- Profile card -->
      <div class="bento-card bento-profile">
        <div class="profile-avatar">&#128187;</div>
        <h2 class="profile-name">devlog</h2>
        <p class="profile-bio">Writing about code, architecture, and things I learn along the way.</p>
      </div>

      <!-- Social links -->
      <div class="bento-card bento-social">
        <h3 class="card-label">Find me</h3>
        <div class="social-links">
          <a href="https://github.com" target="_blank" rel="noopener" class="social-link">GitHub</a>
          <a href="https://twitter.com" target="_blank" rel="noopener" class="social-link">Twitter</a>
        </div>
      </div>

      <!-- Featured / Pinned post (span 2 cols) -->
      <div v-if="recentPosts.length" class="bento-card bento-featured">
        <span class="featured-badge">Featured</span>
        <router-link
          :to="`/posts/${recentPosts[0].slug}`"
          class="featured-link"
        >
          <h2 class="featured-title">{{ recentPosts[0].title }}</h2>
          <p v-if="recentPosts[0].summary" class="featured-summary">
            {{ recentPosts[0].summary }}
          </p>
        </router-link>
      </div>

      <!-- Categories row (span 2 cols) -->
      <div class="bento-card bento-categories">
        <h3 class="card-label">Categories</h3>
        <div class="category-grid">
          <router-link
            v-for="cat in categories.slice(0, 4)"
            :key="cat.id"
            :to="`/posts?category=${cat.slug}`"
            class="category-item"
          >
            {{ cat.name }}
          </router-link>
          <span v-if="categories.length === 0" class="empty-hint">No categories yet</span>
        </div>
      </div>

      <!-- Tag cloud -->
      <div class="bento-card bento-tag-cloud">
        <h3 class="card-label">Tags</h3>
        <div class="tag-cloud">
          <router-link
            v-for="tag in tags"
            :key="tag.id"
            :to="`/posts?tag=${tag.slug}`"
            class="cloud-tag"
          >
            #{{ tag.name }}
          </router-link>
          <span v-if="tags.length === 0" class="empty-hint">No tags yet</span>
        </div>
      </div>
    </section>

    <!-- Recent Posts -->
    <section class="recent-posts">
      <h2 class="section-title">Recent Posts</h2>
      <div v-if="loading" class="loading">Loading...</div>
      <div v-else-if="recentPosts.length" class="posts-grid">
        <PostCard
          v-for="post in recentPosts"
          :key="post.id"
          :post="post"
        />
      </div>
      <p v-else class="empty">No posts yet.</p>
    </section>
  </div>
</template>

<style scoped>
.home {
  padding: 40px 0 80px;
}

/* Bento Grid */
.bento-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.bento-card {
  padding: 24px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--card-radius);
  transition: all 0.2s ease;
}

.bento-card:hover {
  border-color: var(--border-hover);
}

.bento-hero {
  grid-row: span 2;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.hero-greeting {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.hero-subtitle {
  font-size: 1.1rem;
  color: var(--text-secondary);
  margin-bottom: 24px;
}

.hero-stats {
  display: flex;
  gap: 24px;
}

.stat {
  display: flex;
  flex-direction: column;
}

.stat-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--accent);
}

.stat-label {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.bento-profile {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.profile-avatar {
  font-size: 3rem;
  margin-bottom: 12px;
}

.profile-name {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.profile-bio {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.bento-social {
  display: flex;
  flex-direction: column;
}

.card-label {
  font-size: 0.8rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 12px;
}

.social-links {
  display: flex;
  gap: 8px;
}

.social-link {
  padding: 6px 14px;
  border-radius: 8px;
  background: var(--bg-hover);
  color: var(--text-secondary);
  font-size: 0.85rem;
  transition: all 0.2s ease;
}

.social-link:hover {
  color: var(--accent);
}

.bento-featured {
  grid-column: span 2;
  position: relative;
  border-color: var(--accent);
  border-width: 1.5px;
}

.featured-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 20px;
  background: var(--tag-bg);
  color: var(--tag-text);
  font-size: 0.75rem;
  margin-bottom: 12px;
}

.featured-link {
  text-decoration: none;
  color: inherit;
}

.featured-title {
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.featured-summary {
  font-size: 0.9rem;
  color: var(--text-secondary);
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.bento-categories {
  grid-column: span 2;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.category-item {
  padding: 8px 12px;
  text-align: center;
  border-radius: 8px;
  background: var(--bg-hover);
  color: var(--text-secondary);
  font-size: 0.85rem;
  transition: all 0.2s ease;
}

.category-item:hover {
  color: var(--accent);
}

.bento-tag-cloud {
  /* single column */
}

.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.cloud-tag {
  padding: 4px 10px;
  border-radius: 6px;
  background: var(--tag-bg);
  color: var(--tag-text);
  font-size: 0.8rem;
  transition: all 0.2s ease;
}

.cloud-tag:hover {
  color: var(--accent);
}

.empty-hint {
  font-size: 0.85rem;
  color: var(--text-muted);
}

/* Recent Posts */
.recent-posts {
  margin-top: 60px;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 24px;
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
  padding: 40px;
}

/* Responsive */
@media (max-width: 1023px) and (min-width: 769px) {
  .bento-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .bento-hero {
    grid-row: span 1;
  }

  .bento-featured {
    grid-column: span 2;
  }

  .bento-categories {
    grid-column: span 2;
  }

  .posts-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .category-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .bento-grid {
    grid-template-columns: 1fr;
  }

  .bento-hero {
    grid-row: span 1;
  }

  .bento-featured {
    grid-column: span 1;
  }

  .bento-categories {
    grid-column: span 1;
  }

  .posts-grid {
    grid-template-columns: 1fr;
  }

  .category-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .hero-greeting {
    font-size: 1.5rem;
  }
}
</style>
