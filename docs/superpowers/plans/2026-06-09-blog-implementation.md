# 个人技术博客 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建前后端分离的个人技术博客，支持 Markdown 文章管理、Bento Grid 首页、三主题切换

**Architecture:** FastAPI 后端 + Vue 3 前端 + PostgreSQL。后端统一渲染 Markdown→HTML 并用 bleach 做 XSS 清洗。前端使用 Vue Router 做 SPA 路由、Pinia 管理状态、CSS 变量驱动三主题切换。

**Tech Stack:** FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL, Vue 3, Vite, Pinia, python-markdown, bleach, pygments

---

## 文件结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 入口
│   ├── config.py             # 配置 (DB, JWT, CORS)
│   ├── database.py           # 异步数据库会话
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py           # User 模型
│   │   ├── post.py           # Post 模型
│   │   ├── tag.py            # Tag 模型
│   │   └── category.py       # Category 模型
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── post.py           # Post Pydantic 模型
│   │   ├── tag.py            # Tag Pydantic 模型
│   │   ├── category.py       # Category Pydantic 模型
│   │   └── auth.py           # Auth Pydantic 模型
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── posts.py          # 公开文章路由
│   │   ├── tags.py           # 公开标签路由
│   │   ├── categories.py     # 公开分类路由
│   │   └── admin/
│   │       ├── __init__.py
│   │       ├── auth.py       # 后台认证路由
│   │       ├── posts.py      # 后台文章管理路由
│   │       ├── tags.py       # 后台标签管理路由
│   │       └── categories.py # 后台分类管理路由
│   ├── services/
│   │   ├── __init__.py
│   │   └── markdown.py       # Markdown 渲染 + XSS 清洗
│   └── dependencies/
│       ├── __init__.py
│       └── auth.py           # JWT 认证依赖
├── alembic/                   # 自动生成
├── alembic.ini
├── requirements.txt
├── pyproject.toml
└── Dockerfile
frontend/
├── src/
│   ├── main.js
│   ├── App.vue
│   ├── router/index.js
│   ├── stores/app.js         # Pinia 主题/用户状态
│   ├── composables/useTheme.js
│   ├── api/index.js           # Axios API 封装
│   ├── views/
│   │   ├── Home.vue           # Bento Grid 首页
│   │   ├── PostDetail.vue     # 文章详情
│   │   ├── Posts.vue          # 文章列表
│   │   ├── Tags.vue           # 标签列表
│   │   └── admin/
│   │       ├── Login.vue
│   │       ├── Dashboard.vue
│   │       └── Editor.vue
│   ├── components/
│   │   ├── ThemeSwitcher.vue
│   │   ├── Navbar.vue
│   │   ├── PostCard.vue
│   │   ├── Pagination.vue
│   │   └── MarkdownPreview.vue
│   └── assets/styles/
│       ├── main.css           # 全局样式 + CSS 变量
│       └── themes.css         # 三套主题变量
├── index.html
├── package.json
└── vite.config.js
```

---

## Phase 1: 后端基础

### Task 1.1: 项目脚手架 + 数据库配置

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/pyproject.toml`
- Create: `backend/app/__init__.py`
- Create: `backend/app/config.py`
- Create: `backend/app/database.py`
- Create: `backend/app/main.py`

- [ ] **Step 1: 创建 requirements.txt**

写入 `backend/requirements.txt`:

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy[asyncio]==2.0.35
asyncpg==0.30.0
alembic==1.13.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.12
python-markdown==3.7.0
pygments==2.18.0
bleach==6.1.0
pytest==8.3.0
pytest-asyncio==0.24.0
httpx==0.27.0
```

- [ ] **Step 2: 创建 pyproject.toml**

写入 `backend/pyproject.toml`:

```toml
[project]
name = "blog-backend"
version = "0.1.0"
requires-python = ">=3.11"

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"

[tool.ruff]
line-length = 100
```

- [ ] **Step 3: 创建 config.py**

写入 `backend/app/config.py`:

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/blog"
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24h
    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = {"env_prefix": "BLOG_", "env_file": ".env"}


settings = Settings()
```

- [ ] **Step 4: 创建 database.py**

写入 `backend/app/database.py`:

```python
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

- [ ] **Step 5: 创建 models/__init__.py**

写入 `backend/app/models/__init__.py`:

```python
from app.models.user import User
from app.models.post import Post
from app.models.tag import Tag
from app.models.category import Category

__all__ = ["User", "Post", "Tag", "Category"]
```

- [ ] **Step 6: 创建 main.py（脚手架版本）**

写入 `backend/app/main.py`:

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Blog API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 7: 验证启动**

Run:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Expected: 访问 http://localhost:8000/docs 看到 Swagger UI

---

### Task 1.2: 数据模型

**Files:**
- Create: `backend/app/models/user.py`
- Create: `backend/app/models/post.py`
- Create: `backend/app/models/tag.py`
- Create: `backend/app/models/category.py`

- [ ] **Step 1: 创建 User 模型**

写入 `backend/app/models/user.py`:

```python
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
```

- [ ] **Step 2: 创建 Category 模型**

写入 `backend/app/models/category.py`:

```python
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
```

- [ ] **Step 3: 创建 Tag 模型**

写入 `backend/app/models/tag.py`:

```python
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
```

- [ ] **Step 4: 创建 Post 模型**

写入 `backend/app/models/post.py`:

```python
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class PostStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    content_md: Mapped[str] = mapped_column(Text, nullable=False)
    content_html: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[PostStatus] = mapped_column(
        Enum(PostStatus), default=PostStatus.DRAFT
    )
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    author = relationship("User", lazy="joined")
    category = relationship("Category", lazy="joined")
    tags = relationship("Tag", secondary=post_tags, lazy="selectin")
```

注意: 需要在文件顶部添加导入:

```python
from sqlalchemy import Column, Table
```

修正后的完整导入段:

```python
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Table, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)
```

- [ ] **Step 5: 初始化 Alembic**

```bash
cd backend
alembic init alembic
```

编辑 `backend/alembic.ini`，修改数据库连接:
```ini
sqlalchemy.url = postgresql+asyncpg://postgres:postgres@localhost:5432/blog
```

编辑 `backend/alembic/env.py`:
```python
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.database import Base
from app.models import User, Post, Tag, Category  # noqa: F401
from app.config import settings

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

- [ ] **Step 6: 生成初始迁移**

```bash
cd backend
alembic revision --autogenerate -m "init models"
alembic upgrade head
```
Expected: `INFO  [alembic.runtime.migration] Running upgrade -> xxx, init models`

---

### Task 1.3: Pydantic Schemas

**Files:**
- Create: `backend/app/schemas/__init__.py`
- Create: `backend/app/schemas/post.py`
- Create: `backend/app/schemas/tag.py`
- Create: `backend/app/schemas/category.py`
- Create: `backend/app/schemas/auth.py`

- [ ] **Step 1: 创建 schemas/__init__.py**

```python
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.schemas.post import PostCreate, PostListItem, PostResponse, PostUpdate
from app.schemas.tag import TagCreate, TagResponse, TagUpdate

__all__ = [
    "LoginRequest", "TokenResponse",
    "CategoryCreate", "CategoryResponse", "CategoryUpdate",
    "PostCreate", "PostListItem", "PostResponse", "PostUpdate",
    "TagCreate", "TagResponse", "TagUpdate",
]
```

- [ ] **Step 2: 创建 auth.py**

