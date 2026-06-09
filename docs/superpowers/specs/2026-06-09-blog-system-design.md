# 个人技术博客系统设计

> 作者: Moon
> 日期: 2026-06-09
> 状态: 草稿

## 审批修改意见

审批结论: ✅ 已解决，所有 5 项均已修复。

1. **明确 Markdown 渲染职责** ✅
   - 方案: **后端统一渲染**。文章保存时由 `services/markdown.py` 渲染 Markdown → HTML 并写入 `content_html`，前端公开页直接展示 `content_html`，不做二次渲染。后台编辑器的实时预览出于响应速度考虑，本地用 `marked` 做临时渲染，但最终保存以服务端渲染为准。

2. **补充 Markdown/HTML 安全清洗方案** ✅
   - 方案: 后端使用 `bleach` 库清洗渲染后的 HTML。白名单允许标签: p, a, img, code, pre, blockquote, ul, ol, li, table, h1-h6, strong, em 等。已加入 requirements.txt。

3. **补齐后台标签/分类管理接口** ✅
   - 已补充: `GET /admin/tags` 标签管理列表、`GET /admin/categories` 分类管理列表、`PUT/DELETE /admin/categories/{id}` 分类更新/删除。

4. **收紧公开文章状态筛选** ✅
   - 服务端固定公开接口只返回 `status=published` 的文章，移除 `status` 作为访客可选筛选参数。管理后台列表同时返回草稿和已发布文章。

5. **明确 Token 刷新策略** ✅
   - 初期单用户场景，已删除 `/api/v1/admin/auth/refresh` 接口。仅使用 24h access token，过期重新登录即可，降低实现复杂度。

## 概述

前后端分离的个人技术博客系统。博主通过 Markdown 编写技术文章，访客浏览阅读。首页采用 Bento Grid 布局，支持三主题切换。

## 技术栈

| 层次 | 选型 | 理由 |
|------|------|------|
| 后端框架 | FastAPI (Python) | 学习 Python 的首要目标，性能优秀，自动生成 OpenAPI 文档 |
| ORM | SQLAlchemy 2.0 + Alembic | FastAPI 生态标配，异步支持好，迁移管理 |
| 数据库 | PostgreSQL | 功能最丰富，JSON 支持好，个人博客长期使用无瓶颈 |
| 前端框架 | Vue 3 + Vite | 学习曲线平缓，文档中文友好，Composition API 现代 |
| 认证 | JWT (python-jose + passlib) | 单用户后台认证，无需复杂 OAuth |
| Markdown 渲染 | 后端: python-markdown + bleach + pygments | 后端统一渲染 + XSS 清洗，前端展示安全 HTML |
| 部署 | 后端: Docker/Uvicorn; 前端: Vercel/Netlify/Nginx | 待定，优先开发 |

## 系统架构

```
┌─────────────────────────────────────┐
│  Browser (Vue 3 SPA)                │
│  ┌──────────┐  ┌──────────────────┐ │
│  │ 前台页面  │  │ 后台管理界面      │ │
│  │ 首页/文章 │  │ 文章编辑/标签管理 │ │
│  │ 标签/分类 │  │ 登录/仪表盘      │ │
│  └──────────┘  └──────────────────┘ │
└──────────────┬──────────────────────┘
               │ REST API (JSON)
               ▼
┌─────────────────────────────────────┐
│  FastAPI Backend                    │
│  ┌─────────┐ ┌────────┐ ┌───────┐  │
│  │ Routers │ │ Schemas│ │Models │  │
│  │ posts/  │ │ Pydant │ │SQLAlc │  │
│  │ tags/   │ │ ic     │ │hemy   │  │
│  │ admin/  │ │        │ │       │  │
│  └─────────┘ └────────┘ └───────┘  │
│  ┌──────────────────────────────┐   │
│  │ Services: markdown→html + XSS 清洗   │   │
│  └──────────────────────────────┘   │
└──────────────┬──────────────────────┘
               │ SQLAlchemy ORM
               ▼
┌─────────────────────────────────────┐
│  PostgreSQL                          │
│  posts │ tags │ categories │ users   │
└─────────────────────────────────────┘
```

