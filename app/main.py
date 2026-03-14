from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, users, posts, feed, communities, notifications, analytics

app = FastAPI(title="Social Platform API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # your React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,          prefix="/api/auth",          tags=["auth"])
app.include_router(users.router,         prefix="/api/users",         tags=["users"])
app.include_router(posts.router,         prefix="/api/posts",         tags=["posts"])
app.include_router(feed.router,          prefix="/api/feed",          tags=["feed"])
app.include_router(communities.router,   prefix="/api/communities",   tags=["communities"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(analytics.router,     prefix="/api/analytics",     tags=["analytics"])

@app.get("/health")
def health(): return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