```python
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

- [ ] **Step 3: 创建 tag.py**

```python
from datetime import datetime

from pydantic import BaseModel


class TagBase(BaseModel):
    name: str
    slug: str


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None


class TagResponse(TagBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
```

- [ ] **Step 4: 创建 category.py**

```python
from datetime import datetime

from pydantic import BaseModel


class CategoryBase(BaseModel):
    name: str
    slug: str
    description: str | None = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    description: str | None = None


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
```

- [ ] **Step 5: 创建 post.py**

```python
from datetime import datetime

from pydantic import BaseModel

from app.schemas.category import CategoryResponse
from app.schemas.tag import TagResponse


class PostBase(BaseModel):
    title: str
    slug: str
    content_md: str
    summary: str | None = None
    category_id: int | None = None
    tag_ids: list[int] = []


class PostCreate(PostBase):
    status: str = "draft"


class PostUpdate(BaseModel):
    title: str | None = None
    slug: str | None = None
    content_md: str | None = None
    summary: str | None = None
    status: str | None = None
    category_id: int | None = None
    tag_ids: list[int] | None = None


class PostListItem(BaseModel):
    id: int
    title: str
    slug: str
    summary: str | None
    status: str
    category: CategoryResponse | None = None
    tags: list[TagResponse] = []
    created_at: datetime
    published_at: datetime | None = None

    model_config = {"from_attributes": True}


class PostResponse(PostListItem):
    content_md: str
    content_html: str
    updated_at: datetime

    model_config = {"from_attributes": True}
```

---

### Task 1.4: Markdown 渲染服务

**Files:**
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/services/markdown.py`
- Create: `backend/tests/test_markdown.py`

- [ ] **Step 1: 创建 services/__init__.py**

空文件。

- [ ] **Step 2: 创建 markdown.py**

```python
import markdown as md
import bleach

ALLOWED_TAGS = [
    "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "br", "hr",
    "a", "img",
    "ul", "ol", "li",
    "pre", "code", "blockquote",
    "table", "thead", "tbody", "tr", "th", "td",
    "strong", "em", "del", "ins", "sup", "sub",
    "div", "span", "dl", "dt", "dd", "abbr", "cite",
]

ALLOWED_ATTRS = {
    "a": ["href", "title", "rel"],
    "img": ["src", "alt", "title"],
    "code": ["class"],
    "pre": ["class"],
    "th": ["align"],
    "td": ["align"],
    "*": ["id"],
}

EXTENSIONS = [
    "markdown.extensions.fenced_code",
    "markdown.extensions.codehilite",
    "markdown.extensions.tables",
    "markdown.extensions.toc",
    "markdown.extensions.nl2br",
]


def render_markdown(text: str) -> str:
    """渲染 Markdown 并清洗 HTML，返回安全的 HTML 字符串"""
    html = md.markdown(text, extensions=EXTENSIONS)
    cleaned = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        strip=True,
    )
    return cleaned
```

- [ ] **Step 3: 创建测试文件**

```bash
mkdir -p backend/tests
```

写入 `backend/tests/test_markdown.py`:

```python
import pytest
from app.services.markdown import render_markdown


def test_basic_markdown():
    html = render_markdown("# Hello")
    assert "<h1>Hello</h1>" in html


def test_code_block():
    md_text = "```python\nprint('hi')\n```"
    html = render_markdown(md_text)
    assert "<code" in html or "<pre" in html


def test_xss_removed():
    malicious = '<script>alert("xss")</script>'
    html = render_markdown(malicious)
    assert "<script>" not in html


def test_allowed_tags_preserved():
    html = render_markdown("[link](http://example.com)")
    assert '<a href="http://example.com"' in html
```

- [ ] **Step 4: 运行测试**

```bash
cd backend
pytest tests/test_markdown.py -v
```
Expected: 4 passed

---

### Task 1.5: JWT 认证依赖

**Files:**
- Create: `backend/app/dependencies/__init__.py`
- Create: `backend/app/dependencies/auth.py`

- [ ] **Step 1: 创建 dependencies/__init__.py**

空文件。

- [ ] **Step 2: 创建 auth.py**

```python
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return int(payload["sub"])
    except (JWTError, ValueError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    user_id = decode_token(credentials.credentials)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
```

- [ ] **Step 3: 写测试**

写入 `backend/tests/test_auth.py`:

```python
import pytest
from app.dependencies.auth import create_access_token, decode_token, hash_password, verify_password


def test_password_hashing():
    hashed = hash_password("hello123")
    assert verify_password("hello123", hashed)
    assert not verify_password("wrong", hashed)


def test_token_roundtrip():
    token = create_access_token(42)
    user_id = decode_token(token)
    assert user_id == 42


def test_invalid_token():
    with pytest.raises(Exception):
        decode_token("bad-token")
```

- [ ] **Step 4: 运行测试**

```bash
cd backend
pytest tests/ -v
```
Expected: 7 passed (4 from markdown + 3 from auth)

---

### Task 1.6: 公开 API 路由

**Files:**
- Create: `backend/app/routers/__init__.py`
- Create: `backend/app/routers/posts.py`
- Create: `backend/app/routers/tags.py`
- Create: `backend/app/routers/categories.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 创建 routers/__init__.py**

空文件。

- [ ] **Step 2: 创建 categories.py (公开)**

```python
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryResponse

router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).order_by(Category.name))
    return result.scalars().all()


@router.get("/{slug}", response_model=CategoryResponse)
async def get_category(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).where(Category.slug == slug))
    category = result.scalar_one_or_none()
    if category is None:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category
```

- [ ] **Step 3: 创建 tags.py (公开)**

```python
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.tag import Tag
from app.schemas.tag import TagResponse

router = APIRouter(prefix="/api/v1/tags", tags=["Tags"])


@router.get("", response_model=list[TagResponse])
async def list_tags(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag).order_by(Tag.name))
    return result.scalars().all()


@router.get("/{slug}", response_model=TagResponse)
async def get_tag(slug: str, db: AsyncSession = Depends(get_db)):
    from fastapi import HTTPException, status
    result = await db.execute(select(Tag).where(Tag.slug == slug))
    tag = result.scalar_one_or_none()
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag
```

- [ ] **Step 4: 创建 posts.py (公开)**

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.post import Post, PostStatus
from app.schemas.post import PostListItem, PostResponse

router = APIRouter(prefix="/api/v1/posts", tags=["Posts"])


@router.get("", response_model=list[PostListItem])
async def list_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    tag: str | None = None,
    category: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Post)
        .where(Post.status == PostStatus.PUBLISHED)
        .options(selectinload(Post.tags), selectinload(Post.category))
        .order_by(Post.published_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    if tag:
        query = query.where(Post.tags.any(slug=tag))
    if category:
        query = query.where(Post.category.has(slug=category))

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{slug}", response_model=PostResponse)
async def get_post(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Post)
        .where(Post.slug == slug, Post.status == PostStatus.PUBLISHED)
        .options(selectinload(Post.tags), selectinload(Post.category))
    )
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.get("/search", response_model=list[PostListItem])
async def search_posts(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Post)
        .where(
            Post.status == PostStatus.PUBLISHED,
            Post.title.ilike(f"%{q}%"),
        )
        .options(selectinload(Post.tags), selectinload(Post.category))
        .order_by(Post.published_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()
```

注意: `search` 路由必须放在 `/{slug}` 之前，否则 FastAPI 会把 "search" 视为 slug 值。在 main.py 中按此顺序 include_router。

