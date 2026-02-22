import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()
import database
import models
import auth
from routers_products import router as products_router
from routers_cart import router as cart_router
from routers_orders import router as orders_router
from routers_reviews import router as reviews_router
app = FastAPI(title="Aurelia Jewels API")
# --- THE FIX: This allows EVERY website (Vercel, Local, etc.) ---
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex='https://.*\.vercel\.app', # This allows ANY vercel sub-domain
    allow_credentials=True,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(products_router)
app.include_router(cart_router)
app.include_router(orders_router)
app.include_router(reviews_router)
@app.on_event("startup")
def on_startup() -> None:
    database.init_db()
    # This automatically fills your database with products on Render
    try:
        from scripts.seed import seed
        seed(reset=False)
        print("✅ Database auto-seeded successfully!")
    except Exception as e:
        print(f"⚠️ Seeding skipped: {e}")
@app.get("/")
def home():
    return {"status": "ok", "message": "Jewellery API is Live!"}
@app.get("/health")
def health():
    return {"status": "ok"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))