### 项目目录结构

```
blog/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI 应用入口
│   │   ├── config.py          # 配置（数据库、JWT 密钥等）
│   │   ├── database.py        # 数据库连接
│   │   ├── models/            # SQLAlchemy 模型
│   │   │   ├── __init__.py
│   │   │   ├── post.py
│   │   │   ├── tag.py
│   │   │   ├── category.py
│   │   │   └── user.py
│   │   ├── schemas/           # Pydantic 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── post.py
│   │   │   ├── tag.py
│   │   │   ├── category.py
│   │   │   └── auth.py
│   │   ├── routers/           # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── posts.py       # 公开: 文章列表/详情
│   │   │   ├── tags.py        # 公开: 标签列表
│   │   │   ├── categories.py  # 公开: 分类列表
│   │   │   └── admin/         # 后台: 需要 JWT 认证
│   │   │       ├── __init__.py
│   │   │       ├── auth.py
│   │   │       └── posts.py
│   │   ├── services/          # 业务逻辑
│   │   │   ├── __init__.py
│   │   │   └── markdown.py    # Markdown → HTML 渲染
│   │   └── dependencies/      # 依赖注入
│   │       ├── __init__.py
│   │       └── auth.py
│   ├── alembic/               # 数据库迁移
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── router/            # Vue Router
│   │   ├── views/             # 页面组件
│   │   │   ├── Home.vue       # 首页 (Bento Grid)
│   │   │   ├── PostDetail.vue # 文章详情
│   │   │   ├── Posts.vue      # 文章列表
│   │   │   ├── Tags.vue       # 标签页
│   │   │   └── admin/
│   │   │       ├── Login.vue
│   │   │       ├── Dashboard.vue
│   │   │       └── Editor.vue # Markdown 编辑器
│   │   ├── components/        # 通用组件
│   │   │   ├── ThemeSwitcher.vue
│   │   │   ├── MarkdownPreview.vue
│   │   │   └── ...
│   │   ├── composables/       # 组合式函数
│   │   │   └── useTheme.js
│   │   ├── stores/            # Pinia 状态管理
│   │   └── assets/            # 样式/图片
│   │       └── styles/
│   │           ├── themes.css # 三套 CSS 变量
│   │           └── ... 
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
```

## 首页设计 (Bento Grid × 三主题)

### 布局 (Bento Grid)

CSS Grid 不对称布局，桌面端 3 列：

```
┌─────────────────┬──────────┬──────────┐
│                 │ Profile  │ Social   │
│    Hero /      │ (1 col)  │ Links    │
│     个人介绍    │          │ (1 col)  │
│   (跨 2 行)     ├──────────┴──────────┤
│                 │  Pinned Post         │
│                 │  (跨 2 列)           │
├─────────────────┴──────────┬──────────┤
│  Category × 4              │ Tag Cloud│
│  (跨 2 列)                 │ (1 col)  │
└────────────────────────────┴──────────┘
┌────────────────────────────────────────┐
│  Recent Posts (3 列 grid)              │
└────────────────────────────────────────┘
```

响应式断点:
- ≥1024px: 3 列 Bento Grid
- 768-1023px: 2 列
- <768px: 单列垂直堆叠

### 三主题配色