- [ ] **Step 5: 注册路由到 main.py**

编辑 `backend/app/main.py`:

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import categories, posts, tags


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Blog API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts.router)
app.include_router(tags.router)
app.include_router(categories.router)


@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 6: 手动测试**

确保 PostgreSQL 运行中且有数据后:
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```
访问 http://localhost:8000/docs → 确认 3 组路由可见

---

### Task 1.7: 后台 API 路由

**Files:**
- Create: `backend/app/routers/admin/__init__.py`
- Create: `backend/app/routers/admin/auth.py`
- Create: `backend/app/routers/admin/posts.py`
- Create: `backend/app/routers/admin/tags.py`
- Create: `backend/app/routers/admin/categories.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 创建 admin/__init__.py**

空文件。

- [ ] **Step 2: 创建 admin/auth.py**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import create_access_token, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/api/v1/admin/auth", tags=["Admin Auth"])


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == body.username))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_access_token(user.id)
    return TokenResponse(access_token=token)
```

- [ ] **Step 3: 创建 admin/tags.py**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagResponse, TagUpdate

router = APIRouter(prefix="/api/v1/admin/tags", tags=["Admin Tags"],
                   dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[TagResponse])
async def list_tags(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag).order_by(Tag.name))
    return result.scalars().all()


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(body: TagCreate, db: AsyncSession = Depends(get_db)):
    tag = Tag(name=body.name, slug=body.slug)
    db.add(tag)
    await db.flush()
    await db.refresh(tag)
    return tag


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(tag_id: int, body: TagUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    if body.name is not None:
        tag.name = body.name
    if body.slug is not None:
        tag.slug = body.slug
    await db.flush()
    await db.refresh(tag)
    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tag_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    await db.delete(tag)
    await db.flush()
```

- [ ] **Step 4: 创建 admin/categories.py**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate

router = APIRouter(prefix="/api/v1/admin/categories", tags=["Admin Categories"],
                   dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[CategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).order_by(Category.name))
    return result.scalars().all()


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(body: CategoryCreate, db: AsyncSession = Depends(get_db)):
    category = Category(name=body.name, slug=body.slug, description=body.description)
    db.add(category)
    await db.flush()
    await db.refresh(category)
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: int, body: CategoryUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    if body.name is not None:
        category.name = body.name
    if body.slug is not None:
        category.slug = body.slug
    if body.description is not None:
        category.description = body.description
    await db.flush()
    await db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    await db.delete(category)
    await db.flush()
```

- [ ] **Step 5: 创建 admin/posts.py**

```python
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.post import Post, PostStatus
from app.models.tag import Tag
from app.schemas.post import PostCreate, PostListItem, PostResponse, PostUpdate
from app.services.markdown import render_markdown

router = APIRouter(prefix="/api/v1/admin/posts", tags=["Admin Posts"],
                   dependencies=[Depends(get_current_user)])


def _generate_summary(content_md: str, max_len: int = 200) -> str:
    clean = content_md.strip()
    if len(clean) <= max_len:
        return clean
    return clean[:max_len].rsplit(" ", 1)[0] + "..."


@router.get("", response_model=list[PostListItem])
async def list_posts_admin(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Post)
        .options(selectinload(Post.tags), selectinload(Post.category))
        .order_by(Post.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    body: PostCreate,
    db: AsyncSession = Depends(get_db),
    author=Depends(get_current_user),
):
    content_html = render_markdown(body.content_md)
    summary = body.summary or _generate_summary(body.content_md)

    post = Post(
        title=body.title,
        slug=body.slug,
        content_md=body.content_md,
        content_html=content_html,
        summary=summary,
        status=PostStatus(body.status) if body.status else PostStatus.DRAFT,
        author_id=author.id,
        category_id=body.category_id,
    )

    if body.tag_ids:
        result = await db.execute(select(Tag).where(Tag.id.in_(body.tag_ids)))
        post.tags = list(result.scalars().all())

    db.add(post)
    await db.flush()
    await db.refresh(post)
    return post


@router.get("/{post_id}", response_model=PostResponse)
async def get_post_admin(post_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Post).where(Post.id == post_id).options(
            selectinload(Post.tags), selectinload(Post.category)
        )
    )
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, body: PostUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Post).where(Post.id == post_id).options(
            selectinload(Post.tags), selectinload(Post.category)
        )
    )
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    if body.title is not None:
        post.title = body.title
    if body.slug is not None:
        post.slug = body.slug
    if body.content_md is not None:
        post.content_md = body.content_md
        post.content_html = render_markdown(body.content_md)
    if body.summary is not None:
        post.summary = body.summary
    if body.status is not None:
        post.status = PostStatus(body.status)
    if body.category_id is not None:
        post.category_id = body.category_id
    if body.tag_ids is not None:
        tag_result = await db.execute(select(Tag).where(Tag.id.in_(body.tag_ids)))
        post.tags = list(tag_result.scalars().all())

    await db.flush()
    await db.refresh(post)
    return post


@router.put("/{post_id}/publish", response_model=PostResponse)
async def publish_post(post_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Post).where(Post.id == post_id).options(
            selectinload(Post.tags), selectinload(Post.category)
        )
    )
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.status == PostStatus.PUBLISHED:
        post.status = PostStatus.DRAFT
        post.published_at = None
    else:
        post.status = PostStatus.PUBLISHED
        post.published_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(post)
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    await db.delete(post)
    await db.flush()
```

- [ ] **Step 6: 注册 admin 路由到 main.py**

修改 `backend/app/main.py` 中的导入和路由注册:

```python
from app.routers.admin import auth as admin_auth
from app.routers.admin import posts as admin_posts
from app.routers.admin import tags as admin_tags
from app.routers.admin import categories as admin_categories

# 注册路由
app.include_router(admin_auth.router)
app.include_router(admin_posts.router)
app.include_router(admin_tags.router)
app.include_router(admin_categories.router)
```

- [ ] **Step 7: 加入种子脚本 (创建初始管理员)**

创建 `backend/scripts/seed.py`:

```bash
mkdir -p backend/scripts
```

写入 `backend/scripts/seed.py`:

```python
"""创建初始管理员用户。运行: python -m scripts.seed"""
import asyncio

from app.database import async_session
from app.dependencies.auth import hash_password
from app.models.user import User


async def main():
    async with async_session() as session:
        user = User(username="admin", password_hash=hash_password("admin123"))
        session.add(user)
        await session.commit()
        print("Admin user created: admin / admin123")


asyncio.run(main())
```

---

## Phase 2: 前端基础

### Task 2.1: Vue 3 项目初始化

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.vue`

- [ ] **Step 1: 创建项目**

```bash
cd frontend
npm create vite@latest . -- --template vue
npm install vue-router@4 pinia axios marked highlight.js
npm install -D @vitejs/plugin-vue
```

- [ ] **Step 2: 修改 vite.config.js**

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

- [ ] **Step 3: 创建 main.js**

```javascript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/styles/main.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
```

- [ ] **Step 4: 创建 App.vue (基础壳子)**

```vue
<script setup>
import Navbar from './components/Navbar.vue'
</script>

<template>
  <div class="app">
    <Navbar />
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
}
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}
</style>
```

---

### Task 2.2: CSS 变量 + 三主题系统

**Files:**
- Create: `frontend/src/assets/styles/main.css`
- Create: `frontend/src/assets/styles/themes.css`
- Create: `frontend/src/composables/useTheme.js`
- Create: `frontend/src/components/ThemeSwitcher.vue`
- Modify: `frontend/src/App.vue`

