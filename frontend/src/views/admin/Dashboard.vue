<!--
  @author beishi
  @date 2026/6/9
  @description Admin analytics dashboard - UV/PV stats, trend charts, china map, popular pages, device/referer pies
-->
<script setup>
import { ref, onMounted, shallowRef } from 'vue'
import { useRouter } from 'vue-router'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, MapChart, PieChart, BarChart } from 'echarts/charts'
import {
  TitleComponent, TooltipComponent, LegendComponent,
  GridComponent, VisualMapComponent, GeoComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import {
  adminGetAnalyticsOverview,
  adminGetAnalyticsTrend,
  adminGetAnalyticsRegion,
  adminGetAnalyticsCities,
  adminGetPopularPages,
  adminGetDevices,
  adminGetReferers,
  adminGetPosts,
  adminDeletePost,
  adminTogglePublish,
} from '../../api/index.js'
import { useAppStore } from '../../stores/app.js'
import { setupChinaMap } from '../../utils/echarts-setup.js'

use([
  CanvasRenderer, LineChart, MapChart, PieChart, BarChart,
  TitleComponent, TooltipComponent, LegendComponent,
  GridComponent, VisualMapComponent, GeoComponent,
])

const router = useRouter()
const store = useAppStore()

const overview = ref({ today: { pv: 0, uv: 0 }, yesterday: { pv: 0, uv: 0 }, week: { pv: 0, uv: 0 }, month: { pv: 0, uv: 0 } })
const trendDays = ref(7)
const trendOption = shallowRef({})
const mapOption = shallowRef({})
const popularPages = ref([])
const deviceOption = shallowRef({})
const refererOption = shallowRef({})
const posts = ref([])
const selectedProvince = ref('')
const cityData = ref([])

onMounted(async () => {
  try {
    const [overviewRes, trendRes, regionRes, pagesRes, deviceRes, refererRes, postsRes] = await Promise.all([
      adminGetAnalyticsOverview(),
      adminGetAnalyticsTrend(trendDays.value),
      adminGetAnalyticsRegion(),
      adminGetPopularPages(10),
      adminGetDevices(),
      adminGetReferers(10),
      adminGetPosts({ limit: 5 }),
    ])
    overview.value = overviewRes.data
    buildTrendChart(trendRes.data)
    await setupChinaMap()
    buildMapChart(regionRes.data)
    popularPages.value = pagesRes.data
    buildDeviceChart(deviceRes.data)
    buildRefererChart(refererRes.data)
    posts.value = postsRes.data
  } catch (e) {
    console.error('Dashboard.onMounted - failed to load dashboard data:', e.message)
  }
})

function pctChange(current, previous) {
  if (!previous) return current > 0 ? 100 : 0
  return Math.round(((current - previous) / previous) * 100)
}

async function switchTrend(days) {
  trendDays.value = days
  const res = await adminGetAnalyticsTrend(days)
  buildTrendChart(res.data)
}

function buildTrendChart(data) {
  trendOption.value = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['PV', 'UV'], textStyle: { color: 'var(--text-secondary)' } },
    grid: { left: 50, right: 20, top: 40, bottom: 30 },
    xAxis: { type: 'category', data: data.map(d => d.date.slice(5)), axisLabel: { color: 'var(--text-muted)' } },
    yAxis: { type: 'value', axisLabel: { color: 'var(--text-muted)' } },
    series: [
      { name: 'PV', type: 'line', smooth: true, data: data.map(d => d.pv), areaStyle: { opacity: 0.1 }, lineStyle: { color: '#818cf8' }, itemStyle: { color: '#818cf8' } },
      { name: 'UV', type: 'line', smooth: true, data: data.map(d => d.uv), areaStyle: { opacity: 0.1 }, lineStyle: { color: '#ff79c6' }, itemStyle: { color: '#ff79c6' } },
    ],
  }
}

function buildMapChart(data) {
  const mapData = data.map(d => ({
    name: d.province.replace(/省|市|自治区|壮族自治区|维吾尔自治区|回族自治区|特别行政区/g, ''),
    value: d.pv,
    uv: d.uv,
  }))
  mapOption.value = {
    tooltip: { trigger: 'item', formatter: '{b}<br/>PV: {c}' },
    visualMap: { min: 0, max: Math.max(...data.map(d => d.pv), 10), text: ['高', '低'], inRange: { color: ['#e0e7ff', '#818cf8', '#4f46e5'] }, textStyle: { color: 'var(--text-secondary)' }, left: 'left', bottom: 10 },
    series: [{
      type: 'map', map: 'china', roam: true,
      label: { show: false },
      emphasis: { label: { show: true } },
      data: mapData,
    }],
  }
}