| CSS 变量 | Amber | Dracula | Slate |
|----------|-------|---------|-------|
| `--bg` | #0d0b09 | #282a36 | #fafbfc |
| `--card-bg` | rgba(255,255,255,0.03) | rgba(255,255,255,0.03) | #ffffff |
| `--text-primary` | #faf5ed | #f8f8f2 | #111827 |
| `--text-secondary` | rgba(250,245,237,0.5) | rgba(248,248,242,0.5) | #6b7280 |
| `--accent` | #f59e0b | #bd93f9 / #ff79c6 | #111827 |
| `--border` | rgba(255,255,255,0.08) | rgba(255,255,255,0.08) | #e5e7eb |
| 代码高亮主题 | Monokai | Dracula | GitHub Light |

### 主题切换实现

- **CSS 变量**: `:root`, `[data-theme="amber"]`, `[data-theme="dracula"]`, `[data-theme="slate"]`
- **切换方式**: 修改 `<html>` 的 `data-theme` 属性
- **持久化**: localStorage 存储用户选择
- **默认**: 跟随系统 `prefers-color-scheme`（Slate 亮色 / Dracula 暗色）
- **切换 UI**: 导航栏右侧主题切换按钮，点击轮换三个主题

## 数据模型

### Users

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| username | String(50) | 登录用户名 |
| password_hash | String(255) | bcrypt 加密 |
| created_at | DateTime | 创建时间 |

### Posts

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| title | String(200) | 文章标题 |
| slug | String(200) UNIQUE | URL 友好的标识 |
| content_md | Text | Markdown 原文 |
| content_html | Text | 渲染后的 HTML |
| summary | String(500) | 摘要 |
| status | Enum(draft/published) | 状态 |
| author_id | FK → users.id | 作者 |
| category_id | FK → categories.id | 分类 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |
| published_at | DateTime | 发布时间 |

### Tags

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| name | String(50) | 标签名称 |
| slug | String(50) UNIQUE | URL 友好的标识 |

### Categories

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| name | String(50) | 分类名称 |
| slug | String(50) UNIQUE | URL 友好的标识 |
| description | String(200) | 分类描述 |

### Post-Tags (多对多关联表)

| 字段 | 类型 | 说明 |
|------|------|------|
| post_id | FK → posts.id | 文章 ID |
| tag_id | FK → tags.id | 标签 ID |

## API 设计

### 公开接口

| 方法 | 路径 | 说明 | 分页 | 筛选参数 |
|------|------|------|------|----------|
| GET | /api/v1/posts | 文章列表 (仅 published) | ✔️ page, limit | tag, category |
| GET | /api/v1/posts/{slug} | 文章详情 | — | — |
| GET | /api/v1/tags | 标签列表 | — | — |
| GET | /api/v1/tags/{slug} | 标签详情+文章列表 | ✔️ | — |
| GET | /api/v1/categories | 分类列表 | — | — |
| GET | /api/v1/categories/{slug} | 分类详情+文章列表 | ✔️ | — |
| GET | /api/v1/posts/search?q= | 文章搜索 | ✔️ | q 关键词 |

### 后台接口 (需 JWT)

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/admin/auth/login | 登录 (返回 24h access token) |
| GET | /api/v1/admin/posts | 文章管理列表 (含草稿) |
| POST | /api/v1/admin/posts | 创建文章 |
| PUT | /api/v1/admin/posts/{id} | 更新文章 |
| DELETE | /api/v1/admin/posts/{id} | 删除文章 |
| PUT | /api/v1/admin/posts/{id}/publish | 发布/下架 |
| GET | /api/v1/admin/tags | 标签管理列表 |
| POST | /api/v1/admin/tags | 创建标签 |
| PUT | /api/v1/admin/tags/{id} | 更新标签 |
| DELETE | /api/v1/admin/tags/{id} | 删除标签 |
| GET | /api/v1/admin/categories | 分类管理列表 |
| POST | /api/v1/admin/categories | 创建分类 |
| PUT | /api/v1/admin/categories/{id} | 更新分类 |
| DELETE | /api/v1/admin/categories/{id} | 删除分类 |

### API 响应格式

```json
{
  "success": true,
  "data": {},
  "error": null,
  "meta": {
    "total": 47,
    "page": 1,
    "limit": 10
  }
}
```