- [ ] **Step 1: 创建 themes.css**

```css
/* ===== 主题变量 ===== */
:root,
[data-theme="dracula"] {
  --bg: #282a36;
  --bg-card: rgba(248, 248, 242, 0.03);
  --bg-hover: rgba(248, 248, 242, 0.06);
  --text-primary: #f8f8f2;
  --text-secondary: rgba(248, 248, 242, 0.5);
  --text-muted: rgba(248, 248, 242, 0.3);
  --accent: #bd93f9;
  --accent-secondary: #ff79c6;
  --border: rgba(248, 248, 242, 0.08);
  --border-hover: rgba(248, 248, 242, 0.15);
  --nav-bg: rgba(40, 42, 54, 0.95);
  --tag-bg: rgba(189, 147, 249, 0.15);
  --tag-text: #bd93f9;
  --card-radius: 14px;
}

[data-theme="amber"] {
  --bg: #0d0b09;
  --bg-card: rgba(255, 255, 255, 0.03);
  --bg-hover: rgba(255, 255, 255, 0.06);
  --text-primary: #faf5ed;
  --text-secondary: rgba(250, 245, 237, 0.5);
  --text-muted: rgba(250, 245, 237, 0.25);
  --accent: #f59e0b;
  --accent-secondary: #d97706;
  --border: rgba(255, 255, 255, 0.08);
  --border-hover: rgba(255, 255, 255, 0.15);
  --nav-bg: rgba(13, 11, 9, 0.95);
  --tag-bg: rgba(245, 158, 11, 0.15);
  --tag-text: #fbbf24;
  --card-radius: 14px;
}

[data-theme="slate"] {
  --bg: #fafbfc;
  --bg-card: #ffffff;
  --bg-hover: #f3f4f6;
  --text-primary: #111827;
  --text-secondary: #6b7280;
  --text-muted: #9ca3af;
  --accent: #111827;
  --accent-secondary: #4b5563;
  --border: #e5e7eb;
  --border-hover: #d1d5db;
  --nav-bg: rgba(250, 251, 252, 0.95);
  --tag-bg: #f3f4f6;
  --tag-text: #4b5563;
  --card-radius: 12px;
}
```

- [ ] **Step 2: 创建 main.css**

```css
@import './themes.css';

*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  color-scheme: dark;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC',
    'Noto Sans SC', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background-color: var(--bg);
  color: var(--text-primary);
  line-height: 1.6;
  transition: background-color 0.3s, color 0.3s;
  -webkit-font-smoothing: antialiased;
}

a {
  color: var(--accent);
  text-decoration: none;
}

img {
  max-width: 100%;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  gap: 6px;
  padding: 20px 0;
}

.pagination button {
  background: var(--bg-card);
  border: 1px solid var(--border);
  color: var(--text-primary);
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: border-color 0.2s;
}

.pagination button:hover {
  border-color: var(--accent);
}

.pagination button.active {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}
```

- [ ] **Step 3: 创建 useTheme.js**

```javascript
import { ref, watch } from 'vue'

const THEMES = ['dracula', 'amber', 'slate']
const currentTheme = ref(localStorage.getItem('blog-theme') || 'dracula')

export function useTheme() {
  const applyTheme = (theme) => {
    document.documentElement.setAttribute('data-theme', theme)
    currentTheme.value = theme
    localStorage.setItem('blog-theme', theme)
  }

  const cycleTheme = () => {
    const idx = THEMES.indexOf(currentTheme.value)
    const next = THEMES[(idx + 1) % THEMES.length]
    applyTheme(next)
  }

  // 初始化
  applyTheme(currentTheme.value)

  return {
    currentTheme,
    themes: THEMES,
    cycleTheme,
    applyTheme,
  }
}
```

- [ ] **Step 4: 创建 ThemeSwitcher.vue**

```vue
<script setup>
import { useTheme } from '../composables/useTheme.js'

const { currentTheme, cycleTheme } = useTheme()

const themeIcon = {
  dracula: '☾',
  amber: '☀',
  slate: '◐',
}
</script>

<template>
  <button class="theme-btn" @click="cycleTheme" :title="`Theme: ${currentTheme}`">
    <span>{{ themeIcon[currentTheme] }}</span>
  </button>
</template>

<style scoped>
.theme-btn {
  background: var(--bg-card);
  border: 1px solid var(--border);
  color: var(--text-primary);
  width: 36px;
  height: 36px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 0.2s;
}
.theme-btn:hover {
  border-color: var(--accent);
}
</style>
```

- [ ] **Step 5: 创建 Navbar.vue**

```vue
<script setup>
import { useRouter } from 'vue-router'
import ThemeSwitcher from './ThemeSwitcher.vue'

const router = useRouter()
</script>

<template>
  <nav class="navbar">
    <div class="navbar-inner">
      <div class="nav-left">
        <span class="logo" @click="router.push('/')">
          <span class="logo-accent">&lt;/&gt;</span> devlog
        </span>
      </div>
      <div class="nav-center">
        <router-link to="/" class="nav-link">Home</router-link>
        <router-link to="/posts" class="nav-link">Posts</router-link>
        <router-link to="/tags" class="nav-link">Tags</router-link>
      </div>
      <div class="nav-right">
        <ThemeSwitcher />
      </div>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--nav-bg);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
}
.navbar-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 56px;
}
.logo {
  font-size: 18px;
  font-weight: 700;
  cursor: pointer;
  color: var(--text-primary);
}
.logo-accent {
  background: linear-gradient(135deg, var(--accent), var(--accent-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.nav-center {
  display: flex;
  gap: 24px;
}
.nav-link {
  color: var(--text-secondary);
  font-size: 13px;
  transition: color 0.2s;
}
.nav-link:hover,
.nav-link.router-link-active {
  color: var(--text-primary);
}
</style>
```

---

### Task 2.3: API 封装

**Files:**
- Create: `frontend/src/api/index.js`

- [ ] **Step 1: 创建 API 封装**

```javascript
import axios from 'axios'
import { useAppStore } from '../stores/app.js'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const store = useAppStore()
  if (store.token) {
    config.headers.Authorization = `Bearer ${store.token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      const store = useAppStore()
      store.logout()
    }
    return Promise.reject(err)
  }
)

export function getPosts(params) {
  return api.get('/posts', { params })
}

export function getPost(slug) {
  return api.get(`/posts/${slug}`)
}

export function searchPosts(params) {
  return api.get('/posts/search', { params })
}

export function getTags() {
  return api.get('/tags')
}

export function getCategories() {
  return api.get('/categories')
}

// Admin
export function adminLogin(username, password) {
  return api.post('/admin/auth/login', { username, password })
}

export function adminGetPosts(params) {
  return api.get('/admin/posts', { params })
}

export function adminGetPost(id) {
  return api.get(`/admin/posts/${id}`)
}

export function adminCreatePost(data) {
  return api.post('/admin/posts', data)
}

export function adminUpdatePost(id, data) {
  return api.put(`/admin/posts/${id}`, data)
}

export function adminDeletePost(id) {
  return api.delete(`/admin/posts/${id}`)
}

export function adminTogglePublish(id) {
  return api.put(`/admin/posts/${id}/publish`)
}

export function adminGetTags() {
  return api.get('/admin/tags')
}

export function adminCreateTag(data) {
  return api.post('/admin/tags', data)
}

