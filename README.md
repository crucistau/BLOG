# DevLog - 个人技术博客

> 前后端分离的个人技术博客系统，支持 Markdown 文章管理、三主题切换、Bento Grid 首页、访客统计分析。

## 技术栈

| 层次 | 技术 |
|------|------|
| 后端 | FastAPI + SQLAlchemy 2.0 + Alembic + PostgreSQL |
| 前端 | Vue 3 + Vite + Pinia + Vue Router |
| 图表 | ECharts + vue-echarts |
| 地域解析 | ip2region（离线 IP → 省份/城市） |
| Markdown 渲染 | python-markdown + Pygments + bleach（后端统一渲染 + XSS 清洗） |
| 认证 | JWT (python-jose + passlib/bcrypt) |

## 项目结构

```
blog/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── models/          # SQLAlchemy 数据模型
│   │   ├── schemas/         # Pydantic 数据模型
│   │   ├── routers/         # API 路由
│   │   │   ├── posts.py     # 公开文章接口
│   │   │   ├── tags.py      # 公开标签接口
│   │   │   ├── categories.py# 公开分类接口
│   │   │   ├── analytics.py # 访客追踪接口
│   │   │   └── admin/       # 后台管理接口 (JWT 认证)
│   │   ├── services/        # 业务逻辑
│   │   │   ├── markdown.py  # Markdown 渲染 + XSS 清洗
│   │   │   ├── location.py  # IP 地域解析
│   │   │   └── tracker.py   # 访客记录
│   │   ├── dependencies/    # 依赖注入 (JWT 认证)
│   │   └── config.py        # 配置管理
│   ├── tests/               # 单元测试
│   └── scripts/seed.py      # 创建初始管理员
├── frontend/                # Vue 3 前端
│   └── src/
│       ├── views/           # 页面组件
│       │   ├── Home.vue     # Bento Grid 首页
│       │   ├── PostDetail.vue# 文章详情
│       │   ├── Posts.vue    # 文章列表
│       │   ├── Tags.vue     # 标签页
│       │   └── admin/       # 后台管理
│       │       ├── Login.vue       # 登录
│       │       ├── Dashboard.vue   # 分析仪表盘
│       │       └── Editor.vue      # Markdown 编辑器
│       ├── components/      # 通用组件
│       ├── composables/     # 组合式函数 (useTheme)
│       ├── stores/          # Pinia 状态管理
│       └── assets/styles/   # 三主题 CSS 变量
└── docs/                    # 设计文档
```

## 功能特性

### 前台
- 🏠 **Bento Grid 首页** — 不对称网格布局，Hero + 精选文章 + 标签云 + 分类
- 🎨 **三主题切换** — Dracula（暗色）/ Amber（暖金）/ Slate（极简白），一键切换，刷新保持
- 📝 **Markdown 渲染** — 代码高亮、表格、TOC，后端统一渲染 + XSS 清洗
- 🔍 **文章搜索** — 按标题关键词搜索
- 🏷 **标签 & 分类** — 文章多标签、单分类，支持按标签/分类筛选

### 后台管理
- 📊 **分析仪表盘**
  - UV/PV 四维统计（今日/昨日/本周/本月）+ 环比变化
  - 🗺 中国省份访客热力地图（点击展开城市详情）
  - 📈 UV/PV 趋势折线图（7天/30天切换）
  - 🏆 热门页面排行 Top 10
  - 🌐 访客来源分布（直接访问/百度/Google...）
  - 💻 设备分布（Mobile/Desktop/Tablet）
- ✏️ **Markdown 编辑器** — 左右分栏实时预览，自动 Slug 生成
- 📋 **文章管理** — CRUD、草稿/发布切换
- 🏷 **标签 & 分类管理** — 完整增删改查

## 快速开始

### 前置条件
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

### 后端

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 设置数据库连接

# 数据库迁移
alembic upgrade head

# 创建管理员用户
python -m scripts.seed

# 启动服务
uvicorn app.main:app --reload --port 8000
```

### 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:5173 查看前台，http://localhost:5173/admin 登录后台。

默认管理员: `admin` / `admin123`

## API 文档

启动后端后访问 http://localhost:8000/docs 查看 Swagger UI 自动生成的 API 文档。

## 主题预览

| Dracula | Amber | Slate |
|---------|-------|-------|
| 深紫暗色 | 暖金暖色 | 极简白色 |
| 编辑器风格 | 咖啡质感 | Vercel 同款 |

## 许可

MIT