async function onMapClick(params) {
  if (params.componentType === 'series') {
    selectedProvince.value = params.name
    const res = await adminGetAnalyticsCities(params.name)
    cityData.value = res.data
  }
}

function buildDeviceChart(data) {
  const colors = ['#818cf8', '#ff79c6', '#fbbf24']
  deviceOption.value = {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    series: [{
      type: 'pie', radius: ['40%', '70%'],
      label: { color: 'var(--text-secondary)', fontSize: 11 },
      data: data.map((d, i) => ({ ...d, itemStyle: { color: colors[i % colors.length] } })),
    }],
  }
}

function buildRefererChart(data) {
  const colors = ['#818cf8', '#ff79c6', '#fbbf24', '#4ade80', '#60a5fa', '#f97316']
  refererOption.value = {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    series: [{
      type: 'pie', radius: ['40%', '70%'],
      label: { color: 'var(--text-secondary)', fontSize: 11 },
      data: data.map((d, i) => ({ ...d, itemStyle: { color: colors[i % colors.length] } })),
    }],
  }
}

async function togglePublish(id) {
  await adminTogglePublish(id)
  window.location.reload()
}
async function removePost(id) {
  if (confirm('确定删除？')) {
    await adminDeletePost(id)
    posts.value = posts.value.filter(p => p.id !== id)
  }
}
function logout() {
  store.logout()
  router.push('/admin/login')
}
</script>