export function adminUpdateTag(id, data) {
  return api.put(`/admin/tags/${id}`, data)
}

export function adminDeleteTag(id) {
  return api.delete(`/admin/tags/${id}`)
}

export function adminGetCategories() {
  return api.get('/admin/categories')
}

export function adminCreateCategory(data) {
  return api.post('/admin/categories', data)
}

export function adminUpdateCategory(id, data) {
  return api.put(`/admin/categories/${id}`, data)
}

export function adminDeleteCategory(id) {
  return api.delete(`/admin/categories/${id}`)
}
```

- [ ] **Step 2: 创建 Pinia 状态 store**

```javascript
// stores/app.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  const token = ref(localStorage.getItem('blog-token') || '')
  const user = ref(null)

  const isLoggedIn = computed(() => !!token.value)

  function setToken(t) {
    token.value = t
    localStorage.setItem('blog-token', t)
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('blog-token')
  }

  return { token, user, isLoggedIn, setToken, logout }
})
```

---

### Task 2.4: Vue Router

**Files:**
- Create: `frontend/src/router/index.js`

- [ ] **Step 1: 创建路由**

```javascript
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Home', component: () => import('../views/Home.vue') },
  { path: '/posts', name: 'Posts', component: () => import('../views/Posts.vue') },
  { path: '/posts/:slug', name: 'PostDetail', component: () => import('../views/PostDetail.vue') },
  { path: '/tags', name: 'Tags', component: () => import('../views/Tags.vue') },
  { path: '/admin/login', name: 'Login', component: () => import('../views/admin/Login.vue') },
  { path: '/admin', name: 'Dashboard', component: () => import('../views/admin/Dashboard.vue'), meta: { requiresAuth: true } },
  { path: '/admin/posts/new', name: 'NewPost', component: () => import('../views/admin/Editor.vue'), meta: { requiresAuth: true } },
  { path: '/admin/posts/:id/edit', name: 'EditPost', component: () => import('../views/admin/Editor.vue'), meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !localStorage.getItem('blog-token')) {
    return '/admin/login'
  }
})

export default router
```

---

### Task 2.5: PostCard 组件

**Files:**
- Create: `frontend/src/components/PostCard.vue`

- [ ] **Step 1: 创建 PostCard**

```vue
<script setup>
defineProps({
  post: { type: Object, required: true },
})
</script>

<template>
  <router-link :to="`/posts/${post.slug}`" class="post-card">
    <div class="post-meta">
      <span class="post-date">{{ new Date(post.published_at || post.created_at).toLocaleDateString('zh-CN') }}</span>
      <span v-if="post.category" class="post-category">{{ post.category.name }}</span>
    </div>
    <h3 class="post-title">{{ post.title }}</h3>
    <p v-if="post.summary" class="post-summary">{{ post.summary }}</p>
    <div v-if="post.tags?.length" class="post-tags">
      <span v-for="tag in post.tags" :key="tag.id" class="tag">{{ tag.name }}</span>
    </div>
  </router-link>
</template>

<style scoped>
.post-card {
  display: block;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--card-radius);
  padding: 16px 20px;
  transition: border-color 0.2s, background 0.2s;
  text-decoration: none;
  color: inherit;
}
.post-card:hover {
  border-color: var(--border-hover);
  background: var(--bg-hover);
}
.post-meta {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 6px;
}
.post-date {
  font-size: 11px;
  color: var(--text-muted);
}
.post-category {
  font-size: 9px;
  background: var(--tag-bg);
  color: var(--tag-text);
  padding: 1px 6px;
  border-radius: 4px;
}
.post-title {
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 6px;
  line-height: 1.4;
}
.post-summary {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 8px;
}
.post-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}
.tag {
  font-size: 10px;
  background: var(--tag-bg);
  color: var(--tag-text);
  padding: 2px 8px;
  border-radius: 12px;
}
</style>
```

---

### Task 2.6: 首页 (Bento Grid)

**Files:**
- Create: `frontend/src/views/Home.vue`

- [ ] **Step 1: 创建 Home.vue**

```vue
<script setup>
import { ref, onMounted } from 'vue'
import PostCard from '../components/PostCard.vue'
import { getPosts, getTags, getCategories } from '../api/index.js'

const posts = ref([])
const tags = ref([])
const categories = ref([])
const featuredPost = ref(null)

onMounted(async () => {
  try {
    const [postsRes, tagsRes, catsRes] = await Promise.all([
      getPosts({ limit: 6 }),
      getTags(),
      getCategories(),
    ])
    posts.value = postsRes.data
    tags.value = tagsRes.data
    categories.value = catsRes.data
    featuredPost.value = posts.value[0] || null
  } catch (e) {
    console.error('Failed to load home data', e)
  }
})
</script>

<template>
  <div class="home">
    <!-- Bento Grid -->
    <div class="bento-grid">
      <!-- Hero -->
      <div class="bento-hero">
        <span class="hero-label">Technical Blog</span>
        <h1 class="hero-title">
          <span class="hero-accent">Hello,</span><br>I Write Code &amp; Thoughts
        </h1>
        <p class="hero-desc">Python · Vue · System Design<br>记录技术探索的每一步</p>
        <div class="hero-stats">
          <div v-if="posts.length" class="stat">
            <span class="stat-num">{{ posts.length }}+</span>
            <span class="stat-label">Articles</span>
          </div>
          <div v-if="tags.length" class="stat">
            <span class="stat-num">{{ tags.length }}</span>
            <span class="stat-label">Topics</span>
          </div>
        </div>
      </div>

      <!-- Profile -->
      <div class="bento-profile">
        <div class="avatar">👨‍💻</div>
        <div>
          <div class="profile-name">Moon</div>
          <div class="profile-role">Developer</div>
        </div>
      </div>

      <!-- Social -->
      <div class="bento-social">
        <div class="social-item">🐙 github.com/moon</div>
        <div class="social-item">🐦 @moon_dev</div>
      </div>

      <!-- Featured Post -->
      <div v-if="featuredPost" class="bento-featured">
        <span class="featured-badge">PINNED</span>
        <span class="featured-label">Featured Article</span>
        <h2 class="featured-title">{{ featuredPost.title }}</h2>
        <p class="featured-summary">{{ featuredPost.summary }}</p>
        <div class="featured-tags">
          <span v-for="tag in featuredPost.tags" :key="tag.id" class="tag-featured">{{ tag.name }}</span>
          <span class="featured-date">{{ new Date(featuredPost.published_at).toLocaleDateString('zh-CN') }}</span>
        </div>
      </div>

      <!-- Categories -->
      <div class="bento-categories">
        <router-link v-for="cat in categories" :key="cat.id" :to="`/posts?category=${cat.slug}`" class="cat-item">
          <div class="cat-name">{{ cat.name }}</div>
        </router-link>
      </div>

      <!-- Tag Cloud -->
      <div class="bento-tags">
        <div class="bento-tags-title">Topics</div>
        <div class="tags-cloud">
          <router-link v-for="tag in tags" :key="tag.id" :to="`/tags/${tag.slug}`"
            class="cloud-tag" :style="{ borderColor: 'var(--border)' }">
            {{ tag.name }}
          </router-link>
        </div>
      </div>
    </div>

    <!-- Recent Posts -->
    <div v-if="posts.length" class="recent-section">
      <div class="section-header">
        <span class="section-title">Recent Posts</span>
        <router-link to="/posts" class="section-link">View all →</router-link>
      </div>
      <div v-if="posts.length" class="recent-grid">
        <PostCard v-for="post in posts" :key="post.id" :post="post" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.home {
  padding: 24px 0 40px;
}

