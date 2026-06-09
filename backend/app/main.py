from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import analytics, categories, posts, tags
from app.routers.admin import analytics as admin_analytics
from app.routers.admin import auth as admin_auth
from app.routers.admin import categories as admin_categories
from app.routers.admin import posts as admin_posts
from app.routers.admin import tags as admin_tags


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

# Public routes
app.include_router(categories.router)
app.include_router(tags.router)
app.include_router(posts.router)
app.include_router(analytics.router)

# Admin routes
app.include_router(admin_auth.router)
app.include_router(admin_posts.router)
app.include_router(admin_tags.router)
app.include_router(admin_categories.router)
app.include_router(admin_analytics.router)


@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}