## 前端路由

| 路径 | 页面 | 权限 |
|------|------|------|
| / | 首页 (Bento Grid) | 公开 |
| /posts | 文章列表 | 公开 |
| /posts/{slug} | 文章详情 | 公开 |
| /tags | 标签列表 | 公开 |
| /tags/{slug} | 标签筛选的文章列表 | 公开 |
| /categories/{slug} | 分类筛选的文章列表 | 公开 |
| /about | 关于页面 | 公开 |
| /admin/login | 后台登录 | 公开 |
| /admin | 后台仪表盘 | 需登录 |
| /admin/posts/new | 新建文章 | 需登录 |
| /admin/posts/{id}/edit | 编辑文章 | 需登录 |

## 后台 Markdown 编辑器

编辑器页面采用左右分栏布局:

```
┌─────────────────┬─────────────────┐
│  Markdown 编辑器  │  实时预览       │
│  (textarea)      │  (渲染后 HTML)   │
│                  │                  │
│  ## 标题         │  标题            │
│  ```python       │  代码块高亮     │
│  def hello():    │  def hello():   │
│      print("hi") │      print("hi")│
│  ```             │                  │
│  正文内容...      │  正文渲染...     │
│                  │                  │
├─────────────────┴─────────────────┤
│  标题输入  │  标签选择  │  发布/保存  │
└───────────────────────────────────┘
```

- 使用 `python-markdown` + `pygments` 后端统一渲染 Markdown → HTML
- 使用 `bleach` 库清洗渲染后的 HTML，防止 XSS 攻击 (允许的标签: p, a, img, code, pre, blockquote, ul, ol, li, table, h1-h6, strong, em 等)
- 自动生成文章摘要（截取前 N 个字符）
- Slug 根据标题自动生成，可手动修改

> Markdown 渲染职责: 后端统一渲染 + XSS 清洗，文章保存时写入 `content_html`。前端公开页直接展示 `content_html`，不做二次渲染。后台编辑器的实时预览出于响应速度考虑，在本地用 `marked` 做临时渲染，但最终保存以服务端渲染为准。

## 非功能性需求

- **SEO**: Vue 前端使用客户端渲染，但所有内容 API 返回结构化数据。考虑后续添加 prerender-spa-plugin 或切换到 Nuxt 做 SSR
- **响应式**: 移动端优先，Bento Grid 自动降级
- **性能**: API 分页默认 10 条/页，文章详情直接返回预渲染 `content_html`，无需后端实时渲染
- **安全**: JWT 24h 单 token 认证（无 refresh token），密码 bcrypt 加密，CORS 配置白名单，文章 HTML 使用 bleach 清洗防 XSS

## 排除的功能 (YAGNI)

- 评论系统（后续可集成第三方如 Giscus）
- 多用户/角色权限
- GitHub/社交登录
- RSS 订阅（后期可加）
- 文章阅读统计（后期可加）
- 图片上传/图床（初期用外部图床）

## 开发顺序 (Phase)

### Phase 1: 后端基础
1. FastAPI 项目脚手架 + 数据库配置
2. SQLAlchemy 模型 + Alembic 迁移
3. 公开 API: 文章列表/详情、标签、分类
4. 后台 API: JWT 登录、文章 CRUD

### Phase 2: 前端基础
1. Vue 3 + Vite 项目初始化
2. 三主题系统 (CSS 变量 + localStorage)
3. 首页 Bento Grid 布局
4. 文章详情页 (Markdown 渲染 + 代码高亮)

### Phase 3: 后台前端
1. 登录页面
2. Markdown 编辑器 (左右分栏 + 实时预览)
3. 文章管理列表
4. 标签/分类管理

### Phase 4: 完善
1. 文章搜索
2. 分页组件
3. 错误处理与空状态
4. 响应式适配
5. 部署配置