/* Bento Grid */
.bento-grid {
  display: grid;
  grid-template-columns: 1.8fr 1fr 1fr;
  grid-auto-rows: auto;
  gap: 12px;
  margin-bottom: 32px;
}

.bento-grid > div {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--card-radius);
  padding: 20px;
  position: relative;
  overflow: hidden;
  transition: border-color 0.2s;
}

/* Hero */
.bento-hero {
  grid-row: span 2;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.hero-label {
  font-size: 10px;
  color: var(--accent);
  background: var(--tag-bg);
  padding: 3px 10px;
  border-radius: 20px;
  display: inline-block;
  width: fit-content;
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-bottom: 12px;
}
.hero-title {
  font-size: 26px;
  font-weight: 800;
  line-height: 1.3;
  margin: 0 0 6px;
}
.hero-accent {
  background: linear-gradient(135deg, var(--accent), var(--accent-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-desc {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 16px;
}
.hero-stats {
  display: flex;
  gap: 24px;
}
.stat-num {
  font-size: 22px;
  font-weight: 700;
  display: block;
}
.stat-label {
  font-size: 10px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* Profile */
.bento-profile {
  display: flex;
  align-items: center;
  gap: 12px;
}
.avatar {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, var(--accent), var(--accent-secondary));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}
.profile-name {
  font-size: 14px;
  font-weight: 600;
}
.profile-role {
  font-size: 11px;
  color: var(--text-secondary);
}

/* Social */
.bento-social {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 8px;
}
.social-item {
  font-size: 11px;
  color: var(--accent);
}

/* Featured */
.bento-featured {
  grid-column: span 2;
  border: 1px solid var(--accent) !important;
}
.featured-badge {
  position: absolute;
  top: 0;
  right: 0;
  background: linear-gradient(135deg, var(--accent), var(--accent-secondary));
  color: #fff;
  font-size: 9px;
  padding: 3px 10px;
  font-weight: 600;
  border-radius: 0 var(--card-radius) 0 8px;
}
.featured-label {
  font-size: 10px;
  color: var(--accent);
  letter-spacing: 1px;
  text-transform: uppercase;
}
.featured-title {
  font-size: 17px;
  font-weight: 700;
  margin: 8px 0 4px;
  line-height: 1.3;
}
.featured-summary {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 10px;
}
.featured-tags {
  display: flex;
  gap: 6px;
  align-items: center;
}
.tag-featured {
  font-size: 10px;
  background: var(--tag-bg);
  color: var(--tag-text);
  padding: 2px 8px;
  border-radius: 4px;
}
.featured-date {
  font-size: 10px;
  color: var(--text-muted);
  margin-left: auto;
}

/* Categories */
.bento-categories {
  grid-column: span 2;
  display: flex;
  gap: 10px;
  align-items: center;
}
.cat-item {
  flex: 1;
  background: var(--bg-hover);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 12px;
  text-align: center;
  text-decoration: none;
  transition: border-color 0.2s;
}
.cat-item:hover {
  border-color: var(--accent);
}
.cat-name {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
}

/* Tag Cloud */
.bento-tags-title {
  font-size: 11px;
  color: var(--text-secondary);
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-bottom: 10px;
}
.tags-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}
.cloud-tag {
  font-size: 10px;
  padding: 4px 10px;
  border-radius: 12px;
  border: 1px solid var(--border);
  color: var(--text-primary);
  text-decoration: none;
  transition: border-color 0.2s;
}
.cloud-tag:hover {
  border-color: var(--accent);
}

/* Recent */
.recent-section {
  margin-top: 8px;
}
.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.section-title {
  font-size: 14px;
  font-weight: 600;
}
.section-link {
  font-size: 12px;
  color: var(--accent);
}
.section-link::before {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
  margin-right: 12px;
}
.recent-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

/* Responsive */
@media (max-width: 768px) {
  .bento-grid {
    grid-template-columns: 1fr;
  }
  .bento-hero { grid-row: auto; }
  .bento-featured { grid-column: auto; }
  .bento-categories { grid-column: auto; flex-wrap: wrap; }
  .recent-grid { grid-template-columns: 1fr; }
}
@media (min-width: 769px) and (max-width: 1023px) {
  .bento-grid { grid-template-columns: 1fr 1fr; }
  .recent-grid { grid-template-columns: 1fr 1fr; }
}
</style>
```

---

### Task 2.7: 文章列表 + 详情页

**Files:**
- Create: `frontend/src/views/Posts.vue`
- Create: `frontend/src/views/PostDetail.vue`
- Create: `frontend/src/views/Tags.vue`

- [ ] **Step 1: 创建 Posts.vue**

```vue
<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getPosts } from '../api/index.js'
import PostCard from '../components/PostCard.vue'
import Pagination from '../components/Pagination.vue'

const route = useRoute()
const posts = ref([])
const page = ref(1)
const total = ref(0)

async function load() {
  try {
    const params = { page: page.value, limit: 10 }
    if (route.query.tag) params.tag = route.query.tag
    if (route.query.category) params.category = route.query.category
    const res = await getPosts(params)
    posts.value = res.data
    total.value = parseInt(res.headers['x-total'] || '0')
  } catch (e) {
    console.error(e)
  }
}

onMounted(load)
watch(() => route.query, load)
</script>

<template>
  <div class="posts-page">
    <h2 class="page-title">Articles</h2>
    <div v-if="posts.length" class="posts-list">
      <PostCard v-for="post in posts" :key="post.id" :post="post" />
    </div>
    <div v-else class="empty-state">暂无文章</div>
    <Pagination v-if="total > 10" :page="page" :total="total" @change="page = $event; load()" />
  </div>
</template>

<style scoped>
.posts-page {
  padding: 24px 0 40px;
}
.page-title {
  font-size: 20px;
  margin-bottom: 20px;
}
.posts-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.empty-state {
  text-align: center;
  padding: 60px 0;
  color: var(--text-muted);
}
</style>
```

- [ ] **Step 2: 创建 Pagination.vue**

```vue
<script setup>
defineProps({ page: Number, total: Number })
const emit = defineEmits(['change'])
</script>

<template>
  <div class="pagination">
    <button :disabled="page <= 1" @click="emit('change', page - 1)">←</button>
    <button :class="{ active: true }">{{ page }}</button>
    <button :disabled="total <= page * 10" @click="emit('change', page + 1)">→</button>
  </div>
</template>
```

- [ ] **Step 3: 创建 PostDetail.vue**

```vue
<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getPost } from '../api/index.js'

const route = useRoute()
const router = useRouter()
const post = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await getPost(route.params.slug)
    post.value = res.data
  } catch (e) {
    router.push('/')
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="detail-page">
    <div v-if="loading" class="loading">Loading...</div>
    <article v-else-if="post" class="detail-article">
      <header class="detail-header">
        <div class="detail-meta">
          <span class="detail-date">{{ new Date(post.published_at).toLocaleDateString('zh-CN') }}</span>
          <span v-if="post.category" class="detail-category">{{ post.category.name }}</span>
          <span v-if="post.tags?.length">·</span>
          <span v-for="tag in post.tags" :key="tag.id" class="detail-tag">{{ tag.name }}</span>
        </div>
        <h1 class="detail-title">{{ post.title }}</h1>
      </header>
      <div class="detail-content" v-html="post.content_html"></div>
      <div class="detail-footer">
        <router-link to="/posts" class="back-link">← Back to articles</router-link>
      </div>
    </article>
  </div>
</template>

<style scoped>
.detail-page {
  padding: 32px 0 60px;
  max-width: 720px;
  margin: 0 auto;
}
.detail-header {
  margin-bottom: 32px;
}
.detail-meta {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 8px;
  display: flex;
  gap: 6px;
  align-items: center;
}
.detail-title {
  font-size: 32px;
  font-weight: 800;
  line-height: 1.25;
  letter-spacing: -0.5px;
}
.detail-content {
  font-size: 16px;
  line-height: 1.8;
  color: var(--text-primary);
}
.detail-content :deep(h2) {
  font-size: 24px;
  margin: 32px 0 12px;
}
.detail-content :deep(h3) {
  font-size: 20px;
  margin: 24px 0 8px;
}
.detail-content :deep(p) {
  margin-bottom: 16px;
}
.detail-content :deep(pre) {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px;
  overflow-x: auto;
  margin-bottom: 16px;
}
.detail-content :deep(code) {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 14px;
}
.detail-content :deep(a) {
  text-decoration: underline;
}
.detail-footer {
  margin-top: 48px;
  padding-top: 24px;
  border-top: 1px solid var(--border);
}
.back-link {
  font-size: 13px;
  color: var(--accent);
}
.loading {
  text-align: center;
  padding: 80px 0;
  color: var(--text-muted);
}
</style>
```

- [ ] **Step 4: 创建 Tags.vue**

```vue
<script setup>
import { ref, onMounted } from 'vue'
import { getTags } from '../api/index.js'

const tags = ref([])
onMounted(async () => {
  const res = await getTags()
  tags.value = res.data
})
</script>

<template>
  <div class="tags-page">
    <h2 class="page-title">Tags</h2>
    <div class="tags-grid">
      <router-link v-for="tag in tags" :key="tag.id" :to="`/posts?tag=${tag.slug}`" class="tag-card">
        <span class="tag-name">{{ tag.name }}</span>
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.tags-page { padding: 24px 0 40px; }
.page-title { font-size: 20px; margin-bottom: 20px; }
.tags-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.tag-card {
  background: var(--tag-bg);
  color: var(--tag-text);
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 13px;
  text-decoration: none;
  transition: opacity 0.2s;
}
.tag-card:hover { opacity: 0.8; }
</style>
```

---

## Phase 3: 后台前端

### Task 3.1: 登录页 + Dashboard

**Files:**
- Create: `frontend/src/views/admin/Login.vue`
- Create: `frontend/src/views/admin/Dashboard.vue`

- [ ] **Step 1: 创建 Login.vue**

```vue
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { adminLogin } from '../../api/index.js'
import { useAppStore } from '../../stores/app.js'

const router = useRouter()
const store = useAppStore()
const username = ref('')
const password = ref('')
const error = ref('')

async function login() {
  try {
    const res = await adminLogin(username.value, password.value)
    store.setToken(res.data.access_token)
    router.push('/admin')
  } catch (e) {
    error.value = '登录失败，请检查用户名和密码'
  }
}
</script>

<template>
  <div class="login-page">
    <form class="login-form" @submit.prevent="login">
      <h2 class="login-title">Admin Login</h2>
      <input v-model="username" placeholder="Username" class="input" />
      <input v-model="password" type="password" placeholder="Password" class="input" />
      <p v-if="error" class="error">{{ error }}</p>
      <button type="submit" class="btn">Login</button>
    </form>
  </div>
</template>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
}
.login-form {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--card-radius);
  padding: 32px;
  width: 360px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.login-title {
  text-align: center;
  margin-bottom: 8px;
}
.input {
  background: var(--bg);
  border: 1px solid var(--border);
  color: var(--text-primary);
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
}
.input:focus {
  border-color: var(--accent);
}
.btn {
  background: var(--accent);
  color: #fff;
  border: none;
  padding: 10px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}
