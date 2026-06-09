<!--
  @author beishi
  @date 2026/6/9
  @description Markdown editor with split view - title, slug, category, tags, preview
-->
<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MarkdownPreview from '../../components/MarkdownPreview.vue'
import {
  adminGetPost,
  adminCreatePost,
  adminUpdatePost,
  adminGetCategories,
  adminGetTags,
} from '../../api'

const route = useRoute()
const router = useRouter()

const isEditing = computed(() => !!route.params.id)

const title = ref('')
const slug = ref('')
const content = ref('')
const summary = ref('')
const selectedCategory = ref('')
const selectedTags = ref([])
const isPublished = ref(false)
const saving = ref(false)
const errorMsg = ref('')

const categories = ref([])
const tags = ref([])

async function fetchMetadata() {
  try {
    const [categoriesRes, tagsRes] = await Promise.all([
      adminGetCategories(),
      adminGetTags(),
    ])
    categories.value = categoriesRes.data || []
    tags.value = tagsRes.data || []
  } catch (err) {
    console.error('Editor.fetchMetadata - error:', err.message)
  }
}

async function fetchPost(id) {
  try {
    const res = await adminGetPost(id)
    const post = res.data
    title.value = post.title || ''
    slug.value = post.slug || ''
    content.value = post.content_md || post.content || ''
    summary.value = post.summary || ''
    isPublished.value = post.is_published || false
    selectedCategory.value = post.category?.id?.toString() || ''
    selectedTags.value = (post.tags || []).map((t) => (t.id || t).toString())
  } catch (err) {
    console.error('Editor.fetchPost - error:', err.message)
    errorMsg.value = 'Failed to load post'
  }
}

function generateSlug() {
  slug.value = title.value
    .toLowerCase()
    .replace(/[^a-z0-9一-龥]+/g, '-')
    .replace(/^-|-$/g, '')
}

function toggleTag(tagId) {
  const id = tagId.toString()
  const index = selectedTags.value.indexOf(id)
  if (index === -1) {
    selectedTags.value = [...selectedTags.value, id]
  } else {
    selectedTags.value = selectedTags.value.filter((t) => t !== id)
  }
}

async function handleSave(publish) {
  errorMsg.value = ''

  if (!title.value.trim()) {
    errorMsg.value = 'Title is required'
    return
  }

  saving.value = true
  const postData = {
    title: title.value,
    slug: slug.value || undefined,
    content_md: content.value,
    summary: summary.value,
    category_id: selectedCategory.value ? Number(selectedCategory.value) : null,
    tag_ids: selectedTags.value.map(Number),
    is_published: publish,
  }

  try {
    if (isEditing.value) {
      await adminUpdatePost(route.params.id, postData)
    } else {
      await adminCreatePost(postData)
    }
    router.push('/admin')
  } catch (err) {
    console.error('Editor.handleSave - error:', err.message)
    errorMsg.value = err.response?.data?.detail || 'Save failed'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await fetchMetadata()
  if (isEditing.value) {
    await fetchPost(route.params.id)
  }
})
</script>

