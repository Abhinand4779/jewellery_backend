"""
Jewellery FastAPI – application entry-point.

Startup sequence
----------------
1. Load .env
2. Create DB tables (SQLite by default, or whatever DATABASE_URL points to)
3. Mount routers

Environment variables (see .env)
---------------------------------
DATABASE_URL               – SQLAlchemy URL (default: sqlite:///./jewellery.db)
JWT_SECRET                 – Secret for signing JWTs
JWT_ALGORITHM              – HS256 (default)
ACCESS_TOKEN_EXPIRE_MINUTES – defaults to 10080 (7 days)
FRONTEND_URL               – used for the CORS allow-list
"""

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()   # Must happen before any module that reads os.getenv()

import database  # noqa: E402  (import after load_dotenv)
import models    # noqa: E402
import auth      # noqa: E402
from routers_products import router as products_router
from routers_cart import router as cart_router
from routers_orders import router as orders_router
from routers_reviews import router as reviews_router

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Aurelia Jewels API",
    version="1.0.0",
    description="Backend API for the Aurelia Jewels e-commerce platform.",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

# Collect allowed origins from env; fallback to localhost for development
_frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
ALLOWED_ORIGINS: list[str] = [
    origin.strip()
    for origin in _frontend_url.split(",")
    if origin.strip()
]
# Always allow local dev servers
for _local in ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]:
    if _local not in ALLOWED_ORIGINS:
        ALLOWED_ORIGINS.append(_local)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,   # explicit list — never "*" with credentials
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(auth.router)
app.include_router(products_router)
app.include_router(cart_router)
app.include_router(orders_router)
app.include_router(reviews_router)

# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------

@app.on_event("startup")
def on_startup() -> None:
    """Initialise the database tables on application start."""
    database.init_db()


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/", tags=["health"])
def read_root() -> dict:
    return {"status": "ok", "message": "Aurelia Jewels API is running"}


@app.get("/health", tags=["health"])
def health_check() -> dict:
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Dev server entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
    )