<template>
  <div class="dashboard">
    <!-- Header -->
    <div class="dash-header">
      <h2>Dashboard</h2>
      <div class="dash-actions">
        <router-link to="/admin/posts/new" class="btn-primary">+ 新建文章</router-link>
        <button @click="logout" class="btn-ghost">Logout</button>
      </div>
    </div>

    <!-- Row 1: UV/PV Stats Cards -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-label">今日 PV</div>
        <div class="stat-value">{{ overview.today.pv }}</div>
        <div class="stat-change" :class="{ up: pctChange(overview.today.pv, overview.yesterday.pv) >= 0, down: pctChange(overview.today.pv, overview.yesterday.pv) < 0 }">
          {{ pctChange(overview.today.pv, overview.yesterday.pv) >= 0 ? '↑' : '↓' }} {{ Math.abs(pctChange(overview.today.pv, overview.yesterday.pv)) }}% vs 昨日
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-label">今日 UV</div>
        <div class="stat-value accent">{{ overview.today.uv }}</div>
        <div class="stat-change" :class="{ up: pctChange(overview.today.uv, overview.yesterday.uv) >= 0, down: pctChange(overview.today.uv, overview.yesterday.uv) < 0 }">
          {{ pctChange(overview.today.uv, overview.yesterday.uv) >= 0 ? '↑' : '↓' }} {{ Math.abs(pctChange(overview.today.uv, overview.yesterday.uv)) }}% vs 昨日
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-label">本周 PV</div>
        <div class="stat-value">{{ overview.week.pv }}</div>
        <div class="stat-sub">UV {{ overview.week.uv }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">本月 PV</div>
        <div class="stat-value">{{ overview.month.pv }}</div>
        <div class="stat-sub">UV {{ overview.month.uv }}</div>
      </div>
    </div>

    <!-- Row 2: Charts -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">📈 UV/PV 趋势</span>
          <div class="chart-toggle">
            <button :class="{ active: trendDays === 7 }" @click="switchTrend(7)">7天</button>
            <button :class="{ active: trendDays === 30 }" @click="switchTrend(30)">30天</button>
          </div>
        </div>
        <v-chart class="chart" :option="trendOption" autoresize />
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">🗺 访客地域分布</span>
          <span v-if="selectedProvince" class="chart-subtitle" @click="selectedProvince = ''; cityData = []">{{ selectedProvince }} ✕</span>
        </div>
        <v-chart v-if="!selectedProvince" class="chart" :option="mapOption" autoresize @click="onMapClick" />
        <div v-else class="city-list">
          <div v-for="c in cityData" :key="c.city" class="city-item">
            <span class="city-name">{{ c.city }}</span>
            <span class="city-pv">PV {{ c.pv }}</span>
            <span class="city-uv">UV {{ c.uv }}</span>
          </div>
          <div v-if="!cityData.length" class="empty-city">暂无数据</div>
        </div>
      </div>
    </div>

    <!-- Row 3: Popular + Pie Charts -->
    <div class="detail-row">
      <div class="chart-card">
        <div class="chart-title">🏆 热门页面</div>
        <table class="rank-table">
          <thead><tr><th>#</th><th>页面</th><th>PV</th><th>UV</th></tr></thead>
          <tbody>
            <tr v-for="(page, i) in popularPages" :key="page.path">
              <td class="rank-num">{{ i + 1 }}</td>
              <td class="rank-path">{{ page.path }}</td>
              <td>{{ page.pv }}</td>
              <td>{{ page.uv }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="chart-card">
        <div class="chart-title">🌐 访客来源 &amp; 💻 设备</div>
        <div class="pie-row">
          <v-chart class="pie-chart" :option="refererOption" autoresize />
          <v-chart class="pie-chart" :option="deviceOption" autoresize />
        </div>
      </div>
    </div>

    <!-- Row 4: Recent Posts -->
    <div class="chart-card">
      <div class="chart-header">
        <span class="chart-title">📝 最近文章</span>
        <router-link to="/admin/posts/new" class="section-link">+ 新建</router-link>
      </div>
      <table class="post-table">
        <thead><tr><th>标题</th><th>状态</th><th>日期</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="post in posts" :key="post.id">
            <td>{{ post.title }}</td>
            <td><span :class="post.status">{{ post.status }}</span></td>
            <td class="date-cell">{{ new Date(post.created_at).toLocaleDateString('zh-CN') }}</td>
            <td class="actions-cell">
              <button @click="router.push(`/admin/posts/${post.id}/edit`)" class="btn-sm">Edit</button>
              <button @click="togglePublish(post.id)" class="btn-sm">{{ post.status === 'published' ? 'Unpublish' : 'Publish' }}</button>
              <button @click="removePost(post.id)" class="btn-sm btn-danger">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.dashboard { padding: 24px 0 60px; }
.dash-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.dash-actions { display: flex; gap: 8px; align-items: center; }
.btn-primary {
  background: var(--accent); color: #fff; padding: 8px 16px;
  border-radius: 8px; text-decoration: none; font-size: 13px; font-weight: 600;
  border: none; cursor: pointer;
}
.btn-ghost {
  background: none; border: 1px solid var(--border); color: var(--text-primary);
  padding: 8px 16px; border-radius: 8px; cursor: pointer; font-size: 13px;
}

/* Stats Cards */
.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }
.stat-card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--card-radius); padding: 20px;
}
.stat-label { font-size: 12px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
.stat-value { font-size: 32px; font-weight: 800; }
.stat-value.accent { background: linear-gradient(135deg, var(--accent), var(--accent-secondary)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.stat-change { font-size: 11px; margin-top: 4px; }
.stat-change.up { color: #22c55e; }
.stat-change.down { color: #ef4444; }
.stat-sub { font-size: 11px; color: var(--text-muted); margin-top: 4px; }

/* Charts */
.charts-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px; }
.detail-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px; }
.chart-card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--card-radius); padding: 20px;
}
.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.chart-title { font-size: 14px; font-weight: 600; }
.chart-subtitle { font-size: 12px; color: var(--accent); cursor: pointer; }
.chart-toggle { display: flex; gap: 4px; }
.chart-toggle button {
  background: var(--bg-hover); border: 1px solid var(--border);
  color: var(--text-secondary); padding: 4px 12px; border-radius: 6px;
  cursor: pointer; font-size: 11px;
}
.chart-toggle button.active { background: var(--accent); color: #fff; border-color: var(--accent); }
.chart { height: 320px; }

/* City list */
.city-list { max-height: 320px; overflow-y: auto; }
.city-item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--border); font-size: 12px; }
.city-name { color: var(--text-primary); }
.city-pv { color: var(--accent); }
.city-uv { color: var(--text-secondary); }
.empty-city { text-align: center; padding: 40px; color: var(--text-muted); }

/* Pie charts */
.pie-row { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.pie-chart { height: 240px; }

/* Tables */
.rank-table, .post-table { width: 100%; border-collapse: collapse; }
.rank-table th, .rank-table td, .post-table th, .post-table td {
  padding: 8px 12px; text-align: left; border-bottom: 1px solid var(--border); font-size: 12px;
}
.rank-table th, .post-table th { color: var(--text-secondary); font-weight: 600; }
.rank-num { color: var(--accent); font-weight: 700; }
.rank-path { color: var(--text-primary); max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.draft { color: #f59e0b; }
.published { color: #22c55e; }
.date-cell { color: var(--text-muted); }
.actions-cell { display: flex; gap: 4px; }
.btn-sm {
  background: var(--bg-card); border: 1px solid var(--border); color: var(--text-primary);
  padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 11px;
}
.btn-danger { color: #ff6b6b; }
.section-link { font-size: 12px; color: var(--accent); text-decoration: none; }

/* Responsive */
@media (max-width: 768px) {
  .stats-row { grid-template-columns: repeat(2, 1fr); }
  .charts-row, .detail-row { grid-template-columns: 1fr; }
}
</style>