<template>
  <div class="editor-page">
    <div class="editor-header">
      <h1 class="page-title">{{ isEditing ? 'Edit Post' : 'New Post' }}</h1>
      <router-link to="/admin" class="back-link">&larr; Back to Dashboard</router-link>
    </div>

    <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

    <!-- Top: Metadata -->
    <div class="metadata-section">
      <div class="metadata-row">
        <div class="field title-field">
          <label for="title">Title</label>
          <input
            id="title"
            v-model="title"
            type="text"
            placeholder="Post title"
            @blur="generateSlug"
          />
        </div>
        <div class="field slug-field">
          <label for="slug">Slug</label>
          <input
            id="slug"
            v-model="slug"
            type="text"
            placeholder="post-url-slug"
          />
        </div>
      </div>

      <div class="field">
        <label for="summary">Summary</label>
        <input
          id="summary"
          v-model="summary"
          type="text"
          placeholder="Brief summary of the post"
        />
      </div>

      <div class="metadata-row">
        <div class="field category-field">
          <label for="category">Category</label>
          <select id="category" v-model="selectedCategory">
            <option value="">No category</option>
            <option
              v-for="cat in categories"
              :key="cat.id"
              :value="cat.id.toString()"
            >
              {{ cat.name }}
            </option>
          </select>
        </div>

        <div class="field published-field">
          <label>
            <input type="checkbox" v-model="isPublished" />
            Published
          </label>
        </div>
      </div>

      <!-- Tags -->
      <div class="field">
        <label>Tags</label>
        <div class="tags-checkboxes">
          <label
            v-for="tag in tags"
            :key="tag.id"
            class="tag-checkbox"
            :class="{ selected: selectedTags.includes(tag.id.toString()) }"
          >
            <input
              type="checkbox"
              :checked="selectedTags.includes(tag.id.toString())"
              @change="toggleTag(tag.id)"
            />
            {{ tag.name }}
          </label>
          <span v-if="tags.length === 0" class="empty-hint">No tags available</span>
        </div>
      </div>
    </div>

    <!-- Bottom: Split Editor -->
    <div class="split-editor">
      <div class="editor-pane">
        <label>Markdown Content</label>
        <textarea
          v-model="content"
          class="editor-textarea"
          placeholder="Write your post in Markdown..."
        />
      </div>
      <div class="preview-pane">
        <label>Preview</label>
        <div class="preview-content">
          <MarkdownPreview :content="content" />
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="editor-actions">
      <button
        class="save-btn"
        :disabled="saving"
        @click="handleSave(false)"
      >
        {{ saving ? 'Saving...' : 'Save Draft' }}
      </button>
      <button
        class="publish-btn"
        :disabled="saving"
        @click="handleSave(true)"
      >
        {{ saving ? 'Publishing...' : 'Publish' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.editor-page {
  padding: 40px 0 80px;
}

.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.back-link {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.back-link:hover {
  color: var(--accent);
}

.error-msg {
  padding: 10px 16px;
  border-radius: 8px;
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  font-size: 0.85rem;
  margin-bottom: 16px;
}

/* Metadata */
.metadata-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.metadata-row {
  display: flex;
  gap: 16px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.title-field {
  flex: 2;
}

.slug-field {
  flex: 1;
}

.category-field {
  flex: 1;
}

.published-field {
  display: flex;
  align-items: flex-end;
  padding-bottom: 4px;
}

.published-field label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: var(--text-secondary);
}

.field input[type="text"],
.field select {
  padding: 10px 14px;
  border-radius: 8px;
  background: var(--bg);
  border: 1px solid var(--border);
  color: var(--text-primary);
  font-size: 0.95rem;
}

.field input[type="text"]:focus,
.field select:focus {
  border-color: var(--accent);
  outline: none;
}

.tags-checkboxes {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-checkbox {
  padding: 6px 14px;
  border-radius: 8px;
  background: var(--bg-hover);
  border: 1px solid var(--border);
  color: var(--text-secondary);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tag-checkbox input {
  display: none;
}

.tag-checkbox.selected {
  background: var(--tag-bg);
  border-color: var(--accent);
  color: var(--tag-text);
}

.tag-checkbox:hover {
  border-color: var(--border-hover);
}

.empty-hint {
  font-size: 0.85rem;
  color: var(--text-muted);
}

/* Split Editor */
.split-editor {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  height: 500px;
  margin-bottom: 24px;
}

.editor-pane,
.preview-pane {
  display: flex;
  flex-direction: column;
}

.editor-pane label,
.preview-pane label {
  font-size: 0.8rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
}

.editor-textarea {
  flex: 1;
  padding: 16px;
  border-radius: 8px;
  background: var(--bg);
  border: 1px solid var(--border);
  color: var(--text-primary);
  font-family: 'Fira Code', 'Cascadia Code', 'Consolas', monospace;
  font-size: 0.9rem;
  line-height: 1.6;
  resize: none;
}

.editor-textarea:focus {
  border-color: var(--accent);
  outline: none;
}

.preview-pane {
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
}

.preview-pane label {
  padding: 10px 16px;
  background: var(--bg-hover);
  border-bottom: 1px solid var(--border);
  margin-bottom: 0;
}

.preview-content {
  flex: 1;
  overflow-y: auto;
  background: var(--bg-card);
}

/* Actions */
.editor-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.save-btn,
.publish-btn {
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.save-btn {
  background: var(--bg-hover);
  border: 1px solid var(--border);
  color: var(--text-secondary);
}

.save-btn:hover:not(:disabled) {
  border-color: var(--border-hover);
  color: var(--text-primary);
}

.publish-btn {
  background: var(--accent);
  color: var(--bg);
}

.publish-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.save-btn:disabled,
.publish-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .metadata-row {
    flex-direction: column;
  }

  .split-editor {
    grid-template-columns: 1fr;
    height: auto;
  }

  .editor-textarea {
    min-height: 300px;
  }

  .preview-content {
    min-height: 300px;
  }

  .editor-actions {
    flex-direction: column;
  }
}
</style>
