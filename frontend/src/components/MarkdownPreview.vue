<!--
  @author beishi
  @date 2026/6/9
  @description Markdown preview component - renders markdown using marked library
-->
<script setup>
import { computed } from 'vue'
import { marked } from 'marked'

const props = defineProps({
  content: {
    type: String,
    default: '',
  },
})

marked.setOptions({
  gfm: true,
  breaks: true,
})

const renderedHtml = computed(() => {
  if (!props.content) return '<p class="empty-preview">Start writing to see preview...</p>'
  return marked(props.content)
})
</script>

<template>
  <div class="markdown-preview" v-html="renderedHtml" />
</template>

<style scoped>
.markdown-preview {
  padding: 20px;
  font-size: 1rem;
  line-height: 1.7;
  color: var(--text-primary);
  overflow-y: auto;
  height: 100%;
}

.markdown-preview :deep(h1),
.markdown-preview :deep(h2),
.markdown-preview :deep(h3),
.markdown-preview :deep(h4) {
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  font-weight: 600;
}

.markdown-preview :deep(h2) {
  font-size: 1.5rem;
}

.markdown-preview :deep(h3) {
  font-size: 1.2rem;
}

.markdown-preview :deep(p) {
  margin-bottom: 1em;
}

.markdown-preview :deep(a) {
  color: var(--accent);
}

.markdown-preview :deep(blockquote) {
  border-left: 3px solid var(--accent);
  padding: 8px 16px;
  margin: 1em 0;
  background: var(--bg-hover);
  border-radius: 0 6px 6px 0;
  color: var(--text-secondary);
}

.markdown-preview :deep(code) {
  padding: 2px 6px;
  border-radius: 4px;
  background: var(--bg-hover);
  font-size: 0.9em;
}

.markdown-preview :deep(pre) {
  margin: 1em 0;
  padding: 16px;
  border-radius: 8px;
  background: #1a1b26;
  overflow-x: auto;
}

.markdown-preview :deep(pre code) {
  padding: 0;
  background: none;
}

.markdown-preview :deep(ul),
.markdown-preview :deep(ol) {
  margin: 1em 0;
  padding-left: 2em;
}

.markdown-preview :deep(li) {
  margin-bottom: 0.3em;
}

.markdown-preview :deep(img) {
  border-radius: 6px;
  max-width: 100%;
}

.markdown-preview :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1em 0;
}

.markdown-preview :deep(th),
.markdown-preview :deep(td) {
  padding: 8px 12px;
  border: 1px solid var(--border);
  text-align: left;
}

.markdown-preview :deep(th) {
  background: var(--bg-hover);
  font-weight: 600;
}
</style>