.error { color: #ff6b6b; font-size: 12px; }
</style>
```

- [ ] **Step 2: 创建 Dashboard.vue**

```vue
<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { adminGetPosts, adminDeletePost, adminTogglePublish, adminGetTags, adminGetCategories } from '../../api/index.js'
import { useAppStore } from '../../stores/app.js'

const router = useRouter()
const store = useAppStore()
const posts = ref([])
const tags = ref([])
const categories = ref([])

onMounted(async () => {
  const [p, t, c] = await Promise.all([
    adminGetPosts({ limit: 100 }),
    adminGetTags(),
    adminGetCategories(),
  ])
  posts.value = p.data
  tags.value = t.data
  categories.value = c.data
})

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
    <div class="dash-header">
      <h2>Dashboard</h2>
      <div class="dash-actions">
        <router-link to="/admin/posts/new" class="btn-primary">+ New Post</router-link>
        <button @click="logout" class="btn-ghost">Logout</button>
      </div>
    </div>

    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-val">{{ posts.length }}</div>
        <div class="stat-lbl">Posts</div>
      </div>
      <div class="stat-card">
        <div class="stat-val">{{ tags.length }}</div>
        <div class="stat-lbl">Tags</div>
      </div>
      <div class="stat-card">
        <div class="stat-val">{{ categories.length }}</div>
        <div class="stat-lbl">Categories</div>
      </div>
    </div>

    <h3 class="section-title">Recent Posts</h3>
    <table class="post-table">
      <thead>
        <tr>
          <th>Title</th><th>Status</th><th>Date</th><th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="post in posts.slice(0, 10)" :key="post.id">
          <td>{{ post.title }}</td>
          <td><span :class="post.status">{{ post.status }}</span></td>
          <td class="date-cell">{{ new Date(post.created_at).toLocaleDateString('zh-CN') }}</td>
          <td class="actions-cell">
            <button @click="router.push(`/admin/posts/${post.id}/edit`)" class="btn-sm">Edit</button>
            <button @click="togglePublish(post.id)" class="btn-sm">
              {{ post.status === 'published' ? 'Unpublish' : 'Publish' }}
            </button>
            <button @click="removePost(post.id)" class="btn-sm btn-danger">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.dashboard { padding: 24px 0; }
.dash-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.dash-actions { display: flex; gap: 8px; align-items: center; }
.btn-primary {
  background: var(--accent); color: #fff; padding: 8px 16px;
  border-radius: 8px; text-decoration: none; font-size: 13px; font-weight: 600;
}
.btn-ghost { background: none; border: 1px solid var(--border); color: var(--text-primary); padding: 8px 16px; border-radius: 8px; cursor: pointer; font-size: 13px; }
.stats-row { display: flex; gap: 12px; margin-bottom: 24px; }
.stat-card {
  flex: 1; background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--card-radius); padding: 16px; text-align: center;
}
.stat-val { font-size: 28px; font-weight: 700; }
.stat-lbl { font-size: 11px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px; }
.post-table { width: 100%; border-collapse: collapse; }
.post-table th, .post-table td { padding: 10px 12px; text-align: left; border-bottom: 1px solid var(--border); font-size: 13px; }
.post-table th { color: var(--text-secondary); font-weight: 600; }
.draft { color: #f59e0b; font-size: 11px; text-transform: uppercase; }
.published { color: #22c55e; font-size: 11px; text-transform: uppercase; }
.date-cell { color: var(--text-muted); }
.actions-cell { display: flex; gap: 4px; }
.btn-sm {
  background: var(--bg-card); border: 1px solid var(--border); color: var(--text-primary);
  padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 11px;
}
.btn-danger { color: #ff6b6b; }
</style>
```

### Task 3.2: Markdown 编辑器

**Files:**
- Create: `frontend/src/views/admin/Editor.vue`
- Create: `frontend/src/components/MarkdownPreview.vue`

- [ ] **Step 1: 创建 MarkdownPreview.vue**

```vue
<script setup>
import { watch, ref } from 'vue'
import { marked } from 'marked'

const props = defineProps({ content: String })
const html = ref('')

watch(() => props.content, (val) => {
  html.value = val ? marked.parse(val) : ''
}, { immediate: true })
</script>

<template>
  <div class="preview" v-html="html"></div>
</template>

<style scoped>
.preview {
  line-height: 1.8;
  font-size: 15px;
}
.preview :deep(pre) {
  background: #1e1e2e;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
  padding: 14px;
  overflow-x: auto;
}
.preview :deep(code) {
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
}
</style>
```

- [ ] **Step 2: 创建 Editor.vue**

```vue
<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { adminGetPost, adminCreatePost, adminUpdatePost, adminGetTags, adminGetCategories } from '../../api/index.js'
import MarkdownPreview from '../../components/MarkdownPreview.vue'

const route = useRoute()
const router = useRouter()
const isEdit = !!route.params.id

const title = ref('')
const slug = ref('')
const contentMd = ref('')
const categoryId = ref(null)
const tagIds = ref([])
const tags = ref([])
const categories = ref([])

onMounted(async () => {
  const [tagRes, catRes] = await Promise.all([adminGetTags(), adminGetCategories()])
  tags.value = tagRes.data
  categories.value = catRes.data
  if (isEdit) {
    const res = await adminGetPost(route.params.id)
    const post = res.data
    title.value = post.title
    slug.value = post.slug
    contentMd.value = post.content_md
    categoryId.value = post.category?.id || null
    tagIds.value = post.tags.map(t => t.id)
  }
})

function generateSlug() {
  if (!slug.value && title.value) {
    slug.value = title.value
      .toLowerCase()
      .replace(/[^a-z0-9一-龥]+/g, '-')
      .replace(/(^-|-$)/g, '')
  }
}

async function save(status = 'draft') {
  const data = { title: title.value, slug: slug.value, content_md: contentMd.value, category_id: categoryId.value, tag_ids: tagIds.value, status }
  try {
    if (isEdit) {
      await adminUpdatePost(route.params.id, data)
    } else {
      await adminCreatePost(data)
    }
    router.push('/admin')
  } catch (e) {
    alert('保存失败: ' + (e.response?.data?.detail || e.message))
  }
}
</script>

<template>
  <div class="editor-page">
    <div class="editor-toolbar">
      <input v-model="title" placeholder="Article Title" class="title-input" @blur="generateSlug" />
      <div class="toolbar-actions">
        <button @click="save('draft')" class="btn-ghost">Save Draft</button>
        <button @click="save('published')" class="btn-primary">Publish</button>
      </div>
    </div>
    <div class="editor-meta">
      <input v-model="slug" placeholder="slug" class="slug-input" />
      <select v-model="categoryId" class="select">
        <option :value="null">No category</option>
        <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
      </select>
      <div class="tag-picker">
        <label v-for="t in tags" :key="t.id" class="tag-checkbox">
          <input type="checkbox" :value="t.id" v-model="tagIds" />
          {{ t.name }}
        </label>
      </div>
    </div>
    <div class="editor-body">
      <textarea v-model="contentMd" class="editor-textarea" placeholder="Write Markdown here..." />
      <MarkdownPreview :content="contentMd" class="editor-preview" />
    </div>
  </div>
</template>

<style scoped>
.editor-page { padding: 20px 0; }
.editor-toolbar {
  display: flex; gap: 12px; align-items: center; margin-bottom: 12px;
}
.title-input {
  flex: 1; background: var(--bg); border: 1px solid var(--border);
  color: var(--text-primary); padding: 12px 16px; border-radius: 10px;
  font-size: 20px; font-weight: 700; outline: none;
}
.title-input:focus { border-color: var(--accent); }
.toolbar-actions { display: flex; gap: 8px; }
.btn-primary { background: var(--accent); color: #fff; border: none; padding: 8px 20px; border-radius: 8px; font-weight: 600; cursor: pointer; }
.btn-ghost { background: var(--bg-card); border: 1px solid var(--border); color: var(--text-primary); padding: 8px 20px; border-radius: 8px; cursor: pointer; }
.editor-meta {
  display: flex; gap: 10px; margin-bottom: 12px; align-items: center; flex-wrap: wrap;
}
.slug-input { background: var(--bg); border: 1px solid var(--border); color: var(--text-primary); padding: 8px 12px; border-radius: 6px; font-size: 12px; outline: none; width: 200px; }
.select { background: var(--bg); border: 1px solid var(--border); color: var(--text-primary); padding: 8px; border-radius: 6px; font-size: 12px; }
.tag-picker { display: flex; gap: 8px; flex-wrap: wrap; }
.tag-checkbox { font-size: 12px; display: flex; align-items: center; gap: 4px; color: var(--text-secondary); }
.editor-body {
  display: grid; grid-template-columns: 1fr 1fr; gap: 12px; min-height: 60vh;
}
.editor-textarea {
  background: var(--bg); border: 1px solid var(--border); color: var(--text-primary);
  padding: 16px; border-radius: 10px; font-family: 'JetBrains Mono', monospace;
  font-size: 14px; line-height: 1.7; resize: vertical; outline: none;
}
.editor-textarea:focus { border-color: var(--accent); }
.editor-preview {
  background: var(--bg); border: 1px solid var(--border);
  padding: 16px; border-radius: 10px; overflow-y: auto;
}
@media (max-width: 768px) {
  .editor-body { grid-template-columns: 1fr; }
}
</style>
```

---

## Phase 4: 完善

### Task 4.1: 响应式适配 + 空状态

**Files:**
- Modify: `frontend/src/assets/styles/main.css`

- [ ] **Step 1: 完善全局 CSS**

在 `main.css` 末尾追加:

```css
@media (max-width: 768px) {
  .main-content {
    padding: 0 12px;
  }
}
```

### Task 4.2: .gitignore + 环境变量

**Files:**
- Create: `backend/.env.example`
- Create: `.gitignore`

- [ ] **Step 1: 创建 .env.example**

```bash
# backend/.env.example
BLOG_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/blog
BLOG_JWT_SECRET_KEY=change-me-in-production
BLOG_CORS_ORIGINS=["http://localhost:5173"]
```

- [ ] **Step 2: 创建 .gitignore (项目根目录)**

```gitignore
__pycache__/
.env
*.pyc
node_modules/
dist/
.superpowers/
```

---

## 自审清单

1. **Spec 覆盖度**: 每个 spec 章节都有对应任务: 数据模型(Task 1.2), API(Task 1.6+1.7), Markdown 渲染(Task 1.4), 首页(Task 2.6), 主题(Task 2.2), 后台编辑器(Task 3.2), 文章列表/详情(Task 2.7), 登录(Task 3.1), Dashboard(Task 3.1), 搜索(Task 1.6 路由)
2. **占位符检查**: 所有代码均已内联，无 TBD/TODO
3. **类型一致性**: PostResponse 包含 content_md + content_html; PostListItem 不含正文; API 路径统一 `/api/v1/...`; 前端 API 函数名与后端路由一致
